# Importing the required libraries
import yfinance as yf
import datetime
import pandas as pd

# Downloading the data for a specific stock ticker
data = yf.download("AAPL", interval="5m", multi_level_index=False)

# Displaying the first few rows of the data
stock_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# Define the start and end dates for the data
start_date = datetime.datetime.today() - datetime.timedelta(days=45)
end_date = datetime.datetime.today()

cl_price = pd.DataFrame()

# Downloading the closing prices for each stock ticker
for ticker in stock_tickers:
    data = yf.download(ticker, start=start_date, end=end_date, interval="5m", multi_level_index=False)
    cl_price[ticker] = data['Close']

# Dropping rows with NaN values and resetting the index
cl_price = cl_price.dropna()

# Converting the index to a datetime format
cl_price = cl_price.reset_index()

# Converting the 'Datetime' column to datetime format
cl_price['Datetime'] = pd.to_datetime(cl_price['Datetime'])

ohlcv = {}
for ticker in stock_tickers:
    data = yf.download(ticker, start=start_date, end=end_date, interval="5m", multi_level_index=False)
    ohlcv[ticker] = data