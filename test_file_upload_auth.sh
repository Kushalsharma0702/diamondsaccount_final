#!/bin/bash

# Test file upload with authentication

echo "🧪 Testing File Upload Authentication..."
echo ""

# Step 1: Login and get token
echo "1️⃣ Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "Developer@aurocode.app",
    "password": "Developer@123"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Token received: ${TOKEN:0:50}..."
echo ""

# Step 2: Test file upload with token
echo "2️⃣ Testing file upload with authentication..."

# Create a test file
echo "Test file content" > /tmp/test_upload.txt

UPLOAD_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "http://localhost:8001/api/v1/files/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_upload.txt")

HTTP_CODE=$(echo "$UPLOAD_RESPONSE" | tail -n1)
BODY=$(echo "$UPLOAD_RESPONSE" | head -n-1)

echo "HTTP Status: $HTTP_CODE"
echo "Response: $BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"

if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
    echo ""
    echo "✅ File upload successful!"
else
    echo ""
    echo "❌ File upload failed!"
    echo ""
    echo "Possible issues:"
    echo "1. Token not being sent correctly"
    echo "2. HTTPBearer not extracting token from multipart request"
    echo "3. Token expired"
fi

# Cleanup
rm -f /tmp/test_upload.txt


