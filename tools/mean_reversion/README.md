# Mean Reversion Trading Strategy Tools

This project provides a set of tools for analyzing cryptocurrency price data and identifying mean reversion opportunities.

## Structure

The project has been reorganized into a more maintainable structure:

```
Mean_Reversion/
├── core/             - Core functionality
│   ├── api.py        - API client for price data (CoinGecko, DeFi Llama, CoinAPI)
│   └── indicators.py - Technical indicator calculations
├── tools/            - Tool integrations
│   └── langchain_tools.py - LangChain tool wrappers
├── example.py        - Example usage
├── defillama_example.py - DeFi Llama API example
├── ohlc_example.py   - OHLC data example
├── test_api.py       - API testing script
├── test_ohlc.py      - OHLC data testing script
└── test_indicators.py - Test script
```

## Features

- Fetch cryptocurrency price data from public APIs (CoinGecko, DeFi Llama, and CoinAPI)
- Calculate technical indicators:
  - Z-score (deviation from mean)
  - RSI (Relative Strength Index)
  - Bollinger Bands
  - MACD (Moving Average Convergence Divergence)
  - ATR (Average True Range)
- Support for OHLC (Open, High, Low, Close) candle data for detailed technical analysis
- Identify mean reversion opportunities
- Multiple data provider support (switch between providers)
- LangChain integration for AI agents
- Historical analysis capabilities

## Getting Started

### Prerequisites

```
pip install requests pandas numpy langchain-core
```

### Basic Usage

```python
from core.api import TokenPriceAPI
from core.indicators import MeanReversionService

# Initialize the service with DeFi Llama (default)
service = MeanReversionService()

# Get metrics for a token
metrics = service.get_all_metrics("bitcoin")
print(f"Bitcoin Z-Score: {metrics['metrics']['z_score']['value']}")
print(f"Bitcoin RSI: {metrics['metrics']['rsi']['value']}")

# Using CoinGecko API instead
service_cg = MeanReversionService(api_provider="coingecko")
metrics_cg = service_cg.get_all_metrics("ethereum")
print(f"Ethereum Z-Score (CoinGecko): {metrics_cg['metrics']['z_score']['value']}")
```

### Using with LangChain

```python
from tools.langchain_tools import get_token_indicators

# Get indicators directly using DeFi Llama (default)
result = get_token_indicators("ethereum")
print(result)

# Get indicators using CoinGecko
result_cg = get_token_indicators("ethereum", api_provider="coingecko")
print(result_cg)

# Or use with a LangChain agent
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.render import format_tool_to_openai_function
from langchain.schema import SystemMessage

# Define your agent with the tools
# See example.py for a complete implementation
```

## Examples

- See `example.py` for complete examples of using the tools directly and with LangChain agents.
- See `defillama_example.py` for examples specifically demonstrating the DeFi Llama API integration.
- See `ohlc_example.py` for examples using OHLC data with CoinAPI.
- See `test_api.py` for examples comparing CoinGecko and DeFi Llama APIs.

## Testing

To run the tests:

```bash
python test_api.py           # Tests both price APIs and compares them
python defillama_example.py  # Tests DeFi Llama integration
python test_ohlc.py          # Tests OHLC data from CoinAPI
```

## License

See the LICENSE file for details.
