from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def cache_path(symbol: str, interval: str) -> Path:
    return DATA_DIR / f"{symbol.replace('/','-')}_{interval}.parquet"

def save_parquet(df: pd.DataFrame, path: Path) -> None:
    df.to_parquet(path, index=True)

def load_parquet(path: Path) -> pd.DataFrame | None:
    return pd.read_parquet(path) if path.exists() else None
