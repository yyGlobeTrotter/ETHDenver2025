# Mean Reversion Trading Strategy Tools

This project provides a set of tools for analyzing cryptocurrency price data and identifying mean reversion opportunities.

## Structure

The project has been reorganized into a more maintainable structure:

```
Mean_Reversion/
├── core/             - Core functionality
│   ├── api.py        - API client for price data
│   └── indicators.py - Technical indicator calculations
├── tools/            - Tool integrations
│   └── langchain_tools.py - LangChain tool wrappers
├── token_price_tool.py - Legacy API wrapper (for compatibility)
├── example.py        - Example usage
└── test_indicators.py - Test script
```

## Features

- Fetch cryptocurrency price data from public APIs
- Calculate technical indicators:
  - Z-score (deviation from mean)
  - RSI (Relative Strength Index)
  - Bollinger Bands
- Identify mean reversion opportunities
- LangChain integration for AI agents
- Historical analysis capabilities

## Getting Started

### Prerequisites

```
pip install requests pandas numpy langchain-core
```

### Basic Usage

```python
from core.api import TokenPriceAPI
from core.indicators import MeanReversionService

# Initialize the service
service = MeanReversionService()

# Get metrics for a token
metrics = service.get_all_metrics("bitcoin")
print(f"Bitcoin Z-Score: {metrics['metrics']['z_score']['value']}")
print(f"Bitcoin RSI: {metrics['metrics']['rsi']['value']}")
```

### Using with LangChain

```python
from tools.langchain_tools import get_token_indicators

# Get indicators directly
result = get_token_indicators("ethereum")
print(result)

# Or use with a LangChain agent
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.render import format_tool_to_openai_function
from langchain.schema import SystemMessage

# Define your agent with the tools
# See example.py for a complete implementation
```

## Examples

See `example.py` for complete examples of using the tools directly and with LangChain agents.

## Code Consolidation

This project has recently undergone a code consolidation to reduce redundancy and improve maintainability. See `CONSOLIDATION_SUMMARY.md` for details.

## License

See the LICENSE file for details.