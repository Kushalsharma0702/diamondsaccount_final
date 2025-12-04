#!/bin/bash

# Start all services for end-to-end testing
# - Client Backend (port 8001)
# - Admin Backend (port 8002)
# - Admin Dashboard (port 8080)
# - Ngrok tunnel for client backend

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT_BACKEND_DIR="$BASE_DIR/client_side"
ADMIN_BACKEND_DIR="$BASE_DIR/tax-hub-dashboard/backend"
ADMIN_DASHBOARD_DIR="$BASE_DIR/tax-hub-dashboard"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 Starting All Tax-Ease Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

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

# Create log directory
mkdir -p "$BASE_DIR/logs"

# Start Client Backend
echo -e "${BLUE}📦 Starting Client Backend (Port 8001)...${NC}"
if check_port 8001; then
    echo -e "${YELLOW}⚠️  Port 8001 is already in use. Skipping client backend.${NC}"
else
    cd "$CLIENT_BACKEND_DIR"
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    source venv/bin/activate
    export DATABASE_URL="postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db"
    export ADMIN_API_BASE_URL="http://localhost:8002/api/v1"
    export STORAGE_BASE_DIR="$CLIENT_BACKEND_DIR/storage/uploads"
    
    nohup uvicorn main:app --host 0.0.0.0 --port 8001 > "$BASE_DIR/logs/client-backend.log" 2>&1 &
    CLIENT_BACKEND_PID=$!
    echo "Client Backend PID: $CLIENT_BACKEND_PID" > "$BASE_DIR/logs/client-backend.pid"
    
    wait_for_service "http://localhost:8001/health" "Client Backend"
    echo -e "${GREEN}✅ Client Backend started on http://localhost:8001${NC}"
fi
echo ""

# Start Admin Backend
echo -e "${BLUE}📦 Starting Admin Backend (Port 8002)...${NC}"
if check_port 8002; then
    echo -e "${YELLOW}⚠️  Port 8002 is already in use. Skipping admin backend.${NC}"
else
    cd "$ADMIN_BACKEND_DIR"
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    # Update .env if needed
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=["http://localhost:8080","http://localhost:5173"]
EOF
    fi
    
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8002 > "$BASE_DIR/logs/admin-backend.log" 2>&1 &
    ADMIN_BACKEND_PID=$!
    echo "Admin Backend PID: $ADMIN_BACKEND_PID" > "$BASE_DIR/logs/admin-backend.pid"
    
    wait_for_service "http://localhost:8002/health" "Admin Backend"
    echo -e "${GREEN}✅ Admin Backend started on http://localhost:8002${NC}"
fi
echo ""

# Start Admin Dashboard
echo -e "${BLUE}📦 Starting Admin Dashboard (Port 8080)...${NC}"
if check_port 8080; then
    echo -e "${YELLOW}⚠️  Port 8080 is already in use. Skipping admin dashboard.${NC}"
else
    cd "$ADMIN_DASHBOARD_DIR"
    if [ ! -d "node_modules" ]; then
        echo "Installing npm dependencies..."
        npm install
    fi
    
    nohup npm run dev > "$BASE_DIR/logs/admin-dashboard.log" 2>&1 &
    ADMIN_DASHBOARD_PID=$!
    echo "Admin Dashboard PID: $ADMIN_DASHBOARD_PID" > "$BASE_DIR/logs/admin-dashboard.pid"
    
    sleep 5  # Wait for Vite to start
    echo -e "${GREEN}✅ Admin Dashboard started on http://localhost:8080${NC}"
fi
echo ""

# Start Ngrok (optional - user can start separately)
echo -e "${BLUE}📡 Ngrok Setup${NC}"
echo -e "${YELLOW}To start ngrok tunnel, run:${NC}"
echo -e "  ${GREEN}./start-ngrok.sh${NC}"
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All Services Started!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}📍 Service URLs:${NC}"
echo -e "  • Client Backend:  ${BLUE}http://localhost:8001${NC}"
echo -e "  • Admin Backend:   ${BLUE}http://localhost:8002${NC}"
echo -e "  • Admin Dashboard: ${BLUE}http://localhost:8080${NC}"
echo ""
echo -e "${GREEN}📋 Next Steps:${NC}"
echo -e "  1. Start ngrok: ${YELLOW}./start-ngrok.sh${NC}"
echo -e "  2. Update Flutter app with ngrok URL"
echo -e "  3. Build Flutter APK"
echo -e "  4. Test file upload"
echo ""
echo -e "${YELLOW}📝 Logs are in: ${BASE_DIR}/logs/${NC}"
echo -e "${YELLOW}🛑 Stop all services: ${GREEN}./stop-all-services.sh${NC}"
echo ""


