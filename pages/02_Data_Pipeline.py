import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
from qts import inject_css

inject_css()
st.markdown('<p class="main-header">Data Pipeline</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Data Sources", "Data Quality", "Recent Updates"])

with tab1:
    st.subheader("📊 Connected Data Sources")
    sources = pd.DataFrame({
        "Source": ["Alpha Vantage", "Yahoo Finance", "FXCM API", "OANDA API", "Web Scraping"],
        "Type":   ["API", "API", "Broker API", "Broker API", "Custom"],
        "Status": ["Active", "Active", "Active", "Active", "Active"],
        "Last Update": ["2 min ago", "5 min ago", "1 min ago", "3 min ago", "10 min ago"],
        "Records": ["12,450", "8,320", "3,210", "2,890", "5,600"],
    })
    st.dataframe(sources, hide_index=True, width='stretch')

with tab2:
    st.subheader("✅ Data Quality Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Completeness", "98.5%")
    c2.metric("Accuracy", "99.2%")
    c3.metric("Timeliness", "99.8%")
    c4.metric("Missing Values", "0.3%")

    st.subheader("Data Volume Over Time")
    volume = pd.DataFrame({
        "Date": pd.date_range(end=datetime.now(), periods=30, freq="D"),
        "Records": np.random.randint(8000, 12000, 30),
    })
    fig = px.line(volume, x="Date", y="Records", title="Daily Data Records Collected")
    fig.update_layout(height=400)
    st.plotly_chart(fig, width='stretch')

with tab3:
    st.subheader("🔄 Recent Data Updates")
    updates = pd.DataFrame({
        "Timestamp": pd.date_range(end=datetime.now(), periods=10, freq="5min")[::-1],
        "Ticker": ["AAPL", "GOOGL", "EUR/USD", "BTC/USD", "MSFT", "TSLA", "GBP/USD", "ETH/USD", "AMZN", "NVDA"],
        "Data Type": ["Stock", "Stock", "Forex", "Crypto", "Stock", "Stock", "Forex", "Crypto", "Stock", "Stock"],
        "Price": ["$178.45", "$142.30", "1.0952", "$62,450", "$412.80", "$265.33", "1.3045", "$3,210", "$183.25", "$485.90"],
    })
    st.dataframe(updates, hide_index=True, width='stretch')