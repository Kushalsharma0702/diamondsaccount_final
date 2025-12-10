#!/bin/bash

# Master Script: Complete Setup and Start
# 1. Creates .env files in required directories
# 2. Starts ngrok and gets URL
# 3. Updates Flutter app with ngrok URL
# 4. Builds Flutter APK
# 5. Starts all services

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
echo -e "${BLUE}🚀 Tax-Ease Complete Setup & Start${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================
# STEP 1: Create .env files
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 1: Creating .env files...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Client Backend .env
CLIENT_ENV="$BASE_DIR/client_side/.env"
if [ ! -f "$CLIENT_ENV" ]; then
    echo -e "${YELLOW}Creating client_side/.env...${NC}"
    cat > "$CLIENT_ENV" << 'EOF'
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db

# AWS Cognito Configuration
COGNITO_USER_POOL_ID=ca-central-1_FP2WE41eW
COGNITO_CLIENT_ID=504mgtvq1h97vlml90c3iibnt0
AWS_REGION=ca-central-1
AWS_ACCESS_KEY_ID=AKIA3BMJ25BIYDGPA47X
AWS_SECRET_ACCESS_KEY=BDSPNqu7MlgZ38C1yPMEOZ2X43DgvpJYOMc4ddVA1CJl

# AWS SES Configuration
AWS_SES_FROM_EMAIL=diamondacc.project@gmail.com

# OTP Configuration
OTP_EXPIRY_MINUTES=5
OTP_LENGTH=6

# Development Mode
DEVELOPMENT_MODE=false
DEVELOPER_OTP=123456
SKIP_EMAIL_VERIFICATION=false

# Storage Configuration
STORAGE_BASE_DIR=./storage/uploads

# Admin Backend URL
ADMIN_API_BASE_URL=http://localhost:8002/api/v1

# JWT Configuration
JWT_SECRET=your-jwt-secret-key-change-in-production
JWT_REFRESH_SECRET=your-jwt-refresh-secret-key-change-in-production
EOF
    echo -e "${GREEN}✅ Created client_side/.env${NC}"
else
    echo -e "${YELLOW}⚠️  client_side/.env already exists (keeping existing file)${NC}"
fi

# Admin Backend .env
ADMIN_ENV="$BASE_DIR/tax-hub-dashboard/backend/.env"
if [ ! -f "$ADMIN_ENV" ]; then
    echo -e "${YELLOW}Creating tax-hub-dashboard/backend/.env...${NC}"
    cat > "$ADMIN_ENV" << 'EOF'
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:Kushal07@localhost:5432/taxease_db

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production

# CORS Configuration
CORS_ORIGINS=["http://localhost:8080","http://localhost:5173"]
EOF
    echo -e "${GREEN}✅ Created tax-hub-dashboard/backend/.env${NC}"
else
    echo -e "${YELLOW}⚠️  tax-hub-dashboard/backend/.env already exists (keeping existing file)${NC}"
fi

echo ""
sleep 1

# ============================================
# STEP 2: Start ngrok and get URL
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 2: Starting ngrok tunnel...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED}❌ ngrok is not installed!${NC}"
    echo "Please install ngrok:"
    echo "  - Download from: https://ngrok.com/download"
    echo "  - Or via snap: sudo snap install ngrok"
    exit 1
fi

# Kill existing ngrok processes
pkill -f "ngrok http 8001" 2>/dev/null || true
sleep 2

# Start ngrok in background
echo -e "${YELLOW}Starting ngrok tunnel on port 8001...${NC}"
ngrok http 8001 > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!
sleep 5

# Get ngrok URL
MAX_RETRIES=15
RETRY=0
NGROK_URL=""

echo -e "${YELLOW}Waiting for ngrok to establish tunnel...${NC}"
while [ $RETRY -lt $MAX_RETRIES ]; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$NGROK_URL" ]; then
        break
    fi
    echo "  Attempt $((RETRY+1))/$MAX_RETRIES..."
    sleep 2
    RETRY=$((RETRY+1))
done

if [ -z "$NGROK_URL" ]; then
    echo -e "${RED}❌ Failed to get ngrok URL after $MAX_RETRIES attempts${NC}"
    echo "Please check ngrok manually: http://localhost:4040"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✅ Ngrok tunnel established!${NC}"
