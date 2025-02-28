# Crypto Trading Strategy Tools for LangChain

This project provides a comprehensive set of LangChain tools for crypto trading strategy development, backtesting, and analysis. The tools can be integrated into LangChain-based applications or agents to provide sophisticated financial analysis capabilities.

## Features

- **Data Retrieval**:
  - Fetch current and historical token prices from CoinGecko API
  - Support for multiple cryptocurrencies

- **Technical Indicators**:
  - Z-score (price deviation from moving average)
  - Relative Strength Index (RSI)
  - Bollinger Bands
  - Moving Averages

- **Trading Strategy Tools**:
  - Mean Reversion strategy
  - Moving Average Crossover strategy
  - Strategy parameter optimization
  - Strategy performance comparison

- **Backtesting**:
  - Historical performance evaluation
  - Comparison against buy-and-hold benchmark
  - Trading statistics and metrics
  - Visualization capabilities

- **LLM Integration**:
  - Full LangChain compatibility
  - Tool artifacts for downstream processing
  - Ready-to-use with OpenAI function calling

## Requirements

- Python 3.8+
- Required packages:
  - langchain-core
  - langchain-openai (for example usage)
  - requests
  - pandas
  - numpy
  - matplotlib

## Installation

```bash
pip install langchain-core langchain-openai requests pandas numpy matplotlib
```

## Project Structure

- `token_price_tool.py`: Core tools for fetching price data and basic indicators
- `advanced_strategy.py`: Implementation of mean reversion strategy and backtesting
- `algo_trading_toolkit.py`: Additional strategies and optimization tools
- `example.py`: Demo script showing how to use tools with LangChain
- `test_mean_reversion.py`: Script for testing the mean reversion tools

## Basic Usage

```python
from token_price_tool import get_token_price, mean_reversion_analyzer
from advanced_strategy import get_token_mean_reversion_signal
from algo_trading_toolkit import get_ma_crossover_signal, compare_trading_strategies

# Get current price of a token
price = get_token_price.invoke({"token_id": "bitcoin"})
print(f"Current price of Bitcoin: ${price}")

# Get mean reversion trading signal
signal = get_token_mean_reversion_signal.invoke({"token_id": "ethereum"})
print(signal)

# Get moving average crossover signal
ma_signal = get_ma_crossover_signal.invoke({
    "token_id": "solana", 
    "fast_period": 10, 
    "slow_period": 50
})
print(ma_signal)

# Compare different trading strategies
comparison = compare_trading_strategies.invoke({
    "token_id": "bitcoin",
    "days": 365,
    "initial_capital": 10000.0
})
print(comparison)
```

## Integration with LangChain Agents

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.render import format_tool_to_openai_function
from langchain.schema import SystemMessage

from token_price_tool import get_token_price, get_token_z_score, get_token_rsi, mean_reversion_analyzer
from advanced_strategy import get_token_mean_reversion_signal, backtest_mean_reversion_strategy
from algo_trading_toolkit import get_ma_crossover_signal, compare_trading_strategies

# Define the tools to use
tools = [
    get_token_price,
    get_token_mean_reversion_signal,
    get_ma_crossover_signal,
    compare_trading_strategies,
    backtest_mean_reversion_strategy
]

# Convert tools to functions for OpenAI function calling
functions = [format_tool_to_openai_function(t) for t in tools]

# Create system message
system_message = SystemMessage(
    content="""You are a crypto trading assistant. 
    You have access to tools that can analyze cryptocurrency prices and provide trading signals.
    Use these tools to help users make informed trading decisions based on technical analysis.
    Always remind users that your analysis is for informational purposes only and not financial advice."""
)

# Initialize the LLM with function calling capability
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    functions=functions
)

# Create the agent
agent = create_tool_calling_agent(llm, tools, system_message)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Use the agent
result = agent_executor.invoke({
    "input": "What's the current trend for Ethereum? Should I consider buying or selling?"
})
print(result["output"])
```

## Advanced Features

### Backtesting Trading Strategies

```python
from advanced_strategy import backtest_mean_reversion_strategy
from algo_trading_toolkit import backtest_ma_crossover_strategy

# Backtest mean reversion strategy
message, artifact = backtest_mean_reversion_strategy.invoke({
    "token_id": "bitcoin",
    "days": 365,
    "initial_capital": 10000.0
})
print(message)

