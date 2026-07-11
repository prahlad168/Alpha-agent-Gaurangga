#!/system/bin/sh
# 👑 GAURANGA - ONE COMMAND INSTALL
# Pak Pur, tinggal jalankan ini di Termux:
# 
# wget -O- https://raw.githubusercontent.com/prahlad168/Alpha-agent-Gaurangga/main/android-native/system-gaurangga/install-package/GAURANGA-ONE-COMMAND.sh | sh
#
# ATAU copy-paste semua kode ini ke Termux:
#
# mount -o rw,remount /system && mkdir -p /data/gaurangga/logs /system/etc/init.d /data/su.d && cat > /system/etc/init.d/99gaurangga << 'EEOF'
# #!/system/bin/sh
# LOG="/data/gaurangga/logs/boot.log"
# mkdir -p /data/gaurangga/logs
# echo "[$(date)] GAURANGA BOOT" >> $LOG
# while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done
# sleep 5
# am start -n com.gaurangga.alpha/.ui.SecurityActivity --ez from_boot true 2>/dev/null
# echo "[$(date)] GAURANGA STARTED" >> $LOG
# EEOF
# chmod 0755 /system/etc/init.d/99gaurangga
# cat > /data/su.d/99gaurangga << 'SEOF'
# #!/system/bin/sh
# while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done
# am start -n com.gaurangga.alpha/.ui.SecurityActivity --ez from_boot true 2>/dev/null
# SEOF
# chmod 0755 /data/su.d/99gaurangga
# setprop gauranga.installed 1
# reboot

# Check if running as root
if [ "$(id -u)" != "0" ]; then
    echo "❌ Butuh ROOT! Ketik 'su' dulu!"
    exit 1
fi

echo "👑 GAURANGA SYSTEM INSTALL..."
echo "=============================="

# Mount system
mount -o rw,remount /system 2>/dev/null

# Create directories
mkdir -p /data/gaurangga/logs
mkdir -p /system/etc/init.d
mkdir -p /data/su.d

# Install boot script
cat > /system/etc/init.d/99gaurangga << 'BOOTEOF'
#!/system/bin/sh
LOG="/data/gaurangga/logs/boot.log"
mkdir -p /data/gaurangga/logs
echo "[$(date)] GAURANGA BOOT" >> $LOG
while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done
sleep 5
am start -n com.gaurangga.alpha/.ui.SecurityActivity --ez from_boot true 2>/dev/null
echo "[$(date)] GAURANGA STARTED" >> $LOG
BOOTEOF
chmod 0755 /system/etc/init.d/99gaurangga

# Install SU script
cat > /data/su.d/99gaurangga << 'SUEOF'
#!/system/bin/sh
while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done
am start -n com.gaurangga.alpha/.ui.SecurityActivity --ez from_boot true 2>/dev/null
SUEOF
chmod 0755 /data/su.d/99gaurangga

# Set property
setprop gauranga.installed 1

echo ""
echo "✅ INSTALL COMPLETE!"
echo ""
echo "🔄 Sekarang ketik: reboot"
echo ""
echo "👑 GAURANGA AKTIF SETELAH RESTART!"
