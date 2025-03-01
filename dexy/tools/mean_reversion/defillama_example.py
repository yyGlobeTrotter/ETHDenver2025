"""
Example script demonstrating the use of DeFi Llama API 
with the crypto mean reversion tools.
"""

import time
from core.api import TokenPriceAPI
from core.indicators import MeanReversionService

def test_defillama_basic():
    """Test basic DeFi Llama API functionality."""
    print("\n=== Basic DeFi Llama API Test ===")
    
    # Initialize API with DeFi Llama
    api = TokenPriceAPI(api_provider="defillama")
    
    tokens = ["bitcoin", "ethereum", "solana"]
    
    for token_id in tokens:
        try:
            # Get current price
            price = api.get_price(token_id)
            print(f"Current price of {token_id}: ${price:.2f}")
            
            # Add delay to avoid rate limiting
            time.sleep(1)
            
            # Get historical prices (20 days instead of 5)
            prices, dates = api.get_historical_prices(token_id, days=20)
            print(f"Historical prices for {token_id} (last 20 days):")
            for date, price in zip(dates, prices):
                print(f"  {date}: ${price:.2f}")
            
            print()
            # Add delay to avoid rate limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing {token_id}: {str(e)}\n")
            time.sleep(1)

def test_mean_reversion_service():
    """Test MeanReversionService with DeFi Llama API."""
    print("\n=== Mean Reversion Service with DeFi Llama ===")
    
    # Initialize service with DeFi Llama
    service = MeanReversionService(api_provider="defillama")
    
    token_id = "ethereum"
    
    try:
        # Get all metrics
        print(f"Getting metrics for {token_id}...")
        metrics = service.get_all_metrics(token_id, days=20)  # Use 20 days instead of 10
        
        # Print key information
        print(f"Current price: ${metrics['current_price']:.2f}")
        print(f"Z-Score: {metrics['metrics']['z_score']['value']:.2f} - {metrics['metrics']['z_score']['interpretation']}")
        print(f"RSI: {metrics['metrics']['rsi']['value']:.2f} - {metrics['metrics']['rsi']['interpretation']}")
        
        bb = metrics['metrics']['bollinger_bands']
        print(f"Bollinger Bands:")
        print(f"  Upper: ${bb['upper_band']:.2f}")
        print(f"  Middle: ${bb['middle_band']:.2f}")
        print(f"  Lower: ${bb['lower_band']:.2f}")
        print(f"  Percent B: {bb['percent_b']:.2f} - {bb['interpretation']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def compare_providers():
    """Compare data from CoinGecko and DeFi Llama."""
    print("\n=== Comparing CoinGecko and DeFi Llama ===")
    
    token_id = "bitcoin"
    
    # Initialize services
    service_cg = MeanReversionService(api_provider="coingecko")
    service_dl = MeanReversionService(api_provider="defillama")
    
    try:
        # Get metrics from both services
        print(f"Getting metrics for {token_id} from both services...")
        metrics_cg = service_cg.get_all_metrics(token_id, days=20)
        metrics_dl = service_dl.get_all_metrics(token_id, days=20)
        
        # Compare prices
        price_cg = metrics_cg['current_price']
        price_dl = metrics_dl['current_price']
        print(f"Current price:")
        print(f"  CoinGecko: ${price_cg:.2f}")
        print(f"  DeFi Llama: ${price_dl:.2f}")
        print(f"  Difference: ${abs(price_cg - price_dl):.2f} ({abs(price_cg - price_dl) / price_cg * 100:.2f}%)")
        
        # Compare Z-Scores
        z_cg = metrics_cg['metrics']['z_score']['value']
        z_dl = metrics_dl['metrics']['z_score']['value']
        print(f"\nZ-Score:")
        print(f"  CoinGecko: {z_cg:.2f}")
        print(f"  DeFi Llama: {z_dl:.2f}")
        print(f"  Difference: {abs(z_cg - z_dl):.2f}")
        
        # Compare RSI
        rsi_cg = metrics_cg['metrics']['rsi']['value']
        rsi_dl = metrics_dl['metrics']['rsi']['value']
        print(f"\nRSI:")
        print(f"  CoinGecko: {rsi_cg:.2f}")
        print(f"  DeFi Llama: {rsi_dl:.2f}")
        print(f"  Difference: {abs(rsi_cg - rsi_dl):.2f}")
        
        # Compare Bollinger Bands
        bb_cg = metrics_cg['metrics']['bollinger_bands']
        bb_dl = metrics_dl['metrics']['bollinger_bands']
        print(f"\nBollinger Bands Middle:")
        print(f"  CoinGecko: ${bb_cg['middle_band']:.2f}")
        print(f"  DeFi Llama: ${bb_dl['middle_band']:.2f}")
        print(f"  Difference: ${abs(bb_cg['middle_band'] - bb_dl['middle_band']):.2f}")
        
        print(f"\nBollinger Bands %B:")
        print(f"  CoinGecko: {bb_cg['percent_b']:.2f}")
        print(f"  DeFi Llama: {bb_dl['percent_b']:.2f}")
        print(f"  Difference: {abs(bb_cg['percent_b'] - bb_dl['percent_b']):.2f}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("DEFI LLAMA API INTEGRATION TESTS")
    print("================================")
    
    # Test basic API functionality
    test_defillama_basic()
    
    # Test Mean Reversion Service
    test_mean_reversion_service()
    
    # Compare providers
    compare_providers()