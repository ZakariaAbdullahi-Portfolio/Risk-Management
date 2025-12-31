import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm, t
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime, timedelta

# CONFIGURATION & PAGE SETUP
st.set_page_config(page_title="Quantitative Risk Engine v4.4", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    .stButton>button { background-color: #262730; border: 1px solid #4e535e; color: white; width: 100%; height: 3em; }
    h1, h2, h3 { color: #58a6ff; font-family: 'Courier New', monospace; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .main-control { background-color: #1c2128; padding: 20px; border-radius: 15px; border: 1px solid #444c56; margin-bottom: 25px; }
    .macro-alert { background-color: #2a1b1b; padding: 10px; border-radius: 5px; border: 1px solid #ff4b4b; color: #ff4b4b; font-weight: bold; }
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

# SECTION 2: ASSET DATABASE
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
    "NORDIC": ["VOLV-B.ST", "ERIC-B.ST", "AZN.ST", "HM-B.ST", "INVE-B.ST"]
}

# SECTION 3: CORE ENGINES
class MathEngine:
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
        return (returns.rolling(30).std() + returns.rolling(10).std()) / 2 * np.sqrt(252)

# SECTION 4: MACRO LOGIC
def check_macro_proximity():
    today = datetime.now()
    active_events = []
    for event in MACRO_EVENTS:
        event_date = datetime.strptime(event['date'], "%Y-%MM-%DD")
        diff = (event_date - today).days
        if 0 <= diff <= 2: # 48 timmars fönster
            active_events.append(f"{event['label']} in {diff} days")
    return active_events

# SECTION 5: ANALYSIS EXECUTION
def run_analysis(ticker):
    st.markdown("---")
    macro_risks = check_macro_proximity()
    
    if macro_risks:
        for risk in macro_risks:
            st.markdown(f'<div class="macro-alert">⚠️ MACRO OVERLAY ACTIVE: {risk}</div>', unsafe_allow_html=True)
        st.write("*System conviction automatically capped due to exogenous event risk.*")

    try:
        df = yf.download(ticker, period="2y", progress=False, multi_level_index=False)
        prices = df['Close']
        current_price = float(prices.iloc[-1])
        vol_regime = IndicatorBuilder.calculate_volatility_regime(prices)
        current_vol = float(vol_regime.iloc[-1])
        sma_200 = float(prices.rolling(200).mean().iloc[-1])
        
        prob = MathEngine.black_scholes_tail_adjusted(current_price, 0.045, current_vol, 30, ticker)
        
        # Display Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Price", f"${current_price:.2f}")
        m2.metric("Probability", f"{prob*100:.1f}%")
        m3.metric("Regime Vol.", f"{current_vol*100:.1f}%")

        # VERDICT LOGIC WITH MACRO OVERRIDE
        st.subheader("QUANTITATIVE VERDICT")
        is_uptrend = current_price > sma_200
        
        if macro_risks:
            st.warning("**CAUTION: Macro-Event Suppression Active.**")
            st.write("*The model identifies upcoming systematic risk. Statistical edge is secondary to potential event-driven volatility shocks. Capital preservation is prioritized.*")
        elif prob > 0.55 and is_uptrend:
            st.success("**CONVERGENCE: Statistical edge is confirmed.**")
            st.write("*High-Conviction state: Probability density is clustered above price target and structural momentum is positive.*")
        elif prob < 0.30:
            st.warning("**CAUTION: Insufficient statistical conviction.**")
            st.write("*Excessive market noise identified. Statistical conviction is insufficient for a high-conviction trade entry.*")
        else:
            st.info("**NEUTRAL: Market indecision or mean reversion phase.**")
            st.write("*Probabilistic modeling indicates moderate potential, but lack of structural trend suggests waiting for a breakout.*")

    except Exception as e:
        st.error(f"Analysis failed: {e}")

# SECTION 6: MAIN
def main():
    st.title("📊 Quantitative Risk Engine v4.4")
    
    with st.container():
        st.markdown('<div class="main-control">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1: mode = st.selectbox("Mode:", ["STOCKS", "INDICES", "SEARCH"])
        with col2:
            if mode == "STOCKS": selected_ticker = st.selectbox("Asset:", STOCKS_DB["TECH"])
            elif mode == "INDICES":
                cat = st.selectbox("Market:", list(INDICES_DB.keys()))
                idx = st.selectbox("Index:", list(INDICES_DB[cat].keys()))
                selected_ticker = INDICES_DB[cat][idx]
            else: selected_ticker = st.text_input("Ticker:").upper()
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            run_btn = st.button("INITIATE ANALYSIS")
        st.markdown('</div>', unsafe_allow_html=True)

    if run_btn and selected_ticker:
        run_analysis(selected_ticker)

if __name__ == "__main__":
    main()