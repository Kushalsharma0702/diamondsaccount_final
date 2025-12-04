#!/bin/bash

# Test admin panel login

ADMIN_BACKEND_URL="http://localhost:8002"

echo "🧪 Testing Admin Panel Login..."
echo ""

# Test 1: Superadmin login
echo "1️⃣ Testing Superadmin Login..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$ADMIN_BACKEND_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@taxease.ca",
    "password": "demo123"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "HTTP Status: $HTTP_CODE"
echo "Response: $BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Superadmin login successful!"
    TOKEN=$(echo "$BODY" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    if [ ! -z "$TOKEN" ]; then
        echo "✅ Access token received!"
        echo ""
        
        # Test getting current user
        echo "2️⃣ Testing Get Current User..."
        USER_RESPONSE=$(curl -s -X GET "$ADMIN_BACKEND_URL/api/v1/auth/me" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json")
        
        echo "$USER_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$USER_RESPONSE"
    fi
else
    echo "❌ Superadmin login failed!"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check if backend is running: curl $ADMIN_BACKEND_URL/health"
    echo "2. Verify admin exists: cd tax-hub-dashboard/backend && python3 create_default_admin.py"
fi

echo ""


