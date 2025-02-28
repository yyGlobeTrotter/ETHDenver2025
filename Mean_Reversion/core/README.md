# Mean Reversion Core Modules

This directory contains the core functionality for the Mean Reversion trading strategy tools.

## Module Overview

### `api.py`

The API module provides a unified interface for fetching cryptocurrency price data.

- `TokenPriceAPI`: A class for fetching token price data with efficient caching mechanism
  - Handles API rate limiting with exponential backoff
  - Implements caching to avoid repeated requests
  - Provides methods for current and historical price data

### `indicators.py`

The indicators module implements all the technical indicators used for mean reversion analysis.

- `MeanReversionIndicators`: Class containing the core calculation methods
  - `calculate_z_score`: Calculates Z-score for measuring deviation from mean
  - `calculate_rsi`: Calculates Relative Strength Index
  - `calculate_bollinger_bands`: Calculates Bollinger Bands and %B
  - Various interpretation methods for each indicator

- `MeanReversionService`: High-level service combining API and calculations
  - `get_all_metrics`: Get comprehensive metrics for a token
  - `get_risk_metrics`: Get focused risk metrics for integration
  - `get_historical_indicators`: Get indicators over a historical time period

## Usage

```python
from core.api import TokenPriceAPI
from core.indicators import MeanReversionService

# Initialize the service
service = MeanReversionService()

# Get complete metrics for a token
metrics = service.get_all_metrics("bitcoin")

# Get historical indicators
historical = service.get_historical_indicators("ethereum", days=30, window=20)
```

## Integration

These core modules are used by the LangChain tools in the `tools/` directory to provide a user-friendly interface for agents and chat models.