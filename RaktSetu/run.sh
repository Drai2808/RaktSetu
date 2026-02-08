#!/bin/bash

echo "========================================"
echo "  BloodFlow AI - Starting Server"
echo "========================================"
echo ""

# Add current directory to Python path
export PYTHONPATH="${PWD}:${PYTHONPATH}"

echo "Starting FastAPI server..."
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 main.py
