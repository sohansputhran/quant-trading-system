# Implementing the Performance Measurements
# This module contains functions to calculate various performance metrics for financial data.

# Import necessary libraries
import numpy as np

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

def Sharpe_Ratio(df, risk_free_rate=0.01):
    """
    Calculate the Sharpe Ratio of a stock based on its historical data.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing the OHLCV data for the stock.
    risk_free_rate (float): The risk-free rate to use in the calculation.

    Returns:
    float: The Sharpe Ratio of the specified stock.
    """
    # Calculate daily returns
    daily_returns = df['Close'].pct_change()
    
    # Calculate excess returns
    excess_returns = daily_returns - risk_free_rate / 252
    
    # Calculate annualized Sharpe Ratio
    sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
    
    return sharpe_ratio

def Sortino_Ratio(df, target_return=0):
    """
    Calculate the Sortino Ratio of a stock based on its historical data.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing the OHLCV data for the stock.
    target_return (float): The target return to use in the calculation.

    Returns:
    float: The Sortino Ratio of the specified stock.
    """
    # Calculate daily returns
    daily_returns = df['Close'].pct_change()
    
    # Calculate downside returns
    downside_returns = daily_returns[daily_returns < target_return]
    
    # Calculate annualized Sortino Ratio
    sortino_ratio = (daily_returns.mean() - target_return) / downside_returns.std() * np.sqrt(252)
    
    return sortino_ratio

def Maximum_Drawdown(df):
    """
    Calculate the Maximum Drawdown of a stock based on its historical data.

    Parameters:
    df (pd.DataFrame): DataFrame containing the OHLCV data for the stock.

    Returns:
    float: The Maximum Drawdown of the specified stock.
    """
    # Calculate daily returns
    daily_returns = df['Close'].pct_change()

    # Calculate cumulative returns
    cumulative_returns = (1 + daily_returns).cumprod()

    # Calculate maximum drawdown
    max_drawdown = (cumulative_returns / cumulative_returns.cummax() - 1).min()

    return max_drawdown

def Calmar_Ratio(df):
    """
    Calculate the Calmar Ratio of a stock based on its historical data.

    Parameters:
    df (pd.DataFrame): DataFrame containing the OHLCV data for the stock.

    Returns:
    float: The Calmar Ratio of the specified stock.
    """
    # Calculate daily returns
    daily_returns = df['Close'].pct_change()

    # Calculate maximum drawdown
    max_drawdown = Maximum_Drawdown(df)

    # Calculate annualized Calmar Ratio
    calmar_ratio = daily_returns.mean() / abs(max_drawdown)

    return calmar_ratio