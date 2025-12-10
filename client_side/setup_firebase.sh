#!/bin/bash

# Firebase Admin SDK Setup Script
# This script helps set up Firebase Admin SDK for backend token verification

echo "=========================================="
echo "Firebase Admin SDK Setup"
echo "=========================================="
echo ""

# Check if firebase-admin is installed
if ! python3 -c "import firebase_admin" 2>/dev/null; then
    echo "❌ firebase-admin package not found"
    echo "📦 Installing firebase-admin..."
    pip install firebase-admin
    echo "✅ firebase-admin installed"
else
    echo "✅ firebase-admin package is installed"
fi

echo ""
echo "📋 To configure Firebase Admin SDK:"
echo ""
echo "1. Go to Firebase Console: https://console.firebase.google.com/"
echo "2. Select your project: taxease-ec35f"
echo "3. Go to Project Settings > Service Accounts"
echo "4. Click 'Generate new private key'"
echo "5. Save the JSON file securely"
echo ""
echo "6. Set environment variable:"
echo "   export FIREBASE_CREDENTIALS_PATH=/path/to/your/service-account-key.json"
echo ""
echo "   Or add to .env file:"
echo "   FIREBASE_CREDENTIALS_PATH=/path/to/your/service-account-key.json"
echo ""
echo "7. Restart your backend server"
echo ""
echo "=========================================="

