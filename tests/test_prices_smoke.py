import pandas as pd
from qts.data.prices import fetch_yf_prices

def test_fetch_yf_prices_basic():
    df = fetch_yf_prices("AAPL", period="1mo", interval="1d")
    assert isinstance(df.index, pd.DatetimeIndex)
    for col in ["Open","High","Low","Close","Adj Close","Volume"]:
        assert col in df.columns
    assert len(df) > 0
