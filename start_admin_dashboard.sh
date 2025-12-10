#!/bin/bash

# Start Admin Dashboard Script
# This script starts both the admin backend and frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADMIN_BACKEND_DIR="$SCRIPT_DIR/admin-dashboard/backend"
ADMIN_FRONTEND_DIR="$SCRIPT_DIR/admin-dashboard/frontend"

echo "=========================================="
echo "🚀 Starting Admin Dashboard"
echo "=========================================="
echo ""

# Check if backends are already running
if pgrep -f "uvicorn.*admin.*main" > /dev/null; then
    echo "⚠️  Admin backend is already running"
    read -p "Stop existing backend and restart? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "uvicorn.*admin.*main"
        sleep 2
    else
        echo "Keeping existing backend running"
    fi
fi

# Start Admin Backend
echo "1️⃣ Starting Admin Backend (port 8002)..."
cd "$ADMIN_BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
if [ ! -f "venv/.installed" ]; then
    echo "📦 Installing dependencies..."
    pip install -q -r requirements.txt
    touch venv/.installed
fi

# Start backend in background
echo "✅ Starting admin backend on http://localhost:8002"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload > /tmp/admin_backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   Logs: tail -f /tmp/admin_backend.log"

# Wait a bit for backend to start
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "⚠️  Backend health check failed, but continuing..."
else
    echo "✅ Admin backend is healthy"
fi

# Start Admin Frontend
echo ""
echo "2️⃣ Starting Admin Frontend (port 5173)..."
cd "$ADMIN_FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
echo "✅ Starting admin frontend on http://localhost:5173"
npm run dev > /tmp/admin_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo "   Logs: tail -f /tmp/admin_frontend.log"

echo ""
echo "=========================================="
echo "✅ Admin Dashboard Started!"
echo "=========================================="
echo ""
echo "📊 Admin Backend:  http://localhost:8002"
echo "📚 API Docs:       http://localhost:8002/docs"
echo "🎨 Admin Frontend: http://localhost:5173"
echo ""
echo "📋 T1 Forms API: http://localhost:8002/api/v1/t1-forms"
echo ""
echo "🛑 To stop:"
echo "   pkill -f 'uvicorn.*admin.*main'"
echo "   pkill -f 'vite'"
echo ""
echo "📝 View logs:"
echo "   Backend:  tail -f /tmp/admin_backend.log"
echo "   Frontend: tail -f /tmp/admin_frontend.log"
echo ""

