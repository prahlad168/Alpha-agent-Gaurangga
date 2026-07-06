# 💾 GAURANGA Memory Management Skill

## 📋 Skill Overview

| Field | Value |
|-------|-------|
| **Skill Name** | Local Memory Management |
| **Category** | System / Data Management |
| **Level** | Expert |
| **Author** | GAURANGA Team |
| **Version** | 1.0.0 |

---

## 🎯 Deskripsi Skill

Skill ini mengelola penyimpanan lokal, enkripsi, dan transfer data memori GAURANGA secara on-device. Semua data disimpan secara lokal tanpa cloud sync untuk menjaga privasi dan keamanan data Pak Pur.

---

## 🔧 Fitur Utama

### 1. Penyimpanan Lokal (On-Device Storage)

```
┌─────────────────────────────────────────────────────────┐
│  💾 PENYIMPANAN LOKAL                                 │
├─────────────────────────────────────────────────────────┤
│  ✅ Database: SQLite (Python) / IndexedDB (Web)        │
│  ✅ Path: ./data/local_memory/gauranga_memory.db        │
│  ✅ Enkripsi: AES-256-GCM (Fernet)                    │
│  ✅ Kompresi: zlib untuk efisiensi storage               │
│  ❌ Cloud Sync: TIDAK ADA (Privasi terjamin)           │
└─────────────────────────────────────────────────────────┘
```

### 2. Tipe Data yang Disimpan

| Tipe | Deskripsi | Contoh |
|------|-----------|--------|
| `general` | Memori umum | Catatan, ide |
| `conversation` | Riwayat percakapan | Chat history |
| `preference` | Preferensi pengguna | Settings, mode |
| `skill` | Skills yang dipelajari | Workflows |
| `learned` | Data pembelajaran | Patterns |
| `reminder` | Pengingat terjadwal | Meetings |
| `business` | Data bisnis | SBUs, revenue |
| `personal` | Data pribadi | Family info |
| `sensitive` | Data sensitif terenkripsi | Passwords, keys |

### 3. Enkripsi Data

```
┌─────────────────────────────────────────────────────────┐
│  🔐 ENKRIPSI AES-256                                   │
├─────────────────────────────────────────────────────────┤
│  Metode: AES-128-CBC (Fernet) / AES-GCM (Web Crypto)   │
│  Key Derivation: PBKDF2-SHA256 (100,000 iterations)   │
│  Salt: Random 32 bytes per device                      │
│  Data Dienkripsi: Konten sensitif, preference          │
│  Auto-Decrypt: Ya, saat retrieval                      │
└─────────────────────────────────────────────────────────┘
```

### 4. Transfer Data (On Command)

