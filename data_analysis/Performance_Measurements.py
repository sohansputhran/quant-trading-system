# Implementing the Performance Measurements
# This module contains functions to calculate various performance metrics for financial data.

# Import necessary libraries
import numpy as np

# Implementation of Cumulative Annual Growth Rate (CAGR)
def CAGR(df, period=1):
    """
    Calculate the Cummulative Annual Growth Rate (CAGR) of a given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data.
    period (int): The number of periods to calculate CAGR for.

    Returns:
    float: The CAGR value.
    """
    # Calculate the CAGR
    df['return'] = df['Close'].pct_change()
    df['cumulative_return'] = (1 + df['return']).cumprod()
    cagr = (df['cumulative_return'].iloc[-1] ** (1 / period)) - 1
    # Drop the 'return' and 'cumulative_return' columns
    df.drop(columns=['return', 'cumulative_return'], inplace=True)
    # Return the CAGR value
    return cagr

def Volatility(df):
    """
    Calculate the volatility of a stock based on its historical data.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing the OHLCV data for the stock.

    Returns:
    float: The volatility of the specified stock.
    """
    # Calculate daily returns
    daily_returns = df['Close'].pct_change()
    
    # Calculate annualized volatility
    volatility = daily_returns.std() * np.sqrt(252)
    
    return volatility