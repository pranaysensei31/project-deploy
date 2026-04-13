import streamlit as st

st.set_page_config(page_title="FinSight | Investor Education", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 10% 0%, #0b1220 0%, #050814 45%, #050814 100%);
        font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
        color: #FFFFFF;
    }
    .block-container { max-width: 1300px; padding-top: 1.2rem; padding-bottom: 3rem; }
    h1, h2, h3 { color: #FFFFFF !important; font-weight: 950 !important; letter-spacing: -0.6px; }
    p, li { color: rgba(255,255,255,0.86) !important; font-size: 15px; line-height: 1.7; }
    .hero {
        border-radius: 26px; padding: 28px;
        background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.03) 100%);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 20px 60px rgba(0,0,0,0.35); margin-bottom: 18px;
    }
    .hero-title { font-size: 46px; font-weight: 950; margin: 0 0 10px 0; line-height: 1.05; color: #FFFFFF; }
    .hero-sub { margin: 0; font-size: 15px; color: rgba(255,255,255,0.82); line-height: 1.6; max-width: 1000px; }
    .tag {
        padding: 9px 14px; border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.10); background: rgba(255,255,255,0.05);
        font-size: 12px; font-weight: 850; color: rgba(255,255,255,0.95);
        display: inline-block; margin-top: 14px; margin-right: 8px;
    }
    .card {
        border-radius: 26px; padding: 20px;
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 20px 60px rgba(0,0,0,0.35); margin-bottom: 18px;
    }
    .callout {
        margin-top: 14px; border-radius: 18px; padding: 14px;
        border: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.06);
        color: rgba(255,255,255,0.90); font-weight: 750;
    }
    hr { border: none; border-top: 1px solid rgba(255,255,255,0.10); margin: 26px 0; }
    div[data-testid="stImage"] img {
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-title">Investor Education</div>
    <p class="hero-sub">
        A professional guide to stock market fundamentals. Learn how stocks are issued,
        how exchanges function, how prices are discovered, and how to think about risk.
    </p>
    <span class="tag">Market structure</span>
    <span class="tag">Primary vs Secondary market</span>
    <span class="tag">Price discovery</span>
    <span class="tag">Risk &amp; volatility</span>
    <span class="tag">Long-term investing</span>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.5, 1], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("1) What is the stock market?")
    st.markdown("""
The **stock market** refers to the collection of exchanges and marketplaces where shares of publicly traded companies are **issued** and **traded**.

- **Capital formation:** companies raise money to expand operations
- **Investment access:** investors can participate in business growth

Owning a share produces returns through:
- **Capital gains** (price increases)
- **Dividends** (profit distribution)
""")
    st.markdown('<div class="callout">Professional view: stock markets exist primarily to allocate capital efficiently and enable price discovery — not just "buy low, sell high".</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("2) Primary market vs Secondary market")
    st.markdown("""
### Primary market
Where companies **issue new shares** and raise capital.
- **IPO (Initial Public Offering)**
- Follow-on public offers

### Secondary market
Where investors **trade shares among themselves**.
- When you buy on NSE/BSE/NYSE, you are in the **secondary market**
- The company does **not** directly receive your money
""")
    st.markdown('<div class="callout">Why this matters: the stock market is both a capital-raising engine (primary) and a trading engine (secondary).</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📺 Recommended Watch")
    st.caption("How the stock market works — click the button below the thumbnail to watch")
    st.image(
        "https://img.youtube.com/vi/p7HKvqRI_Bo/maxresdefault.jpg",
        use_container_width=True,
    )
    st.link_button(
        "▶  Watch on YouTube — How does the stock market work?",
        url="https://www.youtube.com/watch?v=p7HKvqRI_Bo",
        use_container_width=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("3) How stock exchanges work")
    st.markdown("""
A stock exchange is an organized marketplace that ensures trading occurs under standardized rules.

In modern markets:
- Orders are matched electronically (buyer and seller)
- Trades happen via brokers / trading platforms
- Settlement happens after the trade (**T+1 / T+2** depending on the market)

Exchanges exist to provide **liquidity**, **transparency**, and standardized trading rules.
""")
    st.markdown('<div class="callout">Professional term: exchanges enable "order matching" and make price information publicly available.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("4) Price discovery (why prices move)")
    st.markdown("""
The stock market is fundamentally a system of **price discovery**.

Prices move as the market updates expectations about:
- Future earnings, growth, interest rates, competition, risk

Common short-term drivers:
- Earnings results vs expectations
- Macroeconomic news (rates, inflation, policy)
- Sector sentiment and geopolitical news
""")
    st.markdown('<div class="callout">Investing insight: the market reacts to changes in expectations — not only whether the news is "good" or "bad".</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("5) Risk in the stock market")
    st.markdown("""
Key risk concepts:
- **Volatility:** intensity of price movements
- **Drawdown:** fall from peak to trough
- **Concentration risk:** too much in one stock/sector
- **Liquidity risk:** can't exit at a fair price during stress

FinSight measures: annualized volatility, max drawdown, Sharpe ratio.
""")
    st.markdown('<div class="callout">Rule: returns are optional; risk is unavoidable. Always manage risk before chasing returns.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Glossary")
    st.markdown("""
- **Stock / Share:** ownership unit in a company
- **IPO:** first time shares are sold publicly
- **Market Cap:** price x shares outstanding
- **Exchange:** marketplace for trading securities
- **Liquidity:** ease of buying/selling
- **Index:** benchmark basket (NIFTY 50 / S&P 500)
- **ETF:** instrument that tracks an index
- **Volatility:** risk via price movement
- **Sharpe Ratio:** return per unit of risk
- **Drawdown:** peak-to-trough fall %
""")
    st.caption("These terms map directly to the data shown in FinSight.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("Common mistakes")
    st.markdown("""
- Trading without understanding volatility and drawdowns
- Buying based on hype without reading fundamentals
- Ignoring diversification
- Confusing "good company" with "good entry price"
- Investing without a time horizon
""")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

st.header("A professional learning path")
c1, c2, c3 = st.columns(3, gap="large")
with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Step 1: Learn market structure")
    st.markdown("Understand IPOs, exchanges, liquidity and price discovery before stock picking.")
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Step 2: Learn risk metrics")
    st.markdown("Use volatility, drawdown, and Sharpe ratio to evaluate instruments professionally.")
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Step 3: Build portfolio discipline")
    st.markdown("Diversify, rebalance, avoid concentrated positions and emotional decisions.")
    st.markdown('</div>', unsafe_allow_html=True)

with st.expander("FAQ", expanded=False):
    st.markdown("""
**Is the stock market the economy?**
Not exactly. The stock market is forward-looking — it reflects expectations about future profits and risk.

**Does buying stock help the company?**
In the primary market (IPO): yes. In normal trading (secondary): usually no.

**Should I use AI to invest?**
AI should support learning and analysis. Final decisions should reflect your own risk tolerance and time horizon.
""")

st.caption("FinSight Education — For learning purposes only — Not financial advice")