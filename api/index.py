from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import json
import sys
import traceback

# Add parent directory to path so we can import from tools
# But wrap in try/except to handle any import errors
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except Exception as e:
    print(f"Error setting up path: {str(e)}")

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
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.json
        if not data:
            return jsonify({"response": "No data received. Please send a message."}), 200
            
        user_message = data.get("message", "")
        
        if not user_message:
            return jsonify({"response": "I didn't receive a message. What would you like to know?"}), 200
        
        # For now, provide a simple response
        response = {
            "response": "I understand you're asking about: " + user_message + "\nI'm currently in test mode, but I can help you analyze cryptocurrencies and interact with blockchain using CDP AgentKit. What would you like to know?"
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error in query endpoint: {str(e)}")
        return jsonify({
            "response": "I encountered an error processing your request. Please try again."
        }), 200

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """Analysis endpoint that combines technical and whale analysis"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    try:
        data = request.json
        if not data:
            data = {}
            
        token_id = data.get("token_id", "bitcoin")
        
        # Try to combine both analysis types into one comprehensive report
        technical_data = None
        whale_data = None
        
        # Get technical analysis data
        try:
            from tools.mean_reversion.core.indicators import MeanReversionService
            service = MeanReversionService()
            analysis_result = service.get_all_indicators(token_id)
            
            technical_data = {
                "current_price": analysis_result["current_price"],
                "z_score": analysis_result["indicators"]["z_score"]["value"],
                "z_score_interpretation": analysis_result["indicators"]["z_score"]["interpretation"],
                "rsi": analysis_result["indicators"]["rsi"]["value"],
                "rsi_interpretation": analysis_result["indicators"]["rsi"]["interpretation"],
                "bb_percent": analysis_result["indicators"]["bollinger_bands"]["percent_b"],
                "bb_interpretation": analysis_result["indicators"]["bollinger_bands"]["interpretation"],
                "signal": "BULLISH" if analysis_result["indicators"]["z_score"]["interpretation"].startswith("POTENTIAL UPWARD") else 
                         "BEARISH" if analysis_result["indicators"]["z_score"]["interpretation"].startswith("POTENTIAL DOWNWARD") else
                         "NEUTRAL"
            }
        except Exception as tech_error:
            print(f"Error getting technical data: {str(tech_error)}")
            # Fall back to mock technical data
            technical_data = {
                "current_price": 65432.10,
                "z_score": -0.85,
                "z_score_interpretation": "Moderately oversold",
                "rsi": 42.3,
                "rsi_interpretation": "Neutral with bearish bias",
                "bb_percent": 0.42,
                "bb_interpretation": "Within normal range",
                "signal": "NEUTRAL"
            }
            
        # Get whale analysis data
        try:
            from tools.whalesignal.whale_dominance import generate_risk_signals
            risk_result = generate_risk_signals()
            
            whale_data = {
                "risk_score": risk_result["risk_score"] * 20 if risk_result["risk_score"] <= 5 else 100,  # Scale to 0-100
                "level": risk_result["level"].replace("🚨", "").replace("⚠️", "").replace("🟢", "").strip(),
                "signals": risk_result["signals"]
            }
        except Exception as whale_error:
            print(f"Error getting whale data: {str(whale_error)}")
            # Fall back to mock whale data
            whale_data = {
                "risk_score": 65,
                "level": "MEDIUM RISK",
                "signals": [
                    "Increased exchange inflows detected",
                    "Moderate whale wallet movement",
                    "Historical volatility above average"
                ]
            }
            
        # Combine the data into one integrated result
        result = {
            "token": token_id,
            "current_price": technical_data["current_price"],
            "metrics": {
                "z_score": {"value": technical_data["z_score"], "interpretation": technical_data["z_score_interpretation"]},
                "rsi": {"value": technical_data["rsi"], "interpretation": technical_data["rsi_interpretation"]},
                "bollinger_bands": {
                    "percent_b": technical_data["bb_percent"],
                    "interpretation": technical_data["bb_interpretation"]
                }
            },
            "whale_metrics": {
                "risk_score": whale_data["risk_score"],
                "level": whale_data["level"],
                "signals": whale_data["signals"]
            },
            "signal": technical_data["signal"],
            "overall_risk": "HIGH" if whale_data["risk_score"] > 70 else "MEDIUM" if whale_data["risk_score"] > 30 else "LOW"
        }
        
        return jsonify({"result": result})
    except Exception as e:
        print(f"Error in analyze endpoint: {str(e)}")
        return jsonify({"result": {"error": "Analysis failed", "message": "Please try again later"}})

@app.route('/technical', methods=['POST', 'OPTIONS'])
def technical():
    """API endpoint to get technical indicators"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    try:
        data = request.json
        if not data:
            data = {}
            
        token_id = data.get("token_id", "bitcoin")
        days = int(data.get("days", 30))
        
        # Import the Mean Reversion Service here
        try:
            from tools.mean_reversion.core.indicators import MeanReversionService
            
            # Initialize the service with default settings (DeFi Llama API)
            service = MeanReversionService()
            
            # Get all indicators for the specified token
            analysis_result = service.get_all_indicators(token_id, window=min(days, 20))
            
            # Format the response to match the expected structure
            result = {
                "token": token_id,
                "current_price": analysis_result["current_price"],
                "metrics": {
                    "z_score": {
                        "value": analysis_result["indicators"]["z_score"]["value"],
                        "interpretation": analysis_result["indicators"]["z_score"]["interpretation"]
                    },
                    "rsi": {
                        "value": analysis_result["indicators"]["rsi"]["value"],
                        "interpretation": analysis_result["indicators"]["rsi"]["interpretation"]
                    },
                    "bollinger_bands": {
                        "upper": analysis_result["indicators"]["bollinger_bands"]["upper_band"],
                        "middle": analysis_result["indicators"]["bollinger_bands"]["middle_band"],
                        "lower": analysis_result["indicators"]["bollinger_bands"]["lower_band"],
                        "percent_b": analysis_result["indicators"]["bollinger_bands"]["percent_b"],
                        "interpretation": analysis_result["indicators"]["bollinger_bands"]["interpretation"]
                    }
                },
                "signal": "BULLISH" if analysis_result["indicators"]["z_score"]["interpretation"].startswith("POTENTIAL UPWARD") else 
                         "BEARISH" if analysis_result["indicators"]["z_score"]["interpretation"].startswith("POTENTIAL DOWNWARD") else
                         "NEUTRAL"
            }
            
            return jsonify({"indicators": result})
            
        except Exception as import_error:
            print(f"Error importing or using Mean Reversion Service: {str(import_error)}")
            # If there's an error with the service, fall back to mock data
            mock_data = {
                "token": token_id,
                "current_price": 65432.10,
                "metrics": {
                    "z_score": {"value": -0.85, "interpretation": "Moderately oversold"},
                    "rsi": {"value": 42.3, "interpretation": "Neutral with bearish bias"},
                    "bollinger_bands": {
                        "upper": 68500,
                        "middle": 64200,
                        "lower": 59900,
                        "percent_b": 0.42,
                        "interpretation": "Within normal range"
                    }
                },
                "signal": "NEUTRAL",
                "note": "This is simulated data for demonstration purposes."
            }
            return jsonify({"indicators": mock_data})
            
    except Exception as e:
        print(f"Error in technical endpoint: {str(e)}")
        return jsonify({"indicators": {"error": "Technical analysis failed", "message": "Please try again later"}})

@app.route('/whale', methods=['POST', 'OPTIONS'])
def whale():
    """API endpoint to get whale activity analysis"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    try:
        data = request.json
        if not data:
            data = {}
            
        token_id = data.get("token_id", "bitcoin")
        
        # Try to use the whale_dominance module
        try:
            from tools.whalesignal.whale_dominance import generate_risk_signals
            
            # Generate risk signals
            risk_result = generate_risk_signals()
            
            # Format the response
            result = {
                "token_id": token_id,
                "risk_score": risk_result["risk_score"] * 20 if risk_result["risk_score"] <= 5 else 100,  # Scale to 0-100
                "level": risk_result["level"].replace("🚨", "").replace("⚠️", "").replace("🟢", "").strip(),
                "signals": risk_result["signals"]
            }
            
            return jsonify(result)
            
        except Exception as import_error:
            print(f"Error importing or using Whale Signal: {str(import_error)}")
            # If there's an error with the module, fall back to mock data
            mock_data = {
                "token_id": token_id,
                "risk_score": 65,
                "level": "MEDIUM",
                "signals": [
                    "Increased exchange inflows detected",
                    "Moderate whale wallet movement",
                    "Historical volatility above average"
                ],
                "note": "This is simulated data for demonstration purposes."
            }
            
            return jsonify(mock_data)
            
    except Exception as e:
        print(f"Error in whale endpoint: {str(e)}")
        return jsonify({
            "token_id": token_id if 'token_id' in locals() else "unknown",
            "risk_score": 0,
            "level": "ERROR",
            "signals": ["Could not analyze whale activity at this time"],
            "error": "Please try again later"
        })

# Add an endpoint for wallet
@app.route('/wallet', methods=['GET', 'OPTIONS'])
def wallet():
    """API endpoint to get wallet information"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response
    
    try:    
        return jsonify({
            "wallet": {
                "address": "0x1234...5678",
                "balance": "0.5 ETH",
                "network": "Sepolia"
            }
        })
    except Exception as e:
        print(f"Error in wallet endpoint: {str(e)}")
        return jsonify({
            "wallet": {
                "address": "Connection error",
                "balance": "0.0",
                "network": "Unknown"
            }
        })

# Add an endpoint for health check
@app.route('/health', methods=['GET'])
def health():
    """API endpoint to check health status"""
    return jsonify({
        "status": "healthy",
        "message": "API is operational",
        "version": "1.0.0"
    })

# Catch-all route to handle all paths and methods
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def catch_all(path):
    """Catch-all route to handle all paths and methods"""
    # Handle OPTIONS requests for CORS
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        return response
        
    try:
        with app.request_context(request.environ):
            return app.full_dispatch_request()
    except Exception as e:
        print(f"Error in catch-all route: {str(e)}")
        return jsonify({
            "error": "Unknown endpoint or method",
            "path": path,
            "method": request.method
        }), 404

# Handler for Vercel serverless deployment
def handler(event, context):
    """
    This function is used by Vercel to handle serverless requests.
    It properly sets up the Flask request context and returns a response
    in the format expected by Vercel.
    """
    try:
        # Create a WSGI environment from the event
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        body = event.get('body', '')
        
        # Add CORS headers for all responses
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        
        # Handle preflight OPTIONS request directly
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    **cors_headers,
                    'Content-Type': 'application/json'
                },
                'body': '{}'
            }
        
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
                
                # Add CORS headers to every response
                for key, value in cors_headers.items():
                    response_headers[key] = value
                
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
                    'statusCode': 200,  # Return 200 even on error to avoid Vercel showing error pages
                    'headers': {
                        **cors_headers,
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({
                        'error': 'Processing error',
                        'message': "Something went wrong processing your request"
                    })
                }
    except Exception as e:
        # Catch-all handler error
        print(f"Top-level handler error: {str(e)}")
        traceback.print_exc()
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Server error',
                'message': "The server encountered an error processing your request"
            })
        }