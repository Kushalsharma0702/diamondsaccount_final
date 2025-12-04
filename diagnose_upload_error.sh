#!/bin/bash

echo "🔍 Diagnosing File Upload Error..."
echo ""

# Check if backend is running
echo "1️⃣ Checking if backend is running..."
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is NOT running on port 8001"
    echo "   Start it with: cd client_side && python -m uvicorn main:app --reload --port 8001"
    exit 1
fi
echo ""

# Test login
echo "2️⃣ Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "Developer@aurocode.app",
    "password": "Developer@123"
  }')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)
    echo "   ✅ Login successful"
    echo "   Token: ${TOKEN:0:50}..."
else
    echo "   ❌ Login failed"
    echo "   Response: $LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Test authentication
echo "3️⃣ Testing authentication..."
AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "http://localhost:8001/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$AUTH_RESPONSE" | tail -n1)
BODY=$(echo "$AUTH_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ Authentication working"
    USER_EMAIL=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('email', ''))" 2>/dev/null)
    echo "   User: $USER_EMAIL"
else
    echo "   ❌ Authentication failed"
    echo "   HTTP Code: $HTTP_CODE"
    echo "   Response: $BODY"
    exit 1
fi
echo ""

# Test file upload
echo "4️⃣ Testing file upload..."
# Create a test PDF file
echo "%PDF-1.4" > /tmp/test_upload.pdf
echo "Test content" >> /tmp/test_upload.pdf

UPLOAD_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "http://localhost:8001/api/v1/files/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_upload.pdf")

HTTP_CODE=$(echo "$UPLOAD_RESPONSE" | tail -n1)
BODY=$(echo "$UPLOAD_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
    echo "   ✅ File upload working!"
    FILE_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    echo "   File ID: $FILE_ID"
else
    echo "   ❌ File upload failed"
    echo "   HTTP Code: $HTTP_CODE"
    echo "   Response: $BODY"
    echo ""
    echo "   Common issues:"
    echo "   - HTTP 401: Authentication failed (check token)"
    echo "   - HTTP 400: File validation error (check file type/size)"
    echo "   - HTTP 500: Server error (check backend logs)"
fi

# Cleanup
rm -f /tmp/test_upload.pdf

echo ""
echo "✅ Diagnosis complete!"


