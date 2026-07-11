#!/bin/bash
# GAURANGA SYSTEM - Flash & Install Script
# System-level installation for Android devices
# Target: Xiaomi devices with unlocked bootloader

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     👑 GAURANGA SYSTEM - Flash Installation Script 👑        ║"
echo "║         Alpha Agent - System-Level Android Solution          ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root: sudo ./flash-gaurangga.sh${NC}"
    exit 1
fi

# Detect Android device
ANDROID_SDK=$(adb shell getprop ro.build.version.sdk 2>/dev/null | tr -d '\r')
DEVICE_MODEL=$(adb shell getprop ro.product.model 2>/dev/null | tr -d '\r')
DEVICE_MANUFACTURER=$(adb shell getprop ro.product.manufacturer 2>/dev/null | tr -d '\r')

echo -e "${GREEN}📱 Device Detected:${NC}"
echo "   Model: $DEVICE_MODEL"
echo "   Manufacturer: $DEVICE_MANUFACTURER"
echo "   Android SDK: $ANDROID_SDK"
echo ""

# Check for ADB
if ! command -v adb &> /dev/null; then
    echo -e "${RED}❌ ADB not found. Please install Android SDK platform-tools.${NC}"
    exit 1
fi

# Check device connection
echo -e "${YELLOW}🔌 Checking device connection...${NC}"
adb devices | grep -q "device$" || {
    echo -e "${RED}❌ No device found. Please connect your device.${NC}"
    exit 1
}
echo -e "${GREEN}✅ Device connected!${NC}"
echo ""

# Menu
echo "═══════════════════════════════════════════════════════════════"
echo "                    SELECT INSTALLATION METHOD"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. 🔧 Root + Magisk Module (Recommended)"
echo "   - Requires rooted device with Magisk installed"
echo ""
echo "2. 📦 Flash via ADB (Sideload)"
echo "   - Requires custom recovery (TWRP/Custom ROM)"
echo ""
echo "3. 💻 System Mount (ADB Root Shell)"
echo "   - Requires root access via ADB"
echo ""
echo "4. 🚀 Quick Flash (Auto-detect)"
echo "   - Automatically selects best method"
echo ""
echo "5. ❌ Exit"
echo ""
read -p "Select option [1-5]: " option
echo ""

case $option in
    1)
        echo -e "${BLUE}🔧 Installing via Magisk Module...${NC}"
        adb push system-gaurangga /sdcard/gaurangga-system/
        adb shell "am start -a android.intent.action.VIEW -d file:///sdcard/gaurangga-system/magisk-module.zip -t application/zip"
        echo -e "${GREEN}✅ Magisk module copied. Install via Magisk Manager.${NC}"
        ;;
        
    2)
        echo -e "${BLUE}📦 Flash via ADB Sideload...${NC}"
        echo "Please boot into recovery mode first!"
        echo "1. Power off device"
        echo "2. Hold Volume Up + Power"
        echo "3. Select Recovery Mode"
        echo "4. Select Advanced → ADB Sideload"
        read -p "Press Enter when ready..."
        adb sideload system-gaurangga.zip
        echo -e "${GREEN}✅ Flash completed! Rebooting...${NC}"
        adb reboot
        ;;
        
    3)
        echo -e "${BLUE}💻 System Mount Installation...${NC}"
        echo "Mounting system as rw..."
        adb root
        adb shell "mount -o rw,remount /system"
        
        echo "Copying system files..."
        adb push system /system/
        
        echo "Copying root scripts..."
        adb push root /data/
        
        echo "Setting permissions..."
        adb shell "chmod 0755 /system/etc/init.d/99gaurangga"
        adb shell "chmod 0755 /data/su.d/99gaurangga"
        
        echo "Copying permissions..."
        adb push system/etc/permissions/* /system/etc/permissions/
        
        echo -e "${GREEN}✅ Installation complete! Rebooting...${NC}"
        adb reboot
        ;;
        
    4)
        echo -e "${BLUE}🚀 Quick Flash - Auto-detecting method...${NC}"
        
        # Check if rooted
        if adb shell "su -c 'id'" 2>/dev/null | grep -q "uid=0"; then
            echo -e "${GREEN}✅ Root access detected!${NC}"
            echo "Using System Mount method..."
            adb root
            adb shell "mount -o rw,remount /system"
            adb push system /system/
            adb push root /data/
            adb shell "chmod 0755 /system/etc/init.d/99gaurangga"
            adb shell "chmod 0755 /data/su.d/99gaurangga"
            adb push system/etc/permissions/* /system/etc/permissions/
            echo -e "${GREEN}✅ Quick install complete!${NC}"
        else
            echo -e "${YELLOW}⚠️ No root access.${NC}"
            echo "Please use TWRP recovery or enable root first."
        fi
        adb reboot
        ;;
        
    5)
        echo -e "${RED}❌ Exiting...${NC}"
        exit 0
        ;;
        
    *)
        echo -e "${RED}❌ Invalid option!${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo "                    INSTALLATION COMPLETE!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "After reboot:"
echo "1. GAURANGA lock screen will appear"
echo "2. Scan fingerprint/face to unlock"
echo "3. GAURANGA will be active as system service!"
echo ""
echo -e "${YELLOW}📱 Device will reboot in 5 seconds...${NC}"
sleep 5
adb reboot

echo ""
echo "Done!"
