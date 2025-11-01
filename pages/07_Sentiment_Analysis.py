from __future__ import annotations

import logging
from datetime import date

import pandas as pd
import streamlit as st

from tenacity import RetryError
from qts.data.news import fetch_news, aggregate_sentiment, NewsAPIError, NewsAPITransient
from qts.config import settings

log = logging.getLogger(__name__)

st.set_page_config(page_title="Sentiment Analysis", layout="wide")
st.title("Market Sentiment Analysis")

with st.expander("How this works", expanded=False):
    st.markdown(
        "- Pulls recent headlines via **NewsAPI** (free tier) for your query.\n"
        "- Uses **VADER** to score each headline/description.\n"
        "- Aggregates to a daily mean to draw the red/green bars.\n"
        "_Note: Free tier has rate limits & no deep history._"
    )

# ---------- Controls ----------
colq, colw, coldays = st.columns([3,1,1])
query = colq.text_input("Query (tickers, sectors, or keywords)", value="(AAPL OR Apple) AND (stock OR earnings OR iPhone)")
window = coldays.number_input("Lookback (days)", min_value=1, max_value=30, value=7, step=1)
page_info = colw.selectbox("Sort", ["publishedAt", "relevancy", "popularity"], index=0)

tabs = st.tabs(["News Sentiment", "Social Media (coming soon)", "Market Indicators (coming soon)"])

# ---------- NEWS TAB ----------
with tabs[0]:
    if not settings.NEWSAPI_KEY:
        st.warning("Add NEWSAPI_KEY to your .env to enable live news. Showing empty state.")
        st.stop()

    try:
        with st.spinner("Fetching fresh headlines..."):
            df = fetch_news(
                query,
                from_days=int(window),
                sort_by="publishedAt",   # safest on free plan
                max_pages=2,
                page_size=50,
            )

    except RetryError as re:
        # Unwrap the last exception to see why it kept failing
        last = getattr(re, "last_attempt", None)
        cause = getattr(last, "exception", lambda: None)()
        msg = f"{type(cause).__name__}: {cause}" if cause else str(re)
        st.warning(
            "Temporary issue talking to NewsAPI (rate limit or server hiccup). "
            "Please try again in a minute.\n\n"
            f"Details: {msg}"
        )
        st.stop()

    except NewsAPIError as e:
        # Non-retryable: wrong key/plan/params
        st.error(
            f"NewsAPI error: {e}\n\n"
            "Quick checks:\n"
            "• Is `NEWSAPI_KEY` valid and present in your `.env`?\n"
            "• On free plan, stick to `sortBy='publishedAt'`.\n"
            "• Keep `max_pages` small and queries simple.\n"
        )
        st.stop()

    except NewsAPITransient as e:
        st.warning(
            "NewsAPI is temporarily unavailable or you hit the rate limit. "
            "Try again shortly."
        )
        st.stop()

    agg = aggregate_sentiment(df)

    # headline metrics row
    m1, m2, m3 = st.columns(3)
    m1.metric("Overall Sentiment", agg["headline"], delta=None)
    m2.metric("Sentiment Score", f"{agg['score']:.2f}", delta=f"{agg['delta']:+.2f}")
    m3.metric("Sources Analyzed", f"{agg['sources']:,}", delta=None)

    st.subheader("Recent News Sentiment")

    # Daily bar chart (green for >0, red for <0); Streamlit Altair is fine here.
    if not agg["daily"].empty:
        d = agg["daily"].copy()
        d["date"] = d["published_at"].dt.date if "published_at" in d else d["published_at"]
        d = d.rename(columns={"mean_sentiment":"sentiment"})
        d["color"] = d["sentiment"].apply(lambda x: "positive" if x >= 0 else "negative")

        st.caption("Daily News Sentiment Score")
        st.bar_chart(d.set_index("date")["sentiment"])

    # Articles table
    with st.expander("Articles"):
        if df.empty:
            st.info("No articles returned for this query and window.")
        else:
            show = df[["published_at","source","title","sentiment","url"]].copy()
            show["published_at"] = show["published_at"].dt.tz_convert(None)
            st.dataframe(show, width='stretch')

# ---------- FUTURE TABS ----------
with tabs[1]:
    st.info("TODO: integrate X/Reddit APIs or a firehose proxy, then reuse the VADER pipeline.")
with tabs[2]:
    st.info("TODO: derive sentiment from options skew / put-call ratio / AAII survey, etc.")
