#!/bin/bash

# Complete Authentication Test Script
# Tests registration, OTP, verification, and login with Cognito

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$BASE_DIR"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TEST_EMAIL="kushalsharmacse@gmail.com"
TEST_PASSWORD="Test123!@#"
BASE_URL="http://localhost:8001/api/v1"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Cognito Authentication & Authorization Test${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if backend is running
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend is not running on port 8001${NC}"
    echo -e "${YELLOW}Please start the backend first: ./MASTER_CONTROL.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend is running${NC}"
echo ""

# Enable development mode for OTP
echo -e "${YELLOW}Enabling development mode...${NC}"
cd client_side
if ! grep -q "DEVELOPMENT_MODE=true" .env 2>/dev/null; then
    if grep -q "DEVELOPMENT_MODE" .env 2>/dev/null; then
        sed -i 's/DEVELOPMENT_MODE=.*/DEVELOPMENT_MODE=true/' .env
    else
        echo "DEVELOPMENT_MODE=true" >> .env
    fi
    echo -e "${GREEN}✅ Development mode enabled${NC}"
else
    echo -e "${GREEN}✅ Development mode already enabled${NC}"
fi
cd "$BASE_DIR"

# Run Python test script
echo ""
echo -e "${YELLOW}Running comprehensive authentication tests...${NC}"
echo ""

python3 "$BASE_DIR/scripts/testing/test_cognito_auth.py" << EOF
123456
y
EOF

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""


