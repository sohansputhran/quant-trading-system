import time
import yfinance as yf
import pandas as pd
from datetime import datetime
from .schemas import OHLCV, PriceInterval
from .cache import cache_path, save_parquet, load_parquet

def fetch_ohlcv_yahoo(symbol: str, start: str, end: str, interval: PriceInterval, use_cache: bool=True, max_retries: int=3) -> OHLCV:
    p = cache_path(symbol, interval)
    if use_cache and (cached := load_parquet(p)) is not None:
        return OHLCV(symbol, interval, cached)

    for attempt in range(1, max_retries+1):
        try:
            df = yf.download(symbol, start=start, end=end, interval=interval, auto_adjust=False, progress=False)
            if not isinstance(df, pd.DataFrame) or df.empty:
                raise ValueError("Empty dataframe from Yahoo")
            df = df.rename(columns={c: c.title() for c in df.columns})  # normalize
            save_parquet(df, p)
            return OHLCV(symbol, interval, df)
        except Exception as e:
            if attempt == max_retries:
                raise
            time.sleep(1.5 * attempt)
