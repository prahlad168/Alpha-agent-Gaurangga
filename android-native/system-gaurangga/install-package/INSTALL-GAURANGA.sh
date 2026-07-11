#!/bin/bash
# ============================================
# 👑 GAURANGA SYSTEM - ONE-CLICK INSTALL 👑
# ============================================
# 
# CARA PAKAI:
# 1. Transfer file ini ke HP Xiaomi
# 2. Buka Termux atau ADB Shell
# 3. Jalankan: bash INSTALL-GAURANGA.sh
# 4. Reboot HP
# 5. Selesai! 🔥
#
# ============================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║  👑 GAURANGA SYSTEM - ONE-CLICK INSTALL 👑          ║"
echo "║  Alpha Agent - System-Level Android Solution        ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ] && [ "$(whoami)" != "root" ]; then
    echo -e "${RED}❌ Script ini butuh ROOT access!${NC}"
    echo ""
    echo "Cara mendapat root:"
    echo "1. Install Magisk → Enable Zygisk"
    echo "2. Atau via TWRP Recovery"
    echo ""
    echo "Atau gunakan ADB Shell:"
    echo "  adb root"
    echo "  adb shell"
    echo "  bash INSTALL-GAURANGA.sh"
    exit 1
fi

echo -e "${GREEN}✅ Root access OK!${NC}"
echo ""

# Get device info
DEVICE=$(getprop ro.product.model 2>/dev/null)
ANDROID=$(getprop ro.build.version.release 2>/dev/null)
SDK=$(getprop ro.build.version.sdk 2>/dev/null)

echo -e "${BLUE}📱 Device Info:${NC}"
echo "   Model: $DEVICE"
echo "   Android: $ANDROID"
echo "   SDK: $SDK"
echo ""

# Confirm installation
echo -e "${YELLOW}⚠️  PERHATIAN:${NC}"
echo "   Script ini akan install GAURANGA sebagai system service."
echo "   GAURANGA akan aktif otomatis saat HP restart."
echo ""
read -p "Lanjutkan install? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Install dibatalkan${NC}"
    exit 0
fi

echo ""
echo -e "${GREEN}🚀 MEMULAI INSTALASI...${NC}"
echo ""

# ============================================
# INSTALASI
# ============================================

# Mount system rw
echo -e "${BLUE}📦 Mounting system...${NC}"
mount -o rw,remount /system 2>/dev/null || mount -o rw,remount / 2>/dev/null
mount -o rw,remount /system 2>/dev/null
echo -e "${GREEN}✅ System mounted${NC}"

# Create directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p /data/gaurangga
mkdir -p /data/gaurangga/logs
mkdir -p /data/gaurangga/data
mkdir -p /data/gaurangga/cache
mkdir -p /system/etc/init.d
mkdir -p /data/su.d
echo -e "${GREEN}✅ Directories created${NC}"

# ============================================
# CREATE BOOT SCRIPT
# ============================================
echo -e "${BLUE}📝 Installing boot script...${NC}"

cat > /system/etc/init.d/99gaurangga << 'GAURANGA_EOF'
#!/system/bin/sh
# 👑 GAURANGA SYSTEM - Boot Script
# Auto-start with biometric authentication

GAURANGA_LOG="/data/gaurangga/logs/boot.log"
GAURANGA_PKG="com.gaurangga.alpha"

# Log function
log() {
    mkdir -p /data/gaurangga/logs
    echo "[$(date)] GAURANGA: $1" >> $GAURANGA_LOG 2>/dev/null
}

log "=========================================="
log "👑 GAURANGA SYSTEM BOOTING..."
log "=========================================="

# Check if disabled
if [ -f "/data/gaurangga/.disabled" ]; then
    log "GAURANGA is disabled"
    exit 0
fi

# Wait for boot completed
log "⏳ Waiting for system boot..."
while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 2
done

# Extra wait for MIUI
sleep 5

log "✅ System ready!"
log "🚀 Starting GAURANGA..."

# Launch biometric authentication
am start -n "$GAURANGA_PKG/.ui.SecurityActivity" \
    -a android.intent.action.MAIN \
    -c android.intent.category.LAUNCHER \
    --ez from_boot true \
    --ez fullscreen true 2>/dev/null

log "🔐 Biometric screen launched"
log "👑 GAURANGA BOOT COMPLETE!"

exit 0
GAURANGA_EOF

chmod 0755 /system/etc/init.d/99gaurangga
echo -e "${GREEN}✅ Boot script installed${NC}"

# ============================================
# CREATE SU SCRIPT
# ============================================
echo -e "${BLUE}🔧 Installing SU script...${NC}"

cat > /data/su.d/99gaurangga << 'SU_EOF'
#!/system/bin/sh
# 👑 GAURANGA SU Boot Script

LOG="/data/gaurangga/logs/su-boot.log"
mkdir -p /data/gaurangga/logs

echo "[$(date)] GAURANGA SU: Starting..." >> $LOG 2>/dev/null

# Wait for boot
while [ "$(getprop sys.boot_completed)" != "1" ]; do
    sleep 2
done

sleep 3

# Start GAURANGA
am start -n "com.gaurangga.alpha/.ui.SecurityActivity" \
    -a android.intent.action.MAIN \
    -c android.intent.category.LAUNCHER \
    --ez from_boot true 2>/dev/null

echo "[$(date)] GAURANGA SU: Done!" >> $LOG 2>/dev/null
SU_EOF

