# Implementation of Average True Range (ATR) indicator

import pandas as pd
import matplotlib.pyplot as plt

def implement_ATR(df, period=14):
    """
    Calculate Average True Range (ATR)
    Parameters:
    - df (DataFrame) : DataFrame containing 'High', 'Low', and 'Close' prices
    - period (int) : The number of periods to calculate the ATR

    Returns:
    - atr (Series) : Series containing the ATR values
    """
    df['High-Low'] = df['High'] - df['Low']
    df['High-Prev Close'] = abs(df['High'] - df['Close'].shift(1))
    df['Low-Prev Close'] = abs(df['Low'] - df['Close'].shift(1))
    df['True Range'] = df[['High-Low', 'High-Prev Close', 'Low-Prev Close']].max(axis=1)
    atr = df['True Range'].rolling(window=period).mean()
    return atr

def ATR_plot(df, ticker):
    """
    Plot ATR
    Parameters:
    - df (DataFrame) : DataFrame containing 'High', 'Low', and 'Close' prices
    - ticker (str) : Ticker symbol for the stock

    Returns:
    - None : Displays the ATR plot
    """
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['ATR'], label='ATR', color='blue')
    plt.title(f'Average True Range (ATR) for {ticker}')
    plt.xlabel('Date')
    plt.ylabel('ATR')
    plt.legend()
    plt.grid()
    plt.show()