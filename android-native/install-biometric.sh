#!/bin/bash
# GAURANGA Biometric - Quick Install Script
# Usage: ./install-biometric.sh

set -e

echo "🔐 GAURANGA Biometric Authentication Installer"
echo "==============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "android-native" ]; then
    echo -e "${RED}❌ Error: Run from project root directory${NC}"
    exit 1
fi

cd android-native

# Check if gradle wrapper exists
if [ ! -f "./gradlew" ]; then
    echo -e "${RED}❌ Gradle wrapper not found. Run from android-native directory.${NC}"
    exit 1
fi

# Make gradle executable
chmod +x ./gradlew

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Clean and build
echo -e "${YELLOW}🔨 Building GAURANGA with Biometric...${NC}"
./gradlew clean assembleDebug

# Check if APK was built
if [ -f "app/build/outputs/apk/debug/app-debug.apk" ]; then
    APK_SIZE=$(du -h app/build/outputs/apk/debug/app-debug.apk | cut -f1)
    echo ""
    echo -e "${GREEN}✅ Build successful!${NC}"
    echo -e "   APK: app/build/outputs/apk/debug/app-debug.apk"
    echo -e "   Size: $APK_SIZE"
    echo ""
    
    # Ask to install
    read -p "Install to connected device? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}📱 Installing to device...${NC}"
        adb install -r app/build/outputs/apk/debug/app-debug.apk
        echo ""
        echo -e "${GREEN}✅ Installation complete!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Open GAURANGA app"
        echo "2. Setup fingerprint/face in phone Settings (if not done)"
        echo "3. Verify biometric to access app"
        echo ""
        echo "To test auto-start:"
        echo "1. Settings → Apps → GAURANGA → Auto-start (enable)"
        echo "2. Restart phone"
        echo "3. Lock screen should appear after boot"
    fi
else
    echo -e "${RED}❌ Build failed. Check errors above.${NC}"
    exit 1
fi
