# Implementation of Average True Range (ATR) indicator

import pandas as pd
import matplotlib.pyplot as plt

def implement_ATR(df, period=14):
    """
    Calculate Average True Range (ATR)
    """
    df['High-Low'] = df['High'] - df['Low']
    df['High-Prev Close'] = abs(df['High'] - df['Close'].shift(1))
    df['Low-Prev Close'] = abs(df['Low'] - df['Close'].shift(1))
    df['True Range'] = df[['High-Low', 'High-Prev Close', 'Low-Prev Close']].max(axis=1)
    atr = df['True Range'].rolling(window=period).mean()
    return atr

def ATR_plot(df, ticker, period=14):
    """
    Plot ATR
    """
    # df['ATR'] = implement_ATR(df, period)
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['ATR'], label='ATR', color='blue')
    plt.title(f'Average True Range (ATR) for {ticker}')
    plt.xlabel('Date')
    plt.ylabel('ATR')
    plt.legend()
    plt.grid()
    plt.show()