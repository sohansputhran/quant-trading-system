import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from qts import inject_css, generate_sample_strategy_data

inject_css()
st.markdown('<p class="main-header">Strategy Performance</p>', unsafe_allow_html=True)

strategy = st.selectbox("Select Strategy", ["Momentum Strategy", "Mean Reversion", "Moving Average Crossover",
                                            "RSI Oscillator", "Bollinger Bands"])
df = generate_sample_strategy_data(365)

ret = df["Strategy"].pct_change().dropna()
total_return = (df["Strategy"].iloc[-1] / df["Strategy"].iloc[0] - 1) * 100
sharpe = ret.mean() / ret.std() * np.sqrt(252)
max_dd = ((df["Strategy"].cummax() - df["Strategy"]) / df["Strategy"].cummax()).max() * 100
win_rate = (ret > 0).sum() / len(ret) * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Return", f"{total_return:.2f}%")
c2.metric("Sharpe Ratio", f"{sharpe:.2f}")
c3.metric("Max Drawdown", f"{max_dd:.2f}%")
c4.metric("Win Rate", f"{win_rate:.2f}%")

st.markdown("---")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Date"], y=df["Strategy"], name="Strategy", line=dict(color="#1f77b4", width=2)))
fig.add_trace(go.Scatter(x=df["Date"], y=df["Benchmark"], name="Benchmark", line=dict(color="gray", width=1, dash="dash")))
fig.update_layout(title="Cumulative Returns: Strategy vs Benchmark", xaxis_title="Date", yaxis_title="Cumulative Return", height=500)
st.plotly_chart(fig, width='stretch')

c1, c2 = st.columns(2)
with c1:
    st.subheader("📊 Returns Distribution")
    st.plotly_chart(px.histogram(ret, nbins=50, labels={"value": "Daily Returns", "count": "Frequency"}).update_layout(showlegend=False, height=300), width='stretch')
with c2:
    st.subheader("📈 Monthly Returns")
    monthly = {"Month": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep"], "Return": [2.3,-0.5,3.1,1.8,-1.2,2.7,1.5,3.4,0.9]}
    st.plotly_chart(px.bar(monthly, x="Month", y="Return", color="Return", color_continuous_scale=["red","green"]).update_layout(height=300, showlegend=False), width='stretch')