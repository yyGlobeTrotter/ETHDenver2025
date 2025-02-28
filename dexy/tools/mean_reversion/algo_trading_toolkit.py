"""
Algorithmic Trading Toolkit - LangChain Tools
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from langchain_core.tools import tool

from core.api import TokenPriceAPI
from tools.langchain_tools import (
    get_token_price,
    get_token_z_score,
    get_token_rsi,
)
from advanced_strategy import (
    MeanReversionCalculator,
    MeanReversionStrategy,
    get_token_mean_reversion_signal,
)


class AlgoTradingStrategy:
    """Base class for algorithmic trading strategies."""

    def __init__(self, name: str):
        self.name = name
        self.api = TokenPriceAPI()

    def get_historical_data(self, token_id: str, days: int = 60) -> pd.DataFrame:
        """Get historical price data and convert to DataFrame."""
        historical_data = self.api.get_historical_prices(token_id, days=days)
        timestamps = [price[0] for price in historical_data]
        prices = [price[1] for price in historical_data]
        dates = [
            datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d") for ts in timestamps
        ]

        df = pd.DataFrame({"date": dates, "timestamp": timestamps, "price": prices})
        return df

    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate trading signals. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement calculate_signals")

    def backtest(
        self, token_id: str, days: int = 365, initial_capital: float = 10000.0
    ) -> Dict[str, Any]:
        """Run backtest for the strategy."""
        raise NotImplementedError("Subclasses must implement backtest")


class MACrossoverStrategy(AlgoTradingStrategy):
    """Moving Average Crossover Strategy."""

    def __init__(self, fast_period: int = 10, slow_period: int = 50):
        super().__init__(name="MA Crossover")
        self.fast_period = fast_period
        self.slow_period = slow_period

    def calculate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MA crossover signals."""
        # Calculate moving averages
        df["fast_ma"] = df["price"].rolling(window=self.fast_period).mean()
        df["slow_ma"] = df["price"].rolling(window=self.slow_period).mean()

        # Calculate crossover signals
        df["ma_diff"] = df["fast_ma"] - df["slow_ma"]
        df["signal"] = 0
        df.loc[df["ma_diff"] > 0, "signal"] = 1  # Buy when fast MA > slow MA
        df.loc[df["ma_diff"] < 0, "signal"] = -1  # Sell when fast MA < slow MA

        # Generate entry/exit points
        df["position"] = df["signal"].shift(
            1
        )  # Position based on previous day's signal
        df["position"] = df["position"].fillna(0)

        return df

    def backtest(
        self, token_id: str, days: int = 365, initial_capital: float = 10000.0
    ) -> Dict[str, Any]:
        """Backtest the MA crossover strategy."""
        # Get historical data
        df = self.get_historical_data(token_id, days=days)

        # Calculate signals
        df = self.calculate_signals(df)

        # Initialize backtest variables
        df["capital"] = 0.0
        df["holdings"] = 0.0
        df["portfolio_value"] = 0.0

        # Set initial values
        df.loc[max(self.slow_period, self.fast_period), "capital"] = initial_capital

        # Run simulation
        for i in range(max(self.slow_period, self.fast_period) + 1, len(df)):
            prev_i = i - 1

            # Get position change
            position_change = df["position"].iloc[i] - df["position"].iloc[prev_i]

            # Copy values by default
            df.loc[df.index[i], "capital"] = df["capital"].iloc[prev_i]
            df.loc[df.index[i], "holdings"] = df["holdings"].iloc[prev_i]

            # Handle position changes
            if position_change > 0:  # Buy
                # Calculate shares to buy
                capital_to_spend = df["capital"].iloc[prev_i]
                new_holdings = capital_to_spend / df["price"].iloc[i]

                df.loc[df.index[i], "capital"] = 0
                df.loc[df.index[i], "holdings"] = new_holdings

            elif position_change < 0:  # Sell
                # Calculate proceeds from selling
                proceeds = df["holdings"].iloc[prev_i] * df["price"].iloc[i]

                df.loc[df.index[i], "capital"] = proceeds
                df.loc[df.index[i], "holdings"] = 0

            # Calculate portfolio value
            df.loc[df.index[i], "portfolio_value"] = (
                df["capital"].iloc[i] + df["holdings"].iloc[i] * df["price"].iloc[i]
            )

        # Calculate performance metrics
        start_idx = max(self.slow_period, self.fast_period)
        start_price = df["price"].iloc[start_idx]
        end_price = df["price"].iloc[-1]

        start_value = initial_capital
        end_value = df["portfolio_value"].iloc[-1]

        total_return = (end_value / start_value - 1) * 100
        buy_hold_return = (end_price / start_price - 1) * 100

        # Calculate trade statistics
        trades = df[df["position"].diff() != 0]
        num_trades = len(trades)

        return {
            "strategy": self.name,
            "dataframe": df,
            "total_return": total_return,
            "buy_hold_return": buy_hold_return,
            "num_trades": num_trades,
            "initial_capital": initial_capital,
            "ending_capital": end_value,
            "token_id": token_id,
            "params": {
                "fast_period": self.fast_period,
                "slow_period": self.slow_period,
            },
        }

    def plot_backtest_results(
        self, results: Dict[str, Any], save_path: Optional[str] = None
    ) -> None:
        """Plot backtest results."""
        df = results["dataframe"]
        token_id = results["token_id"]
        total_return = results["total_return"]
        buy_hold_return = results["buy_hold_return"]

        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

        # Plot price and moving averages
        ax1.plot(df["date"], df["price"], label="Price")
        ax1.plot(df["date"], df["fast_ma"], label=f"{self.fast_period}-period MA")
        ax1.plot(df["date"], df["slow_ma"], label=f"{self.slow_period}-period MA")

        # Mark buy and sell signals
        buy_signals = df[df["position"].diff() > 0]
        sell_signals = df[df["position"].diff() < 0]

        ax1.scatter(
            buy_signals["date"],
            buy_signals["price"],
            marker="^",
            color="g",
            s=100,
            label="Buy",
        )
        ax1.scatter(
            sell_signals["date"],
            sell_signals["price"],
            marker="v",
            color="r",
            s=100,
            label="Sell",
        )

        ax1.set_title(f"{token_id.upper()} - {self.name} Strategy")
        ax1.set_ylabel("Price (USD)")
        ax1.legend()
        ax1.grid(True)

        # Plot portfolio value
        ax2.plot(df["date"], df["portfolio_value"], label="Strategy")

        # Calculate buy-and-hold performance for comparison
        start_idx = max(self.slow_period, self.fast_period)
        initial_shares = results["initial_capital"] / df["price"].iloc[start_idx]
        df["buy_hold_value"] = initial_shares * df["price"]

        ax2.plot(df["date"], df["buy_hold_value"], label="Buy & Hold")
        ax2.set_title(
            f"Portfolio Performance (Strategy: {total_return:.2f}%, Buy & Hold: {buy_hold_return:.2f}%)"
        )
        ax2.set_ylabel("Portfolio Value (USD)")
        ax2.set_xlabel("Date")
        ax2.legend()
        ax2.grid(True)

        # Format x-axis
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        else:
            plt.show()


