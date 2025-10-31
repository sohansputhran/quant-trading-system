import plotly.graph_objects as go
import streamlit as st
from qts import inject_css, generate_sample_price_data

inject_css()
st.markdown('<p class="main-header">Technical Analysis</p>', unsafe_allow_html=True)

ticker = st.selectbox("Select Ticker", ["AAPL", "GOOGL", "MSFT", "TSLA", "EUR/USD", "BTC/USD"])
df = generate_sample_price_data(365)

# indicators
df["SMA_20"] = df["Close"].rolling(window=20).mean()
df["SMA_50"] = df["Close"].rolling(window=50).mean()
df["EMA_12"] = df["Close"].ewm(span=12).mean()
delta = df["Close"].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df["RSI"] = 100 - (100 / (1 + rs))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}",
          f"{((df['Close'].iloc[-1]-df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100):.2f}%")
c2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
c3.metric("SMA (20)", f"${df['SMA_20'].iloc[-1]:.2f}")
c4.metric("SMA (50)", f"${df['SMA_50'].iloc[-1]:.2f}")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Price", line=dict(color="#1f77b4", width=2)))
fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA_20"], name="SMA 20", line=dict(color="orange", width=1)))
fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA_50"], name="SMA 50", line=dict(color="red", width=1)))
fig.update_layout(title=f"{ticker} - Price with Moving Averages", xaxis_title="Date", yaxis_title="Price ($)", height=500)
st.plotly_chart(fig, use_container_width=True)

fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df["Date"], y=df["RSI"], name="RSI", line=dict(color="purple")))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
fig_rsi.update_layout(title="Relative Strength Index (RSI)", xaxis_title="Date", yaxis_title="RSI", height=300)
st.plotly_chart(fig_rsi, use_container_width=True)
