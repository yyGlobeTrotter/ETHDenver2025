# Mean Reversion Strategy Tools

A collection of tools for implementing and analyzing cryptocurrency mean reversion trading strategies. This package provides data fetching, technical indicator calculation, and analysis tools without requiring AI components.

## Core Components

The package is structured around three main components:

1. **API Module (`core/api.py`)** - Data fetching and manipulation
   - `TokenPriceAPI` - Fetches price data from different sources (DeFi Llama, CoinGecko, CoinAPI)
   - `OHLCData` - Data class for Open, High, Low, Close candle data

2. **Indicators Module (`core/indicators.py`)** - Technical indicators
   - `MeanReversionIndicators` - Core calculations for technical indicators
   - `MeanReversionService` - Higher-level service combining API and indicators with utilities

3. **Demo Script (`mean_reversion_demo.py`)** - Example usage
   - Demonstrates how to use the core components directly without AI

## Usage

The simplified demo script shows how to use the core components without any AI dependencies:

```python
from core.api import TokenPriceAPI
from core.indicators import MeanReversionIndicators

# Initialize components
api = TokenPriceAPI()
indicators = MeanReversionIndicators()

# Get price data
token_id = "bitcoin"
current_price = api.get_price(token_id)
prices, dates = api.get_historical_prices(token_id, days=30)

# Calculate indicators
z_score = indicators.calculate_z_score(prices, window=20)
rsi = indicators.calculate_rsi(prices, window=14)
bb = indicators.calculate_bollinger_bands(prices, window=20, num_std=2.0)

# Interpret results
z_interpretation = indicators.interpret_z_score(z_score)
rsi_interpretation = indicators.interpret_rsi(rsi)
bb_interpretation = indicators.interpret_bb(bb['percent_b'])

# Print results
print(f"Current price: ${current_price:.2f}")
print(f"Z-Score: {z_score:.2f} - {z_interpretation}")
print(f"RSI: {rsi:.2f} - {rsi_interpretation}")
print(f"Bollinger %B: {bb['percent_b']:.2f} - {bb_interpretation}")
```

## Available Indicators

The package provides several key mean reversion indicators:

1. **Z-Score** - Measures how many standard deviations price is from its mean
2. **RSI (Relative Strength Index)** - Momentum oscillator showing overbought/oversold conditions
3. **Bollinger Bands** - Volatility-based bands around a moving average
4. **ATR (Average True Range)** - Measures market volatility
5. **MACD (Moving Average Convergence Divergence)** - Trend-following momentum indicator

## Integration Options

While this package can be used standalone, it also integrates with:

1. **LangChain Tools** - For AI-based analysis and natural language interaction (see `langchain_tools.py`)
2. **Coinbase Developer Platform (CDP) AgentKit** - For blockchain interaction (see `/Users/mitch/Desktop/mean_reversion/ETHDenver2025/dexy/chatbot.py`)

## Data Providers

The package supports multiple data providers:

1. **DeFi Llama API** (default) - Free and reliable price data
2. **CoinGecko API** - Popular cryptocurrency data API
3. **CoinAPI** - Premium API with OHLC (candle) data support

## Running the Demo

```bash
python mean_reversion_demo.py
```

The demo will:
1. Run basic mean reversion analysis on Bitcoin
2. Compare mean reversion signals across multiple cryptocurrencies
3. Optionally run OHLC-based analysis (requires CoinAPI key)