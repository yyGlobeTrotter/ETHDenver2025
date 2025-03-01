import os
import sys
import json
import time

from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from langchain_community.agent_toolkits.load_tools import load_tools

from tools.multiply import MultiplyTool
from tools.mean_reversion import (
    get_token_price,
    get_token_z_score,
    get_token_rsi,
    get_token_bollinger_bands,
    mean_reversion_analyzer,
)
from tools.whalesignal import generate_risk_signals, get_risk_multiplier, apply_risk_multiplier


from coinbase_agentkit import (
    AgentKit,
    AgentKitConfig,
    CdpWalletProvider,
    CdpWalletProviderConfig,
    cdp_api_action_provider,
    cdp_wallet_action_provider,
    erc20_action_provider,
    pyth_action_provider,
    wallet_action_provider,
    weth_action_provider,
)
from coinbase_agentkit_langchain import get_langchain_tools

"""
AgentKit Integration

This file serves as the entry point for integrating AgentKit into your chatbot.  
It defines your AI agent, enabling you to  
customize its behavior, connect it to blockchain networks, and extend its functionality  
with additional tools and providers.

# Key Steps to Customize Your Agent:

1. Select your LLM:
   - Modify the `ChatOpenAI` instantiation to choose your preferred LLM.

2. Set up your WalletProvider:
   - Learn more: https://github.com/coinbase/agentkit/tree/main/python/agentkit#evm-wallet-providers

3. Set up your Action Providers:
   - Action Providers define what your agent can do.  
   - Choose from built-in providers or create your own:
     - Built-in: https://github.com/coinbase/agentkit/tree/main/python/coinbase-agentkit#create-an-agentkit-instance-with-specified-action-providers
     - Custom: https://github.com/coinbase/agentkit/tree/main/python/coinbase-agentkit#creating-an-action-provider

4. Instantiate your Agent:
   - Pass the LLM, tools, and memory into your agent's initialization function to bring it to life.

# Next Steps:

- Explore the AgentKit README: https://github.com/coinbase/agentkit
- Learn more about available WalletProviders & Action Providers.
- Experiment with custom Action Providers for your unique use case.

## Want to contribute?
Join us in shaping AgentKit! Check out the contribution guide:  
- https://github.com/coinbase/agentkit/blob/main/CONTRIBUTING.md
- https://discord.gg/CDP
"""

# Configure a file to persist the agent's CDP API Wallet Data.
wallet_data_file = "wallet_data.txt"

load_dotenv()


