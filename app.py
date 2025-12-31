import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm, t
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta

# CONFIGURATION & PAGE SETUP
st.set_page_config(page_title="Quantitative Risk Engine v4.4.1", layout="wide")

# Custom CSS for Analytic Theme
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    .stButton>button { background-color: #262730; border: 1px solid #4e535e; color: white; width: 100%; height: 3em; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Courier New', monospace; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .main-control { background-color: #1c2128; padding: 20px; border-radius: 15px; border: 1px solid #444c56; margin-bottom: 25px; }
    .macro-alert { background-color: #2a1b1b; padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b; color: #ff4b4b; font-weight: bold; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# SECTION 1: MACRO EVENT DATABASE (2026 Projections)
MACRO_EVENTS = [
    {"date": "2026-01-14", "label": "US CPI (Inflation Data)"},
    {"date": "2026-01-28", "label": "FOMC Interest Rate Decision"},
    {"date": "2026-02-11", "label": "US CPI (Inflation Data)"},
    {"date": "2026-03-18", "label": "FOMC Interest Rate Decision"},
    {"date": "2026-02-10", "label": "Riksbanken Räntebesked"}
]

# SECTION 2: MASTER ASSET DATABASE
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

# SECTION 3: ADVANCED MATH ENGINE
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
        target_move = 1.020 if (ticker.startswith("^") or ticker in ["SPUS"]) else 1.045
        K = S * target_move 
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        return t.cdf(d1, df=5) 

class IndicatorBuilder:
    @staticmethod
    def calculate_volatility_regime(prices):
        returns = np.log(prices / prices.shift(1))
        # Kombinerar 30-dagars och 10-dagars vol för att fånga regimskiften
        hist_vol = returns.rolling(window=30).std() * np.sqrt(252)
        short_vol = returns.rolling(window=10).std() * np.sqrt(252)
        return (hist_vol + short_vol) / 2

# SECTION 4: MACRO LOGIC
def check_macro_proximity():
    today = datetime.now()
    active_events = []
    for event in MACRO_EVENTS:
        # KORRIGERAT DATUMFORMAT: %m och %d istället för %MM %DD
        event_date = datetime.strptime(event['date'], "%Y-%m-%d")
        diff = (event_date - today).days
        if 0 <= diff <= 2: 
            active_events.append(f"{event['label']} in {diff} days")
    return active_events

# SECTION 5: ANALYSIS EXECUTION
def run_analysis(ticker):
    st.markdown("---")
    macro_risks = check_macro_proximity()
    
    if macro_risks:
        for risk in macro_risks:
            st.markdown(f'<div class="macro-alert">⚠️ MACRO OVERLAY ACTIVE: {risk}</div>', unsafe_allow_html=True)
        st.write("*System conviction automatically adjusted due to exogenous event risk.*")

    try:
        df = yf.download(ticker, period="2y", progress=False, multi_level_index=False)
        prices = df['Close']
        current_price = float(prices.iloc[-1])
        vol_regime = IndicatorBuilder.calculate_volatility_regime(prices)
        current_vol = float(vol_regime.iloc[-1])
        sma_200 = float(prices.rolling(200).mean().iloc[-1])
        
        prob = MathEngine.black_scholes_tail_adjusted(current_price, 0.045, current_vol, 30, ticker)
        kelly_suggestion = MathEngine.calculate_kelly(prob)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Price", f"${current_price:.2f}")
        m2.metric("Probability", f"{prob*100:.1f}%")
        m3.metric("Regime Vol.", f"{current_vol*100:.1f}%")
        m4.metric("Kelly Allocation", f"{kelly_suggestion*100:.1f}%")

        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(df.index, prices, color='#58a6ff', label='Price')
        ax.plot(df.index, prices.rolling(200).mean(), color='orange', linestyle='--', label='200-SMA')
        ax.set_facecolor('#0e1117')
        fig.patch.set_facecolor('#0e1117')
        ax.tick_params(colors='white')
        ax.legend()
        st.pyplot(fig)

        st.subheader("QUANTITATIVE VERDICT")
        is_uptrend = current_price > sma_200
        
        if macro_risks:
            st.warning("**CAUTION: Macro-Event Suppression Active.**")
            st.write("*The model identifies upcoming systematic risk. Statistical edge is secondary to potential event-driven volatility shocks. Capital preservation is prioritized.*")
        elif prob > 0.55 and is_uptrend:
            st.success("**CONVERGENCE: Statistical edge is confirmed.**")
            st.write("*The system identifies a 'High-Conviction' state. Probability density is clustered above the price target while the asset maintains positive structural momentum. Probabilistic modeling supports directional expansion.*")
        elif prob < 0.30:
            st.warning("**CAUTION: Insufficient statistical conviction.**")
            st.write("*The model identifies excessive market noise where current volatility exceeds standard predictive limits. Statistical conviction is insufficient, indicating an unfavorable risk/reward profile.*")
        else:
            st.info("**NEUTRAL: Market indecision or mean reversion phase.**")
            st.write("*The asset is in a 'Mean Reversion' or 'Indecision' phase. While probabilistic modeling indicates moderate potential, the lack of a confirmed structural trend suggests waiting for a cleaner breakout signal.*")

    except Exception as e:
        st.error(f"Analysis failed: {e}")

# SECTION 6: MAIN INTERFACE
def main():
    st.title("📊 Quantitative Risk Engine v4.4.1")
    
    with st.container():
        st.markdown('<div class="main-control">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            mode = st.selectbox("Select Mode:", ["STOCKS", "INDICES", "SEARCH"])
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
    - **Macro:** Event-Timer Proximity Override.
    - **Volatility:** Regime-weighted realized vol.
    - **Risk:** Fractional Kelly allocation.
    """)

if __name__ == "__main__":
    main()