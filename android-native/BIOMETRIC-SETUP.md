# 🔐 GAURANGA Biometric Authentication Setup

## 📋 Overview

GAURANGA sekarang dilengkapi dengan **autentikasi biometrik** yang memungkinkan:
- ✅ Verifikasi fingerprint / face recognition saat buka app
- ✅ Auto-start setelah restart HP dengan lock screen
- ✅ Session trusted selama 5 menit tanpa re-auth
- ✅ Lockout setelah 5x gagal verifikasi

## 🎯 Fitur Utama

### 1. Biometric Authentication
- **Fingerprint**: Sidik jari
- **Face Recognition**: Pengenalan wajah
- **Device Credential**: PIN/Password fallback

### 2. Auto-Start After Boot
```
HP Restart → Lock Screen → Verify → GAURANGA Active
```

### 3. Security Flow
```
┌─────────────────────────────────────────────────────────┐
│                    SECURITY FLOW                        │
├─────────────────────────────────────────────────────────┤
│  1. App Launch / Boot Complete                          │
│              ↓                                          │
│  2. Show SecurityActivity (Lock Screen)                │
│              ↓                                          │
│  3. User Authenticate (Fingerprint/Face)                │
│              ↓                                          │
│  4. Success → MainActivity → Voice Service 24/7       │
│              ↓                                          │
│  5. Session Trusted for 5 minutes                       │
└─────────────────────────────────────────────────────────┘
```

## 📱 Setup di HP

### 1. Setup Fingerprint/Face di HP
```
Settings → Security → Fingerprint / Face Recognition
```

### 2. Install GAURANGA APK
```bash
cd android-native
./gradlew assembleDebug
# APK: app/build/outputs/apk/debug/app-debug.apk
```

### 3. Install di HP
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

### 4. Buka App → Verifikasi Biometric
```
GAURANGA → Lock Screen → Verify → Ready!
```

## 🔧 Konfigurasi

### Auto-Start Modes
```kotlin
// Dalam BootReceiver, bisa pilih mode:
"full"          → Lock Screen → Main Activity → Service (default)
"service_only"  → Service saja (tanpa UI)
"lock_only"     → Lock Screen saja
```

### Session Timeout
```kotlin
// Default: 5 menit trusted session
AUTH_VALIDITY_DURATION = 5 * 60 * 1000L // 5 minutes
```

### Max Failed Attempts
```kotlin
// Default: 5 percobaan sebelum lockout
maxAttempts = 5
lockoutDuration = 30_000L // 30 detik
```

## 📁 File Baru

| File | Fungsi |
|------|--------|
| `security/BiometricAuthManager.kt` | Logic autentikasi biometrik |
| `ui/SecurityActivity.kt` | Lock screen UI |
| `res/layout/activity_security.xml` | Layout lock screen |
| `res/drawable/bg_security_gradient.xml` | Background gradient |

## 🔄 Build & Test

### Build Debug APK
```bash
cd android-native
./gradlew clean assembleDebug
```

### Test Biometric
1. Install APK di HP
2. Buka app → Lock screen muncul
3. Tap "VERIFIKASI" atau tap anywhere
4. Gunakan fingerprint/face
5. Berhasil → Main activity terbuka

### Test Auto-Start
1. Aktifkan auto-start di settings HP (vendor-specific)
2. Restart HP
3. Lock screen GAURANGA muncul otomatis
4. Verifikasi → GAURANGA aktif

## ⚠️ Troubleshooting

### "Biometric not available"
- Pastikan HP mendukung fingerprint/face
- Setup biometric di Settings HP dulu

### "No biometric enrolled"
- Buka Settings → Security → Setup fingerprint/face

### Auto-start tidak berfungsi
- Cek Settings → Apps → GAURANGA → Auto-start (enabled)
- Beberapa HP perlu allow auto-start manually

### Locked out (terlalu banyak gagal)
- Tunggu 30 detik automatic unlock
- Atau restart HP

## 🔒 Keamanan

### What We Protect
- ✅ Akses ke GAURANGA app
- ✅ Voice service 24/7
- ✅ Personal data & settings

### Security Best Practices
- Biometric confirmation required each session (if timeout)
- No bypass without physical device access
- Session invalidates after 5 minutes of inactivity

## 📞 Dukungan

Jika ada masalah:
1. Cek Settings HP → Security biometric setup
2. Pastikan app permissions granted
3. Cek Logcat: `adb logcat | grep BiometricAuthManager`

---

**Version:** 1.0.0
**Created:** 11 Juli 2026
**Status:** ✅ IMPLEMENTED

## 📖 More Info

For complete Auto-Deploy & Auto-Run guide, see: [AUTO-DEPLOY-GUIDE.md](./AUTO-DEPLOY-GUIDE.md)
