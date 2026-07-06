# 📱 GAURANGA SYSTEM AGENT - INSTALLATION GUIDE

## Panduan Lengkap Install di HP Baru

---

## 📋 PILIHAN INSTALLASI

### **Option A: Termux (Paling Mudah - Tanpa Root)**
- ✅ Tidak perlu root
- ✅ Bisa langsung install sekarang
- ⚠️ Fitur terbatas (tidak bisa kontrol UI HP lain)

### **Option B: Full Android App (Tanpa Root)**
- ✅ UI lengkap
- ✅ Floating button
- ⚠️ Perlu build APK

### **Option C: Magisk Module (Dengan Root)**
- ✅ Full system access
- ✅ Auto-start
- ✅ Kontrol penuh
- ❌ Perlu root

---

# ===========================================
# OPTION A: TERMUX (DIREKOMENDASIKAN)
# ===========================================

## Langkah 1: Install Termux

1. Buka browser di HP
2. Kunjungi **F-Droid** (BUKAN Google Play):
   ```
   https://f-droid.org/en/packages/com.termux/
   ```
3. Download dan install Termux
4. Buka Termux

> ⚠️ **PENTING:** Jangan install dari Google Play! Versi di Play Store sudah outdated dan tidak bekerja dengan baik.

## ⚠️ PENTING: AKTIFKAN FINGERPRINT DULU!

Sebelum install GAURANGA, pastikan fingerprint sudah aktif:

1. **Settings → Security → Fingerprint** (atau Face ID)
2. **Tambahkan fingerprint** Anda (Pak Pur)
3. **Verifikasi** fingerprint berfungsi

GAURANGA akan meminta fingerprint untuk autentikasi saat dibuka!

## Langkah 2: Setup Termux

Di Termux, jalankan perintah berikut:

```bash
# Update packages
pkg update && pkg upgrade -y

# Install dependencies
pkg install git python -y

# Beri akses storage
termux-setup-storage
```

## Langkah 3: Clone Project

```bash
# Clone GAURANGA
git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git

# Masuk ke folder
cd Alpha-agent-Gaurangga/system-agent
```

## Langkah 4: Install Python Dependencies

```bash
pip install pyyaml numpy
```

## Langkah 5: Jalankan GAURANGA

```bash
# Test mode
python gauranga_agent.py --test

# Interactive mode
python gauranga_agent.py

# Voice mode
python gauranga_agent.py --voice
```

## Langkah 6: Auto-Start (Optional)

```bash
# Edit crontab
crontab -e

# Tambahkan baris ini (untuk auto-start saat Termux dibuka)
@reboot cd ~/Alpha-agent-Gaurangga/system-agent && python gauranga_agent.py --daemon
```

---

# ===========================================
# FINGERPRINT / BIOMETRIC SETUP
# ===========================================

GAURANGA menggunakan fingerprint untuk keamanan. Berikut cara setup:

## Di HP Baru:

### 1. Aktifkan Fingerprint

```
Settings → Security → Fingerprint
```

### 2. Tambahkan Fingerprint

1. Tap "Add fingerprint"
2. Letakkan jari di sensor
3. Angkat dan letakkan kembali (berulang)
4. Beri nama: "Pak Pur"

### 3. Verifikasi

Coba unlock HP dengan fingerprint untuk memastikan berfungsi.

## Di GAURANGA App:

1. Buka GAURANGA
2. Akan muncul screen fingerprint
3. Letakkan jari di sensor
4. ✅ Autentikasi berhasil!

> ⚠️ **Catatan:** Jika fingerprint gagal 5x, gunakan PIN/Pattern sebagai fallback.

---

# ===========================================
# OPTION B: FULL ANDROID APP (TANPA ROOT)
# ===========================================

## Langkah 1: Install Prerequisites

Di PC, install Android Studio:
```
https://developer.android.com/studio
```

## Langkah 2: Setup Project

1. Clone repo ke PC:
   ```bash
   git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git
   ```

2. Buka Android Studio
3. Open project: `system-agent/full-system/android-app`

## Langkah 3: Setup Ollama SDK

