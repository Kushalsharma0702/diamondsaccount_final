#!/bin/bash

# Update Flutter app with ngrok URL or localhost

FLUTTER_DIR="/home/cyberdude/Documents/Projects/CA-final/frontend/tax_ease-main (1)/tax_ease-main"
API_ENDPOINTS_FILE="$FLUTTER_DIR/lib/core/constants/api_endpoints.dart"

if [ "$1" = "ngrok" ]; then
    # Use ngrok URL if provided
    if [ -n "$2" ]; then
        NGROK_URL="$2"
    elif [ -f "/tmp/ngrok_url.txt" ]; then
        NGROK_URL=$(cat /tmp/ngrok_url.txt)
    else
        echo "❌ Ngrok URL not provided and not found in /tmp/ngrok_url.txt"
        echo "Usage: ./update-flutter-url.sh ngrok <ngrok-url>"
        exit 1
    fi
    
    BASE_URL="${NGROK_URL}/api/v1"
    echo "📱 Updating Flutter app to use ngrok URL: $BASE_URL"
else
    # Use localhost
    BASE_URL="http://localhost:8001/api/v1"
    echo "📱 Updating Flutter app to use localhost: $BASE_URL"
fi

if [ ! -f "$API_ENDPOINTS_FILE" ]; then
    echo "❌ Flutter API endpoints file not found: $API_ENDPOINTS_FILE"
    exit 1
fi

# Backup original file
cp "$API_ENDPOINTS_FILE" "${API_ENDPOINTS_FILE}.backup"

# Update BASE_URL
sed -i "s|static const String BASE_URL = '.*';|static const String BASE_URL = '$BASE_URL';|" "$API_ENDPOINTS_FILE"

echo "✅ Flutter app updated!"
echo "   New BASE_URL: $BASE_URL"




