from typing import Dict, List, Optional, Union, Tuple, Any
from langchain_core.tools import tool
import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

class TokenPriceAPI:
    """API wrapper for fetching token price data."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        # Using CoinGecko public API for demonstration
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
                    # Exponential backoff: 2^attempt * 1 seconds (2, 4, 8 seconds)
                    wait_time = 2 ** attempt * 1
                    print(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                raise
    
    def get_price(self, token_id: str) -> float:
        """Get current price of a token."""
        url = f"{self.base_url}/simple/price"
        params = {
            "ids": token_id,
            "vs_currencies": "usd"
        }
        response = self._make_request_with_retry(url, params)
        return response.json()[token_id]["usd"]
    
    def get_historical_prices(self, token_id: str, days: int = 30) -> List[Dict]:
        """Get historical price data for a token."""
        url = f"{self.base_url}/coins/{token_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days
        }
        response = self._make_request_with_retry(url, params)
        return response.json()["prices"]

class MeanReversionCalculator:
    """Calculator for mean reversion metrics."""
    
    @staticmethod
    def calculate_z_score(prices: List[float], window: int = 10) -> float:
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
    def calculate_rsi(prices: List[float], window: int = 10) -> float:
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
    def calculate_bollinger_bands(prices: List[float], window: int = 10, num_std: float = 2.0) -> Dict[str, float]:
        """
        Calculate Bollinger Bands.
        Middle Band = 10-day SMA
        Upper Band = Middle Band + (10-day std_dev * 2)
        Lower Band = Middle Band - (10-day std_dev * 2)
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

# Create the LangChain tools
@tool
def get_token_price(token_id: str) -> float:
    """
    Get the current price of a cryptocurrency token in USD.
    
    Args:
        token_id: The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')
    
    Returns:
        The current price of the token in USD.
    """
    api = TokenPriceAPI()
    return api.get_price(token_id)

@tool
def get_token_z_score(token_id: str, window: int = 10) -> float:
    """
    Calculate the Z-score for a token to determine how many standard deviations
    the current price is from the moving average.
    
    Args:
        token_id: The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')
        window: The number of days to use for calculating the moving average and standard deviation (default: 10)
    
    Returns:
        The Z-score value. Positive values indicate the price is above the mean, 
        negative values indicate it's below the mean.
    """
    api = TokenPriceAPI()
    historical_data = api.get_historical_prices(token_id, days=10)
    prices = [price[1] for price in historical_data]
    
    calculator = MeanReversionCalculator()
    return calculator.calculate_z_score(prices, window=window)

@tool
def get_token_rsi(token_id: str, window: int = 10) -> float:
    """
    Calculate the Relative Strength Index (RSI) for a token.
    
    Args:
        token_id: The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')
        window: The number of days to use for the RSI calculation (default: 10)
    
    Returns:
        The RSI value (0-100). Values above 70 generally indicate overbought conditions,
        while values below 30 indicate oversold conditions.
    """
    api = TokenPriceAPI()
    historical_data = api.get_historical_prices(token_id, days=10)
    prices = [price[1] for price in historical_data]
    
    calculator = MeanReversionCalculator()
    return calculator.calculate_rsi(prices, window=window)

@tool(response_format="content_and_artifact")
def get_token_bollinger_bands(token_id: str, window: int = 10, num_std: float = 2.0) -> Tuple[str, Dict[str, Any]]:
    """
    Calculate Bollinger Bands for a token and determine if it's in a mean reversion zone.
    
    Args:
        token_id: The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')
        window: The number of days to use for calculations (default: 10)
        num_std: Number of standard deviations for the bands (default: 2.0)
    
    Returns:
        Analysis of the token's position relative to Bollinger Bands and mean reversion potential.
    """
    api = TokenPriceAPI()
    historical_data = api.get_historical_prices(token_id, days=10)
    prices = [price[1] for price in historical_data]
    dates = [datetime.fromtimestamp(price[0]/1000).strftime('%Y-%m-%d') for price in historical_data]
    
    calculator = MeanReversionCalculator()
    bb_data = calculator.calculate_bollinger_bands(prices, window=window, num_std=num_std)
    
    # Create a DataFrame for visualization
    df = pd.DataFrame({
        'Date': dates,
        'Price': prices
    })
    
    # Prepare analysis message
    current_price = bb_data["current_price"]
    upper_band = bb_data["upper_band"]
    lower_band = bb_data["lower_band"]
    percent_b = bb_data["percent_b"]
    
    if current_price > upper_band:
        mean_reversion_msg = "The token is currently ABOVE the upper Bollinger Band, suggesting it may be OVERVALUED and due for a potential DOWNWARD mean reversion."
    elif current_price < lower_band:
        mean_reversion_msg = "The token is currently BELOW the lower Bollinger Band, suggesting it may be UNDERVALUED and due for a potential UPWARD mean reversion."
    else:
        mean_reversion_msg = f"The token is currently WITHIN the Bollinger Bands (percent B: {percent_b:.2f}), suggesting it is trading within normal volatility range."
    
    message = f"""
Token: {token_id.upper()}
Current Price: ${current_price:.2f}
Bollinger Bands (window: {window}, std: {num_std}):
- Upper Band: ${upper_band:.2f}
- Middle Band: ${bb_data["middle_band"]:.2f}
- Lower Band: ${lower_band:.2f}
Percent B: {percent_b:.2f}

Analysis: {mean_reversion_msg}
"""
    
    # Return both the text message and the data as artifact
    return message, {
        "token_id": token_id,
        "data": bb_data,
        "dates": dates,
        "prices": prices,
        "percent_b": percent_b
    }

