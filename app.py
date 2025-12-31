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
    "US MARKETS": {
        "S&P 500": "^GSPC",
        "S&P 500 Sharia": "SPUS",
        "NASDAQ 100": "^IXIC",
        "Dow Jones": "^DJI",
        "Russell 2000": "^RUT"
    },
    "GLOBAL": {
        "Euro Stoxx 50": "^STOXX50E",
        "OMX Stockholm 30": "^OMX",
        "Nikkei 225": "^N225"
    }
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
    
    prob = MathEngine.black_scholes_tail_adjusted(current_price, 0.045, current_vol, 30, ticker)
    kelly_suggestion = MathEngine.calculate_kelly(prob)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Price", f"${current_price:.2f}")
    m2.metric("Probability", f"{prob*100:.1f}%")
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

    st.subheader("QUANTITATIVE VERDICT")
    is_uptrend = current_price > sma_200.iloc[-1]
    
    if prob > 0.55 and is_uptrend:
        st.success(f"**CONVERGENCE:** Mathematical conviction ({prob*100:.1f}%) aligns with structural trend.")
        st.write("""
        *The system identifies a 'High-Conviction' state. Probability density is clustered above the price target while 
        the asset maintains positive structural momentum above the 200-SMA. Statistical edge is confirmed.*
        """)
    elif prob < 0.30:
        st.warning(f"**CAUTION: Probabilistic model indicates low statistical edge.**")
        st.write("""
        *The model identifies high market 'noise' or a price target that exceeds current volatility limits. 
        Statistical conviction is low, suggesting that the current risk/reward profile is unfavorable.*
        """)
    else:
        st.info("**NEUTRAL: Wait for trend confirmation or volatility contraction.**")
        st.write("""
        *The asset is in a 'Mean Reversion' or 'Indecision' phase. While math shows moderate probability, 
        lack of structural trend or fluctuating volatility suggests waiting for a cleaner breakout signal.*
        """)

# SECTION 5: MAIN INTERFACE
def main():
    st.title("📊 Quantitative Risk Engine")
    st.markdown("Select an asset to initiate advanced probabilistic analysis.")

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
                cat_indices = st.selectbox("Market:", list(INDICES_DB.keys()))
                index_name = st.selectbox("Index:", list(INDICES_DB[cat_indices].keys()))
                selected_ticker = INDICES_DB[cat_indices][index_name]
            else:
                selected_ticker = st.text_input("Enter Ticker (e.g., TSLA):").upper()

        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            run_btn = st.button("INITIATE ANALYSIS", type="primary")
        
        st.markdown('</div>', unsafe_allow_html=True)

    if run_btn and selected_ticker:
        run_analysis(selected_ticker)

    st.sidebar.subheader("SYSTEM ARCHITECTURE")
    st.sidebar.info("""
    - **Logic:** Black-Scholes Model + Student's t-adjustment.
    - **Volatility:** Regime-weighted realized vol.
    - **Risk:** Fractional Kelly allocation.
    - **Structure:** 200-day SMA trend filtering.
    """)

if __name__ == "__main__":
    main()