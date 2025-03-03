"""
Integrated Demo combining Mean Reversion signals with Whale Dominance risk multipliers
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.api import TokenPriceAPI
from core.indicators import MeanReversionIndicators, MeanReversionService
from whalesignal.risk_multiplier import get_risk_multiplier, apply_risk_multiplier
from whalesignal.whale_dominance import generate_risk_signals

def calculate_mean_reversion_score(z_score, rsi, percent_b):
    """
    Calculate a unified mean reversion score from technical indicators.
    
    Args:
        z_score: Z-score value (standard deviations from mean)
        rsi: Relative Strength Index value (0-100)
        percent_b: Bollinger Bands %B value
    
    Returns:
        A score between -10 and 10, where:
        - Negative values indicate downward reversion potential
        - Positive values indicate upward reversion potential
        - Magnitude represents strength of the signal
    """
    # Z-score contribution (-3 to 3)
    # Negative z-score (price below mean) contributes to positive signal (upward potential)
    z_score_component = max(min(-z_score, 3), -3)
    
    # RSI contribution (-3 to 3)
    # Low RSI contributes to positive signal (upward potential)
    if rsi <= 30:
        rsi_component = 3 * (30 - rsi) / 30  # 0 to 3 for RSI 30 to 0
    elif rsi >= 70:
        rsi_component = -3 * (rsi - 70) / 30  # -3 to 0 for RSI 100 to 70
    else:
        # Neutral zone
        rsi_component = 0
    
    # Bollinger %B contribution (-4 to 4)
    # Low %B contributes to positive signal (upward potential)
    if percent_b <= 0:
        bb_component = 4 * min(abs(percent_b), 1)  # 0 to 4 for %B 0 to -1 or lower
    elif percent_b >= 1:
        bb_component = -4 * min(percent_b - 1, 1)  # -4 to 0 for %B 2 or higher to 1
    else:
        # Within bands - scale from -2 to 2
        bb_component = -4 * (percent_b - 0.5)  # -2 to 2 for %B 1 to 0
    
    # Combine components
    total_score = z_score_component + rsi_component + bb_component
    
    # Ensure within -10 to 10 range
    return max(min(total_score, 10), -10)

def integrated_analysis(token_id="bitcoin", apply_whale_risk=True):
    """
    Perform integrated analysis combining mean reversion with whale dominance.
    
    Args:
        token_id: The cryptocurrency to analyze
        apply_whale_risk: Whether to apply the whale risk multiplier
    
    Returns:
        Dictionary with analysis results
    """
    print(f"\n=== INTEGRATED ANALYSIS FOR {token_id.upper()} ===")
    
    # Initialize services
    service = MeanReversionService()
    indicators = MeanReversionIndicators()
    
    # Get mean reversion metrics
    metrics = service.get_all_metrics(token_id)
    
    # Extract key values
    current_price = metrics["current_price"]
    
    z_score = metrics["metrics"]["z_score"]["value"]
    z_signal = metrics["metrics"]["z_score"]["interpretation"]
    
    rsi = metrics["metrics"]["rsi"]["value"]
    rsi_signal = metrics["metrics"]["rsi"]["interpretation"]
    
    bb_data = metrics["metrics"]["bollinger_bands"]
    bb_signal = bb_data["interpretation"]
    percent_b = bb_data["percent_b"]
    
    # Print basic analysis
    print(f"Current Price: ${current_price:.2f}")
    print(f"Z-Score: {z_score:.2f} - {z_signal}")
    print(f"RSI: {rsi:.2f} - {rsi_signal}")
    print(f"Bollinger %B: {percent_b:.2f} - {bb_signal}")
    
    # Calculate mean reversion score
    mr_score = calculate_mean_reversion_score(z_score, rsi, percent_b)
    
    print(f"\nMean Reversion Score: {mr_score:.2f}")
    if mr_score > 3:
        direction = "STRONG UPWARD REVERSION POTENTIAL"
    elif mr_score > 0:
        direction = "MODERATE UPWARD REVERSION POTENTIAL"
    elif mr_score > -3:
        direction = "MODERATE DOWNWARD REVERSION POTENTIAL"
    else:
        direction = "STRONG DOWNWARD REVERSION POTENTIAL"
    
    print(f"Direction: {direction}")
    
    # Apply whale dominance risk multiplier if requested
    if apply_whale_risk:
        print("\n=== WHALE DOMINANCE RISK ANALYSIS ===")
        
        # Get risk data
        risk_data = generate_risk_signals()
        risk_score = risk_data["risk_score"]
        risk_level = risk_data["level"]
        
        print(f"Risk Score: {risk_score} - {risk_level}")
        for signal in risk_data["signals"]:
            print(f"- {signal}")
        
        # Calculate and apply multiplier
        multiplier_data = apply_risk_multiplier(mr_score, risk_score)
        multiplier = multiplier_data["multiplier"]
        adjusted_score = multiplier_data["adjusted_value"]
        
        print(f"\nRisk Multiplier: {multiplier:.1f}x ({multiplier_data['explanation']})")
        print(f"Original Mean Reversion Score: {mr_score:.2f}")
        print(f"Adjusted Mean Reversion Score: {adjusted_score:.2f}")
        
        # Determine final signal strength
        if abs(adjusted_score) > abs(mr_score):
            print(f"Signal Strength: INCREASED due to whale activity")
        else:
            print(f"Signal Strength: UNCHANGED")
        
        # Return integrated results
        return {
            "token": token_id,
            "price": current_price,
            "technical_indicators": {
                "z_score": z_score,
                "rsi": rsi,
                "percent_b": percent_b
            },
            "mean_reversion_score": mr_score,
            "risk_data": risk_data,
            "risk_multiplier": multiplier,
            "adjusted_score": adjusted_score,
            "final_direction": direction,
            "signal_strength": "INCREASED" if abs(adjusted_score) > abs(mr_score) else "UNCHANGED"
        }
    else:
        # Return results without whale risk
        return {
            "token": token_id,
            "price": current_price,
            "technical_indicators": {
                "z_score": z_score,
                "rsi": rsi,
                "percent_b": percent_b
            },
            "mean_reversion_score": mr_score,
            "final_direction": direction
        }

def multi_token_integrated_analysis():
    """Run integrated analysis on multiple tokens."""
    print("\n=== MULTI-TOKEN INTEGRATED ANALYSIS ===")
    
    tokens = ["bitcoin", "ethereum", "solana"]
    results = []
    
    for token_id in tokens:
        try:
            result = integrated_analysis(token_id)
            results.append(result)
            print("\n" + "-" * 50 + "\n")
        except Exception as e:
            print(f"Error analyzing {token_id}: {str(e)}")
    
    # Display comparison table
    print("\nIntegrated Signal Comparison:")
    print("{:<10} {:<12} {:<10} {:<10} {:<12} {:<12} {:<12}".format(
        "Token", "Price", "MR Score", "Risk Score", "Multiplier", "Adj Score", "Signal"))
    print("-" * 80)
    
    for r in results:
        print("{:<10} ${:<11.2f} {:<10.2f} {:<10} {:<12.1f} {:<12.2f} {:<12}".format(
            r["token"], 
            r["price"], 
            r["mean_reversion_score"], 
            r["risk_data"]["risk_score"],
            r["risk_multiplier"],
            r["adjusted_score"],
            r["signal_strength"]
        ))

def main():
    """Run the integrated analysis demo."""
    print("INTEGRATED MEAN REVERSION + WHALE DOMINANCE DEMO")
    print("================================================")
    print("This demo shows how to combine mean reversion signals with whale dominance risk multipliers")
    
    # Run multi-token analysis
    multi_token_integrated_analysis()

if __name__ == "__main__":
    main()