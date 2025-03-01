# Crypto Trading Strategy Tools for LangChain

This project provides tools for building, backtesting, and analyzing cryptocurrency trading strategies, integrated with LangChain.  It focuses on Mean Reversion and Moving Average Crossover strategies, but is easily extensible.

## Features

*   **Data Retrieval:** Fetches current/historical prices from CoinGecko or DeFi Llama, and OHLC data from CoinAPI.
*   **Technical Indicators:** Z-score, RSI, Bollinger Bands, Moving Averages, MACD, and ATR.
*   **OHLC Support:** Full OHLC (Open, High, Low, Close) candle data for advanced technical analysis.
*   **Trading Strategies:** Mean Reversion, Moving Average Crossover.
*   **Backtesting:** Evaluates performance on historical data.
*   **Optimization:** Finds optimal strategy parameters.
*   **Visualization:** Plots backtest results.
*   **LangChain Integration:**  Ready to use with LangChain agents and OpenAI function calling.
*   **Artifact Return:**  Provides structured data artifacts for further processing.
*   **Multiple API Providers:** Support for CoinGecko, DeFi Llama, and CoinAPI.

## Requirements

*   Python 3.8+
*   `langchain-core`, `langchain-openai`, `requests`, `pandas`, `numpy`, `matplotlib`

## Installation


pip install langchain-core langchain-openai requests pandas numpy matplotlib
content_copy
download
Use code with caution.
Markdown
## Project Structure

advanced_strategy.py: MeanReversionStrategy class, backtesting, visualization, and LangChain tools.

algo_trading_toolkit.py: AlgoTradingStrategy base class, MACrossoverStrategy, backtesting, optimization, and comparison tools.

example.py: Usage examples (direct and with LangChain agent).

mean_reversion_metrics.py: Core calculations for mean reversion indicators (Z-score, RSI, Bollinger Bands).

README.md: This documentation.

test_mean_reversion.py: Test functions.

core/api.py: TokenPriceAPI for fetching cryptocurrency price data.
core/indicators.py: MeanReversionIndicators and other technical indicators.
tools/langchain_tools.py: LangChain tool implementations.

Usage
### Basic Usage
from ETHDenver2025.Mean_Reversion.tools.langchain_tools import get_token_price, mean_reversion_analyzer
from ETHDenver2025.Mean_Reversion.advanced_strategy import get_token_mean_reversion_signal
from ETHDenver2025.Mean_Reversion.algo_trading_toolkit import get_ma_crossover_signal, compare_trading_strategies

# Get current price
price = get_token_price.invoke({"token_id": "bitcoin"})
print(f"Current price of Bitcoin: ${price}")

# Get other info/signals...
content_copy
download
Use code with caution.
Python
### Using Mean Reversion Metrics Directly

The `core/indicators.py` file provides a `MeanReversionIndicators` class with static methods for calculating key technical indicators used in mean reversion strategies:

```python
from core.indicators import MeanReversionIndicators
from core.api import TokenPriceAPI

# Initialize API client (can choose CoinGecko or DeFi Llama)
api = TokenPriceAPI(api_provider="coingecko")  # or "defillama"

# Fetch historical price data
prices, dates = api.get_historical_prices("bitcoin", days=30)

# Create indicator instance
indicators = MeanReversionIndicators()

# Calculate Z-score
z_score = indicators.calculate_z_score(prices, window=14)
print(f"Bitcoin Z-score: {z_score:.2f}")

# Calculate RSI
rsi = indicators.calculate_rsi(prices, window=14)
print(f"Bitcoin RSI: {rsi:.2f}")

# Calculate Bollinger Bands
bb_data = indicators.calculate_bollinger_bands(prices, window=20, num_std=2.0)
print(f"Middle Band: ${bb_data['middle_band']:.2f}")
print(f"Upper Band: ${bb_data['upper_band']:.2f}")
print(f"Lower Band: ${bb_data['lower_band']:.2f}")
print(f"Percent B: {bb_data['percent_b']:.2f}")

# Use DeFi Llama API instead
api_dl = TokenPriceAPI(api_provider="defillama")
prices_dl, dates_dl = api_dl.get_historical_prices("bitcoin", days=10)
```