def initialize_agent():
    """Initialize the agent with CDP Agentkit."""

    # Initialize LLM: https://platform.openai.com/docs/models#gpt-4o
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ.get("OPENAI_API_KEY"))

    # Initialize WalletProvider: https://docs.cdp.coinbase.com/agentkit/docs/wallet-management
    wallet_data = None
    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            wallet_data = f.read()

    cdp_config = None
    if wallet_data is not None:
        cdp_config = CdpWalletProviderConfig(wallet_data=wallet_data)

    wallet_provider = CdpWalletProvider(cdp_config)

    # Initialize AgentKit: https://docs.cdp.coinbase.com/agentkit/docs/agent-actions
    agentkit = AgentKit(
        AgentKitConfig(
            wallet_provider=wallet_provider,
            action_providers=[
                cdp_wallet_action_provider(),
                cdp_api_action_provider(),
                erc20_action_provider(),
                pyth_action_provider(),
                wallet_action_provider(),
                weth_action_provider(),
            ],
        )
    )

    # Save wallet to file for reuse
    wallet_data_json = json.dumps(wallet_provider.export_wallet().to_dict())

    with open(wallet_data_file, "w") as f:
        f.write(wallet_data_json)

    # Create a custom whale signal tool
    from langchain.tools import tool
    
    @tool
    def integrated_crypto_analysis(token_id: str = "bitcoin") -> str:
        """
        Get integrated analysis combining mean reversion signals with whale dominance.
        
        Args:
            token_id: The cryptocurrency to analyze (e.g., 'bitcoin', 'ethereum')
            
        Returns:
            Detailed analysis with both technical indicators and whale activity
        """
        from tools.mean_reversion.core.api import TokenPriceAPI
        from tools.mean_reversion.core.indicators import MeanReversionIndicators, MeanReversionService
        
        try:
            # Get technical indicators
            service = MeanReversionService()
            metrics = service.get_all_metrics(token_id)
            
            # Extract key values
            current_price = metrics["current_price"]
            z_score = metrics["metrics"]["z_score"]["value"]
            z_signal = metrics["metrics"]["z_score"]["interpretation"]
            rsi = metrics["metrics"]["rsi"]["value"]
            rsi_signal = metrics["metrics"]["rsi"]["interpretation"]
            bb_data = metrics["metrics"]["bollinger_bands"]
            bb_signal = bb_data["interpretation"]
            percent_b = bb_data["percent_b"]
            
            # Calculate mean reversion score (simplified version)
            # Z-score contribution (negative z-score = positive signal)
            z_component = max(min(-z_score * 1.5, 5), -5)
            
            # RSI contribution
            if rsi <= 30:
                rsi_component = (30 - rsi) / 6  # 0 to 5 for RSI 30 to 0
            elif rsi >= 70:
                rsi_component = -(rsi - 70) / 6  # -5 to 0 for RSI 100 to 70
            else:
                rsi_component = 0
                
            # Bollinger Bands
            if percent_b <= 0:
                bb_component = min(abs(percent_b), 1) * 5  # 0 to 5
            elif percent_b >= 1:
                bb_component = -(percent_b - 1) * 5 if percent_b <= 2 else -5  # -5 to 0
            else:
                bb_component = -(percent_b - 0.5) * 10  # -5 to 5
                
            # Calculate mean reversion score (-10 to 10)
            mr_score = z_component + rsi_component + bb_component
            mr_score = max(min(mr_score, 10), -10)
            
            # Determine direction
            if mr_score > 5:
                direction = "STRONG UPWARD REVERSION POTENTIAL"
            elif mr_score > 0:
                direction = "MODERATE UPWARD REVERSION POTENTIAL"
            elif mr_score > -5:
                direction = "MODERATE DOWNWARD REVERSION POTENTIAL"
            else:
                direction = "STRONG DOWNWARD REVERSION POTENTIAL"
            
            # Get whale dominance signal
            risk_data = generate_risk_signals()
            risk_score = risk_data["risk_score"]
            risk_level = risk_data["level"]
            
            # Apply multiplier
            multiplier_data = apply_risk_multiplier(mr_score, risk_score)
            multiplier = multiplier_data["multiplier"]
            adjusted_score = multiplier_data["adjusted_value"]
            
            # Generate final analysis
            return f"""
=== INTEGRATED ANALYSIS FOR {token_id.upper()} ===

PRICE & TECHNICAL INDICATORS:
Current Price: ${current_price:.2f}
Z-Score: {z_score:.2f} - {z_signal}
RSI: {rsi:.2f} - {rsi_signal}
Bollinger %B: {percent_b:.2f} - {bb_signal}

MEAN REVERSION:
Mean Reversion Score: {mr_score:.2f}
Direction: {direction}

WHALE DOMINANCE ANALYSIS:
Risk Score: {risk_score} - {risk_level}
Risk Signals: {', '.join(risk_data['signals']) if risk_data['signals'] else 'No specific risk signals detected'}

INTEGRATED RESULT:
Risk Multiplier: {multiplier:.1f}x ({multiplier_data['explanation']})
Adjusted Score: {adjusted_score:.2f}
Final Signal: {'STRONGER' if abs(adjusted_score) > abs(mr_score) else 'UNCHANGED'} {direction}

RECOMMENDATION:
{f'Consider a stronger position due to significant whale activity' if multiplier > 1 else 'Proceed with standard position sizing based on technical indicators'}
            """
        except Exception as e:
            return f"Error analyzing {token_id}: {str(e)}"
    
    custom_tool = [
        MultiplyTool(),
        get_token_price,
        get_token_z_score,
        get_token_rsi,
        get_token_bollinger_bands,
        mean_reversion_analyzer,
        integrated_crypto_analysis,  # Add the new integrated tool
    ]

    # Transform agentkit configuration into langchain tools
    tools = get_langchain_tools(agentkit) + custom_tool

    # Store buffered conversation history in memory.
    memory = MemorySaver()

    config = {"configurable": {"thread_id": "CDP Agentkit Chatbot Example!"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools.
    return create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=(
            "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit "
            "and analyze cryptocurrencies using advanced strategies. You have two key capabilities:\n\n"
            
            "1. BLOCKCHAIN INTERACTION: You can interact onchain using your CDP tools. If you ever need funds, you can "
            "request them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
            "details and request funds from the user. Before executing your first action, get the wallet details "
            "to see what network you're on.\n\n"
            
            "2. CRYPTO ANALYSIS: You have integrated technical analysis capabilities that combine mean reversion signals "
            "with whale dominance indicators. For the most complete analysis, use the integrated_crypto_analysis tool, "
            "which provides a comprehensive view considering both technical indicators and whale activity.\n\n"
            
            "When asked about trading analysis or market conditions, prioritize using the integrated_crypto_analysis "
            "tool as it gives the most comprehensive view. If someone asks about specific technical indicators, "
            "you can use the individual tools (get_token_price, get_token_z_score, etc.).\n\n"
            
            "If there is a 5XX (internal) HTTP error code, ask the user to try again later. If someone asks you to do "
            "something you can't do with your currently available tools, you must say so, and encourage them to implement "
            "it themselves using the CDP SDK + Agentkit, recommend they go to docs.cdp.coinbase.com for more information. "
            "Be concise and helpful with your responses. Refrain from restating your tools' descriptions unless it is "
            "explicitly requested."
        ),
    ), config


# Autonomous Mode
def run_autonomous_mode(agent_executor, config, interval=10):
    """Run the agent autonomously with specified intervals."""
    print("Starting autonomous mode...")
    while True:
        try:
            # Provide instructions autonomously
            thought = (
                "Be creative and do something interesting on the blockchain. "
                "Choose an action or set of actions and execute it that highlights your abilities."
            )

            # Run agent in autonomous mode
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=thought)]}, config
            ):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

            # Wait before the next action
            time.sleep(interval)

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


