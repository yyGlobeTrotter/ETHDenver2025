import os
import json
import random
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='.')

# Mock data for the API endpoints
def get_mock_analysis(token_id):
    tokens = {
        "bitcoin": {
            "price": 63240.85,
            "z_score": 1.37,
            "rsi": 68.4,
            "bollinger_b": 0.87,
            "signal": "MODERATE DOWNWARD REVERSION POTENTIAL",
            "risk_score": 62,
            "level": "MODERATE"
        },
        "ethereum": {
            "price": 3254.72,
            "z_score": -0.82,
            "rsi": 45.2,
            "bollinger_b": 0.32,
            "signal": "NEUTRAL - NO SIGNIFICANT SIGNAL",
            "risk_score": 45,
            "level": "LOW"
        },
        "solana": {
            "price": 139.85,
            "z_score": 2.14,
            "rsi": 79.7,
            "bollinger_b": 1.12,
            "signal": "STRONG DOWNWARD REVERSION POTENTIAL",
            "risk_score": 78,
            "level": "HIGH"
        },
        "cardano": {
            "price": 0.58,
            "z_score": 0.21,
            "rsi": 53.6,
            "bollinger_b": 0.54,
            "signal": "NEUTRAL - NO SIGNIFICANT SIGNAL",
            "risk_score": 55,
            "level": "MODERATE"
        },
        "ripple": {
            "price": 1.08,
            "z_score": -1.53,
            "rsi": 39.8,
            "bollinger_b": 0.18,
            "signal": "MODERATE UPWARD REVERSION POTENTIAL",
            "risk_score": 38,
            "level": "LOW"
        }
    }
    
    token_data = tokens.get(token_id.lower(), tokens["bitcoin"])
    
    return f"""
=== INTEGRATED ANALYSIS FOR {token_id.upper()} ===

PRICE & TECHNICAL INDICATORS:
Current Price: ${token_data['price']:.2f}
Z-Score: {token_data['z_score']:.2f} - {'OVERBOUGHT' if token_data['z_score'] > 1 else 'OVERSOLD' if token_data['z_score'] < -1 else 'NEUTRAL'}
RSI: {token_data['rsi']:.2f} - {'OVERBOUGHT' if token_data['rsi'] > 70 else 'OVERSOLD' if token_data['rsi'] < 30 else 'NEUTRAL'}
Bollinger %B: {token_data['bollinger_b']:.2f} - {'UPPER BAND' if token_data['bollinger_b'] > 0.8 else 'LOWER BAND' if token_data['bollinger_b'] < 0.2 else 'MIDDLE BAND'}

MEAN REVERSION:
Mean Reversion Score: {-2.5 if 'DOWNWARD' in token_data['signal'] else 2.5 if 'UPWARD' in token_data['signal'] else 0:.2f}
Direction: {token_data['signal']}

WHALE DOMINANCE ANALYSIS:
Risk Score: {token_data['risk_score']} - {token_data['level']}
Risk Signals: {'EXCHANGE OUTFLOWS, LARGE WALLETS ACCUMULATING' if token_data['risk_score'] < 50 else 'UNUSUAL WHALE TRANSFERS, EXCHANGE INFLOWS INCREASING'}

INTEGRATED RESULT:
Risk Multiplier: {1.2 if token_data['risk_score'] > 60 else 0.8 if token_data['risk_score'] < 40 else 1.0:.1f}x
Adjusted Score: {-3.0 if 'DOWNWARD' in token_data['signal'] and token_data['risk_score'] > 60 else 3.0 if 'UPWARD' in token_data['signal'] and token_data['risk_score'] < 40 else -2.0 if 'DOWNWARD' in token_data['signal'] else 2.0 if 'UPWARD' in token_data['signal'] else 0:.2f}
Final Signal: {'STRONGER' if (('DOWNWARD' in token_data['signal'] and token_data['risk_score'] > 60) or ('UPWARD' in token_data['signal'] and token_data['risk_score'] < 40)) else 'UNCHANGED'} {token_data['signal']}

RECOMMENDATION:
{'Consider a stronger position due to significant whale activity' if token_data['risk_score'] > 60 or token_data['risk_score'] < 40 else 'Proceed with standard position sizing based on technical indicators'}
"""

