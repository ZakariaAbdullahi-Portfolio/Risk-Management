import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm
import matplotlib.pyplot as plt
import math
import streamlit as st

# CONFIGURATION & PAGE SETUP
st.set_page_config(page_title="Risk Management System", layout="wide")

# Custom CSS for Analytic Theme
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    .stButton>button { background-color: #262730; border: 1px solid #4e535e; color: white; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

# SECTION 1: MASTER ASSET DATABASE
INDICES_DB = {
    "US MARKETS": {
        "^GSPC": "S&P 500 (US Large Cap)",
        "^IXIC": "NASDAQ 100 (Tech)",
        "^DJI": "Dow Jones Industrial",
        "^RUT": "Russell 2000 (Small Cap)"
    },
    "SHARIA COMPLIANT": {
        "SPUS": "S&P 500 Sharia (SP Funds)",
        "HLAL": "Wahed FTSE USA Sharia"
    },
    "GLOBAL INDICES": {
        "^STOXX50E": "Euro Stoxx 50 (Europe)",
        "^GDAXI": "DAX 40 (Germany)",
        "^FTSE": "FTSE 100 (UK)",
        "^OMX": "OMX Stockholm 30",
        "^N225": "Nikkei 225 (Japan)",
        "000001.SS": "Shanghai Composite (China)"
    }
}

STOCKS_DB = {
    "MAGNIFICENT 7 (TECH)": ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"],
    "NORDIC GIANTS": ["VOLV-B.ST", "ERIC-B.ST", "AZN.ST", "HM-B.ST", "INVE-B.ST", "EQNR.OL", "NOVO-B.CO", "SAND.ST", "ATCO-A.ST", "TELIA.ST"],
    "US FINANCE & BANKING": ["JPM", "BAC", "V", "MA", "GS", "MS", "WFC", "BLK"],
    "GLOBAL CONSUMER": ["KO", "PEP", "MCD", "NKE", "SBUX", "WMT", "COST", "PG"],
    "PHARMA & HEALTH": ["LLY", "JNJ", "PFE", "MRK", "ABBV", "UNH"],
    "ENERGY & COMMODITIES": ["XOM", "CVX", "SHEL", "BP", "RIO", "VALE"]
}

# Flatten stocks for search
ALL_STOCKS = {}
for category, tickers in STOCKS_DB.items():
    for ticker in tickers:
        ALL_STOCKS[f"{ticker} - {category}"] = ticker

# SECTION 2: MATH & LOGIC ENGINE
class MathEngine:
    @staticmethod
    def black_scholes_probability(S, r, sigma, t):
        if t <= 0 or sigma == 0: return 0.0
        K = S * (1 + (r * t)) 
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
        return norm.cdf(d1)

class IndicatorBuilder:
    @staticmethod
    def calculate_sma(prices, period):
        return pd.Series(prices).rolling(window=period).mean()

    @staticmethod
    def calculate_rsi(prices, period=14):
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_volatility(prices, window=30):
        log_ret = np.log(pd.Series(prices) / pd.Series(prices).shift(1))
        return log_ret.rolling(window=window).std() * np.sqrt(252)

# SECTION 3: TRADING SYSTEM
def run_analysis(ticker):
    st.write(f"### ANALYZING ASSET: {ticker}")
    
    # 1. Fetch Data
    try:
        df = yf.download(ticker, period="2y", progress=False, multi_level_index=False)
        if len(df) < 200:
            st.error("Not enough data to analyze.")
            return
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return

    prices = df['Close']
    
    # 2. Calculate Indicators
    sma_50 = IndicatorBuilder.calculate_sma(prices, 50)
    sma_200 = IndicatorBuilder.calculate_sma(prices, 200)
    rsi = IndicatorBuilder.calculate_rsi(prices, 14)
    volatility = IndicatorBuilder.calculate_volatility(prices, 30)
    
    # 3. Get Latest Metrics
    current_price = prices.iloc[-1]
    current_vol = volatility.iloc[-1]
    current_rsi = rsi.iloc[-1]
    bs_prob = MathEngine.black_scholes_probability(current_price, 0.045, current_vol, 30/365)

    # 4. Display Metrics Dashboard
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Price", f"${current_price:.2f}")
    col2.metric("RSI (14)", f"{current_rsi:.1f}")
    col3.metric("Volatility", f"{current_vol*100:.1f}%")
    col4.metric("BS Probability", f"{bs_prob*100:.1f}%", help="Probability of profit in 30 days")

    # 5. Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df.index, prices, label='Price', color='white', alpha=0.6)
    ax.plot(df.index, sma_50, label='SMA 50', color='cyan', alpha=0.8)
    ax.plot(df.index, sma_200, label='SMA 200', color='orange', alpha=0.8)
    
    # Buy Signals
    buy_signals = (prices > sma_200) & (rsi < 40)
    ax.scatter(df.index[buy_signals], prices[buy_signals], marker='^', color='#00ff00', s=100, label='Buy Signal', zorder=5)

    ax.set_facecolor('#0e1117')
    fig.patch.set_facecolor('#0e1117')
    ax.tick_params(colors='white')
    for spine in ax.spines.values(): spine.set_color('#4e535e')
    ax.legend()
    st.pyplot(fig)

    # 6. Analyst Verdict
    st.subheader("SYSTEM VERDICT")
    if current_price > sma_200.iloc[-1]:
        trend = "BULLISH (Uptrend)"
        color = "green"
    else:
        trend = "BEARISH (Downtrend)"
        color = "red"
        
    st.markdown(f"**Trend:** :{color}[{trend}]")
    st.markdown(f"**RSI Status:** {'Overbought' if current_rsi > 70 else 'Oversold' if current_rsi < 30 else 'Neutral'}")
    
    if bs_prob > 0.55:
        st.success(f"OPPORTUNITY: High mathematical probability ({bs_prob*100:.1f}%) of upside.")
    else:
        st.warning("CAUTION: Mathematical probability is low. Stay Liquid.")

# MAIN APP INTERFACE
def main():
    st.sidebar.title("ACCESS TERMINAL")
    st.sidebar.markdown("---")
    
    # MODE SELECTION
    mode = st.sidebar.radio("Select Data Source:", ["TOP 100 STOCKS", "GLOBAL INDICES", "MANUAL SEARCH"])
    
    selected_ticker = None

    if mode == "TOP 100 STOCKS":
        st.header("Major Equities Database")
        category = st.selectbox("Select Sector:", list(STOCKS_DB.keys()))
        ticker_key = st.selectbox("Select Asset:", STOCKS_DB[category])
        selected_ticker = ticker_key

    elif mode == "GLOBAL INDICES":
        st.header("Global Market Indices")
        all_indices = {}
        for cat, data in INDICES_DB.items():
            for t, n in data.items():
                all_indices[f"{n} ({t})"] = t
        
        choice = st.selectbox("Select Index:", list(all_indices.keys()))
        selected_ticker = all_indices[choice]

    elif mode == "MANUAL SEARCH":
        st.header("Manual Ticker Entry")
        user_input = st.text_input("Enter Ticker (e.g., TSLA, BTC-USD, GLD):").upper()
        if user_input:
            selected_ticker = user_input

    # RUN BUTTON
    if st.sidebar.button("INITIATE ANALYSIS", type="primary"):
        if selected_ticker:
            run_analysis(selected_ticker)
        else:
            st.error("Please select a valid ticker.")

if __name__ == "__main__":
    main()