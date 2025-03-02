"""
Test script for the mean reversion tools.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import time  # Add time module for delays

# Get API key from environment variable
# Set this in your environment or .env file before running
os.environ.setdefault("OPENAI_API_KEY", "")  # Default to empty string if not set

from langchain_tools import (
    get_token_price,
    get_token_z_score,
    get_token_rsi,
    get_token_bollinger_bands,
    mean_reversion_analyzer,
)

from advanced_strategy import (
    get_token_mean_reversion_signal,
    backtest_mean_reversion_strategy,
    MeanReversionStrategy,
)


def test_basic_metrics():
    """Test the basic metric tools."""
    tokens = ["bitcoin", "ethereum", "solana", "cardano", "polkadot"]

    print("=== BASIC METRICS TEST ===")

    for token in tokens:
        print(f"\nTesting {token.upper()}:")

        try:
            # Get current price
            price = get_token_price.invoke({"token_id": token})
            print(f"✅ Current price: ${price:.2f}")
            time.sleep(1)  # Add delay to avoid rate limiting

            # Get Z-Score (deviation from mean)
            z_score = get_token_z_score.invoke({"token_id": token})
            print(f"✅ Z-Score: {z_score:.2f}")
            time.sleep(1)  # Add delay to avoid rate limiting

            # Get RSI (momentum)
            rsi = get_token_rsi.invoke({"token_id": token})
            print(f"✅ RSI: {rsi:.2f}")
            time.sleep(2)  # Add longer delay between tokens

        except Exception as e:
            print(f"❌ Error: {str(e)}")

        # Add delay between tokens
        time.sleep(3)

    print("\n" + "=" * 50)


def test_mean_reversion_score():
    """Test the mean reversion score calculation for multiple tokens."""
    tokens = ["bitcoin", "ethereum"]  # Reduced number of tokens to test

    print("=== MEAN REVERSION SCORE TEST ===")

    results = []

    for token in tokens:
        try:
            print(f"\n🔍 Analyzing {token.upper()}...")

            # Get comprehensive analysis
            analysis = mean_reversion_analyzer.invoke({"token_id": token})
            print(analysis)
            time.sleep(2)  # Add delay to avoid rate limiting

            # Get trading signal
            signal = get_token_mean_reversion_signal.invoke({"token_id": token})

            # Extract trading signal from the returned string
            if "Signal: BUY" in signal:
                action = "BUY"
            elif "Signal: SELL" in signal:
                action = "SELL"
            else:
                action = "HOLD"

            # Store result for comparison
            results.append({"token": token.upper(), "action": action})

            # Add delay between tokens
            time.sleep(3)

        except Exception as e:
            print(f"❌ Error with {token}: {str(e)}")

    # Print results table
    print("\n=== SUMMARY OF MEAN REVERSION SIGNALS ===")
    for result in results:
        print(f"{result['token']:10} | {result['action']}")

    print("\n" + "=" * 50)


def test_bollinger_bands_artifact():
    """Test the Bollinger Bands tool with artifact return."""
    token = "bitcoin"

    try:
        print(f"\n=== BOLLINGER BANDS TEST FOR {token.upper()} ===")

        # Get Bollinger Bands data with artifact
        message, artifact = get_token_bollinger_bands.invoke(
            {"token_id": token, "window": 20, "num_std": 2.0}
        )

        # Print the analysis message
        print(message)

        # Print the artifact data
        print("\nArtifact Data:")
        print(f"Token ID: {artifact['token_id']}")
        print(f"Percent B: {artifact['percent_b']:.4f}")
        print(f"Number of price points: {len(artifact['prices'])}")

        # Create simple visualization
        print("\nGenerating plot from artifact data...")

        plt.figure(figsize=(12, 6))

        # Price data
        plt.plot(artifact["dates"][-30:], artifact["prices"][-30:], label="Price")

        # Bollinger Bands
        bb_data = artifact["data"]
        plt.axhline(
            y=bb_data["upper_band"], color="r", linestyle="--", label="Upper Band"
        )
        plt.axhline(
            y=bb_data["middle_band"], color="g", linestyle="-", label="Middle Band"
        )
        plt.axhline(
            y=bb_data["lower_band"], color="b", linestyle="--", label="Lower Band"
        )

        plt.title(f"{token.upper()} with Bollinger Bands (Last 30 Days)")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig(f"{token}_bollinger_bands.png")
        print(f"✅ Plot saved as {token}_bollinger_bands.png")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print("\n" + "=" * 50)


def test_backtest_strategy():
    """Test the backtesting functionality."""
    token = "ethereum"
    days = 180
    initial_capital = 10000.0

    try:
        print(f"\n=== BACKTEST STRATEGY TEST FOR {token.upper()} ===")
        print(f"Timeframe: {days} days")
        print(f"Initial Capital: ${initial_capital}")

        # Run backtest
        result = backtest_mean_reversion_strategy.invoke(
            {"token_id": token, "days": days, "initial_capital": initial_capital}
        )

        # Check if result is a tuple (message, artifact) or just a message
        if isinstance(result, tuple) and len(result) == 2:
            message, artifact = result
        else:
            message = result
            artifact = None

        # Print the backtest results
        print(message)

        # Only proceed with visualization if we have the artifact
        if artifact and "results" in artifact:
            # Visualize with the strategy class
            strategy = MeanReversionStrategy()
            results = strategy.backtest_strategy(
                token, days=days, initial_capital=initial_capital
            )

            # Save the visualization
            save_path = f"{token}_backtest_results.png"
            strategy.plot_backtest_results(results, save_path=save_path)
            print(f"✅ Backtest visualization saved as {save_path}")
        else:
            print("⚠️ No artifact data available for visualization")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print("\n" + "=" * 50)


def main():
    """Run all tests."""
    print("\n" + "=" * 20 + " TESTING MEAN REVERSION TOOLS " + "=" * 20)

    # Test basic metrics
    test_basic_metrics()

    # Add delay between test sections
    time.sleep(10)

    # Test mean reversion score
    test_mean_reversion_score()

    # Add delay between test sections
    time.sleep(10)

    # Test Bollinger Bands artifact
    test_bollinger_bands_artifact()

    # Add delay between test sections
    time.sleep(10)

    # Test backtesting strategy
    test_backtest_strategy()

    print("\n" + "=" * 30 + " TESTS COMPLETED " + "=" * 30)


if __name__ == "__main__":
    main()
