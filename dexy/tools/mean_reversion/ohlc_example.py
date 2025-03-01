"""
Example script demonstrating the use of OHLC data with the mean reversion tools.
"""

from langchain_tools import get_ohlc_data, get_ohlc_indicators
from pprint import pprint

def test_ohlc_tools():
    """Test the OHLC langchain tools."""
    print("\n=== Testing OHLC LangChain Tools ===")
    
    token_id = "bitcoin"
    
    # Get OHLC data
    print(f"Getting OHLC data for {token_id}...")
    message, data = get_ohlc_data(token_id, period="1DAY", limit=10)
    
    # Display the human-readable message
    print("\nHuman-readable OHLC data:")
    print(message)
    
    # Display the structured data
    print("\nStructured OHLC data (first candle):")
    pprint(data[0])
    
    # Get OHLC indicators
    print(f"\nGetting OHLC indicators for {token_id}...")
    message, metrics = get_ohlc_indicators(token_id, days=10)
    
    # Display the human-readable message
    print("\nHuman-readable OHLC indicators:")
    print(message)
    
    # Display some of the structured data
    print("\nStructured OHLC metrics (selected):")
    print(f"Current price: ${metrics['current_price']:.2f}")
    print(f"Z-Score: {metrics['metrics']['z_score']['value']:.2f}")
    print(f"RSI: {metrics['metrics']['rsi']['value']:.2f}")
    print(f"ATR: {metrics['metrics']['ohlc_specific']['atr']['value']:.2f}")
    print(f"MACD: {metrics['metrics']['ohlc_specific']['macd']['macd_line']:.4f}")

def main():
    """Run the OHLC tools example."""
    print("OHLC DATA TOOLS EXAMPLE")
    print("======================")
    test_ohlc_tools()

if __name__ == "__main__":
    main()