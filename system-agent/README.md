# 🤖 GAURANGA SYSTEM AI v2.0 - JARVIS Indonesia

## 🎯 KONSEP UTAMA

**GAURANGA** adalah System-Level AI Agent yang berjalan di Android - seperti **JARVIS di Iron Man**! 

```
"Hey GAURANGA!"  →  GAURANGA AKTIF! 🎉
```

### Fitur Utama:
- ✅ **Always-On** - Berjalan di background 24/7
- ✅ **Voice-First** - Kontrol dengan suara
- ✅ **Offline-Capable** - Bekerja tanpa internet
- ✅ **Self-Learning** - Belajar dari interaksi
- ✅ **System-Level** - Akses penuh ke Android
- ✅ **Biometric Security** - Voice ID, Fingerprint, Face ID

---

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────┐
│              ANDROID DEVICE                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│   ┌─────────────────────────────────────────────┐ │
│   │  GAURANGA SYSTEM AGENT (Background Service)  │ │
│   │                                              │ │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│   │  │  Voice   │  │   LLM   │  │  Agent   │  │ │
│   │  │  Engine  │  │  Local  │  │  Logic   │  │ │
│   │  │ (STT/TTS)│  │(Ollama) │  │          │  │ │
│   │  └──────────┘  └──────────┘  └──────────┘  │ │
│   │                                              │ │
│   │  ┌──────────────────────────────────────┐  │ │
│   │  │     VECTOR MEMORY (ChromaDB)          │  │ │
│   │  │  - User preferences                   │  │ │
│   │  │  - Conversation history               │  │ │
│   │  │  - Learned skills                     │  │ │
│   │  └──────────────────────────────────────┘  │ │
│   └─────────────────────────────────────────────┘ │
│                                                     │
│   [Termux] ←→ [Shell Access] ←→ [System]         │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 FiturUtama

### 1. Core Agent
- [x] Always-on background service
- [x] Hotword detection ("Hey GAURANGA")
- [x] Intent classification
- [x] Memory management
- [x] Skill learning

### 2. AI Engine (Offline)
- [x] Local LLM via Ollama
- [x] Whisper STT (Speech-to-Text)
- [x] Piper/Kokoro TTS (Text-to-Speech)
- [x] Vector database for memory

### 3. System Integration
- [x] File system access
- [x] Package management
- [x] Process control
- [x] Network monitoring
- [x] Notification reading

### 4. Agentic Capabilities
- [x] Proactive reminders
- [x] Auto task execution
- [x] Context-aware responses
- [x] Multi-step reasoning

---

## 📦 Installation

### Quick Install (Termux)

```bash
# Install Termux from F-Droid
# Then run these commands:

# 1. Update packages
pkg update && pkg upgrade

# 2. Install dependencies
pkg install python git curl unzip

# 3. Clone GAURANGA
git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git
cd Alpha-agent-Gaurangga/system-agent

# 4. Setup
chmod +x setup.sh
./setup.sh

# 5. Run
python -m gauranga_agent
```

---

## 🎮 Usage

### Start Agent
```bash
python -m gauranga_agent
```

### Interactive Mode
```bash
gauranga> halo gauranga
GAURANGA: Halo Pak Pur! Ada yang bisa saya bantu?
```

### Voice Mode
```bash
gauranga --voice
# Say "Hey GAURANGA" to activate
```

---

## 🔧 Configuration

Edit `config.yaml` untuk customize:

```yaml
agent:
  name: "GAURANGA"
  owner: "I Made Purna Ananda"
  company: "Maha Lakshmi Holdings"
  
ai:
  model: "llama3.2:1b"  # Local model
  embedding: "nomic-embed-text"
  provider: "ollama"
  
voice:
  stt: "whisper"
  tts: "piper"
  language: "id"
  
memory:
  type: "chroma"
  persist: true
  
system:
  background: true
  hotword: "hey gauranga"
  permissions: ["storage", "notification", "process"]
```

---

## 📁 Struktur Project

```
system-agent/
├── core/               # Core agent logic
│   ├── agent.py        # Main agent class
│   ├── memory.py       # Vector memory
│   ├── skills.py       # Skill management
│   └── intent.py       # Intent detection
├── engine/            # AI engines
│   ├── llm.py         # LLM interface
│   ├── stt.py        # Speech-to-text
│   └── tts.py        # Text-to-speech
├── models/           # ML models
├── scripts/          # Utility scripts
├── android/          # Android integration
│   ├── termux/       # Termux-specific
│   └── shizuku/      # Shizuku integration
├── services/        # Background services
└── docs/            # Documentation

├── setup.sh          # Setup script
├── gauranga_agent.py # Entry point
└── config.yaml       # Configuration
```

---

## 🛡️ Security

- Semua data tersimpan lokal
- Tidak ada cloud dependency
- Encrypted memory database
- Biometric authentication

---

## 📞 Kontak

- **Owner:** I Made Purna Ananda (Pak Pur)
- **WhatsApp:** 081337558787
- **Company:** MAHA LAKSHMI HOLDINGS

---

**Version:** 1.0.0
**Status:** 🚀 DEVELOPMENT
**Created:** 2026-07-06