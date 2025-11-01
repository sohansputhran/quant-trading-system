from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Iterable, Literal

import pandas as pd
import requests
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from requests import HTTPError, Timeout, ConnectionError as ReqConnError

from qts.config import settings

log = logging.getLogger(__name__)
analyzer = SentimentIntensityAnalyzer()

_NEWSAPI_BASE = "https://newsapi.org/v2/"
_SORT_BY = Literal["publishedAt", "relevancy", "popularity"]

class NewsAPIError(RuntimeError):
    """Non-retryable API errors (bad key, plan limits, bad request)."""

class NewsAPITransient(RuntimeError):
    """Retryable errors (429, 5xx, timeouts, network hiccups)."""

def _headers():
    if not settings.NEWSAPI_KEY:
        raise NewsAPIError("NEWSAPI_KEY missing. Add it to .env")
    return {"X-Api-Key": settings.NEWSAPI_KEY}

def _classify_status(status: int, text_preview: str) -> Exception:
    # Non-retryable: fix your inputs/plan/keys
    if status in (400, 401, 403, 404, 405, 426):
        return NewsAPIError(f"{status}: {text_preview}")
    # Retryable: rate limit or server error
    if status == 429 or 500 <= status < 600:
        return NewsAPITransient(f"{status}: {text_preview}")
    # Default to non-retryable to be conservative
    return NewsAPIError(f"{status}: {text_preview}")

def _should_retry(exc: Exception) -> bool:
    # Only retry transient categories; never retry on "fix your config/plan" errors
    return isinstance(exc, (NewsAPITransient, Timeout, ReqConnError))

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception(_should_retry),
    reraise=True,
)
def _get(url: str, params: dict) -> dict:
    try:
        r = requests.get(url, params=params, headers=_headers(), timeout=20)
    except (Timeout, ReqConnError) as e:
        # Network hiccup → retry
        raise NewsAPITransient(str(e)) from e
    except Exception as e:
        # Anything else unexpected → do not retry blindly
        raise NewsAPIError(f"Unexpected error: {e}") from e

    # Don’t let HTTPError bubble – we inspect status and wrap explicitly
    if r.status_code != 200:
        preview = r.text[:400].replace("\n", " ")
        raise _classify_status(r.status_code, preview)
    try:
        return r.json()
    except ValueError as e:
        # Bad/HTML response – treat as transient
        raise NewsAPITransient(f"Invalid JSON response: {e}") from e

def fetch_news(
    query: str,
    *,
    from_days: int = 7,
    language: str = "en",
    sources: Iterable[str] | None = None,
    sort_by: _SORT_BY = "publishedAt",
    max_pages: int = 3,
    page_size: int = 100,
) -> pd.DataFrame:
    """
    Pull recent articles for `query` and return a tidy DataFrame.
    Notes:
      - Free NewsAPI tier is recent news only (no full historical).
      - We paginate modestly to stay within quotas.
    """
    if from_days < 1:
        from_days = 1
    since = (datetime.now(timezone.utc) - timedelta(days=from_days)).isoformat(timespec="seconds")

    rows: list[dict] = []
    for page in range(1, max_pages + 1):
        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "page": page,
            "pageSize": page_size,
            "from": since,
        }
        if sources:
            params["sources"] = ",".join(sources)

        payload = _get(f"{_NEWSAPI_BASE}/everything", params)
        arts = payload.get("articles", [])
        log.info("Fetched %d articles (page %d)", len(arts), page)
        for a in arts:
            rows.append({
                "published_at": a.get("publishedAt"),
                "source": (a.get("source") or {}).get("name"),
                "author": a.get("author"),
                "title": a.get("title"),
                "description": a.get("description"),
                "content": a.get("content"),
                "url": a.get("url"),
            })

        # stop early if fewer than page_size returned
        if len(arts) < page_size:
            break

    if not rows:
        return pd.DataFrame(columns=["published_at","source","title","description","content","url","sentiment"])

    df = pd.DataFrame(rows)
    # clean + sentiment
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    df["text"] = (df["title"].fillna("") + ". " + df["description"].fillna(""))
    df["sentiment"] = df["text"].apply(lambda t: analyzer.polarity_scores(str(t))["compound"])
    df = df.sort_values("published_at", ascending=False).reset_index(drop=True)
    return df

def aggregate_sentiment(df: pd.DataFrame) -> dict:
    """
    Returns overall headline (Bullish/Bearish/Neutral), numeric score, and daily bars.
    """
    if df.empty:
        return {
            "headline": "No Data",
            "score": 0.0,
            "sources": 0,
            "delta": 0.0,
            "daily": pd.DataFrame(columns=["date", "mean_sentiment", "count"]),
        }

    overall = float(df["sentiment"].mean())
    sources = df["source"].nunique()

    # daily bars (mean sentiment per day UTC)
    daily = (
        df.set_index("published_at")
          .resample("1D")["sentiment"]
          .agg(["mean","count"])
          .rename(columns={"mean":"mean_sentiment"})
          .reset_index()
    )
    # day-over-day delta (today - yesterday)
    delta = 0.0
    if len(daily) >= 2 and pd.notna(daily["mean_sentiment"].iloc[-2]):
        delta = float((daily["mean_sentiment"].iloc[-1] or 0) - (daily["mean_sentiment"].iloc[-2] or 0))

    if overall >= 0.05:
        headline = "Bullish"
    elif overall <= -0.05:
        headline = "Bearish"
    else:
        headline = "Neutral"

    return {
        "headline": headline,
        "score": round(overall, 2),
        "sources": int(sources),
        "delta": round(delta, 2),
        "daily": daily,
    }
