# 🛡️ Quantitative Risk Engine v4.1 (Public Edition)
**A High-Precision Market Analysis Tool for Probabilistic Risk Management.**

---

## 📈 Overview
The **Quantitative Risk Engine** is a professional-grade analytical terminal designed to eliminate emotional bias from trading. By combining the **Black-Scholes-Merton** framework with advanced statistical adjustments for market "fat-tails," the engine provides users with a mathematically grounded probability of price targets being reached within a 30-day horizon.

This version (v4.1) has been specifically engineered for public use, integrating institutional risk management principles such as the **Kelly Criterion** and **Dynamic Volatility Regimes**.

---

## 🔬 Core Methodology

### 1. Fat-Tail Probability Modeling
Standard financial models often assume a Normal (Gaussian) distribution. However, real markets experience "Black Swan" events more frequently than standard models predict. 
- **The Solution:** Our engine utilizes a **Student’s t-distribution** with a fixed degree of freedom ($df=5$). This allows the model to account for "fat-tails," providing a more realistic and conservative probability estimate during periods of market stress.



### 2. Dynamic Volatility Regime (DVR)
Volatility is not constant. The engine implements a weighted regime-adjuster:
- **60% Weight:** Long-term historical volatility (30-day lookback).
- **40% Weight:** Short-term realized volatility (10-day lookback).
This captures **Volatility Clustering**—the phenomenon where high-volatility periods are followed by high-volatility periods—ensuring the engine reacts instantly to sudden market panic.

### 3. Capital Allocation via Kelly Criterion
To prevent over-leveraging, the engine integrates the **Kelly Criterion**, a formula used by professional fund managers to determine optimal position sizes.
- **Formula:** $K\% = \frac{bp - q}{b}$
- **Safety Feature:** We implement a **25% Fractional Kelly** constraint. This ensures that even in high-conviction scenarios, the suggested allocation remains conservative to protect user capital.

---

## 🛠️ Technical Stack
- **Language:** Python 3.12
- **Data Source:** Yahoo Finance API (Real-time & Historical)
- **Mathematical Libraries:** SciPy (Student's t-distribution), NumPy (Vectorized computations)
- **Frontend:** Streamlit (Analytical Dashboard)
- **Visuals:** Matplotlib (Institutional charting theme)

---

## 🚀 How to Use
1. **Select Market Source:** Choose between our curated high-liquidity stock database, global indices, or use the manual search for any ticker globally.
2. **Initiate Analysis:** The engine fetches 2 years of daily data to establish a structural baseline.
3. **Interpret Output:**
   - **Probability:** The statistical chance of a price move within 30 days.
   - **Kelly Allocation:** The suggested % of your portfolio to risk based on the mathematical edge.
   - **Institutional Trend:** Cross-reference with the 200-day Simple Moving Average (SMA).

---

## ⚠️ Risk Disclaimer
Quantitative modeling involves statistical probabilities, not certainties. Past performance and mathematical projections do not guarantee future results. This tool is designed for **analytical decision support** and should not be the sole basis for investment decisions.