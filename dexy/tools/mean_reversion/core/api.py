"""
Core API module for cryptocurrency price data.
This module provides a unified API interface for fetching cryptocurrency price data.
It includes efficient caching mechanisms and robust error handling.
"""

from typing import Dict, List, Optional, Union, Tuple, Any
import requests
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('crypto_api')

class TokenPriceAPI:
    """Efficient API wrapper for fetching token price data with caching."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            api_key: Optional API key for price data provider
            base_url: Optional custom URL for price data provider
        """
        self.api_key = api_key
        # Default to CoinGecko, but allow override
        self.base_url = base_url or "https://api.coingecko.com/api/v3"
        self._cache = {}  # Simple cache to avoid repeated requests
    
    def _get_cache_key(self, token_id: str, days: int) -> str:
        """Generate a cache key for historical data."""
        return f"{token_id}_{days}"
    
    def _make_request_with_retry(self, url: str, params: Dict = None, max_retries: int = 3) -> requests.Response:
        """Make a request with retry logic for rate limiting."""
        params = params or {}
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and attempt < max_retries - 1:  # Too Many Requests
                    # Exponential backoff: 2^attempt * 1 seconds (2, 4, 8 seconds)
                    wait_time = 2 ** attempt * 1
                    logger.warning(f"Rate limit hit. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                logger.error(f"HTTP error: {e}")
                raise
            except Exception as e:
                logger.error(f"Request error: {e}")
                raise
    
    def get_price(self, token_id: str) -> float:
        """Get current price of a token."""
        url = f"{self.base_url}/simple/price"
        params = {
            "ids": token_id,
            "vs_currencies": "usd"
        }
        try:
            response = self._make_request_with_retry(url, params)
            return response.json()[token_id]["usd"]
        except KeyError:
            logger.error(f"Invalid token ID: {token_id}")
            raise ValueError(f"Invalid token ID: {token_id}")
    
    def get_historical_prices(self, token_id: str, days: int = 30) -> Tuple[List[float], List[str]]:
        """
        Get historical price data for a token.
        
        Args:
            token_id: The ID of the token (e.g., 'bitcoin', 'ethereum')
            days: Number of days of historical data to fetch
            
        Returns:
            Tuple containing (prices, dates)
        """
        cache_key = self._get_cache_key(token_id, days)
        
        # Check if we have this data cached
        if cache_key in self._cache:
            logger.info(f"Using cached data for {token_id}, {days} days")
            return self._cache[cache_key]
        
        url = f"{self.base_url}/coins/{token_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days
        }
        
        try:
            response = self._make_request_with_retry(url, params)
            historical_data = response.json()["prices"]
            
            # Extract prices and dates
            prices = [price[1] for price in historical_data]
            dates = [datetime.fromtimestamp(price[0]/1000).strftime('%Y-%m-%dT%H:%M:%SZ') for price in historical_data]
            
            # Cache the results
            self._cache[cache_key] = (prices, dates)
            
            return prices, dates
        except Exception as e:
            logger.error(f"Failed to get historical prices for {token_id}: {e}")
            raise
            
    def get_price_with_format(self, token_id: str, error_msg: str = None) -> float:
        """Get current price with LangChain-friendly error handling."""
        try:
            return self.get_price(token_id)
        except Exception as e:
            error = error_msg or f"Error fetching price for {token_id}: {str(e)}"
            logger.error(error)
            # Re-raise the error with a more descriptive message
            # This allows LangChain tools to properly handle the error
            raise ValueError(error)