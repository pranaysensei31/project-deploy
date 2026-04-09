# app.py - HOME PAGE
import yfinance as yf
yf.set_tz_cache_location("/tmp")
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="FinSight | AI Financial Advisor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>

/* =========================
   GLOBAL SYSTEM
========================= */
.stApp {
    background: radial-gradient(circle at 20% 0%, #0f172a 0%, #020617 60%);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #e2e8f0;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* =========================
   NAVBAR (FLOATING GLASS)
========================= */
.nav-container {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 14px 28px;
    margin: -60px -60px 30px -60px;
}

.nav-logo {
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
}

/* =========================
   HERO (UPGRADED)
========================= */
.hero {
    background: linear-gradient(135deg, rgba(59,130,246,0.12), rgba(2,6,23,0.4));
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(18px);
    border-radius: 20px;
    padding: 50px;
    margin-bottom: 40px;
    text-align: left;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 14px;
    letter-spacing: -0.8px;
}

.hero-subtitle {
    font-size: 16px;
    color: #94a3b8;
    max-width: 700px;
    line-height: 1.6;
}

/* Feature pills refined */
.feature-pill {
    display: inline-block;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    color: #cbd5f5;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 12px;
    margin-top: 14px;
    margin-right: 6px;
}

/* =========================
   SECTION HEADER
========================= */
.section-header {
    font-size: 22px;
    font-weight: 600;
    color: #f8fafc;
    margin: 30px 0 18px;
}

/* =========================
   MARKET OVERVIEW (NEW LOOK)
========================= */
.market-ticker {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 20px;
    text-align: left;
    transition: all 0.2s ease;
}

.market-ticker:hover {
    border-color: rgba(59,130,246,0.4);
    background: rgba(255,255,255,0.05);
}

.ticker-name {
    font-size: 12px;
    color: #94a3b8;
}

.ticker-price {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    margin: 6px 0;
}

.ticker-change {
    font-size: 13px;
    font-weight: 500;
}

.positive { color: #22c55e; }
.negative { color: #ef4444; }

/* =========================
   FEATURE CARDS (LEVEL UP)
========================= */
.section-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 26px;
    transition: all 0.2s ease;
    height: 100%;
}

.section-card:hover {
    transform: translateY(-4px);
    border-color: rgba(59,130,246,0.5);
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

.card-title {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 10px;
}

.card-description {
    font-size: 14px;
    color: #94a3b8;
    line-height: 1.7;
}

/* =========================
   BUTTONS (PREMIUM)
========================= */
div.stButton > button {
    border-radius: 10px !important;
    height: 44px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: white !important;
    border: none !important;
    transition: 0.2s;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 30px rgba(59,130,246,0.4);
}

/* =========================
   TRENDING LIST
========================= */
.trending-stock {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px;
    display: flex;
    justify-content: space-between;
    transition: 0.2s;
}

.trending-stock:hover {
    border-color: rgba(59,130,246,0.4);
}

.stock-name {
    font-size: 14px;
    color: #e2e8f0;
}

.stock-price {
    font-size: 14px;
    font-weight: 600;
    color: #60a5fa;
}

</style>
""", unsafe_allow_html=True)
# Navigation Bar
st.markdown("""
<div class="nav-container">
    <span class="nav-logo"> FinSight</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero">
    <div class="hero-title">Welcome to FinSight AI</div>
    <div class="hero-subtitle">
        Your intelligent financial companion for stocks, mutual funds, and commodities analysis.
        Powered by advanced AI and real-time market data.
    </div>
    <div class="feature-pills">
        <span class="feature-pill"> AI-Powered Insights</span>
        <span class="feature-pill"> Real-time Data</span>
        <span class="feature-pill"> Portfolio Analytics</span>
        <span class="feature-pill"> Risk Assessment</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Market Overview
st.markdown('<div class="section-header"> Market Overview</div>', unsafe_allow_html=True)

@st.cache_data(ttl=300)
def get_index_data(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="5d")
        hist = hist['Close'].dropna()
        
        if len(hist) >= 2:
            current = float(hist.iloc[-1])
            prev = float(hist.iloc[-2])
            change = current - prev
            change_pct = (change / prev) * 100
            return current, change, change_pct
        return None, None, None
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None, None, None

indices = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "BANK NIFTY": "^NSEBANK",
    "NASDAQ": "^IXIC"
}

market_cols = st.columns(4)
for idx, (name, ticker) in enumerate(indices.items()):
    price, change, change_pct = get_index_data(ticker)
    
    if price is not None:
        change_class = "positive" if change >= 0 else "negative"
        sign = "+" if change >= 0 else ""
        
        market_cols[idx].markdown(f"""
        <div class="market-ticker">
            <div class="ticker-name">{name}</div>
            <div class="ticker-price">{price:,.2f}</div>
            <div class="ticker-change {change_class}">{sign}{change:,.2f} ({sign}{change_pct:.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)

# Quick Access Sections
st.markdown('<div class="section-header"> Explore Features</div>', unsafe_allow_html=True)

section_cols = st.columns(3)

with section_cols[0]:
    st.markdown("""
    <div class="section-card">
        <div class="card-content">
            <div class="card-icon"></div>
            <div class="card-title">Stock Analysis</div>
            <div class="card-description">
                Deep dive into stocks with AI-powered insights, fundamentals, risk metrics, 
                and comparison tools. Generate comprehensive reports instantly.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Analyze Stocks →", key="goto_stocks"):
        st.switch_page("pages/0_Stocks.py")

with section_cols[1]:
    st.markdown("""
    <div class="section-card">
        <div class="card-content">
            <div class="card-icon"></div>
            <div class="card-title">Mutual Funds</div>
            <div class="card-description">
                Explore top-performing mutual funds, compare returns, and build your 
                investment portfolio with expert recommendations.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Funds →", key="goto_mf"):
        st.switch_page("pages/2_Mutual_Funds_Predictor.py")

with section_cols[2]:
    st.markdown("""
    <div class="section-card">
        <div class="card-content">
            <div class="card-icon"></div>
            <div class="card-title">Commodities</div>
            <div class="card-description">
                Track real-time prices of gold, silver, crude oil, and other commodities. 
                Stay updated with market trends.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Commodities →", key="goto_comm"):
        st.switch_page("pages/3_Commodities.py")

# Trending Stocks
st.markdown('<div class="section-header"> Trending Stocks</div>', unsafe_allow_html=True)

trending_cols = st.columns(2)

trending_stocks_left = {
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS"
}

trending_stocks_right = {
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Wipro": "WIPRO.NS"
}

with trending_cols[0]:
    for name, ticker in trending_stocks_left.items():
        price, change, change_pct = get_index_data(ticker)
        if price is not None:
            change_class = "positive" if change >= 0 else "negative"
            sign = "+" if change >= 0 else ""
            st.markdown(f"""
            <div class="trending-stock">
                <div>
                    <div class="stock-name">{name}</div>
                    <div class="ticker-change {change_class}">{sign}{change_pct:.2f}%</div>
                </div>
                <div class="stock-price">₹{price:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

with trending_cols[1]:
    for name, ticker in trending_stocks_right.items():
        price, change, change_pct = get_index_data(ticker)
        if price is not None:
            change_class = "positive" if change >= 0 else "negative"
            sign = "+" if change >= 0 else ""
            st.markdown(f"""
            <div class="trending-stock">
                <div>
                    <div class="stock-name">{name}</div>
                    <div class="ticker-change {change_class}">{sign}{change_pct:.2f}%</div>
                </div>
                <div class="stock-price">₹{price:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

st.caption("FinSight • AI Financial Advisor • Streamlit + Yahoo Finance")

# Floating chatbot (if exists)
try:
    from utils.floating_chatbot import render_floating_chatbot
    render_floating_chatbot()
except ImportError:
    pass