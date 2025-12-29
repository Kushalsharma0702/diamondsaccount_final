#!/bin/bash
# Simple script to run API tests (assumes server is already running)

echo "🧪 Running Tax-Ease Backend API Tests..."
echo ""

# Check if server is running
if ! curl -s http://localhost:8001/ > /dev/null 2>&1; then
    echo "❌ Server is not running on port 8001"
    echo ""
    echo "Please start the server first:"
    echo "  uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001"
    echo ""
    echo "Or use the automated script:"
    echo "  ./backend/start_and_test.sh"
    exit 1
fi

echo "✅ Server is running"
echo ""
python3 backend/test_api.py
