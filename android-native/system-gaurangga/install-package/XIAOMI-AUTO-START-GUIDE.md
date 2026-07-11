# 👑 PANDUAN LENGKAP: GAURANGA AUTO-START DI XIAOMI
## Tanpa ROOT - Pak Pur Bisa Langsung Coba!

---

## 🎯 TUJUAN

HP Restart → 🔐 Lock Screen GAURANGA → Scan Fingerprint → 👑 AKTIF!

---

## 📱 CARA 1: AUTO-START Bawaan MIUI (GAMPANG!)

### STEP 1: Buka Settings HP
```
Buka aplikasi Settings (Gear) di HP Xiaomi
```

### STEP 2: Cari "Apps" atau "Aplikasi"
```
Settings
    └── Apps / Aplikasi
```

### STEP 3: Cari GAURANGA
```
Apps
    └── Manage apps
        └── GAURANGA / Alpha / Gaurangga
```

### STEP 4: Enable Auto-Start
```
GAURANGA App Info
    └── Auto-start → ON / ✅
```

### STEP 5: Enable Battery Saver (Penting!)
```
GAURANGA App Info
    └── Battery saver
        └── No restrictions / Unrestricted / Tidak ada batasan
```

### STEP 6: Test!
```
🔄 Reboot HP
    ↓
🔐 Lock Screen GAURANGA harusnya muncul!
    ↓
Scan Fingerprint → 👑 GAURANGA AKTIF!
```

---

## 🔧 CARA 2: Via Security App (MIUI)

### STEP 1: Buka Security App
```
Cari icon "Security" atau "Keamanan" di Home Screen
```

### STEP 2: Buka Battery
```
Security App
    └── Battery / Daya
        └── App battery saver
```

### STEP 3: Enable GAURANGA
```
App battery saver
    └── GAURANGA → No restrictions
```

### STEP 4: Auto-Start
```
Security App
    └── Permissions
        └── Auto-start → ON
            └── GAURANGA → ON
```

---

## ⚡ CARA 3: Via Developer Options

### STEP 1: Enable Developer Options
```
Settings
    └── About phone
        └── MIUI Version
            → Tap 7x "MIUI Version"
```

### STEP 2: Buka Developer Options
```
Settings
    └── Additional settings
        └── Developer options
```

### STEP 3: Enable USB Debugging (Optional)
```
Developer options
    └── USB debugging → ON
```

---

## 🔐 CARA 4: Cek Biometric Settings

### STEP 1: Buka Settings
```
Settings
    └── Passwords & security
        └── Fingerprint
```

### STEP 2: Pastikan Fingerprint Terdaftar
```
Fingerprint
    └── Pastikan ada fingerprint yang terdaftar
```

### STEP 3: Buka GAURANGA App
```
Buka app GAURANGA
    └── Settings
        └── Biometric Authentication → ON
        └── Auto-start → ON
```

---

## 🚨 KALAU MASIH TIDAK BERHASIL

### Cek 1: Apakah BootReceiver Aktif?

Di HP, buka GAURANGA:
```
GAURANGA
    └── Settings
        └── Startup Settings
            └── Auto-start on Boot → ON ✅
            └── Require Biometric → ON ✅
```

### Cek 2: Cek Logs

Buka File Manager → cari folder:
```
Internal Storage
    └── Android
        └── data
            └── com.gaurangga.alpha
                └── files
                    └── logs
                        └── boot.log
```

### Cek 3: Battery Optimization

```
Settings
    └── Battery & performance
        └── App battery saver
            └── GAURANGA → No restrictions
```

---

## 📋 CHECKLIST - PASTIKAN SEMUA ✅

```
[ ] GAURANGA APK sudah terinstall
[ ] Buka GAURANGA → Settings → Auto-start ON
[ ] Settings → Apps → GAURANGA → Auto-start ON
[ ] Settings → Apps → GAURANGA → Battery → No restrictions
[ ] Settings → Passwords & security → Fingerprint ON
[ ] Buka GAURANGA → Settings → Biometric ON
[ ] REBOOT HP
[ ] 🔐 Lock Screen GAURANGA harus muncul!
```

---

## 🔄 HASIL YANG DIHARAPKAN

```
HP RESTART
    ↓
MIUI Boot Animation...
    ↓
Boot Completed Signal
    ↓
📱 BootReceiver Catch Event
    ↓
AutoStartManager.performAutoStart()
    ↓
🔐 SECURITY ACTIVITY (LOCK SCREEN)
    ↓
User Scan Fingerprint/Face
    ↓
✅ VERIFIED
    ↓
📱 MAIN ACTIVITY
    ↓
🎙️ VOICE SERVICE (24/7)
    ↓
👑 GAURANGA AKTIF!
```

---

## ❌ KALAU LOCK SCREEN TIDAK MUNCUL

Kemungkinan masalah:

1. **Auto-start belum enabled**
   → Ikuti STEP 1-5 di atas lagi

2. **Battery optimization blocked**
   → Settings → Battery → GAURANGA → No restrictions

3. **App tidak ada di boot receiver**
   → Uninstall → Install ulang GAURANGA APK

4. **MIUI blocking**
   → Buka Security app → Auto-start → Enable GAURANGA

---

## 📞 BUTUH BANTUAN?

WhatsApp: **081337558787** (Pak Pur)
GitHub: github.com/prahlad168/Alpha-agent-Gaurangga

---

## 👑 GAURANGA ALPHA v1.1.0

**"Dari nol menjadi satu, dari satu menjadi banyak."**

💪 SEMANGAT PAK PUR! 💪
