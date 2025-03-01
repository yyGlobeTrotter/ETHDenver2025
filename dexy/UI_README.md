# Dexy UI - Windows 97 Themed Crypto Analysis Interface

This is a Windows 97-themed user interface for the Dexy cryptocurrency analysis chatbot, built for ETHDenver 2025.

## Overview

The UI provides a nostalgic Windows 97-style desktop environment for interacting with Dexy's crypto analysis tools. It includes:

- Chat interface for natural language queries
- Analysis tools for technical indicators
- Whale activity monitoring
- CDP wallet integration
- Classic Windows 97 desktop experience

## Getting Started

1. Install the project dependencies:
   ```
   poetry install
   ```

2. Run the server:
   ```
   poetry run python server.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5050
   ```

## Features

### Chat Window
- Natural language interaction with Dexy
- Ask about cryptocurrencies, technical indicators, and blockchain
- Markdown-style formatting for responses

### Analysis Window
- Quick Analysis: Get a snapshot of key technical indicators for any cryptocurrency
- Technical Indicators: Customize your analysis with specific indicators and timeframes
- Whale Analysis: Monitor large holder activity and exchange flows

### Settings
- Configure API providers
- Connect CDP wallet
- Customize UI settings

## Development

### File Structure
- `index.html` - Main UI layout
- `static/css/win97.css` - Windows 97 theme styling
- `static/js/win97.js` - UI interaction functionality
- `static/img/` - Windows 97 icons and graphics
- `server.py` - Flask server integrating with Dexy chatbot

### API Endpoints
- `/query` - Send chat messages to Dexy
- `/analyze` - Perform quick crypto analysis
- `/technical` - Get technical indicators
- `/whale` - Get whale activity analysis
- `/wallet` - Get CDP wallet information

## Credits

- Built for ETHDenver 2025
- Uses Coinbase's AgentKit for blockchain interactions
- Powered by Dexy's mean reversion and whale signal analysis tools
- Windows 97-themed UI design