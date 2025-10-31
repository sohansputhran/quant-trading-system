"""
Price loaders for yfinance (and helpers) that robustly handle the MultiIndex
shape: Level0='Price', Level1=['Open','High','Low','Close', 'Adj Close', 'Volume'],
Level2=ticker (e.g., 'AAPL').

We flatten to single-level columns: Open, High, Low, Close, Adj Close, Volume.

Usage:
    df = fetch_yf_prices("AAPL", period="6mo", interval="1d")
    # df.index -> tz-naive DatetimeIndex (UTC originally), sorted ascending
    # df.columns -> ['Open','High','Low','Close','Adj Close','Volume']
"""
from __future__ import annotations

import datetime as dt
from typing import Iterable, Optional
import pandas as pd
import yfinance as yf

# Normalization utilities
def _normalize_ohlcv_from_yf(df: pd.DataFrame, symbol_preference: Optional[str] = None) -> pd.DataFrame:
    """
    Normalize yfinance output to a tidy OHLCV frame.

    Handles:
      - MultiIndex columns with top level 'Price'
      - Field x Ticker multiindex (select preferred symbol or the first)
      - Missing 'Adj Close' (creates from 'Close')
      - Timezone-naive index for plotting/serialization
    """
    out = df.copy()

    # If we have a 3-level MultiIndex and Level 0 contains 'Price', slice it.
    if isinstance(out.columns, pd.MultiIndex) and "Price" in out.columns.get_level_values(0):
        out = out.xs("Price", axis=1, level=0)

    # If still MultiIndex (fields x ticker), choose a ticker column slice
    if isinstance(out.columns, pd.MultiIndex):
        # Typical yfinance layout now: level 0 = field, level -1 = ticker
        tickers = out.columns.get_level_values(-1).unique()
        chosen = symbol_preference or str(tickers[0])
        # In case preference doesn't exist (case-mismatch), try a case-insensitive match
        if chosen not in tickers:
            try:
                chosen = [t for t in tickers if str(t).upper() == str(chosen).upper()][0]
            except IndexError:
                chosen = str(tickers[0])
        out = out.xs(chosen, axis=1, level=-1)

    # Standardize names
    out = out.rename(columns=lambda c: str(c).strip().title())
    # yfinance occasionally uses 'Adj Close*'
    if "Adj Close*" in out.columns:
        out = out.rename(columns={"Adj Close*": "Adj Close"})

    # Ensure required columns exist
    required_any = {"Open", "High", "Low", "Close"}
    missing = [c for c in sorted(required_any) if c not in out.columns]
    if missing:
        raise ValueError(f"[prices] Missing OHLC columns after flattening: {missing} | got {list(out.columns)}")

    # Fill Adj Close if absent (intraday usually lacks it)
    if "Adj Close" not in out.columns:
        out["Adj Close"] = out["Close"]

    # Volume may not exist for some assets/intervals; if missing, create zeros
    if "Volume" not in out.columns:
        out["Volume"] = 0

    # Coerce numeric + drop rows without OHLC (indicator warm-up is fine)
    for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["Open", "High", "Low", "Close"])

    # Plotly prefers tz-naive timestamps; keep ordering
    idx = pd.to_datetime(out.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_convert("UTC").tz_localize(None)
    out.index = idx

    # Keep clean order
    cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    return out[[c for c in cols if c in out.columns]].sort_index()

# Public API
def fetch_yf_prices(
    symbol: str,
    period: str = "6mo",
    interval: str = "1d",
    auto_adjust: bool = False,
) -> pd.DataFrame:
    """
    Fetch OHLCV from Yahoo Finance and normalize to a single-ticker, single-level
    DataFrame with columns: Open, High, Low, Close, Adj Close, Volume.

    Parameters
    ----------
    symbol : str
        Ticker (e.g., 'AAPL')
    period : str
        e.g., '1mo','3mo','6mo','1y','2y','5y','max'
    interval : str
        e.g., '1d','1h','30m','15m','5m','1m'
    auto_adjust : bool
        If True, yfinance will adjust OHLC automatically; we still keep 'Adj Close'
        as a column (equal to 'Close' if intraday).
    """
    df = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=auto_adjust,
        progress=False,
        threads=True,
    )
    if df is None or df.empty:
        raise ValueError(f"[prices] No data from yfinance for {symbol} ({period=}, {interval=})")

    return _normalize_ohlcv_from_yf(df, symbol_preference=symbol)


def ensure_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Validate presence/order of OHLCV columns and return a sorted copy."""
    required = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"[prices] OHLCV columns missing: {missing}")
    return df[required].sort_index()


def resample_bars(df: pd.DataFrame, rule: str = "1D") -> pd.DataFrame:
    """
    Downsample intraday to daily/weekly bars using OHLCV semantics.
    Example: rule='1W' or '1M'.
    """
    df = ensure_ohlcv(df)
    o = df["Open"].resample(rule).first()
    h = df["High"].resample(rule).max()
    l = df["Low"].resample(rule).min()
    c = df["Close"].resample(rule).last()
    a = df["Adj Close"].resample(rule).last()
    v = df["Volume"].resample(rule).sum(min_count=1)
    out = pd.concat([o, h, l, c, a, v], axis=1)
    out.columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    return out.dropna(subset=["Open", "High", "Low", "Close"])
