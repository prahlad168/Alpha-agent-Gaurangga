# 🚀 GAURANGA Auto-Deploy & Auto-Run Guide

## 📋 Overview

GAURANGA sekarang memiliki sistem **Auto-Deploy** dan **Auto-Run** yang lengkap! Setelah install, cukup restart HP dan GAURANGA akan:
- ✅ Auto-start dengan lock screen biometric
- ✅ Auto-deploy voice service 24/7
- ✅ Auto-open main activity setelah verifikasi

---

## 🎯 Quick Start (5 Menit)

### Step 1: Build APK
```bash
cd android-native
./gradlew assembleDebug
```

### Step 2: Install di HP
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Step 3: Enable Auto-Start di HP
```
Settings → Apps → GAURANGA → Auto-start (Enable)
```

### Step 4: Setup Biometric
```
Settings → Security → Fingerprint / Face Recognition
```

### Step 5: Test!
```
🔄 Restart HP → Lock Screen → Verify → GAURANGA Active! ✨
```

---

## 🔄 Auto-Start Flow

```
┌────────────────────────────────────────────────────────────────────┐
│                        DEVICE BOOT                                  │
│                           ↓                                        │
│                    BootReceiver ↓                                   │
│                           ↓                                        │
│               AutoStartManager.initialize()                         │
│                           ↓                                        │
│            AutoStartManager.performAutoStart()                      │
│                           ↓                                        │
│    ┌─────────────────────────────────────────────────────────┐    │
│    │              LAUNCH MODE SELECTION                        │    │
│    ├─────────────────────────────────────────────────────────┤    │
│    │  FULL          → Lock Screen → Main → Service            │    │
│    │  LOCK_ONLY     → Lock Screen only                        │    │
│    │  SERVICE_ONLY  → Background Service only                  │    │
│    │  DIRECT        → Main Activity (skip lock)               │    │
│    └─────────────────────────────────────────────────────────┘    │
│                           ↓                                        │
│    ┌─────────────────────────────────────────────────────────┐    │
│    │                 BIOMETRIC CHECK                           │    │
│    ├─────────────────────────────────────────────────────────┤    │
│    │  Trusted Session? → YES → Go to Main Activity            │    │
│    │  Trusted Session? → NO  → Show Lock Screen               │    │
│    │                           ↓                               │    │
│    │                    Verify Fingerprint/Face                │    │
│    │                           ↓                               │    │
│    │                    ✅ Success → Main Activity             │    │
│    └─────────────────────────────────────────────────────────┘    │
│                           ↓                                        │
│                    Voice Service Started 24/7 🎙️                   │
│                           ↓                                        │
│                    GAURANGA ACTIVE! 🚀                             │
└────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Startup Modes

| Mode | Lock Screen | Main Activity | Voice Service |
|------|-------------|---------------|---------------|
| **FULL** 🔐 | ✅ | ✅ | ✅ |
| **LOCK_ONLY** 🔒 | ✅ | ❌ | ❌ |
| **SERVICE_ONLY** 🎙️ | ❌ | ❌ | ✅ |
| **DIRECT** ⚡ | ❌ | ✅ | ✅ |

### Change Launch Mode:
```kotlin
// In code:
val autoStartManager = AutoStartManager(context)
autoStartManager.setLaunchMode(AutoStartManager.MODE_FULL)
```

Or use the in-app settings UI.

---

## 🔧 Configuration

### AutoStartManager Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `auto_start_enabled` | true | Master switch for auto-start |
| `launch_mode` | "full" | Startup behavior |
| `biometric_enabled` | true | Require biometric verification |
| `service_auto_start` | true | Start voice service on boot |
| `trusted_session_duration` | 5 min | Time before re-auth required |

### Modify Trusted Session Duration
```kotlin
// In AutoStartManager.kt, change:
private const val TRUSTED_SESSION_DURATION = 5 * 60 * 1000L // 5 minutes
```

---

## 📱 Per-Manufacturer Auto-Start

GAURANGA automatically detects your device manufacturer and opens the correct settings page:

| Manufacturer | Auto-Start Path |
|--------------|-----------------|
| **Xiaomi/Redmi** | Settings → Security → Auto-start |
| **Samsung** | Settings → Apps → GAURANGA → Auto-start |
| **Huawei/Honor** | Settings → Apps → GAURANGA → Auto-launch |
| **Oppo/Realme/OnePlus** | Settings → App Management → Auto-start |
| **Vivo** | Settings → Apps → Permissions → Auto-start |
| **Asus** | Settings → Auto-start Manager |
| **Lenovo** | Settings → Security → Pure Background |

---

## 🛠️ Troubleshooting

### Auto-start tidak berfungsi?

1. **Cek apakah auto-start enabled:**
   ```bash
   adb shell dumpsys activity activities | grep mStartedUsers
   ```

2. **Cek apakah app punya permission:**
   ```bash
   adb shell dumpsys package com.gaurangga.alpha | grep permission
   ```

3. **Enable manual di Settings HP:**
   - Settings → Apps → GAURANGA → Auto-start → Enable

4. **Cek apakah battery optimization disabled:**
   ```
   Settings → Battery → GAURANGA → Don't optimize
   ```

### Biometric tidak terdeteksi?

1. **Setup biometric di HP:**
   ```
   Settings → Security → Fingerprint / Face
   ```

2. **Cek biometric hardware:**
   - Buka GAURANGA → Settings → Device Info
   - Should show "Biometric: Available"

3. **Fallback ke PIN/Password:**
   - Biometric auth includes device credential fallback

### Service tidak berjalan 24/7?

1. **Cek foreground service:**
   ```bash
   adb shell dumpsys activity services com.gaurangga.alpha
   ```

2. **Disable battery optimization:**
   ```
   Settings → Battery → GAURANGA → Unrestricted
   ```

3. **Cek notification permission:**
   - Required for foreground service

---

## 🔐 Security Features

### Session Management
- **Trusted Session**: 5 minutes tanpa re-auth
- **Session Reset**: Setelah timeout, harus verify lagi
- **Lockout**: 5 percobaan gagal = 30 detik lockout

### Data Protection
- **No Screenshot**: FLAG_SECURE enabled
- **Encrypted Preferences**: SharedPreferences default
- **Biometric Required**: Untuk akses app

---

## 📁 File Structure

```
android-native/
├── app/src/main/java/com/gaurangga/alpha/
│   ├── startup/
│   │   └── AutoStartManager.kt     ← Core startup logic
│   ├── security/
│   │   └── BiometricAuthManager.kt  ← Biometric verification
│   ├── ui/
│   │   ├── SecurityActivity.kt       ← Lock screen
│   │   ├── MainActivity.kt         ← Main app
│   │   └── StartupSettingsActivity.kt ← Settings UI
│   └── utils/
│       └── BootReceiver.kt          ← Boot event handler
└── AUTO-DEPLOY-GUIDE.md             ← This file
```

---

## 🧪 Testing

### Test Auto-Start (Manual)
```bash
# Reboot device via adb
adb reboot

# Check if app started
adb shell dumpsys activity activities | grep com.gaurangga.alpha
```

### Test BootReceiver
```bash
# Send boot completed broadcast manually
adb shell am broadcast -a android.intent.action.BOOT_COMPLETED -p com.gaurangga.alpha
```

### Check Logs
```bash
# Filter GAURANGA logs
adb logcat -s BootReceiver AutoStartManager BiometricAuthManager
```

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Startup Time | ~2-5 detik |
| Biometric Verify | ~1 detik |
| Service Start | ~1 detik |
| Total Boot to Active | ~5-10 detik |

---

## 🚀 Future Enhancements

- [ ] Widget untuk quick toggle
- [ ] Scheduled auto-start (e.g., 6 AM daily)
- [ ] Background sync with server
- [ ] Push notification for updates
- [ ] Remote wipe capability

---

## 📞 Support

If auto-start still doesn't work:
1. Check manufacturer-specific settings
2. Disable battery optimization
3. Enable all permissions
4. Contact: 081337558787 (Pak Pur)

---

**Version:** 1.1.0
**Updated:** 11 Juli 2026
**Status:** ✅ Production Ready
