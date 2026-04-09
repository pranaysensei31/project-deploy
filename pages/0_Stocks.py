import os
import re
import math
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

try:
    import yfinance as yf
    YF_AVAILABLE = True
except Exception:
    YF_AVAILABLE = False

if YF_AVAILABLE:
    yf.set_tz_cache_location("/tmp")

try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage
    GROQ_AVAILABLE = True
except Exception:
    GROQ_AVAILABLE = False


st.set_page_config(
    page_title="FinSight | AI Financial Advisor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "chat_memory" not in st.session_state:
    st.session_state["chat_memory"] = []

if "run_full_report" not in st.session_state:
    st.session_state["run_full_report"] = False


SMART_TICKERS = {
    "Apple":      "AAPL",
    "Tesla":      "TSLA",
    "Microsoft":  "MSFT",
    "NVIDIA":     "NVDA",
    "Amazon":     "AMZN",
    "Google":     "GOOGL",
    "Meta":       "META",
    "TCS":        "TCS.NS",
    "Infosys":    "INFY.NS",
    "Reliance":   "RELIANCE.NS",
    "HDFC Bank":  "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Zomato":     "ZOMATO.NS",
}


@st.cache_data(ttl=180)
def _safe_download(ticker: str, period: str = "5d") -> pd.Series:
    if not YF_AVAILABLE:
        return pd.Series(dtype=float)
    try:
        df = yf.download(
            ticker,
            period=period,
            interval="1d",
            progress=False,
            auto_adjust=True,
        )
        if df is None or df.empty:
            return pd.Series(dtype=float)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df["Close"].dropna().astype(float)
    except Exception:
        return pd.Series(dtype=float)


@st.cache_data(ttl=600)
def get_fx_rate(symbol: str) -> float:
    close = _safe_download(symbol, period="5d")
    if close.empty:
        return 0.0
    return float(close.iloc[-1])


def get_live_quote(ticker: str) -> dict:
    if not YF_AVAILABLE:
        return {}
    try:
        close = _safe_download(ticker, period="5d")
        if close.empty:
            return {}

        last_close = float(close.iloc[-1])
        prev_close = float(close.iloc[-2]) if len(close) >= 2 else last_close
        change     = last_close - prev_close
        change_pct = (change / prev_close * 100) if prev_close != 0 else 0.0

        ticker_up = ticker.upper()
        if ticker_up.endswith(".NS") or ticker_up.endswith(".BO"):
            currency = "INR"
        else:
            currency = "USD"

        price_inr = None
        fx_rate   = None

        if currency == "USD":
            fx_rate = get_fx_rate("USDINR=X")
            if fx_rate > 0:
                price_inr = last_close * fx_rate
        elif currency == "EUR":
            fx_rate = get_fx_rate("EURINR=X")
            if fx_rate > 0:
                price_inr = last_close * fx_rate

        return {
            "ticker":     ticker,
            "price":      last_close,
            "prev_close": prev_close,
            "change":     change,
            "change_pct": change_pct,
            "currency":   currency,
            "price_inr":  price_inr,
            "fx_rate_to_inr": fx_rate,
            "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception:
        return {}


@st.cache_data(ttl=600)
def get_stock_summary(ticker: str) -> dict:
    if not YF_AVAILABLE:
        return {}
    try:
        info = yf.Ticker(ticker).info or {}
        return {
            "ticker":          ticker,
            "name":            info.get("longName") or info.get("shortName") or ticker,
            "sector":          info.get("sector",          "N/A"),
            "industry":        info.get("industry",        "N/A"),
            "market_cap":      info.get("marketCap"),
            "pe":              info.get("trailingPE"),
            "forward_pe":      info.get("forwardPE"),
            "pb":              info.get("priceToBook"),
            "eps":             info.get("trailingEps"),
            "roe":             info.get("returnOnEquity"),
            "profit_margins":  info.get("profitMargins"),
            "debt_to_equity":  info.get("debtToEquity"),
            "free_cashflow":   info.get("freeCashflow"),
            "revenue_growth":  info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "52w_high":        info.get("fiftyTwoWeekHigh"),
            "52w_low":         info.get("fiftyTwoWeekLow"),
            "website":         info.get("website"),
            "exchange":        info.get("exchange"),
            "currency":        info.get("currency"),
        }
    except Exception:
        return {}


@st.cache_data(ttl=300)
def fetch_prices(ticker: str, days: int) -> pd.DataFrame:
    close = _safe_download(ticker, period=f"{days}d")
    if close.empty:
        return pd.DataFrame()
    df = close.reset_index()
    df.columns = ["date", "close"]
    df["date"]  = pd.to_datetime(df["date"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna().sort_values("date")
    return df[["date", "close"]]


@st.cache_data(ttl=3600)
def fetch_benchmark_prices(ticker: str, start_date, end_date) -> pd.DataFrame:
    if not YF_AVAILABLE:
        return pd.DataFrame()
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval="1d", progress=False)
        if df is None or df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        if "Date" not in df.columns or "Close" not in df.columns:
            return pd.DataFrame()
        df.rename(columns={"Date": "date", "Close": "close"}, inplace=True)
        df = df.dropna(subset=["date", "close"])
        df["date"]  = pd.to_datetime(df["date"], errors="coerce")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df = df.dropna(subset=["date", "close"]).sort_values("date")
        return df[["date", "close"]]
    except Exception:
        return pd.DataFrame()


def normalize_growth(series: pd.Series) -> pd.Series:
    if series is None or len(series) == 0:
        return series
    first = float(series.iloc[0])
    if first == 0:
        return series
    return series / first


def extract_tickers(query: str) -> list:
    raw = re.findall(r"\b[A-Za-z]{1,12}(?:\.[A-Za-z]{1,6})?\b", query)
    blacklist = {
        "and","the","with","show","what","this","that",
        "csv","report","for","give","export","generate","data",
        "analyze","compare","visualize","plot","trend","me","please",
    }
    tickers = []
    for r in raw:
        rc = r.upper()
        if rc.lower() in blacklist:
            continue
        if re.match(r"^[A-Z]{1,12}(\.[A-Z]{1,6})?$", rc):
            tickers.append(rc)
    return list(dict.fromkeys(tickers))


def compute_returns(series: pd.Series) -> pd.Series:
    return series.pct_change().dropna()


def sharpe_ratio(returns: pd.Series, rf_annual: float = 0.0) -> float:
    if len(returns) < 2:
        return float("nan")
    rf_daily = rf_annual / 252
    excess   = returns - rf_daily
    if excess.std() == 0:
        return float("nan")
    return float((excess.mean() / excess.std()) * math.sqrt(252))


def max_drawdown(series: pd.Series) -> float:
    prices = series.values
    peak   = -np.inf
    mdd    = 0.0
    for p in prices:
        peak = max(peak, p)
        dd   = (peak - p) / peak if peak > 0 else 0.0
        mdd  = max(mdd, dd)
    return float(mdd)


def format_market_cap(x):
    try:
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return "N/A"
        x = float(x)
        if x >= 1e12: return f"{x/1e12:.2f}T"
        if x >= 1e9:  return f"{x/1e9:.2f}B"
        if x >= 1e6:  return f"{x/1e6:.2f}M"
        return f"{x:.0f}"
    except Exception:
        return "N/A"


def simple_strength_rating(meta: dict) -> str:
    score = 0
    pe  = meta.get("pe");  pb  = meta.get("pb");  roe = meta.get("roe")
    dte = meta.get("debt_to_equity");  pm  = meta.get("profit_margins")
    rg  = meta.get("revenue_growth"); eg  = meta.get("earnings_growth")

    if isinstance(roe, (int, float)) and roe >= 0.12: score += 2
    elif isinstance(roe, (int, float)) and roe >= 0.07: score += 1
    if isinstance(pm,  (int, float)) and pm  >= 0.12: score += 2
    elif isinstance(pm, (int, float)) and pm >= 0.06: score += 1
    if isinstance(dte, (int, float)) and dte <= 80:   score += 2
    elif isinstance(dte, (int, float)) and dte <= 160: score += 1
    if isinstance(pe,  (int, float)) and pe > 0:
        if pe <= 25: score += 2
        elif pe <= 40: score += 1
    if isinstance(pb,  (int, float)) and pb > 0 and pb <= 4: score += 1
    if isinstance(rg,  (int, float)) and rg > 0: score += 1
    if isinstance(eg,  (int, float)) and eg > 0: score += 1

    if score >= 8: return "STRONG"
    if score >= 5: return "MODERATE"
    return "WEAK"


def compare_table(tickers: list, days: int, rf_annual: float) -> pd.DataFrame:
    rows = []
    for t in tickers[:5]:
        df = fetch_prices(t, days)
        if df.empty:
            continue
        rets = compute_returns(df["close"])
        rows.append({
            "Ticker":       t,
            "Last Close":   float(df["close"].iloc[-1]),
            "Volatility":   float(rets.std() * math.sqrt(252)),
            "Sharpe":       float(sharpe_ratio(rets, rf_annual)),
            "Max Drawdown": float(max_drawdown(df["close"])),
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(by="Sharpe", ascending=False)


def build_price_chart(tickers: list, days: int) -> go.Figure:
    fig = go.Figure()
    for t in tickers[:5]:
        df = fetch_prices(t, days)
        if df.empty:
            continue
        fig.add_trace(go.Scatter(x=df["date"], y=df["close"], mode="lines", name=t))
    fig.update_layout(
        title=f"Price Trend (Last {days} Days)",
        xaxis_title="Date",
        yaxis_title="Close Price",
    )
    return fig


def build_csv_dataset(tickers: list, days: int) -> str:
    records = []
    for t in tickers[:5]:
        df = fetch_prices(t, days)
        if df.empty:
            continue
        tmp = df.copy()
        tmp["ticker"] = t
        records.append(tmp)
    if not records:
        return ""
    out = pd.concat(records, ignore_index=True)[["date", "ticker", "close"]]
    return out.to_csv(index=False)


def llm_advisor_summary(user_query: str, analysis_text: str) -> str:
    if not GROQ_AVAILABLE:
        return ""
    key = os.getenv("GROQ_API_KEY", "")
    if not key.strip():
        return ""
    try:
        chat   = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0.3, groq_api_key=key)
        prompt = f"""You are a professional financial advisor.
User tickers: {user_query}

Create a short professional advisor-style summary:
- insights
- risk
- suggestion (no guarantee)
- caution

ANALYSIS:
{analysis_text}
"""
        return chat.invoke([HumanMessage(content=prompt)]).content.strip()
    except Exception:
        return ""


def safe_float(x, default=None):
    try:
        return float(x)
    except Exception:
        return default


def parse_portfolio_input(text: str):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    items = []
    for ln in lines:
        parts = ln.split()
        if len(parts) != 2:
            continue
        t = parts[0].upper().strip()
        w = safe_float(parts[1], None)
        if w is None:
            continue
        items.append((t, w))
    if not items:
        return [], np.array([])
    tickers_  = [t for t, _ in items]
    weights   = np.array([w for _, w in items], dtype=float)
    if weights.sum() <= 0:
        return [], np.array([])
    weights = weights / weights.sum()
    return tickers_, weights


def portfolio_metrics(tickers_: list, weights: np.ndarray, days_: int, rf_annual: float):
    price_df = pd.DataFrame()
    for t in tickers_:
        df = fetch_prices(t, days_)
        if df.empty:
            continue
        df = df.rename(columns={"close": t}).set_index("date")
        price_df = df[[t]] if price_df.empty else price_df.join(df[[t]], how="outer")

    price_df = price_df.dropna()
    if price_df.empty or len(price_df) < 7:
        return {}

    returns      = price_df.pct_change().dropna()
    w            = np.array(weights, dtype=float)
    port_returns = returns.dot(w)

    vol          = float(port_returns.std() * math.sqrt(252))
    sr           = float(sharpe_ratio(port_returns, rf_annual))
    total_return = float((1 + port_returns).prod() - 1)

    contrib       = returns.mean() * w
    top_contrib   = contrib.idxmax()
    worst_contrib = contrib.idxmin()

    return {
        "volatility":      vol,
        "sharpe":          sr,
        "total_return":    total_return,
        "top_contributor": top_contrib,
        "worst_contributor": worst_contrib,
        "returns_series":  port_returns,
    }


# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 10% 0%, #0b1220 0%, #050814 45%, #050814 100%);
        font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
        color: #FFFFFF;
    }
    .block-container { max-width: 1300px; padding-top: 1.2rem; padding-bottom: 2.5rem; }
    .hero {
        border-radius: 26px; padding: 28px;
        background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.03) 100%);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 20px 60px rgba(0,0,0,0.35); margin-bottom: 18px;
    }
    .hero h1 { font-size: 46px; font-weight: 950; line-height: 1.05; margin: 0 0 10px 0; color: #FFFFFF; letter-spacing: -0.8px; }
    .hero p  { margin: 0; font-size: 15px; color: rgba(255,255,255,0.82); line-height: 1.6; max-width: 900px; }
    .tag {
        padding: 9px 14px; border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.10); background: rgba(255,255,255,0.05);
        font-size: 12px; font-weight: 800; color: rgba(255,255,255,0.9);
        display: inline-block; margin-top: 12px; margin-right: 8px;
    }
    .panel {
        border-radius: 26px; padding: 18px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 20px 60px rgba(0,0,0,0.35);
    }
    .panel-title { font-size: 15px; font-weight: 950; color: #FFFFFF; margin: 0 0 12px 0; }
    .stMarkdown, .stMarkdown * { color: rgba(255,255,255,0.96) !important; opacity: 1 !important; }
    div[data-testid="stCaptionContainer"], div[data-testid="stCaptionContainer"] * {
        color: rgba(255,255,255,0.88) !important; opacity: 1 !important; font-weight: 850 !important;
    }
    label, div[data-testid="stWidgetLabel"] * {
        color: #FFFFFF !important; opacity: 1 !important; font-weight: 900 !important; letter-spacing: 0.2px !important;
    }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea {
        background: rgba(10,15,35,0.95) !important; border: 1px solid rgba(255,255,255,0.14) !important;
        border-radius: 16px !important; box-shadow: none !important;
    }
    div[data-baseweb="input"] input, textarea {
        color: #ffffff !important; font-weight: 950 !important; background: transparent !important;
    }
    div[data-baseweb="select"] span { color: #ffffff !important; font-weight: 950 !important; }
    ::placeholder { color: rgba(255,255,255,0.55) !important; font-weight: 800 !important; }
    div[data-testid="stMetricLabel"] * { color: rgba(255,255,255,0.90) !important; opacity: 1 !important; font-weight: 900 !important; }
    div[data-testid="stMetricValue"] * { color: #ffffff !important; opacity: 1 !important; font-weight: 950 !important; }
    div[data-testid="stMetricDelta"] * { opacity: 1 !important; font-weight: 950 !important; }
    button[data-baseweb="tab"] { color: rgba(255,255,255,0.85) !important; font-weight: 900 !important; opacity: 1 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #ffffff !important; font-weight: 950 !important; }
    div[data-baseweb="tab-highlight"] {
        background: linear-gradient(90deg, #3B82F6, #22C55E) !important; height: 3px !important; border-radius: 999px !important;
    }
    div.stButton > button {
        border-radius: 18px !important; height: 56px !important; font-size: 15px !important;
        font-weight: 950 !important; color: #0B1220 !important;
        background: linear-gradient(135deg, #22C55E 0%, #3B82F6 100%) !important;
        border: none !important; width: 100%; box-shadow: 0 18px 60px rgba(0,0,0,0.45); transition: 0.2s;
    }
    div.stButton > button:hover { transform: translateY(-1px); filter: brightness(1.06); }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <h1>Stock insights that feel effortless.</h1>
    <p>
        Enter tickers and generate a full report: live prices, company overview, fundamentals,
        risk metrics, comparison, charts, CSV export. Portfolio mode is also available.
    </p>
    <span class="tag">One-click report</span>
    <span class="tag">USD/EUR → INR</span>
    <span class="tag">Fundamentals</span>
    <span class="tag">Risk metrics</span>
    <span class="tag">Charts</span>
    <span class="tag">Benchmark Comparison</span>
</div>
""", unsafe_allow_html=True)


left, right = st.columns([1.05, 1.65], gap="large")

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Input</div>', unsafe_allow_html=True)

    selected_company = st.selectbox(
        "Quick search (optional)",
        ["None"] + list(SMART_TICKERS.keys()),
        index=0,
    )

    default_q = SMART_TICKERS[selected_company] if selected_company != "None" else "AAPL TSLA MSFT"

    query = st.text_input(
        "Tickers / Query",
        value=default_q,
        placeholder="Example: AAPL TSLA MSFT | TCS.NS INFY.NS",
    )

    days = st.slider("History window (days)", min_value=3, max_value=365, value=90)

    rf_annual_ui = st.slider("Risk-free rate (annual, %)", min_value=0.0, max_value=12.0, value=4.0, step=0.25)
    rf_annual    = rf_annual_ui / 100.0

    tickers = extract_tickers(query)
    st.caption("Detected tickers: " + (", ".join(tickers[:10]) if tickers else "none"))

    st.write("")
    st.markdown("#### Live Prices (Top 4)")

    if tickers:
        cols = st.columns(min(4, len(tickers)))
        for i, t in enumerate(tickers[:4]):
            q = get_live_quote(t)
            if not q:
                cols[i].metric(label=t, value="Loading…")
            else:
                delta_str = f"{q['change']:.2f} ({q['change_pct']:.2f}%)"
                currency  = q.get("currency", "")
                symbol    = {"USD": "$", "EUR": "€"}.get(currency, "")

                if currency in ["USD", "EUR"] and q.get("price_inr") is not None:
                    cols[i].metric(
                        label=t,
                        value=f"{symbol}{q['price']:.2f} | ₹{q['price_inr']:.2f}",
                        delta=delta_str,
                    )
                else:
                    cols[i].metric(
                        label=t,
                        value=f"{q['price']:.2f} {currency}",
                        delta=delta_str,
                    )
    else:
        st.info("Enter tickers to view live prices.")

    st.write("")
    st.markdown("#### Generate")

    if st.button("Generate Full Advisor Report"):
        st.session_state["run_full_report"] = True

    st.write("")
    st.markdown("#### Portfolio Mode")

    portfolio_text = st.text_area(
        "Portfolio input (ticker weight)",
        value="AAPL 40\nTSLA 30\nMSFT 30",
        height=120,
    )

    run_portfolio = st.button("Run portfolio analysis")

    st.markdown('</div>', unsafe_allow_html=True)


with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Results</div>', unsafe_allow_html=True)

    if run_portfolio:
        ptickers, pweights = parse_portfolio_input(portfolio_text)

        if len(ptickers) < 2:
            st.error("Enter at least 2 tickers in portfolio mode.")
        else:
            with st.spinner("Analyzing portfolio…"):
                pm = portfolio_metrics(ptickers, pweights, days_=max(days, 90), rf_annual=rf_annual)

            if not pm:
                st.error("Not enough market data to compute portfolio metrics.")
            else:
                st.success("Portfolio analysis complete.")

                a1, a2, a3, a4 = st.columns(4)
                a1.metric("Volatility (ann.)", f"{pm['volatility']:.2%}")
                a2.metric("Sharpe Ratio",      f"{pm['sharpe']:.2f}")
                a3.metric("Return (approx)",   f"{pm['total_return']:.2%}")
                a4.metric("Top Contributor",    pm["top_contributor"])
                st.caption(f"Worst contributor: {pm['worst_contributor']}")

                figp = go.Figure()
                figp.add_trace(go.Scatter(
                    x=pm["returns_series"].index,
                    y=(1 + pm["returns_series"]).cumprod(),
                    mode="lines",
                    name="Portfolio Growth",
                ))
                figp.update_layout(title="Portfolio Growth Curve", xaxis_title="Date", yaxis_title="Growth")
                st.plotly_chart(figp, use_container_width=True)

    elif st.session_state["run_full_report"]:
        if not tickers:
            st.error("Please enter at least one valid ticker (example: AAPL).")
            st.session_state["run_full_report"] = False
        else:
            primary    = tickers[0]
            meta       = get_stock_summary(primary)
            df_primary = fetch_prices(primary, days)

            rets = compute_returns(df_primary["close"]) if not df_primary.empty else pd.Series(dtype=float)

            vol = float(rets.std() * math.sqrt(252)) if len(rets) > 2 else float("nan")
            mdd = float(max_drawdown(df_primary["close"])) if not df_primary.empty else float("nan")
            sr  = float(sharpe_ratio(rets, rf_annual)) if len(rets) > 2 else float("nan")

            if not np.isnan(vol):
                risk_label = "LOW" if vol < 0.20 else ("MEDIUM" if vol < 0.35 else "HIGH")
            else:
                risk_label = "N/A"

            comp_df  = compare_table(tickers, days, rf_annual) if len(tickers) >= 2 else pd.DataFrame()
            fig      = build_price_chart(tickers, days)
            csv_data = build_csv_dataset(tickers, days)

            analysis_text = f"""
Primary ticker: {primary}
Volatility (annualized): {vol}
Max Drawdown: {mdd}
Sharpe: {sr}
Risk Level: {risk_label}

Comparison:
{comp_df.to_string(index=False) if not comp_df.empty else 'N/A'}
"""
            advisor = llm_advisor_summary(query, analysis_text)

            st.session_state["chat_memory"].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query":     query,
                "mode":      "full_report",
                "response":  advisor[:2000] if advisor else "Generated full report",
            })

            t0, t1, t2, t3, t4, t5, t6 = st.tabs([
                "Overview", "Advisor Summary", "Fundamentals",
                "Risk + Recommendation", "Compare", "Benchmark", "Chart + CSV"
            ])

            with t0:
                st.subheader("Company Overview")
                if meta:
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Ticker",   meta.get("ticker",   "N/A"))
                    m2.metric("Company",  meta.get("name",     "N/A"))
                    m3.metric("Exchange", meta.get("exchange", "N/A"))
                    m4.metric("Currency", meta.get("currency", "N/A"))

                    m5, m6, m7, m8 = st.columns(4)
                    m5.metric("Market Cap", format_market_cap(meta.get("market_cap")))
                    pe_val = meta.get("pe")
                    m6.metric("P/E Ratio", f"{pe_val:.2f}" if isinstance(pe_val, (int, float)) else "N/A")
                    hi = meta.get("52w_high"); lo = meta.get("52w_low")
                    m7.metric("52W High", f"{hi:.2f}" if isinstance(hi, (int, float)) else "N/A")
                    m8.metric("52W Low",  f"{lo:.2f}" if isinstance(lo, (int, float)) else "N/A")

                    st.caption(f"Sector: {meta.get('sector','N/A')} | Industry: {meta.get('industry','N/A')}")
                    if meta.get("website"):
                        st.caption(f"Website: {meta['website']}")
                else:
                    st.info("No overview available for this ticker.")

            with t1:
                st.subheader("Advisor Summary")
                if advisor:
                    st.markdown(advisor)
                else:
                    st.info("Groq API not configured. Set GROQ_API_KEY to enable AI advisor summary.")

            with t2:
                st.subheader("Fundamentals (Primary ticker)")
                if not meta:
                    st.info("Fundamental data not available for this ticker.")
                else:
                    rating = simple_strength_rating(meta)
                    st.caption("Fundamentals fetched from Yahoo Finance — may be incomplete for some tickers.")

                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Strength Rating", rating)
                    c2.metric("Market Cap", format_market_cap(meta.get("market_cap")))
                    pe_val  = meta.get("pe")
                    c3.metric("P/E (TTM)", f"{pe_val:.2f}" if isinstance(pe_val, (int, float)) else "N/A")
                    fpe_val = meta.get("forward_pe")
                    c4.metric("Forward P/E", f"{fpe_val:.2f}" if isinstance(fpe_val, (int, float)) else "N/A")

                    d1, d2, d3, d4 = st.columns(4)
                    pb_val  = meta.get("pb")
                    d1.metric("P/B", f"{pb_val:.2f}" if isinstance(pb_val, (int, float)) else "N/A")
                    eps_val = meta.get("eps")
                    d2.metric("EPS (TTM)", f"{eps_val:.2f}" if isinstance(eps_val, (int, float)) else "N/A")
                    roe_val = meta.get("roe")
                    d3.metric("ROE", f"{roe_val:.2%}" if isinstance(roe_val, (int, float)) else "N/A")
                    dte_val = meta.get("debt_to_equity")
                    d4.metric("Debt/Equity", f"{dte_val:.2f}" if isinstance(dte_val, (int, float)) else "N/A")

                    e1, e2, e3, e4 = st.columns(4)
                    pm_val  = meta.get("profit_margins")
                    e1.metric("Profit Margin",   f"{pm_val:.2%}" if isinstance(pm_val, (int, float)) else "N/A")
                    rg_val  = meta.get("revenue_growth")
                    e2.metric("Revenue Growth",  f"{rg_val:.2%}" if isinstance(rg_val, (int, float)) else "N/A")
                    eg_val  = meta.get("earnings_growth")
                    e3.metric("Earnings Growth", f"{eg_val:.2%}" if isinstance(eg_val, (int, float)) else "N/A")
                    fcf_val = meta.get("free_cashflow")
                    e4.metric("Free Cash Flow",  format_market_cap(fcf_val) if isinstance(fcf_val, (int, float)) else "N/A")

                    if rating == "STRONG":
                        st.success("Fundamentals look strong based on available ratios.")
                    elif rating == "MODERATE":
                        st.warning("Fundamentals look moderate — verify with deeper research.")
                    else:
                        st.error("Fundamentals appear weak or incomplete — treat with caution.")

            with t3:
                st.subheader("Risk Metrics (Primary ticker)")
                if df_primary.empty:
                    st.info("Not enough data for risk analysis.")
                else:
                    r1, r2, r3, r4 = st.columns(4)
                    r1.metric("Ticker",             primary)
                    r2.metric("Volatility (ann.)",  f"{vol:.2%}" if not np.isnan(vol) else "N/A")
                    r3.metric("Max Drawdown",        f"{mdd:.2%}" if not np.isnan(mdd) else "N/A")
                    r4.metric("Sharpe",              f"{sr:.2f}"  if not np.isnan(sr)  else "N/A")
                    st.caption(f"Risk Level: {risk_label}")

            with t4:
                st.subheader("Comparison Report")
                if comp_df.empty:
                    st.info("Enter 2+ tickers to compare.")
                else:
                    st.dataframe(comp_df, use_container_width=True)
                    best  = comp_df.iloc[0]["Ticker"]
                    worst = comp_df.iloc[-1]["Ticker"]
                    st.caption(f"Top risk-adjusted (Sharpe): {best} | Weakest: {worst}")

            with t5:
                st.subheader(f"Benchmark Comparison — {primary} vs NIFTY 50 & NASDAQ")

                if df_primary.empty:
                    st.info("Not enough stock data for benchmark comparison.")
                elif not YF_AVAILABLE:
                    st.info("yfinance not available.")
                else:
                    start_date = df_primary["date"].iloc[0]
                    end_date   = df_primary["date"].iloc[-1]

                    nifty  = fetch_benchmark_prices("^NSEI",  start_date, end_date)
                    nasdaq = fetch_benchmark_prices("^IXIC",  start_date, end_date)

                    def align_stock_bench(df_stock: pd.DataFrame, df_bench: pd.DataFrame) -> pd.DataFrame:
                        s = df_stock.rename(columns={"close": "stock"}).set_index("date")
                        b = df_bench.rename(columns={"close": "bench"}).set_index("date")
                        merged = s.join(b, how="inner").dropna().reset_index()
                        return merged

                    merged_nifty  = align_stock_bench(df_primary, nifty)  if not nifty.empty  else pd.DataFrame()
                    merged_nasdaq = align_stock_bench(df_primary, nasdaq) if not nasdaq.empty else pd.DataFrame()

                    if merged_nifty.empty and merged_nasdaq.empty:
                        st.info("Benchmark data not available right now. Try again later.")
                    else:
                        def series_cagr(series: pd.Series, dates: pd.Series) -> float:
                            try:
                                years = max(1e-9, (dates.iloc[-1] - dates.iloc[0]).days / 365.25)
                                return float((series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1)
                            except Exception:
                                return float("nan")

                        stock_cagr = series_cagr(df_primary["close"], df_primary["date"])

                        c1, c2, c3 = st.columns(3)
                        c1.metric(f"{primary} CAGR", f"{stock_cagr:.2%}" if not np.isnan(stock_cagr) else "N/A")

                        if not merged_nifty.empty:
                            nifty_cagr = series_cagr(merged_nifty["bench"], merged_nifty["date"])
                            c2.metric("NIFTY 50 CAGR", f"{nifty_cagr:.2%}" if not np.isnan(nifty_cagr) else "N/A")
                        else:
                            c2.metric("NIFTY 50 CAGR", "N/A")
                            nifty_cagr = float("nan")

                        if not merged_nasdaq.empty:
                            nasdaq_cagr = series_cagr(merged_nasdaq["bench"], merged_nasdaq["date"])
                            c3.metric("NASDAQ CAGR", f"{nasdaq_cagr:.2%}" if not np.isnan(nasdaq_cagr) else "N/A")
                        else:
                            c3.metric("NASDAQ CAGR", "N/A")
                            nasdaq_cagr = float("nan")

                        figb = go.Figure()
                        stock_norm = normalize_growth(df_primary["close"])
                        figb.add_trace(go.Scatter(x=df_primary["date"], y=stock_norm, mode="lines", name=primary))

                        if not merged_nifty.empty:
                            figb.add_trace(go.Scatter(x=merged_nifty["date"], y=normalize_growth(merged_nifty["bench"]), mode="lines", name="NIFTY 50"))

                        if not merged_nasdaq.empty:
                            figb.add_trace(go.Scatter(x=merged_nasdaq["date"], y=normalize_growth(merged_nasdaq["bench"]), mode="lines", name="NASDAQ"))

                        figb.update_layout(
                            title="Benchmark Growth Comparison (Normalized, Start = 1.0)",
                            xaxis_title="Date",
                            yaxis_title="Growth Index",
                            height=460
                        )
                        st.plotly_chart(figb, use_container_width=True)

                        alpha_parts = []
                        if not np.isnan(stock_cagr) and not np.isnan(nifty_cagr):
                            alpha_parts.append(f"vs NIFTY 50: {stock_cagr - nifty_cagr:+.2%}")
                        if not np.isnan(stock_cagr) and not np.isnan(nasdaq_cagr):
                            alpha_parts.append(f"vs NASDAQ: {stock_cagr - nasdaq_cagr:+.2%}")
                        if alpha_parts:
                            st.caption(f"Outperformance — " + " | ".join(alpha_parts))

            with t6:
                st.subheader("Chart")
                st.plotly_chart(fig, use_container_width=True)
                st.write("")
                st.subheader("CSV Export")
                if csv_data:
                    st.download_button("Download report.csv", data=csv_data, file_name="report.csv", mime="text/csv")
                else:
                    st.info("CSV not available for these tickers.")

            st.session_state["run_full_report"] = False

    else:
        st.info("Enter tickers and click **Generate Full Advisor Report**, or use portfolio mode.")

    st.markdown('</div>', unsafe_allow_html=True)


st.write("")
with st.expander("Recent activity", expanded=False):
    if not st.session_state["chat_memory"]:
        st.info("No activity yet.")
    else:
        for chat in st.session_state["chat_memory"][::-1][:10]:
            st.markdown(f"**{chat['timestamp']}**")
            st.markdown(f"Action: `{chat['mode']}`")
            st.markdown(f"Tickers: `{chat['query']}`")
            st.markdown("---")


st.caption("FinSight • AI Financial Advisor • Streamlit + Yahoo Finance")

try:
    from utils.floating_chatbot import render_floating_chatbot
    render_floating_chatbot()
except ImportError:
    pass