# Risk-Management

# Quantitative Risk Management System v4.0

### ⚠️ Status: Active | Protocol: "Stay Liquid"

## 1. System Overview
This repository contains a proprietary algorithmic trading engine transformed into a **Streamlit Web Application**. The system combines classical statistical mechanics (**Black-Scholes Model**) with modern technical analysis to identify high-probability entry and exit points in global markets.

Unlike standard screeners, this engine calculates the mathematical probability of price action using volatility surfaces and momentum logic.

## 2. Core Features

### 🧠 The Math Engine
* **Black-Scholes Probability:** Calculates the likelihood of an asset hitting a profit target within 30 days based on implied volatility ($\sigma$) and risk-free rates ($r$).
* **Fortress Logic:** Trades are only flagged if mathematical probability aligns with technical trend indicators.

### 📊 Dashboard & Data Coverage
The system features a fully interactive GUI with three analysis modes:
1.  **Top 100 Stocks:** Deep-dive into categorized equities (Magnificent 7, Nordic Giants, Banking, Energy).
2.  **Global Indices:** Real-time analysis of major world markets, including specialized **Sharia Compliant (S&P 500 Sharia)** and Ethical indices.
3.  **Manual Search:** Flexible ticker lookup for any asset available on Yahoo Finance.

## 3. Tech Stack
* **Frontend:** Streamlit (Python Web Framework)
* **Data Feed:** yFinance API (Real-time market data)
* **Analysis:** NumPy, Pandas, SciPy (Statistical modeling)
* **Visualization:** Matplotlib

## 4. Installation & Usage

**Prerequisites:** Python 3.8+

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/ZakariaAbdullahi-Portfolio/Risk-Management.git](https://github.com/ZakariaAbdullahi-Portfolio/Risk-Management.git)
    cd Risk-Management
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Launch the Dashboard**
    ```bash
    streamlit run app.py
    ```

---
*Disclaimer: This software is for educational and analytical purposes only. Always manage your risk.*