@app.route('/')
def index():
    """Serve the main UI page"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/status', methods=['GET'])
def status():
    """API endpoint to check server status"""
    return jsonify({"status": "AgentKit is running"}), 200

@app.route('/query', methods=['POST'])
def query():
    """API endpoint to query the agent"""
    data = request.json
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Mock responses based on keywords in the message
    if "price" in user_message.lower():
        if "bitcoin" in user_message.lower():
            response = "Bitcoin (BTC) is currently trading at $63,240.85, up 1.2% in the last 24 hours."
        elif "ethereum" in user_message.lower():
            response = "Ethereum (ETH) is currently trading at $3,254.72, down 0.5% in the last 24 hours."
        elif "solana" in user_message.lower():
            response = "Solana (SOL) is currently trading at $139.85, up 3.2% in the last 24 hours."
        else:
            response = "Bitcoin (BTC) is currently trading at $63,240.85, Ethereum (ETH) at $3,254.72, and Solana (SOL) at $139.85."
    elif "analysis" in user_message.lower() or "analyze" in user_message.lower():
        if "bitcoin" in user_message.lower():
            response = "Bitcoin is showing signs of being overbought with a Z-Score of 1.37 and RSI of 68.4. Technical indicators suggest a potential downward reversion in the short term."
        elif "ethereum" in user_message.lower():
            response = "Ethereum is currently in neutral territory with a Z-Score of -0.82 and RSI of 45.2. No significant mean reversion signals at the moment."
        else:
            response = "Based on technical indicators, Bitcoin is showing signs of being overbought, while Ethereum remains in neutral territory. Solana appears significantly overbought with a Z-Score of 2.14."
    elif "wallet" in user_message.lower():
        response = "Your CDP wallet address is 0x742d35Cc6634C0532925a3b844Bc454e4438f44e with a current balance of 0.05 ETH."
    else:
        responses = [
            "I'm Dexy, a cryptocurrency analysis assistant. I can help with price information, technical analysis, and blockchain interactions.",
            "I can analyze cryptocurrencies using mean reversion and whale activity indicators. What would you like to know?",
            "I can provide technical analysis using indicators like Z-Score, RSI, and Bollinger Bands. Which cryptocurrency are you interested in?",
            "For detailed analysis, try asking about a specific cryptocurrency like Bitcoin or Ethereum.",
            "I can help you understand the current market conditions for cryptocurrencies using technical and whale activity analysis."
        ]
        response = random.choice(responses)

    return jsonify({"response": response})

@app.route('/analyze', methods=['POST'])
def analyze():
    """API endpoint to perform quick analysis"""
    data = request.json
    token_id = data.get("token_id", "bitcoin")
    
    # Use our mock analysis function
    analysis_result = get_mock_analysis(token_id)
    
    return jsonify({"result": analysis_result})

@app.route('/technical', methods=['POST'])
def technical():
    """API endpoint to get technical indicators"""
    data = request.json
    token_id = data.get("token_id", "bitcoin")
    days = data.get("days", 30)
    
    tokens = {
        "bitcoin": {"current_price": 63240.85, "z_score": 1.37, "rsi": 68.4, "bollinger_b": 0.87},
        "ethereum": {"current_price": 3254.72, "z_score": -0.82, "rsi": 45.2, "bollinger_b": 0.32},
        "solana": {"current_price": 139.85, "z_score": 2.14, "rsi": 79.7, "bollinger_b": 1.12},
        "cardano": {"current_price": 0.58, "z_score": 0.21, "rsi": 53.6, "bollinger_b": 0.54},
        "ripple": {"current_price": 1.08, "z_score": -1.53, "rsi": 39.8, "bollinger_b": 0.18}
    }
    
    token_data = tokens.get(token_id.lower(), tokens["bitcoin"])
    
    # Create mock technical indicators response
    response = {
        "indicators": {
            "token_id": token_id,
            "current_price": token_data["current_price"],
            "metrics": {
                "z_score": {
                    "value": token_data["z_score"],
                    "interpretation": "OVERBOUGHT" if token_data["z_score"] > 1 else "OVERSOLD" if token_data["z_score"] < -1 else "NEUTRAL"
                },
                "rsi": {
                    "value": token_data["rsi"],
                    "interpretation": "OVERBOUGHT" if token_data["rsi"] > 70 else "OVERSOLD" if token_data["rsi"] < 30 else "NEUTRAL"
                },
                "bollinger_bands": {
                    "percent_b": token_data["bollinger_b"],
                    "interpretation": "UPPER BAND" if token_data["bollinger_b"] > 0.8 else "LOWER BAND" if token_data["bollinger_b"] < 0.2 else "MIDDLE BAND"
                }
            },
            "summary": f"Based on {days} days of data, {token_id.title()} is currently showing {'overbought conditions' if token_data['z_score'] > 1 or token_data['rsi'] > 70 else 'oversold conditions' if token_data['z_score'] < -1 or token_data['rsi'] < 30 else 'neutral conditions with no strong directional bias'}."
        }
    }
    
    return jsonify(response)

@app.route('/whale', methods=['POST'])
def whale():
    """API endpoint to get whale activity analysis"""
    data = request.json
    token_id = data.get("token_id", "bitcoin")
    
    # Mock risk data based on token
    risk_data = {
        "bitcoin": {"risk_score": 62, "level": "MODERATE", "signals": ["EXCHANGE OUTFLOWS", "LARGE WALLETS ACCUMULATING"]},
        "ethereum": {"risk_score": 45, "level": "LOW", "signals": ["NORMAL ACTIVITY", "SLIGHT DISTRIBUTION"]},
        "solana": {"risk_score": 78, "level": "HIGH", "signals": ["UNUSUAL WHALE TRANSFERS", "EXCHANGE INFLOWS INCREASING", "TOP WALLETS SELLING"]},
        "cardano": {"risk_score": 55, "level": "MODERATE", "signals": ["MIXED SIGNALS", "SOME ACCUMULATION"]},
        "ripple": {"risk_score": 38, "level": "LOW", "signals": ["WHALE ACCUMULATION", "EXCHANGE OUTFLOWS"]}
    }
    
    response = risk_data.get(token_id.lower(), risk_data["bitcoin"])
    response["token_id"] = token_id
    
    return jsonify(response)

@app.route('/wallet', methods=['GET'])
def wallet():
    """API endpoint to get wallet information"""
    # Mock wallet data
    wallet_json = {
        "address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "balance": "0.05 ETH",
        "network": "base-sepolia"
    }
    
    return jsonify({"wallet": wallet_json})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)