#!/bin/bash

# Start ngrok tunnel for client backend
# This exposes the backend at port 8001 through ngrok

CLIENT_BACKEND_PORT=8001

echo "🚀 Starting ngrok tunnel for client backend (port $CLIENT_BACKEND_PORT)..."

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed!"
    echo "Please install ngrok:"
    echo "  - Download from: https://ngrok.com/download"
    echo "  - Or via snap: sudo snap install ngrok"
    echo "  - Or via brew: brew install ngrok"
    exit 1
fi

# Kill any existing ngrok processes on this port
pkill -f "ngrok http $CLIENT_BACKEND_PORT" 2>/dev/null

# Start ngrok tunnel
echo "📡 Starting ngrok tunnel..."
ngrok http $CLIENT_BACKEND_PORT > /tmp/ngrok.log 2>&1 &

NGROK_PID=$!
sleep 3

# Get the ngrok URL
if [ -f /tmp/ngrok.log ]; then
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -z "$NGROK_URL" ]; then
        echo "⏳ Waiting for ngrok to start..."
        sleep 2
        NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)
    fi
    
    if [ -n "$NGROK_URL" ]; then
        echo ""
        echo "✅ Ngrok tunnel established!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🌐 Public URL: $NGROK_URL"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "📋 Update Flutter app with this URL:"
        echo "   $NGROK_URL/api/v1"
        echo ""
        echo "🔍 View ngrok dashboard: http://localhost:4040"
        echo "🛑 Press Ctrl+C to stop ngrok"
        echo ""
        
        # Save URL to file for other scripts
        echo "$NGROK_URL" > /tmp/ngrok_url.txt
        
        # Wait for user interrupt
        wait $NGROK_PID
    else
        echo "❌ Failed to get ngrok URL. Check ngrok dashboard: http://localhost:4040"
        kill $NGROK_PID 2>/dev/null
        exit 1
    fi
else
    echo "❌ Failed to start ngrok. Check if ngrok is properly installed."
    exit 1
fi




