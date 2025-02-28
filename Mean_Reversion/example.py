"""
Example script demonstrating the use of crypto mean reversion tools
with LangChain chat models.

This updated version showcases both the original tools and the enhanced
technical indicators with advanced LangChain features like error handling,
content_and_artifact responses, and detailed parameter schemas.
"""
import os
import time
from typing import List, Dict

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.render import format_tool_to_openai_function
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.messages.tool import ToolMessage

# Import all tools from the consolidated structure
from ETHDenver2025.Mean_Reversion.tools.langchain_tools import (
    get_token_price, 
    get_token_z_score, 
    get_token_rsi,
    get_token_bollinger_bands, 
    mean_reversion_analyzer,
    get_token_indicators,
    get_advanced_indicators,
    get_historical_indicators
)

def main():
    """
    Run the original agent with basic tools.
    All data fetching and calculations are limited to the past 10 days.
    """
    # Get API key from environment variable
    # Set this in your environment or .env file before running
    os.environ.setdefault("OPENAI_API_KEY", "")  # Default to empty string if not set
    
    # Define the tools to use
    tools = [
        get_token_price,
        get_token_z_score,
        get_token_rsi,
        get_token_bollinger_bands,
        mean_reversion_analyzer
    ]

    # Convert tools to functions for OpenAI function calling
    functions = [format_tool_to_openai_function(t) for t in tools]
    
    # Create system message
    system_message = SystemMessage(
        content="""You are a crypto trading assistant. 
        You have access to tools that can analyze cryptocurrency prices and calculate mean reversion metrics.
        All data fetching and calculations are limited to the past 10 days.
        Use these tools to help users make informed trading decisions based on technical analysis.
        Always remind users that your analysis is for informational purposes only and not financial advice."""
    )
    
    print("🚀 Initializing the crypto trading assistant...")
    
    # Initialize the LLM with function calling capability
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
        functions=functions
    )
    
    # Create the agent
    agent = create_tool_calling_agent(llm, tools, system_message)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    print("\n✅ Agent ready!")
    print("Ask questions about cryptocurrency prices and mean reversion analysis.")
    print("Example: 'What's the current price of Ethereum?' or 'Is Bitcoin due for a reversal?'")
    print("Note: All analysis is based on the past 10 days of data.")
    print("Type 'exit' to quit.\n")
    
    # Interactive session
    while True:
        user_input = input("👤 You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("👋 Goodbye!")
            break
        
        print("\n🤖 Assistant: Analyzing...")
        try:
            result = agent_executor.invoke({"input": user_input})
            print(f"\n🤖 Assistant: {result['output']}")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        print("\n" + "-" * 50 + "\n")

def create_enhanced_agent():
    """
    Create a LangChain agent with our enhanced technical indicator tools.
    These tools incorporate advanced LangChain features like error handling
    and content_and_artifact responses.
    """
    # Define the tools to use
    tools = [
        get_token_indicators,
        get_advanced_indicators,
        get_historical_indicators
    ]
    
    # Convert tools to functions for OpenAI function calling
    functions = [format_tool_to_openai_function(t) for t in tools]
    
    # Create system message with enhanced capabilities explanation
    system_message = SystemMessage(
        content="""You are a crypto analysis assistant with access to enhanced technical indicators.
        
Your tools have the following advanced capabilities:
1. Error handling: You can handle API errors and provide helpful fallback responses.
2. Content and artifact responses: Some tools return both human-readable text and structured data.
3. Detailed schema information: Tools have well-defined parameters with descriptions.

When analyzing cryptocurrencies:
- Provide insights based on multiple technical indicators (Z-score, RSI, Bollinger Bands)
- Explain what the indicators mean and how they can be interpreted
- Be clear about the timeframes used in the analysis (default is 10-day window)
- Remind users that technical analysis is based on historical patterns
- Avoid making specific financial recommendations
- When errors occur, explain them in user-friendly terms
"""
    )
    
    # Initialize the LLM with function calling capability
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable is not set.")
        print("Please set it to use the LLM functionality.")
    
    # Initialize ChatGPT model
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=api_key,
        functions=functions
    )
    
    # Create the agent
    agent = create_tool_calling_agent(llm, tools, system_message)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

