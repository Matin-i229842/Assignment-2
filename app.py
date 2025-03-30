import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns

# Set page config
st.set_page_config(page_title="Investment Portfolio Analyzer", layout="wide")

# App title
st.title("📊 Investment Portfolio Analyzer")

# User Input Section
st.sidebar.header("Portfolio Input")

tickers = st.sidebar.text_input("Enter stock symbols (comma separated):", "AAPL, MSFT, TSLA")
tickers = [t.strip().upper() for t in tickers.split(",")]

num_shares = st.sidebar.text_input("Enter number of shares (comma separated):", "10, 5, 8")
num_shares = [int(n.strip()) for n in num_shares.split(",")]

purchase_prices = st.sidebar.text_input("Enter purchase price per share (comma separated):", "150, 250, 700")
purchase_prices = [float(p.strip()) for p in purchase_prices.split(",")]

start_date = st.sidebar.date_input("Select start date for performance analysis", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("Select end date", pd.to_datetime("today"))

# Fetch stock data with improved error handling
@st.cache_data
def get_stock_data(tickers, start_date, end_date):
    try:
        data = yf.download(tickers, start=start_date, end=end_date)

        # Check if data is empty
        if data.empty:
            st.error("⚠️ No stock data found. Check stock symbols and date range.")
            return None

        # Adjust handling for single vs. multiple tickers
        if len(tickers) > 1:
            if "Adj Close" in data.columns:
                return data["Adj Close"]
            else:
                st.error("❌ 'Adj Close' column missing. Try different stock symbols.")
                return None
        else:
            return data[["Adj Close"]] if "Adj Close" in data.columns else None

    except Exception as e:
        st.error(f"❌ Error fetching stock data: {str(e)}")
        return None

# Fetch stock data
stock_data = get_stock_data(tickers, start_date, end_date)

# Stop execution if no data is found
if stock_data is None or stock_data.empty:
    st.error("⚠️ No valid stock data available. Please check your stock symbols and date range.")
    st.stop()

# Portfolio Analysis
portfolio = pd.DataFrame({
    "Ticker": tickers,
    "Shares": num_shares,
    "Purchase Price": purchase_prices,
    "Current Price": [stock_data[t][-1] if t in stock_data.columns else np.nan for t in tickers],
})

# Drop tickers with missing price data
portfolio.dropna(inplace=True)

portfolio["Investment"] = portfolio["Shares"] * portfolio["Purchase Price"]
portfolio["Current Value"] = portfolio["Shares"] * portfolio["Current Price"]
portfolio["Profit/Loss"] = portfolio["Current Value"] - portfolio["Investment"]
portfolio["Return (%)"] = (portfolio["Profit/Loss"] / portfolio["Investment"]) * 100

st.subheader("Portfolio Summary")
st.dataframe(portfolio)

# Portfolio Value Over Time
st.subheader("📈 Portfolio Performance Over Time")
fig, ax = plt.subplots(figsize=(10, 5))
stock_data.plot(ax=ax)
st.pyplot(fig)

# Asset Allocation Pie Chart
st.subheader("📊 Asset Allocation")
fig, ax = plt.subplots()
ax.pie(portfolio["Current Value"], labels=portfolio["Ticker"], autopct="%1.1f%%", startangle=140)
st.pyplot(fig)

# Performance Metrics
st.subheader("📊 Portfolio Performance Metrics")
portfolio_returns = stock_data.pct_change().dropna()
portfolio_std = portfolio_returns.std().mean() * np.sqrt(252)
sharpe_ratio = portfolio_returns.mean().mean() / portfolio_std * np.sqrt(252)

st.metric(label="Portfolio Volatility", value=f"{portfolio_std:.2%}")
st.metric(label="Sharpe Ratio", value=f"{sharpe_ratio:.2f}")