Tambahkan di `build.gradle`:
```gradle
dependencies {
    implementation 'org.ollama.android:sdk:1.0.0'
}
```

## Langkah 4: Build APK

```bash
cd system-agent/full-system/android-app
./build.sh
```

## Langkah 5: Install di HP

1. Copy APK ke HP
2. Enable "Install from unknown sources" di HP
3. Install APK
4. Buka app dan grant permissions:
   - ✅ Accessibility Service
   - ✅ Overlay Permission
   - ✅ Notification access

## Langkah 6: Start Service

1. Buka GAURANGA app
2. Tap "START"
3. GAURANGA Agent aktif!

---

# ===========================================
# OPTION C: MAGISK MODULE (DENGAN ROOT)
# ===========================================

## Prerequisites

- HP sudah di-root dengan Magisk
- Magisk Manager terinstall

## Langkah 1: Build Module ZIP

Di PC, jalankan:
```bash
cd system-agent/full-system/magisk-module
zip -r gauranga-module.zip .
```

## Langkah 2: Install Module

1. Copy ZIP ke HP
2. Buka Magisk Manager
3. Tap "Modules"
4. Tap "Install from storage"
5. Pilih file ZIP
6. Reboot HP

## Langkah 3: Verifikasi

```bash
# Di Termux atau ADB shell
su
gauranga-agent status
```

## Langkah 4: Start/Stop

```bash
# Start
gauranga-agent start

# Stop
gauranga-agent stop

# Status
gauranga-agent status
```

---

# ===========================================
# SETUP OLLAMA (UNTUK AI OFFLINE)
# ===========================================

Setelah basic install, untuk AI offline:

## Langkah 1: Install Ollama

Di Termux:
```bash
# Download Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Atau download binary langsung
curl -LO https://github.com/ollama/ollama/releases/latest/download/ollama-linux-arm64.zip
unzip ollama-linux-arm64.zip
```

## Langkah 2: Download Model

```bash
# Pull Llama 3.2 (3GB)
ollama pull llama3.2:1b

# Atau model lebih kecil (lebih cepat)
ollama pull phi4:latest
```

## Langkah 3: Start Ollama

```bash
# Start daemon
ollama serve &

# Test
ollama list
```

## Langkah 4: Test GAURANGA with AI

```bash
python gauranga_agent.py --test
```

---

# ===========================================
# TROUBLESHOOTING
# ===========================================

## Termux Error: "Permission denied"

```bash
termux-setup-storage
# Pilih Allow
```

## Ollama not found

```bash
# Cek instalasi
which ollama

# Install manual
curl -LO https://ollama.com/install.sh
sh install.sh
```

## Python module error

```bash
pip install --upgrade pip
pip install pyyaml numpy requests
```

## Overlay not working

1. Settings → Apps → GAURANGA
2. Tap "Display over other apps"
3. Enable permission

## Accessibility not working

1. Settings → Accessibility
2. Find "GAURANGA"
3. Enable and grant permission

## Service won't start

```bash
# Check logs
logcat | grep GAURANGA

# Or in Termux
python gauranga_agent.py -v
```

---

# ===========================================
# QUICK COMMANDS REFERENCE
# ===========================================

```bash
# Start GAURANGA
gauranga

# Test mode
gauranga --test

# Voice mode
gauranga --voice

# Daemon mode (background)
gauranga --daemon

# Help
gauranga --help
```

---

# ===========================================
# PERMISSIONS YANG DIPERLUKAN
# ===========================================

| Permission | Fungsi | WAJIB? |
|------------|--------|---------|
| Storage | Akses file | ✅ Ya |
| Accessibility | Kontrol UI | ✅ Ya |
| Overlay | Floating button | ⚡ Rekomendasi |
| Notification | Service running | ⚡ Rekomendasi |
| Microphone | Voice input | ❌ Optional |

---

# 📞 BUTUH BANTUAN?

- **WhatsApp:** 081337558787 (Pak Pur)
- **GitHub Issues:** https://github.com/prahlad168/Alpha-agent-Gaurangga/issues

---

**Owner:** I Made Purna Ananda (Pak Pur)
**Company:** MAHA LAKSHMI HOLDINGS
**Version:** 1.0.0