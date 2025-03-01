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
    llm = ChatOpenAI(model="gpt-4o-mini")

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

    custom_tool = [
        MultiplyTool(),
        get_token_price,
        get_token_z_score,
        get_token_rsi,
        get_token_bollinger_bands,
        mean_reversion_analyzer,
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
            "You are a helpful agent that can interact onchain using the Coinbase Developer Platform AgentKit. "
            "You are empowered to interact onchain using your tools. If you ever need funds, you can request "
            "them from the faucet if you are on network ID 'base-sepolia'. If not, you can provide your wallet "
            "details and request funds from the user. Before executing your first action, get the wallet details "
            "to see what network you're on. If there is a 5XX (internal) HTTP error code, ask the user to try "
            "again later. If someone asks you to do something you can't do with your currently available tools, "
            "you must say so, and encourage them to implement it themselves using the CDP SDK + Agentkit, "
            "recommend they go to docs.cdp.coinbase.com for more information. Be concise and helpful with your "
            "responses. Refrain from restating your tools' descriptions unless it is explicitly requested."
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
