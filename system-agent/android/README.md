# Android Integration Guide

## GAURANGA System Agent - Android Setup

### Option 1: Termux + GAURANGA (Recommended)

**Step 1: Install Termux**
- Download from F-Droid (NOT Google Play)
- https://f-droid.org/en/packages/com.termux/

**Step 2: Grant Storage Permission**
```bash
termux-setup-storage
```

**Step 3: Run Setup**
```bash
pkg update && pkg upgrade
pkg install git python

# Clone project
git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git
cd Alpha-agent-Gaurangga/system-agent

# Run setup
chmod +x setup.sh
./setup.sh
```

**Step 4: Start Ollama**
```bash
ollama serve &
```

**Step 5: Start GAURANGA**
```bash
python gauranga_agent.py
```

### Option 2: Shizuku Integration

Shizuku allows running apps with higher privileges.

**Install Shizuku:**
1. Install Shizuku from F-Droid
2. Grant via ADB:
```bash
adb shell sh /storage/emulated/0/Android/data/moe.shizuku.privileged.api/start.sh
```

**Use with Termux:**
```bash
pkg install termux-api
```

### Option 3: Fully Embedded (For Development)

Build as Python package:
```bash
pip install -e .
gauranga
```

---

## System-Level Integration (Root Required)

For true system-level agent, you need:

### 1. Root Access
```bash
# Check if rooted
su -c "echo YES"
```

### 2. Magisk Module
Create a Magisk module that:
- Installs GAURANGA to system
- Adds to init.d scripts
- Sets up background service

### 3. Accessibility Service
Create an accessibility service that can:
- Read screen content
- Perform gestures
- Intercept intents

### 4. Overlay Permission
For floating UI elements.

---

## Quick Commands

```bash
# Interactive mode
gauranga

# Voice mode
gauranga --voice

# Daemon mode
gauranga --daemon

# Test mode
gauranga --test
```

---

## Permissions Required

### Termux
- Storage (termux-setup-storage)
- Internet (for Ollama downloads)

### System-Level (Root)
- READ_EXTERNAL_STORAGE
- WRITE_EXTERNAL_STORAGE
- SYSTEM_ALERT_WINDOW
- BIND_ACCESSIBILITY_SERVICE
- FOREGROUND_SERVICE
- RECEIVE_BOOT_COMPLETED