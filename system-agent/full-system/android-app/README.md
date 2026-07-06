# GAURANGA FULL SYSTEM AGENT - Android App

## Overview

GAURANGA Full System Agent adalah aplikasi Android yang berjalan di level sistem dengan kemampuan:
- Accessibility Service untuk kontrol penuh UI
- Foreground Service untuk always-on operation
- Overlay Service untuk floating UI
- Boot receiver untuk auto-start

## Arsitektur

```
┌─────────────────────────────────────────────────────┐
│                  ANDROID SYSTEM                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────────────────────────┐ │
│  │  GAURANGA SYSTEM AGENT                       │ │
│  │                                              │ │
│  │  ┌─────────────┐  ┌─────────────────────┐  │ │
│  │  │ Accessibility │  │ Foreground Service │  │ │
│  │  │   Service    │  │  (Always On)       │  │ │
│  │  └─────────────┘  └─────────────────────┘  │ │
│  │                                              │ │
│  │  ┌─────────────┐  ┌─────────────────────┐  │ │
│  │  │   Overlay   │  │   Boot Receiver    │  │ │
│  │  │   Service   │  │  (Auto Start)      │  │ │
│  │  └─────────────┘  └─────────────────────┘  │ │
│  │                                              │ │
│  │  ┌─────────────────────────────────────┐  │ │
│  │  │     GAURANGA CORE (Python + LLM)     │  │ │
│  │  └─────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Components

### 1. MainActivity
- Entry point aplikasi
- Permission requests
- Service management UI

### 2. GaurangaAccessibilityService
- Membaca konten layar
- Simulasi sentuhan
- Mengintercept event UI
- Overlay detection

### 3. GaurangaForegroundService  
- Tetap berjalan di background
- Notifikasi persistent
- Python subprocess management

### 4. GaurangaOverlayService
- Floating button
- Chat interface overlay
- Quick actions

### 5. BootReceiver
- Start service saat boot
- Auto-restart jika crash

## Installation

### Requirements
- Android 8.0+ (API 26)
- Root access (untuk auto-start optimal)

### Steps

1. Install APK
2. Grant permissions:
   - Accessibility Service
   - Overlay Permission
   - Background App Access
3. Start service
4. (Optional) Grant root via Magisk module

## Source Files

```
android-app/
├── app/
│   ├── src/main/
│   │   ├── java/com/gauranga/agent/
│   │   │   ├── MainActivity.kt
│   │   │   ├── services/
│   │   │   │   ├── GaurangaService.kt
│   │   │   │   ├── AccessibilityService.kt
│   │   │   │   └── OverlayService.kt
│   │   │   ├── receivers/
│   │   │   │   └── BootReceiver.kt
│   │   │   └── core/
│   │   │       ├── GaurangaCore.kt
│   │   │       └── IntentClassifier.kt
│   │   ├── python/
│   │   │   └── gauranga_agent.py
│   │   └── res/
│   └── build.gradle.kts
└── README.md
```

## Usage

### Start Service
```kotlin
val intent = Intent(this, GaurangaForegroundService::class.java)
startForegroundService(intent)
```

### Trigger via Floating Button
```kotlin
// Floating button di overlay
// Tap untuk open chat interface
```

### Voice Activation
```
Katakan "Hey GAURANGA" 
→ Service mendeteksi dan aktif
→ Agent siap menerima perintah
```

## Security

- Semua data tersimpan lokal
- Encrypted SharedPreferences
- Biometric untuk unlock
- No cloud dependency

## Status: 🚀 DEVELOPMENT