"""
Core API module for cryptocurrency price data.
This module provides a unified API interface for fetching cryptocurrency price data.
It includes efficient caching mechanisms and robust error handling.
It supports CoinGecko, DeFi Llama, and CoinAPI for price data, including OHLC data.
"""

from typing import Dict, List, Optional, Union, Tuple, Any, NamedTuple
import requests
import time
from datetime import datetime, timedelta
import logging
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('crypto_api')

class OHLCData(NamedTuple):
    """Data class for OHLC candle data."""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0

class TokenPriceAPI:
    """Efficient API wrapper for fetching token price data with caching."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, api_provider: str = "defillama"):
        """
        Initialize the API client.
        
        Args:
            api_key: Optional API key for price data provider
            base_url: Optional custom URL for price data provider
            api_provider: The API provider to use (defillama, coingecko, or coinapi)
        """
        self.api_key = api_key
        self.api_provider = api_provider.lower()
        
        # Set default base URL based on provider
        if not base_url:
            if self.api_provider == "coingecko":
                self.base_url = "https://api.coingecko.com/api/v3"
            elif self.api_provider == "defillama":
                self.base_url = "https://coins.llama.fi"
            elif self.api_provider == "coinapi":
                self.base_url = "https://rest.coinapi.io/v1"
                # Use the provided API key or a default one
                self.api_key = api_key or "7015c46d-7184-4fe7-a989-26892b87db58"
            else:
                raise ValueError(f"Unsupported API provider: {api_provider}. Use 'defillama', 'coingecko', or 'coinapi'.")
        else:
            self.base_url = base_url
            
        self._cache = {}  # Simple cache to avoid repeated requests
        
        # Map of standard token IDs to CoinAPI symbols
        self.coinapi_symbol_map = {
            "bitcoin": "BITSTAMP_SPOT_BTC_USD",
            "ethereum": "BITSTAMP_SPOT_ETH_USD",
            "solana": "BITSTAMP_SPOT_SOL_USD",
            "cardano": "BITSTAMP_SPOT_ADA_USD",
            "ripple": "BITSTAMP_SPOT_XRP_USD",
            "dogecoin": "BINANCE_SPOT_DOGE_USDT",
            "polkadot": "BINANCE_SPOT_DOT_USDT",
        }
    
    def _get_cache_key(self, token_id: str, days: int) -> str:
        """Generate a cache key for historical data."""
        return f"{self.api_provider}_{token_id}_{days}"
    
    def _make_request_with_retry(self, url: str, params: Dict = None, headers: Dict = None, max_retries: int = 3) -> requests.Response:
        """Make a request with retry logic for rate limiting."""
        params = params or {}
        headers = headers or {}
        
        # Add API key to headers if using CoinAPI
        if self.api_provider == "coinapi" and self.api_key:
            headers["X-CoinAPI-Key"] = self.api_key
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=headers)
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
        if self.api_provider == "coingecko":
            return self._get_price_coingecko(token_id)
        elif self.api_provider == "defillama":
            return self._get_price_defillama(token_id)
        elif self.api_provider == "coinapi":
            return self._get_price_coinapi(token_id)
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")
    
    def _get_price_coingecko(self, token_id: str) -> float:
        """Get current price using CoinGecko API."""
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
    
    def _get_price_defillama(self, token_id: str) -> float:
        """Get current price using DeFi Llama API."""
        coins = f"coingecko:{token_id}"  # Use CoinGecko token ID with prefix
        url = f"{self.base_url}/prices/current/{coins}"
        try:
            response = self._make_request_with_retry(url)
            data = response.json()
            return data["coins"][coins]["price"]
        except KeyError:
            logger.error(f"Invalid token ID: {token_id}")
            raise ValueError(f"Invalid token ID: {token_id}")
            
    def _get_price_coinapi(self, token_id: str) -> float:
        """Get current price using CoinAPI."""
        # Get the latest OHLC data and use the close price
        try:
            ohlc_data = self.get_ohlc_data(token_id, limit=1)
            if not ohlc_data:
                raise ValueError(f"No OHLC data available for {token_id}")
            return ohlc_data[0].close
        except Exception as e:
            logger.error(f"Error fetching price from CoinAPI for {token_id}: {e}")
            raise ValueError(f"Error fetching price for {token_id}: {str(e)}")
    
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
        
        if self.api_provider == "coingecko":
            return self._get_historical_prices_coingecko(token_id, days, cache_key)
        elif self.api_provider == "defillama":
            return self._get_historical_prices_defillama(token_id, days, cache_key)
        elif self.api_provider == "coinapi":
            return self._get_historical_prices_coinapi(token_id, days, cache_key)
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")
    
    def _get_historical_prices_coingecko(self, token_id: str, days: int, cache_key: str) -> Tuple[List[float], List[str]]:
        """Get historical prices using CoinGecko API."""
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
    
    def _get_historical_prices_defillama(self, token_id: str, days: int, cache_key: str) -> Tuple[List[float], List[str]]:
        """Get historical prices using DeFi Llama API."""
        prices = []
        dates = []
        coins = f"coingecko:{token_id}"  # Use CoinGecko token ID with prefix
        
        try:
            for i in range(days):
                # Calculate timestamp for each day at midnight UTC
                date = (datetime.now() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
                timestamp = int(time.mktime(date.timetuple()))
                url = f"{self.base_url}/prices/historical/{timestamp}/{coins}"
                
                response = self._make_request_with_retry(url)
                data = response.json()
                price = data["coins"].get(coins, {}).get("price")
                
                if price is not None:
                    prices.append(price)
                    dates.append(date.strftime('%Y-%m-%dT%H:%M:%SZ'))
                
                # Add a small delay to avoid rate limiting
                if i < days - 1:  # No need to sleep after the last request
                    time.sleep(0.2)
            
            # Reverse to get oldest to newest
            prices = prices[::-1]
            dates = dates[::-1]
            
            # Cache the results
            self._cache[cache_key] = (prices, dates)
            
            return prices, dates
        except Exception as e:
            logger.error(f"Failed to get historical prices for {token_id} from DeFi Llama: {e}")
            raise
    
    def _get_historical_prices_coinapi(self, token_id: str, days: int, cache_key: str) -> Tuple[List[float], List[str]]:
        """Get historical prices using CoinAPI."""
        try:
            # Get OHLC data for the specified days
            ohlc_data = self.get_ohlc_data(token_id, period="1DAY", limit=days)
            
            if not ohlc_data:
                raise ValueError(f"No OHLC data available for {token_id}")
            
            # Extract closing prices and timestamps
            prices = [candle.close for candle in ohlc_data]
            dates = [candle.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ') for candle in ohlc_data]
            
            # Cache the results
            self._cache[cache_key] = (prices, dates)
            
            return prices, dates
        except Exception as e:
            logger.error(f"Failed to get historical prices for {token_id} from CoinAPI: {e}")
            raise
    
    def get_ohlc_data(self, token_id: str, period: str = "1DAY", limit: int = 30) -> List[OHLCData]:
        """
        Get OHLC (Open, High, Low, Close) candle data for a token.
        
        Args:
            token_id: The ID of the token (e.g., 'bitcoin', 'ethereum')
            period: Time period for each candle (e.g., '1DAY', '1HRS', '15MIN')
            limit: Number of candles to fetch
            
        Returns:
            List of OHLCData objects
        """
        cache_key = f"ohlc_{self.api_provider}_{token_id}_{period}_{limit}"
        
        # Check if we have this data cached
        if cache_key in self._cache:
            logger.info(f"Using cached OHLC data for {token_id}, {period} x {limit}")
            return self._cache[cache_key]
        
        # Check if this is a supported token for CoinAPI
        if token_id not in self.coinapi_symbol_map:
            raise ValueError(f"Unsupported token for OHLC data: {token_id}. Available tokens: {list(self.coinapi_symbol_map.keys())}")
        
        symbol = self.coinapi_symbol_map[token_id]
        url = f"{self.base_url}/ohlcv/{symbol}/history"
        
        params = {
            "period_id": period,
            "limit": limit
        }
        
        headers = {
            "Accept": "application/json",
            "X-CoinAPI-Key": self.api_key
        }
        
        try:
            response = self._make_request_with_retry(url, params, headers)
            data = response.json()
            
            if not data:
                return []
            
            # Parse the data into OHLCData objects
            ohlc_data = []
            for item in data:
                candle = OHLCData(
                    timestamp=datetime.fromisoformat(item["time_period_start"].replace("Z", "+00:00")),
                    open=float(item["price_open"]),
                    high=float(item["price_high"]),
                    low=float(item["price_low"]),
                    close=float(item["price_close"]),
                    volume=float(item.get("volume_traded", 0))
                )
                ohlc_data.append(candle)
            
            # Sort by timestamp (oldest first)
            ohlc_data.sort(key=lambda x: x.timestamp)
            
            # Cache the results
            self._cache[cache_key] = ohlc_data
            
            return ohlc_data
        except Exception as e:
            logger.error(f"Failed to get OHLC data for {token_id}: {e}")
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