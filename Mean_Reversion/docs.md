# Crypto Trading Strategy Tools for LangChain - Documentation

This project provides a set of tools for building, backtesting, and analyzing cryptocurrency trading strategies, specifically designed for integration with LangChain. It offers functionality for fetching price data, calculating technical indicators, implementing trading strategies (Mean Reversion and Moving Average Crossover), and performing backtesting and optimization.

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Features](#features)
3.  [Requirements](#requirements)
4.  [Installation](#installation)
5.  [Project Structure](#project-structure)
6.  [Usage](#usage)
    *   [Basic Usage](#basic-usage)
    *   [LangChain Agent Integration](#langchain-agent-integration)
    *   [Advanced Features](#advanced-features)
        *   [Backtesting](#backtesting)
        *   [Parameter Optimization](#parameter-optimization)
        *   [Visualization](#visualization)
    *   [Custom Strategies](#custom-strategies)
    *  [API Customization](#api-customization)
7.  [Available Tools](#available-tools)
    *   [Basic Price Tools](#basic-price-tools)
    *   [Advanced Strategy Tools](#advanced-strategy-tools)
    *   [Algorithmic Trading Toolkit](#algorithmic-trading-toolkit)
8.  [Limitations](#limitations)
9.  [Future Enhancements](#future-enhancements)
10. [Testing](#testing)
11. [License](#license)
12. [File Documentation](#file-documentation)
    * [advanced_strategy.py](#advanced_strategy.py)
    * [algo_trading_toolkit.py](#algo_trading_toolkit.py)
    * [example.py](#example.py)
    * [README.md](#readme.md)
    * [test_mean_reversion.py](#test_mean_reversion.py)
    * [token_price_tool.py](#token_price_tool.py)

## 1. Project Overview <a name="project-overview"></a>

This project aims to provide a robust and extensible toolkit for cryptocurrency trading strategy development within the LangChain ecosystem. It leverages popular libraries like `pandas`, `numpy`, and `matplotlib` for data manipulation, analysis, and visualization, and integrates seamlessly with LangChain's tool and agent frameworks. The primary focus is on mean reversion and moving average crossover strategies, but the architecture allows for easy addition of custom strategies.

## 2. Features <a name="features"></a>

*   **Data Retrieval:** Fetches current and historical cryptocurrency price data from the CoinGecko API.
*   **Technical Indicators:** Calculates essential indicators like Z-score, RSI, Bollinger Bands, and Moving Averages.
*   **Trading Strategies:** Implements Mean Reversion and Moving Average Crossover strategies.
*   **Backtesting:** Evaluates strategy performance on historical data, providing metrics like total return, buy-and-hold return, and the number of trades.
*   **Optimization:** Offers tools to find optimal strategy parameters through parameter sweeping.
*   **Visualization:** Generates plots to visualize backtest results and indicator values.
*   **LangChain Integration:** Designed as LangChain tools, making them easily usable within LangChain agents and applications. Includes support for OpenAI function calling.
*  **Artifact Return:** Some tools return both a human-readable message and a structured data artifact, useful for downstream processing or visualization.

## 3. Requirements <a name="requirements"></a>

*   Python 3.8+
*   Libraries:
    *   `langchain-core`
    *   `langchain-openai` (for example usage and agent integration)
    *   `requests`
    *   `pandas`
    *   `numpy`
    *   `matplotlib`

## 4. Installation <a name="installation"></a>


pip install langchain-core langchain-openai requests pandas numpy matplotlib
content_copy
download
Use code with caution.
Markdown
5. Project Structure <a name="project-structure"></a>

The project is organized into the following files:

advanced_strategy.py: Contains the MeanReversionStrategy class, including backtesting and visualization methods, and LangChain tools for getting trading signals and backtesting.

algo_trading_toolkit.py: Provides a base class AlgoTradingStrategy and the MACrossoverStrategy implementation, along with backtesting, visualization, strategy comparison, and parameter optimization tools.

example.py: Demonstrates how to use the tools with a LangChain agent and directly.

README.md: This documentation file.

test_mean_reversion.py: Includes test functions for the mean reversion tools, including basic metrics, trading signals, Bollinger Bands, and backtesting.

token_price_tool.py: Defines the TokenPriceAPI for fetching price data and the MeanReversionCalculator for calculating indicators, along with basic LangChain tools for price, Z-score, RSI, and Bollinger Bands.

6. Usage <a name="usage"></a>
6.1 Basic Usage <a name="basic-usage"></a>
from token_price_tool import get_token_price, mean_reversion_analyzer
from advanced_strategy import get_token_mean_reversion_signal
from algo_trading_toolkit import get_ma_crossover_signal, compare_trading_strategies

# Get current price
price = get_token_price.invoke({"token_id": "bitcoin"})
print(f"Current price of Bitcoin: ${price}")

# Get mean reversion analysis
analysis = mean_reversion_analyzer.invoke({"token_id": "ethereum"})
print(analysis)

# Get mean reversion trading signal
signal = get_token_mean_reversion_signal.invoke({"token_id": "ethereum"})
print(signal)

# Get MA crossover signal
ma_signal = get_ma_crossover_signal.invoke({
    "token_id": "solana",
    "fast_period": 10,
    "slow_period": 50
})
print(ma_signal)

# Compare strategies
comparison = compare_trading_strategies.invoke({
    "token_id": "bitcoin",
    "days": 365,
    "initial_capital": 10000.0
})
print(comparison)
content_copy
download
Use code with caution.
Python
6.2 LangChain Agent Integration <a name="langchain-agent-integration"></a>
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.render import format_tool_to_openai_function
from langchain.schema import SystemMessage

from token_price_tool import get_token_price, get_token_z_score, get_token_rsi, mean_reversion_analyzer
from advanced_strategy import get_token_mean_reversion_signal, backtest_mean_reversion_strategy
from algo_trading_toolkit import get_ma_crossover_signal, compare_trading_strategies

# Define tools
tools = [
    get_token_price,
    get_token_mean_reversion_signal,
    get_ma_crossover_signal,
    compare_trading_strategies,
    backtest_mean_reversion_strategy
]

# Format tools for OpenAI function calling
functions = [format_tool_to_openai_function(t) for t in tools]

# System message
system_message = SystemMessage(
    content="""You are a crypto trading assistant.
    You have access to tools that can analyze cryptocurrency prices and provide trading signals.
    Use these tools to help users make informed trading decisions.
    Always remind users that your analysis is for informational purposes only and not financial advice."""
)

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    functions=functions
)

# Create agent
agent = create_tool_calling_agent(llm, tools, system_message)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run agent
result = agent_executor.invoke({
    "input": "What's the current trend for Ethereum? Should I consider buying or selling?"
})
print(result["output"])
content_copy
download
Use code with caution.
Python
6.3 Advanced Features <a name="advanced-features"></a>
6.3.1 Backtesting <a name="backtesting"></a>
from advanced_strategy import backtest_mean_reversion_strategy
from algo_trading_toolkit import backtest_ma_crossover_strategy

# Backtest mean reversion
message, artifact = backtest_mean_reversion_strategy.invoke({
    "token_id": "bitcoin",
    "days": 365,
    "initial_capital": 10000.0
})
print(message)

# Backtest MA crossover
message, artifact = backtest_ma_crossover_strategy.invoke({
    "token_id": "ethereum",
    "fast_period": 10,
    "slow_period": 50,
    "days": 365,
    "initial_capital": 10000.0
})
print(message)
content_copy
download
Use code with caution.
Python
6.3.2 Parameter Optimization <a name="parameter-optimization"></a>
from algo_trading_toolkit import get_optimal_strategy_parameters

# Optimal parameters for MA Crossover
optimal_ma = get_optimal_strategy_parameters.invoke({
    "token_id": "bitcoin",
    "strategy_type": "ma_crossover",
    "days": 365
})
print(optimal_ma)

# Optimal parameters for Mean Reversion
optimal_mr = get_optimal_strategy_parameters.invoke({
    "token_id": "ethereum",
    "strategy_type": "mean_reversion",
    "days": 365
})
print(optimal_mr)
content_copy
download
Use code with caution.
Python
6.3.3 Visualization <a name="visualization"></a>
from advanced_strategy import backtest_mean_reversion_strategy, MeanReversionStrategy
import matplotlib.pyplot as plt

# Backtest and get artifact
message, artifact = backtest_mean_reversion_strategy.invoke({
    "token_id": "bitcoin",
    "days": 365,
    "initial_capital": 10000.0
})

# Visualize using the artifact
results = artifact["results"]
token_id = artifact["token_id"]

# Create custom visualization using the strategy class
strategy = MeanReversionStrategy()
strategy.plot_backtest_results(results, save_path=f"{token_id}_backtest.png")

# Example using Bollinger Bands artifact (from test_mean_reversion.py)
from token_price_tool import get_token_bollinger_bands
message, artifact = get_token_bollinger_bands.invoke({"token_id": "bitcoin"})
plt.figure(figsize=(12, 6))
plt.plot(artifact['dates'][-30:], artifact['prices'][-30:], label='Price')
bb_data = artifact['data']
plt.axhline(y=bb_data["upper_band"], color='r', linestyle='--', label='Upper Band')
plt.axhline(y=bb_data["middle_band"], color='g', linestyle='-', label='Middle Band')
plt.axhline(y=bb_data["lower_band"], color='b', linestyle='--', label='Lower Band')
plt.title(f'Bitcoin with Bollinger Bands (Last 30 Days)')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("bitcoin_bollinger_bands.png")
plt.show()  # Add this line to display the plot
content_copy
download
Use code with caution.
Python
6.4 Custom Strategies <a name="custom-strategies"></a>

You can create custom strategies by subclassing AlgoTradingStrategy:

from algo_trading_toolkit import AlgoTradingStrategy

class MyCustomStrategy(AlgoTradingStrategy):
    def __init__(self, param1=10, param2=20):
        super().__init__(name="My Custom Strategy")
        self.param1 = param1
        self.param2 = param2

    def calculate_signals(self, df):
        # Implement your signal calculation logic here
        return df

    def backtest(self, token_id, days=365, initial_capital=10000.0):
        # Implement your backtesting logic here
        return {} # Return results dictionary
content_copy
download
Use code with caution.
Python
6.5 API Customization <a name="api-customization"></a>
from token_price_tool import TokenPriceAPI

# Customize API with your own key
api = TokenPriceAPI(api_key="your_api_key_here")

# Change the base URL for a different provider
api.base_url = "https://your-api-provider.com/api/v1"
content_copy
download
Use code with caution.
Python
7. Available Tools <a name="available-tools"></a>
7.1 Basic Price Tools <a name="basic-price-tools"></a>

get_token_price(token_id: str) -> float: Gets the current price.

get_token_z_score(token_id: str, window: int = 20) -> float: Calculates the Z-score.

get_token_rsi(token_id: str, window: int = 14) -> float: Calculates the RSI.

get_token_bollinger_bands(token_id: str, window: int = 20, num_std: float = 2.0) -> Tuple[str, Dict[str, Any]]: Calculates Bollinger Bands (returns analysis and artifact).

mean_reversion_analyzer(token_id: str) -> str: Provides a comprehensive mean reversion analysis.

7.2 Advanced Strategy Tools <a name="advanced-strategy-tools"></a>

get_token_mean_reversion_signal(token_id: str) -> str: Generates a BUY/SELL/HOLD signal based on mean reversion.

backtest_mean_reversion_strategy(token_id: str, days: int = 365, initial_capital: float = 10000.0) -> Tuple[str, Dict[str, Any]]: Backtests the mean reversion strategy (returns analysis and artifact).

7.3 Algorithmic Trading Toolkit <a name="algorithmic-trading-toolkit"></a>

get_ma_crossover_signal(token_id: str, fast_period: int = 10, slow_period: int = 50) -> str: Generates a signal based on Moving Average Crossover.

backtest_ma_crossover_strategy(token_id: str, fast_period: int = 10, slow_period: int = 50, days: int = 365, initial_capital: float = 10000.0) -> Tuple[str, Dict[str, Any]]: Backtests the MA Crossover strategy (returns analysis and artifact).

compare_trading_strategies(token_id: str, days: int = 365, initial_capital: float = 10000.0) -> str: Compares multiple strategies.

get_optimal_strategy_parameters(token_id: str, strategy_type: str = "ma_crossover", days: int = 365, initial_capital: float = 10000.0) -> str: Finds optimal parameters for a given strategy.

8. Limitations <a name="limitations"></a>

Relies on CoinGecko's public API, which has rate limits.

Technical analysis is based on historical data and does not guarantee future results.

Data is fetched at the time of invocation; no real-time updates.

Backtesting does not account for slippage, fees, or liquidity.

9. Future Enhancements <a name="future-enhancements"></a>

Support for more technical indicators.

Integration with additional data providers.

Portfolio optimization tools.

Risk management strategies.

Sentiment analysis integration.

10. Testing <a name="testing"></a>

The test_mean_reversion.py file contains several test functions to validate the core functionality of the mean reversion tools. These tests cover:

Basic Metrics: test_basic_metrics() checks get_token_price, get_token_z_score, and get_token_rsi for multiple tokens.

Mean Reversion Score: test_mean_reversion_score() tests the mean_reversion_analyzer and get_token_mean_reversion_signal tools, collecting results in a summary table.

Bollinger Bands Artifact: test_bollinger_bands_artifact() verifies the get_token_bollinger_bands tool, including its artifact output and the generation of a simple plot.

Backtesting: test_backtest_strategy() tests the backtest_mean_reversion_strategy tool, including both the message and artifact outputs, and generates a backtest visualization.

The tests include delays (time.sleep()) to avoid hitting API rate limits. The testing script can be run directly:

python test_mean_reversion.py
content_copy
download
Use code with caution.
Bash
11. License <a name="license"></a>

MIT License

12. File Documentation <a name="file-documentation"></a>
advanced_strategy.py <a name="advanced_strategy.py"></a>

This file implements the MeanReversionStrategy class and provides LangChain tools for utilizing it.

Classes:

MeanReversionStrategy:

__init__(self, lookback_period: int = 20, z_threshold: float = 2.0, rsi_overbought: int = 70, rsi_oversold: int = 30): Initializes the strategy with parameters.

calculate_metrics(self, token_id: str, days: int = 60) -> Dict[str, Any]: Calculates Z-score, RSI, Bollinger Bands, and generates trading signals. Returns a dictionary containing a Pandas DataFrame and individual metrics.

backtest_strategy(self, token_id: str, days: int = 365, initial_capital: float = 10000.0) -> Dict[str, Any]: Backtests the strategy, simulating trades based on historical data. Returns a dictionary with the backtest DataFrame, performance metrics, and trade statistics.

plot_backtest_results(self, backtest_results: Dict[str, Any], save_path: Optional[str] = None) -> None: Visualizes the backtest results, including price, moving average, Bollinger Bands, Z-score, RSI, and portfolio value. Can save the plot to a file.

LangChain Tools:

get_token_mean_reversion_signal(token_id: str) -> str: Generates a BUY, SELL, or HOLD signal based on the mean reversion strategy, along with a detailed explanation.

backtest_mean_reversion_strategy(token_id: str, days: int = 365, initial_capital: float = 10000.0) -> Tuple[str, Dict[str, Any]]: Runs a backtest and returns a formatted analysis message and a data artifact containing the detailed results.

algo_trading_toolkit.py <a name="algo_trading_toolkit.py"></a>

This file defines a base class for algorithmic trading strategies and implements the Moving Average Crossover strategy.

Classes:

AlgoTradingStrategy:

__init__(self, name: str): Initializes the strategy with a name.

get_historical_data(self, token_id: str, days: int = 60) -> pd.DataFrame: Fetches historical data and returns a Pandas DataFrame.

calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame: Abstract method; subclasses must implement this to calculate trading signals.

backtest(self, token_id: str, days: int = 365, initial_capital: float = 10000.0) -> Dict[str, Any]: Abstract method; subclasses must implement backtesting.

MACrossoverStrategy(AlgoTradingStrategy):

__init__(self, fast_period: int = 10, slow_period: int = 50): Initializes the strategy with fast and slow moving average periods.

calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame: Calculates MA crossover signals (BUY when fast MA crosses above slow MA, SELL when fast MA crosses below).

backtest(self, token_id: str, days: int = 365, initial_capital: float = 10000.0) -> Dict[str, Any]: Backtests the MA crossover strategy.

plot_backtest_results(self, results: Dict[str, Any], save_path: Optional[str] = None) -> None: Plots backtest results.

LangChain Tools:

get_ma_crossover_signal(token_id: str, fast_period: int = 10, slow_period: int = 50) -> str: Generates a BUY, SELL, or HOLD signal based on MA crossover.

backtest_ma_crossover_strategy(token_id: str, fast_period: int = 10, slow_period: int = 50, days: int = 365, initial_capital: float = 10000.0) -> Tuple[str, Dict[str, Any]]: Backtests the MA crossover strategy and returns an analysis message and a data artifact.

compare_trading_strategies(token_id: str, days: int = 365, initial_capital: float = 10000.0) -> str: Compares Mean Reversion, two MA Crossover strategies (short-term and medium-term), and Buy & Hold.

get_optimal_strategy_parameters(token_id: str, strategy_type: str = "ma_crossover", days: int = 365, initial_capital: float = 10000.0) -> str: Finds optimal parameters for either MA Crossover or Mean Reversion through parameter sweeping.

example.py <a name="example.py"></a>

This file provides example usage of the tools, both directly and within a LangChain agent.

Functions:

main(): Sets up a LangChain agent with the available tools and provides an interactive command-line interface for users to ask questions.

demo_direct_tool_usage(): Demonstrates how to use the tools directly (without an agent) to fetch data, calculate indicators, and perform analysis.

README.md <a name="readme.md"></a>

The README file provides a high-level overview of the project, including features, requirements, installation instructions, basic usage examples, LangChain integration instructions, advanced features, available tools, limitations, and future enhancements. This current document is an expanded version of the README.

test_mean_reversion.py <a name="test_mean_reversion.py"></a>

This file contains test functions to verify the functionality of the mean reversion tools. See the Testing section above for details.

token_price_tool.py <a name="token_price_tool.py"></a>

This file provides the core functionality for fetching token price data and calculating mean reversion metrics.

Classes:

TokenPriceAPI:

__init__(self, api_key: Optional[str] = None): Initializes the API wrapper.

get_price(self, token_id: str) -> float: Gets the current price of a token.

get_historical_prices(self, token_id: str, days: int = 30) -> List[Dict]: Gets historical price data.

MeanReversionCalculator:

calculate_z_score(prices: List[float], window: int = 20) -> float: Calculates the Z-score.

calculate_rsi(prices: List[float], window: int = 14) -> float: Calculates the RSI.

calculate_bollinger_bands(prices: List[float], window: int = 20, num_std: float = 2.0) -> Dict[str, float]: Calculates Bollinger Bands.

LangChain Tools:

get_token_price(token_id: str) -> float: Gets the current price.

get_token_z_score(token_id: str, window: int = 20) -> float: Calculates the Z-score.

get_token_rsi(token_id: str, window: int = 14) -> float: Calculates the RSI.

get_token_bollinger_bands(token_id: str, window: int = 20, num_std: float = 2.0) -> Tuple[str, Dict[str, Any]]: Calculates Bollinger Bands and returns an analysis message and a data artifact.

mean_reversion_analyzer(token_id: str) -> str: Provides a comprehensive mean reversion analysis by combining Z-score, RSI, and Bollinger Bands.

content_copy
download
Use code with caution.