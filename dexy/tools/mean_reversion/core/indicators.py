"""
Core indicators module for cryptocurrency technical analysis.
This module provides consistent implementations of various technical indicators
used in mean reversion trading strategies.
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from datetime import datetime

from .api import TokenPriceAPI

class MeanReversionIndicators:
    """
    Core calculator for mean reversion indicators.
    This class contains all calculation methods shared across the project.
    """
    
    @staticmethod
    def calculate_z_score(prices: List[float], window: int = 20) -> float:
        """
        Calculate the Z-score for the latest price.
        Z-score = (current_price - moving_average) / standard_deviation
        """
        if len(prices) < window:
            raise ValueError(f"Not enough price data. Need at least {window} data points.")
        
        prices_array = np.array(prices)
        moving_avg = np.mean(prices_array[-window:])
        std_dev = np.std(prices_array[-window:])
        
        if std_dev == 0:
            return 0  # Avoid division by zero
        
        current_price = prices_array[-1]
        z_score = (current_price - moving_avg) / std_dev
        
        return z_score
    
    @staticmethod
    def calculate_rsi(prices: List[float], window: int = 14) -> float:
        """
        Calculate the Relative Strength Index (RSI).
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss
        """
        if len(prices) < window + 1:
            raise ValueError(f"Not enough price data. Need at least {window + 1} data points.")
        
        # Calculate price changes
        deltas = np.diff(prices)
        
        # Get gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gains and losses
        avg_gain = np.mean(gains[-window:])
        avg_loss = np.mean(losses[-window:])
        
        if avg_loss == 0:
            return 100  # Avoid division by zero
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], window: int = 20, num_std: float = 2.0) -> Dict[str, float]:
        """
        Calculate Bollinger Bands.
        Middle Band = n-day SMA
        Upper Band = Middle Band + (n-day std_dev * num_std)
        Lower Band = Middle Band - (n-day std_dev * num_std)
        """
        if len(prices) < window:
            raise ValueError(f"Not enough price data. Need at least {window} data points.")
        
        prices_array = np.array(prices)
        moving_avg = np.mean(prices_array[-window:])
        std_dev = np.std(prices_array[-window:])
        
        upper_band = moving_avg + (std_dev * num_std)
        lower_band = moving_avg - (std_dev * num_std)
        
        current_price = prices_array[-1]
        
        # Calculate percent B
        percent_b = (current_price - lower_band) / (upper_band - lower_band) if upper_band != lower_band else 0.5
        
        return {
            "middle_band": moving_avg,
            "upper_band": upper_band,
            "lower_band": lower_band,
            "current_price": current_price,
            "percent_b": percent_b
        }
    
    @staticmethod
    def interpret_z_score(z_score: float) -> str:
        """Interpret the Z-score value."""
        if z_score > 2.0:
            return "POTENTIAL DOWNWARD REVERSION (Overvalued)"
        elif z_score < -2.0:
            return "POTENTIAL UPWARD REVERSION (Undervalued)"
        else:
            return "NEUTRAL"
    
    @staticmethod
    def interpret_rsi(rsi: float) -> str:
        """Interpret the RSI value."""
        if rsi > 70:
            return "POTENTIAL DOWNWARD REVERSION (Overbought)"
        elif rsi < 30:
            return "POTENTIAL UPWARD REVERSION (Oversold)"
        else:
            return "NEUTRAL"
    
    @staticmethod
    def interpret_bb(percent_b: float) -> str:
        """Interpret the Bollinger Bands percent B value."""
        if percent_b > 1.0:
            return "POTENTIAL DOWNWARD REVERSION (Above Upper Band)"
        elif percent_b < 0.0:
            return "POTENTIAL UPWARD REVERSION (Below Lower Band)"
        else:
            return "NEUTRAL (Within Bands)"


class MeanReversionService:
    """
    Service for calculating technical indicators for cryptocurrencies.
    This class combines the API and calculation functionality with
    additional features for analysis and interpretation.
    """
    
    def __init__(self, api_key: Optional[str] = None, custom_api_url: Optional[str] = None):
        """
        Initialize the service with optional API credentials.
        
        Args:
            api_key: Optional API key for price data provider
            custom_api_url: Optional custom URL for price data provider
        """
        self.api = TokenPriceAPI(api_key=api_key, base_url=custom_api_url)
        self.indicators = MeanReversionIndicators()
    
    def get_all_metrics(self, token_id: str, days: int = 30, 
                       z_window: int = 20, rsi_window: int = 14, 
                       bb_window: int = 20, bb_std: float = 2.0) -> Dict[str, Any]:
        """
        Calculate all mean reversion metrics in a single efficient call.
        
        Args:
            token_id: The ID of the token (e.g., 'bitcoin', 'ethereum')
            days: Number of days of historical data to fetch
            z_window: Window size for Z-score calculation
            rsi_window: Window size for RSI calculation
            bb_window: Window size for Bollinger Bands calculation
            bb_std: Number of standard deviations for Bollinger Bands
            
        Returns:
            Dictionary containing all calculated metrics and raw data
        """
        try:
            # Single API call to get all required data
            prices, dates = self.api.get_historical_prices(token_id, days)
            current_price = prices[-1]
            
            # Calculate all metrics
            z_score = self.indicators.calculate_z_score(prices, window=z_window)
            rsi = self.indicators.calculate_rsi(prices, window=rsi_window)
            bb_data = self.indicators.calculate_bollinger_bands(prices, window=bb_window, num_std=bb_std)
            
            # Format time series data for potential further analysis
            time_series = pd.DataFrame({
                'date': dates,
                'price': prices
            })
            
            # Compile all metrics into a single response dictionary
            return {
                "token_id": token_id,
                "current_price": current_price,
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "z_score": {
                        "value": z_score,
                        "window": z_window,
                        "interpretation": self.indicators.interpret_z_score(z_score)
                    },
                    "rsi": {
                        "value": rsi,
                        "window": rsi_window,
                        "interpretation": self.indicators.interpret_rsi(rsi)
                    },
                    "bollinger_bands": {
                        "upper_band": bb_data["upper_band"],
                        "middle_band": bb_data["middle_band"],
                        "lower_band": bb_data["lower_band"],
                        "percent_b": bb_data["percent_b"],
                        "window": bb_window,
                        "std_multiplier": bb_std,
                        "interpretation": self.indicators.interpret_bb(bb_data["percent_b"])
                    }
                },
                "raw_data": {
                    "time_series": time_series.to_dict(orient='records'),
                    "days": days
                }
            }
        except Exception as e:
            raise ValueError(f"Error calculating metrics for {token_id}: {str(e)}")
    
    def get_risk_metrics(self, token_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get focused risk metrics for integration with other risk scoring systems.
        
        Args:
            token_id: The ID of the token (e.g., 'bitcoin', 'ethereum')
            days: Number of days of historical data to fetch
            
        Returns:
            Dictionary containing key risk metrics without verbose data
        """
        try:
            # Get all metrics
            all_data = self.get_all_metrics(token_id, days)
            
            # Extract just the data needed for risk scoring
            risk_data = {
                "token_id": token_id,
                "current_price": all_data["current_price"],
                "timestamp": all_data["timestamp"],
                "z_score": all_data["metrics"]["z_score"]["value"],
                "rsi": all_data["metrics"]["rsi"]["value"],
                "bollinger_percent_b": all_data["metrics"]["bollinger_bands"]["percent_b"],
                "upper_band": all_data["metrics"]["bollinger_bands"]["upper_band"],
                "lower_band": all_data["metrics"]["bollinger_bands"]["lower_band"]
            }
            
            return risk_data
        except Exception as e:
            raise ValueError(f"Error calculating risk metrics for {token_id}: {str(e)}")
    
    def get_all_indicators(self, token_id: str, window: int = 20, num_std: float = 2.0) -> Dict[str, Any]:
        """
        Get all indicators for a token with a single API call.
        
        Args:
            token_id: The ID of the token (e.g., 'bitcoin', 'ethereum')
            window: The lookback window for calculations
            num_std: Number of standard deviations for Bollinger Bands
            
        Returns:
            Dictionary containing all indicators and their interpretations
        """
        try:
            # Get all metrics using the existing method
            all_data = self.get_all_metrics(token_id, days=window*2, 
                                           z_window=window, rsi_window=window, 
                                           bb_window=window, bb_std=num_std)
            
            # Reformat to match the expected structure in test_indicators.py
            result = {
                "token_id": token_id,
                "current_price": all_data["current_price"],
                "timestamp": all_data["timestamp"],
                "indicators": {
                    "z_score": {
                        "value": all_data["metrics"]["z_score"]["value"],
                        "interpretation": all_data["metrics"]["z_score"]["interpretation"]
                    },
                    "rsi": {
                        "value": all_data["metrics"]["rsi"]["value"],
                        "interpretation": all_data["metrics"]["rsi"]["interpretation"]
                    },
                    "bollinger_bands": {
                        "upper_band": all_data["metrics"]["bollinger_bands"]["upper_band"],
                        "middle_band": all_data["metrics"]["bollinger_bands"]["middle_band"],
                        "lower_band": all_data["metrics"]["bollinger_bands"]["lower_band"],
                        "percent_b": all_data["metrics"]["bollinger_bands"]["percent_b"],
                        "interpretation": all_data["metrics"]["bollinger_bands"]["interpretation"]
                    }
                }
            }
            
            return result
        except Exception as e:
            raise ValueError(f"Error calculating indicators for {token_id}: {str(e)}")
    
    def get_historical_indicators(self, token_id: str, days: int = 30, window: int = 20) -> Dict[str, Any]:
        """
        Get historical indicators over a time period.
        
        Args:
            token_id: The ID of the token
            days: Number of days of historical data to return
            window: The lookback window for calculations
            
        Returns:
            Dictionary with historical indicators
        """
        try:
            # Get historical data
            prices, dates = self.api.get_historical_prices(token_id, days=days + window)  # Extra data for calculations
            
            # Calculate indicators for each day in the period
            results = []
            
            for i in range(window, len(prices)):
                price_window = prices[max(0, i-window):i+1]
                current_price = prices[i]
                current_date = dates[i]
                
                # Z-score
                z_score = self.indicators.calculate_z_score(price_window, window=min(window, len(price_window)))
                
                # RSI 
                rsi = self.indicators.calculate_rsi(price_window, window=min(window, len(price_window)-1))
                
                # Bollinger Bands
                bb = self.indicators.calculate_bollinger_bands(price_window, window=min(window, len(price_window)))
                
                results.append({
                    "date": current_date,
                    "price": current_price,
                    "z_score": z_score,
                    "rsi": rsi,
                    "bollinger_bands": bb
                })
            
            return {
                "token_id": token_id,
                "window": window,
                "data": results[-days:]  # Return only the requested number of days
            }
        except Exception as e:
            raise ValueError(f"Error calculating historical indicators for {token_id}: {str(e)}")