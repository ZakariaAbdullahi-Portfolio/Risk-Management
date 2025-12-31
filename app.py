import numpy as np
import pandas as pd
import yfinance as yf
from scipy.stats import norm
import matplotlib.pyplot as plt
import sys
import math


# MASTER ASSET DATABASE (CATEGORIZED)
INDICES_DB = {
    'US MARKETS': {
        '^GSPC': 'S&P 500 (US Large Cap)',
        '^IXIC': 'NASDAQ 100 (Tech)',
        '^DJI': 'Dow Jones Industrial',
        '^RUT': 'Russell 2000 (Small Cap)'
    },
    'SHARIA & ETHICAL': {
        'SPUS': 'S&P 500 Sharia (US)',
        'HLAL': 'Wahed FTSE USA Sharia',
        'SPSK': 'SP Funds Global Sukuk',
        'UMMA': 'Wahed Dow Jones Islamic'
    },
    'EUROPE': {
        '^STOXX50E': 'Euro Stoxx 50 (Europe)',
        '^FTSE': 'FTSE 100 (UK)',
        '^GDAXI': 'DAX 40 (Germany)',
        '^FCHI': 'CAC 40 (France)',
        '^OMX': 'OMX Stockholm 30',
        '^OMXC25': 'OMX Copenhagen 25'
    },
    'ASIA & EMERGING': {
        '^N225': 'Nikkei 225 (Japan)',
        '^HSI': 'Hang Seng (Hong Kong)',
        '^BSESN': 'BSE SENSEX (India)',
        '000001.SS': 'Shanghai Composite'
    }
}


STOCKS_DB = {
    'MAGNIFICENT 7 (TECH)': {
        'NVDA': 'NVIDIA Corp',
        'AAPL': 'Apple Inc',
        'MSFT': 'Microsoft Corp',
        'GOOGL': 'Alphabet (Google)',
        'AMZN': 'Amazon.com',
        'TSLA': 'Tesla Inc',
        'META': 'Meta Platforms'
    },
    'NORDIC GIANTS': {
        'VOLV-B.ST': 'Volvo Group',
        'ERIC-B.ST': 'Ericsson',
        'AZN.ST': 'AstraZeneca',
        'HM-B.ST': 'Hennes & Mauritz',
        'INVE-B.ST': 'Investor AB',
        'EQNR.OL': 'Equinor (Norway)',
        'NOVO-B.CO': 'Novo Nordisk (Denmark)'
    },
    'FINANCE & BANKING': {
        'JPM': 'JPMorgan Chase',
        'V': 'Visa Inc',
        'MA': 'Mastercard',
        'BAC': 'Bank of America',
        'SEB-A.ST': 'SEB Bank'
    }
}

# MATH ENGINE & INDICATORS Black-Scholes Model
class MathEngine:
    @staticmethod
    def calculate_mean(data):
        return sum(data) / len(data) if len(data) > 0 else 0

    @staticmethod
    def calculate_std_dev(data):
        if len(data) < 2: return 0
        mean = MathEngine.calculate_mean(data)
        variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
        return math.sqrt(variance)

    @staticmethod
    def black_scholes_probability(S, r, sigma, t):
        # S=Price, r=Risk-free rate, sigma=Volatility, t=Time
        if t <= 0 or sigma == 0: return 0.0
        K = S * (1 + (r * t)) 
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * t) / (sigma * np.sqrt(t))
        return norm.cdf(d1)

class IndicatorBuilder:
    @staticmethod
    def calculate_sma(prices, period):
        return pd.Series(prices).rolling(window=period).mean().tolist()

    @staticmethod
    def calculate_rsi(prices, period=14):
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return (100 - (100 / (1 + rs))).tolist()

    @staticmethod
    def calculate_volatility(prices, window):
        log_ret = np.log(pd.Series(prices) / pd.Series(prices).shift(1))
        return (log_ret.rolling(window=window).std() * np.sqrt(252)).tolist()
    

# Trading System 
# ==============================================================================
# SECTION 3: TRADING SYSTEM
# ==============================================================================

class TradingSystem:
    def __init__(self, ticker):
        self.ticker = ticker
        self.r = 0.045 # Risk-free rate (approx 4.5%)
        
    def fetch_data(self):
        print(f"\n[SYSTEM] Connecting to Exchange API for {self.ticker}...")
        try:
            return yf.download(self.ticker, period="3y", progress=False, multi_level_index=False)
        except: return None

    def analyze(self, df, capital):
        prices = df['Close'].tolist()
        dates = df.index.tolist()
        sma_50 = IndicatorBuilder.calculate_sma(prices, 50)
        sma_200 = IndicatorBuilder.calculate_sma(prices, 200)
        rsi = IndicatorBuilder.calculate_rsi(prices, 14)
        hist_vol = IndicatorBuilder.calculate_volatility(prices, 30)
        
        position = None
        curr_cap = capital
        buys, sells = [], []

        print("[SYSTEM] Executing Fortress Logic...")
        for i in range(200, len(prices)):
            price = prices[i]
            date = dates[i]
            vol = hist_vol[i]
            # Black-Scholes Probability
            prob = MathEngine.black_scholes_probability(price, self.r, vol, 30/365)
            
            if position is None:
                # BUY LOGIC: Trend + Probability + Value
                if price > sma_200[i] and price > sma_50[i] and prob > 0.51 and rsi[i] < 70:
                    position = {'price': price, 'shares': curr_cap / price}
                    buys.append((date, price))
                    print(f"   [BUY]  {date.date()} | ${price:.2f} | Prob: {prob:.2f}")
            else:
                # SELL LOGIC: Stop Loss or Overbought
                stop = position['price'] * 0.95 
                if price < stop or rsi[i] > 80:
                    val = position['shares'] * price
                    curr_cap = val
                    sells.append((date, price))
                    print(f"   [SELL] {date.date()} | ${price:.2f} | Balance: ${curr_cap:.0f}")
                    position = None

        return curr_cap, df.iloc[200:], buys, sells

    def plot(self, df, buys, sells):
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Close'], label='Price', alpha=0.5)
        if buys: plt.scatter(*zip(*buys), marker='^', color='green', s=100, label='Buy')
        if sells: plt.scatter(*zip(*sells), marker='v', color='red', s=100, label='Sell')
        plt.title(f"Analysis: {self.ticker}")
        plt.show()

# ==============================================================================
# MAIN MENU
# ==============================================================================

if __name__ == "__main__":
    print("\n=== RISK MANAGEMENT SYSTEM v4.0 ===")
    print("1. US INDICES (SP500, NASDAQ)")
    print("2. TECH GIANTS (NVDA, APPLE)")
    print("3. SEARCH MANUALLY")
    
    c = input("Select Option: ")
    ticker = None
    
    if c == '1': ticker = '^GSPC' # S&P 500
    elif c == '2': ticker = 'NVDA'
    elif c == '3': ticker = input("Enter Ticker (e.g., TSLA): ").upper()
    
    if ticker:
        sys = TradingSystem(ticker)
        data = sys.fetch_data()
        if data is not None and len(data) > 200:
            final_cap, _, _, _ = sys.analyze(data, 10000)
            print(f"\n[RESULT] Final Balance: ${final_cap:.2f}")
            sys.plot(data.iloc[200:], [], [])
        else:
            print("[ERROR] Could not fetch data.")