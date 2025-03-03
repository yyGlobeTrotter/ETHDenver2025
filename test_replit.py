from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from VinRouge-Dexy-Bot! The server is working correctly."

if __name__ == "__main__":
    port = 8080
    print(f"Starting test server on port {port}")
    app.run(host="0.0.0.0", port=port) 