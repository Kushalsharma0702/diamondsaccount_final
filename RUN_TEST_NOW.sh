#!/bin/bash

# ========================================
# MASTER TEST SCRIPT - START EVERYTHING
# ========================================
# This script starts all services needed for end-to-end testing:
# - Client Backend (port 8001)
# - Admin Backend (port 8002)
# - Admin Dashboard (port 8080)
# - Ngrok tunnel (exposes 8001)
# - Updates Flutter app URL

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 STARTING COMPLETE TEST ENVIRONMENT${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    return 1
}

# Create logs directory
mkdir -p "$BASE_DIR/logs"

# ========================================
# PREREQUISITES CHECK
# ========================================
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check PostgreSQL
if ! command_exists psql; then
    echo -e "${RED}❌ PostgreSQL client not found${NC}"
    exit 1
fi

# Check Redis (optional)
if ! command_exists redis-cli; then
    echo -e "${YELLOW}⚠️  Redis CLI not found (Redis might still work)${NC}"
fi

# Check Python
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

# Check Node.js
if ! command_exists node; then
    echo -e "${RED}❌ Node.js not found${NC}"
    exit 1
fi

# Check ngrok
NGROK_AVAILABLE=false
if command_exists ngrok; then
    NGROK_AVAILABLE=true
    echo -e "${GREEN}✅ Ngrok found${NC}"
else
    echo -e "${YELLOW}⚠️  Ngrok not found - you'll need to start it manually${NC}"
fi

echo ""

# ========================================
# START CLIENT BACKEND
# ========================================
CLIENT_BACKEND_DIR="$BASE_DIR/client_side"
echo -e "${BLUE}📦 Starting Client Backend (Port 8001)...${NC}"

if check_port 8001; then
    echo -e "${YELLOW}⚠️  Port 8001 already in use. Skipping client backend.${NC}"
else
    cd "$CLIENT_BACKEND_DIR"
    
    # Create venv if needed
    if [ ! -d "venv" ]; then
        echo "   Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f "venv/.deps_installed" ]; then
        echo "   Installing dependencies..."
        pip install -q -r requirements.txt 2>/dev/null || true
        touch "venv/.deps_installed"
    fi
    
    # Set environment variables
    export DATABASE_URL="postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db"
    export ADMIN_API_BASE_URL="http://localhost:8002/api/v1"
    export STORAGE_BASE_DIR="$CLIENT_BACKEND_DIR/storage/uploads"
    
    # Start backend
    nohup uvicorn main:app --host 0.0.0.0 --port 8001 > "$BASE_DIR/logs/client-backend.log" 2>&1 &
    CLIENT_PID=$!
    echo "$CLIENT_PID" > "$BASE_DIR/logs/client-backend.pid"
    
    if wait_for_service "http://localhost:8001/health" "Client Backend"; then
        echo -e "${GREEN}✅ Client Backend started (PID: $CLIENT_PID)${NC}"
    else
        echo -e "${RED}❌ Client Backend failed to start${NC}"
        tail -20 "$BASE_DIR/logs/client-backend.log"
    fi
fi
echo ""

# ========================================
# START ADMIN BACKEND
# ========================================
ADMIN_BACKEND_DIR="$BASE_DIR/tax-hub-dashboard/backend"
echo -e "${BLUE}📦 Starting Admin Backend (Port 8002)...${NC}"

if check_port 8002; then
    echo -e "${YELLOW}⚠️  Port 8002 already in use. Skipping admin backend.${NC}"
else
    cd "$ADMIN_BACKEND_DIR"
    
    # Create venv if needed
    if [ ! -d "venv" ]; then
        echo "   Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install dependencies if needed
    if [ ! -f "venv/.deps_installed" ]; then
        echo "   Installing dependencies..."
        pip install -q -r requirements.txt 2>/dev/null || true
        touch "venv/.deps_installed"
    fi
    
    # Create .env if needed
    if [ ! -f ".env" ]; then
        echo "   Creating .env file..."
        cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:8080","http://localhost:5173"]
EOF
    fi
    
    # Start backend
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8002 > "$BASE_DIR/logs/admin-backend.log" 2>&1 &
    ADMIN_PID=$!
    echo "$ADMIN_PID" > "$BASE_DIR/logs/admin-backend.pid"
    
    if wait_for_service "http://localhost:8002/health" "Admin Backend"; then
        echo -e "${GREEN}✅ Admin Backend started (PID: $ADMIN_PID)${NC}"
    else
        echo -e "${RED}❌ Admin Backend failed to start${NC}"
        tail -20 "$BASE_DIR/logs/admin-backend.log"
    fi
