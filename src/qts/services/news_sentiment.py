from __future__ import annotations
import pandas as pd
from qts.data.news import fetch_news, aggregate_sentiment

def compute_news_sentiment(query: str, days: int = 7) -> tuple[pd.DataFrame, dict]:
    """
    Helper used by Streamlit and scheduled jobs.
    Returns (articles_df, aggregates_dict)
    """
    df = fetch_news(query, from_days=days, sort_by="publishedAt", max_pages=3, page_size=100)
    agg = aggregate_sentiment(df)
    return df, agg
