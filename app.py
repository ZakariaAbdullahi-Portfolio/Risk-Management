import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm, t
import matplotlib.pyplot as plt
import streamlit as st

# CONFIGURATION & PAGE SETUP
st.set_page_config(page_title="Quantitative Risk Engine", layout="wide")

# Custom CSS for Analytic Theme
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    .stButton>button { background-color: #262730; border: 1px solid #4e535e; color: white; width: 100%; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Courier New', monospace; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# SECTION 1: MASTER ASSET DATABASE
INDICES_DB = {
    "US MARKETS": {"^GSPC": "S&P 500", "^IXIC": "NASDAQ 100", "^DJI": "Dow Jones", "^RUT": "Russell 2000"},
    "SHARIA COMPLIANT": {"SPUS": "S&P 500 Sharia", "HLAL": "Wahed Sharia"},
    "GLOBAL": {"^STOXX50E": "Euro Stoxx 50", "^OMX": "OMX Stockholm 30", "^N225": "Nikkei 225"}
}

STOCKS_DB = {
    "TECH": ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"],
    "NORDIC": ["VOLV-B.ST", "ERIC-B.ST", "AZN.ST", "HM-B.ST", "INVE-B.ST"],
    "FINANCE": ["JPM", "BAC", "V", "GS"],
    "HEALTH/ENERGY": ["LLY", "JNJ", "XOM", "CVX"]
}

# SECTION 2: ADVANCED MATH ENGINE
class MathEngine:
    @staticmethod
    def calculate_kelly(prob, win_loss_ratio=1.5):
        q = 1 - prob
        k = (prob * win_loss_ratio - q) / win_loss_ratio
        return max(0, k * 0.25)  # 25% Fractional Kelly for safety

    @staticmethod
    def black_scholes_tail_adjusted(S, r, sigma, days, ticker):
        T = days / 365
        if T <= 0 or sigma <= 0: return 0.0
        target_move = 1.020 if (ticker.startswith("^") or ticker in ["SPUS", "HLAL"]) else 1.045
        K = S * target_move 
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        # Student's t-distribution capture extremes (df=5)
        return t.cdf(d1, df=5) 

# SECTION 3: INDICATOR BUILDER
class IndicatorBuilder:
    @staticmethod
    def calculate_volatility_regime(prices, window=30):
        returns = np.log(prices / prices.shift(1))
        hist_vol = returns.rolling(window=window).std() * np.sqrt(252)
        short_vol = returns.rolling(window=10).std() * np.sqrt(252)
        return (hist_vol + short_vol) / 2

    @staticmethod
    def calculate_sma(prices, period): return prices.rolling(window=period).mean()
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        return 100 - (100 / (1 + gain/loss))

# SECTION 4: ANALYSIS EXECUTION
def run_analysis(ticker):
    st.write(f"### ANALYZING ASSET: {ticker}")
    
    try:
        df = yf.download(ticker, period="2y", progress=False, multi_level_index=False)
        if len(df) < 200:
            st.error("Insufficient data."); return
    except Exception as e:
        st.error(f"Error: {e}"); return

    prices = df['Close']
    current_price = float(prices.iloc[-1])
    vol_regime = IndicatorBuilder.calculate_volatility_regime(prices)
    current_vol = float(vol_regime.iloc[-1])
    sma_200 = IndicatorBuilder.calculate_sma(prices, 200)
    rsi = IndicatorBuilder.calculate_rsi(prices)
    current_rsi = float(rsi.iloc[-1])
    
    bs_prob = MathEngine.black_scholes_tail_adjusted(current_price, 0.045, current_vol, 30, ticker)
    kelly_suggestion = MathEngine.calculate_kelly(bs_prob)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Price", f"${current_price:.2f}")
    m2.metric("Probability", f"{bs_prob*100:.1f}%")
    m3.metric("Regime Vol.", f"{current_vol*100:.1f}%")
    m4.metric("Kelly Allocation", f"{kelly_suggestion*100:.1f}%")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df.index, prices, color='#58a6ff', label='Price')
    ax.plot(df.index, sma_200, color='orange', linestyle='--', label='200-SMA')
    ax.set_facecolor('#0e1117')
    fig.patch.set_facecolor('#0e1117')
    ax.tick_params(colors='white')
    ax.legend()
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("QUANTITATIVE VERDICT")
    is_uptrend = current_price > sma_200.iloc[-1]
    
    if bs_prob > 0.55 and is_uptrend:
        st.success(f"**CONVERGENCE:** Mathematical conviction ({bs_prob*100:.1f}%) aligns with structural trend.")
    elif bs_prob < 0.40:
        st.warning(f"**CAUTION:** Probabilistic model indicates low statistical edge.")
    else:
        st.info("**NEUTRAL:** Wait for trend confirmation or volatility contraction.")

# SECTION 5: MAIN INTERFACE
def main():
    st.sidebar.title("QUANTITATIVE TERMINAL")
    st.sidebar.markdown("---")
    
    mode = st.sidebar.radio("Market Access:", ["DATABASE", "INDICES", "SEARCH"])
    selected_ticker = None

    if mode == "DATABASE":
        cat = st.selectbox("Sector:", list(STOCKS_DB.keys()))
        selected_ticker = st.selectbox("Asset:", STOCKS_DB[cat])
    elif mode == "INDICES":
        cat = st.selectbox("Market:", list(INDICES_DB.keys()))
        choice = st.selectbox("Index:", list(INDICES_DB[cat].keys()))
        selected_ticker = choice
    else:
        selected_ticker = st.sidebar.text_input("Enter Ticker:").upper()

    # INITIATE BUTTON
    st.sidebar.markdown(" ")
    if st.sidebar.button("INITIATE ANALYSIS", type="primary"):
        if selected_ticker:
            run_analysis(selected_ticker)

    st.sidebar.markdown("---")
    st.sidebar.subheader("SYSTEM ARCHITECTURE v4.1")
    st.sidebar.info("""
    - **Logic:** BS-Model + Student's t-adjustment.
    - **Volatility:** Regime-weighted realized vol.
    - **Risk:** Fractional Kelly allocation.
    - **Structure:** Non-linear trend filtering.
    """)

if __name__ == "__main__":
    main()