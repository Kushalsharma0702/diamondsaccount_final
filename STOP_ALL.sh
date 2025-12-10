#!/bin/bash

# Stop All Services Script

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🛑 Stopping All Tax-Ease Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Stop services by PID files
if [ -f "$BASE_DIR/logs/client-backend.pid" ]; then
    PID=$(cat "$BASE_DIR/logs/client-backend.pid")
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID 2>/dev/null || true
        echo -e "${GREEN}✅ Stopped Client Backend (PID: $PID)${NC}"
    fi
fi

if [ -f "$BASE_DIR/logs/admin-backend.pid" ]; then
    PID=$(cat "$BASE_DIR/logs/admin-backend.pid")
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID 2>/dev/null || true
        echo -e "${GREEN}✅ Stopped Admin Backend (PID: $PID)${NC}"
    fi
fi

if [ -f "$BASE_DIR/logs/admin-dashboard.pid" ]; then
    PID=$(cat "$BASE_DIR/logs/admin-dashboard.pid")
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID 2>/dev/null || true
        echo -e "${GREEN}✅ Stopped Admin Dashboard (PID: $PID)${NC}"
    fi
fi

if [ -f "$BASE_DIR/logs/flutter-web.pid" ]; then
    PID=$(cat "$BASE_DIR/logs/flutter-web.pid")
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID 2>/dev/null || true
        echo -e "${GREEN}✅ Stopped Flutter Web (PID: $PID)${NC}"
    fi
fi

# Stop ngrok
pkill -f "ngrok http 8001" 2>/dev/null && echo -e "${GREEN}✅ Stopped Ngrok${NC}" || echo -e "${YELLOW}⚠️  Ngrok not running${NC}"

# Kill by port as fallback
for port in 8001 8002 8080 3000; do
    if lsof -ti :$port > /dev/null 2>&1; then
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✅ Cleared port $port${NC}"
    fi
done

echo ""
echo -e "${GREEN}✅ All services stopped!${NC}"
echo ""