# Backtest moving average crossover strategy
message, artifact = backtest_ma_crossover_strategy.invoke({
    "token_id": "ethereum",
    "fast_period": 10,
    "slow_period": 50,
    "days": 365,
    "initial_capital": 10000.0
})
print(message)
```

### Strategy Parameter Optimization

```python
from algo_trading_toolkit import get_optimal_strategy_parameters

# Find optimal parameters for MA Crossover strategy
optimal_ma = get_optimal_strategy_parameters.invoke({
    "token_id": "bitcoin",
    "strategy_type": "ma_crossover",
    "days": 365
})
print(optimal_ma)

# Find optimal parameters for Mean Reversion strategy
optimal_mr = get_optimal_strategy_parameters.invoke({
    "token_id": "ethereum",
    "strategy_type": "mean_reversion",
    "days": 365
})
print(optimal_mr)
```

### Using Artifacts for Visualization

```python
from advanced_strategy import backtest_mean_reversion_strategy
import matplotlib.pyplot as plt

# Get backtest results with artifact
message, artifact = backtest_mean_reversion_strategy.invoke({
    "token_id": "bitcoin",
    "days": 365,
    "initial_capital": 10000.0
})

# Create visualization using the returned artifact
results = artifact["results"]
token_id = artifact["token_id"]

# Create a custom visualization
strategy = MeanReversionStrategy()
strategy.plot_backtest_results(results, save_path=f"{token_id}_backtest.png")
```

## Available Tools

### Basic Price Tools
1. `get_token_price`: Fetches the current price of a cryptocurrency token
2. `get_token_z_score`: Calculates the Z-score for a token's price
3. `get_token_rsi`: Calculates the Relative Strength Index (RSI)
4. `get_token_bollinger_bands`: Calculates Bollinger Bands with artifact return
5. `mean_reversion_analyzer`: Provides comprehensive mean reversion analysis

### Advanced Strategy Tools
6. `get_token_mean_reversion_signal`: Generates a BUY/SELL/HOLD signal based on mean reversion
7. `backtest_mean_reversion_strategy`: Backtests a mean reversion strategy with artifact return

### Algorithmic Trading Toolkit
8. `get_ma_crossover_signal`: Generates a signal based on Moving Average Crossover
9. `backtest_ma_crossover_strategy`: Backtests a MA Crossover strategy
10. `compare_trading_strategies`: Compares multiple trading strategies on the same token
11. `get_optimal_strategy_parameters`: Finds optimal parameters for a given strategy

## Customization

You can extend the existing strategies or create new ones by subclassing the base classes:

```python
from algo_trading_toolkit import AlgoTradingStrategy

class MyCustomStrategy(AlgoTradingStrategy):
    """Implementation of a custom trading strategy."""
    
    def __init__(self, param1=10, param2=20):
        super().__init__(name="My Custom Strategy")
        self.param1 = param1
        self.param2 = param2
    
    def calculate_signals(self, df):
        # Your signal calculation logic here
        # ...
        return df
    
    def backtest(self, token_id, days=365, initial_capital=10000.0):
        # Your backtesting logic here
        # ...
        return results
```

## API Configuration

You can modify the API endpoints to use different data sources or add your own API key:

```python
from token_price_tool import TokenPriceAPI

# Example of customizing the API with your own key
api = TokenPriceAPI(api_key="your_api_key_here")

# You can also modify the base URL to use a different provider
api.base_url = "https://your-api-provider.com/api/v1"
```

## Limitations

- The default implementation uses CoinGecko's public API which has rate limits
- Technical analysis is based on historical data and should not be considered financial advice
- The tools fetch data at the time of invocation and do not provide real-time updates
- Backtesting results do not account for factors like slippage, fees, or liquidity

## Future Enhancements

- Support for additional technical indicators
- Integration with more crypto data providers
- Portfolio optimization tools
- Risk management strategies
- Sentiment analysis integration

## Environment Setup

This project requires an OpenAI API key for some functionality. Set up your environment variables:

1. Create a `.env` file in the project root with:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

2. Or set the environment variable directly:
   ```bash
   # On Linux/Mac
   export OPENAI_API_KEY=your_api_key_here
   
   # On Windows
   set OPENAI_API_KEY=your_api_key_here
   ```

**Important:** Never commit your API keys to version control.

## License

MIT