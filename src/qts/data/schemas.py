from dataclasses import dataclass
from typing import Literal
import pandas as pd

PriceInterval = Literal["1d","1h","30m","15m","5m","1m"]

@dataclass(frozen=True)
class OHLCV:
    symbol: str
    interval: PriceInterval
    df: pd.DataFrame  # index=DatetimeIndex; columns=['Open','High','Low','Close','Adj Close','Volume']
