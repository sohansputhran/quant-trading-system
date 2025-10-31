import os, datetime as dt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from qts.data.prices import fetch_yf_prices, fetch_alpaca_intraday, ensure_ohlcv, resample_bars
from qts.analysis.indicators import compute_indicators

st.set_page_config(page_title="Technical Analysis", page_icon="📈", layout="wide")
st.title("📈 Technical Analysis")

with st.sidebar:
    st.subheader("Parameters")
    symbol = st.text_input("Symbol", value="AAPL").upper()
    source = st.selectbox("Data Source", ["Yahoo Finance", "Alpaca (intraday)"])
    period = st.selectbox("Period (Yahoo)", ["1mo","3mo","6mo","1y","2y","5y"], index=2)
    interval = st.selectbox("Interval (Yahoo)", ["1d","1h","30m","15m","5m"], index=0)
    tf = st.selectbox("Timeframe (Alpaca)", ["1Min","5Min","15Min"], index=1)
    start = dt.datetime.utcnow() - dt.timedelta(days=5)
    end = dt.datetime.utcnow()

    st.markdown("---")
    st.caption("Indicators")
    sma = st.number_input("SMA window", 5, 200, 20, 1)
    ema = st.number_input("EMA span", 5, 200, 50, 1)
    rsi = st.number_input("RSI period", 5, 50, 14, 1)

@st.cache_data(show_spinner=False, ttl=300)
def _load_data(symbol, source, period, interval, tf, start, end):
    if source.startswith("Yahoo"):
        df = fetch_yf_prices(symbol, period=period, interval=interval)
    else:
        try:
            df = fetch_alpaca_intraday(symbol, start=start, end=end, tf=tf)
        except Exception as e:
            st.warning(f"Falling back to Yahoo Finance (reason: {e})")
            df = fetch_yf_prices(symbol, period="1mo", interval="15m")
    return ensure_ohlcv(df)

df = _load_data(symbol, source, period, interval, tf, start, end)

dfi = compute_indicators(df, {"sma": int(sma), "ema": int(ema), "rsi": int(rsi)})
print(dfi.head())
# For the candlestick patterns in the chart
def normalize_ohlcv_from_yf_multi(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # If top level contains 'Price', select that slice
    if isinstance(out.columns, pd.MultiIndex) and "Price" in out.columns.get_level_values(0):
        out = out.xs("Price", axis=1, level=0)

    # If still multiindex (fields x ticker), pick the first ticker (or a specific one)
    if isinstance(out.columns, pd.MultiIndex):
        # fields at level 0, tickers at last level
        tickers = out.columns.get_level_values(-1).unique()
        ticker = str(tickers[0])   # or pass a desired ticker
        out = out.xs(ticker, axis=1, level=-1)

    # Standardize names and enforce required columns
    out = out.rename(columns=lambda c: str(c).strip().title())
    required = ["Open", "High", "Low", "Close"]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError(f"Missing OHLC columns after flattening: {missing} | got {list(out.columns)}")

    # Add Adj Close (yfinance intraday often lacks it)
    if "Adj Close" not in out.columns:
        out["Adj Close"] = out["Close"]

    # Coerce numeric, drop rows with missing OHLC, and make index tz-naive for Plotly
    for c in ["Open", "High", "Low", "Close", "Adj Close"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["Open", "High", "Low", "Close"])

    idx = pd.to_datetime(out.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_convert("UTC").tz_localize(None)
    out.index = idx

    # Keep a clean column order
    cols = ["Open", "High", "Low", "Close", "Adj Close"]
    return out[[c for c in cols if c in out.columns]]

pxdf = normalize_ohlcv_from_yf_multi(dfi)

# --- Price chart (candles + SMA/EMA)
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=pxdf.index,
    open=pxdf["Open"],
    high=pxdf["High"],
    low=pxdf["Low"],
    close=pxdf["Close"],
    name="Price"
))
fig.update_layout(xaxis_rangeslider_visible=False, height=500, margin=dict(l=10,r=10,t=30,b=10))
fig.add_trace(go.Scatter(x=dfi.index, y=dfi[f"SMA_{int(sma)}"], mode="lines", name=f"SMA {int(sma)}"))
fig.add_trace(go.Scatter(x=dfi.index, y=dfi[f"EMA_{int(ema)}"], mode="lines", name=f"EMA {int(ema)}"))
st.plotly_chart(fig, use_container_width=True)

# col1, col2 = st.columns([3,1])
# with col1:
#     st.plotly_chart(fig, use_container_width=True)
# with col2:
#     st.metric("Last Close", f"{dfi['Close'].iloc[-1]:,.2f}")
#     delta = dfi["Close"].iloc[-1] / dfi["Close"].iloc[0] - 1
#     st.metric("Period Return", f"{delta*100:,.2f}%")

# --- RSI + MACD
r1, r2 = st.columns(2)
with r1:
    st.subheader("RSI")
    st.area_chart(dfi[[f"RSI_{int(rsi)}"]].rename(columns={f"RSI_{int(rsi)}":"RSI"}), height=200)
with r2:
    st.subheader("MACD")
    macd_df = dfi[["MACD","MACD_signal","MACD_hist"]]
    st.line_chart(macd_df[["MACD","MACD_signal"]], height=200)
    st.bar_chart(macd_df[["MACD_hist"]], height=200)

# --- Data table + download
with st.expander("Raw Data", expanded=False):
    st.dataframe(dfi.tail(500))
    csv = dfi.to_csv(index=True).encode()
    st.download_button("Download CSV", csv, file_name=f"{symbol}_ta.csv", mime="text/csv")
