"""
Mean Reversion Strategy Demo

A simplified example showing how to use the core mean reversion classes
without any AI/LangChain dependencies.
"""

from core.api import TokenPriceAPI, OHLCData
from core.indicators import MeanReversionIndicators, MeanReversionService
from pprint import pprint

def demo_basic_indicators():
    """
    Demonstrate basic mean reversion indicators for a cryptocurrency.
    """
    print("\n=== BASIC MEAN REVERSION INDICATORS ===")
    
    # Initialize services
    api = TokenPriceAPI()  # Uses DeFi Llama API by default
    indicators = MeanReversionIndicators()
    
    # Choose token to analyze
    token_id = "bitcoin"
    print(f"Analyzing {token_id.upper()}...")
    
    # Get current price
    current_price = api.get_price(token_id)
    print(f"Current price: ${current_price:.2f}")
    
    # Get historical prices (last 30 days)
    prices, dates = api.get_historical_prices(token_id, days=30)
    
    # Calculate Z-score (how many standard deviations from mean)
    z_score = indicators.calculate_z_score(prices, window=20)
    print(f"Z-Score (20-day): {z_score:.2f}")
    print(f"Interpretation: {indicators.interpret_z_score(z_score)}")
    
    # Calculate RSI (momentum indicator)
    rsi = indicators.calculate_rsi(prices, window=14)
    print(f"RSI (14-day): {rsi:.2f}")
    print(f"Interpretation: {indicators.interpret_rsi(rsi)}")
    
    # Calculate Bollinger Bands
    bb = indicators.calculate_bollinger_bands(prices, window=20, num_std=2.0)
    print("\nBollinger Bands:")
    print(f"- Upper Band: ${bb['upper_band']:.2f}")
    print(f"- Middle Band: ${bb['middle_band']:.2f}")
    print(f"- Lower Band: ${bb['lower_band']:.2f}")
    print(f"- Percent B: {bb['percent_b']:.2f}")
    print(f"Interpretation: {indicators.interpret_bb(bb['percent_b'])}")
    
    # Overall mean reversion signal
    signals = [
        indicators.interpret_z_score(z_score),
        indicators.interpret_rsi(rsi),
        indicators.interpret_bb(bb['percent_b'])
    ]
    
    upward_signals = sum(1 for s in signals if "UPWARD" in s)
    downward_signals = sum(1 for s in signals if "DOWNWARD" in s)
    
    if upward_signals > downward_signals:
        overall_signal = "POTENTIAL UPWARD REVERSION"
    elif downward_signals > upward_signals:
        overall_signal = "POTENTIAL DOWNWARD REVERSION"
    else:
        overall_signal = "NEUTRAL"
        
    print(f"\nOVERALL SIGNAL: {overall_signal}")

def demo_ohlc_data():
    """
    Demonstrate OHLC-based indicators for more detailed analysis.
    """
    print("\n=== OHLC-BASED INDICATORS ===")
    
    # Initialize with CoinAPI for OHLC data
    api = TokenPriceAPI(api_provider="coinapi")  
    indicators = MeanReversionIndicators()
    
    # Choose token to analyze
    token_id = "bitcoin"
    print(f"Analyzing {token_id.upper()} with OHLC data...")
    
    # Get OHLC data (last 30 days)
    try:
        ohlc_data = api.get_ohlc_data(token_id, period="1DAY", limit=30)
        
        # Display basic info
        print(f"Retrieved {len(ohlc_data)} days of OHLC data")
        print(f"Date range: {ohlc_data[0].timestamp.strftime('%Y-%m-%d')} to {ohlc_data[-1].timestamp.strftime('%Y-%m-%d')}")
        
        # Calculate indicators using OHLC data
        current_price = ohlc_data[-1].close
        print(f"Current price: ${current_price:.2f}")
        
        z_score = indicators.calculate_z_score(ohlc_data, window=20, use_ohlc=True)
        print(f"Z-Score (20-day): {z_score:.2f}")
        
        rsi = indicators.calculate_rsi(ohlc_data, window=14, use_ohlc=True)
        print(f"RSI (14-day): {rsi:.2f}")
        
        bb = indicators.calculate_bollinger_bands(ohlc_data, window=20, num_std=2.0, use_ohlc=True)
        print(f"Bollinger %B: {bb['percent_b']:.2f}")
        
        # OHLC-specific indicators
        atr = indicators.calculate_average_true_range(ohlc_data, window=14)
        print(f"ATR (14-day): {atr:.2f}")
        print(f"ATR as % of price: {(atr/current_price)*100:.2f}%")
        
        # Extract data for MACD
        closes = [candle.close for candle in ohlc_data]
        macd = indicators.calculate_macd(closes)
        print(f"MACD: {macd['macd_line']:.4f}")
        print(f"Signal: {macd['signal_line']:.4f}")
        print(f"Histogram: {macd['histogram']:.4f}")
        print(f"MACD Signal: {'BULLISH' if macd['macd_line'] > macd['signal_line'] else 'BEARISH'}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Note: OHLC data requires a valid CoinAPI key for full functionality.")

