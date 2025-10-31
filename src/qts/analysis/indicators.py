"""
Lean indicator pipeline that works directly on the normalized OHLCV frame.
We keep math simple and explicit (better for interviews & review).
"""
from __future__ import annotations
import pandas as pd


def add_sma(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    out = df.copy()
    out[f"SMA_{window}"] = out["Close"].rolling(window, min_periods=window).mean()
    return out


def add_ema(df: pd.DataFrame, span: int = 20) -> pd.DataFrame:
    out = df.copy()
    out[f"EMA_{span}"] = out["Close"].ewm(span=span, adjust=False).mean()
    return out


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Classic Wilder's RSI approximation using SMA-of-gains/losses.
    Handles small divides by adding a tiny epsilon to denominator.
    """
    out = df.copy()
    delta = out["Close"].diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)

    avg_gain = gain.rolling(period, min_periods=period).mean()
    avg_loss = loss.rolling(period, min_periods=period).mean()

    rs = avg_gain / (avg_loss.replace(0, 1e-12))
    out[f"RSI_{period}"] = 100.0 - (100.0 / (1.0 + rs))
    return out


def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    out = df.copy()
    ema_fast = out["Close"].ewm(span=fast, adjust=False).mean()
    ema_slow = out["Close"].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    sig = macd.ewm(span=signal, adjust=False).mean()
    out["MACD"] = macd
    out["MACD_signal"] = sig
    out["MACD_hist"] = macd - sig
    return out


def compute_indicators(
    df: pd.DataFrame,
    cfg: dict | None = None,
) -> pd.DataFrame:
    """
    Composable indicator pipeline with sane defaults.
    Example:
        dfi = compute_indicators(prices, {"sma": 20, "ema": 50, "rsi": 14, "macd": {"fast":12,"slow":26,"signal":9}})
    """
    cfg = cfg or {}
    out = df.copy()

    if "sma" in cfg:
        out = add_sma(out, int(cfg["sma"]))
    else:
        out = add_sma(out, 20)

    if "ema" in cfg:
        out = add_ema(out, int(cfg["ema"]))
    else:
        out = add_ema(out, 50)

    out = add_rsi(out, int(cfg.get("rsi", 14)))

    macd_cfg = {"fast": 12, "slow": 26, "signal": 9}
    macd_cfg.update(cfg.get("macd", {}))
    out = add_macd(out, **macd_cfg)

    return out
