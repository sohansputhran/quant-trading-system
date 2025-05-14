import yfinance as yf
import datetime
import pandas as pd

data = yf.download("AAPL", interval="5m", multi_level_index=False)

stock_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
start_date = datetime.datetime.today() - datetime.timedelta(days=45)
end_date = datetime.datetime.today()

cl_price = pd.DataFrame()

for ticker in stock_tickers:
    data = yf.download(ticker, start=start_date, end=end_date, interval="5m", multi_level_index=False)
    cl_price[ticker] = data['Close']
cl_price = cl_price.dropna()
cl_price = cl_price.reset_index()
cl_price['Datetime'] = pd.to_datetime(cl_price['Datetime'])

ohlcv = {}
for ticker in stock_tickers:
    data = yf.download(ticker, start=start_date, end=end_date, interval="5m", multi_level_index=False)
    ohlcv[ticker] = data