#!/bin/bash
# GAURANGA Auto-Deploy & Auto-Run Setup Script
# Complete installation with auto-start configuration

set -e

echo "🚀 GAURANGA Auto-Deploy & Auto-Run Setup"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Banner
cat << 'EOF'
    ╔═══════════════════════════════════════════╗
    ║     👑 GAURANGA ALPHA AUTO-DEPLOY        ║
    ║     Alpha Agent Master v1.1.0            ║
    ╚═══════════════════════════════════════════╝
EOF
echo ""

# Check if we're in the right directory
if [ ! -d "android-native" ]; then
    echo -e "${RED}❌ Error: Run from project root directory${NC}"
    exit 1
fi

cd android-native

# Check if gradle wrapper exists
if [ ! -f "./gradlew" ]; then
    echo -e "${RED}❌ Gradle wrapper not found.${NC}"
    exit 1
fi

# Make gradle executable
chmod +x ./gradlew

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Function to show progress
progress() {
    echo -e "${BLUE}📦 $1...${NC}"
}

# Function to show success
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to show warning
warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to show error
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Clean and build
progress "Building GAURANGA with Auto-Deploy"
./gradlew clean assembleDebug

# Check if APK was built
if [ -f "app/build/outputs/apk/debug/app-debug.apk" ]; then
    APK_SIZE=$(du -h app/build/outputs/apk/debug/app-debug.apk | cut -f1)
    success "Build successful!"
    echo "   APK: app/build/outputs/apk/debug/app-debug.apk"
    echo "   Size: $APK_SIZE"
    echo ""
else
    error "Build failed!"
    exit 1
fi

# Check if ADB is available
if command -v adb &> /dev/null; then
    echo ""
    echo -e "${BLUE}🔌 Checking for connected device...${NC}"
    
    DEVICE_COUNT=$(adb devices 2>/dev/null | grep -c "device$" || true)
    
    if [ "$DEVICE_COUNT" -gt 0 ]; then
        success "Device connected!"
        echo ""
        echo -e "${YELLOW}📱 Installing APK...${NC}"
        adb install -r app/build/outputs/apk/debug/app-debug.apk
        
        success "Installation complete!"
        echo ""
        
        # Ask to enable auto-start
        echo -e "${BLUE}⚙️  Auto-Start Configuration${NC}"
        echo "-----------------------------------"
        echo ""
        echo "Please enable auto-start for GAURANGA in your phone settings."
        echo ""
        echo "Common paths:"
        echo "  • Xiaomi: Settings → Apps → Auto-start"
        echo "  • Samsung: Settings → Apps → GAURANGA → Auto-start"
        echo "  • Huawei: Settings → Apps → GAURANGA → Auto-launch"
        echo "  • Oppo: Settings → App Management → Auto-start"
        echo "  • Vivo: Settings → Apps → Permission → Auto-start"
        echo ""
        
        read -p "Open auto-start settings now? (y/n): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}🔧 Opening device auto-start settings...${NC}"
            
            # Try different manufacturer-specific intents
            MANUFACTURER=$(adb shell getprop ro.product.manufacturer | tr '[:upper:]' '[:lower:]')
            
            case "$MANUFACTURER" in
                *xiaomi*|*redmi*)
                    adb shell am start -n com.miui.securitycenter/com.miui.permcenter.autostart.AutoStartManagementActivity 2>/dev/null || warn "Could not open auto-start settings"
                    ;;
                *samsung*)
                    adb shell am start -n com.samsung.android.lool/com.samsung.android.sm.ui.battery.BatteryActivity 2>/dev/null || warn "Could not open auto-start settings"
                    ;;
                *huawei*|*honor*)
                    adb shell am start -n com.huawei.systemmanager/com.huawei.systemmanager.startupmgr.ui.StartupNormalAppListActivity 2>/dev/null || warn "Could not open auto-start settings"
                    ;;
                *oppo*|*realme*|*oneplus*)
                    adb shell am start -n com.coloros.safecenter/com.coloros.safecenter.permission.startup.StartupAppListActivity 2>/dev/null || warn "Could not open auto-start settings"
                    ;;
                *vivo*)
                    adb shell am start -n com.vivo.permissionmanager/com.vivo.permissionmanager.activity.BgStartUpManagerActivity 2>/dev/null || warn "Could not open auto-start settings"
                    ;;
                *)
                    # Open app info as fallback
                    adb shell am start -a android.settings.APPLICATION_DETAILS_SETTINGS -d package:com.gaurangga.alpha 2>/dev/null || warn "Could not open settings"
                    ;;
            esac
        fi
        
        echo ""
        echo -e "${GREEN}🎉 Setup Complete!${NC}"
        echo ""
        echo "What happens next:"
        echo "1. 📱 Open GAURANGA app"
        echo "2. 🔐 Verify fingerprint/face (first time)"
        echo "3. 🔄 Restart your phone"
        echo "4. ✨ GAURANGA auto-starts with biometric lock screen!"
        echo ""
        
    else
        warn "No device connected. Please connect your device and run:"
        echo "   adb install app/build/outputs/apk/debug/app-debug.apk"
        echo ""
    fi
else
    warn "ADB not found. Please install ADB and run:"
    echo "   adb install app/build/outputs/apk/debug/app-debug.apk"
    echo ""
fi

echo "📖 For more info, see: android-native/AUTO-DEPLOY-GUIDE.md"
echo ""
echo "Done!"