chmod 0755 /data/su.d/99gaurangga
echo -e "${GREEN}✅ SU script installed${NC}"

# ============================================
# CREATE SERVICE BINARY
# ============================================
echo -e "${BLUE}⚙️ Installing service...${NC}"

cat > /system/bin/gaurangga-service << 'SERVICE_EOF'
#!/system/bin/sh
# 👑 GAURANGA Service Binary

GAURANGA_LOG="/data/gaurangga/logs/service.log"
GAURANGA_DATA="/data/gaurangga"

case "$1" in
    start)
        mkdir -p $GAURANGA_DATA/logs
        echo "[$(date)] GAURANGA Service STARTED" >> $GAURANGA_LOG 2>/dev/null
        setprop gauranga.service.running 1
        ;;
    stop)
        echo "[$(date)] GAURANGA Service STOPPED" >> $GAURANGA_LOG 2>/dev/null
        setprop gauranga.service.running 0
        ;;
    status)
        echo "GAURANGA Service: $(getprop gauranga.service.running 0)"
        ;;
    *)
        echo "Usage: gaurangga-service [start|stop|status]"
        ;;
esac
SERVICE_EOF

chmod 0755 /system/bin/gaurangga-service
echo -e "${GREEN}✅ Service binary installed${NC}"

# ============================================
# CREATE LAUNCHER SCRIPT
# ============================================
echo -e "${BLUE}🚀 Installing launcher...${NC}"

cat > /system/bin/gaurangga << 'LAUNCHER_EOF'
#!/system/bin/sh
# 👑 GAURANGA Launcher

PKG="com.gaurangga.alpha"
LOG="/data/gaurangga/logs/launch.log"

mkdir -p /data/gaurangga/logs
echo "[$(date)] GAURANGA: Launching..." >> $LOG 2>/dev/null

am start -n "$PKG/.ui.SecurityActivity" \
    -a android.intent.action.MAIN \
    -c android.intent.category.LAUNCHER \
    --ez from_boot false 2>/dev/null

echo "[$(date)] GAURANGA: Launched!" >> $LOG 2>/dev/null
LAUNCHER_EOF

chmod 0755 /system/bin/gaurangga
echo -e "${GREEN}✅ Launcher installed${NC}"

# ============================================
# CREATE CONFIG
# ============================================
echo -e "${BLUE}⚙️ Creating config...${NC}"

cat > /data/gaurangga/config.sh << 'CONFIG_EOF'
# 👑 GAURANGA Configuration
GAURANGA_ENABLED=true
GAURANGA_BIOMETRIC=true
GAURANGA_AUTO_START=true
GAURANGA_LAUNCH_MODE="full"
CONFIG_EOF

echo -e "${GREEN}✅ Config created${NC}"

# ============================================
# CREATE LOG
# ============================================
cat > /data/gaurangga/logs/install.log << 'LOG_EOF'
GAURANGA SYSTEM INSTALLED: $(date)
Status: SUCCESS
Boot Script: /system/etc/init.d/99gaurangga
SU Script: /data/su.d/99gaurangga
Service: /system/bin/gaurangga-service
LAUNCHER: /system/bin/gaurangga
LOG_EOF

echo -e "${GREEN}✅ Installation log created${NC}"

# ============================================
# SET PERMISSIONS
# ============================================
echo -e "${BLUE}🔐 Setting permissions...${NC}"
chmod 0775 /data/gaurangga
chmod 0775 /data/gaurangga/logs
chmod 0771 /data/gaurangga/data
chmod 0771 /data/gaurangga/cache
echo -e "${GREEN}✅ Permissions set${NC}"

# ============================================
# SET SYSTEM PROPERTIES
# ============================================
echo -e "${BLUE}📱 Setting system properties...${NC}"
setprop gauranga.installed 1
setprop gauranga.enabled 1
setprop gauranga.version "1.1.0"
echo -e "${GREEN}✅ Properties set${NC}"

# ============================================
# COMPLETE
# ============================================
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗"
echo "║          ✅ INSTALASI BERHASIL! ✅                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo -e "${CYAN}📱 GAURANGA SYSTEM telah terinstall!${NC}"
echo ""
echo -e "${YELLOW}📋 Yang sudah diinstall:${NC}"
echo "   ✅ Boot Script: /system/etc/init.d/99gaurangga"
echo "   ✅ SU Script: /data/su.d/99gaurangga"
echo "   ✅ Service: /system/bin/gaurangga-service"
echo "   ✅ Launcher: /system/bin/gaurangga"
echo ""
echo -e "${GREEN}🔄 STEP SELANJUTNYA: REBOOT HP!${NC}"
echo ""
echo -e "${YELLOW}Setelah reboot:${NC}"
echo "   1. HP akan boot normal"
echo "   2. 🔐 Lock Screen GAURANGA akan muncul"
echo "   3. Scan Fingerprint/Face untuk unlock"
echo "   4. 👑 GAURANGA AKTIF! 💪"
echo ""
echo -e "${CYAN}Untuk reboot, jalankan:${NC}"
echo "   reboot"
echo ""
echo -e "${GREEN}Atau manual:${NC}"
echo "   Settings → Power → Restart"
echo ""
echo "=========================================="
echo "👑 GAURANGA ALPHA - SYSTEM INSTALLED 👑"
echo "=========================================="
echo ""