def demo_multi_token_analysis():
    """
    Compare mean reversion signals across multiple tokens.
    """
    print("\n=== MULTI-TOKEN MEAN REVERSION ANALYSIS ===")
    
    service = MeanReversionService()
    tokens = ["bitcoin", "ethereum", "solana"]
    
    results = []
    
    for token_id in tokens:
        try:
            print(f"Analyzing {token_id.upper()}...")
            metrics = service.get_all_metrics(token_id)
            
            # Extract key metrics
            current_price = metrics["current_price"]
            z_score = metrics["metrics"]["z_score"]["value"]
            z_signal = metrics["metrics"]["z_score"]["interpretation"]
            rsi = metrics["metrics"]["rsi"]["value"]
            rsi_signal = metrics["metrics"]["rsi"]["interpretation"]
            bb_data = metrics["metrics"]["bollinger_bands"]
            percent_b = bb_data["percent_b"]
            bb_signal = bb_data["interpretation"]
            
            # Determine overall signal
            signals = [z_signal, rsi_signal, bb_signal]
            upward_signals = sum(1 for s in signals if "UPWARD" in s)
            downward_signals = sum(1 for s in signals if "DOWNWARD" in s)
            
            if upward_signals > downward_signals:
                overall_signal = "POTENTIAL UPWARD REVERSION"
            elif downward_signals > upward_signals:
                overall_signal = "POTENTIAL DOWNWARD REVERSION"
            else:
                overall_signal = "NEUTRAL"
                
            results.append({
                "token": token_id,
                "price": current_price,
                "z_score": z_score,
                "rsi": rsi,
                "percent_b": percent_b,
                "overall_signal": overall_signal
            })
            
        except Exception as e:
            print(f"Error analyzing {token_id}: {str(e)}")
    
    # Display comparison table
    print("\nToken Comparison:")
    print("{:<10} {:<10} {:<10} {:<10} {:<10} {:<25}".format(
        "Token", "Price", "Z-Score", "RSI", "% B", "Signal"))
    print("-" * 75)
    
    for r in results:
        print("{:<10} ${:<9.2f} {:<10.2f} {:<10.2f} {:<10.2f} {:<25}".format(
            r["token"], r["price"], r["z_score"], r["rsi"], r["percent_b"], r["overall_signal"]))

def main():
    """Run the mean reversion strategy demo."""
    print("MEAN REVERSION STRATEGY DEMO")
    print("============================")
    print("This demo shows how to use the core mean reversion classes without AI dependencies")
    
    # Run basic analysis
    demo_basic_indicators()
    
    # Run analysis on multiple tokens
    demo_multi_token_analysis()
    
    # Uncomment the following line to run OHLC analysis
    # Note: OHLC analysis requires a valid CoinAPI key
    # demo_ohlc_data()

if __name__ == "__main__":
    main()