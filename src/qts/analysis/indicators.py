from __future__ import annotations
import pandas as pd

def add_sma(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    df = df.copy()
    df[f"SMA_{window}"] = df["Close"].rolling(window).mean()
    return df

def add_ema(df: pd.DataFrame, span: int = 20) -> pd.DataFrame:
    df = df.copy()
    df[f"EMA_{span}"] = df["Close"].ewm(span=span, adjust=False).mean()
    return df

def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    df = df.copy()
    delta = df["Close"].diff()
    gain = (delta.clip(lower=0)).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / (loss.replace(0, 1e-9))
    df[f"RSI_{period}"] = 100 - (100 / (1 + rs))
    return df

def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    df = df.copy()
    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    sig = macd.ewm(span=signal, adjust=False).mean()
    df["MACD"] = macd
    df["MACD_signal"] = sig
    df["MACD_hist"] = macd - sig
    return df

def compute_indicators(df: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """Composable indicator pipeline with sane defaults."""
    cfg = cfg or {}
    out = df.copy()
    out = add_sma(out, cfg.get("sma", 20))
    out = add_ema(out, cfg.get("ema", 50))
    out = add_rsi(out, cfg.get("rsi", 14))
    out = add_macd(out, **cfg.get("macd", {"fast":12,"slow":26,"signal":9}))
    return out
