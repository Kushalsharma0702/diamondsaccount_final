#!/bin/bash
# Start backend server and run API tests

echo "🚀 Starting Tax-Ease Backend Server..."
cd "$(dirname "$0")/.."

# Start server in background
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001 > backend/server.log 2>&1 &
SERVER_PID=$!

echo "⏳ Waiting for server to start..."
sleep 3

# Check if server is running
if curl -s http://localhost:8001/ > /dev/null; then
    echo "✅ Server is running (PID: $SERVER_PID)"
    echo ""
    echo "🧪 Running API tests..."
    echo ""
    python3 backend/test_api.py
    
    echo ""
    echo "📋 Test complete. Server is still running."
    echo "   To stop server: kill $SERVER_PID"
    echo "   View logs: tail -f backend/server.log"
else
    echo "❌ Server failed to start. Check backend/server.log"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi
