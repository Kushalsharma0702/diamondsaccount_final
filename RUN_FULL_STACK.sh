#!/bin/bash

# Full Stack Startup Script
# Runs everything: Backends, Admin Dashboard, Ngrok, and Flutter Web

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 Starting Full Tax-Ease Stack${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Create logs directory
mkdir -p "$BASE_DIR/logs"

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to be ready...${NC}"
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    echo -e "${RED}❌ $service_name failed to start${NC}"
    return 1
}

# Function to kill process on port
kill_port() {
    local port=$1
    if check_port $port; then
        echo -e "${YELLOW}⚠️  Port $port is in use. Stopping existing service...${NC}"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# ============================================
# Step 1: Start Ngrok
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 1: Starting Ngrok Tunnel...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ! command -v ngrok &> /dev/null; then
    echo -e "${RED}❌ ngrok is not installed!${NC}"
    exit 1
fi

# Kill existing ngrok
pkill -f "ngrok http 8001" 2>/dev/null || true
sleep 2

echo -e "${YELLOW}Starting ngrok tunnel on port 8001...${NC}"
ngrok http 8001 > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!
sleep 5

# Get ngrok URL
MAX_RETRIES=15
RETRY=0
NGROK_URL=""

while [ $RETRY -lt $MAX_RETRIES ]; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$NGROK_URL" ]; then
        break
    fi
    sleep 2
    RETRY=$((RETRY+1))
done

if [ -z "$NGROK_URL" ]; then
    echo -e "${RED}❌ Failed to get ngrok URL${NC}"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✅ Ngrok tunnel established!${NC}"
echo -e "${BLUE}   Public URL: $NGROK_URL${NC}"
echo "$NGROK_URL" > /tmp/ngrok_url.txt
echo ""

# ============================================
# Step 2: Update Flutter Web with Ngrok URL
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 2: Updating Flutter Web with Ngrok URL...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

FLUTTER_DIR="$BASE_DIR/frontend/tax_ease-main (1)/tax_ease-main"
API_ENDPOINTS_FILE="$FLUTTER_DIR/lib/core/constants/api_endpoints.dart"

if [ -f "$API_ENDPOINTS_FILE" ]; then
    NEW_BASE_URL="${NGROK_URL}/api/v1"
    sed -i "s|static const String BASE_URL = '.*';|static const String BASE_URL = '$NEW_BASE_URL';|" "$API_ENDPOINTS_FILE"
    echo -e "${GREEN}✅ Flutter web updated!${NC}"
    echo -e "${BLUE}   New BASE_URL: $NEW_BASE_URL${NC}"
else
    echo -e "${YELLOW}⚠️  Flutter API endpoints file not found${NC}"
fi
echo ""

# ============================================
# Step 3: Start Client Backend
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 3: Starting Client Backend (Port 8001)...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

kill_port 8001

CLIENT_BACKEND_DIR="$BASE_DIR/client_side"
cd "$CLIENT_BACKEND_DIR"

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Load .env if exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults if not in .env
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db}"
export ADMIN_API_BASE_URL="${ADMIN_API_BASE_URL:-http://localhost:8002/api/v1}"
export STORAGE_BASE_DIR="${STORAGE_BASE_DIR:-$CLIENT_BACKEND_DIR/storage/uploads}"

echo -e "${YELLOW}Starting client backend...${NC}"
nohup uvicorn main:app --host 0.0.0.0 --port 8001 > "$BASE_DIR/logs/client-backend.log" 2>&1 &
CLIENT_BACKEND_PID=$!
echo "$CLIENT_BACKEND_PID" > "$BASE_DIR/logs/client-backend.pid"

wait_for_service "http://localhost:8001/health" "Client Backend" || true
echo -e "${GREEN}✅ Client Backend started on http://localhost:8001${NC}"
echo ""

# ============================================
# Step 4: Start Admin Backend
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 4: Starting Admin Backend (Port 8002)...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

kill_port 8002

