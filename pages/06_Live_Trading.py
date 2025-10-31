import pandas as pd
import streamlit as st
from datetime import datetime
from qts import inject_css

inject_css()
st.markdown('<p class="main-header">Live Trading</p>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Portfolio Value", "$125,430", "+$2,340")
c2.metric("Today's P&L", "+$1,245", "+0.99%")
c3.metric("Open Positions", "5")
c4.metric("Available Cash", "$34,570")

st.markdown("---")
t1, t2, t3 = st.tabs(["Open Positions", "Trade History", "Order Book"])

with t1:
    st.subheader("📌 Current Positions")
    positions = pd.DataFrame({
        "Ticker": ["AAPL","GOOGL","EUR/USD","MSFT","BTC/USD"],
        "Quantity": [50,30,10000,40,0.5],
        "Entry Price": ["$175.20","$139.80","1.0920","$408.50","$61,200"],
        "Current Price": ["$178.45","$142.30","1.0952","$412.80","$62,450"],
        "P&L": ["+$162.50","+$75.00","+$320.00","+$172.00","+$625.00"],
        "P&L %": ["+1.85%","+1.79%","+0.29%","+1.05%","+2.04%"],
    })
    st.dataframe(positions, hide_index=True, width='stretch')

with t2:
    st.subheader("📜 Recent Trades")
    trades = pd.DataFrame({
        "Timestamp": pd.date_range(end=datetime.now(), periods=10, freq="2H")[::-1],
        "Ticker": ["AAPL","GOOGL","MSFT","EUR/USD","TSLA","BTC/USD","AAPL","AMZN","NVDA","ETH/USD"],
        "Action": ["BUY","BUY","SELL","BUY","SELL","BUY","SELL","BUY","BUY","SELL"],
        "Quantity": [50,30,25,10000,15,0.5,20,10,20,2],
        "Price": ["$175.20","$139.80","$410.30","1.0920","$268.50","$61,200","$177.80","$181.40","$482.90","$3,180"],
        "P&L": ["-","-","+$45.00","-","+$180.00","-","+$52.00","-","-","+$60.00"],
    })
    st.dataframe(trades, hide_index=True, width='stretch')

with t3:
    st.subheader("📋 Pending Orders")
    orders = pd.DataFrame({
        "Order ID": ["ORD-1001","ORD-1002","ORD-1003","ORD-1004"],
        "Ticker": ["AAPL","TSLA","EUR/USD","NVDA"],
        "Type": ["LIMIT BUY","STOP LOSS","LIMIT SELL","LIMIT BUY"],
        "Quantity": [25,20,5000,15],
        "Target Price": ["$172.00","$260.00","1.1000","$475.00"],
        "Status": ["Pending","Pending","Pending","Pending"],
    })
    st.dataframe(orders, hide_index=True, width='stretch')