from __future__ import annotations
import os, datetime as dt
import pandas as pd
import yfinance as yf

# Optional Alpaca import (used only if keys exist)
_ALPACA_READY = all(os.getenv(k) for k in ["ALPACA_API_KEY_ID", "ALPACA_API_SECRET_KEY"])
try:
    if _ALPACA_READY:
        from alpaca.data import StockHistoricalDataClient, StockBarsRequest, TimeFrame
except Exception:
    _ALPACA_READY = False

def _coerce_dt(x):  # small helper for consistent index names
    if isinstance(x, pd.DatetimeIndex):
        return x.tz_convert("UTC") if x.tz is not None else x.tz_localize("UTC")
    return x

def fetch_yf_prices(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV from Yahoo Finance. Works well for daily and most intraday."""
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False)
    if df.empty:
        raise ValueError(f"No data from yfinance for {symbol} ({period=}, {interval=})")
    df.index = _coerce_dt(df.index)
    df.rename(columns=str.capitalize, inplace=True)  # Open, High, Low, Close, Volume
    return df[["Open", "High", "Low", "Close", "Volume"]]

def fetch_alpaca_intraday(symbol: str, start: dt.datetime, end: dt.datetime, tf: str = "1Min") -> pd.DataFrame:
    """Fetch intraday bars via Alpaca (if credentials available)."""
    if not _ALPACA_READY:
        raise RuntimeError("Alpaca credentials not configured")
    tf_map = {"1Min": TimeFrame.Minute, "5Min": TimeFrame(5, "Min"), "15Min": TimeFrame(15, "Min")}
    client = StockHistoricalDataClient(os.getenv("ALPACA_API_KEY_ID"), os.getenv("ALPACA_API_SECRET_KEY"))
    req = StockBarsRequest(symbol_or_symbols=symbol, timeframe=tf_map.get(tf, TimeFrame.Minute),
                           start=start, end=end, adjustment="raw")
    bars = client.get_stock_bars(req).df  # MultiIndex -> (symbol, timestamp)
    if bars.empty:
        raise ValueError(f"No Alpaca data for {symbol}")
    df = bars.reset_index().query("symbol == @symbol").set_index("timestamp") \
             .rename(columns={"open":"Open","high":"High","low":"Low","close":"Close","volume":"Volume"})
    df.index = _coerce_dt(df.index)
    # # create Adj Close placeholder (use Close for now)
    # df["Adj Close"] = df["Close"]
    return df[["Open","High","Low","Close","Volume"]]

def ensure_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    req = ["Open","High","Low","Close","Volume"]
    missing = [c for c in req if c not in df.columns]
    if missing:
        raise ValueError(f"OHLCV columns missing: {missing}")
    return df.sort_index()

def resample_bars(df: pd.DataFrame, rule: str = "1D") -> pd.DataFrame:
    """Downsample intraday to daily or weekly bars."""
    o = df["Open"].resample(rule).first()
    h = df["High"].resample(rule).max()
    l = df["Low"].resample(rule).min()
    c = df["Close"].resample(rule).last()
    # a = df["Adj Close"].resample(rule).last()
    v = df["Volume"].resample(rule).sum()
    out = pd.concat([o,h,l,c,v], axis=1)
    out.columns = ["Open","High","Low","Close","Volume"]
    return out.dropna(how="any")