# LangChain Tools


@tool
def get_ma_crossover_signal(
    token_id: str, fast_period: int = 10, slow_period: int = 50
) -> str:
    """
    Get a trading signal based on Moving Average Crossover strategy.

    Args:
        token_id: The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')
        fast_period: Period for the fast moving average (default: 10)
        slow_period: Period for the slow moving average (default: 50)

    Returns:
        A trading signal: BUY, SELL, or HOLD with detailed analysis.
    """
    strategy = MACrossoverStrategy(fast_period=fast_period, slow_period=slow_period)
    df = strategy.get_historical_data(token_id, days=max(slow_period, fast_period) + 10)
    df = strategy.calculate_signals(df)

    # Get current signal
    current_price = df["price"].iloc[-1]
    current_fast_ma = df["fast_ma"].iloc[-1]
    current_slow_ma = df["slow_ma"].iloc[-1]
    current_signal = df["signal"].iloc[-1]

    # Prepare signal string
    if current_signal == 1:
        signal = "BUY"
        reason = (
            f"Fast MA ({current_fast_ma:.2f}) is ABOVE Slow MA ({current_slow_ma:.2f})"
        )
    elif current_signal == -1:
        signal = "SELL"
        reason = (
            f"Fast MA ({current_fast_ma:.2f}) is BELOW Slow MA ({current_slow_ma:.2f})"
        )
    else:
        signal = "HOLD"
        reason = f"No clear trend. Fast MA: {current_fast_ma:.2f}, Slow MA: {current_slow_ma:.2f}"

    return f"""
=== MA CROSSOVER SIGNAL FOR {token_id.upper()} ===
Current Price: ${current_price:.2f}
Signal: {signal}
Reason: {reason}

TECHNICAL INDICATORS:
- {fast_period}-period MA: ${current_fast_ma:.2f}
- {slow_period}-period MA: ${current_slow_ma:.2f}
- MA Difference: ${current_fast_ma - current_slow_ma:.2f}

NOTE: This is an algorithmic signal based solely on moving average crossover.
It should not be considered financial advice.
"""


