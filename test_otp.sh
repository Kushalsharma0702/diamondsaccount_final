#!/bin/bash
# Quick OTP Testing Script

API_URL="http://localhost:8000"

echo "======================================"
echo "OTP VERIFICATION TEST"
echo "======================================"
echo ""

# Step 1: Register a test user
echo "1. Registering test user..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "otptest@example.com",
    "password": "TestPass123!",
    "first_name": "OTP",
    "last_name": "Test",
    "phone": "+1234567890"
  }')

echo "$REGISTER_RESPONSE" | jq '.' 2>/dev/null || echo "$REGISTER_RESPONSE"
echo ""

# Step 2: Request OTP
echo "2. Requesting OTP for email verification..."
OTP_REQUEST=$(curl -s -X POST "$API_URL/api/v1/auth/otp/request" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "otptest@example.com",
    "purpose": "email_verification"
  }')

echo "$OTP_REQUEST" | jq '.' 2>/dev/null || echo "$OTP_REQUEST"
echo ""

# Step 3: Get OTP from logs
echo "3. Extracting OTP from API logs..."
OTP_CODE=$(tail -50 /tmp/taxease-start.log 2>/dev/null | grep "OTP for otptest@example.com" | tail -1 | grep -oP '\d{6}' | tail -1)

if [ -z "$OTP_CODE" ]; then
    echo "❌ Could not extract OTP from logs"
    echo "Check logs manually: tail -50 /tmp/taxease-start.log | grep OTP"
    exit 1
fi

echo "✅ OTP Code: $OTP_CODE"
echo ""

# Step 4: Verify OTP
echo "4. Verifying OTP..."
VERIFY_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/otp/verify" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"otptest@example.com\",
    \"code\": \"$OTP_CODE\",
    \"purpose\": \"email_verification\"
  }")

echo "$VERIFY_RESPONSE" | jq '.' 2>/dev/null || echo "$VERIFY_RESPONSE"
echo ""

# Check if verification succeeded
if echo "$VERIFY_RESPONSE" | grep -q "successfully"; then
    echo "✅ OTP Verification SUCCESSFUL"
else
    echo "❌ OTP Verification FAILED"
    echo "Response: $VERIFY_RESPONSE"
fi

echo ""
echo "======================================"
echo "TEST COMPLETE"
echo "======================================"
