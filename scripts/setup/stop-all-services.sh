#!/bin/bash

# Stop all running services

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛑 Stopping all services..."

# Stop services by PID files
for pid_file in "$BASE_DIR/logs"/*.pid; do
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        SERVICE=$(basename "$pid_file" .pid)
        if kill -0 $PID 2>/dev/null; then
            echo "Stopping $SERVICE (PID: $PID)..."
            kill $PID 2>/dev/null
            rm "$pid_file"
        fi
    fi
done

# Kill processes by port
echo "Checking for processes on ports 8001, 8002, 8080..."
for port in 8001 8002 8080; do
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$PID" ]; then
        echo "Killing process on port $port (PID: $PID)..."
        kill $PID 2>/dev/null
    fi
done

# Stop ngrok
pkill -f "ngrok http" 2>/dev/null
echo "✅ Stopped ngrok (if running)"

echo "✅ All services stopped!"




