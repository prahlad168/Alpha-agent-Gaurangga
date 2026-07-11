# 👑 GAURANGA - ONE CLICK INSTALL
## Auto-Start + Biometric Authentication

---

## 🚀 CARA PALING GAMPANG

### STEP 1: Buka Termux di HP
```
Buka aplikasi Termux
```

### STEP 2: Copy-Paste Kode Ini
```
su && mount -o rw,remount /system && mkdir -p /data/gaurangga/logs /system/etc/init.d /data/su.d && cat > /system/etc/init.d/99gaurangga << 'EOF'
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
cat > /data/su.d/99gaurangga << 'EOF'
#!/system/bin/sh
while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done
am start -n com.gaurangga.alpha/.ui.SecurityActivity --ez from_boot true 2>/dev/null
EOF
chmod 0755 /data/su.d/99gaurangga
setprop gauranga.installed 1
echo "✅ INSTALLED! Ketik reboot"
```

### STEP 3: Ketik `reboot`
```
Ketik: reboot
```

### STEP 4: SELESAI! 👑
```
HP Restart → Lock Screen GAURANGA → Scan Fingerprint → AKTIF!
```

---

## 📋 APA YANG TERJADI

```
HP Boot
    ↓
Boot Script Jalan (/system/etc/init.d/99gaurangga)
    ↓
Boot Completed Detected
    ↓
Tunggu 5 Detik
    ↓
🔐 GAURANGA LOCK SCREEN MUNCUL
    ↓
User Scan Fingerprint/Face
    ↓
✅ VERIFIED → GAURANGA AKTIF!
```

---

## ⚠️ PERSYARATAN

1. ✅ HP Xiaomi sudah di-ROOT (Magisk/TWRP)
2. ✅ GAURANGA APK sudah terinstall
3. ✅ Biometric (Fingerprint/Face) sudah setup di HP

---

## 🔧 KALAU GAGAL

### Error "permission denied"?
```
Pastikan sudah jalankan 'su' dulu
```

### Lock screen tidak muncul?
```
Cek apakah script terinstall:
ls -la /system/etc/init.d/99gaurangga

Kalau tidak ada, jalankan lagi kode di atas
```

### Cek log:
```
cat /data/gaurangga/logs/boot.log
```

---

## 📞 BANTUAN

WhatsApp: 081337558787 (Pak Pur)
GitHub: github.com/prahlad168/Alpha-agent-Gaurangga

---

## 👑 GAURANGA ALPHA v1.1.0

**"Dari nol menjadi satu, dari satu menjadi banyak."**
