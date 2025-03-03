"""
Core indicators module for cryptocurrency technical analysis.
This module provides consistent implementations of various technical indicators
used in mean reversion trading strategies, including OHLC-based indicators.
"""

from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd
from datetime import datetime

from .api import TokenPriceAPI, OHLCData

class MeanReversionIndicators:
    """
    Core calculator for mean reversion indicators.
    This class contains all calculation methods shared across the project,
    including support for OHLC-based indicators.
    """
    
    @staticmethod
    def calculate_z_score(prices: Union[List[float], List[OHLCData]], window: int = 20, use_ohlc: bool = False) -> float:
        """
        Calculate the Z-score for the latest price.
        Z-score = (current_price - moving_average) / standard_deviation
        
        Args:
            prices: List of price data or OHLC data
            window: Window size for calculations
            use_ohlc: Whether the input is OHLC data
            
        Returns:
            Z-score value
        """
        if len(prices) < window:
            raise ValueError(f"Not enough price data. Need at least {window} data points.")
        
        if use_ohlc:
            # Extract close prices from OHLC data
            close_prices = np.array([candle.close for candle in prices])
            prices_array = close_prices
        else:
            prices_array = np.array(prices)
        
        moving_avg = np.mean(prices_array[-window:])
        std_dev = np.std(prices_array[-window:])
        
        if std_dev == 0:
            return 0  # Avoid division by zero
        
        current_price = prices_array[-1]
        z_score = (current_price - moving_avg) / std_dev
        
        return z_score
    
    @staticmethod
    def calculate_rsi(prices: Union[List[float], List[OHLCData]], window: int = 14, use_ohlc: bool = False) -> float:
        """
        Calculate the Relative Strength Index (RSI).
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss
        
        Args:
            prices: List of price data or OHLC data
            window: Window size for RSI calculation
            use_ohlc: Whether the input is OHLC data
            
        Returns:
            RSI value (0-100)
        """
        if len(prices) < window + 1:
            raise ValueError(f"Not enough price data. Need at least {window + 1} data points.")
        
        if use_ohlc:
            # Extract close prices from OHLC data
            price_data = [candle.close for candle in prices]
        else:
            price_data = prices
        
        # Calculate price changes
        deltas = np.diff(price_data)
        
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
    def calculate_bollinger_bands(
        prices: Union[List[float], List[OHLCData]], 
        window: int = 20, 
        num_std: float = 2.0,
        use_ohlc: bool = False
    ) -> Dict[str, float]:
        """
        Calculate Bollinger Bands.
        Middle Band = n-day SMA
        Upper Band = Middle Band + (n-day std_dev * num_std)
        Lower Band = Middle Band - (n-day std_dev * num_std)
        
        Args:
            prices: List of price data or OHLC data
            window: Window size for Bollinger Bands calculation
            num_std: Number of standard deviations for bands
            use_ohlc: Whether the input is OHLC data
            
        Returns:
            Dictionary with Bollinger Bands values
        """
        if len(prices) < window:
            raise ValueError(f"Not enough price data. Need at least {window} data points.")
        
        if use_ohlc:
            # Extract close prices from OHLC data
            price_data = np.array([candle.close for candle in prices])
        else:
            price_data = np.array(prices)
        
        moving_avg = np.mean(price_data[-window:])
        std_dev = np.std(price_data[-window:])
        
        upper_band = moving_avg + (std_dev * num_std)
        lower_band = moving_avg - (std_dev * num_std)
        
        current_price = price_data[-1]
        
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
            
    @staticmethod
    def calculate_average_true_range(ohlc_data: List[OHLCData], window: int = 14) -> float:
        """
        Calculate Average True Range (ATR).
        ATR is a measure of volatility.
        
        Args:
            ohlc_data: List of OHLC data points
            window: Window size for ATR calculation
            
        Returns:
            ATR value
        """
        if len(ohlc_data) < window:
            raise ValueError(f"Not enough price data. Need at least {window} data points.")
            
        true_ranges = []
        
        # Calculate true range for each candle
        for i in range(1, len(ohlc_data)):
            high = ohlc_data[i].high
            low = ohlc_data[i].low
            prev_close = ohlc_data[i-1].close
            
            # True Range is the greatest of:
            # 1. Current High - Current Low
            # 2. |Current High - Previous Close|
            # 3. |Current Low - Previous Close|
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        # Calculate ATR as average of true ranges
        atr = np.mean(true_ranges[-window:])
        
        return atr
    
    @staticmethod
    def calculate_atr(highs: List[float], lows: List[float], closes: List[float], window: int = 14) -> float:
        """
        Calculate Average True Range (ATR) from separate high, low, close arrays.
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of close prices
            window: Window size for ATR calculation
            
        Returns:
            ATR value
        """
        if len(highs) < window + 1 or len(lows) < window + 1 or len(closes) < window + 1:
            raise ValueError(f"Not enough price data. Need at least {window + 1} data points.")
        
        true_ranges = []
        
        # Calculate true range for each candle
        for i in range(1, len(closes)):
            # True Range is the greatest of:
            # 1. Current High - Current Low
            # 2. |Current High - Previous Close|
            # 3. |Current Low - Previous Close|
            tr1 = highs[i] - lows[i]
            tr2 = abs(highs[i] - closes[i-1])
            tr3 = abs(lows[i] - closes[i-1])
            
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)
        
        # Calculate ATR as average of true ranges
        atr = np.mean(true_ranges[-window:])
        
        return atr
        
    @staticmethod
    def calculate_macd(prices: Union[List[float], List[OHLCData]], 
                      fast_period: int = 12, 
                      slow_period: int = 26, 
                      signal_period: int = 9, 
                      use_ohlc: bool = False) -> Dict[str, float]:
        """
        Calculate Moving Average Convergence Divergence (MACD).
        
        Args:
            prices: List of price data or OHLC data
            fast_period: Period for fast EMA
            slow_period: Period for slow EMA
            signal_period: Period for signal line
            use_ohlc: Whether the input is OHLC data
            
        Returns:
            Dictionary with MACD values
        """
        if len(prices) < slow_period + signal_period:
            raise ValueError(f"Not enough price data. Need at least {slow_period + signal_period} data points.")
        
        if use_ohlc:
            # Extract close prices from OHLC data
            price_data = np.array([candle.close for candle in prices])
        else:
            price_data = np.array(prices)
            
        # Calculate EMAs
        ema_fast = pd.Series(price_data).ewm(span=fast_period, adjust=False).mean().iloc[-1]
        ema_slow = pd.Series(price_data).ewm(span=slow_period, adjust=False).mean().iloc[-1]
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line
        macd_series = pd.Series(price_data).ewm(span=fast_period, adjust=False).mean() - \
                      pd.Series(price_data).ewm(span=slow_period, adjust=False).mean()
        signal_line = macd_series.ewm(span=signal_period, adjust=False).mean().iloc[-1]
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        return {
            "macd_line": macd_line,
            "signal_line": signal_line,
            "histogram": histogram,
        }


