#!/bin/bash

# Master Control Script
# Interactive script to start or stop all Tax-Ease services

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
echo -e "${BLUE}🎛️  Tax-Ease Master Control${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Function to stop all services
stop_all_services() {
    echo -e "${YELLOW}🛑 Stopping all services...${NC}"
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
    if pkill -f "ngrok http 8001" 2>/dev/null; then
        echo -e "${GREEN}✅ Stopped Ngrok${NC}"
    fi
    
    # Kill by port as fallback
    for port in 8001 8002 8080 3000; do
        if lsof -ti :$port > /dev/null 2>&1; then
            lsof -ti :$port | xargs kill -9 2>/dev/null || true
            echo -e "${GREEN}✅ Cleared port $port${NC}"
        fi
    done
    
    # Wait a moment for processes to fully terminate
    sleep 2
    
    echo ""
    echo -e "${GREEN}✅ All services stopped!${NC}"
    echo ""
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
    echo -e "${YELLOW}⚠️  $service_name may still be starting...${NC}"
    return 1
}

# Function to start all services
start_all_services() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🚀 Starting All Services${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Create logs directory
    mkdir -p "$BASE_DIR/logs"
    
    # Step 1: Start Ngrok
    echo -e "${CYAN}Step 1: Starting Ngrok Tunnel...${NC}"
    
    if ! command -v ngrok &> /dev/null; then
        echo -e "${RED}❌ ngrok is not installed!${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Starting ngrok tunnel on port 8001...${NC}"
    ngrok http 8001 > /tmp/ngrok.log 2>&1 &
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
    
    if [ -n "$NGROK_URL" ]; then
        echo -e "${GREEN}✅ Ngrok tunnel established!${NC}"
        echo -e "${BLUE}   Public URL: $NGROK_URL${NC}"
        echo "$NGROK_URL" > /tmp/ngrok_url.txt
    else
        echo -e "${YELLOW}⚠️  Could not get ngrok URL (may still be starting)${NC}"
    fi
    echo ""
    
    # Step 2: Update Flutter Web with Ngrok URL
    echo -e "${CYAN}Step 2: Updating Flutter Web with Ngrok URL...${NC}"
    
    # Try to find Flutter app directory (prefer mobile-app)
    FLUTTER_DIR=""
    if [ -d "$BASE_DIR/mobile-app" ]; then
        FLUTTER_DIR="$BASE_DIR/mobile-app"
    elif [ -d "$BASE_DIR/frontend/tax_ease-main (1)/tax_ease-main" ]; then
        FLUTTER_DIR="$BASE_DIR/frontend/tax_ease-main (1)/tax_ease-main"
    fi
    
    if [ -n "$FLUTTER_DIR" ] && [ -d "$FLUTTER_DIR" ]; then
        API_ENDPOINTS_FILE="$FLUTTER_DIR/lib/core/constants/api_endpoints.dart"
        if [ -f "$API_ENDPOINTS_FILE" ] && [ -n "$NGROK_URL" ]; then
            NEW_BASE_URL="${NGROK_URL}/api/v1"
            sed -i "s|static const String BASE_URL = '.*';|static const String BASE_URL = '$NEW_BASE_URL';|" "$API_ENDPOINTS_FILE"
            echo -e "${GREEN}✅ Flutter web updated!${NC}"
            echo -e "${BLUE}   New BASE_URL: $NEW_BASE_URL${NC}"
        else
            echo -e "${YELLOW}⚠️  Skipping Flutter URL update (file not found or no ngrok URL)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Flutter directory not found. Skipping URL update.${NC}"
    fi
    echo ""
    
    # Step 3: Start Client Backend
    echo -e "${CYAN}Step 3: Starting Client Backend (Port 8001)...${NC}"
    
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
    
    # Step 4: Start Admin Backend
    echo -e "${CYAN}Step 4: Starting Admin Backend (Port 8002)...${NC}"
    
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
    
    export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db}"
    
    echo -e "${YELLOW}Starting admin backend...${NC}"
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8002 > "$BASE_DIR/logs/admin-backend.log" 2>&1 &
    ADMIN_BACKEND_PID=$!
    echo "$ADMIN_BACKEND_PID" > "$BASE_DIR/logs/admin-backend.pid"
    
    wait_for_service "http://localhost:8002/health" "Admin Backend" || true
    echo -e "${GREEN}✅ Admin Backend started on http://localhost:8002${NC}"
    echo ""
    
    # Step 5: Start Admin Dashboard
    echo -e "${CYAN}Step 5: Starting Admin Dashboard (Port 8080)...${NC}"
    
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
    
    # Step 6: Start Flutter Web
    echo -e "${CYAN}Step 6: Starting Flutter Web (Client Frontend)...${NC}"
    
    # Try to find Flutter app directory (prefer mobile-app)
    FLUTTER_APP_DIR=""
    if [ -d "$BASE_DIR/mobile-app" ]; then
        FLUTTER_APP_DIR="$BASE_DIR/mobile-app"
    elif [ -d "$BASE_DIR/frontend/tax_ease-main (1)/tax_ease-main" ]; then
        FLUTTER_APP_DIR="$BASE_DIR/frontend/tax_ease-main (1)/tax_ease-main"
    fi
    
    if [ -z "$FLUTTER_APP_DIR" ] || [ ! -d "$FLUTTER_APP_DIR" ]; then
        echo -e "${YELLOW}⚠️  Flutter app directory not found. Skipping Flutter Web.${NC}"
        echo -e "${YELLOW}   Expected: $BASE_DIR/mobile-app or $BASE_DIR/frontend/tax_ease-main (1)/tax_ease-main${NC}"
    elif ! command -v flutter &> /dev/null; then
        echo -e "${RED}❌ Flutter is not installed or not in PATH${NC}"
        echo -e "${YELLOW}⚠️  Skipping Flutter Web${NC}"
    else
        cd "$FLUTTER_APP_DIR"
        flutter config --enable-web > /dev/null 2>&1
        echo -e "${YELLOW}Getting Flutter dependencies...${NC}"
        flutter pub get > /dev/null 2>&1
        
        echo -e "${YELLOW}Starting Flutter web on port 3000...${NC}"
        echo -e "${YELLOW}⚠️  IMPORTANT: For Google Sign-In to work, add http://localhost:3000 to:${NC}"
        echo -e "${YELLOW}   Firebase Console > Authentication > Sign-in method > Google > Web client ID${NC}"
        echo -e "${YELLOW}   Authorized JavaScript origins: http://localhost:3000${NC}"
        nohup flutter run -d web-server --web-port 3000 --web-hostname localhost > "$BASE_DIR/logs/flutter-web.log" 2>&1 &
        FLUTTER_WEB_PID=$!
        echo "$FLUTTER_WEB_PID" > "$BASE_DIR/logs/flutter-web.pid"
        
        sleep 10
        
        if check_port 3000; then
            echo -e "${GREEN}✅ Flutter Web started on http://localhost:3000${NC}"
        else
            echo -e "${YELLOW}⚠️  Flutter web may still be starting. Check logs: $BASE_DIR/logs/flutter-web.log${NC}"
        fi
    fi
    echo ""
    
    # Summary
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ All Services Started!${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}📍 Service URLs:${NC}"
    echo -e "  • Client Backend:  ${BLUE}http://localhost:8001${NC}"
    echo -e "  • Admin Backend:   ${BLUE}http://localhost:8002${NC}"
    echo -e "  • Admin Dashboard: ${BLUE}http://localhost:8080${NC}"
    echo -e "  • Flutter Web:     ${BLUE}http://localhost:3000${NC}"
    if [ -n "$NGROK_URL" ]; then
        echo -e "  • Ngrok URL:       ${BLUE}$NGROK_URL${NC}"
    fi
    echo ""
    echo -e "${YELLOW}📝 Logs Location: ${BASE_DIR}/logs/${NC}"
    echo ""
}

