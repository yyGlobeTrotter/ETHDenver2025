"""
Technical Indicators Module

This module provides simplified functions for calculating technical indicators
(Z-scores, RSI, and Bollinger Bands) for cryptocurrency data. These indicators
can be combined with other off-chain data to create composite risk scores.
"""
from typing import Dict, List, Optional, Tuple, Any
import requests
import numpy as np
import pandas as pd
import time
from datetime import datetime


class PriceDataAPI:
    """Simplified API wrapper for fetching token price data."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def _make_request_with_retry(self, url: str, params: Dict, max_retries: int = 3) -> requests.Response:
        """Make a request with retry logic for rate limiting."""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:  # Too Many Requests
                    wait_time = 2 ** attempt * 1
                    print(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                raise
    
    def get_current_price(self, token_id: str) -> float:
        """Get current price of a token in USD."""
        url = f"{self.base_url}/simple/price"
        params = {
            "ids": token_id,
            "vs_currencies": "usd"
        }
        response = self._make_request_with_retry(url, params)
        return response.json()[token_id]["usd"]
    
    def get_historical_prices(self, token_id: str, days: int = 30) -> Tuple[List[datetime], List[float]]:
        """
        Get historical price data for a token.
        
        Args:
            token_id: The ID of the token (e.g., 'bitcoin', 'ethereum')
            days: Number of days of historical data to retrieve
            
        Returns:
            Tuple containing (dates, prices)
        """
        url = f"{self.base_url}/coins/{token_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days
        }
        response = self._make_request_with_retry(url, params)
        price_data = response.json()["prices"]
        
        # Extract timestamps and prices
        dates = [datetime.fromtimestamp(price[0]/1000) for price in price_data]
        prices = [price[1] for price in price_data]
        
        return dates, prices


class TechnicalIndicators:
    """Class for calculating technical indicators."""
    
    @staticmethod
    def calculate_z_score(prices: List[float], window: int = 20) -> float:
        """
        Calculate the Z-score for the latest price.
        Z-score = (current_price - moving_average) / standard_deviation
        
        Args:
            prices: List of historical prices
            window: Number of periods for the moving average and standard deviation
            
        Returns:
            Z-score value
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
        
        Args:
            prices: List of historical prices
            window: RSI period
            
        Returns:
            RSI value (0-100)
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
        Middle Band = SMA
        Upper Band = Middle Band + (std_dev * num_std)
        Lower Band = Middle Band - (std_dev * num_std)
        
        Args:
            prices: List of historical prices
            window: Period for the moving average and standard deviation
            num_std: Number of standard deviations for the upper and lower bands
            
        Returns:
            Dictionary with middle_band, upper_band, lower_band, and percent_b values
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