Available methods:
- `calculate_z_score(prices, window)`: Calculates the Z-score (standard deviations from mean)
- `calculate_rsi(prices, window)`: Calculates the Relative Strength Index
- `calculate_bollinger_bands(prices, window, num_std)`: Calculates Bollinger Bands and returns a dictionary with bands, current price, and percent B

### LangChain Agent Integration
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.render import format_tool_to_openai_function
from langchain.schema import SystemMessage

# ... (import tools) ...

tools = [
    get_token_price,
    get_token_mean_reversion_signal,
    # ... other tools ...
]

functions = [format_tool_to_openai_function(t) for t in tools]

system_message = SystemMessage(content="You are a crypto trading assistant...")

llm = ChatOpenAI(model="gpt-4", temperature=0, functions=functions)
agent = create_tool_calling_agent(llm, tools, system_message)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = agent_executor.invoke({"input": "Analyze Ethereum..."})
print(result["output"])
content_copy
download
Use code with caution.
Python
## Advanced Features

Backtesting: backtest_mean_reversion_strategy, backtest_ma_crossover_strategy

Parameter Optimization: get_optimal_strategy_parameters

Visualization: MeanReversionStrategy.plot_backtest_results() and example using get_token_bollinger_bands artifact.

Custom Strategies: Subclass AlgoTradingStrategy.

API Customization: Modify TokenPriceAPI for different data sources.

# Available Tools
Basic Price Tools

get_token_price: Current price (supports CoinGecko or DeFi Llama).

get_token_z_score: Z-score (supports CoinGecko or DeFi Llama).

get_token_rsi: RSI (supports CoinGecko or DeFi Llama).

get_token_bollinger_bands: Bollinger Bands (with artifact, supports CoinGecko or DeFi Llama).

mean_reversion_analyzer: Comprehensive mean reversion analysis (supports CoinGecko or DeFi Llama).

OHLC Tools

get_ohlc_data: Fetch OHLC (Open, High, Low, Close) candle data from CoinAPI.

get_ohlc_indicators: Calculate comprehensive technical indicators from OHLC data, including ATR and MACD.

Advanced Strategy Tools

get_token_mean_reversion_signal: Mean reversion signal (BUY/SELL/HOLD).

backtest_mean_reversion_strategy: Backtests mean reversion (with artifact).

# Algorithmic Trading Toolkit

get_ma_crossover_signal: MA crossover signal.

backtest_ma_crossover_strategy: Backtests MA crossover (with artifact).

compare_trading_strategies: Compares multiple strategies.

get_optimal_strategy_parameters: Finds optimal parameters.

# Limitations

Uses public APIs (DeFi Llama, CoinGecko, and CoinAPI) which are rate-limited.

Historical data doesn't guarantee future results.

No real-time updates.

Backtesting doesn't include slippage, fees, or liquidity.

DeFi Llama historical price data requires one API call per day, which can be slower for long time periods.

CoinAPI has strict rate limits (250 requests per day on the free plan), so use carefully.

OHLC data is limited to certain token pairs available on CoinAPI.

# Testing

Run test_mean_reversion.py to test the mean reversion tools. Includes delays to avoid rate limits.

License

MIT License

# File Documentation (Brief)

advanced_strategy.py: MeanReversionStrategy class and related LangChain tools.

algo_trading_toolkit.py: AlgoTradingStrategy base class, MACrossoverStrategy, and related tools.

example.py: Demonstrates usage.

mean_reversion_metrics.py: Core calculations for Z-score, RSI, and Bollinger Bands metrics.

test_mean_reversion.py: Test functions.

core/api.py: TokenPriceAPI for fetching cryptocurrency price data.
core/indicators.py: MeanReversionIndicators and other technical indicators.
tools/langchain_tools.py: LangChain tool implementations.

content_copy
download
Use code with caution.

## Enhanced Technical Indicators with Advanced LangChain Features

This module extends the Crypto Trading Strategy Tools project with improved features from the LangChain framework, making the tools more robust, informative, and flexible for both users and agents.

### Features Added

