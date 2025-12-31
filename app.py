import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm, t
import matplotlib.pyplot as plt
import streamlit as st

# ==========================================
# CONFIGURATION & GLOBAL STYLING
# ==========================================
st.set_page_config(page_title="Quantitative Risk Engine v4.1", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    .stButton>button { 
        background-color: #238636; 
        border: 1px solid #2ea043; 
        color: white; 
        width: 100%; 
        font-weight: bold;
    }
    h1, h2, h3 { color: #58a6ff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stMetric { 
        background-color: #161b22; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #30363d; 
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# ASSET ARCHIVE
# ==========================================
INDICES_DB = {
    "US EQUITIES": {"^GSPC": "S&P 500 Index", "^IXIC": "NASDAQ 100", "^DJI": "Dow Jones Industrial", "^RUT": "Russell 2000"},
    "SHARIA COMPLIANT": {"SPUS": "S&P 500 Sharia ETF", "HLAL": "Wahed FTSE USA Sharia"},
    "GLOBAL": {"^STOXX50E": "Euro Stoxx 50", "^OMX": "OMX Stockholm 30", "^N225": "Nikkei 225"}
}

STOCKS_DB = {
    "TECHNOLOGY": ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"],
    "NORDIC MARKETS": ["VOLV-B.ST", "ERIC-B.ST", "AZN.ST", "HM-B.ST", "INVE-B.ST"],
    "FINANCE/HEALTH": ["JPM", "BAC", "GS", "LLY", "JNJ", "PFE"]
}

# ==========================================
# QUANTITATIVE COMPUTATION ENGINE
# ==========================================
class RiskEngine:
    @staticmethod
    def get_black_scholes_probability(S, r, sigma, days, ticker):
        T = days / 365
        if T <= 0 or sigma <= 0: return 0.0
        
        is_index = ticker.startswith("^") or ticker in ["SPUS", "HLAL"]
        target_multiplier = 1.020 if is_index else 1.045
        K = S * target_multiplier
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        # Use Student's t-distribution for Fat-Tails
        return t.cdf(d1, df=5)

    @staticmethod
    def calculate_kelly_criterion(win_prob, edge_ratio=1.5):
        loss_prob = 1 - win_prob
        kelly_fraction = (win_prob * edge_ratio - loss_prob) / edge_ratio
        return max(0, kelly_fraction * 0.25)

# ==========================================
# SIGNAL PROCESSING
# ==========================================
class SignalProcessor:
    @staticmethod
    def get_regime_volatility(prices, window=30):
        log_returns = np.log(prices / prices.shift(1))
        long_term_vol = log_returns.rolling(window=window).std() * np.sqrt(252)
        short_term_vol = log_returns.rolling(window=10).std() * np.sqrt(252)
        return (long_term_vol * 0.6) + (short_term_vol * 0.4)

    @staticmethod
    def get_market_structure(prices):
        sma_200 = prices.rolling(window=200).mean()
        return sma_200

# ==========================================
# ANALYSIS EXECUTION
# ==========================================
def execute_terminal_analysis(ticker):
    st.subheader(f"TERMINAL OUTPUT: {ticker}")
    
    try:
        df = yf.download(ticker, period="2y", progress=False, multi_level_index=False)
        if df.empty or len(df) < 200:
            st.error("Insufficient historical data.")
            return
    except Exception as e:
        st.error(f"DATA FEED ERROR: {str(e)}"); return

    prices = df['Close']
    current_price = float(prices.iloc[-1])
    vol_series = SignalProcessor.get_regime_volatility(prices)
    current_vol = float(vol_series.iloc[-1])
    sma_200 = SignalProcessor.get_market_structure(prices)
    
    probability = RiskEngine.get_black_scholes_probability(current_price, 0.045, current_vol, 30, ticker)
    suggested_allocation = RiskEngine.calculate_kelly_criterion(probability)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Market Price", f"${current_price:.2f}")
    col2.metric("Probability", f"{probability*100:.1f}%")
    col3.metric("Regime Volatility", f"{current_vol*100:.1f}%")
    col4.metric("Kelly Allocation", f"{suggested_allocation*100:.1f}%")

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df.index, prices, label='Price', color='#58a6ff', linewidth=2)
    ax.plot(df.index, sma_200, label='Institutional Trend (200 SMA)', color='#ff7b72', linestyle='--')
    ax.set_facecolor('#0d1117')
    fig.patch.set_facecolor('#0d1117')
    ax.tick_params(colors='white')
    ax.legend()
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("STRATEGIC VERDICT")
    trend_aligned = current_price > sma_200.iloc[-1]
    
    if probability > 0.55 and trend_aligned:
        st.success(f"**CONVERGENCE:** Mathematical conviction ({probability*100:.1f}%) aligns with structural trend.")
    elif not trend_aligned:
        st.error(f"**STRUCTURAL WEAKNESS:** Asset is trading below institutional support (200 SMA).")
    else:
        st.warning(f"**LOW CONVICTION:** Volatility regime devalues the predictive edge.")

# ==========================================
# MAIN INTERFACE
# ==========================================
def main():
    st.sidebar.title("QUANT TERMINAL")
    st.sidebar.caption("Public Risk Management Edition v4.1")
    st.sidebar.markdown("---")
    
    mode = st.sidebar.selectbox("Market Source:", ["STOCK DATABASE", "GLOBAL INDICES", "MANUAL SEARCH"])
    selected_ticker = None

    if mode == "STOCK DATABASE":
        sector = st.sidebar.selectbox("Sector:", list(STOCKS_DB.keys()))
        selected_ticker = st.sidebar.selectbox("Asset:", STOCKS_DB[sector])
    elif mode == "GLOBAL INDICES":
        region = st.sidebar.selectbox("Region:", list(INDICES_DB.keys()))
        selected_ticker = st.sidebar.selectbox("Index:", list(INDICES_DB[region].keys()))
    else:
        selected_ticker = st.sidebar.text_input("Enter Ticker:").upper()

    st.sidebar.markdown(" ")
    if st.sidebar.button("INITIATE RISK ANALYSIS"):
        if selected_ticker: execute_terminal_analysis(selected_ticker)

    st.sidebar.markdown("---")
    st.sidebar.subheader("SYSTEM SPECS")
    st.sidebar.write("● **Model:** BS-Merton + Student's t")
    st.sidebar.write("● **Vol Engine:** Dynamic Regime Weighting")
    st.sidebar.write("● **Positioning:** Fractional Kelly (0.25x)")

if __name__ == "__main__":
    main()