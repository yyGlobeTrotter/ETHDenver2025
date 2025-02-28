# Mean Reversion LangChain Tools

This directory contains LangChain tool implementations for the Mean Reversion trading strategy tools.

## Module Overview

### `langchain_tools.py`

This module provides LangChain tools for cryptocurrency technical analysis and mean reversion strategies.

- Basic tools:
  - `get_token_price`: Get current price of a token
  - `get_token_z_score`: Calculate the Z-score for a token
  - `get_token_rsi`: Calculate the RSI for a token
  - `get_token_bollinger_bands`: Calculate Bollinger Bands with analysis

- Advanced tools:
  - `get_token_indicators`: Get comprehensive technical indicators
  - `get_advanced_indicators`: Get indicators with both human-readable and structured data
  - `get_historical_indicators`: Get historical indicators over time
  - `mean_reversion_analyzer`: Comprehensive mean reversion analysis

## Features

- **Error Handling**: All tools include proper error handling for API failures
- **Content and Artifact**: Some tools return both human-readable text and structured data
- **Detailed Documentation**: Each tool includes detailed parameter descriptions
- **Interpretation**: Tools provide analysis and interpretation of indicators

## Usage

```python
from tools.langchain_tools import get_token_indicators, get_advanced_indicators

# Get basic indicators
result = get_token_indicators("bitcoin")
print(result)

# Get advanced indicators with structured data
message, data = get_advanced_indicators("ethereum")
print(message)
print(f"Z-Score: {data['metrics']['z_score']['value']}")
```

## Integration with LangChain

These tools can be used directly with LangChain agents:

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.render import format_tool_to_openai_function
from langchain.schema import SystemMessage

# Import tools
from tools.langchain_tools import get_token_indicators, get_historical_indicators

# Define the tools to use
tools = [get_token_indicators, get_historical_indicators]

# Convert tools to functions
functions = [format_tool_to_openai_function(t) for t in tools]

# Create the agent
system_message = SystemMessage(content="You are a crypto analysis assistant...")
agent = create_tool_calling_agent(llm, tools, system_message)
agent_executor = AgentExecutor(agent=agent, tools=tools)
```