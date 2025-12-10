#!/bin/bash

# Build Flutter APK

FLUTTER_DIR="/home/cyberdude/Documents/Projects/CA-final/frontend/tax_ease-main (1)/tax_ease-main"

if [ ! -d "$FLUTTER_DIR" ]; then
    echo "❌ Flutter directory not found: $FLUTTER_DIR"
    exit 1
fi

cd "$FLUTTER_DIR"

echo "📦 Building Flutter APK..."
echo ""

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed or not in PATH"
    echo "Please install Flutter: https://flutter.dev/docs/get-started/install"
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
flutter clean

# Get dependencies
echo "📥 Getting dependencies..."
flutter pub get

# Build APK
echo "🔨 Building APK (this may take a few minutes)..."
flutter build apk --release

# Check if APK was created
APK_PATH="build/app/outputs/flutter-apk/app-release.apk"
if [ -f "$APK_PATH" ]; then
    APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
    echo ""
    echo "✅ APK built successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📱 APK Location: $FLUTTER_DIR/$APK_PATH"
    echo "📦 APK Size: $APK_SIZE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📋 To install on device:"
    echo "   adb install $APK_PATH"
    echo ""
else
    echo "❌ APK build failed!"
    exit 1
fi




