#!/bin/bash
# GAURANGA Android App Build Script
# Requires Android SDK and Gradle

echo "╔══════════════════════════════════════════════╗"
echo "║   GAURANGA Android App Build Script         ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Check for Android SDK
if [ -z "$ANDROID_HOME" ]; then
    if [ -d "$HOME/Android/Sdk" ]; then
        export ANDROID_HOME="$HOME/Android/Sdk"
    elif [ -d "/opt/android-sdk" ]; then
        export ANDROID_HOME="/opt/android-sdk"
    else
        echo "❌ Android SDK not found!"
        echo "Please set ANDROID_HOME environment variable"
        exit 1
    fi
fi

echo "✅ Android SDK: $ANDROID_HOME"

# Change to app directory
cd "$(dirname "$0")/app" || exit 1

# Create local.properties if not exists
if [ ! -f "local.properties" ]; then
    echo "sdk.dir=$ANDROID_HOME" > local.properties
    echo "✅ Created local.properties"
fi

# Clean
echo ""
echo "🧹 Cleaning..."
./gradlew clean 2>/dev/null || gradle clean 2>/dev/null || true

# Build Debug APK
echo ""
echo "🔨 Building Debug APK..."
./gradlew assembleDebug 2>/dev/null || gradle assembleDebug 2>/dev/null

# Check result
if [ -f "build/outputs/apk/debug/app-debug.apk" ]; then
    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║   ✅ BUILD SUCCESSFUL!                      ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""
    echo "📦 APK Location:"
    echo "   $(realpath build/outputs/apk/debug/app-debug.apk)"
    echo ""
    echo "📱 Install to device:"
    echo "   adb install build/outputs/apk/debug/app-debug.apk"
else
    echo ""
    echo "❌ BUILD FAILED"
    echo "Check errors above"
    exit 1
fi