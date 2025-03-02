import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory

# Import the agent initialization from chatbot.py
from chatbot import initialize_agent, HumanMessage

app = Flask(__name__, static_folder='static', template_folder='.')

# Initialize AgentKit
agent_executor, config = initialize_agent()

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
    
    # Get response from AgentKit
    response_text = ""
    for chunk in agent_executor.stream({"messages": [HumanMessage(content=user_message)]}, config):
        if "agent" in chunk and chunk["agent"]["messages"]:
            response_text = chunk["agent"]["messages"][0].content
        elif "tools" in chunk and chunk["tools"]["messages"]:
            response_text = chunk["tools"]["messages"][0].content

    return jsonify({"response": response_text})

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analysis endpoint"""
    data = request.json
    token_id = data.get("token_id", "bitcoin")
    
    try:
        # Use invoke instead of __call__
        indicators = get_token_indicators_tool.invoke({"token_id": token_id})
        if indicators:
            return jsonify({"result": indicators})
        else:
            return jsonify({"error": "Could not retrieve indicators"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/technical', methods=['POST'])
def technical():
    """API endpoint to get technical indicators"""
    data = request.json
    token_id = data.get("token_id", "bitcoin")
    
    try:
        # Import the tools
        from tools.mean_reversion import get_token_indicators
        
        # Get the indicators
        indicators = get_token_indicators(token_id)
        
        return jsonify({"indicators": indicators})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/whale', methods=['POST'])
def whale():
    """API endpoint to get whale activity analysis"""
    data = request.json
    token_id = data.get("token_id", "bitcoin")
    
    try:
        # Import the tools
        from tools.whalesignal import generate_risk_signals
        
        # Get risk signals
        risk_data = generate_risk_signals()
        
        # Format response
        response = {
            "token_id": token_id,
            "risk_score": risk_data["risk_score"],
            "level": risk_data["level"],
            "signals": risk_data["signals"]
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/wallet', methods=['GET'])
def wallet():
    """API endpoint to get wallet information"""
    wallet_data_file = "wallet_data.txt"
    
    if os.path.exists(wallet_data_file):
        with open(wallet_data_file) as f:
            wallet_data = f.read()
            
        try:
            wallet_json = json.loads(wallet_data)
            return jsonify({"wallet": wallet_json})
        except:
            return jsonify({"error": "Invalid wallet data format"}), 500
    else:
        return jsonify({"error": "No wallet data found"}), 404

# Handler for Vercel serverless deployment
def handler(request, context):
    """
    This function is used by Vercel to handle serverless requests.
    It forwards the request to the Flask app.
    """
    with app.request_context(request):
        return app.full_dispatch_request()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)