def run_enhanced_agent():
    """Run an interactive session with the enhanced agent."""
    agent_executor = create_enhanced_agent()
    
    print("\n🤖 Enhanced Crypto Technical Analysis Agent")
    print("Ask about technical indicators, mean reversion signals, or historical trends for any cryptocurrency.")
    print("This agent uses enhanced tools with error handling and structured data responses.")
    print("Type 'exit' to quit.\n")
    
    # Interactive loop
    while True:
        user_input = input("👤 You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("👋 Goodbye!")
            break
        
        print("\n🔍 Analyzing...")
        try:
            result = agent_executor.invoke({"input": user_input})
            print(f"\n🤖 Assistant: {result['output']}")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        print("\n" + "-" * 50 + "\n")

def demo_enhanced_examples():
    """Demonstrate predefined examples with the enhanced agent."""
    agent_executor = create_enhanced_agent()
    
    example_questions = [
        "What are the current technical indicators for Ethereum?",
        "Is Bitcoin showing mean reversion signals based on recent data?",
        "What do the historical indicators for Bitcoin show over the last 5 days?",
        "What does a Bollinger %B value of 1.2 mean for Ethereum?"
    ]
    
    print("\n🤖 CRYPTO TECHNICAL ANALYSIS AGENT - EXAMPLES")
    print("=" * 80)
    
    for i, question in enumerate(example_questions, 1):
        print(f"\nExample {i}: \"{question}\"")
        print("-" * 80)
        
        try:
            result = agent_executor.invoke({"input": question})
            print(f"\n🤖 Response: {result['output']}")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        print("\n" + "=" * 80)
        
        # Add delay between examples to avoid rate limiting
        if i < len(example_questions):
            print("Waiting a moment before the next example...")
            time.sleep(5)

def demo_enhanced_error_handling():
    """Demonstrate the error handling capabilities of the enhanced agent."""
    agent_executor = create_enhanced_agent()
    
    print("\n🤖 DEMONSTRATING ERROR HANDLING")
    print("=" * 80)
    
    # Example with non-existent token
    question = "What are the technical indicators for dogecoin123xyz?"
    
    print(f"\nQuery with invalid token: \"{question}\"")
    print("-" * 80)
    
    try:
        result = agent_executor.invoke({"input": question})
        print(f"\n🤖 Response: {result['output']}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)

def demo_content_and_artifact():
    """Demonstrate content_and_artifact responses with the enhanced agent."""
    agent_executor = create_enhanced_agent()
    
    print("\n🤖 DEMONSTRATING CONTENT AND ARTIFACT RESPONSES")
    print("=" * 80)
    
    question = "Give me a detailed technical analysis of Ethereum and explain what insights I can get from the data."
    
    print(f"\nQuery: \"{question}\"")
    print("-" * 80)
    
    try:
        result = agent_executor.invoke({"input": question})
        
        # Extract the message chain to inspect the ToolMessage artifacts
        messages = result.get("intermediate_steps", [])
        
        print(f"\n🤖 Response: {result['output']}")
        
        # Look for any ToolMessages with artifacts in the message chain
        print("\nChecking for artifact data in the responses...")
        for action, message in messages:
            if isinstance(message, ToolMessage) and hasattr(message, "artifact") and message.artifact:
                print(f"\n✅ Found artifact data from tool: {message.name}")
                if message.name == "get_advanced_indicators":
                    data = message.artifact
                    print(f"Token: {data['token_id']}")
                    print(f"Current price: ${data['current_price']:.2f}")
                    print(f"Z-Score: {data['indicators']['z_score']['value']:.2f}")
                    print(f"RSI: {data['indicators']['rsi']['value']:.2f}")
                    print(f"Bollinger %B: {data['indicators']['bollinger_bands']['percent_b']:.2f}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)

def demo_direct_tool_usage():
    """
    Demonstrate using the tools directly without an agent.
    All data fetching and calculations are limited to the past 10 days.
    """
    # Get API key from environment variable
    # Set this in your environment or .env file before running
    os.environ.setdefault("OPENAI_API_KEY", "")  # Default to empty string if not set
    
    print("🔍 Direct Tool Usage Demo (using 10-day data):\n")
    
    tokens = ["bitcoin", "ethereum", "solana"]
    
    for token in tokens:
        print(f"📊 Analysis for {token.upper()} (past 10 days):")
        
        # Get current price
        try:
            price = get_token_price.invoke({"token_id": token})
            print(f"Current price: ${price:.2f}")
            
            # Add longer delay to avoid rate limiting
            time.sleep(5)
            
            # Get Z-Score
            z_score = get_token_z_score.invoke({"token_id": token})
            print(f"Z-Score (10-day window): {z_score:.2f}")
            
            # Add longer delay to avoid rate limiting
            time.sleep(5)
            
            # Get RSI
            rsi = get_token_rsi.invoke({"token_id": token})
            print(f"RSI (10-day window): {rsi:.2f}")
            
            # Add delay to avoid rate limiting
            time.sleep(1)
            
            # Get Bollinger Bands info (with artifact)
            result = get_token_bollinger_bands.invoke({"token_id": token})
            # Handle both tuple unpacking and direct result
            if isinstance(result, tuple) and len(result) == 2:
                message, artifact = result
            else:
                message = result
            print("\nBollinger Bands Analysis (10-day window):")
            print(message)
            
            # Add longer delay to avoid rate limiting
            time.sleep(5)
            
            # Full analysis
            print("\nComprehensive Analysis (10-day window):")
            analysis = mean_reversion_analyzer.invoke({"token_id": token})
            print(analysis)
            
        except Exception as e:
            print(f"Error analyzing {token}: {str(e)}")
        
        print("\n" + "=" * 50 + "\n")
        # Add substantial delay between tokens to avoid rate limiting
        time.sleep(10)

def demo_enhanced_direct_tool_usage():
    """
    Demonstrate using the enhanced tools directly without an agent.
    This showcases the error handling and content_and_artifact features.
    """
    print("🔍 Enhanced Direct Tool Usage Demo:\n")
    
    tokens = ["bitcoin", "ethereum"]
    
    for token in tokens:
        print(f"📊 Enhanced Analysis for {token.upper()}:")
        
        try:
            # Basic indicators with error handling
            print("\nBasic Indicators:")
            basic_result = get_token_indicators(token)
            print(basic_result)
            
            # Add delay to avoid rate limiting
            time.sleep(3)
            
            # Advanced indicators with content and artifact
            print("\nAdvanced Indicators (with content and artifact):")
            message, data = get_advanced_indicators(token)
            print("Human-readable content:")
            print(message)
            print("\nStructured data highlights:")
            print(f"Current price: ${data['current_price']:.2f}")
            print(f"Overall sentiment: {data['indicators']['z_score']['signal']}")
            
            # Add delay to avoid rate limiting
            time.sleep(3)
            
            # Historical indicators with custom error handling
            print("\nHistorical Indicators (5 days):")
            historical = get_historical_indicators(token, days=5)
            print(historical)
            
        except Exception as e:
            print(f"Error analyzing {token}: {str(e)}")
        
        print("\n" + "=" * 50 + "\n")
        # Add substantial delay between tokens to avoid rate limiting
        time.sleep(5)

if __name__ == "__main__":
    print("CRYPTO TRADING STRATEGY TOOLS EXAMPLES")
    print("======================================")
    print("\nThis script demonstrates both the original tools and")
    print("the enhanced technical indicator tools with advanced LangChain features.")
    print("\nChoose which demo to run by uncommenting the appropriate function call below.")
    
    # Original functionality
    # demo_direct_tool_usage()
    # main()
    
    # Enhanced functionality 
    # demo_enhanced_direct_tool_usage()
    # run_enhanced_agent()
    # demo_enhanced_examples()
    # demo_enhanced_error_handling()
    # demo_content_and_artifact()
    
    # By default, run the enhanced examples
    demo_enhanced_examples() 