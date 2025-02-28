"""
Test script for the technical_indicators module.
"""
from technical_indicators import IndicatorService

def test_multiple_tokens():
    # Initialize the service
    service = IndicatorService()
    
    # Test with multiple tokens
    tokens = ['bitcoin', 'ethereum', 'solana', 'cardano']
    
    print("=== CURRENT TECHNICAL INDICATORS ===")
    print("Token\t\tPrice\t\tZ-Score\t\tRSI\t\tBollinger %B")
    print("-" * 80)
    
    for token in tokens:
        try:
            indicators = service.get_all_indicators(token)
            
            # Extract values
            price = indicators['current_price']
            z_score = indicators['indicators']['z_score']['value']
            rsi = indicators['indicators']['rsi']['value']
            percent_b = indicators['indicators']['bollinger_bands']['percent_b']
            
            # Format token name for display
            token_name = token.ljust(8)
            
            # Print the results
            print(f"{token_name}\t${price:.2f}\t\t{z_score:.2f}\t\t{rsi:.2f}\t\t{percent_b:.2f}")
        except Exception as e:
            print(f"{token}: Error - {str(e)}")
    
    print("\n")
    
    # Test historical data for Bitcoin
    print("=== BITCOIN HISTORICAL INDICATORS (LAST 5 DAYS) ===")
    try:
        historical = service.get_historical_indicators("bitcoin", days=5)
        for day in historical["data"]:
            date = day['date'].split('T')[0]  # Just get the date part
            print(f"{date}: Price=${day['price']:.2f}, Z-Score={day['z_score']:.2f}, RSI={day['rsi']:.2f}, %B={day['bollinger_bands']['percent_b']:.2f}")
    except Exception as e:
        print(f"Error retrieving historical data: {str(e)}")

if __name__ == "__main__":
    test_multiple_tokens() 