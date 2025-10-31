import os
import plotly.graph_objects as go
import streamlit as st
from qts import inject_css
from qts import FRED_PRESETS, fred_fetch_many, fred_transform, fred_key_loaded

inject_css()
st.markdown('<p class="main-header">Macro (FRED)</p>', unsafe_allow_html=True)
st.caption("Live FRED data with optional transforms and CSV download")

with st.sidebar:
    st.subheader("FRED Settings")
    st.write(f"FRED key loaded: {'✅' if fred_key_loaded() else '❌'}")
    if not fred_key_loaded():
        st.info("Add FRED_API_KEY to your .env at the repo root and restart the app.")

mode = st.radio("Mode", ["Preset", "Custom"], horizontal=True)
transform_kind = st.selectbox("Transform", ["level", "pct_change", "yoy"], index=0)

c1, c2 = st.columns(2)
with c1:
    start = st.date_input("Start", value=None)
with c2:
    end = st.date_input("End", value=None)

if mode == "Preset":
    names = list(FRED_PRESETS.keys())
    select = st.multiselect("Choose series", names, default=["CPI (All Urban Consumers)"])
    codes = [FRED_PRESETS[n] for n in select] if select else []
else:
    user_codes = st.text_input("Enter FRED series codes (comma-separated)", value="CPIAUCSL, UNRATE")
    codes = [c.strip() for c in user_codes.split(",") if c.strip()]

go_btn = st.button("Load Data", type="primary", disabled=(not codes) or (not fred_key_loaded()))

if go_btn:
    try:
        api_key = os.getenv("FRED_API_KEY", "")
        raw_df = fred_fetch_many(api_key, tuple(codes), start=start or None, end=end or None)
        tf_df = fred_transform(raw_df, transform_kind)
        if tf_df.empty:
            st.warning("No data returned for the selected series/date range.")
        else:
            st.success(f"Loaded {len(codes)} series. Rows: {len(tf_df)}")

            st.subheader("Data Preview")
            st.dataframe(tf_df.tail(200), width='stretch')

            st.subheader("Chart")
            fig = go.Figure()
            for col in tf_df.columns:
                fig.add_trace(go.Scatter(x=tf_df.index, y=tf_df[col], mode="lines", name=col))
            fig.update_layout(height=520, margin=dict(t=30, l=10, r=10, b=10))
            st.plotly_chart(fig, width='stretch')

            c1, c2 = st.columns(2)
            c1.download_button("Download transformed CSV", tf_df.to_csv(index=True).encode("utf-8"),
                               file_name="fred_transformed.csv", mime="text/csv")
            c2.download_button("Download raw CSV", raw_df.to_csv(index=True).encode("utf-8"),
                               file_name="fred_raw.csv", mime="text/csv")

            st.subheader("Latest values")
            clean = tf_df.dropna()
            if not clean.empty:
                last = clean.iloc[-1]
                cols = st.columns(min(4, len(last)))
                for i, (name, val) in enumerate(last.items()):
                    with cols[i % len(cols)]:
                        st.metric(name, f"{val:,.2f}")
    except Exception as e:
        st.error(f"Error loading FRED data: {e}")
else:
    st.write("Select series and click **Load Data** to fetch FRED data.")
    st.markdown(
        """
- Try presets: CPIAUCSL (CPI), UNRATE (Unemployment), FEDFUNDS (Fed Funds)  
- *pct_change* = period-to-period % change  
- *yoy* = 12-period % change (needs at least 13 observations)
"""
    )