The enhanced tools leverage several advanced LangChain features:

#### 1. Enhanced Error Handling

All tools now implement proper error handling using `ToolException` and the `handle_tool_error` parameter:

```python
@tool(handle_tool_error=True)
def get_token_indicators(token_id: str, window: int = 10) -> str:
    """Get comprehensive technical indicators for a cryptocurrency token."""
    # ...
```

This allows tools to gracefully handle common errors like:
- Invalid token IDs
- API rate limiting
- Insufficient data points

Instead of crashing, tools can return helpful fallback messages or explanations.

#### 2. Content and Artifact Responses

Some tools now implement the `response_format="content_and_artifact"` pattern, which allows them to return both:
- Human-readable analysis text (for the model/user)
- Structured data (for downstream processing)

```python
@tool(response_format="content_and_artifact", handle_tool_error=True)
def get_advanced_indicators(token_id: str, window: int = 10) -> Tuple[str, Dict[str, Any]]:
    """Get technical indicators with both human-readable analysis and structured data."""
    # ...
    return message, indicators
```

This provides flexibility for using the tools in different contexts - whether generating reports for humans or processing data for algorithms.

#### 3. Improved Parameter Schemas with Pydantic

All parameters now have detailed schema definitions using Pydantic models with field descriptions:

```python
class IndicatorParams(BaseModel):
    """Parameters for technical indicator calculations."""
    token_id: str = Field(description="The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')")
    window: int = Field(default=10, description="The lookback window for indicator calculations (in days)")
    num_std: float = Field(default=2.0, description="Number of standard deviations for Bollinger Bands")
```

This provides better documentation and validation for parameters, improving both accuracy and user experience.

### New Tools

The enhanced module includes these new LangChain tools:

1. **`get_token_indicators`**: Comprehensive technical analysis with graceful error handling
2. **`get_advanced_indicators`**: Analysis with both text and structured data artifacts
3. **`get_historical_indicators`**: Time-series analysis with custom error messages

### IndicatorService Class

The core functionality is provided by the `IndicatorService` class, which handles:
- API requests with retry logic
- Technical indicator calculations
- Data processing and formatting
- Error handling and propagation

### Usage Examples

#### Basic Usage

```python
from technical_indicators import get_token_indicators

# Get a comprehensive analysis of Bitcoin indicators
analysis = get_token_indicators("bitcoin")
print(analysis)
```

#### Working with Content and Artifacts

```python
from technical_indicators import get_advanced_indicators

# Get both analysis text and structured data
message, data = get_advanced_indicators("ethereum")

# Use the message for display
print(message)

# Use the structured data for computation or visualization
print(f"Current price: ${data['current_price']}")
print(f"Z-Score: {data['indicators']['z_score']['value']}")
```

#### Error Handling

```python
from technical_indicators import get_historical_indicators

# This will return a helpful error message instead of crashing
result = get_historical_indicators("bitcoin", days=3, window=100)
print(result)  # "Data not available or insufficient price history. Try a different token or time window."
```

### Demo Scripts

Two demo scripts demonstrate the new functionality:

1. **`test_indicators.py`**: Demonstrates all features with visualizations
2. **`example.py`**: Integrates the tools with a LangChain agent and shows direct usage

### Integration with LangChain Agents

The tools are designed to work seamlessly with LangChain agents:

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from technical_indicators import get_token_indicators, get_advanced_indicators

# Define the tools to use
tools = [get_token_indicators, get_advanced_indicators]

# Create the agent
agent = create_tool_calling_agent(llm, tools, system_message)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Use the agent
result = agent_executor.invoke({"input": "What are the technical indicators for Ethereum?"})
```

### Benefits

These enhancements provide several key benefits:

1. **Improved Robustness**: Better error handling means fewer crashes and more informative fallbacks
2. **Greater Flexibility**: Content and artifact responses enable both human and machine consumption
3. **Better Documentation**: Detailed parameter schemas improve discoverability and usability
4. **Enhanced Integration**: Cleaner integration with LangChain agents and agentic workflows

By implementing these enhanced features from the LangChain documentation, the tools are now more powerful, user-friendly, and ready for production use.
