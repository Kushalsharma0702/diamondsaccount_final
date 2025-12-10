#!/bin/bash

# Stop all services for Tax Hub Dashboard

echo "🛑 Stopping Tax Hub Dashboard Services..."
echo ""

# Stop Backend
echo "Stopping Backend..."
pkill -f "uvicorn app.main:app" && echo "✅ Backend stopped" || echo "⚠️  Backend was not running"

# Stop Frontend
echo "Stopping Frontend..."
pkill -f "vite" && echo "✅ Frontend stopped" || echo "⚠️  Frontend was not running"

echo ""
echo "✅ All services stopped"



