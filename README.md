# FX-Imbalance-Dashboard [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1m3Gsfx8VUI4z3Z7ry1aZTAwq6HGo5XR8?usp=sharing)
This Plotly Dashboard explores how growth in **M2 Money Supply** might be affecting **GBP/USD spot currency exchange rate (CABLE)**. Live Dashboard is hosted on [**Render.com**](https://fx-currency-imbalance.onrender.com/).
## Tutorial:
![](https://github.com/viczommers/FX-Imbalance-Dashboard/blob/main/FX_Tutorial.gif)
## Resources:
- M2 = Cash in Circulation + Checking Accounts in Banks + Savings Accounts in Banks 
- [1. M2 ($, Seasonally Adj.), FRED](https://fred.stlouisfed.org/series/M2SL)
- [2. M2 (£, Seasonally Adj.), BOE](https://www.bankofengland.co.uk/boeapps/database/FromShowColumns.asp?Travel=&searchText=LPMVWYW)  

**Business Objective:**
Dashboard connects to FRED API through ```pandas-datareader``` and to Bank of England Database through ```requests``` library to fetch data. The dashboard plots monthly Money Supply (total money in circulation) in the US and UK and overlays it over daily FX rate. Dashboard also calculates correlation matrix. (Note: I suggest using Monthly weighted exchange rate, instead of Daily/End-of-Month rate to accurately capture corr between Money Base and FX)  

**Business Logic:**
Imagine fluctuations in FX exchange rate as a divergence between growth rates of 2 money supplies:
- If Money Supply of $ increases, while Money Supply of £ stays the same - Dollar would depreciate against Pound, ceteris paribus
- If Money Supply of $ decreases, while Money Supply of £ stays the same - Dollar would appreciate against Pound, ceteris paribus  

**Graphic Objective:**
I wanted to explore alternative visualisation techniques for plotting multivariate time-series data, specifically to move beyond always having time dimension on X-axis. I also wanted to experiment with darker themes.
