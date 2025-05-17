# Implementation of Moving Average Convergence Divergence (MACD) indicator
# MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price.

import matplotlib.pyplot as plt

def implement_MACD(data, short_window=12, long_window=26, signal_window=9):
    """
    Calculate MACD and Signal Line
    Parameters:
    - data (DataFrame) : DataFrame containing 'Close' prices
    - short_window (int) : The short-term EMA period
    - long_window (int) : The long-term EMA period
    - signal_window (int) : The signal line EMA period

    Returns:
    - macd (Series) : Series containing the MACD values
    - signal_line (Series) : Series containing the Signal Line values
    """
    # Calculate the short-term and long-term EMAs
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()

    # Calculate MACD
    macd = short_ema - long_ema

    # Calculate Signal Line
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()

    return macd, signal_line

# Plotting MACD and Signal Line for each ticker 
def plot_macd(data, ticker):
    """
    Plot MACD and Signal Line
    Parameters:
    - data (DataFrame) : DataFrame containing 'Close' prices and MACD values
    - ticker (str) : Ticker symbol for the stock

    Returns:
    - None : Displays the MACD plot
    """
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.plot(data['MACD'], label='MACD', color='blue')
    ax.plot(data['Signal Line'], label='Signal Line', color='red')
    ax.set(title=f"MACD for {ticker}", xlabel="Date", ylabel="MACD")
    ax.legend()
    plt.show()