class MeanReversionService:
    """
    Service for calculating technical indicators for cryptocurrencies.
    This class combines the API and calculation functionality with
    additional features for analysis and interpretation.
    Supports both regular price data and OHLC (Open, High, Low, Close) data.
    """
    
    def __init__(self, api_key: Optional[str] = None, custom_api_url: Optional[str] = None, api_provider: str = "defillama"):
        """
        Initialize the service with optional API credentials.
        
        Args:
            api_key: Optional API key for price data provider
            custom_api_url: Optional custom URL for price data provider
            api_provider: The API provider to use (defillama, coingecko, or coinapi)
        """
        self.api = TokenPriceAPI(api_key=api_key, base_url=custom_api_url, api_provider=api_provider)
        self.indicators = MeanReversionIndicators()
        self.use_ohlc = (api_provider == "coinapi")
    
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
            if self.use_ohlc:
                return self._get_historical_indicators_ohlc(token_id, days, window)
            
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
    
    def _get_historical_indicators_ohlc(self, token_id: str, days: int = 30, window: int = 20) -> Dict[str, Any]:
        """
        Get historical indicators using OHLC data.
        
        Args:
            token_id: The ID of the token
            days: Number of days of historical data to return
            window: The lookback window for calculations
            
        Returns:
            Dictionary with historical indicators including OHLC-specific metrics
        """
        try:
            # Get OHLC data
            ohlc_data = self.api.get_ohlc_data(token_id, period="1DAY", limit=days + window)
            
            if not ohlc_data:
                raise ValueError(f"No OHLC data available for {token_id}")
            
            # Calculate indicators for each day in the period
            results = []
            
            for i in range(window, len(ohlc_data)):
                ohlc_window = ohlc_data[max(0, i-window):i+1]
                current_candle = ohlc_data[i]
                current_date = current_candle.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
                
                # Z-score
                z_score = self.indicators.calculate_z_score(ohlc_window, window=min(window, len(ohlc_window)), use_ohlc=True)
                
                # RSI 
                rsi = self.indicators.calculate_rsi(ohlc_window, window=min(window, len(ohlc_window)-1), use_ohlc=True)
                
                # Bollinger Bands
                bb = self.indicators.calculate_bollinger_bands(ohlc_window, window=min(window, len(ohlc_window)), use_ohlc=True)
                
                # ATR (OHLC-specific)
                atr = self.indicators.calculate_average_true_range(ohlc_window, window=min(14, len(ohlc_window)-1))
                
                # MACD (OHLC-specific)
                if len(ohlc_window) >= 26:  # Minimum data needed for MACD
                    macd = self.indicators.calculate_macd(ohlc_window, use_ohlc=True)
                else:
                    macd = {"macd_line": None, "signal_line": None, "histogram": None}
                
                results.append({
                    "date": current_date,
                    "open": current_candle.open,
                    "high": current_candle.high,
                    "low": current_candle.low,
                    "close": current_candle.close,
                    "volume": current_candle.volume,
                    "z_score": z_score,
                    "rsi": rsi,
                    "bollinger_bands": bb,
                    "atr": atr,
                    "macd": macd
                })
            
            return {
                "token_id": token_id,
                "window": window,
                "data_type": "ohlc",
                "data": results[-days:]  # Return only the requested number of days
            }
        except Exception as e:
            raise ValueError(f"Error calculating OHLC indicators for {token_id}: {str(e)}")
            
    def get_ohlc_metrics(self, token_id: str, days: int = 30, 
                        z_window: int = 20, rsi_window: int = 14, 
                        bb_window: int = 20, bb_std: float = 2.0) -> Dict[str, Any]:
        """
        Get comprehensive OHLC-based metrics for a token.
        
        Args:
            token_id: The ID of the token
            days: Number of days of historical data to fetch
            z_window: Window size for Z-score calculation
            rsi_window: Window size for RSI calculation
            bb_window: Window size for Bollinger Bands calculation
            bb_std: Number of standard deviations for Bollinger Bands
            
        Returns:
            Dictionary containing all calculated metrics based on OHLC data
        """
        if not self.use_ohlc:
            raise ValueError("This method requires CoinAPI as the data provider for OHLC data")
            
        try:
            # Get OHLC data
            ohlc_data = self.api.get_ohlc_data(token_id, period="1DAY", limit=days)
            
            if not ohlc_data:
                raise ValueError(f"No OHLC data available for {token_id}")
                
            # Most recent candle
            current_candle = ohlc_data[-1]
            current_price = current_candle.close
            
            # Calculate all metrics
            z_score = self.indicators.calculate_z_score(ohlc_data, window=z_window, use_ohlc=True)
            rsi = self.indicators.calculate_rsi(ohlc_data, window=rsi_window, use_ohlc=True)
            bb_data = self.indicators.calculate_bollinger_bands(ohlc_data, window=bb_window, num_std=bb_std, use_ohlc=True)
            
            # Calculate OHLC-specific indicators
            atr = self.indicators.calculate_average_true_range(ohlc_data, window=14)
            macd = self.indicators.calculate_macd(ohlc_data, use_ohlc=True)
            
            # Format time series data for potential further analysis
            time_series = []
            for candle in ohlc_data:
                time_series.append({
                    'date': candle.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'open': candle.open,
                    'high': candle.high,
                    'low': candle.low,
                    'close': candle.close,
                    'volume': candle.volume
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
                    },
                    "ohlc_specific": {
                        "atr": {
                            "value": atr,
                            "window": 14,
                            "interpretation": f"Volatility indicator: {atr:.2f} units"
                        },
                        "macd": {
                            "macd_line": macd["macd_line"],
                            "signal_line": macd["signal_line"],
                            "histogram": macd["histogram"],
                            "interpretation": "BULLISH" if macd["histogram"] > 0 else "BEARISH"
                        }
                    }
                },
                "raw_data": {
                    "time_series": time_series,
                    "days": days,
                    "data_type": "ohlc"
                }
            }
        except Exception as e:
            raise ValueError(f"Error calculating OHLC metrics for {token_id}: {str(e)}")