@tool(response_format="content_and_artifact")
def backtest_ma_crossover_strategy(
    token_id: str,
    fast_period: int = 10,
    slow_period: int = 50,
    days: int = 365,
    initial_capital: float = 10000.0,
) -> Tuple[str, Dict[str, Any]]:
    """
    Backtest a Moving Average Crossover strategy on a token.

    Args:
        token_id: The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')
        fast_period: Period for the fast moving average (default: 10)
        slow_period: Period for the slow moving average (default: 50)
        days: Number of days to backtest (default: 365)
        initial_capital: Initial capital for the backtest in USD (default: 10000)

    Returns:
        Analysis of backtest results with performance metrics.
    """
    strategy = MACrossoverStrategy(fast_period=fast_period, slow_period=slow_period)

    try:
        # Run backtest
        results = strategy.backtest(
            token_id, days=days, initial_capital=initial_capital
        )

        # Format results message
        token_upper = token_id.upper()
        total_return = results["total_return"]
        buy_hold_return = results["buy_hold_return"]
        num_trades = results["num_trades"]
        ending_capital = results["ending_capital"]

        # Determine if strategy outperformed buy-and-hold
        performance = (
            "OUTPERFORMED" if total_return > buy_hold_return else "UNDERPERFORMED"
        )

        message = f"""
=== MA CROSSOVER STRATEGY BACKTEST FOR {token_upper} ===
Strategy Parameters:
- Fast MA Period: {fast_period}
- Slow MA Period: {slow_period}

Time Period: Last {days} days
Initial Capital: ${initial_capital:.2f}
Ending Capital: ${ending_capital:.2f}

PERFORMANCE:
- Strategy Return: {total_return:.2f}%
- Buy & Hold Return: {buy_hold_return:.2f}%
- Relative Performance: Strategy {performance} buy & hold by {abs(total_return - buy_hold_return):.2f}%
- Number of Trades: {num_trades}

ANALYSIS:
The MA Crossover strategy would have {"generated higher returns" if total_return > buy_hold_return else "underperformed"} 
compared to a simple buy-and-hold approach over this period.
"""

        # Return both the message and data artifact
        return message, {
            "token_id": token_id,
            "strategy": "MA Crossover",
            "results": results,
            "params": {"fast_period": fast_period, "slow_period": slow_period},
            "days": days,
            "initial_capital": initial_capital,
            "total_return": total_return,
            "buy_hold_return": buy_hold_return,
        }

    except Exception as e:
        return f"Error backtesting strategy for {token_id}: {str(e)}", {"error": str(e)}


