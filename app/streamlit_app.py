
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# New imports for FRED support
from dotenv import load_dotenv, find_dotenv
from fredapi import Fred

# Load .env so FRED_API_KEY is available regardless of CWD
load_dotenv(find_dotenv(usecwd=True))

# Page configuration
st.set_page_config(
    page_title="Quant Trading System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .positive {
        color: #00c853;
    }
    .negative {
        color: #ff3d00;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation  (added "Macro (FRED)")
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Overview", "Data Pipeline", "Macro (FRED)", "Technical Analysis", "Strategy Performance", "Live Trading", "Sentiment Analysis"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "Quant Trading System - A comprehensive automated trading platform "
    "integrating data extraction, analysis, backtesting, and live trading."
)

# ----------------------
# Helpers & sample data
# ----------------------
@st.cache_data
def generate_sample_price_data(days=365):
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    price = 100
    prices = []
    for _ in range(days):
        price = price * (1 + np.random.randn() * 0.02)
        prices.append(price)
    return pd.DataFrame({'Date': dates, 'Close': prices})

@st.cache_data
def generate_sample_strategy_data(days=365):
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    cumulative_returns = np.cumprod(1 + np.random.randn(days) * 0.015)
    benchmark = np.cumprod(1 + np.random.randn(days) * 0.01)
    return pd.DataFrame({
        'Date': dates,
        'Strategy': cumulative_returns,
        'Benchmark': benchmark
    })

# ----------------------
# FRED helpers
# ----------------------
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

FRED_PRESETS = {
    "CPI (All Urban Consumers)": "CPIAUCSL",
    "Unemployment Rate": "UNRATE",
    "Effective Fed Funds Rate": "FEDFUNDS",
    "Industrial Production Index": "INDPRO",
    "10Y Treasury Constant Maturity": "DGS10",
}

@st.cache_data(ttl=60*60)
def fred_fetch_many(api_key: str, codes, start=None, end=None) -> pd.DataFrame:
    fred = Fred(api_key=api_key)
    frames = []
    for code in codes:
        s = fred.get_series(code)
        df = s.to_frame(name=code)
        df.index.name = "Date"
        if start or end:
            df = df.loc[str(start or ""):str(end or "")]
        frames.append(df)
    out = pd.concat(frames, axis=1) if frames else pd.DataFrame()
    return out.sort_index()