fi
echo ""

# ========================================
# START ADMIN DASHBOARD
# ========================================
ADMIN_DASHBOARD_DIR="$BASE_DIR/tax-hub-dashboard"
echo -e "${BLUE}📦 Starting Admin Dashboard (Port 8080)...${NC}"

if check_port 8080; then
    echo -e "${YELLOW}⚠️  Port 8080 already in use. Skipping admin dashboard.${NC}"
else
    cd "$ADMIN_DASHBOARD_DIR"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "   Installing npm dependencies..."
        npm install --silent
    fi
    
    # Start dashboard
    nohup npm run dev > "$BASE_DIR/logs/admin-dashboard.log" 2>&1 &
    DASHBOARD_PID=$!
    echo "$DASHBOARD_PID" > "$BASE_DIR/logs/admin-dashboard.pid"
    
    sleep 5
    echo -e "${GREEN}✅ Admin Dashboard started (PID: $DASHBOARD_PID)${NC}"
fi
echo ""

# ========================================
# START NGROK
# ========================================
if [ "$NGROK_AVAILABLE" = true ]; then
    echo -e "${BLUE}📡 Starting Ngrok Tunnel...${NC}"
    
    # Kill existing ngrok
    pkill -f "ngrok http 8001" 2>/dev/null || true
    sleep 1
    
    # Start ngrok
    nohup ngrok http 8001 > "$BASE_DIR/logs/ngrok.log" 2>&1 &
    NGROK_PID=$!
    echo "$NGROK_PID" > "$BASE_DIR/logs/ngrok.pid"
    
    sleep 5
    
    # Get ngrok URL
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$NGROK_URL" ]; then
        echo "$NGROK_URL" > /tmp/ngrok_url.txt
        echo -e "${GREEN}✅ Ngrok tunnel established!${NC}"
        echo -e "${GREEN}   Public URL: $NGROK_URL${NC}"
        
        # Update Flutter app
        FLUTTER_DIR="$BASE_DIR/frontend/tax_ease-main (1)/tax_ease-main"
        API_ENDPOINTS_FILE="$FLUTTER_DIR/lib/core/constants/api_endpoints.dart"
        
        if [ -f "$API_ENDPOINTS_FILE" ]; then
            echo -e "${BLUE}📱 Updating Flutter app with ngrok URL...${NC}"
            sed -i "s|static const String BASE_URL = '.*';|static const String BASE_URL = '$NGROK_URL/api/v1';|" "$API_ENDPOINTS_FILE"
            echo -e "${GREEN}✅ Flutter app updated!${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Could not get ngrok URL. Check: http://localhost:4040${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Ngrok not available. Start manually: ngrok http 8001${NC}"
fi
echo ""

# ========================================
# SUMMARY
# ========================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ ALL SERVICES STARTED!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}📍 Service URLs:${NC}"
echo -e "  • Client Backend:  ${BLUE}http://localhost:8001${NC}"
echo -e "  • Client Backend Docs: ${BLUE}http://localhost:8001/docs${NC}"
echo -e "  • Admin Backend:   ${BLUE}http://localhost:8002${NC}"
echo -e "  • Admin Backend Docs: ${BLUE}http://localhost:8002/docs${NC}"
echo -e "  • Admin Dashboard: ${BLUE}http://localhost:8080${NC}"
if [ -n "$NGROK_URL" ]; then
    echo -e "  • Ngrok URL:       ${BLUE}$NGROK_URL${NC}"
    echo -e "  • Flutter API:     ${BLUE}$NGROK_URL/api/v1${NC}"
fi
echo ""
echo -e "${GREEN}🔐 Admin Login:${NC}"
echo -e "  • Email: ${BLUE}superadmin@taxease.ca${NC}"
echo -e "  • Password: ${BLUE}demo123${NC}"
echo ""
echo -e "${GREEN}📋 Next Steps:${NC}"
echo -e "  1. Build Flutter APK: ${YELLOW}./build-flutter-apk.sh${NC}"
echo -e "  2. Install APK on device"
echo -e "  3. Upload a file from Flutter app"
echo -e "  4. Check admin dashboard: ${BLUE}http://localhost:8080${NC}"
echo -e "  5. Check database: ${YELLOW}psql -U postgres -d taxease_db${NC}"
echo ""
echo -e "${YELLOW}📝 Logs: ${BASE_DIR}/logs/${NC}"
echo -e "${YELLOW}🛑 Stop all: ${GREEN}./stop-all-services.sh${NC}"
echo ""