# Show current status
echo -e "${CYAN}Current Service Status:${NC}"
echo ""
SERVICES_RUNNING=0

if check_port 8001; then
    echo -e "  ${GREEN}●${NC} Client Backend (8001) - ${GREEN}Running${NC}"
    SERVICES_RUNNING=$((SERVICES_RUNNING + 1))
else
    echo -e "  ${RED}●${NC} Client Backend (8001) - ${RED}Stopped${NC}"
fi

if check_port 8002; then
    echo -e "  ${GREEN}●${NC} Admin Backend (8002) - ${GREEN}Running${NC}"
    SERVICES_RUNNING=$((SERVICES_RUNNING + 1))
else
    echo -e "  ${RED}●${NC} Admin Backend (8002) - ${RED}Stopped${NC}"
fi

if check_port 8080; then
    echo -e "  ${GREEN}●${NC} Admin Dashboard (8080) - ${GREEN}Running${NC}"
    SERVICES_RUNNING=$((SERVICES_RUNNING + 1))
else
    echo -e "  ${RED}●${NC} Admin Dashboard (8080) - ${RED}Stopped${NC}"
fi

if check_port 3000; then
    echo -e "  ${GREEN}●${NC} Flutter Web (3000) - ${GREEN}Running${NC}"
    SERVICES_RUNNING=$((SERVICES_RUNNING + 1))
else
    echo -e "  ${RED}●${NC} Flutter Web (3000) - ${RED}Stopped${NC}"
fi

if pgrep -f "ngrok http 8001" > /dev/null; then
    echo -e "  ${GREEN}●${NC} Ngrok - ${GREEN}Running${NC}"
    SERVICES_RUNNING=$((SERVICES_RUNNING + 1))
else
    echo -e "  ${RED}●${NC} Ngrok - ${RED}Stopped${NC}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Ask user what they want to do
echo -e "${YELLOW}What would you like to do?${NC}"
echo ""
echo -e "  ${GREEN}1)${NC} Start all services (will stop existing services first)"
echo -e "  ${RED}2)${NC} Stop all services"
echo -e "  ${BLUE}3)${NC} Exit"
echo ""
read -p "Enter your choice (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}⚠️  This will stop all existing services and start fresh.${NC}"
        read -p "Continue? (y/n): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            stop_all_services
            start_all_services
        else
            echo -e "${YELLOW}Cancelled.${NC}"
            exit 0
        fi
        ;;
    2)
        echo ""
        read -p "Stop all services? (y/n): " confirm
        if [[ $confirm =~ ^[Yy]$ ]]; then
            stop_all_services
        else
            echo -e "${YELLOW}Cancelled.${NC}"
            exit 0
        fi
        ;;
    3)
        echo -e "${YELLOW}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting...${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""


