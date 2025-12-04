#!/bin/bash

# Script to check how many T1 forms you have

CLIENT_BACKEND_URL="http://localhost:8001"
EMAIL="Developer@aurocode.app"
PASSWORD="Developer@123"

echo "🔍 Checking T1 Forms..."
echo ""

# Step 1: Login to get token
echo "1️⃣ Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$CLIENT_BACKEND_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$EMAIL\",
    \"password\": \"$PASSWORD\"
  }")

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Login failed!"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Login successful!"
echo ""

# Step 2: Get T1 forms
echo "2️⃣ Fetching T1 forms..."
FORMS_RESPONSE=$(curl -s -X GET "$CLIENT_BACKEND_URL/api/v1/t1-forms/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

# Extract total count
TOTAL=$(echo "$FORMS_RESPONSE" | grep -o '"total":[0-9]*' | cut -d':' -f2)
FORMS_COUNT=$(echo "$FORMS_RESPONSE" | grep -o '"forms":\[' | wc -l)

# Try to parse JSON properly
if command -v jq &> /dev/null; then
    TOTAL=$(echo "$FORMS_RESPONSE" | jq -r '.total // 0')
    FORMS=$(echo "$FORMS_RESPONSE" | jq -r '.forms | length // 0')
    
    echo "📊 T1 Forms Summary:"
    echo "   Total Forms: $TOTAL"
    echo ""
    
    if [ "$TOTAL" -gt 0 ]; then
        echo "📋 Form Details:"
        echo "$FORMS_RESPONSE" | jq -r '.forms[] | "   - Form ID: \(.id)\n     Status: \(.status)\n     Created: \(.created_at)\n     Name: \(.personalInfo.firstName) \(.personalInfo.lastName)\n"'
    else
        echo "   ℹ️  No forms found. Start by creating a new T1 form!"
    fi
else
    # Fallback if jq is not installed
    echo "📊 T1 Forms Response:"
    echo "$FORMS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$FORMS_RESPONSE"
fi

echo ""
echo "✅ Done!"