def fred_transform(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    if kind == "level":
        return df
    if kind == "pct_change":
        return df.pct_change().mul(100)
    if kind == "yoy":
        # 12-period pct change (works for monthly series)
        return df.pct_change(12).mul(100)
    return df

# ----------------------
# PAGE: OVERVIEW
# ----------------------
if page == "Overview":
    st.markdown('<p class="main-header">Quant Trading System Dashboard</p>', unsafe_allow_html=True)
    st.markdown("### End-to-End Automated Trading Platform")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Strategies", "12", "+3")
    with col2:
        st.metric("Active Trades", "5", "+2")
    with col3:
        st.metric("YTD Returns", "24.5%", "+5.2%")
    with col4:
        st.metric("Sharpe Ratio", "1.85", "+0.15")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Key Features")
        st.markdown("""
        - **Data Extraction**: Daily and intraday data via APIs and web scraping
        - **Technical Analysis**: Multiple indicators and custom metrics
        - **Fundamental Analysis**: Financial ratios and company metrics
        - **Strategy Development**: Modular backtesting framework
        - **Live Trading**: Integration with FXCM and OANDA APIs
        - **Sentiment Analysis**: Market sentiment from news and social media
        """)
    
    with col2:
        st.markdown("#### 📈 Recent Activity")
        activity_data = pd.DataFrame({
            'Date': pd.date_range(end=datetime.now(), periods=5, freq='D'),
            'Activity': [
                'Momentum Strategy executed 3 trades',
                'Mean Reversion Strategy: +2.3% return',
                'Data pipeline updated with new tickers',
                'Sentiment score: Bullish (0.72)',
                'Portfolio rebalanced'
            ]
        })
        st.dataframe(activity_data, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### 💼 Portfolio Allocation")
    
    allocation = pd.DataFrame({
        'Asset': ['Equities', 'Forex', 'Crypto', 'Cash'],
        'Allocation': [45, 30, 15, 10]
    })
    
    fig = px.pie(allocation, values='Allocation', names='Asset', 
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ----------------------
# PAGE: DATA PIPELINE
# ----------------------
elif page == "Data Pipeline":
    st.markdown('<p class="main-header">Data Pipeline</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Data Sources", "Data Quality", "Recent Updates"])
    
    with tab1:
        st.markdown("#### 📊 Connected Data Sources")
        
        sources = pd.DataFrame({
            'Source': ['Alpha Vantage', 'Yahoo Finance', 'FXCM API', 'OANDA API', 'Web Scraping'],
            'Type': ['API', 'API', 'Broker API', 'Broker API', 'Custom'],
            'Status': ['Active', 'Active', 'Active', 'Active', 'Active'],
            'Last Update': ['2 min ago', '5 min ago', '1 min ago', '3 min ago', '10 min ago'],
            'Records': ['12,450', '8,320', '3,210', '2,890', '5,600']
        })
        st.dataframe(sources, hide_index=True, use_container_width=True)
    
    with tab2:
        st.markdown("#### ✅ Data Quality Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Completeness", "98.5%")
        with col2:
            st.metric("Accuracy", "99.2%")
        with col3:
            st.metric("Timeliness", "99.8%")
        with col4:
            st.metric("Missing Values", "0.3%")
        
        st.markdown("#### Data Volume Over Time")
        volume_data = pd.DataFrame({
            'Date': pd.date_range(end=datetime.now(), periods=30, freq='D'),
            'Records': np.random.randint(8000, 12000, 30)
        })
        
        fig = px.line(volume_data, x='Date', y='Records', 
                     title='Daily Data Records Collected')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("#### 🔄 Recent Data Updates")
        
        updates = pd.DataFrame({
            'Timestamp': pd.date_range(end=datetime.now(), periods=10, freq='5min')[::-1],
            'Ticker': ['AAPL', 'GOOGL', 'EUR/USD', 'BTC/USD', 'MSFT', 
                      'TSLA', 'GBP/USD', 'ETH/USD', 'AMZN', 'NVDA'],
            'Data Type': ['Stock', 'Stock', 'Forex', 'Crypto', 'Stock',
                         'Stock', 'Forex', 'Crypto', 'Stock', 'Stock'],
            'Price': ['$178.45', '$142.30', '1.0952', '$62,450', '$412.80',
                     '$265.33', '1.3045', '$3,210', '$183.25', '$485.90']
        })
        st.dataframe(updates, hide_index=True, use_container_width=True)

# ----------------------
# PAGE: MACRO (FRED)  -- NEW
# ----------------------
elif page == "Macro (FRED)":
    st.markdown('<p class="main-header">Macro (FRED)</p>', unsafe_allow_html=True)
    st.caption("Live FRED data with optional transforms and CSV download")
    
    with st.sidebar:
        st.subheader("FRED Settings")
        st.write(f"FRED key loaded: {'✅' if bool(FRED_API_KEY) else '❌'}")
        if not FRED_API_KEY:
            st.info("Add FRED_API_KEY to your .env at the repo root and restart the app.")
    
    mode = st.radio("Mode", ["Preset", "Custom"], horizontal=True)
    transform_kind = st.selectbox("Transform", ["level", "pct_change", "yoy"], index=0)
    
    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("Start", value=None)
    with c2:
        end = st.date_input("End", value=None)
    
    if mode == "Preset":
        preset_names = list(FRED_PRESETS.keys())
        default = ["CPI (All Urban Consumers)"]
        select = st.multiselect("Choose series", preset_names, default=default)
        codes = [FRED_PRESETS[n] for n in select] if select else []
    else:
        user_codes = st.text_input("Enter FRED series codes (comma-separated)", value="CPIAUCSL, UNRATE")
        codes = [c.strip() for c in user_codes.split(",") if c.strip()]
    
    go_btn = st.button("Load Data", type="primary", disabled=(not codes) or (not FRED_API_KEY))
    
    if go_btn:
        try:
            raw_df = fred_fetch_many(FRED_API_KEY, tuple(codes), start=start or None, end=end or None)
            tf_df = fred_transform(raw_df, transform_kind)
            if tf_df.empty:
                st.warning("No data returned for the selected series/date range.")
            else:
                st.success(f"Loaded {len(codes)} series. Rows: {len(tf_df)}")
                
                st.subheader("Data Preview")
                st.dataframe(tf_df.tail(200), use_container_width=True)
                
                st.subheader("Chart")
                fig = go.Figure()
                for col in tf_df.columns:
                    fig.add_trace(go.Scatter(x=tf_df.index, y=tf_df[col], mode="lines", name=col))
                fig.update_layout(height=520, margin=dict(t=30, l=10, r=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
                
                # Downloads
                d1, d2 = st.columns(2)
                with d1:
                    st.download_button(
                        "Download transformed CSV",
                        tf_df.to_csv(index=True).encode("utf-8"),
                        file_name="fred_transformed.csv",
                        mime="text/csv",
                    )
                with d2:
                    st.download_button(
                        "Download raw CSV",
                        raw_df.to_csv(index=True).encode("utf-8"),
                        file_name="fred_raw.csv",
                        mime="text/csv",
                    )
                
                # Latest metrics
                st.subheader("Latest values")
                clean = tf_df.dropna()
                if not clean.empty:
                    last = clean.iloc[-1]
                    cols = st.columns(min(4, len(last)))
                    for i, (name, val) in enumerate(last.items()):
                        with cols[i % len(cols)]:
                            st.metric(name, f"{val:,.2f}")
                else:
                    st.write("No non-NaN values to show yet. Try a different transform or longer date range.")
        except Exception as e:
            st.error(f"Error loading FRED data: {e}")
    else:
        st.write("Select series and click **Load Data** to fetch FRED data.")
        st.markdown(
            """
            **Tips**
            - Try presets: CPIAUCSL (CPI), UNRATE (Unemployment), FEDFUNDS (Fed Funds)
            - *pct_change* = period-to-period % change
            - *yoy* = 12-period % change (needs at least 13 observations)
            """
        )

# ----------------------
# PAGE: TECHNICAL ANALYSIS
# ----------------------
elif page == "Technical Analysis":
    st.markdown('<p class="main-header">Technical Analysis</p>', unsafe_allow_html=True)
    
    ticker = st.selectbox("Select Ticker", ["AAPL", "GOOGL", "MSFT", "TSLA", "EUR/USD", "BTC/USD"])
    
    df = generate_sample_price_data(365)
    
    # Calculate indicators
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    
    # RSI calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"${df['Close'].iloc[-1]:.2f}", 
                 f"{((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100):.2f}%")
    with col2:
        st.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
    with col3:
        st.metric("SMA (20)", f"${df['SMA_20'].iloc[-1]:.2f}")
    with col4:
        st.metric("SMA (50)", f"${df['SMA_50'].iloc[-1]:.2f}")
    
    # Price chart with indicators
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Price', line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_20'], name='SMA 20', line=dict(color='orange', width=1)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], name='SMA 50', line=dict(color='red', width=1)))
    fig.update_layout(title=f'{ticker} - Price with Moving Averages', 
                     xaxis_title='Date', yaxis_title='Price ($)', height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # RSI chart
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], name='RSI', line=dict(color='purple')))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
    fig_rsi.update_layout(title='Relative Strength Index (RSI)', 
                         xaxis_title='Date', yaxis_title='RSI', height=300)
    st.plotly_chart(fig_rsi, use_container_width=True)

