# Implementation of Bollinger Bands indicator

import plotly.graph_objs as go
import pandas as pd

def implement_bollinger_bands(data, window=20, num_std_dev=2):
    """
    Calculate Bollinger Bands for a given DataFrame.
    
    Parameters:
    - data: DataFrame containing 'Close' prices.
    - window: Number of periods for the moving average.
    - num_std_dev: Number of standard deviations for the bands.
    
    Returns:
    - DataFrame with 'Upper Band', 'Lower Band', and 'Middle Band'.
    """
    # Calculate the middle band (simple moving average)
    middle_band = data['Close'].rolling(window=window).mean()
    # Calculate the standard deviation
    std_dev = data['Close'].rolling(window=window).std(ddof=0)
    # Calculate the upper and lower bands
    upper_band = middle_band + (std_dev * num_std_dev)
    lower_band = middle_band - (std_dev * num_std_dev)
    # Calculate the width of the bands
    bb_width = (upper_band - lower_band) / middle_band
    
    return pd.DataFrame({
        'Upper Band': upper_band,
        'Lower Band': lower_band,
        'Middle Band': middle_band,
        'Bollinger Band Width': bb_width
    })


def plot_bollinger_bands(data, ticker):
    """
    Plot Bollinger Bands for a given DataFrame.
    
    Parameters:
    - data: DataFrame containing 'Close' prices.
    - window: Number of periods for the moving average.
    - num_std_dev: Number of standard deviations for the bands.
    """
 
    fig = go.Figure()

    # Add the price chart
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Price'))

    # Add the Bollinger Bands and shade the area
    fig.add_trace(go.Scatter(x=data.index, y=data['Upper Band'], mode='lines', name='Upper Bollinger Band', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=data.index, y=data['Lower Band'], fill='tonexty', mode='lines', name='Lower Bollinger Band', line=dict(color='green')))

    # Add the Middle Bollinger Band
    fig.add_trace(go.Scatter(x=data.index, y=data['Middle Band'], mode='lines', name='Middle Bollinger Band', line=dict(color='blue')))

    # Customize the chart layout
    fig.update_layout(title=f"{ticker} Stock Price with Bollinger Bands",
                      xaxis_title='Date',
                      yaxis_title='Price',
                      showlegend=True)

    # Show the chart
    fig.show()