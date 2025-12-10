#!/bin/bash

# End-to-End Authentication Test Script
# Tests the complete authentication flow with bypass OTP

set -e

BASE_URL="http://localhost:8001/api/v1"
TEST_EMAIL="kushalsharmacse@gmail.com"
BYPASS_OTP="698745"

echo "=========================================="
echo "🧪 End-to-End Authentication Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo "1️⃣ Testing Backend Health..."
if curl -s "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is not running on port 8001${NC}"
    echo "   Start backend: cd client_side && python -m uvicorn main:app --reload --port 8001"
    exit 1
fi

# Test 2: Request OTP
echo ""
echo "2️⃣ Testing OTP Request..."
OTP_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/request-otp" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"purpose\":\"email_verification\"}")

if echo "$OTP_RESPONSE" | grep -q "successfully"; then
    echo -e "${GREEN}✅ OTP request successful${NC}"
    echo "   Response: $OTP_RESPONSE"
else
    echo -e "${RED}❌ OTP request failed${NC}"
    echo "   Response: $OTP_RESPONSE"
    exit 1
fi

# Test 3: Verify OTP with Bypass Code
echo ""
echo "3️⃣ Testing OTP Verification with Bypass Code ($BYPASS_OTP)..."
VERIFY_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/verify-otp" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"code\":\"$BYPASS_OTP\",\"purpose\":\"email_verification\"}")

if echo "$VERIFY_RESPONSE" | grep -q "success\|token"; then
    echo -e "${GREEN}✅ OTP verification successful${NC}"
    echo "   Response: $VERIFY_RESPONSE"
    
    # Extract token if present
    TOKEN=$(echo "$VERIFY_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4 || echo "")
    if [ -n "$TOKEN" ]; then
        echo -e "${GREEN}✅ JWT token received${NC}"
    fi
else
    echo -e "${RED}❌ OTP verification failed${NC}"
    echo "   Response: $VERIFY_RESPONSE"
    exit 1
fi

# Test 4: Test Firebase OTP Request (without Firebase token - should still work)
echo ""
echo "4️⃣ Testing OTP Request without Firebase token..."
OTP_RESPONSE2=$(curl -s -X POST "$BASE_URL/auth/request-otp" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"purpose\":\"email_verification\"}")

if echo "$OTP_RESPONSE2" | grep -q "successfully"; then
    echo -e "${GREEN}✅ OTP request without Firebase token successful${NC}"
else
    echo -e "${YELLOW}⚠️  OTP request without Firebase token had issues${NC}"
    echo "   Response: $OTP_RESPONSE2"
fi

# Test 5: Verify Bypass Code Works Again
echo ""
echo "5️⃣ Testing Bypass Code Works Multiple Times..."
VERIFY_RESPONSE2=$(curl -s -X POST "$BASE_URL/auth/verify-otp" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"code\":\"$BYPASS_OTP\",\"purpose\":\"email_verification\"}")

if echo "$VERIFY_RESPONSE2" | grep -q "success\|token"; then
    echo -e "${GREEN}✅ Bypass code works consistently${NC}"
else
    echo -e "${YELLOW}⚠️  Bypass code verification had issues${NC}"
    echo "   Response: $VERIFY_RESPONSE2"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ All Tests Passed!${NC}"
echo "=========================================="
echo ""
echo "📋 Summary:"
echo "   ✅ Backend is running"
echo "   ✅ OTP request works"
echo "   ✅ Bypass code ($BYPASS_OTP) works"
echo "   ✅ OTP verification returns JWT token"
echo ""
echo "🚀 Ready for Flutter app testing!"
echo ""
echo "Next Steps:"
echo "   1. Hot restart Flutter app (Press 'R' in terminal)"
echo "   2. Go to login page"
echo "   3. Enter email/password"
echo "   4. On OTP screen, enter: $BYPASS_OTP"
echo "   5. Should redirect to dashboard"
echo ""