# ----------------------
# PAGE: STRATEGY PERFORMANCE
# ----------------------
elif page == "Strategy Performance":
    st.markdown('<p class="main-header">Strategy Performance</p>', unsafe_allow_html=True)
    
    strategy = st.selectbox("Select Strategy", 
                           ["Momentum Strategy", "Mean Reversion", "Moving Average Crossover", 
                            "RSI Oscillator", "Bollinger Bands"])
    
    df = generate_sample_strategy_data(365)
    
    # Calculate metrics
    strategy_returns = df['Strategy'].pct_change().dropna()
    total_return = (df['Strategy'].iloc[-1] / df['Strategy'].iloc[0] - 1) * 100
    sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
    max_drawdown = ((df['Strategy'].cummax() - df['Strategy']) / df['Strategy'].cummax()).max() * 100
    win_rate = (strategy_returns > 0).sum() / len(strategy_returns) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Return", f"{total_return:.2f}%")
    with col2:
        st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
    with col3:
        st.metric("Max Drawdown", f"{max_drawdown:.2f}%")
    with col4:
        st.metric("Win Rate", f"{win_rate:.2f}%")
    
    st.markdown("---")
    
    # Equity curve
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Strategy'], name='Strategy', 
                            line=dict(color='#1f77b4', width=2)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Benchmark'], name='Benchmark', 
                            line=dict(color='gray', width=1, dash='dash')))
    fig.update_layout(title='Cumulative Returns: Strategy vs Benchmark', 
                     xaxis_title='Date', yaxis_title='Cumulative Return', height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Returns Distribution")
        fig_hist = px.histogram(strategy_returns, nbins=50, 
                               labels={'value': 'Daily Returns', 'count': 'Frequency'})
        fig_hist.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.markdown("#### 📈 Monthly Returns")
        monthly_returns = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
            'Return': [2.3, -0.5, 3.1, 1.8, -1.2, 2.7, 1.5, 3.4, 0.9]
        })
        fig_bar = px.bar(monthly_returns, x='Month', y='Return',
                        color='Return', color_continuous_scale=['red', 'green'])
        fig_bar.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------
