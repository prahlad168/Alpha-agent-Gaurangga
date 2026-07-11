#!/system/bin/sh
# ============================================
# 👑 GAURANGA - SUPER FAST INSTALL 👑
# ============================================
# Copy-paste ini ke Termux/ADB Shell dan jalankan!
# ============================================

# Check root
if [ "$(id -u)" != "0" ]; then
    echo "❌ Butuh ROOT! Jalankan: su"
    exit 1
fi

echo "👑 GAURANGA FAST INSTALL..."
echo "============================"

# Mount
mount -o rw,remount /system 2>/dev/null

# Dir
mkdir -p /data/gaurangga/logs
mkdir -p /system/etc/init.d
mkdir -p /data/su.d

# Boot Script
cat > /system/etc/init.d/99gaurangga << 'EOF'
#!/system/bin/sh
LOG="/data/gaurangga/logs/boot.log"
mkdir -p /data/gaurangga/logs
echo "[$(date)] GAURANGA BOOT" >> $LOG
while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done
sleep 5
am start -n com.gaurangga.alpha/.ui.SecurityActivity --ez from_boot true 2>/dev/null
echo "[$(date)] GAURANGA STARTED" >> $LOG
EOF
chmod 0755 /system/etc/init.d/99gaurangga

# SU Script
cat > /data/su.d/99gaurangga << 'EOF'
#!/system/bin/sh
while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done
am start -n com.gaurangga.alpha/.ui.SecurityActivity --ez from_boot true 2>/dev/null
EOF
chmod 0755 /data/su.d/99gaurangga

# Props
setprop gauranga.installed 1

echo "✅ SELESAI! Ketik: reboot"
echo "👑 GAURANGA AKTIF SETELAH RESTART!"
