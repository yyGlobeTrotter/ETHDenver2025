"""
Automated testing script for the API endpoints.
This script tests all endpoints and reports the results.
"""
import requests
import json
import time
import subprocess
import sys
import os
import signal
from threading import Thread

# Configuration
API_URL = "http://localhost:8000"
TIMEOUT = 5  # seconds

def run_server():
    """Run the Flask server in a separate process"""
    print("Starting API server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"],
        env={**os.environ, "FLASK_APP": "api.index:app", "FLASK_DEBUG": "0"},
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    return process

def test_home_endpoint():
    """Test the home endpoint"""
    print("\nTesting home endpoint (GET /)...")
    try:
        response = requests.get(f"{API_URL}/", timeout=TIMEOUT)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
            return True
        else:
            print("Failed with status code:", response.status_code)
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_status_endpoint():
    """Test the status endpoint"""
    print("\nTesting status endpoint (GET /status)...")
    try:
        response = requests.get(f"{API_URL}/status", timeout=TIMEOUT)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
            return True
        else:
            print("Failed with status code:", response.status_code)
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_query_endpoint():
    """Test the query endpoint"""
    print("\nTesting query endpoint (POST /query)...")
    try:
        payload = {"message": "Hello, this is a test message"}
        response = requests.post(
            f"{API_URL}/query", 
            json=payload,
            timeout=TIMEOUT
        )
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
            return True
        else:
            print("Failed with status code:", response.status_code)
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_analyze_endpoint():
    """Test the analyze endpoint"""
    print("\nTesting analyze endpoint (POST /analyze)...")
    try:
        payload = {"token_id": "bitcoin"}
        response = requests.post(
            f"{API_URL}/analyze", 
            json=payload,
            timeout=TIMEOUT
        )
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
            return True
        else:
            print("Failed with status code:", response.status_code)
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_technical_endpoint():
    """Test the technical endpoint"""
    print("\nTesting technical endpoint (POST /technical)...")
    try:
        payload = {"token_id": "bitcoin"}
        response = requests.post(
            f"{API_URL}/technical", 
            json=payload,
            timeout=TIMEOUT
        )
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
            return True
        else:
            print("Failed with status code:", response.status_code)
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_whale_endpoint():
    """Test the whale endpoint"""
    print("\nTesting whale endpoint (POST /whale)...")
    try:
        payload = {"token_id": "bitcoin"}
        response = requests.post(
            f"{API_URL}/whale", 
            json=payload,
            timeout=TIMEOUT
        )
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
            return True
        else:
            print("Failed with status code:", response.status_code)
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_tests():
    """Run all tests and report results"""
    print("Waiting for server to start...")
    time.sleep(2)  # Give the server time to start
    
    # Run all tests
    results = {
        "home": test_home_endpoint(),
        "status": test_status_endpoint(),
        "query": test_query_endpoint(),
        "analyze": test_analyze_endpoint(),
        "technical": test_technical_endpoint(),
        "whale": test_whale_endpoint()
    }
    
    # Print summary
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    
    all_passed = True
    for endpoint, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        if not passed:
            all_passed = False
        print(f"{endpoint.ljust(10)}: {status}")
    
    print("\nOverall result:", "PASSED" if all_passed else "FAILED")
    return all_passed

if __name__ == "__main__":
    # Start the server
    server_process = run_server()
    
    try:
        # Run the tests
        success = run_tests()
        
        # Terminate the server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted. Stopping server...")
        server_process.terminate()
        server_process.wait()
        sys.exit(1)
    except Exception as e:
        print(f"\nError during testing: {e}")
        server_process.terminate()
        server_process.wait()
        sys.exit(1) 