# Onchain Agent Powered by AgentKit

This is a Python chatbot project bootstrapped with `create-onchain-agent`.  
It integrates [AgentKit](https://github.com/coinbase/agentkit) to provide AI-driven interactions with on-chain capabilities.

## Prerequisites

Before using `create-onchain-agent`, ensure you have the following installed:

- **Python** (3.10 - 3.12) – [Download here](https://www.python.org/downloads/)
- **Poetry** (latest version) – [Installation guide](https://python-poetry.org/docs/#installation)

## Getting Started

First, install dependencies:

`poetry install`

Then, configure your environment variables:

```sh
mv .env.local .env
```

Finally, run the chatbot:

`poetry run python chatbot.py`

## Configuring Your Agent

You can [modify your agent configuration](https://github.com/coinbase/agentkit/tree/main/typescript/agentkit#usage) in the `chatbot.py` file.

### 1. Select Your LLM  
Modify the `ChatOpenAI` instantiation to use the model of your choice.

### 2. Select Your Wallet Provider  
AgentKit requires a **Wallet Provider** to interact with blockchain networks.

### 3. Select Your Action Providers  
Action Providers define what your agent can do. You can use built-in providers or create your own.

---

## Next Steps

- Explore the AgentKit README: [AgentKit Documentation](https://github.com/coinbase/agentkit)
- Learn more about available Wallet Providers & Action Providers.
- Experiment with custom Action Providers for your specific use case.

## Learn More

- [Learn more about CDP](https://docs.cdp.coinbase.com/)
- [Learn more about AgentKit](https://docs.cdp.coinbase.com/agentkit/docs/welcome)


## Contributing

Interested in contributing to AgentKit? Follow the contribution guide:

- [Contribution Guide](https://github.com/coinbase/agentkit/blob/main/CONTRIBUTING.md)
- Join the discussion on [Discord](https://discord.gg/CDP)