@tool
def compare_trading_strategies(
    token_id: str, days: int = 365, initial_capital: float = 10000.0
) -> str:
    """
    Compare multiple trading strategies on the same token.

    Args:
        token_id: The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')
        days: Number of days to backtest (default: 365)
        initial_capital: Initial capital for each strategy in USD (default: 10000)

    Returns:
        Comparative analysis of different trading strategies.
    """
    try:
        # Strategy 1: Mean Reversion
        mean_rev_strategy = MeanReversionStrategy()
        mean_rev_results = mean_rev_strategy.backtest_strategy(
            token_id, days=days, initial_capital=initial_capital
        )

        # Strategy 2: MA Crossover (Short-term)
        ma_short_strategy = MACrossoverStrategy(fast_period=5, slow_period=20)
        ma_short_results = ma_short_strategy.backtest(
            token_id, days=days, initial_capital=initial_capital
        )

        # Strategy 3: MA Crossover (Medium-term)
        ma_medium_strategy = MACrossoverStrategy(fast_period=10, slow_period=50)
        ma_medium_results = ma_medium_strategy.backtest(
            token_id, days=days, initial_capital=initial_capital
        )

        # Strategy 4: Buy and Hold
        buy_hold_return = mean_rev_results["buy_hold_return"]
        buy_hold_ending = initial_capital * (1 + buy_hold_return / 100)

        # Compare results
        strategies = [
            {
                "name": "Mean Reversion",
                "return": mean_rev_results["total_return"],
                "ending_capital": mean_rev_results["ending_capital"],
                "num_trades": mean_rev_results["num_trades"],
            },
            {
                "name": "MA Crossover (5/20)",
                "return": ma_short_results["total_return"],
                "ending_capital": ma_short_results["ending_capital"],
                "num_trades": ma_short_results["num_trades"],
            },
            {
                "name": "MA Crossover (10/50)",
                "return": ma_medium_results["total_return"],
                "ending_capital": ma_medium_results["ending_capital"],
                "num_trades": ma_medium_results["num_trades"],
            },
            {
                "name": "Buy and Hold",
                "return": buy_hold_return,
                "ending_capital": buy_hold_ending,
                "num_trades": 1,
            },
        ]

        # Sort by performance
        strategies.sort(key=lambda x: x["return"], reverse=True)

        # Generate comparison table
        comparison = "\n".join(
            [
                f"{i + 1}. {s['name']:20} | Return: {s['return']:6.2f}% | "
                + f"Ending Capital: ${s['ending_capital']:9.2f} | Trades: {s['num_trades']}"
                for i, s in enumerate(strategies)
            ]
        )

        # Best strategy
        best_strategy = strategies[0]["name"]
        worst_strategy = strategies[-1]["name"]

        message = f"""
=== TRADING STRATEGY COMPARISON FOR {token_id.upper()} ===
Time Period: Last {days} days
Initial Capital: ${initial_capital:.2f}

PERFORMANCE RANKING:
{comparison}

ANALYSIS:
- Best performing strategy: {best_strategy} with {strategies[0]["return"]:.2f}% return
- Worst performing strategy: {worst_strategy} with {strategies[-1]["return"]:.2f}% return
- The best strategy would have yielded ${strategies[0]["ending_capital"] - initial_capital:.2f} more profit 
  than the worst strategy over this period.

RECOMMENDATION:
Based on historical performance over the last {days} days, the {best_strategy} strategy 
would have been most effective for trading {token_id.upper()}.

NOTE: Past performance does not guarantee future results. This analysis is for 
informational purposes only and should not be considered financial advice.
"""
        return message

    except Exception as e:
        return f"Error comparing strategies for {token_id}: {str(e)}"


