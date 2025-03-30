import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="Investment Portfolio Analyzer", layout="wide")

# App title
st.title("📊 Investment Portfolio Analyzer")

# API Key (Replace this with your Alpha Vantage API key)
API_KEY = "YOUR_API_KEY"

# Function to fetch stock data from Alpha Vantage
@st.cache_data
def get_stock_data(ticker):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "apikey": API_KEY,
        "outputsize": "compact"
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()

    if "Time Series (Daily)" not in data:
        st.error(f"❌ Invalid stock symbol or API limit reached: {ticker}")
        return None

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
    df = df.rename(columns={"5. adjusted close": "Adj Close"}).astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    
    return df

# Sidebar user input
st.sidebar.header("Portfolio Input")
tickers_input = st.sidebar.text_input("Enter stock symbols (comma separated):", "AAPL, MSFT, TSLA")
tickers = [t.strip().upper() for t in tickers_input.split(",")]

num_shares_input = st.sidebar.text_input("Enter number of shares (comma separated):", "10, 5, 8")
num_shares = [int(n.strip()) for n in num_shares_input.split(",")]

purchase_prices_input = st.sidebar.text_input("Enter purchase price per share (comma separated):", "150, 250, 700")
purchase_prices = [float(p.strip()) for p in purchase_prices_input.split(",")]

start_date = st.sidebar.date_input("Select start date for performance analysis", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("Select end date", pd.to_datetime("today"))

# Fetch data for each stock
stock_data = {}
valid_tickers = []

for ticker in tickers:
    data = get_stock_data(ticker)
    if data is not None:
        stock_data[ticker] = data["Adj Close"]
        valid_tickers.append(ticker)

if not stock_data:
    st.error("❌ No valid stock data found. Check stock symbols and API key.")
    st.stop()

stock_df = pd.DataFrame(stock_data)

# Portfolio Analysis
portfolio = pd.DataFrame({
    "Ticker": valid_tickers,
    "Shares": num_shares[:len(valid_tickers)],  # Adjust length in case of invalid tickers
    "Purchase Price": purchase_prices[:len(valid_tickers)]
})

portfolio["Current Price"] = [stock_df[t].dropna().iloc[-1] for t in valid_tickers]
portfolio["Investment"] = portfolio["Shares"] * portfolio["Purchase Price"]
portfolio["Current Value"] = portfolio["Shares"] * portfolio["Current Price"]
portfolio["Profit/Loss"] = portfolio["Current Value"] - portfolio["Investment"]
portfolio["Return (%)"] = (portfolio["Profit/Loss"] / portfolio["Investment"]) * 100

st.subheader("Portfolio Summary")
st.dataframe(portfolio)

# Portfolio Value Over Time
st.subheader("📈 Portfolio Performance Over Time")
fig, ax = plt.subplots(figsize=(10, 5))
stock_df.plot(ax=ax)
st.pyplot(fig)

# Asset Allocation Pie Chart
st.subheader("📊 Asset Allocation")
fig, ax = plt.subplots()
ax.pie(portfolio["Current Value"], labels=portfolio["Ticker"], autopct="%1.1f%%", startangle=140)
st.pyplot(fig)

# Performance Metrics
st.subheader("📊 Portfolio Performance Metrics")
portfolio_returns = stock_df.pct_change().dropna()
portfolio_std = portfolio_returns.std().mean() * np.sqrt(252)
sharpe_ratio = portfolio_returns.mean().mean() / portfolio_std * np.sqrt(252)

st.metric(label="Portfolio Volatility", value=f"{portfolio_std:.2%}")
st.metric(label="Sharpe Ratio", value=f"{sharpe_ratio:.2f}")