# PAGE: LIVE TRADING
# ----------------------
elif page == "Live Trading":
    st.markdown('<p class="main-header">Live Trading</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio Value", "$125,430", "+$2,340")
    with col2:
        st.metric("Today's P&L", "+$1,245", "+0.99%")
    with col3:
        st.metric("Open Positions", "5")
    with col4:
        st.metric("Available Cash", "$34,570")
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["Open Positions", "Trade History", "Order Book"])
    
    with tab1:
        st.markdown("#### 📌 Current Positions")
        positions = pd.DataFrame({
            'Ticker': ['AAPL', 'GOOGL', 'EUR/USD', 'MSFT', 'BTC/USD'],
            'Quantity': [50, 30, 10000, 40, 0.5],
            'Entry Price': ['$175.20', '$139.80', '1.0920', '$408.50', '$61,200'],
            'Current Price': ['$178.45', '$142.30', '1.0952', '$412.80', '$62,450'],
            'P&L': ['+$162.50', '+$75.00', '+$320.00', '+$172.00', '+$625.00'],
            'P&L %': ['+1.85%', '+1.79%', '+0.29%', '+1.05%', '+2.04%']
        })
        st.dataframe(positions, hide_index=True, use_container_width=True)
    
    with tab2:
        st.markdown("#### 📜 Recent Trades")
        trades = pd.DataFrame({
            'Timestamp': pd.date_range(end=datetime.now(), periods=10, freq='2H')[::-1],
            'Ticker': ['AAPL', 'GOOGL', 'MSFT', 'EUR/USD', 'TSLA', 
                      'BTC/USD', 'AAPL', 'AMZN', 'NVDA', 'ETH/USD'],
            'Action': ['BUY', 'BUY', 'SELL', 'BUY', 'SELL', 
                      'BUY', 'SELL', 'BUY', 'BUY', 'SELL'],
            'Quantity': [50, 30, 25, 10000, 15, 0.5, 20, 10, 20, 2],
            'Price': ['$175.20', '$139.80', '$410.30', '1.0920', '$268.50',
                     '$61,200', '$177.80', '$181.40', '$482.90', '$3,180'],
            'P&L': ['-', '-', '+$45.00', '-', '+$180.00', 
                   '-', '+$52.00', '-', '-', '+$60.00']
        })
        st.dataframe(trades, hide_index=True, use_container_width=True)
    
    with tab3:
        st.markdown("#### 📋 Pending Orders")
        orders = pd.DataFrame({
            'Order ID': ['ORD-1001', 'ORD-1002', 'ORD-1003', 'ORD-1004'],
            'Ticker': ['AAPL', 'TSLA', 'EUR/USD', 'NVDA'],
            'Type': ['LIMIT BUY', 'STOP LOSS', 'LIMIT SELL', 'LIMIT BUY'],
            'Quantity': [25, 20, 5000, 15],
            'Target Price': ['$172.00', '$260.00', '1.1000', '$475.00'],
            'Status': ['Pending', 'Pending', 'Pending', 'Pending']
        })
        st.dataframe(orders, hide_index=True, use_container_width=True)

