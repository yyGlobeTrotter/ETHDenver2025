# Crypto Trading Strategy Tools for LangChain

This project provides tools for building, backtesting, and analyzing cryptocurrency trading strategies, integrated with LangChain.  It focuses on Mean Reversion and Moving Average Crossover strategies, but is easily extensible.

## Features

*   **Data Retrieval:** Fetches current/historical prices from CoinGecko.
*   **Technical Indicators:** Z-score, RSI, Bollinger Bands, Moving Averages.
*   **Trading Strategies:** Mean Reversion, Moving Average Crossover.
*   **Backtesting:** Evaluates performance on historical data.
*   **Optimization:** Finds optimal strategy parameters.
*   **Visualization:** Plots backtest results.
*   **LangChain Integration:**  Ready to use with LangChain agents and OpenAI function calling.
*   **Artifact Return:**  Provides structured data artifacts for further processing.

## Requirements

*   Python 3.8+
*   `langchain-core`, `langchain-openai`, `requests`, `pandas`, `numpy`, `matplotlib`

## Installation


pip install langchain-core langchain-openai requests pandas numpy matplotlib
content_copy
download
Use code with caution.
Markdown
Project Structure

advanced_strategy.py: MeanReversionStrategy class, backtesting, visualization, and LangChain tools.

algo_trading_toolkit.py: AlgoTradingStrategy base class, MACrossoverStrategy, backtesting, optimization, and comparison tools.

example.py: Usage examples (direct and with LangChain agent).

README.md: This documentation.

test_mean_reversion.py: Test functions.

token_price_tool.py: TokenPriceAPI, MeanReversionCalculator, and basic LangChain tools.

Usage
Basic Usage
from token_price_tool import get_token_price, mean_reversion_analyzer
from advanced_strategy import get_token_mean_reversion_signal
from algo_trading_toolkit import get_ma_crossover_signal, compare_trading_strategies

# Get current price
price = get_token_price.invoke({"token_id": "bitcoin"})
print(f"Current price of Bitcoin: ${price}")

# Get other info/signals...
content_copy
download
Use code with caution.
Python
LangChain Agent Integration
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
Advanced Features

Backtesting: backtest_mean_reversion_strategy, backtest_ma_crossover_strategy

Parameter Optimization: get_optimal_strategy_parameters

Visualization: MeanReversionStrategy.plot_backtest_results() and example using get_token_bollinger_bands artifact.

Custom Strategies: Subclass AlgoTradingStrategy.

API Customization: Modify TokenPriceAPI for different data sources.

# Available Tools
Basic Price Tools

get_token_price: Current price.

get_token_z_score: Z-score.

get_token_rsi: RSI.

get_token_bollinger_bands: Bollinger Bands (with artifact).

mean_reversion_analyzer: Comprehensive mean reversion analysis.

Advanced Strategy Tools

get_token_mean_reversion_signal: Mean reversion signal (BUY/SELL/HOLD).

backtest_mean_reversion_strategy: Backtests mean reversion (with artifact).

# Algorithmic Trading Toolkit

get_ma_crossover_signal: MA crossover signal.

backtest_ma_crossover_strategy: Backtests MA crossover (with artifact).

compare_trading_strategies: Compares multiple strategies.

get_optimal_strategy_parameters: Finds optimal parameters.

# Limitations

Uses CoinGecko's public API (rate-limited).

Historical data doesn't guarantee future results.

No real-time updates.

Backtesting doesn't include slippage, fees, or liquidity.

# Testing

Run test_mean_reversion.py to test the mean reversion tools. Includes delays to avoid rate limits.

License

MIT License

# File Documentation (Brief)

advanced_strategy.py: MeanReversionStrategy class and related LangChain tools.

algo_trading_toolkit.py: AlgoTradingStrategy base class, MACrossoverStrategy, and related tools.

example.py: Demonstrates usage.

test_mean_reversion.py: Test functions.

token_price_tool.py: TokenPriceAPI, MeanReversionCalculator, and basic tools.

content_copy
download
Use code with caution.