ADMIN_BACKEND_DIR="$BASE_DIR/tax-hub-dashboard/backend"
cd "$ADMIN_BACKEND_DIR"

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Load .env if exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults if not in .env
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db}"

echo -e "${YELLOW}Starting admin backend...${NC}"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8002 > "$BASE_DIR/logs/admin-backend.log" 2>&1 &
ADMIN_BACKEND_PID=$!
echo "$ADMIN_BACKEND_PID" > "$BASE_DIR/logs/admin-backend.pid"

wait_for_service "http://localhost:8002/health" "Admin Backend" || true
echo -e "${GREEN}✅ Admin Backend started on http://localhost:8002${NC}"
echo ""

# ============================================
# Step 5: Start Admin Dashboard
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 5: Starting Admin Dashboard (Port 8080)...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

kill_port 8080

ADMIN_DASHBOARD_DIR="$BASE_DIR/tax-hub-dashboard"
cd "$ADMIN_DASHBOARD_DIR"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing npm dependencies...${NC}"
    npm install
fi

echo -e "${YELLOW}Starting admin dashboard...${NC}"
nohup npm run dev > "$BASE_DIR/logs/admin-dashboard.log" 2>&1 &
ADMIN_DASHBOARD_PID=$!
echo "$ADMIN_DASHBOARD_PID" > "$BASE_DIR/logs/admin-dashboard.pid"

sleep 5
echo -e "${GREEN}✅ Admin Dashboard started on http://localhost:8080${NC}"
echo ""

# ============================================
# Step 6: Start Flutter Web
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 6: Starting Flutter Web (Client Frontend)...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$FLUTTER_DIR"

if ! command -v flutter &> /dev/null; then
    echo -e "${RED}❌ Flutter is not installed or not in PATH${NC}"
    exit 1
fi

# Enable web support
flutter config --enable-web

echo -e "${YELLOW}Getting Flutter dependencies...${NC}"
flutter pub get

# Check if port 3000 is available (default Flutter web port)
kill_port 3000

echo -e "${YELLOW}Starting Flutter web on port 3000...${NC}"
echo -e "${YELLOW}(This may take a moment...)${NC}"

# Start Flutter web in background
nohup flutter run -d web-server --web-port 3000 > "$BASE_DIR/logs/flutter-web.log" 2>&1 &
FLUTTER_WEB_PID=$!
echo "$FLUTTER_WEB_PID" > "$BASE_DIR/logs/flutter-web.pid"

sleep 10

# Check if Flutter web is running
if check_port 3000; then
    echo -e "${GREEN}✅ Flutter Web started on http://localhost:3000${NC}"
else
    echo -e "${YELLOW}⚠️  Flutter web may still be starting. Check logs: $BASE_DIR/logs/flutter-web.log${NC}"
fi
echo ""

# ============================================
# Summary
# ============================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All Services Started!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}📍 Service URLs:${NC}"
echo -e "  • Client Backend:  ${BLUE}http://localhost:8001${NC}"
echo -e "  • Admin Backend:   ${BLUE}http://localhost:8002${NC}"
echo -e "  • Admin Dashboard: ${BLUE}http://localhost:8080${NC}"
echo -e "  • Flutter Web:     ${BLUE}http://localhost:3000${NC}"
echo -e "  • Ngrok URL:       ${BLUE}$NGROK_URL${NC}"
echo ""
echo -e "${GREEN}📋 Access Points:${NC}"
echo -e "  • Client Frontend (Web): ${BLUE}http://localhost:3000${NC}"
echo -e "  • Admin Dashboard:       ${BLUE}http://localhost:8080${NC}"
echo -e "  • Ngrok Dashboard:       ${BLUE}http://localhost:4040${NC}"
echo ""
echo -e "${YELLOW}📝 Logs Location: ${BASE_DIR}/logs/${NC}"
echo -e "${YELLOW}🛑 Stop all services: ${GREEN}./STOP_ALL.sh${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""


