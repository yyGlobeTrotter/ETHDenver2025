from flask import Flask, request, jsonify, Response
import os
import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    """Simple home endpoint"""
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
    return jsonify({"status": "AgentKit is running"}), 200

@app.route('/query', methods=['POST'])
def query():
    """Simplified query endpoint"""
    data = request.json
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Simplified response for testing deployment
    return jsonify({
        "response": f"Received message: {user_message}. This is a simplified API for testing deployment."
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    """Simplified analysis endpoint"""
    data = request.json
    token_id = data.get("token_id", "bitcoin")
    
    # Simplified response for testing deployment
    return jsonify({
        "result": f"Analysis for {token_id} would appear here in the full version."
    })

@app.route('/technical', methods=['POST'])
def technical():
    """Simplified technical indicators endpoint"""
    data = request.json
    token_id = data.get("token_id", "bitcoin")
    
    # Simplified response for testing deployment
    return jsonify({
        "indicators": {
            "token": token_id,
            "message": "Technical indicators would appear here in the full version."
        }
    })

@app.route('/whale', methods=['POST'])
def whale():
    """Simplified whale activity endpoint"""
    data = request.json
    token_id = data.get("token_id", "bitcoin")
    
    # Simplified response for testing deployment
    return jsonify({
        "token_id": token_id,
        "risk_score": 65,
        "level": "MEDIUM",
        "signals": ["This is a simplified API for testing deployment"]
    })

# Handler for Vercel serverless deployment
def handler(request):
    """
    This function is used by Vercel to handle serverless requests.
    """
    with app.request_context(request):
        return app.full_dispatch_request() 