"""
WhaleSignal package for analyzing whale activity and market dominance.
"""

from .whale_dominance import generate_risk_signals
from .risk_multiplier import get_risk_multiplier, apply_risk_multiplier

__all__ = ['generate_risk_signals', 'get_risk_multiplier', 'apply_risk_multiplier']