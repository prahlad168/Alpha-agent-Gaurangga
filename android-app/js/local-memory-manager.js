/**
 * GAURANGA Local Memory Manager (JavaScript/Web Version)
 * On-Device Memory Management System dengan IndexedDB dan Web Crypto API
 * 
 * Fitur:
 * - Penyimpanan lokal menggunakan IndexedDB
 * - Enkripsi AES-GCM untuk data sensitif
 * - Ekspor/Migrasi data memori dengan perintah khusus
 * - Format eksport terenkripsi (.gmem)
 * 
 * Author: GAURANGA Team
 * Owner: I Made Purna Ananda (Pak Pur)
 */

// ==========================================
// CONSTANTS & ENUMS
// ==========================================

const MemoryType = {
    GENERAL: 'general',
    CONVERSATION: 'conversation',
    PREFERENCE: 'preference',
    SKILL: 'skill',
    LEARNED: 'learned',
    REMINDER: 'reminder',
    BUSINESS: 'business',
    PERSONAL: 'personal',
    SENSITIVE: 'sensitive'
};

const MemoryPriority = {
    LOW: 1,
    MEDIUM: 2,
    HIGH: 3,
    CRITICAL: 4
};

const DB_NAME = 'GAURANGA_MEMORY_DB';
const DB_VERSION = 1;

// ==========================================
// LOCAL MEMORY MANAGER CLASS
// ==========================================

class LocalMemoryManager {
    constructor(options = {}) {
        this.storagePath = options.storagePath || 'gauranga_local';
        this.owner = options.owner || 'Pak Pur';
        this.deviceId = null;
        this.encryptionKey = null;
        this.db = null;
        this.version = '1.0.0';
        
        // Event listeners
        this._listeners = {};
    }
    
    // ==========================================
    // INITIALIZATION
    // ==========================================
    
    async initialize() {
        try {
            // Get or create device ID
            await this._initDeviceId();
            
            // Initialize IndexedDB
            await this._initDatabase();
            
            // Initialize encryption
            await this._initEncryption();
            
            console.log('✅ LocalMemoryManager initialized');
            return true;
        } catch (error) {
            console.error('Failed to initialize LocalMemoryManager:', error);
            return false;
        }
    }
    
    async _initDeviceId() {
        const stored = localStorage.getItem('gauranga_device_id');
        if (stored) {
            this.deviceId = stored;
        } else {
            this.deviceId = this._generateUUID().substring(0, 16);
            localStorage.setItem('gauranga_device_id', this.deviceId);
        }
    }
    