```
┌─────────────────────────────────────────────────────────┐
│  📤 FITUR TRANSFER - ON COMMAND ONLY                   │
├─────────────────────────────────────────────────────────┤
│  Trigger: Perintah spesifik dari Pak Pur               │
│  Format: .gmem (terenkripsi, terkompresi)              │
│  Header: Magic bytes + Version + Checksum SHA-256      │
│  Ukuran: Tergantung jumlah data                        │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Command Reference

### Perintah Ekspor Memori

| Command | Description |
|---------|-------------|
| `"gaurangga, ekspor memori"` | Ekspor semua memori |
| `"gaurangga, backup data"` | Backup semua data |
| `"gaurangga, pindahkan memori ke file"` | Export ke file |
| `"gaurangga, simpan memori ke SD card"` | Save ke external storage |

**Dengan Password:**
```
"gaurangga, ekspor memori dengan password [password]"
"gaurangga, backup terenkripsi"
```

**Tanpa Data Sensitif:**
```
"gaurangga, ekspor memori tanpa data sensitif"
```

### Perintah Impor Memori

| Command | Description |
|---------|-------------|
| `"gaurangga, impor memori"` | Import dari file |
| `"gaurangga, pulihkan data dari backup"` | Restore backup |
| `"gaurangga, masukkan file backup"` | Load backup file |
| `"gaurangga, merge memori"` | Merge dengan data existing |

**Dengan Password:**
```
"gaurangga, impor memori dengan password [password]"
```

**Replace (Hapus yang lama):**
```
"gaurangga, impor memori - replace"
```

### Perintah Info Storage

| Command | Description |
|---------|-------------|
| `"gaurangga, info memori"` | Tampilkan storage info |
| `"gaurangga, kapasitas storage"` | Check storage capacity |
| `"gaurangga, statistik memori"` | Memory statistics |

### Perintah Cleanup

| Command | Description |
|---------|-------------|
| `"gaurangga, bersihkan memori lama"` | Hapus data > 30 hari |
| `"gaurangga, bersihkan data 60 hari"` | Hapus data > 60 hari |
| `"gaurangga, optimize database"` | Vacuum & analyze DB |

---

## 🔐 Format File Export

### Struktur File `.gmem`

```
┌─────────────────────────────────────────────────────────┐
│  FILE FORMAT: .gmem                                     │
├─────────────────────────────────────────────────────────┤
│  Header (16 bytes):                                     │
│  ├── Magic: "GAURANGA_MEM"                              │
│  ├── Version: 1 byte                                    │
│  ├── Encrypted: 1 byte (0/1)                           │
│  └── Compressed: 1 byte (0/1)                           │
│                                                          │
│  Checksum: SHA-256 hash (64 hex chars)                  │
│                                                          │
│  Body: Base64 encoded encrypted/compressed data         │
└─────────────────────────────────────────────────────────┘
```

### Metadata Export

```json
{
  "version": "1.0.0",
  "agentName": "GAURANGA",
  "owner": "I Made Purna Ananda",
  "exportDate": "2026-07-06T09:00:00.000Z",
  "deviceId": "abc123def456",
  "totalMemories": 150,
  "totalConversations": 500,
  "totalPreferences": 25,
  "encrypted": true,
  "checksum": "sha256hash..."
}
```

---

## 📊 API Reference (Python)

### LocalMemoryManager

```python
from core.local_memory_manager import LocalMemoryManager

# Initialize
manager = LocalMemoryManager(config={'agent': {'owner': 'Pak Pur'}})

# Store memory
memory_id = manager.store_memory(
    content="Data rahasia bisnis",
    memory_type="business",
    tags=["bisnis", "strategi"],
    priority=3,
    encrypt=True  # Enable encryption
)

# Search memories
results = manager.search_memories(
    query="strategi",
    memory_type="business",
    tags=["bisnis"],
    limit=10
)

# Store conversation
conv_id = manager.store_conversation(
    role="user",
    content="Pertanyaan tentang revenue",
    intent="revenue_query",
    entities={"amount": 1000000}
)

# Get conversation history
history = manager.get_conversation_history(session_id="session_20260706", limit=50)

# Set preference
manager.set_preference("theme", "dark", category="ui")

# Get preference
theme = manager.get_preference("theme", default="light")

# EXPORT - ON COMMAND ONLY
export_path = manager.export_all_data(
    output_path="/sdcard/gauranga_backup.gmem",
    password="optional_password",
    include_sensitive=True
)

# IMPORT - ON COMMAND ONLY
stats = manager.import_data(
    import_path="/sdcard/gauranga_backup.gmem",
    password="optional_password",
    merge=True  # or False to replace
)

# Storage info
info = manager.get_storage_info()

# Cleanup old conversations
deleted = manager.cleanup_old_conversations(days=30)
```

---

## 📊 API Reference (JavaScript)

### LocalMemoryManager (Web)

```javascript
// Initialize
const memoryManager = new LocalMemoryManager({
    owner: 'I Made Purna Ananda'
});
await memoryManager.initialize();

// Store memory
const memoryId = await memoryManager.storeMemory({
    content: 'Data rahasia bisnis',
    type: 'business',
    tags: ['bisnis', 'strategi'],
    priority: 3,
    encrypt: true
});

// Search memories
const results = await memoryManager.searchMemories({
    query: 'strategi',
    type: 'business',
    tags: ['bisnis'],
    limit: 10
});

// Store conversation
const conv = await memoryManager.storeConversation({
    role: 'user',
    content: 'Pertanyaan tentang revenue',
    intent: 'revenue_query',
    entities: { amount: 1000000 }
});

// Get conversation history
const history = await memoryManager.getConversationHistory(limit: 50);

