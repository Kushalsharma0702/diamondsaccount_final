#!/bin/bash

# API Testing Script for Tax Hub Dashboard

BASE_URL="http://localhost:8000/api/v1"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🧪 Testing Tax Hub Dashboard API"
echo "================================"
echo ""

# Test 1: Health Check
echo "1. Testing Health Endpoint..."
HEALTH=$(curl -s http://localhost:8000/health)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "   Response: $HEALTH"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi
echo ""

# Test 2: Login
echo "2. Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "superadmin@taxease.ca",
        "password": "demo123"
    }')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ Login successful${NC}"
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "   Token obtained: ${TOKEN:0:20}..."
else
    echo -e "${RED}❌ Login failed${NC}"
    echo "   Response: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Get Current User
echo "3. Testing Get Current User..."
USER_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/me" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")

if echo "$USER_RESPONSE" | grep -q "superadmin"; then
    echo -e "${GREEN}✅ Get current user successful${NC}"
    echo "   User: $(echo "$USER_RESPONSE" | grep -o '"email":"[^"]*' | cut -d'"' -f4)"
else
    echo -e "${RED}❌ Get current user failed${NC}"
    echo "   Response: $USER_RESPONSE"
fi
echo ""

# Test 4: Get Clients
echo "4. Testing Get Clients..."
CLIENTS_RESPONSE=$(curl -s -X GET "$BASE_URL/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")

if echo "$CLIENTS_RESPONSE" | grep -q "clients"; then
    echo -e "${GREEN}✅ Get clients successful${NC}"
    TOTAL=$(echo "$CLIENTS_RESPONSE" | grep -o '"total":[0-9]*' | cut -d':' -f2)
    echo "   Total clients: ${TOTAL:-0}"
else
    echo -e "${RED}❌ Get clients failed${NC}"
    echo "   Response: $CLIENTS_RESPONSE"
fi
echo ""

# Test 5: Create Client
echo "5. Testing Create Client..."
CREATE_CLIENT_RESPONSE=$(curl -s -X POST "$BASE_URL/clients" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Test Client",
        "email": "test@example.com",
        "phone": "(416) 555-0000",
        "filing_year": 2024
    }')

if echo "$CREATE_CLIENT_RESPONSE" | grep -q "id"; then
    echo -e "${GREEN}✅ Create client successful${NC}"
    CLIENT_ID=$(echo "$CREATE_CLIENT_RESPONSE" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
    echo "   Client ID: ${CLIENT_ID:0:20}..."
else
    echo -e "${YELLOW}⚠️  Create client response:${NC}"
    echo "   $CREATE_CLIENT_RESPONSE"
fi
echo ""

# Test 6: Get Analytics
echo "6. Testing Get Analytics..."
ANALYTICS_RESPONSE=$(curl -s -X GET "$BASE_URL/analytics" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")

if echo "$ANALYTICS_RESPONSE" | grep -q "total_clients"; then
    echo -e "${GREEN}✅ Get analytics successful${NC}"
    TOTAL_CLIENTS=$(echo "$ANALYTICS_RESPONSE" | grep -o '"total_clients":[0-9]*' | cut -d':' -f2)
    echo "   Total clients: ${TOTAL_CLIENTS:-0}"
else
    echo -e "${RED}❌ Get analytics failed${NC}"
    echo "   Response: $ANALYTICS_RESPONSE"
fi
echo ""

# Test 7: Get Admin Users
echo "7. Testing Get Admin Users..."
ADMINS_RESPONSE=$(curl -s -X GET "$BASE_URL/admin-users" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")

if echo "$ADMINS_RESPONSE" | grep -q "email"; then
    echo -e "${GREEN}✅ Get admin users successful${NC}"
    ADMIN_COUNT=$(echo "$ADMINS_RESPONSE" | grep -o '"email"' | wc -l)
    echo "   Admin users: $ADMIN_COUNT"
else
    echo -e "${RED}❌ Get admin users failed${NC}"
    echo "   Response: $ADMINS_RESPONSE"
fi
echo ""

echo "================================"
echo -e "${GREEN}✅ API Testing Complete!${NC}"
echo ""
echo "🌐 Frontend: http://localhost:5173"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Login credentials:"
echo "  Email: superadmin@taxease.ca"
echo "  Password: demo123"