# ----------------------
# PAGE: SENTIMENT ANALYSIS
# ----------------------
elif page == "Sentiment Analysis":
    st.markdown('<p class="main-header">Market Sentiment Analysis</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Sentiment", "Bullish", "↑")
    with col2:
        st.metric("Sentiment Score", "0.72", "+0.08")
    with col3:
        st.metric("Sources Analyzed", "2,450", "+320")
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["News Sentiment", "Social Media", "Market Indicators"])
    
    with tab1:
        st.markdown("#### 📰 Recent News Sentiment")
        
        sentiment_data = pd.DataFrame({
            'Date': pd.date_range(end=datetime.now(), periods=30, freq='D'),
            'Sentiment': np.random.uniform(-1, 1, 30)
        })
        
        fig = go.Figure()
        colors = ['green' if x > 0 else 'red' for x in sentiment_data['Sentiment']]
        fig.add_trace(go.Bar(x=sentiment_data['Date'], y=sentiment_data['Sentiment'],
                            marker_color=colors, name='Sentiment'))
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.update_layout(title='Daily News Sentiment Score', 
                         xaxis_title='Date', yaxis_title='Sentiment Score', height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### Top News Headlines")
        news = pd.DataFrame({
            'Headline': [
                'Tech stocks rally on positive earnings reports',
                'Federal Reserve signals potential rate cuts',
                'Oil prices surge on supply concerns',
                'Major merger announced in pharmaceutical sector',
                'Cryptocurrency market shows strong recovery'
            ],
            'Sentiment': ['Positive', 'Positive', 'Neutral', 'Positive', 'Positive'],
            'Score': [0.85, 0.72, 0.15, 0.68, 0.91],
            'Source': ['Reuters', 'Bloomberg', 'CNBC', 'WSJ', 'CoinDesk']
        })
        st.dataframe(news, hide_index=True, use_container_width=True)
    
    with tab2:
        st.markdown("#### 💬 Social Media Sentiment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            platforms = pd.DataFrame({
                'Platform': ['Twitter', 'Reddit', 'StockTwits', 'Discord'],
                'Posts': [12450, 3280, 5620, 1890]
            })
            fig_pie = px.pie(platforms, values='Posts', names='Platform',
                            title='Posts by Platform')
            fig_pie.update_layout(height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            tickers = pd.DataFrame({
                'Ticker': ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL'],
                'Mentions': [4520, 3840, 2960, 2450, 1980],
                'Sentiment': [0.68, 0.72, 0.81, 0.65, 0.58]
            })
            fig_bar = px.bar(tickers, x='Ticker', y='Mentions',
                            color='Sentiment', color_continuous_scale=['red', 'yellow', 'green'],
                            title='Most Mentioned Tickers')
            fig_bar.update_layout(height=300)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab3:
        st.markdown("#### 📊 Technical Sentiment Indicators")
        
        indicators = pd.DataFrame({
            'Indicator': ['Fear & Greed Index', 'Put/Call Ratio', 'VIX', 'Advance/Decline Ratio', 'New Highs/Lows'],
            'Value': ['68 (Greed)', '0.82', '15.4', '1.45', '2.8:1'],
            'Signal': ['Bullish', 'Bullish', 'Low Volatility', 'Bullish', 'Bullish'],
            'Change': ['↑ +5', '↓ -0.08', '↓ -1.2', '↑ +0.15', '↑']
        })
        st.dataframe(indicators, hide_index=True, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Quant Trading System Dashboard | Data updates every 5 minutes | "
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    "</div>", 
    unsafe_allow_html=True
)
