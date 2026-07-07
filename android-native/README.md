# GAURANGA Alpha - Android Native App

## 🎤🔊 24/7 Voice Assistant - Offline Ready

Native Android app dengan fitur **Speech-to-Text** dan **Text-to-Speech** yang работает **offline**!

### ✨ Fitur Utama

| Fitur | Status | Keterangan |
|-------|--------|------------|
| 🎤 Speech-to-Text Offline | ✅ | Menggunakan Vosk (Indonesian model) |
| 🔊 Text-to-Speech Offline | ✅ | Android TTS Engine (bundled voice) |
| 📱 24/7 Service | ✅ | Foreground service, tetap aktif |
| 🔄 Wake Word Detection | 🔄 | "Hey GAURANGA" (coming soon) |
| 🚀 Background Listening | ✅ | Tetap mendengarkan saat app minimized |
| 📴 Fully Offline | ✅ | Tidak butuh internet setelah install |

### 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────┐
│                  GAURANGA APP                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────┐    ┌─────────────────────────┐ │
│  │   UI Layer  │◄──►│    Voice Engine        │ │
│  │  MainActivity│    │ ┌───────────┐ ┌──────┐│ │
│  └─────────────┘    │ │   STT     │ │ TTS  ││ │
│                      │ │ (Vosk)    │ │(TTS) ││ │
│                      │ └───────────┘ └──────┘│ │
│                      └─────────────────────────┘ │
│                              │                   │
│                      ┌───────▼────────┐         │
│                      │ 24/7 Service   │         │
│                      │ (Foreground)  │         │
│                      └───────────────┘         │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 📁 Struktur Project

```
android-native/
├── app/
│   ├── src/main/
│   │   ├── java/com/gaurangga/alpha/
│   │   │   ├── GaurangaApp.kt          # Application class
│   │   │   ├── ui/
│   │   │   │   └── MainActivity.kt     # Main UI
│   │   │   ├── stt/
│   │   │   │   └── OfflineSpeechRecognizer.kt  # Vosk STT
│   │   │   ├── tts/
│   │   │   │   └── OfflineTextToSpeech.kt     # Android TTS
│   │   │   ├── service/
│   │   │   │   └── GaurangaVoiceService.kt    # 24/7 Service
│   │   │   └── utils/
│   │   │       └── BootReceiver.kt            # Auto-start
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   └── activity_main.xml
│   │   │   ├── values/
│   │   │   │   ├── colors.xml
│   │   │   │   ├── strings.xml
│   │   │   │   └── themes.xml
│   │   │   └── ...
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
├── build.gradle.kts
├── settings.gradle.kts
└── gradle.properties
```

### 🚀 Cara Build

```bash
# 1. Install Gradle (if not present)
brew install gradle  # macOS
# atau download dari https://gradle.org/install

# 2. Build debug APK
cd android-native
./gradlew assembleDebug

# 3. APK ada di:
# app/build/outputs/apk/debug/app-debug.apk
```

### 📱 Cara Install

```bash
# Via ADB
adb install app/build/outputs/apk/debug/app-debug.apk

# Atau copy APK ke HP dan install manual
```

### 🎯 Cara Pakai

1. **Install APK** di HP Android
2. **Buka app** → Grant microphone permission
3. **Klik "START 24/7"** → Service akan jalan di background
4. **Klik tombol 🎤** untuk bicara
5. **App akan jawab dengan suara** (offline!)

### 🔧 Fitur Lanjutan

#### Wake Word (Coming Soon)
```kotlin
// "Hey GAURANGA" detection
wakeWordDetector.start { 
    // Aktifkan listening
    startVoiceInput()
}
```

#### Auto-start on Boot
```kotlin
// Service otomatis start saat HP dinyalakan
// (Aktif secara default)
```

### ⚙️ Requirements

- **Android:** 8.0 (API 26) atau lebih tinggi
- **Storage:** ~100MB untuk Vosk model
- **RAM:** 2GB+
- **Microphone:** Required

### 📦 Dependencies

| Library | Version | Fungsi |
|---------|---------|--------|
| Vosk Android | 0.3.47 | Offline Speech Recognition |
| TensorFlow Lite | 2.14.0 | Wake Word Detection |
| AndroidX | Latest | UI Components |
| Kotlin Coroutines | 1.7.3 | Async Operations |

### 🐛 Troubleshooting

**Q: TTS tidak berbahasa Indonesia?**
```bash
# Install offline voice di Settings → Language → Text-to-Speech
```

**Q: STT tidak bekerja offline?**
```bash
# Pastikan Vosk model sudah ter-download
# (Terjadi otomatis saat pertama kali buka app)
```

**Q: Service mati setelah beberapa jam?**
```bash
# Matikan battery optimization untuk GAURANGA
# Settings → Apps → GAURANGA → Battery → Unrestricted
```

### 📄 License

MIT License - MAHA LAKSHMI CORP

---

**Dibuat dengan ❤️ untuk Pak Pur**  
*GAURANGA Alpha v1.0.0*
