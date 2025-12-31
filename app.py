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
    .stButton>button { background-color: #262730; border: 1px solid #4e535e; color: white; width: 100%; height: 3em; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Courier New', monospace; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .main-control { background-color: #1c2128; padding: 20px; border-radius: 15px; border: 1px solid #444c56; margin-bottom: 25px; }
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
    "FINANCE": ["JPM", "BAC", "V", "MA", "GS"],
    "HEALTH/ENERGY": ["LLY", "JNJ", "XOM", "CVX"]
}

# SECTION 2: ADVANCED MATH ENGINE
class MathEngine:
    @staticmethod
    def calculate_kelly(prob, win_loss_ratio=1.5):
        q = 1 - prob
        k = (prob * win_loss_ratio - q) / win_loss_ratio
        return max(0, k * 0.25)

    @staticmethod
    def black_scholes_tail_adjusted(S, r, sigma, days, ticker):
        T = days / 365
        if T <= 0 or sigma <= 0: return 0.0
        target_move = 1.020 if (ticker.startswith("^") or ticker in ["SPUS", "HLAL"]) else 1.045
        K = S * target_move 
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
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
    st.markdown("---")
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
    
    bs_prob = MathEngine.black_scholes_tail_adjusted(current_price, 0.045, current_vol, 30, ticker)
    kelly_suggestion = MathEngine.calculate_kelly(bs_prob)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Price", f"${current_price:.2f}")
    m2.metric("Probability", f"{bs_prob*100:.1f}%")
    m3.metric("Regime Vol.", f"{current_vol*100:.1f}%")
    m4.metric("Kelly Allocation", f"{kelly_suggestion*100:.1f}%")

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df.index, prices, color='#58a6ff', label='Price')
    ax.plot(df.index, sma_200, color='orange', linestyle='--', label='200-SMA')
    ax.set_facecolor('#0e1117')
    fig.patch.set_facecolor('#0e1117')
    ax.tick_params(colors='white')
    ax.legend()
    st.pyplot(fig)

    is_uptrend = current_price > sma_200.iloc[-1]
    if bs_prob > 0.55 and is_uptrend:
        st.success(f"**CONVERGENCE:** Mathematical conviction ({bs_prob*100:.1f}%) aligns with structural trend.")
    elif bs_prob < 0.40:
        st.warning(f"**CAUTION:** Probabilistic model indicates low statistical edge.")
    else:
        st.info("**NEUTRAL:** Wait for trend confirmation or volatility contraction.")

# SECTION 5: MAIN INTERFACE (Relocated to Main Page)
def main():
    st.title("📊 Quantitative Risk Engine v4.2")
    st.markdown("Select an asset to initiate advanced probabilistic analysis.")

    # Main Control Panel
    with st.container():
        st.markdown('<div class="main-control">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            mode = st.selectbox("Select Mode:", ["STOCKS", "INDICES", "SEARCH"])
        
        selected_ticker = None
        
        with col2:
            if mode == "STOCKS":
                cat = st.selectbox("Sector:", list(STOCKS_DB.keys()))
                selected_ticker = st.selectbox("Asset:", STOCKS_DB[cat])
            elif mode == "INDICES":
                cat = st.selectbox("Market:", list(INDICES_DB.keys()))
                choice = st.selectbox("Index:", list(INDICES_DB[cat].keys()))
                selected_ticker = choice
            else:
                selected_ticker = st.text_input("Enter Ticker (e.g., TSLA):").upper()

        with col3:
            st.markdown("<br>", unsafe_allow_html=True) # Spacer
            run_btn = st.button("INITIATE ANALYSIS", type="primary")
        
        st.markdown('</div>', unsafe_allow_html=True)

    if run_btn and selected_ticker:
        run_analysis(selected_ticker)

    # Sidebar remains for documentation only
    st.sidebar.subheader("SYSTEM ARCHITECTURE")
    st.sidebar.info("""
    - **Logic:** BS-Model + Student's t-adjustment.
    - **Volatility:** Regime-weighted realized vol.
    - **Risk:** Fractional Kelly allocation.
    - **Structure:** 200-day SMA trend filtering.
    """)

if __name__ == "__main__":
    main()