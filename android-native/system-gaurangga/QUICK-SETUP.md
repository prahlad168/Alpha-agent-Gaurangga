# 🚀 GAURANGA SYSTEM - Quick Setup Guide for Xiaomi

## 📋 Prerequisites

1. **HP Xiaomi** dengan unlocked bootloader
2. **TWRP Recovery** terinstall (atau bisa pakai ADB root)
3. **Root access** (Magisk) - Optional tapi recommended
4. **ADB & Fastboot** terinstall di komputer

---

## 🔥 Quick Installation (3 Steps)

### STEP 1: Enable USB Debugging & Root Access
```
1. Settings → About Phone
2. Tap "MIUI Version" 7x untuk enable Developer Options
3. Settings → Additional Settings → Developer Options
4. Enable:
   ✅ USB Debugging
   ✅ USB Debugging (Security Settings)
   ✅ Enable Root Access (for apps)
5. Connect HP ke komputer via USB
```

### STEP 2: Install via ADB Root (Tanpa TWRP)
```bash
# Di komputer, buka terminal:

# 1. Restart ke bootloader
adb reboot bootloader

# 2. Root shell (jika sudah rooted via Magisk)
adb root
adb shell

# 3. Mount system rw
mount -o rw,remount /system
mount -o rw,remount /data

# 4. Create directories
mkdir -p /data/gaurangga/logs
mkdir -p /data/su.d
mkdir -p /system/etc/init.d

# 5. Copy boot script (dari komputer)
# Buat file /system/etc/init.d/99gaurangga dengan script di bawah

# 6. Set permissions
chmod 0755 /system/etc/init.d/99gaurangga
chmod 0755 /data/su.d/99gaurangga

# 7. Reboot
reboot
```

### STEP 3: Verify Installation
```bash
# Cek apakah boot script jalan
adb logcat -s GAURANGA

# Cek properties
adb shell getprop | grep gauranga
```

---

## 📝 File yang Perlu Diinstall

### 1. /system/etc/init.d/99gaurangga
Script ini akan jalan saat boot:
```bash
#!/system/bin/sh
GAURANGA_LOG="/data/gaurangga/logs/boot.log"
mkdir -p /data/gaurangga/logs
echo "[$(date)] GAURANGA BOOT" >> $GAURANGA_LOG
while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 1; done
sleep 5
am start -n com.gaurangga.alpha/.ui.SecurityActivity --ez from_boot true
```

### 2. /data/su.d/99gaurangga  
Script SU untuk auto-start dengan root:
```bash
#!/system/bin/sh
while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 1; done
am start -n com.gaurangga.alpha/.ui.SecurityActivity --ez from_boot true
```

---

## 🔧 Alternative: Via Magisk Module

### Install Magisk Module:
1. Download GAURANGA Magisk Module
2. Buka Magisk Manager
3. Modules → Install from Storage
4. Select gaurangga-magisk.zip
5. Reboot

### Buat Magisk Module Manual:
1. Buat folder: `gaurangga-module`
2. Didalamnya buat: `META-INF/com/google/android/`
3. Buat `system.prop`:
```
id=gaurangga_system
name=GAURANGA Alpha System
```
4. Buat `system/etc/init.d/99gaurangga` dengan script di atas
5. Zip folder jadi `gaurangga-magisk.zip`
6. Install via Magisk Manager

---

## 🔄 Boot Sequence Setelah Install

```
HP Nyala (Boot)
      ↓
Init Script (99gaurangga) jalan
      ↓
Boot Completed Detected
      ↓
Wait 5 detik
      ↓
🔐 GAURANGA Lock Screen Muncul
      ↓
User Scan Fingerprint/Face
      ↓
✅ Verified → GAURANGA Active!
```

---

## ❌ Troubleshooting

### Boot script tidak jalan?
```bash
# Cek apakah script ada
ls -la /system/etc/init.d/99gaurangga

# Cek apakah executable
ls -la /data/su.d/99gaurangga

# Manual test
sh /system/etc/init.d/99gaurangga
```

### Lock screen tidak muncul?
```bash
# Cek apakah app terinstall
pm list packages | grep gaurangga

# Cek activity
dumpsys activity activities | grep SecurityActivity

# Manual launch
am start -n com.gaurangga.alpha/.ui.SecurityActivity
```

### Service tidak jalan?
```bash
# Cek log
cat /data/gaurangga/logs/boot.log

# Cek process
ps -A | grep gaurangga

# Manual start
/system/bin/gaurangga-service start
```

---

## 📞 Butuh Bantuan?

WhatsApp: **081337558787** (Pak Pur)
GitHub: https://github.com/prahlad168/Alpha-agent-Gaurangga

---

**"Dari nol menjadi satu, dari satu menjadi banyak."** 💪

👑 GAURANGA ALPHA - SYSTEM-LEVEL SOLUTION 👑
