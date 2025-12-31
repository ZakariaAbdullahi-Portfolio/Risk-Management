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

# MATH ENGINE & INDICATORS
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