    async _initDatabase() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);
            
            request.onerror = () => reject(request.error);
            
            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Create memories store
                if (!db.objectStoreNames.contains('memories')) {
                    const memoriesStore = db.createObjectStore('memories', { keyPath: 'id' });
                    memoriesStore.createIndex('type', 'type', { unique: false });
                    memoriesStore.createIndex('createdAt', 'createdAt', { unique: false });
                    memoriesStore.createIndex('tags', 'tags', { unique: false, multiEntry: true });
                }
                
                // Create conversations store
                if (!db.objectStoreNames.contains('conversations')) {
                    const convStore = db.createObjectStore('conversations', { keyPath: 'id' });
                    convStore.createIndex('sessionId', 'sessionId', { unique: false });
                    convStore.createIndex('timestamp', 'timestamp', { unique: false });
                }
                
                // Create preferences store
                if (!db.objectStoreNames.contains('preferences')) {
                    db.createObjectStore('preferences', { keyPath: 'key' });
                }
                
                // Create sessions store
                if (!db.objectStoreNames.contains('sessions')) {
                    db.createObjectStore('sessions', { keyPath: 'id' });
                }
                
                // Create export metadata store
                if (!db.objectStoreNames.contains('export_history')) {
                    db.createObjectStore('export_history', { keyPath: 'timestamp' });
                }
            };
        });
    }
    
    async _initEncryption() {
        try {
            // Derive key from device info
            const keyMaterial = await crypto.subtle.importKey(
                'raw',
                this._stringToBuffer(`GAURANGA_${this.owner}_${new Date().getFullYear()}`),
                'PBKDF2',
                false,
                ['deriveBits', 'deriveKey']
            );
            
            // Get or create salt
            let salt = localStorage.getItem('gauranga_key_salt');
            if (!salt) {
                salt = this._arrayBufferToBase64(crypto.getRandomValues(new Uint8Array(32)));
                localStorage.setItem('gauranga_key_salt', salt);
            }
            
            // Derive encryption key
            this.encryptionKey = await crypto.subtle.deriveKey(
                {
                    name: 'PBKDF2',
                    salt: this._base64ToBuffer(salt),
                    iterations: 100000,
                    hash: 'SHA-256'
                },
                keyMaterial,
                { name: 'AES-GCM', length: 256 },
                false,
                ['encrypt', 'decrypt']
            );
            
            console.log('🔐 Encryption initialized');
        } catch (error) {
            console.warn('Encryption initialization failed, using fallback:', error);
            this.encryptionKey = null;
        }
    }
    
    // ==========================================
    // ENCRYPTION METHODS
    // ==========================================
    
    async _encrypt(data) {
        if (!this.encryptionKey) return data;
        
        try {
            const iv = crypto.getRandomValues(new Uint8Array(12));
            const encoded = this._stringToBuffer(JSON.stringify(data));
            
            const encrypted = await crypto.subtle.encrypt(
                { name: 'AES-GCM', iv },
                this.encryptionKey,
                encoded
            );
            
            // Combine IV + encrypted data
            const combined = new Uint8Array(iv.length + encrypted.byteLength);
            combined.set(iv);
            combined.set(new Uint8Array(encrypted), iv.length);
            
            return this._arrayBufferToBase64(combined);
        } catch (error) {
            console.error('Encryption failed:', error);
            return data;
        }
    }
    
    async _decrypt(encryptedData) {
        if (!this.encryptionKey) return encryptedData;
        
        try {
            const combined = this._base64ToBuffer(encryptedData);
            const iv = combined.slice(0, 12);
            const data = combined.slice(12);
            
            const decrypted = await crypto.subtle.decrypt(
                { name: 'AES-GCM', iv },
                this.encryptionKey,
                data
            );
            
            return JSON.parse(this._bufferToString(decrypted));
        } catch (error) {
            console.error('Decryption failed:', error);
            return encryptedData;
        }
    }
    
    // ==========================================
    // MEMORY OPERATIONS
    // ==========================================
    
    generateId() {
        return `mem_${this._generateUUID().substring(0, 16)}`;
    }
    
    async storeMemory({
        content,
        type = MemoryType.GENERAL,
        metadata = {},
        tags = [],
        priority = MemoryPriority.MEDIUM,
        encrypt = false,
        source = 'system'
    }) {
        const id = this.generateId();
        const now = new Date().toISOString();
        
        const entry = {
            id,
            type,
            content: encrypt ? await this._encrypt(content) : content,
            metadata,
            tags,
            priority,
            isEncrypted: encrypt,
            createdAt: now,
            updatedAt: now,
            accessedAt: now,
            accessCount: 0,
            source
        };
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['memories'], 'readwrite');
            const store = transaction.objectStore('memories');
            const request = store.add(entry);
            
            request.onsuccess = () => {
                this._emit('memoryStored', entry);
                resolve(id);
            };
            request.onerror = () => reject(request.error);
        });
    }
    
    async getMemory(id) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['memories'], 'readonly');
            const store = transaction.objectStore('memories');
            const request = store.get(id);
            
            request.onsuccess = async () => {
                const memory = request.result;
                if (memory && memory.isEncrypted) {
                    memory.content = await this._decrypt(memory.content);
                }
                
                // Update access
                if (memory) {
                    this._updateMemoryAccess(id);
                }
                
                resolve(memory);
            };
            request.onerror = () => reject(request.error);
        });
    }
    
    async _updateMemoryAccess(id) {
        const transaction = this.db.transaction(['memories'], 'readwrite');
        const store = transaction.objectStore('memories');
        
        const getRequest = store.get(id);
        getRequest.onsuccess = () => {
            const memory = getRequest.result;
            if (memory) {
                memory.accessCount = (memory.accessCount || 0) + 1;
                memory.accessedAt = new Date().toISOString();
                store.put(memory);
            }
        };
    }
    
    async searchMemories({
        query = null,
        type = null,
        tags = null,
        limit = 50,
        offset = 0
    }) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['memories'], 'readonly');
            const store = transaction.objectStore('memories');
            const results = [];
            
            const request = store.openCursor();
            
            request.onsuccess = async (event) => {
                const cursor = event.target.result;
                
                if (cursor) {
                    let memory = cursor.value;
                    
                    // Apply filters
                    let matches = true;
                    
                    if (type && memory.type !== type) matches = false;
                    if (tags && tags.length > 0) {
                        const hasTag = tags.some(tag => memory.tags.includes(tag));
                        if (!hasTag) matches = false;
                    }
                    if (query) {
                        const q = query.toLowerCase();
                        const contentMatch = memory.content.toLowerCase().includes(q);
                        const metadataMatch = JSON.stringify(memory.metadata).toLowerCase().includes(q);
                        if (!contentMatch && !metadataMatch) matches = false;
                    }
                    
                    if (matches) {
                        // Decrypt if needed
                        if (memory.isEncrypted) {
                            memory = { ...memory, content: await this._decrypt(memory.content) };
                        }
                        results.push(memory);
                    }
                    
                    cursor.continue();
                } else {
                    // Sort by priority and date
                    results.sort((a, b) => {
                        if (b.priority !== a.priority) return b.priority - a.priority;
                        return new Date(b.updatedAt) - new Date(a.updatedAt);
                    });
                    
                    resolve(results.slice(offset, offset + limit));
                }
            };
            
            request.onerror = () => reject(request.error);
        });
    }
    
    async updateMemory(id, updates) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['memories'], 'readwrite');
            const store = transaction.objectStore('memories');
            
            const getRequest = store.get(id);
            getRequest.onsuccess = () => {
                const memory = getRequest.result;
                if (!memory) {
                    resolve(false);
                    return;
                }
                
                Object.assign(memory, updates, {
                    updatedAt: new Date().toISOString()
                });
                
                const putRequest = store.put(memory);
                putRequest.onsuccess = () => resolve(true);
                putRequest.onerror = () => reject(request.error);
            };
            getRequest.onerror = () => reject(getRequest.error);
        });
    }
    
    async deleteMemory(id) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['memories'], 'readwrite');
            const store = transaction.objectStore('memories');
            const request = store.delete(id);
            
            request.onsuccess = () => {
                this._emit('memoryDeleted', { id });
                resolve(true);
            };
            request.onerror = () => reject(request.error);
        });
    }
    
    async getMemoriesByType(type) {
        return this.searchMemories({ type, limit: 1000 });
    }
    
    async getMemoriesByTag(tag) {
        return this.searchMemories({ tags: [tag], limit: 1000 });
    }
    
    // ==========================================
    // CONVERSATION OPERATIONS
    // ==========================================
    
    async storeConversation({
        role,
        content,
        intent = '',
        entities = {},
        sentiment = 'neutral',
        sessionId = null
    }) {
        const id = `conv_${this._generateUUID().substring(0, 16)}`;
        const now = new Date().toISOString();
        
        // Get or create session
        if (!sessionId) {
            sessionId = await this._getOrCreateSession();
        }
        
        const entry = {
            id,
            role,
            content,
            intent,
            entities,
            sentiment,
            timestamp: now,
            sessionId
        };
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['conversations', 'sessions'], 'readwrite');
            
            // Add conversation
            const convStore = transaction.objectStore('conversations');
            convStore.add(entry);
            
            // Update session count
            const sessionStore = transaction.objectStore('sessions');
            const sessionRequest = sessionStore.get(sessionId);
            
            sessionRequest.onsuccess = () => {
                const session = sessionRequest.result;
                if (session) {
                    session.messageCount = (session.messageCount || 0) + 1;
                    sessionStore.put(session);
                }
            };
            
            transaction.oncomplete = () => resolve({ id, sessionId });
            transaction.onerror = () => reject(transaction.error);
        });
    }
    
    async _getOrCreateSession() {
        const today = new Date().toISOString().split('T')[0];
        const sessionId = `session_${today}`;
        
        return new Promise((resolve) => {
            const transaction = this.db.transaction(['sessions'], 'readwrite');
            const store = transaction.objectStore('sessions');
            
            const getRequest = store.get(sessionId);
            getRequest.onsuccess = () => {
                if (getRequest.result) {
                    resolve(sessionId);
                } else {
                    store.add({
                        id: sessionId,
                        startedAt: new Date().toISOString(),
                        messageCount: 0
                    });
                    resolve(sessionId);
                }
            };
        });
    }
    
    async getConversationHistory(sessionId = null, limit = 100) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['conversations'], 'readonly');
            const store = transaction.objectStore('conversations');
            const results = [];
            
            const request = store.openCursor();
            
            request.onsuccess = (event) => {
                const cursor = event.target.result;
                
                if (cursor) {
                    const conv = cursor.value;
                    if (!sessionId || conv.sessionId === sessionId) {
                        results.push(conv);
                    }
                    cursor.continue();
                } else {
                    // Sort by timestamp
                    results.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
                    resolve(results.slice(-limit));
                }
            };
            
            request.onerror = () => reject(request.error);
        });
    }
    
    // ==========================================
    // PREFERENCES OPERATIONS
    // ==========================================
    
    async setPreference(key, value, category = 'general') {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['preferences'], 'readwrite');
            const store = transaction.objectStore('preferences');
            
            const request = store.put({
                key,
                value,
                category,
                updatedAt: new Date().toISOString()
            });
            
            request.onsuccess = () => {
                this._emit('preferenceUpdated', { key, value });
                resolve(true);
            };
            request.onerror = () => reject(request.error);
        });
    }
    
    async getPreference(key, defaultValue = null) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['preferences'], 'readonly');
            const store = transaction.objectStore('preferences');
            const request = store.get(key);
            
            request.onsuccess = () => {
                resolve(request.result ? request.result.value : defaultValue);
            };
            request.onerror = () => reject(request.error);
        });
    }
    
    async getAllPreferences(category = null) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['preferences'], 'readonly');
            const store = transaction.objectStore('preferences');
            const results = {};
            
            const request = store.openCursor();
            
            request.onsuccess = (event) => {
                const cursor = event.target.result;
                
                if (cursor) {
                    const pref = cursor.value;
                    if (!category || pref.category === category) {
                        results[pref.key] = pref.value;
                    }
                    cursor.continue();
                } else {
                    resolve(results);
                }
            };
            
            request.onerror = () => reject(request.error);
        });
    }
    
    // ==========================================
    // EXPORT/IMPORT (ON COMMAND)
    // ==========================================
    
    /**
     * EKSPOR DATA MEMORI - ON COMMAND ONLY
     * Fungsi ini hanya aktif ketika pengguna memberikan perintah spesifik
     */
    async exportData({
        outputPath = null,
        password = null,
        includeSensitive = true
    } = {}) {
        console.log('🔐 Starting memory export...');
        
        // Gather all data
        const data = {
            metadata: this._createExportMetadata(includeSensitive),
            memories: await this._exportMemories(includeSensitive),
            conversations: await this._exportConversations(),
            preferences: await this._exportPreferences()
        };
        
        // Serialize and compress
        const jsonString = JSON.stringify(data, null, 2);
        const compressed = this._compress(jsonString);
        
        // Encrypt
        let finalData;
        if (password) {
            finalData = await this._encryptWithPassword(compressed, password);
        } else if (this.encryptionKey) {
            finalData = await this._encrypt(compressed);
        } else {
            finalData = this._stringToBuffer(compressed);
        }
        
        // Generate output
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = outputPath || `gauranga_backup_${timestamp}.gmem`;
        
        // Create blob
        const header = this._createExportHeader(!!password || !!this.encryptionKey);
        const checksum = await this._calculateChecksum(typeof finalData === 'string' ? finalData : this._arrayBufferToBase64(finalData));
        
        const blob = new Blob([
            header,
            checksum + '\n',
            typeof finalData === 'string' 
                ? btoa(finalData) 
                : this._arrayBufferToBase64(finalData)
        ], { type: 'application/octet-stream' });
        
        // Store export history
        await this._addExportHistory(filename, data.metadata);
        
        console.log('✅ Export completed:', filename);
        
        return {
            blob,
            filename,
            metadata: data.metadata,
            download: () => {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                URL.revokeObjectURL(url);
            }
        };
    }
    
    _createExportHeader(encrypted) {
        const version = 1;
        const compressed = 1;
        return `GAURANGA_MEM\x00${String.fromCharCode(version)}${encrypted ? '\x01' : '\x00'}${compressed ? '\x01' : '\x00'}`;
    }
    
    _createExportMetadata(includeSensitive) {
        return {
            version: this.version,
            agentName: 'GAURANGA',
            owner: this.owner,
            exportDate: new Date().toISOString(),
            deviceId: this.deviceId,
            totalMemories: 0,
            totalConversations: 0,
            totalPreferences: 0,
            encrypted: true,
            checksum: ''
        };
    }
    
    async _exportMemories(includeSensitive) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['memories'], 'readonly');
            const store = transaction.objectStore('memories');
            const results = [];
            
            const request = store.openCursor();
            
            request.onsuccess = (event) => {
                const cursor = event.target.result;
                
                if (cursor) {
                    const memory = cursor.value;
                    if (includeSensitive || memory.type !== MemoryType.SENSITIVE) {
                        results.push(memory);
                    }
                    cursor.continue();
                } else {
                    resolve(results);
                }
            };
            
            request.onerror = () => reject(request.error);
        });
    }
    
    async _exportConversations() {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['conversations'], 'readonly');
            const store = transaction.objectStore('conversations');
            const results = [];
            
            const request = store.openCursor();
            
            request.onsuccess = (event) => {
                const cursor = event.target.result;
                
                if (cursor) {
                    results.push(cursor.value);
                    cursor.continue();
                } else {
                    resolve(results);
                }
            };
            
            request.onerror = () => reject(request.error);
        });
    }
    
    async _exportPreferences() {
        return this.getAllPreferences();
    }
    
    async _encryptWithPassword(data, password) {
        const salt = crypto.getRandomValues(new Uint8Array(32));
        const keyMaterial = await crypto.subtle.importKey(
            'raw',
            this._stringToBuffer(password),
            'PBKDF2',
            false,
            ['deriveKey']
        );
        
        const key = await crypto.subtle.deriveKey(
            { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
            keyMaterial,
            { name: 'AES-GCM', length: 256 },
            false,
            ['encrypt', 'decrypt']
        );
        
        const iv = crypto.getRandomValues(new Uint8Array(12));
        const encoded = this._stringToBuffer(data);
        const encrypted = await crypto.subtle.encrypt(
            { name: 'AES-GCM', iv },
            key,
            encoded
        );
        
        // Combine salt + iv + encrypted
        const combined = new Uint8Array(salt.length + iv.length + encrypted.byteLength);
        combined.set(salt);
        combined.set(iv, salt.length);
        combined.set(new Uint8Array(encrypted), salt.length + iv.length);
        
        return combined;
    }
    
    async _decryptWithPassword(encryptedData, password) {
        const data = encryptedData instanceof Uint8Array 
            ? encryptedData 
            : this._base64ToBuffer(encryptedData);
        
        const salt = data.slice(0, 32);
        const iv = data.slice(32, 44);
        const encrypted = data.slice(44);
        
        const keyMaterial = await crypto.subtle.importKey(
            'raw',
            this._stringToBuffer(password),
            'PBKDF2',
            false,
            ['deriveKey']
        );
        
        const key = await crypto.subtle.deriveKey(
            { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
            keyMaterial,
            { name: 'AES-GCM', length: 256 },
            false,
            ['decrypt']
        );
        
        const decrypted = await crypto.subtle.decrypt(
            { name: 'AES-GCM', iv },
            key,
            encrypted
        );
        
        return this._bufferToString(decrypted);
    }
    
    async _calculateChecksum(data) {
        const encoded = this._stringToBuffer(String(data));
        const hashBuffer = await crypto.subtle.digest('SHA-256', encoded);
        return this._arrayBufferToHex(hashBuffer);
    }
    
    _compress(data) {
        // Simple compression using pako-like approach
        try {
            // Use native compression if available
            const encoded = new TextEncoder().encode(data);
            // Return as base64 for simplicity
            return this._arrayBufferToBase64(encoded);
        } catch {
            return data;
        }
    }
    
    _decompress(data) {
        try {
            const decoded = this._base64ToBuffer(data);
            return new TextDecoder().decode(decoded);
        } catch {
            return data;
        }
    }
    
    async _addExportHistory(filename, metadata) {
        return new Promise((resolve) => {
            const transaction = this.db.transaction(['export_history'], 'readwrite');
            const store = transaction.objectStore('export_history');
            
            store.add({
                timestamp: new Date().toISOString(),
                filename,
                totalMemories: metadata.totalMemories,
                encrypted: metadata.encrypted
            });
            
            transaction.oncomplete = resolve;
        });
    }
    
    /**
     * IMPORT DATA MEMORI - ON COMMAND ONLY
     */
    async importData(file, { password = null, merge = true } = {}) {
        console.log('📥 Starting memory import...');
        
        // Read file
        const text = await file.text();
        const lines = text.split('\n');
        const header = lines[0];
        const checksum = lines[1];
        const data = lines.slice(2).join('');
        
        // Decode data
        let encryptedData;
        try {
            encryptedData = atob(data);
        } catch {
            throw new Error('Invalid file format');
        }
        
        // Verify checksum
        const calculatedChecksum = await this._calculateChecksum(encryptedData);
        if (calculatedChecksum !== checksum) {
            throw new Error('Data integrity check failed!');
        }
        
        // Decrypt
        let jsonData;
        if (password) {
            jsonData = await this._decryptWithPassword(encryptedData, password);
        } else if (this.encryptionKey) {
            const decrypted = await this._decrypt(encryptedData);
            jsonData = typeof decrypted === 'string' ? decrypted : this._bufferToString(decrypted);
        } else {
            jsonData = encryptedData;
        }
        
        // Decompress and parse
        let parsed;
        try {
            parsed = JSON.parse(jsonData);
        } catch {
            // Try decompressing first
            const decompressed = this._decompress(jsonData);
            parsed = JSON.parse(decompressed);
        }
        
        // Import data
        const stats = {
            memoriesImported: 0,
            conversationsImported: 0,
            preferencesImported: 0,
            errors: []
        };
        
        if (!merge) {
            await this._clearAllData();
        }
        
        // Import memories
        for (const memory of (parsed.memories || [])) {
            try {
                await this._importMemory(memory);
                stats.memoriesImported++;
            } catch (e) {
                stats.errors.push(`Memory ${memory.id}: ${e.message}`);
            }
        }
        
        // Import conversations
        for (const conv of (parsed.conversations || [])) {
            try {
                await this._importConversation(conv);
                stats.conversationsImported++;
            } catch (e) {
                stats.errors.push(`Conversation ${conv.id}: ${e.message}`);
            }
        }
        
        // Import preferences
        for (const [key, value] of Object.entries(parsed.preferences || {})) {
            try {
                await this.setPreference(key, value);
                stats.preferencesImported++;
            } catch (e) {
                stats.errors.push(`Preference ${key}: ${e.message}`);
            }
        }
        
        console.log('✅ Import completed:', stats);
        this._emit('dataImported', stats);
        
        return stats;
    }
    
    async _importMemory(memory) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['memories'], 'readwrite');
            const store = transaction.objectStore('memories');
            
            // Check if exists
            const getRequest = store.get(memory.id);
            getRequest.onsuccess = () => {
                if (!getRequest.result) {
                    const addRequest = store.add({
                        ...memory,
                        source: 'import',
                        updatedAt: new Date().toISOString()
                    });
                    addRequest.onsuccess = resolve;
                    addRequest.onerror = () => reject(addRequest.error);
                } else {
                    resolve();
                }
            };
        });
    }
    
    async _importConversation(conv) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['conversations'], 'readwrite');
            const store = transaction.objectStore('conversations');
            
            const getRequest = store.get(conv.id);
            getRequest.onsuccess = () => {
                if (!getRequest.result) {
                    const addRequest = store.add({
                        ...conv,
                        sessionId: conv.sessionId || 'imported'
                    });
                    addRequest.onsuccess = resolve;
                    addRequest.onerror = () => reject(addRequest.error);
                } else {
                    resolve();
                }
            };
        });
    }
    
    async _clearAllData() {
        const stores = ['memories', 'conversations', 'preferences', 'sessions'];
        
        for (const storeName of stores) {
            await new Promise((resolve) => {
                const transaction = this.db.transaction([storeName], 'readwrite');
                const store = transaction.objectStore(storeName);
                store.clear();
                transaction.oncomplete = resolve;
            });
        }
        
        console.log('🗑️ All data cleared');
    }
    
    // ==========================================
    // UTILITY METHODS
    // ==========================================
    
    async countMemories() {
        return this._count('memories');
    }
    
    async countConversations() {
        return this._count('conversations');
    }
    
    async countPreferences() {
        return this._count('preferences');
    }
    
    _count(storeName) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.count();
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }
    
    async getStorageInfo() {
        const memories = await this.countMemories();
        const conversations = await this.countConversations();
        const preferences = await this.countPreferences();
        
        return {
            storagePath: this.storagePath,
            deviceId: this.deviceId,
            totalMemories: memories,
            totalConversations: conversations,
            totalPreferences: preferences,
            encryptionEnabled: !!this.encryptionKey,
            version: this.version
        };
    }
    
    async cleanupOldConversations(days = 30) {
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - days);
        const cutoffStr = cutoff.toISOString();
        
        return new Promise((resolve) => {
            const transaction = this.db.transaction(['conversations'], 'readwrite');
            const store = transaction.objectStore('conversations');
            let deleted = 0;
            
            const request = store.openCursor();
            
            request.onsuccess = (event) => {
                const cursor = event.target.result;
                
                if (cursor) {
                    if (cursor.value.timestamp < cutoffStr) {
                        cursor.delete();
                        deleted++;
                    }
                    cursor.continue();
                } else {
                    console.log(`🗑️ Deleted ${deleted} old conversations`);
                    resolve(deleted);
                }
            };
        });
    }
    
    // ==========================================
    // EVENT SYSTEM
    // ==========================================
    
    on(event, callback) {
        if (!this._listeners[event]) {
            this._listeners[event] = [];
        }
        this._listeners[event].push(callback);
    }
    
    off(event, callback) {
        if (this._listeners[event]) {
            this._listeners[event] = this._listeners[event].filter(cb => cb !== callback);
        }
    }
    
    _emit(event, data) {
        if (this._listeners[event]) {
            this._listeners[event].forEach(cb => cb(data));
        }
    }
    
    // ==========================================
    // HELPER METHODS
    // ==========================================
    
    _generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    _stringToBuffer(str) {
        return new TextEncoder().encode(str);
    }
    
    _bufferToString(buffer) {
        return new TextDecoder().decode(buffer);
    }
    
    _arrayBufferToBase64(buffer) {
        const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }
    
    _base64ToBuffer(base64) {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes;
    }
    
    _arrayBufferToHex(buffer) {
        const bytes = new Uint8Array(buffer);
        return Array.from(bytes)
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }
}

