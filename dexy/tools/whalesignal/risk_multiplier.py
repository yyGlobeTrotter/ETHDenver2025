"""
Risk multiplier module that combines whale dominance signals with mean reversion signals.
"""

from .whale_dominance import generate_risk_signals


def get_risk_multiplier(risk_score=None):
    """
    Calculate a risk multiplier based on whale dominance and activity.
    
    Args:
        risk_score: Optional risk score to use instead of generating from whale signals
        
    Returns:
        A multiplier value (1.0, 1.5, or 2.0) and associated risk information
    """
    # If no risk score provided, generate it from whale signals
    if risk_score is None:
        risk_data = generate_risk_signals()
        risk_score = risk_data["risk_score"]
        risk_level = risk_data["level"]
        risk_signals = risk_data["signals"]
    else:
        risk_level = "🚨 HIGH RISK ALERT" if risk_score >= 5 else "⚠️ MODERATE RISK" if risk_score >= 2 else "🟢 LOW RISK"
        risk_signals = [f"Using provided risk score: {risk_score}"]
    
    # Apply multiplier logic
    if risk_score >= 5:
        multiplier = 2.0
        explanation = "High whale activity/dominance detected - doubling signal strength"
    elif risk_score >= 2:
        multiplier = 1.5
        explanation = "Moderate whale activity/dominance detected - increasing signal strength by 50%"
    else:
        multiplier = 1.0
        explanation = "Normal whale activity/dominance - maintaining original signal strength"
    
    return {
        "multiplier": multiplier,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_signals": risk_signals,
        "explanation": explanation
    }


def apply_risk_multiplier(signal_value, risk_score=None):
    """
    Apply a risk multiplier to a signal value.
    
    Args:
        signal_value: The original signal value to be adjusted
        risk_score: Optional risk score to use instead of generating from whale signals
        
    Returns:
        The adjusted signal value and associated risk information
    """
    multiplier_data = get_risk_multiplier(risk_score)
    
    # Apply the multiplier to the signal
    adjusted_value = signal_value * multiplier_data["multiplier"]
    
    # Add the adjusted value to the return data
    multiplier_data["original_value"] = signal_value
    multiplier_data["adjusted_value"] = adjusted_value
    
    return multiplier_data