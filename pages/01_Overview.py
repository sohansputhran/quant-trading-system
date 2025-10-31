import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
from qts import inject_css

inject_css()
st.markdown('<p class="main-header">Overview</p>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Strategies", "12", "+3")
col2.metric("Active Trades", "5", "+2")
col3.metric("YTD Returns", "24.5%", "+5.2%")
col4.metric("Sharpe Ratio", "1.85", "+0.15")

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.subheader("🎯 Key Features")
    st.markdown(
        """
- **Data Extraction**: APIs & web scraping  
- **Technical Analysis**: Indicators & custom metrics  
- **Fundamentals**: Ratios and company metrics  
- **Backtesting**: Modular frameworks  
- **Live Trading**: Broker integrations  
- **Sentiment**: News & social    
"""
    )
with c2:
    st.subheader("📈 Recent Activity")
    activity = pd.DataFrame({
        "Date": pd.date_range(end=datetime.now(), periods=5, freq="D"),
        "Activity": [
            "Momentum Strategy executed 3 trades",
            "Mean Reversion Strategy: +2.3% return",
            "Data pipeline updated with new tickers",
            "Sentiment score: Bullish (0.72)",
            "Portfolio rebalanced",
        ],
    })
    st.dataframe(activity, hide_index=True, use_container_width=True)

st.markdown("---")
st.subheader("💼 Portfolio Allocation")
allocation = pd.DataFrame({"Asset": ["Equities", "Forex", "Crypto", "Cash"], "Allocation": [45, 30, 15, 10]})
fig = px.pie(allocation, values="Allocation", names="Asset", color_discrete_sequence=px.colors.sequential.Blues_r)
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)
