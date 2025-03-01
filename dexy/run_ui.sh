#!/bin/bash

# Start the Dexy UI
echo "Starting Dexy UI..."
echo "Windows 97-themed interface for crypto analysis"
echo "---------------------------------------------"

# Activate poetry virtual environment if it exists
if command -v poetry &> /dev/null; then
    echo "Running with Poetry..."
    poetry run python server.py
else
    # Fallback to regular Python
    echo "Poetry not found, using system Python..."
    python server.py
fi

echo "UI server stopped."