@tool
def get_optimal_strategy_parameters(
    token_id: str,
    strategy_type: str = "ma_crossover",
    days: int = 365,
    initial_capital: float = 10000.0,
) -> str:
    """
    Find optimal parameters for a given trading strategy through parameter sweeping.

    Args:
        token_id: The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')
        strategy_type: Type of strategy to optimize ("ma_crossover" or "mean_reversion")
        days: Number of days to backtest (default: 365)
        initial_capital: Initial capital for the backtest in USD (default: 10000)

    Returns:
        Optimal parameters for the selected strategy based on historical data.
    """
    try:
        if strategy_type.lower() == "ma_crossover":
            # Parameter combinations to test
            fast_periods = [5, 10, 15, 20]
            slow_periods = [20, 30, 50, 100, 200]

            results = []

            # Test all combinations
            for fast in fast_periods:
                for slow in slow_periods:
                    if fast >= slow:
                        continue  # Skip invalid combinations

                    strategy = MACrossoverStrategy(fast_period=fast, slow_period=slow)
                    backtest = strategy.backtest(
                        token_id, days=days, initial_capital=initial_capital
                    )

                    results.append(
                        {
                            "fast_period": fast,
                            "slow_period": slow,
                            "return": backtest["total_return"],
                            "num_trades": backtest["num_trades"],
                        }
                    )

            # Sort by return
            results.sort(key=lambda x: x["return"], reverse=True)

            # Get top 3 combinations
            top_results = results[:3]
            top_table = "\n".join(
                [
                    f"{i + 1}. Fast MA: {r['fast_period']}, Slow MA: {r['slow_period']} | "
                    + f"Return: {r['return']:6.2f}% | Trades: {r['num_trades']}"
                    for i, r in enumerate(top_results)
                ]
            )

            # Get optimal parameters
            optimal = top_results[0]

            message = f"""
=== OPTIMAL MA CROSSOVER PARAMETERS FOR {token_id.upper()} ===
Time Period: Last {days} days
Initial Capital: ${initial_capital:.2f}

TOP PERFORMING PARAMETER COMBINATIONS:
{top_table}

OPTIMAL PARAMETERS:
- Fast MA Period: {optimal["fast_period"]}
- Slow MA Period: {optimal["slow_period"]}
- Expected Return: {optimal["return"]:.2f}%
- Number of Trades: {optimal["num_trades"]}

RECOMMENDATION:
For {token_id.upper()}, based on the last {days} days of historical data,
the optimal MA Crossover configuration uses a {optimal["fast_period"]}-period fast MA
and a {optimal["slow_period"]}-period slow MA.

NOTE: These results are based on historical backtesting and may not predict future performance.
"""
            return message

        elif strategy_type.lower() == "mean_reversion":
            # Parameter combinations to test
            lookback_periods = [10, 15, 20, 25, 30]
            z_thresholds = [1.0, 1.5, 2.0, 2.5, 3.0]

            results = []

            # Test all combinations
            for lookback in lookback_periods:
                for z_threshold in z_thresholds:
                    strategy = MeanReversionStrategy(
                        lookback_period=lookback, z_threshold=z_threshold
                    )
                    backtest = strategy.backtest_strategy(
                        token_id, days=days, initial_capital=initial_capital
                    )

                    results.append(
                        {
                            "lookback_period": lookback,
                            "z_threshold": z_threshold,
                            "return": backtest["total_return"],
                            "num_trades": backtest["num_trades"],
                        }
                    )

            # Sort by return
            results.sort(key=lambda x: x["return"], reverse=True)

            # Get top 3 combinations
            top_results = results[:3]
            top_table = "\n".join(
                [
                    f"{i + 1}. Lookback: {r['lookback_period']}, Z-threshold: {r['z_threshold']} | "
                    + f"Return: {r['return']:6.2f}% | Trades: {r['num_trades']}"
                    for i, r in enumerate(top_results)
                ]
            )

            # Get optimal parameters
            optimal = top_results[0]

            message = f"""
=== OPTIMAL MEAN REVERSION PARAMETERS FOR {token_id.upper()} ===
Time Period: Last {days} days
Initial Capital: ${initial_capital:.2f}

TOP PERFORMING PARAMETER COMBINATIONS:
{top_table}

OPTIMAL PARAMETERS:
- Lookback Period: {optimal["lookback_period"]}
- Z-score Threshold: {optimal["z_threshold"]}
- Expected Return: {optimal["return"]:.2f}%
- Number of Trades: {optimal["num_trades"]}

RECOMMENDATION:
For {token_id.upper()}, based on the last {days} days of historical data,
the optimal Mean Reversion configuration uses a {optimal["lookback_period"]}-day lookback period
and a Z-score threshold of {optimal["z_threshold"]}.

NOTE: These results are based on historical backtesting and may not predict future performance.
"""
            return message

        else:
            return f"Unsupported strategy type: {strategy_type}. Supported types are 'ma_crossover' and 'mean_reversion'."

    except Exception as e:
        return f"Error optimizing strategy parameters for {token_id}: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Example 1: Get MA Crossover signal
    token = "bitcoin"
    signal = get_ma_crossover_signal.invoke({"token_id": token})
    print(signal)

    # Example 2: Run a backtest
    message, artifact = backtest_ma_crossover_strategy.invoke(
        {
            "token_id": token,
            "fast_period": 10,
            "slow_period": 50,
            "days": 365,
            "initial_capital": 10000.0,
        }
    )
    print("\n" + message)

    # Example 3: Compare strategies
    comparison = compare_trading_strategies.invoke(
        {"token_id": token, "days": 365, "initial_capital": 10000.0}
    )
    print("\n" + comparison)

    # Example 4: Find optimal strategy parameters
    optimal_params = get_optimal_strategy_parameters.invoke(
        {"token_id": token, "strategy_type": "ma_crossover", "days": 365}
    )
    print("\n" + optimal_params)
