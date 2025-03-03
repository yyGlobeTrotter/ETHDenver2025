"""
Test script for the cryptocurrency API implementation.
Tests both CoinGecko and DeFi Llama API providers.
"""

import time
from core.api import TokenPriceAPI

def test_coingecko_api():
    """Test the CoinGecko API implementation."""
    print("\n=== Testing CoinGecko API ===")
    
    # Initialize API with CoinGecko
    api = TokenPriceAPI(api_provider="coingecko")
    
    # Test getting current price
    token_id = "bitcoin"
    try:
        price = api.get_price(token_id)
        print(f"Current price of {token_id}: ${price:.2f}")
    except Exception as e:
        print(f"Error getting price for {token_id}: {str(e)}")
    
    # Test getting historical prices
    try:
        prices, dates = api.get_historical_prices(token_id, days=20)
        print(f"\nHistorical prices for {token_id} (last 20 days):")
        for date, price in zip(dates[-20:], prices[-20:]):
            print(f"{date}: ${price:.2f}")
    except Exception as e:
        print(f"Error getting historical prices for {token_id}: {str(e)}")

def test_defillama_api():
    """Test the DeFi Llama API implementation."""
    print("\n=== Testing DeFi Llama API ===")
    
    # Initialize API with DeFi Llama
    api = TokenPriceAPI(api_provider="defillama")
    
    # Test getting current price
    token_id = "bitcoin"
    try:
        price = api.get_price(token_id)
        print(f"Current price of {token_id}: ${price:.2f}")
    except Exception as e:
        print(f"Error getting price for {token_id}: {str(e)}")
    
    # Test getting historical prices
    try:
        prices, dates = api.get_historical_prices(token_id, days=20)
        print(f"\nHistorical prices for {token_id} (last 20 days):")
        for date, price in zip(dates[-20:], prices[-20:]):
            print(f"{date}: ${price:.2f}")
    except Exception as e:
        print(f"Error getting historical prices for {token_id}: {str(e)}")

def compare_apis():
    """Compare results from both APIs."""
    print("\n=== Comparing APIs ===")
    
    token_id = "ethereum"
    
    # Initialize both APIs
    coingecko_api = TokenPriceAPI(api_provider="coingecko")
    defillama_api = TokenPriceAPI(api_provider="defillama")
    
    # Compare current prices
    try:
        coingecko_price = coingecko_api.get_price(token_id)
        defillama_price = defillama_api.get_price(token_id)
        
        print(f"Current price of {token_id}:")
        print(f"CoinGecko: ${coingecko_price:.2f}")
        print(f"DeFi Llama: ${defillama_price:.2f}")
        print(f"Difference: ${abs(coingecko_price - defillama_price):.2f} ({abs(coingecko_price - defillama_price) / coingecko_price * 100:.2f}%)")
    except Exception as e:
        print(f"Error comparing current prices: {str(e)}")

if __name__ == "__main__":
    # Test CoinGecko API
    test_coingecko_api()
    
    # Add delay to avoid rate limiting
    print("\nWaiting 2 seconds to avoid rate limiting...")
    time.sleep(2)
    
    # Test DeFi Llama API
    test_defillama_api()
    
    # Add delay to avoid rate limiting
    print("\nWaiting 2 seconds to avoid rate limiting...")
    time.sleep(2)
    
    # Compare APIs
    compare_apis()