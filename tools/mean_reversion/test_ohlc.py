"""
Test script for OHLC data integration with the mean reversion tools.
This script demonstrates using CoinAPI to fetch OHLC data and 
calculate technical indicators.
"""

import time
from pprint import pprint
from core.api import TokenPriceAPI
from core.indicators import MeanReversionService, MeanReversionIndicators

def test_ohlc_api():
    """Test the CoinAPI integration for OHLC data."""
    print("\n=== Testing CoinAPI OHLC Data Retrieval ===")
    
    # Initialize the API with CoinAPI provider
    api = TokenPriceAPI(api_provider="coinapi")
    
    token_id = "bitcoin"
    period = "1DAY"
    limit = 20
    
    try:
        print(f"Fetching OHLC data for {token_id} with {period} period, {limit} candles...")
        ohlc_data = api.get_ohlc_data(token_id, period=period, limit=limit)
        
        print(f"Retrieved {len(ohlc_data)} OHLC candles")
        
        # Print the latest 5 candles
        print("\nLatest 5 candles:")
        for candle in ohlc_data[-5:]:
            print(f"{candle.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: " 
                  f"Open=${candle.open:.2f}, High=${candle.high:.2f}, "
                  f"Low=${candle.low:.2f}, Close=${candle.close:.2f}, Vol={candle.volume:.2f}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def test_ohlc_indicators():
    """Test calculating indicators from OHLC data."""
    print("\n=== Testing OHLC Indicator Calculations ===")
    
    # Initialize the API and indicators
    api = TokenPriceAPI(api_provider="coinapi")
    indicators = MeanReversionIndicators()
    
    token_id = "ethereum"
    
    try:
        # Get OHLC data
        ohlc_data = api.get_ohlc_data(token_id, period="1DAY", limit=30)
        
        # Calculate indicators using OHLC data
        z_score = indicators.calculate_z_score(ohlc_data, window=20, use_ohlc=True)
        rsi = indicators.calculate_rsi(ohlc_data, window=14, use_ohlc=True)
        bb = indicators.calculate_bollinger_bands(ohlc_data, window=20, num_std=2.0, use_ohlc=True)
        atr = indicators.calculate_average_true_range(ohlc_data, window=14)
        macd = indicators.calculate_macd(ohlc_data, use_ohlc=True)
        
        # Print the results
        print(f"{token_id.capitalize()} Technical Indicators from OHLC data:")
        print(f"Z-Score: {z_score:.2f} - {indicators.interpret_z_score(z_score)}")
        print(f"RSI: {rsi:.2f} - {indicators.interpret_rsi(rsi)}")
        print(f"Bollinger Bands:")
        print(f"  - Middle Band: ${bb['middle_band']:.2f}")
        print(f"  - Upper Band: ${bb['upper_band']:.2f}")
        print(f"  - Lower Band: ${bb['lower_band']:.2f}")
        print(f"  - Percent B: {bb['percent_b']:.2f} - {indicators.interpret_bb(bb['percent_b'])}")
        print(f"ATR: {atr:.2f}")
        print(f"MACD:")
        print(f"  - MACD Line: {macd['macd_line']:.4f}")
        print(f"  - Signal Line: {macd['signal_line']:.4f}")
        print(f"  - Histogram: {macd['histogram']:.4f}")
        print(f"  - Direction: {'BULLISH' if macd['histogram'] > 0 else 'BEARISH'}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def test_mean_reversion_service_ohlc():
    """Test the MeanReversionService with OHLC data."""
    print("\n=== Testing MeanReversionService with OHLC Data ===")
    
    # Initialize the service with CoinAPI
    service = MeanReversionService(api_provider="coinapi")
    
    token_id = "bitcoin"
    days = 20
    
    try:
        print(f"Getting OHLC metrics for {token_id}...")
        metrics = service.get_ohlc_metrics(token_id, days=days)
        
        # Print key information
        print(f"Current price: ${metrics['current_price']:.2f}")
        print(f"Z-Score: {metrics['metrics']['z_score']['value']:.2f} - {metrics['metrics']['z_score']['interpretation']}")
        print(f"RSI: {metrics['metrics']['rsi']['value']:.2f} - {metrics['metrics']['rsi']['interpretation']}")
        
        bb = metrics['metrics']['bollinger_bands']
        print(f"Bollinger Bands:")
        print(f"  - Upper: ${bb['upper_band']:.2f}")
        print(f"  - Middle: ${bb['middle_band']:.2f}")
        print(f"  - Lower: ${bb['lower_band']:.2f}")
        print(f"  - Percent B: {bb['percent_b']:.2f} - {bb['interpretation']}")
        
        # OHLC-specific metrics
        ohlc = metrics['metrics']['ohlc_specific']
        print(f"OHLC-specific metrics:")
        print(f"  - ATR: {ohlc['atr']['value']:.2f} - {ohlc['atr']['interpretation']}")
        print(f"  - MACD Line: {ohlc['macd']['macd_line']:.4f}")
        print(f"  - MACD Signal: {ohlc['macd']['signal_line']:.4f}")
        print(f"  - MACD Histogram: {ohlc['macd']['histogram']:.4f}")
        print(f"  - MACD Direction: {ohlc['macd']['interpretation']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
    try:
        print("\nGetting historical OHLC indicators...")
        historical = service.get_historical_indicators(token_id, days=5)
        print(f"Got {len(historical['data'])} days of historical data")
        print("\nLatest day indicators:")
        latest = historical['data'][-1]
        print(f"Date: {latest['date']}")
        print(f"OHLC: Open=${latest['open']:.2f}, High=${latest['high']:.2f}, Low=${latest['low']:.2f}, Close=${latest['close']:.2f}")
        print(f"Z-Score: {latest['z_score']:.2f}")
        print(f"RSI: {latest['rsi']:.2f}")
        print(f"ATR: {latest['atr']:.2f}")
        
    except Exception as e:
        print(f"Error with historical data: {str(e)}")
        
def test_all():
    """Run all OHLC tests."""
    test_ohlc_api()
    time.sleep(1)  # Pause to avoid rate limiting
    test_ohlc_indicators()
    time.sleep(1)  # Pause to avoid rate limiting
    test_mean_reversion_service_ohlc()

if __name__ == "__main__":
    print("OHLC DATA INTEGRATION TESTS")
    print("==========================")
    test_all()