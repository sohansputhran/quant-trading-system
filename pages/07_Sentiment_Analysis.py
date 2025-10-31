import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from qts import inject_css

inject_css()
st.markdown('<p class="main-header">Market Sentiment Analysis</p>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("Overall Sentiment", "Bullish", "↑")
c2.metric("Sentiment Score", "0.72", "+0.08")
c3.metric("Sources Analyzed", "2,450", "+320")

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["News Sentiment", "Social Media", "Market Indicators"])

with tab1:
    st.subheader("📰 Recent News Sentiment")
    sentiment = pd.DataFrame({"Date": pd.date_range(end=datetime.now(), periods=30, freq="D"),
                              "Sentiment": np.random.uniform(-1, 1, 30)})
    colors = ["green" if x > 0 else "red" for x in sentiment["Sentiment"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=sentiment["Date"], y=sentiment["Sentiment"], marker_color=colors, name="Sentiment"))
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(title="Daily News Sentiment Score", xaxis_title="Date", yaxis_title="Sentiment", height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top News Headlines")
    news = pd.DataFrame({
        "Headline": [
            "Tech stocks rally on positive earnings reports",
            "Federal Reserve signals potential rate cuts",
            "Oil prices surge on supply concerns",
            "Major merger announced in pharmaceutical sector",
            "Cryptocurrency market shows strong recovery",
        ],
        "Sentiment": ["Positive","Positive","Neutral","Positive","Positive"],
        "Score": [0.85,0.72,0.15,0.68,0.91],
        "Source": ["Reuters","Bloomberg","CNBC","WSJ","CoinDesk"],
    })
    st.dataframe(news, hide_index=True, use_container_width=True)

with tab2:
    st.subheader("💬 Social Media Sentiment")
    c1, c2 = st.columns(2)
    with c1:
        platforms = pd.DataFrame({"Platform": ["Twitter","Reddit","StockTwits","Discord"], "Posts": [12450, 3280, 5620, 1890]})
        st.plotly_chart(px.pie(platforms, values="Posts", names="Platform", title="Posts by Platform").update_layout(height=300), use_container_width=True)
    with c2:
        tickers = pd.DataFrame({"Ticker": ["AAPL","TSLA","NVDA","MSFT","GOOGL"], "Mentions": [4520,3840,2960,2450,1980], "Sentiment": [0.68,0.72,0.81,0.65,0.58]})
        st.plotly_chart(px.bar(tickers, x="Ticker", y="Mentions", color="Sentiment", color_continuous_scale=["red","yellow","green"], title="Most Mentioned Tickers").update_layout(height=300), use_container_width=True)

with tab3:
    st.subheader("📊 Technical Sentiment Indicators")
    indicators = pd.DataFrame({
        "Indicator": ["Fear & Greed Index", "Put/Call Ratio", "VIX", "Advance/Decline Ratio", "New Highs/Lows"],
        "Value": ["68 (Greed)", "0.82", "15.4", "1.45", "2.8:1"],
        "Signal": ["Bullish", "Bullish", "Low Volatility", "Bullish", "Bullish"],
        "Change": ["↑ +5", "↓ -0.08", "↓ -1.2", "↑ +0.15", "↑"],
    })
    st.dataframe(indicators, hide_index=True, use_container_width=True)
