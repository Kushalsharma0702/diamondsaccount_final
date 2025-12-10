#!/bin/bash

# Start all services for Tax Hub Dashboard

set -e

echo "🚀 Starting Tax Hub Dashboard Services..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if PostgreSQL is running
echo -e "${YELLOW}Checking PostgreSQL...${NC}"
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not running. Please start PostgreSQL first.${NC}"
    exit 1
fi

# Check if Redis is running (optional but recommended)
echo -e "${YELLOW}Checking Redis...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠️  Redis is not running (optional)${NC}"
fi

# Start Backend
echo ""
echo -e "${YELLOW}Starting Backend...${NC}"
cd "$(dirname "$0")/backend"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Please run setup first.${NC}"
    exit 1
fi

source venv/bin/activate

# Kill existing backend if running
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 1

# Start backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend started
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend started on http://localhost:8000${NC}"
    echo "   PID: $BACKEND_PID"
else
    echo -e "${RED}❌ Backend failed to start. Check backend.log for details.${NC}"
    exit 1
fi

# Start Frontend
echo ""
echo -e "${YELLOW}Starting Frontend...${NC}"
cd "$(dirname "$0")"

# Kill existing frontend if running
pkill -f "vite" 2>/dev/null || true
sleep 1

# Start frontend
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

# Check if frontend started
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend started on http://localhost:8080${NC}"
    echo "   PID: $FRONTEND_PID"
else
    echo -e "${YELLOW}⚠️  Frontend may still be starting...${NC}"
fi

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 All Services Started!${NC}"
echo "=========================================="
echo ""
echo "📍 Backend:  http://localhost:8000"
echo "📍 Frontend: http://localhost:8080"
echo "📍 API Docs: http://localhost:8000/docs"
echo ""
echo "🔑 Login Credentials:"
echo "   Email:    superadmin@taxease.ca"
echo "   Password: demo123"
echo ""
echo "📊 Database: taxhub_db (PostgreSQL)"
echo ""
echo "📝 Logs:"
echo "   Backend:  backend/backend.log"
echo "   Frontend: frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "   ./stop-all.sh"
echo ""
echo "=========================================="





