import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm, t
import matplotlib.pyplot as plt
import streamlit as st

# CONFIGURATION & GLOBAL STYLING
st.set_page_config(page_title="Quantitative Risk Engine v4.2", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    .stButton>button { 
        background-color: #238636; border: 1px solid #2ea043; color: white; 
        width: 100%; font-weight: bold; height: 3em;
    }
    h1, h2, h3 { color: #58a6ff; font-family: 'Segoe UI', sans-serif; }
    .stMetric { 
        background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; 
    }
    .stAlert { background-color: #161b22; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# ASSET ARCHIVE
INDICES_DB = {
    "US MARKETS": {"^GSPC": "S&P 500 Index", "^IXIC": "NASDAQ 100", "^DJI": "Dow Jones Industrial", "^RUT": "Russell 2000"},
    "SHARIA COMPLIANT": {"SPUS": "S&P 500 Sharia (SP Funds)"},
    "GLOBAL MARKETS": {"^STOXX50E": "Euro Stoxx 50", "^OMX": "OMX Stockholm 30", "^N225": "Nikkei 225"}
}

STOCKS_DB = {
    "TECHNOLOGY": ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"],
    "NORDIC": ["VOLV-B.ST", "ERIC-B.ST", "AZN.ST", "HM-B.ST", "INVE-B.ST"],
    "FINANCIAL/HEALTH": ["JPM", "BAC", "GS", "LLY", "JNJ", "PFE"]
}

# QUANTITATIVE COMPUTATION ENGINE
class RiskEngine:
    @staticmethod
    def get_black_scholes_probability(S, r, sigma, days, ticker):
        T = days / 365
        if T <= 0 or sigma <= 0: return 0.0
        
        is_stable = ticker.startswith("^") or ticker == "SPUS"
        target_multiplier = 1.020 if is_stable else 1.045
        K = S * target_multiplier
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        # Student's t-distribution for Fat-Tail risk (df=5)
        return t.cdf(d1, df=5)

    @staticmethod
    def calculate_kelly_criterion(win_prob, edge_ratio=1.5):
        loss_prob = 1 - win_prob
        kelly_f = (win_prob * edge_ratio - loss_prob) / edge_ratio
        return max(0, kelly_f * 0.25)

# SIGNAL PROCESSING
class SignalProcessor:
    @staticmethod
    def get_regime_volatility(prices):
        log_rets = np.log(prices / prices.shift(1))
        return (log_rets.rolling(30).std() * np.sqrt(252) * 0.6) + (log_rets.rolling(10).std() * np.sqrt(252) * 0.4)

# ANALYSIS EXECUTION
def execute_terminal_analysis(ticker):
    st.subheader(f"TERMINAL ANALYSIS: {ticker}")
    
    try:
        df = yf.download(ticker, period="2y", progress=False, multi_level_index=False)
        if df.empty or len(df) < 200:
            st.error("DATABASE ERROR: Insufficient historical data."); return
    except Exception as e:
        st.error(f"DATA FEED ERROR: {str(e)} "); return

    prices = df['Close']
    curr_price = float(prices.iloc[-1])
    vol_series = SignalProcessor.get_regime_volatility(prices)
    curr_vol = float(vol_series.iloc[-1])
    sma_200 = prices.rolling(200).mean()
    curr_sma = float(sma_200.iloc[-1])
    
    prob = RiskEngine.get_black_scholes_probability(curr_price, 0.045, curr_vol, 30, ticker)
    kelly = RiskEngine.calculate_kelly_criterion(prob)

    # Metrics Layout
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Current Price", f"${curr_price:.2f}")
    m2.metric("Probability", f"{prob*100:.1f}%")
    m3.metric("Regime Volatility", f"{curr_vol*100:.1f}%")
    m4.metric("Kelly Allocation", f"{kelly*100:.1f}%")

    # Charting
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df.index, prices, label='Price', color='#58a6ff', linewidth=2)
    ax.plot(df.index, sma_200, label='200-SMA (Trend)', color='#ff7b72', linestyle='--')
    ax.set_facecolor('#0d1117'); fig.patch.set_facecolor('#0d1117')
    ax.tick_params(colors='white'); ax.legend(); ax.grid(alpha=0.1)
    st.pyplot(fig)

    # DETAILED ANALYSIS EXPLANATION
    st.markdown("---")
    st.subheader("STRATEGIC ANALYSIS AND VERDICT")
    
    uptrend = curr_price > curr_sma
    
    st.write("**Analysis Overview:**")
    
    if curr_vol > 0.30:
        st.write(f"**Volatility Regime:** Current volatility is elevated ({curr_vol*100:.1f}%). This indicates a high-noise environment where standard price targets are less reliable due to increased market variance.")
    else:
        st.write(f"**Volatility Regime:** Market volatility is currently stable. The mathematical model indicates a normalized distribution of price paths with higher predictive reliability.")

    if uptrend:
        st.write(f"**Market Structure:** The asset maintains a position above the 200-day Moving Average. This structural alignment suggests institutional support and a positive long-term momentum bias.")
    else:
        st.write(f"**Market Structure:** The asset is trading below the 200-day SMA. Historically, this indicates structural weakness and potential resistance from institutional sellers.")

    if prob > 0.50:
        st.write(f"**Statistical Conviction:** A probability of {prob*100:.1f}% indicates that the target move is mathematically viable within the current timeframe, accounting for fat-tail risks. The Kelly Criterion suggests a {kelly*100:.1f}% allocation to optimize the risk-reward ratio.")
    else:
        st.write(f"**Statistical Conviction:** The probability ({prob*100:.1f}%) is insufficient to establish a statistical edge. The model suggests zero or minimal capital allocation to preserve liquidity.")

    st.markdown(" ")
    if prob > 0.55 and uptrend:
        st.success("VERDICT: CONVERGENCE. Mathematical conviction and market structure are aligned for a high-probability setup.")
    elif not uptrend:
        st.error("VERDICT: STRUCTURAL RISK. Market structure is bearish. Quantitative signals are invalidated by trend resistance.")
    else:
        st.info("VERDICT: NEUTRAL. Statistical conviction is insufficient for high-conviction deployment.")

# MAIN INTERFACE
def main():
    st.sidebar.title("QUANT TERMINAL")
    st.sidebar.caption("v4.2 | Public Risk Management")
    st.sidebar.markdown("---")
    
    mode = st.sidebar.selectbox("Market Source:", ["STOCK DATABASE", "GLOBAL INDICES", "MANUAL SEARCH"])
    
    selected_ticker = None
    if mode == "STOCK DATABASE":
        sector = st.sidebar.selectbox("Sector:", list(STOCKS_DB.keys()))
        selected_ticker = st.sidebar.selectbox("Asset:", STOCKS_DB[sector])
    elif mode == "GLOBAL INDICES":
        region = st.sidebar.selectbox("Region/Category:", list(INDICES_DB.keys()))
        selected_ticker = st.sidebar.selectbox("Asset:", list(INDICES_DB[region].keys()))
    else:
        selected_ticker = st.sidebar.text_input("Enter Ticker:").upper()

    st.sidebar.markdown(" ")
    if st.sidebar.button("INITIATE RISK ANALYSIS"):
        if selected_ticker: execute_terminal_analysis(selected_ticker)

    st.sidebar.markdown("---")
    st.sidebar.subheader("SYSTEM ARCHITECTURE")
    st.sidebar.info("""
    - Model: Black-Scholes + Student's t (df=5).
    - Volatility: DVR (Dynamic Volatility Regime).
    - Allocation: Fractional Kelly Criterion.
    """)

if __name__ == "__main__":
    main()