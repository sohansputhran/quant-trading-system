# Quant-Trading-System

**Quant-Trading-System** is a Python-based automated trading platform that integrates data extraction, technical and fundamental analysis, strategy backtesting, and live trading using broker APIs. This project showcases end-to-end quantitative analysis and algorithmic trading workflows.

## Features

- Extract daily and intraday data via APIs and web scraping
- Apply technical and fundamental analysis
- Develop and backtest trading strategies
- Integrate live trading via FXCM and OANDA APIs
- Perform sentiment analysis
- Visualize time series data

## Project Structure

```
quant-trading-system/
|-- 01_data_collection/
|-- 02_data_analysis/
|-- 03_strategy/
|-- 04_api_trading/
|-- 05_sentiment_analysis/
|-- notebooks/
|-- utils/
|-- .env
|-- .venv/
|-- requirements.txt
|-- README.md
|-- LICENSE
```

## Installation

```bash
git clone https://github.com/yourusername/quant-trading-system.git
cd quant-trading-system
pip install -r requirements.txt
```

## Getting Started

Explore the notebooks in the `notebooks/` folder or begin implementing trading strategies in `03_strategy/`.

# API Key Setup

Create a `.env` file in the root directory using the `.env.example` template and insert your API key:

ALPHA_API_KEY=your_actual_api_key

## License

[MIT](LICENSE)
