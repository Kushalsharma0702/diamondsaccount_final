#!/bin/bash

# Master script to start everything for testing
# This script will:
# 1. Start all services
# 2. Start ngrok
# 3. Update Flutter app URL
# 4. Show final status

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🚀 QUICK TEST START - Complete Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Step 1: Start all services
echo -e "${YELLOW}Step 1: Starting all services...${NC}"
"$BASE_DIR/start-all-services.sh"
sleep 5
echo ""

# Step 2: Start ngrok
echo -e "${YELLOW}Step 2: Starting ngrok tunnel...${NC}"
echo "This will run in the background..."
"$BASE_DIR/start-ngrok.sh" > /tmp/ngrok-startup.log 2>&1 &
NGROK_PID=$!
sleep 5

# Get ngrok URL
if [ -f /tmp/ngrok_url.txt ]; then
    NGROK_URL=$(cat /tmp/ngrok_url.txt)
    echo -e "${GREEN}✅ Ngrok URL: $NGROK_URL${NC}"
else
    echo -e "${YELLOW}⏳ Waiting for ngrok URL...${NC}"
    sleep 3
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)
    
    if [ -n "$NGROK_URL" ]; then
        echo "$NGROK_URL" > /tmp/ngrok_url.txt
        echo -e "${GREEN}✅ Ngrok URL: $NGROK_URL${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not get ngrok URL automatically${NC}"
        echo "Please check: http://localhost:4040"
        read -p "Enter ngrok URL manually (or press Enter to skip): " NGROK_URL
    fi
fi

# Step 3: Update Flutter app
if [ -n "$NGROK_URL" ]; then
    echo ""
    echo -e "${YELLOW}Step 3: Updating Flutter app with ngrok URL...${NC}"
    "$BASE_DIR/update-flutter-url.sh" ngrok "$NGROK_URL"
else
    echo -e "${YELLOW}⚠️  Skipping Flutter URL update (no ngrok URL)${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}📍 Service URLs:${NC}"
echo -e "  • Client Backend:  ${BLUE}http://localhost:8001${NC}"
echo -e "  • Admin Backend:   ${BLUE}http://localhost:8002${NC}"
echo -e "  • Admin Dashboard: ${BLUE}http://localhost:8080${NC}"
if [ -n "$NGROK_URL" ]; then
    echo -e "  • Ngrok URL:       ${BLUE}$NGROK_URL${NC}"
    echo -e "  • Flutter API:     ${BLUE}$NGROK_URL/api/v1${NC}"
fi
echo ""
echo -e "${GREEN}📋 Next Steps:${NC}"
echo -e "  1. Build Flutter APK: ${YELLOW}./build-flutter-apk.sh${NC}"
echo -e "  2. Install APK on device"
echo -e "  3. Test file upload"
echo -e "  4. Check admin dashboard"
echo ""
echo -e "${YELLOW}🛑 Stop all services: ${GREEN}./stop-all-services.sh${NC}"
echo ""