@tool
def mean_reversion_analyzer(token_id: str) -> str:
    """
    Comprehensive mean reversion analysis for a cryptocurrency token.
    This tool combines multiple technical indicators to provide a holistic view.
    
    Args:
        token_id: The ID of the token (e.g., 'bitcoin', 'ethereum', 'solana')
    
    Returns:
        A comprehensive analysis of the token's mean reversion potential.
    """
    try:
        # Get current price
        api = TokenPriceAPI()
        current_price = api.get_price(token_id)
        
        # Get historical data for the past 10 days
        historical_data = api.get_historical_prices(token_id, days=10)
        prices = [price[1] for price in historical_data]
        
        # Calculate metrics
        calculator = MeanReversionCalculator()
        z_score = calculator.calculate_z_score(prices, window=10)
        rsi = calculator.calculate_rsi(prices, window=10)
        bb_data = calculator.calculate_bollinger_bands(prices, window=10)
        
        # Determine mean reversion signals
        z_signal = "NEUTRAL"
        if z_score > 2.0:
            z_signal = "POTENTIAL DOWNWARD REVERSION (Overvalued)"
        elif z_score < -2.0:
            z_signal = "POTENTIAL UPWARD REVERSION (Undervalued)"
        
        rsi_signal = "NEUTRAL"
        if rsi > 70:
            rsi_signal = "POTENTIAL DOWNWARD REVERSION (Overbought)"
        elif rsi < 30:
            rsi_signal = "POTENTIAL UPWARD REVERSION (Oversold)"
        
        bb_signal = "NEUTRAL"
        percent_b = bb_data["percent_b"]
        if percent_b > 1:
            bb_signal = "POTENTIAL DOWNWARD REVERSION (Above Upper Band)"
        elif percent_b < 0:
            bb_signal = "POTENTIAL UPWARD REVERSION (Below Lower Band)"
        
        # Combine signals for overall recommendation
        signals = [z_signal, rsi_signal, bb_signal]
        upward_signals = sum(1 for s in signals if "UPWARD" in s)
        downward_signals = sum(1 for s in signals if "DOWNWARD" in s)
        
        overall_signal = "NEUTRAL"
        if upward_signals > downward_signals:
            overall_signal = "POTENTIAL UPWARD REVERSION"
        elif downward_signals > upward_signals:
            overall_signal = "POTENTIAL DOWNWARD REVERSION"
        
        # Format the message
        message = f"""
=== MEAN REVERSION ANALYSIS FOR {token_id.upper()} ===
Based on the last 10 days of price data

Current Price: ${current_price:.2f}

TECHNICAL INDICATORS:
1. Z-Score: {z_score:.2f} - {z_signal}
   (Measures how many standard deviations the price is from its 10-day mean)

2. RSI: {rsi:.2f} - {rsi_signal}
   (Measures the speed and change of price movements, range 0-100)

3. Bollinger Bands:
   - Upper Band: ${bb_data["upper_band"]:.2f}
   - Middle Band: ${bb_data["middle_band"]:.2f}
   - Lower Band: ${bb_data["lower_band"]:.2f}
   - Percent B: {percent_b:.2f} - {bb_signal}
   (Measures price relative to Bollinger Bands)

OVERALL SIGNAL: {overall_signal}

Note: This analysis is based on mean reversion principles using 10-day historical data.
Mean reversion strategies assume that prices tend to move back toward their mean over time.
"""
        return message
    except Exception as e:
        return f"Error analyzing token {token_id}: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Example of using the tools directly
    token = "bitcoin"
    price = get_token_price.invoke({"token_id": token})
    print(f"Current price of {token}: ${price}")
    
    analysis = mean_reversion_analyzer.invoke({"token_id": token})
    print(analysis)