class IndicatorService:
    """
    Service class that provides methods to get technical indicators
    for crypto tokens, ready to be combined with other data sources.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api = PriceDataAPI(api_key=api_key)
        self.indicators = TechnicalIndicators()
    
    def get_all_indicators(self, token_id: str, z_score_window: int = 20, 
                          rsi_window: int = 14, bb_window: int = 20, 
                          bb_std: float = 2.0) -> Dict[str, Any]:
        """
        Get all technical indicators for a token in a single call.
        
        Args:
            token_id: Token identifier (e.g., 'bitcoin', 'ethereum')
            z_score_window: Window for Z-score calculation
            rsi_window: Window for RSI calculation
            bb_window: Window for Bollinger Bands calculation
            bb_std: Number of standard deviations for Bollinger Bands
            
        Returns:
            Dictionary containing all indicators
        """
        # Get historical prices with enough history for all indicators
        max_window = max(z_score_window, rsi_window, bb_window)
        days_needed = max(30, max_window + 10)  # Ensure enough data
        
        dates, prices = self.api.get_historical_prices(token_id, days=days_needed)
        
        # Calculate indicators
        z_score = self.indicators.calculate_z_score(prices, window=z_score_window)
        rsi = self.indicators.calculate_rsi(prices, window=rsi_window)
        bb_data = self.indicators.calculate_bollinger_bands(prices, window=bb_window, num_std=bb_std)
        
        # Create result dictionary
        result = {
            "token_id": token_id,
            "current_price": prices[-1],
            "timestamp": dates[-1].isoformat(),
            "indicators": {
                "z_score": {
                    "value": z_score,
                    "window": z_score_window
                },
                "rsi": {
                    "value": rsi,
                    "window": rsi_window
                },
                "bollinger_bands": {
                    "upper_band": bb_data["upper_band"],
                    "middle_band": bb_data["middle_band"],
                    "lower_band": bb_data["lower_band"],
                    "percent_b": bb_data["percent_b"],
                    "window": bb_window,
                    "num_std": bb_std
                }
            }
        }
        
        return result
    
    def get_historical_indicators(self, token_id: str, days: int = 30,
                                z_score_window: int = 20, rsi_window: int = 14,
                                bb_window: int = 20, bb_std: float = 2.0) -> Dict[str, Any]:
        """
        Calculate indicators for historical data points, returning a time series.
        
        Args:
            token_id: Token identifier
            days: Number of days of data to return
            z_score_window: Window for Z-score calculation
            rsi_window: Window for RSI calculation
            bb_window: Window for Bollinger Bands calculation
            bb_std: Number of standard deviations for Bollinger Bands
            
        Returns:
            Dictionary with time series data for all indicators
        """
        # Get enough historical data to calculate indicators for the entire period
        max_window = max(z_score_window, rsi_window, bb_window)
        days_needed = days + max_window
        
        dates, prices = self.api.get_historical_prices(token_id, days=days_needed)
        
        # Create DataFrame for calculations
        df = pd.DataFrame({
            'date': dates,
            'price': prices
        })
        
        # Calculate moving averages and standard deviations
        df['ma_z'] = df['price'].rolling(window=z_score_window).mean()
        df['std_z'] = df['price'].rolling(window=z_score_window).std()
        df['z_score'] = (df['price'] - df['ma_z']) / df['std_z']
        
        # Calculate RSI
        delta = df['price'].diff()
        gain = delta.copy()
        loss = delta.copy()
        gain[gain < 0] = 0
        loss[loss > 0] = 0
        loss = -loss
        
        avg_gain = gain.rolling(window=rsi_window).mean()
        avg_loss = loss.rolling(window=rsi_window).mean()
        
        rs = avg_gain / avg_loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate Bollinger Bands
        df['ma_bb'] = df['price'].rolling(window=bb_window).mean()
        df['std_bb'] = df['price'].rolling(window=bb_window).std()
        df['upper_band'] = df['ma_bb'] + (df['std_bb'] * bb_std)
        df['lower_band'] = df['ma_bb'] - (df['std_bb'] * bb_std)
        df['percent_b'] = (df['price'] - df['lower_band']) / (df['upper_band'] - df['lower_band'])
        
        # Remove the initial NaN values
        df = df.dropna()
        
        # Ensure we only return the requested number of days
        df = df.tail(days)
        
        # Format the result
        result = {
            "token_id": token_id,
            "data": []
        }
        
        for _, row in df.iterrows():
            result["data"].append({
                "date": row['date'].isoformat(),
                "price": row['price'],
                "z_score": row['z_score'],
                "rsi": row['rsi'],
                "bollinger_bands": {
                    "upper_band": row['upper_band'],
                    "middle_band": row['ma_bb'],
                    "lower_band": row['lower_band'],
                    "percent_b": row['percent_b']
                }
            })
        
        return result


# Example usage
if __name__ == "__main__":
    # Create indicator service
    service = IndicatorService()
    
    # Get current indicators for Bitcoin
    btc_indicators = service.get_all_indicators("bitcoin")
    print(f"Bitcoin Price: ${btc_indicators['current_price']:.2f}")
    print(f"Z-Score: {btc_indicators['indicators']['z_score']['value']:.2f}")
    print(f"RSI: {btc_indicators['indicators']['rsi']['value']:.2f}")
    print(f"Bollinger %B: {btc_indicators['indicators']['bollinger_bands']['percent_b']:.2f}")
    
    # Get historical indicators (last 7 days)
    historical = service.get_historical_indicators("ethereum", days=7)
    print(f"\nEthereum Historical Indicators (Last 7 days):")
    for day in historical["data"]:
        print(f"{day['date']}: Price=${day['price']:.2f}, Z-Score={day['z_score']:.2f}, RSI={day['rsi']:.2f}") 