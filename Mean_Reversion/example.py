"""
Example script demonstrating the use of crypto mean reversion tools
with LangChain chat models.

Note: All data fetching and mean reversion calculations are limited to the past 10 days.
"""
import os
import time
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools.render import format_tool_to_openai_function
from langchain.schema import SystemMessage, HumanMessage

from ETHDenver2025.Mean_Reversion.token_price_tool import (
    get_token_price, 
    get_token_z_score, 
    get_token_rsi,
    get_token_bollinger_bands, 
    mean_reversion_analyzer
)

def main():
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

if __name__ == "__main__":
    # Run the direct tool usage demo
    demo_direct_tool_usage()
    
    # Run the interactive agent
    # main() 