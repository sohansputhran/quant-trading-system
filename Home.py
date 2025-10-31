import streamlit as st
from qts import set_page_config, inject_css
from datetime import datetime

set_page_config("Quant Trading System")
inject_css()

st.sidebar.title("📊 Navigation")
st.sidebar.info(
    "Quant Trading System — automated data extraction, analysis, backtesting, and live trading."
)
st.sidebar.markdown("---")

st.markdown('<p class="main-header">Quant Trading System Dashboard</p>', unsafe_allow_html=True)
st.write("Use the left sidebar to navigate across pages.")

st.markdown("---")
st.caption(
    f"Data refresh every 5 minutes • Last updated: {datetime.now():%Y-%m-%d %H:%M:%S}"
)
