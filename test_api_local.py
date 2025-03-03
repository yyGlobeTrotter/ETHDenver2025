"""
Local testing script for the API endpoints.
This script runs the Flask app locally and provides instructions for testing.
"""
import os
from api.index import app

if __name__ == "__main__":
    print("Starting local API server for testing...")
    print("API will be available at http://localhost:8000")
    print("\nTest endpoints with the following commands in another terminal:")
    print("\n1. Test home endpoint:")
    print("   curl http://localhost:8000/")
    print("\n2. Test status endpoint:")
    print("   curl http://localhost:8000/status")
    print("\n3. Test query endpoint:")
    print("   curl -X POST -H \"Content-Type: application/json\" -d '{\"message\": \"Hello\"}' http://localhost:8000/query")
    print("\n4. Test analyze endpoint:")
    print("   curl -X POST -H \"Content-Type: application/json\" -d '{\"token_id\": \"bitcoin\"}' http://localhost:8000/analyze")
    print("\n5. Test technical endpoint:")
    print("   curl -X POST -H \"Content-Type: application/json\" -d '{\"token_id\": \"bitcoin\"}' http://localhost:8000/technical")
    print("\n6. Test whale endpoint:")
    print("   curl -X POST -H \"Content-Type: application/json\" -d '{\"token_id\": \"bitcoin\"}' http://localhost:8000/whale")
    print("\nPress Ctrl+C to stop the server when done testing.")
    
    # Run the Flask app in debug mode
    app.run(debug=True, host="0.0.0.0", port=8000) 