// Set preference
await memoryManager.setPreference('theme', 'dark', 'ui');

// Get preference
const theme = await memoryManager.getPreference('theme', 'light');

// EXPORT - ON COMMAND ONLY
const exportResult = await memoryManager.exportData({
    password: 'optional_password',
    includeSensitive: true
});
exportResult.download(); // Trigger download

// IMPORT - ON COMMAND ONLY
const stats = await memoryManager.importData(file, {
    password: 'optional_password',
    merge: true
});

// Storage info
const info = await memoryManager.getStorageInfo();

// Cleanup
const deleted = await memoryManager.cleanupOldConversations(30);
```

---

## 🎯 Contoh Penggunaan

### Scenario 1: Backup Memori Sebelum Reset HP

```
Pak Pur: "gaurangga, ekspor semua memori ke SD card"

GAURANGA: "Baik Pak, saya akan mengekspor semua memori Anda..."
         
🔐 Memulai ekspor memori...
📦 Mengumpulkan 150 memori...
📦 Mengumpulkan 500 percakapan...
📦 Mengumpulkan 25 preferensi...
🔒 Mengenkripsi data dengan AES-256...
✅ Ekspor selesai!
   File: gauranga_backup_20260706_090000.gmem
   Ukuran: 2.5 MB
   Lokasi: /storage/emulated/0/Download/
```

### Scenario 2: Pindahkan ke HP Baru

```
Pak Pur: "gaurangga, impor memori dari file backup"

GAURANGA: "Baik Pak, silakan pilih file backup..."

[File picker opens]
[User selects: gauranga_backup_20260706_090000.gmem]

GAURANGA: "📥 Memulai impor dari backup..."
🔓 Mendekripsi data...
📦 Mengimpor memori...
   ✅ 150 memori diimpor
   ✅ 500 percakapan diimpor
   ✅ 25 preferensi diimpor
🎉 Impor selesai! Semua data berhasil dipindahkan.
```

### Scenario 3: Info Storage

```
Pak Pur: "gaurangga, info memori"

GAURANGA: 📊 Statistik Memori GAURANGA

💾 Database:
   • Lokasi: ./data/local_memory/
   • Ukuran: 2.5 MB
   • Enkripsi: ✅ Aktif (AES-256)

📦 Data Tersimpan:
   • Memori: 150 items
   • Percakapan: 500 items
   • Preferensi: 25 items

🔒 Keamanan:
   • Device ID: abc123def456
   • Key Salt: ✅ Tersimpan
   • Auto-Encrypt: Aktif untuk data sensitif

🗑️ Kapasitas: 78% tersedia
```

---

## ⚠️ Catatan Keamanan

1. **Tidak Ada Cloud Sync**: Semua data disimpan lokal, tidak pernah dikirim ke server manapun
2. **Enkripsi Default**: Data sensitif dienkripsi otomatis dengan AES-256
3. **Password Protection**: Untuk backup, gunakan password tambahan untuk keamanan ekstra
4. **Device-Specific Key**: Kunci enkripsi derived dari informasi perangkat + nama owner
5. **Checksum Verification**: Setiap file backup diverifikasi integritasnya dengan SHA-256

---

## 🚀 CLI Commands (Python)

```bash
# Export memories
python -m core.local_memory_manager --export --output ./backup.gmem

# Export with password
python -m core.local_memory_manager --export --output ./backup.gmem --password "secret123"

# Import memories
python -m core.local_memory_manager --import ./backup.gmem

# Import with password
python -m core.local_memory_manager --import ./backup.gmem --password "secret123"

# Storage info
python -m core.local_memory_manager --info

# Cleanup old data
python -m core.local_memory_manager --cleanup --days 30
```

---

## 📞 Dukungan

Jika ada pertanyaan tentang penggunaan skill ini:

1. **Dokumentasi**: Lihat file `07-memory-management.md`
2. **Source Code**: `system-agent/core/local_memory_manager.py`
3. **Web Implementation**: `android-app/js/local-memory-manager.js`

---

**Version:** 1.0.0
**Created:** 2026-07-06
**Status:** 🚀 ACTIVE
**Author:** GAURANGA Team
