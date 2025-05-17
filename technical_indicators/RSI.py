# Implementation of Relative Strength Index (RSI) indicator
# RSI is a momentum oscillator that measures the speed and change of price movements.

import plotly.graph_objs as go

def calculate_RSI(ohlcv_data, period=14):
    """
    Calculate the Relative Strength Index (RSI) for a given OHLCV DataFrame.

    Parameters:
    - ohlcv_data (pd.DataFrame): DataFrame containing OHLCV data.
    - period (int): The number of periods to use for the RSI calculation.

    Returns:
    - pd.Series: A Series containing the RSI values.
    """
    delta = ohlcv_data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def plot_rsi(data, ticker):
    """
    Plot the Relative Strength Index (RSI) for a given OHLCV DataFrame.

    Parameters:
    - data (pd.DataFrame): DataFrame containing OHLCV data with RSI values.

    Returns:
    - None: Displays the RSI plot.
    """
    rsi = data['RSI']
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=rsi, mode='lines', name='RSI'))
    fig.update_layout(title=f"{ticker} RSI",
                      xaxis_title='Date',
                      yaxis_title='RSI',
                      showlegend=True)
    fig.show()