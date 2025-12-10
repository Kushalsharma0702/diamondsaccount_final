#!/bin/bash

# Test OTP verification endpoint
# This script tests the OTP verification with developer OTP

CLIENT_BACKEND_URL="http://localhost:8001"

echo "🧪 Testing OTP Verification..."
echo ""

# Test data
TEST_EMAIL="test@example.com"
DEVELOPER_OTP="123456"

echo "📧 Email: $TEST_EMAIL"
echo "🔑 Developer OTP: $DEVELOPER_OTP"
echo ""

# Test verify-otp endpoint
echo "🔍 Testing verify-otp endpoint..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$CLIENT_BACKEND_URL/api/v1/auth/verify-otp" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"code\": \"$DEVELOPER_OTP\",
    \"purpose\": \"email_verification\"
  }")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "HTTP Status: $HTTP_CODE"
echo "Response: $BODY"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ OTP verification successful!"
else
    echo "❌ OTP verification failed!"
    echo "Response body: $BODY"
fi




