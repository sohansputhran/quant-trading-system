from dataclasses import dataclass
from typing import Dict, Iterable, Literal, Optional
from pathlib import Path
import pandas as pd
from fredapi import Fred

from qts.config import FRED_API_KEY

TRANSFORM = Literal["level", "pct_change", "yoy"]

FRED_DIR = Path("data/fred")
FRED_DIR.mkdir(parents=True, exist_ok=True)

PRESETS: Dict[str, str] = {
    "CPI (All Urban Consumers)": "CPIAUCSL",
    "Unemployment Rate": "UNRATE",
    "Effective Fed Funds Rate": "FEDFUNDS",
    "Industrial Production Index": "INDPRO",
    "10Y Treasury Constant Maturity": "DGS10",
}

@dataclass(frozen=True)
class FredSeries:
    code: str
    df: pd.DataFrame  # index=DatetimeIndex; columns=[code]

def _client() -> Fred:
    if not FRED_API_KEY:
        raise RuntimeError("FRED_API_KEY missing. Add it to your .env.")
    return Fred(api_key=FRED_API_KEY)

def fetch_series(code: str, start: Optional[str] = None, end: Optional[str] = None) -> FredSeries:
    """Download a single FRED series and return a tidy df."""
    p = FRED_DIR / f"{code}.parquet"
    if p.exists():
        df = pd.read_parquet(p)
    else:
        fred = _client()
        s = fred.get_series(code)  # pandas Series
        df = s.to_frame(name=code)
        df.index.name = "Date"
        df.to_parquet(p)

    if start or end:
        df = df.loc[start:end]
    # Ensure monotonic datetime index
    df = df.sort_index()
    return FredSeries(code=code, df=df)

def fetch_many(codes: Iterable[str], start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
    frames = [fetch_series(c, start, end).df for c in codes]
    df = pd.concat(frames, axis=1)
    df.index.name = "Date"
    return df

def transform(df: pd.DataFrame, kind: TRANSFORM) -> pd.DataFrame:
    if kind == "level":
        return df
    if kind == "pct_change":
        return df.pct_change().mul(100)  # % change
    if kind == "yoy":
        # Year-over-year percentage change (works for monthly or daily)
        return df.pct_change(12).mul(100)
    raise ValueError(f"Unknown transform: {kind}")
