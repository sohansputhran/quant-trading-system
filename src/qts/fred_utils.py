from __future__ import annotations
import os
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from fredapi import Fred
import streamlit as st

load_dotenv(find_dotenv(usecwd=True))

FRED_PRESETS = {
    "CPI (All Urban Consumers)": "CPIAUCSL",
    "Unemployment Rate": "UNRATE",
    "Effective Fed Funds Rate": "FEDFUNDS",
    "Industrial Production Index": "INDPRO",
    "10Y Treasury Constant Maturity": "DGS10",
}

def fred_key_loaded() -> bool:
    return bool(os.getenv("FRED_API_KEY", ""))

@st.cache_data(ttl=60 * 60)
def fred_fetch_many(api_key: str, codes: tuple[str, ...], start=None, end=None) -> pd.DataFrame:
    fred = Fred(api_key=api_key)
    frames = []
    for code in codes:
        s = fred.get_series(code)
        df = s.to_frame(name=code)
        df.index.name = "Date"
        if start or end:
            df = df.loc[str(start or ""):str(end or "")]
        frames.append(df)
    out = pd.concat(frames, axis=1) if frames else pd.DataFrame()
    return out.sort_index()

def fred_transform(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    if kind == "level":
        return df
    if kind == "pct_change":
        return df.pct_change().mul(100)
    if kind == "yoy":
        return df.pct_change(12).mul(100)
    return df
