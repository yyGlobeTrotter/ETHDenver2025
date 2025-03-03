# Using the Code to Get RSI, Bollinger Bands, and Mean Reversion Signal

There are a few ways to get these indicators for a given token, depending on whether you want to use the direct API or the LangChain tools. Here are the simplest approaches:

## Option 1: Direct API Usage

```python
from ETHDenver2025.Mean_Reversion.core.indicators import MeanReversionService

# Initialize the service
service = MeanReversionService()

# Get all indicators for a token (includes RSI, Bollinger Bands, and more)
token_id = "bitcoin"  # or "ethereum", "solana", etc.
indicators = service.get_all_indicators(token_id)

# Extract the specific indicators you want
rsi = indicators['indicators']['rsi']['value']
bollinger_percent_b = indicators['indicators']['bollinger_bands']['percent_b']
upper_band = indicators['indicators']['bollinger_bands']['upper_band']
lower_band = indicators['indicators']['bollinger_bands']['lower_band']

# Get the mean reversion signal
signal = indicators['indicators']['z_score']['signal']  # "BUY", "SELL", or "HOLD"

# Print the results
print(f"RSI: {rsi:.2f}")
print(f"Bollinger %B: {bollinger_percent_b:.2f}")
print(f"Mean Reversion Signal: {signal}")
```

## Option 2: Using LangChain Tools

```python
from ETHDenver2025.Mean_Reversion.tools.langchain_tools import (
    get_token_rsi,
    get_token_bollinger_bands,
    get_token_mean_reversion_signal
)

# Get RSI for a token
token_id = "bitcoin"
rsi = get_token_rsi.invoke({"token_id": token_id})
print(f"RSI: {rsi:.2f}")

# Get Bollinger Bands for a token
bollinger_info = get_token_bollinger_bands.invoke({"token_id": token_id})
print(bollinger_info)  # This returns a formatted string with all Bollinger Band info

# Get Mean Reversion Signal for a token
signal = get_token_mean_reversion_signal.invoke({"token_id": token_id})
print(f"Mean Reversion Signal: {signal}")
```

## Option 3: All-in-One Analysis

For a comprehensive analysis that includes all these indicators in one call:

```python
from ETHDenver2025.Mean_Reversion.tools.langchain_tools import get_advanced_indicators

# Get comprehensive analysis with all indicators
token_id = "bitcoin"
message, data = get_advanced_indicators.invoke({"token_id": token_id})

# The message contains a human-readable analysis
print(message)

# The data contains structured information you can extract
rsi = data['metrics']['rsi']['value']
bollinger_percent_b = data['metrics']['bollinger_bands']['percent_b']
signal = data['metrics']['z_score']['signal']

print(f"RSI: {rsi:.2f}")
print(f"Bollinger %B: {bollinger_percent_b:.2f}")
print(f"Mean Reversion Signal: {signal}")
```

## Simple One-Line Example

If you just want the simplest possible code to get these indicators:

```python
from ETHDenver2025.Mean_Reversion.core.indicators import MeanReversionService

# One-liner to get RSI, Bollinger %B, and signal for a token
token_id = "bitcoin"
result = MeanReversionService().get_all_indicators(token_id)
print(f"RSI: {result['indicators']['rsi']['value']:.2f}, Bollinger %B: {result['indicators']['bollinger_bands']['percent_b']:.2f}, Signal: {result['indicators']['z_score']['signal']}")
```
