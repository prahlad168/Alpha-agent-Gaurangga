# 🚀 INSTALASI LANGSUNG ALPHA GAURANGA DI HP

## PERSYARATAN
- HP Android dengan Termux terinstall
- Koneksi internet (untuk download)
- Penyimpanan minimal 500MB

---

## CARA 1: INSTALL VIA TERMUX (REKOMENDASI)

### Step 1: Install Termux
1. Buka browser HP
2. Kunjungi: **https://f-droid.org**
3. Download & install **Termux** (BUKAN dari Play Store)
4. Buka Termux

### Step 2: Update Package
```bash
pkg update && pkg upgrade -y
```

### Step 3: Install Python & Dependencies
```bash
pkg install python git nodejs -y
pip install --upgrade pip
```

### Step 4: Clone Project
```bash
cd ~/storage/shared
git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git
cd Alpha-agent-Gaurangga/system-agent
```

### Step 5: Install Python Libraries
```bash
pip install -r requirements.txt
```

### Step 6: Install Audio Packages
```bash
pkg install espeak-ng ffmpeg sox -y
```

### Step 7: Jalankan!
```bash
python3 gauranga_agent.py --always-on
```

---

## CARA 2: AUTO-INSTALL (1 COMMAND)

Buka Termux, paste ini:

```bash
pkg update && pkg upgrade -y && pkg install python git nodejs espeak-ng ffmpeg sox -y && cd ~/storage/shared && git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git && cd Alpha-agent-Gaurangga/system-agent && pip install -r requirements.txt && python3 gauranga_agent.py --always-on
```

---

## CARA 3: INSTALL SEBAGAI APP (PWA)

### Di Browser Chrome/Edge HP:
1. Buka: **https://prahlad168.github.io/Alpha-agent-Gaurangga/**
2. Tunggu loading selesai
3. Ketuk menu (3 titik) di kanan atas
4. Pilih **"Tambahkan ke Layar Utama"**
5. Ketuk **"Tambahkan"**
6. Selesai! Icon GAURANGA muncul di layar utama

---

## CARA 4: VIA ANDROID STUDIO (ADVANCED)

```bash
# Clone di PC
git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git

# Buka di Android Studio
# File > New > Import Project
# Pilih folder android-app

# Run di emulator atau device
```

---

## 🔧 JIKA ERROR

### Error: "package not found"
```bash
pkg update
```

### Error: "pip command not found"
```bash
python3 -m pip install -r requirements.txt
```

### Error: "Permission denied"
```bash
termux-setup-storage
```

### Error: "No module named..."
```bash
pip install nama_module
```

---

## 📱 FITUR SETELAH INSTALL

| Fitur | Status |
|-------|--------|
| 🎤 Voice Recognition | ✅ |
| 🔊 Text-to-Speech | ✅ |
| 👂 Always-On Listening | ✅ |
| 💾 Local Memory | ✅ |
| 🔐 Multi-Layer Encryption | ✅ |
| 🏢 Company Management | ✅ |
| 📸 Camera Access | ✅ |
| 🐦 Social Media | ✅ |
| 🌐 100+ Languages | ✅ |

---

## ⚡ QUICK COMMANDS

```bash
# Start Alpha Gaurangga
python3 gauranga_agent.py

# Start dengan Always-On (24/7)
python3 gauranga_agent.py --always-on

# Start dengan debug mode
python3 gauranga_agent.py --debug

# Test voice
python3 -c "from engine.tts import TTSEngine; t=TTSEngine({'voice':{'tts':'system'}}); t.speak('Halo Pak Pur, Alpha Gaurangga aktif!')"
```

---

## 🌐 INSTALL WEB VERSION (TANPA TERMUX)

Buka di browser HP:
```
https://prahlad168.github.io/Alpha-agent-Gaurangga/
```

Lalu:
1. Klik menu (⋮)
2. Pilih "Tambahkan ke Layar Utama"
3. Selesai!

---

## ❓ BANTUAN

**WhatsApp:** 081337558787 (Pak Pur)

**GitHub Issues:** https://github.com/prahlad168/Alpha-agent-Gaurangga/issues

---

## ✅ VERIFIKASI INSTALL

Setelah install, ketik di Alpha Gaurangga:
```
tes suara
```

Jika Alpha Gaurangga bicara, berarti install BERHASIL! 🎉
