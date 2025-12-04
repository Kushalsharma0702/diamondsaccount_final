#!/bin/bash

echo "🔄 Restarting Admin Backend..."

# Stop existing backend
PID=$(ps aux | grep "uvicorn.*8002" | grep -v grep | awk '{print $2}')
if [ ! -z "$PID" ]; then
    echo "Stopping backend (PID: $PID)..."
    kill $PID
    sleep 2
fi

# Start backend
cd tax-hub-dashboard/backend
echo "Starting backend on port 8002..."
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload > ../../logs/admin_backend.log 2>&1 &
echo $! > ../../logs/admin_backend.pid

sleep 3
echo "✅ Backend restarted!"
echo "Check logs: tail -f logs/admin_backend.log"


