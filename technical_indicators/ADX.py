# Implementation of Average Directional Index (ADX) indicator

import plotly.graph_objs as go
import numpy as np

def calculate_adx(df, period=14):
    """
    Calculates the Average Directional Index (ADX) for a given DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with 'High', 'Low', and 'Close' columns.
        period (int, optional): Lookback period for ADX calculation. Defaults to 14.

    Returns:
        pd.DataFrame: DataFrame with ADX, +DI, and -DI columns added.
    """

    # 1. Calculate True Range (TR)
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)

    # 2. Calculate Directional Movement (+DM and -DM)
    df['UpMove'] = df['High'] - df['High'].shift(1)
    df['DownMove'] = df['Low'].shift(1) - df['Low']
    df['+DM'] = np.where((df['UpMove'] > df['DownMove']) & (df['UpMove'] > 0), df['UpMove'], 0)
    df['-DM'] = np.where((df['DownMove'] > df['UpMove']) & (df['DownMove'] > 0), df['DownMove'], 0)

    # 3. Smooth the True Range and Directional Movements using Exponential Moving Averages
    df['TR_smooth'] = df['TR'].rolling(period).mean()
    df['+DM_smooth'] = df['+DM'].rolling(period).mean()
    df['-DM_smooth'] = df['-DM'].rolling(period).mean()

    # 4. Calculate Directional Indicators (+DI and -DI)
    df['+DI'] = 100 * (df['+DM_smooth'] / df['TR_smooth'])
    df['-DI'] = 100 * (df['-DM_smooth'] / df['TR_smooth'])

    # 5. Calculate Directional Index (DX)
    df['DX'] = 100 * abs((df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI']))

    # 6. Calculate ADX
    df['ADX'] = df['DX'].rolling(period).mean()

    return df[['ADX', '+DI', '-DI']]

def plot_adx(df, ticker):
    """
    Plots the ADX, +DI, and -DI indicators.

    Args:
        df (pd.DataFrame): DataFrame with ADX, +DI, and -DI columns.
        ticker (str): Ticker symbol for the stock.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df['ADX'], mode='lines', name='ADX', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df['+DI'], mode='lines', name='+DI', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df.index, y=df['-DI'], mode='lines', name='-DI', line=dict(color='red')))

    fig.update_layout(title=f'Average Directional Index (ADX) for {ticker}',
                      xaxis_title='Date',
                      yaxis_title='Value',
                      legend_title='Indicators')

    fig.show()