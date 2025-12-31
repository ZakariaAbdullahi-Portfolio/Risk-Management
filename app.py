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