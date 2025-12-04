#!/bin/bash
echo "🔄 Restarting Client Backend..."

# Find and kill the process
PID=$(ps aux | grep "uvicorn main:app.*8001" | grep -v grep | awk '{print $2}')
if [ ! -z "$PID" ]; then
    echo "Stopping backend (PID: $PID)..."
    kill $PID
    sleep 2
fi

# Start the backend
cd client_side
echo "Starting backend..."
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload > ../logs/client_backend.log 2>&1 &
echo $! > ../logs/client_backend.pid

sleep 3
echo "✅ Backend restarted!"
echo "Check logs: tail -f logs/client_backend.log"