echo -e "${BLUE}   Public URL: $NGROK_URL${NC}"
echo "$NGROK_URL" > /tmp/ngrok_url.txt
echo ""

# ============================================
# STEP 3: Update Flutter app with ngrok URL
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 3: Updating Flutter app with ngrok URL...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

FLUTTER_DIR="$BASE_DIR/frontend/tax_ease-main (1)/tax_ease-main"
API_ENDPOINTS_FILE="$FLUTTER_DIR/lib/core/constants/api_endpoints.dart"

if [ ! -f "$API_ENDPOINTS_FILE" ]; then
    echo -e "${RED}❌ Flutter API endpoints file not found: $API_ENDPOINTS_FILE${NC}"
    exit 1
fi

# Backup original file
BACKUP_FILE="${API_ENDPOINTS_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$API_ENDPOINTS_FILE" "$BACKUP_FILE"
echo -e "${YELLOW}Backup created: $BACKUP_FILE${NC}"

# Update BASE_URL
NEW_BASE_URL="${NGROK_URL}/api/v1"
sed -i "s|static const String BASE_URL = '.*';|static const String BASE_URL = '$NEW_BASE_URL';|" "$API_ENDPOINTS_FILE"

echo -e "${GREEN}✅ Flutter app updated!${NC}"
echo -e "${BLUE}   New BASE_URL: $NEW_BASE_URL${NC}"
echo ""

# ============================================
# STEP 4: Build Flutter APK
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 4: Building Flutter APK...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ ! -d "$FLUTTER_DIR" ]; then
    echo -e "${RED}❌ Flutter directory not found: $FLUTTER_DIR${NC}"
    exit 1
fi

cd "$FLUTTER_DIR"

if ! command -v flutter &> /dev/null; then
    echo -e "${RED}❌ Flutter is not installed or not in PATH${NC}"
    echo "Please install Flutter: https://flutter.dev/docs/get-started/install"
    exit 1
fi

echo -e "${YELLOW}Cleaning previous builds...${NC}"
flutter clean > /dev/null 2>&1 || true

echo -e "${YELLOW}Getting dependencies...${NC}"
flutter pub get

echo -e "${YELLOW}Building APK (this may take a few minutes)...${NC}"
if flutter build apk --release; then
    APK_PATH="build/app/outputs/flutter-apk/app-release.apk"
    if [ -f "$APK_PATH" ]; then
        APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
        echo -e "${GREEN}✅ APK built successfully!${NC}"
        echo -e "${BLUE}   Location: $FLUTTER_DIR/$APK_PATH${NC}"
        echo -e "${BLUE}   Size: $APK_SIZE${NC}"
    else
        echo -e "${RED}❌ APK file not found after build${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ APK build failed!${NC}"
    exit 1
fi

cd "$BASE_DIR"
echo ""

# ============================================
# STEP 5: Start all services
# ============================================
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 5: Starting all services...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Source the start-all-services script
bash "$BASE_DIR/scripts/setup/start-all-services.sh"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Complete Setup & Start Finished!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}📍 Service URLs:${NC}"
echo -e "  • Client Backend:  ${BLUE}http://localhost:8001${NC}"
echo -e "  • Admin Backend:   ${BLUE}http://localhost:8002${NC}"
echo -e "  • Admin Dashboard: ${BLUE}http://localhost:8080${NC}"
echo -e "  • Ngrok URL:       ${BLUE}$NGROK_URL${NC}"
echo ""
echo -e "${GREEN}📱 Flutter APK:${NC}"
echo -e "  • Location: ${BLUE}$FLUTTER_DIR/$APK_PATH${NC}"
echo -e "  • Size: ${BLUE}$APK_SIZE${NC}"
echo ""
echo -e "${GREEN}📋 Next Steps:${NC}"
echo -e "  1. Install APK on device:"
echo -e "     ${YELLOW}adb install $FLUTTER_DIR/$APK_PATH${NC}"
echo -e "  2. Test file upload from Flutter app"
echo -e "  3. Check admin dashboard: ${BLUE}http://localhost:8080${NC}"
echo ""
echo -e "${YELLOW}📝 Logs location: ${BASE_DIR}/logs/${NC}"
echo -e "${YELLOW}🛑 Stop all services: ${GREEN}./scripts/setup/stop-all-services.sh${NC}"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""