// ==========================================
// GAURANGA MEMORY COMMANDS
// ==========================================

/**
 * Voice/Text Commands for Memory Management
 */
const MemoryCommands = {
    // Command keywords
    EXPORT_KEYWORDS: ['ekspor', 'export', 'backup', 'simpan', 'pindahkan', 'transfer'],
    IMPORT_KEYWORDS: ['impor', 'import', 'restore', 'pulihkan', 'masukkan'],
    
    /**
     * Check if input contains export command
     */
    isExportCommand(input) {
        const text = input.toLowerCase();
        return this.EXPORT_KEYWORDS.some(k => text.includes(k)) &&
               (text.includes('memori') || text.includes('memory') || 
                text.includes('data') || text.includes('backup'));
    },
    
    /**
     * Check if input contains import command
     */
    isImportCommand(input) {
        const text = input.toLowerCase();
        return this.IMPORT_KEYWORDS.some(k => text.includes(k)) &&
               (text.includes('memori') || text.includes('memory') || 
                text.includes('data') || text.includes('backup'));
    },
    
    /**
     * Parse export parameters from command
     */
    parseExportCommand(input) {
        const params = {
            includeSensitive: !input.toLowerCase().includes('tanpa sensitif'),
            hasPassword: input.toLowerCase().includes('password') || 
                         input.toLowerCase().includes('kata sandi')
        };
        return params;
    },
    
    /**
     * Parse import parameters from command
     */
    parseImportCommand(input) {
        return {
            merge: !input.toLowerCase().includes('ganti') && 
                   !input.toLowerCase().includes('replace'),
            hasPassword: input.toLowerCase().includes('password') || 
                         input.toLowerCase().includes('kata sandi')
        };
    }
};

// ==========================================
// EXPORT INSTANCE
// ==========================================

// Create global instance
window.GaurangaMemoryManager = LocalMemoryManager;
window.MemoryCommands = MemoryCommands;
window.MemoryType = MemoryType;
window.MemoryPriority = MemoryPriority;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    window.gaurangaMemory = new LocalMemoryManager({
        owner: 'I Made Purna Ananda'
    });
    await window.gaurangaMemory.initialize();
    console.log('✅ GAURANGA Local Memory initialized and ready');
});
