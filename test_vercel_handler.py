"""
Test script to simulate the Vercel serverless environment locally.
This helps test the handler function that Vercel will use.
"""
import json
import sys
from api.index import handler

class MockContext:
    """Mock context object for the Vercel serverless function"""
    def __init__(self):
        self.function_name = "api-handler"
        self.function_version = "1.0.0"
        self.memory_limit_in_mb = 128
        self.aws_request_id = "mock-request-id"

class MockEvent:
    """Mock event object for the Vercel serverless function"""
    def __init__(self, method, path, body=None, headers=None):
        self.method = method
        self.path = path
        self.body = body
        self.headers = headers or {}
        
    def __getitem__(self, key):
        if key == "httpMethod":
            return self.method
        elif key == "path":
            return self.path
        elif key == "body":
            return json.dumps(self.body) if self.body else ""
        elif key == "headers":
            return self.headers
        else:
            return None
            
    def get(self, key, default=None):
        """Implement get method to match the expected interface"""
        if key == 'httpMethod':
            return self.method
        elif key == 'path':
            return self.path
        elif key == 'body':
            return json.dumps(self.body) if self.body else ""
        elif key == 'headers':
            return self.headers
        else:
            return default

def test_handler(method, path, body=None, headers=None):
    """Test the handler function with a mock event and context"""
    event = MockEvent(method, path, body, headers)
    context = MockContext()
    
    print(f"\nTesting handler with {method} request to {path}")
    if body:
        print(f"Request body: {json.dumps(body, indent=2)}")
    
    try:
        response = handler(event, context)
        print(f"Status code: {response.get('statusCode', 'unknown')}")
        
        # Try to parse the response body
        try:
            response_body = json.loads(response.get("body", "{}"))
            print(f"Response body: {json.dumps(response_body, indent=2)}")
        except:
            print(f"Response body: {response.get('body', '')}")
        
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def run_tests():
    """Run a series of tests on the handler function"""
    tests = [
        # Test home endpoint
        {"method": "GET", "path": "/", "body": None},
        
        # Test status endpoint
        {"method": "GET", "path": "/status", "body": None},
        
        # Test query endpoint
        {"method": "POST", "path": "/query", "body": {"message": "Hello, this is a test message"}},
        
        # Test analyze endpoint
        {"method": "POST", "path": "/analyze", "body": {"token_id": "bitcoin"}},
        
        # Test technical endpoint
        {"method": "POST", "path": "/technical", "body": {"token_id": "bitcoin"}},
        
        # Test whale endpoint
        {"method": "POST", "path": "/whale", "body": {"token_id": "bitcoin"}}
    ]
    
    results = []
    for test in tests:
        response = test_handler(test["method"], test["path"], test["body"])
        results.append({
            "test": f"{test['method']} {test['path']}",
            "passed": response is not None and response.get("statusCode", 500) < 400
        })
    
    # Print summary
    print("\n" + "="*50)
    print("HANDLER TEST RESULTS SUMMARY")
    print("="*50)
    
    all_passed = True
    for result in results:
        status = "PASSED" if result["passed"] else "FAILED"
        if not result["passed"]:
            all_passed = False
        print(f"{result['test'].ljust(20)}: {status}")
    
    print("\nOverall result:", "PASSED" if all_passed else "FAILED")
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 