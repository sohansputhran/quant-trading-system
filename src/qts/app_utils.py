from __future__ import annotations
import os
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv, find_dotenv

# Load .env once, regardless of working dir
load_dotenv(find_dotenv(usecwd=True))

def set_page_config(title: str = "Quant Trading System"):
    st.set_page_config(
        page_title=title,
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def inject_css():
    st.markdown(
        """
        <style>
        .main-header { font-size: 2.2rem; font-weight: 700; color: #1f77b4; margin-bottom: .5rem; }
        .metric-card { background: #f0f2f6; padding: 1rem; border-radius: .5rem; border-left: 4px solid #1f77b4; }
        .positive { color: #00c853; } .negative { color: #ff3d00; }
        </style>
        """,
        unsafe_allow_html=True,
    )

@st.cache_data
def generate_sample_price_data(days: int = 365) -> pd.DataFrame:
    dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
    price = 100.0
    prices = []
    rng = np.random.default_rng(42)
    for _ in range(days):
        price *= (1 + rng.normal(0, 0.02))
        prices.append(price)
    return pd.DataFrame({"Date": dates, "Close": prices})

@st.cache_data
def generate_sample_strategy_data(days: int = 365) -> pd.DataFrame:
    dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
    rng = np.random.default_rng(43)
    strat = np.cumprod(1 + rng.normal(0, 0.015, size=days))
    bench = np.cumprod(1 + rng.normal(0, 0.01, size=days))
    return pd.DataFrame({"Date": dates, "Strategy": strat, "Benchmark": bench})
