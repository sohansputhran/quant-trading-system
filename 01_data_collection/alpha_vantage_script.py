# I won't be able to collect data from Alpha Vantage because the daily limit is 5 calls per minute and 25 calls per day.
# However, if you buy a premium plan, you can collect data for 100 calls per minute and no limit on the number of calls per day.
# This script collects data from Alpha Vantage and stores it in a pandas DataFrame.

# importing libraries
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import time

import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(".."))

# Import the API_KEY from your config module
from utils.config import API_KEY

# extracting data for a single ticker
ts = TimeSeries(key=API_KEY, output_format='pandas')
data = ts.get_daily(symbol='EURUSD', outputsize='full')[0]
data.columns = ["open","high","low","close","volume"]
data = data.iloc[::-1]

# extracting stock data (historical close price) for multiple stocks
all_tickers = ["AAPL","MSFT","CSCO","AMZN","GOOG","TSLA","META","NFLX","NVDA","AMD","INTC","IBM","ORCL","QCOM","CRM","ADBE","CSX","TXN","AVGO","AMAT","INTU"]
close_prices = pd.DataFrame()
api_call_count = 1
ts = TimeSeries(key=API_KEY, output_format='pandas')
start_time = time.time()
for ticker in all_tickers:
    print(f"Fetching data for {ticker}...")
    # Fetch intraday data for the ticker
    data = ts.get_intraday(symbol=ticker,interval='1min', outputsize='compact')[0]
    # Check if the API call limit has been reached
    api_call_count+=1
    data.columns = ["open","high","low","close","volume"]
    # Reverse the order of the data to have it in chronological order
    data = data.iloc[::-1]
    # Add the close prices to the DataFrame
    close_prices[ticker] = data["close"]
    # Check if the API call limit has been reached
    if api_call_count==5:
        print("API call limit reached, sleeping for 60 seconds...")
        # Sleep for 60 seconds to avoid hitting the API call limit
        api_call_count = 1
        time.sleep(60 - ((time.time() - start_time) % 60.0))