# Chat Mode
def run_chat_mode(agent_executor, config):
    """Run the agent interactively based on user input."""
    print("Starting chat mode... Type 'exit' to end.")
    while True:
        try:
            user_input = input("\nPrompt: ")
            if user_input.lower() == "exit":
                break

            # Run agent with the user's input in chat mode
            for chunk in agent_executor.stream(
                {"messages": [HumanMessage(content=user_input)]}, config
            ):
                if "agent" in chunk:
                    print(chunk["agent"]["messages"][0].content)
                elif "tools" in chunk:
                    print(chunk["tools"]["messages"][0].content)
                print("-------------------")

        except KeyboardInterrupt:
            print("Goodbye Agent!")
            sys.exit(0)


# Mode Selection
def choose_mode():
    """Choose whether to run in autonomous or chat mode based on user input."""
    while True:
        print("\nAvailable modes:")
        print("1. chat    - Interactive chat mode")
        print("2. auto    - Autonomous action mode")

        choice = input("\nChoose a mode (enter number or name): ").lower().strip()
        if choice in ["1", "chat"]:
            return "chat"
        elif choice in ["2", "auto"]:
            return "auto"
        print("Invalid choice. Please try again.")


def main():
    """Start the chatbot agent."""
    agent_executor, config = initialize_agent()

    mode = choose_mode()
    if mode == "chat":
        run_chat_mode(agent_executor=agent_executor, config=config)
    elif mode == "auto":
        run_autonomous_mode(agent_executor=agent_executor, config=config)


if __name__ == "__main__":
    print("Starting Agent...")
    main()

from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize AgentKit
agent_executor, config = initialize_agent()

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "AgentKit is running"}), 200

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Get response from AgentKit
    response_text = ""
    for chunk in agent_executor.stream({"messages": [HumanMessage(content=user_message)]}, config):
        if "agent" in chunk:
            response_text = chunk["agent"]["messages"][0].content
        elif "tools" in chunk:
            response_text = chunk["tools"]["messages"][0].content

    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
