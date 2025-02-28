"""
Test script for the enhanced tools/langchain_tools module.
This script demonstrates the usage of enhanced LangChain tool features
like error handling, content_and_artifact response format, and more.
"""

from tools.langchain_tools import (
    get_token_indicators,
    get_advanced_indicators,
    get_historical_indicators,
)
from langchain_core.tools import ToolException
from core.indicators import MeanReversionService
import time
import matplotlib.pyplot as plt
import pandas as pd


def test_basic_indicators():
    """Test the basic indicator tools with improved error handling."""
    # Initialize the service
    service = MeanReversionService()

    # Test with multiple tokens
    tokens = ["bitcoin", "ethereum", "solana", "cardano"]

    print("=== CURRENT TECHNICAL INDICATORS ===")
    print("Token\t\tPrice\t\tZ-Score\t\tRSI\t\tBollinger %B")
    print("-" * 80)

    for token in tokens:
        try:
            indicators = service.get_all_indicators(token)

            # Extract values
            price = indicators["current_price"]
            z_score = indicators["indicators"]["z_score"]["value"]
            rsi = indicators["indicators"]["rsi"]["value"]
            percent_b = indicators["indicators"]["bollinger_bands"]["percent_b"]

            # Format token name for display
            token_name = token.ljust(8)

            # Print the results
            print(
                f"{token_name}\t${price:.2f}\t\t{z_score:.2f}\t\t{rsi:.2f}\t\t{percent_b:.2f}"
            )
        except ToolException as e:
            # Demonstrates the ToolException error handling
            print(f"{token}: Error - {str(e)}")
        except Exception as e:
            print(f"{token}: Unexpected error - {str(e)}")

        # Add delay between tokens to avoid rate limiting
        time.sleep(2)

    print("\n")


def test_tool_error_handling():
    """Test the error handling capabilities of the tools."""
    print("=== TESTING ERROR HANDLING ===")

    # Test with invalid token
    invalid_token = "not_a_real_token_12345"
    print(f"Testing with invalid token: {invalid_token}")

    try:
        # This should be caught and handled by the tool's error handler
        result = get_token_indicators.invoke({"token_id": invalid_token})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error not handled properly: {str(e)}")

    # Test with insufficient data
    print("\nTesting with extreme window parameter:")
    try:
        # This should return the default error message
        result = get_historical_indicators.invoke({"token_id": "bitcoin", "days": 3})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error not handled properly: {str(e)}")

    print("\n")


def test_content_and_artifact():
    """Test the content_and_artifact response format."""
    print("=== TESTING CONTENT AND ARTIFACT RESPONSE FORMAT ===")

    # Get advanced indicators which returns both a message and structured data
    try:
        result = get_advanced_indicators.invoke({"token_id": "ethereum"})

        # Check if result is a tuple (message, artifact) or just a message
        if isinstance(result, tuple) and len(result) == 2:
            message, data = result
        else:
            message = result
            data = None

        if data is None:
            print("Error: No artifact data returned")
            return

        print("Human-readable content:")
        print(message)

        print("\nStructured data artifact (sample):")
        print(f"Token: {data['token_id']}")
        print(f"Current price: ${data['current_price']:.2f}")
        print(f"Z-Score: {data['metrics']['z_score']['value']:.2f}")
        print(f"RSI: {data['metrics']['rsi']['value']:.2f}")

        # Demonstrate how the artifact can be used for visualization
        print("\nCreating visualization from artifact data...")

        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot price indicator relationships
        bar_data = [
            data["metrics"]["z_score"]["value"],
            data["metrics"]["rsi"]["value"] / 100,  # Normalize RSI to 0-1
            data["metrics"]["bollinger_bands"]["percent_b"],
        ]
        bar_labels = ["Z-Score", "RSI (normalized)", "Bollinger %B"]
        bar_colors = ["blue", "green", "red"]

        ax.bar(bar_labels, bar_data, color=bar_colors)
        ax.axhline(y=0, color="k", linestyle="-", alpha=0.3)
        ax.set_title(f"{data['token_id'].upper()} Technical Indicators")
        ax.set_ylabel("Indicator Value")

        plt.tight_layout()
        plt.savefig(f"{data['token_id']}_indicators.png")
        print(f"Visualization saved as {data['token_id']}_indicators.png")

    except Exception as e:
        print(f"Error: {str(e)}")

    print("\n")


def test_historical_data():
    """Test the historical indicators tool."""
    print("=== BITCOIN HISTORICAL INDICATORS (LAST 5 DAYS) ===")
    try:
        # Using the string-only return format for human-readable analysis
        result = get_historical_indicators.invoke({"token_id": "bitcoin", "days": 5})
        print(result)

        # Now get the raw data directly from the service for visualization
        service = MeanReversionService()
        historical = service.get_historical_indicators("bitcoin", days=5)

        # Create a simple DataFrame for the historical data
        data_list = []
        for day in historical["data"]:
            data_list.append(
                {
                    "date": day["date"].split("T")[0],
                    "price": day["price"],
                    "z_score": day["z_score"],
                    "rsi": day["rsi"],
                    "percent_b": day["bollinger_bands"]["percent_b"],
                }
            )

        df = pd.DataFrame(data_list)

        # Plot historical indicators
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

        # Price and %B (top)
        ax1.plot(df["date"], df["price"], "b-", label="Price")
        ax1.set_ylabel("Price (USD)", color="b")
        ax1.tick_params(axis="y", labelcolor="b")

        ax1b = ax1.twinx()
        ax1b.plot(df["date"], df["percent_b"], "r-", label="%B")
        ax1b.axhline(y=1, color="r", linestyle="--", alpha=0.3)
        ax1b.axhline(y=0, color="r", linestyle="--", alpha=0.3)
        ax1b.set_ylabel("Bollinger %B", color="r")
        ax1b.tick_params(axis="y", labelcolor="r")

        ax1.set_title("Bitcoin Price and Bollinger %B")

        # Z-Score and RSI (bottom)
        ax2.plot(df["date"], df["z_score"], "g-", label="Z-Score")
        ax2.axhline(y=0, color="g", linestyle="--", alpha=0.3)
        ax2.set_ylabel("Z-Score", color="g")
        ax2.tick_params(axis="y", labelcolor="g")

        ax2b = ax2.twinx()
        ax2b.plot(df["date"], df["rsi"], "m-", label="RSI")
        ax2b.axhline(y=70, color="m", linestyle="--", alpha=0.3)
        ax2b.axhline(y=30, color="m", linestyle="--", alpha=0.3)
        ax2b.set_ylabel("RSI", color="m")
        ax2b.tick_params(axis="y", labelcolor="m")

        ax2.set_title("Bitcoin Z-Score and RSI")

        # Format x-axis
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("bitcoin_historical_indicators.png")
        print(f"Historical visualization saved as bitcoin_historical_indicators.png")

    except Exception as e:
        print(f"Error retrieving historical data: {str(e)}")


if __name__ == "__main__":
    print("TESTING ENHANCED TECHNICAL INDICATORS WITH LANGCHAIN FEATURES\n")

    # Run tests
    test_basic_indicators()
    test_tool_error_handling()
    test_content_and_artifact()
    test_historical_data()

    print("\nAll tests completed!")
