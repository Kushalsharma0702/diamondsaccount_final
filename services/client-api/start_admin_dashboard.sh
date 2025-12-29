#!/bin/bash

# Admin Dashboard Quick Start Script
# This script starts the admin dashboard server with proper configuration

echo "=========================================="
echo "🚀 Starting Admin Dashboard Server"
echo "=========================================="
echo ""

# Set the working directory
cd "$(dirname "$0")"

# Check if admin-dashboard directory exists
if [ ! -d "admin-dashboard" ]; then
    echo "❌ Error: admin-dashboard directory not found"
    echo "   Please ensure you're running this script from services/client-api"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if admin backend is running on port 8002
if ! nc -z localhost 8002 2>/dev/null; then
    echo "⚠️  Warning: Admin backend (port 8002) is not running"
    echo "   Please start the admin backend first:"
    echo "   cd services/admin-api && uvicorn app.main:app --host 0.0.0.0 --port 8002"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Kill any process using port 8080
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🔄 Port 8080 is in use. Stopping existing process..."
    lsof -ti:8080 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Start the admin dashboard server
echo ""
echo "✅ Starting admin dashboard server..."
echo ""

python3 serve_admin_dashboard.py

echo ""
echo "=========================================="
echo "👋 Admin Dashboard Server Stopped"
echo "=========================================="
