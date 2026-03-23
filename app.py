import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import t
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime

# CONFIGURATION & PAGE SETUP
st.set_page_config(page_title="Quantitative Risk Engine v4.5", layout="wide")

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

# SECTION 1: MACRO EVENT DATABASE
MACRO_EVENTS = [
    {"date": "2026-01-14", "label": "US CPI (Inflation Data)"},
    {"date": "2026-01-28", "label": "FOMC Interest Rate Decision"},
    {"date": "2026-02-11", "label": "US CPI (Inflation Data)"},
    {"date": "2026-03-18", "label": "FOMC Interest Rate Decision"},
    {"date": "2026-02-10", "label": "Riksbanken Rate Decision"}
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
        return max(0, k * 0.25) # Fractional Kelly (25% of full size)

    @staticmethod
    def black_scholes_tail_adjusted(S, r, sigma, days, ticker):
        T = days / 365
        if T <= 0 or sigma <= 0: return 0.0
        # OBJECTIVE CALIBRATION: 1.5% for indices, 3.0% for individual stocks
        target_move = 1.015 if (ticker.startswith("^") or ticker in ["SPUS"]) else 1.030
        K = S * target_move 
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        return t.cdf(d1, df=5) # Student's t-distribution for Fat-Tails

class IndicatorBuilder:
    @staticmethod
    def calculate_volatility_regime(prices):
        returns = np.log(prices / prices.shift(1))
        vol = returns.rolling(window=20).std() * np.sqrt(252)
        return vol

# SECTION 4: MACRO LOGIC
def check_macro_proximity():
    today = datetime.now()
    active_events = []
    for event in MACRO_EVENTS:
        event_date = datetime.strptime(event['date'], "%Y-%m-%d")
        diff = (event_date - today).days
        if 0 <= diff <= 2: 
            active_events.append(f"{event['label']} in {diff} days")
    return active_events

# SECTION 5: DATA FETCHING LAYER
@st.cache_data(ttl=3600, show_spinner="Fetching market data...") 
def fetch_market_data(ticker):
    """
    Fetches historical data in isolation.
    Forces cache update after 1 hour to prevent stale data.
    """
    try:
        # Enforce timeout to prevent infinite hanging
        df = yf.download(ticker, period="2y", progress=False, timeout=10)
        
        # Handle MultiIndex returned by newer yfinance versions
        if isinstance(df.columns, pd.MultiIndex):
            prices = df['Close'][ticker]
        else:
            prices = df['Close']
            
        return prices.dropna()
    except Exception as e:
        st.error(f"Network error during fetch for {ticker}: {e}")
        return None

# SECTION 6: ANALYSIS EXECUTION
def run_analysis(ticker):
    st.markdown("---")
    macro_risks = check_macro_proximity()
    
    if macro_risks:
        for risk in macro_risks:
            st.markdown(f'<div class="macro-alert">MACRO OVERLAY ACTIVE: {risk}</div>', unsafe_allow_html=True)
        st.write("*System conviction automatically adjusted due to exogenous event risk.*")

    # Fetch cached data
    prices = fetch_market_data(ticker)
    
    if prices is None or prices.empty:
        st.error("Failed to retrieve valid price data. Aborting analysis.")
        return

    try:
        current_price = float(prices.iloc[-1])
        vol_regime = IndicatorBuilder.calculate_volatility_regime(prices)
        current_vol = float(vol_regime.iloc[-1])
        sma_200 = float(prices.rolling(200).mean().iloc[-1])
        
        prob = MathEngine.black_scholes_tail_adjusted(current_price, 0.045, current_vol, 30, ticker)
        kelly_suggestion = MathEngine.calculate_kelly(prob)

        # Output Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Price", f"${current_price:.2f}")
        m2.metric("Probability", f"{prob*100:.1f}%")
        m3.metric("Regime Vol.", f"{current_vol*100:.1f}%")
        m4.metric("Kelly Allocation", f"{kelly_suggestion*100:.1f}%")

        # Visualization
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(prices.index, prices, color='#58a6ff', label='Price', linewidth=1.5)
        ax.plot(prices.index, prices.rolling(200).mean(), color='orange', linestyle='--', label='200-day SMA')
        ax.set_facecolor('#0e1117')
        fig.patch.set_facecolor('#0e1117')
        ax.tick_params(colors='white')
        ax.legend()
        st.pyplot(fig)

        # QUANTITATIVE VERDICT LOGIC
        st.subheader("QUANTITATIVE VERDICT")
        is_uptrend = current_price > sma_200
        
        if macro_risks:
            st.warning("**CAUTION: Macro-Event Suppression Active.**")
            st.write("*The model identifies upcoming systematic risk. Statistical edge is secondary to potential event-driven volatility shocks. Capital preservation is prioritized.*")
        elif prob >= 0.50 and is_uptrend:
            st.success("**CONVERGENCE: Statistical edge is confirmed.**")
            st.write("*The system identifies a 'High-Conviction' state. Probabilistic modeling indicates an edge above 50% while the asset maintains positive structural momentum above the 200-day SMA.*")
        elif prob < 0.35:
            st.warning("**CAUTION: Insufficient statistical conviction.**")
            st.write("*The model identifies excessive market noise where current volatility exceeds standard predictive limits. Statistical conviction is insufficient, indicating an unfavorable risk/reward profile.*")
        else:
            st.info("**NEUTRAL: Market indecision or mean reversion phase.**")
            st.write("*The asset is in a 'Mean Reversion' or 'Indecision' phase. While probabilistic modeling indicates moderate potential, the lack of a confirmed structural trend suggests waiting for a cleaner breakout signal.*")

    except Exception as e:
        st.error(f"Calculation error during analysis: {e}")

# SECTION 7: MAIN INTERFACE
def main():
    st.title("Quantitative Risk Engine v4.5")
    st.markdown("Advanced probabilistic analysis and risk management.")

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
    - **Logic:** Black-Scholes + Student's t-adjustment.
    - **Target:** 3.0% (Stocks) / 1.5% (Indices).
    - **Macro:** Event-Timer Proximity Override.
    - **Risk:** Fractional Kelly Allocation.
    """)

if __name__ == "__main__":
    main()