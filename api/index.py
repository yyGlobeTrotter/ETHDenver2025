from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import json
import sys
import traceback

# Add parent directory to path so we can import from tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variable to track CDP connection status
cdp_connected = False

@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        "status": "online",
        "message": "VinRouge Dexy Bot API is running",
        "endpoints": [
            "/status",
            "/query",
            "/analyze",
            "/technical",
            "/whale"
        ]
    })

@app.route('/status', methods=['GET'])
def status():
    """API endpoint to check server status"""
    try:
        # In the full version, this would actually check CDP connection
        # For now, we'll return a more accurate status
        return jsonify({
            "status": "API is running, but CDP connection is not available in test mode",
            "cdp_connected": False
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "cdp_connected": False
        }), 500

@app.route('/query', methods=['POST', 'OPTIONS'])
def query():
    """Query endpoint for chat functionality"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    data = request.json
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    try:
        # For now, provide a simple response
        response = {
            "response": "I understand you're asking about: " + user_message + "\nI'm currently in test mode, but I can help you analyze cryptocurrencies and interact with blockchain using CDP AgentKit. What would you like to know?"
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analysis endpoint"""
    data = request.json
    token_id = data.get("token_id", "bitcoin")
    
    try:
        # Import the tools
        from tools.mean_reversion import get_token_indicators
        
        # Get the indicators
        indicators = get_token_indicators(token_id)
        
        if not indicators:
            return jsonify({"error": "No indicators returned"}), 500
            
        return jsonify({"result": indicators})
    except ImportError as e:
        error_msg = f"Failed to import required modules: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500
    except Exception as e:
        error_msg = f"Failed to process request: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500

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
        error_msg = f"Error in technical endpoint: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500

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
        error_msg = f"Error in whale endpoint: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return jsonify({"error": error_msg}), 500

# Catch-all route to handle all paths and methods
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def catch_all(path):
    """Catch-all route to handle all paths and methods"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

# Handler for Vercel serverless deployment
def handler(event, context):
    """
    This function is used by Vercel to handle serverless requests.
    It properly sets up the Flask request context and returns a response
    in the format expected by Vercel.
    """
    # Create a WSGI environment from the event
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    headers = event.get('headers', {})
    body = event.get('body', '')
    
    # Convert body to dict if it's a JSON string
    if isinstance(body, str) and body:
        try:
            body = json.loads(body)
        except:
            body = {}
    
    # Create a Flask request context
    with app.test_request_context(
        path=path,
        method=method,
        headers=headers,
        json=body if isinstance(body, dict) else None
    ):
        # Process the request
        try:
            response = app.full_dispatch_request()
            
            # Extract response data
            status_code = response.status_code
            response_headers = dict(response.headers)
            response_body = response.get_data(as_text=True)
            
            # Return response in the format expected by Vercel
            return {
                'statusCode': status_code,
                'headers': response_headers,
                'body': response_body
            }
        except Exception as e:
            # Handle any errors
            error_msg = f"Handler error: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Internal Server Error',
                    'message': str(e)
                })
            } 