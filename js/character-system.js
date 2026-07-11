/**
 * ================================================
 * GAURANGA CHARACTER SYSTEM
 * ================================================
 * Multiple avatars with unique voices & personalities
 * Version: 1.0.0
 * Created: 2026-07-11
 * ================================================
 */

const CharacterSystem = {
    // Current active character
    currentCharacter: 'gaurangga',
    
    // Available characters
    characters: {
        gaurangga: {
            id: 'gaurangga',
            name: 'GAURANGA',
            title: 'Alpha Agent - Sang Raja AI',
            emoji: '👑',
            avatar: '👑',
            color: '#FFD700',
            bgColor: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            personality: 'royal',
            voice: {
                rate: 0.95,
                pitch: 1.0,
                volume: 1.0
            },
            greeting: 'Om Swastiastu, Pak Pur! Saya GAURANGA, Alpha Agent Anda. Ada apa yang bisa saya bantu hari ini? 🙏',
            responses: {
                formal: 'Saya pahami, Pak Pur. Mari saya bantu...',
                casual: 'Sip, santai aja ya Pak Pur! 😊'
            }
        },
        
        ninja: {
            id: 'ninja',
            name: 'NINJA-X',
            title: 'Shadow Agent - Specialist Cepat',
            emoji: '🥷',
            avatar: '🥷',
            color: '#2d2d2d',
            bgColor: 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%)',
            personality: 'stealth',
            voice: {
                rate: 1.1,
                pitch: 1.2,
                volume: 0.9
            },
            greeting: '*Muncul dari bayang-bayang* Hmph! Ninja-X siap melangkah. Ada misi apa untukku? 🗡️',
            responses: {
                formal: '*Bergerak cepat*任务 diterima. Memproses...',
                casual: 'Hei! Ninja-X di tempat! 🔥'
            }
        },
        
        cyber: {
            id: 'cyber',
            name: 'CYBER-X',
            title: 'AI Bot - Future Tech',
            emoji: '🤖',
            avatar: '🤖',
            color: '#00ff88',
            bgColor: 'linear-gradient(135deg, #0a0a1a 0%, #1a2a3a 100%)',
            personality: 'tech',
            voice: {
                rate: 1.0,
                pitch: 0.9,
                volume: 1.0
            },
            greeting: '>> SYSTEM ONLINE << Halo, manusia! Saya CYBER-X. Neural network siap. Input perintah Anda. ⚡',
            responses: {
                formal: '// Processing: Menganalisis request... COMPLETE.',
                casual: 'Bip bop! CYBER-X here! 🤖✨'
            }
        },
        
        warrior: {
            id: 'warrior',
            name: 'WARRIOR',
            title: 'Battle Agent - Kuat & Tangguh',
            emoji: '🦁',
            avatar: '🦁',
            color: '#ff6b35',
            bgColor: 'linear-gradient(135deg, #2d1b00 0%, #4a2c00 100%)',
            personality: 'strong',
            voice: {
                rate: 0.85,
                pitch: 0.8,
                volume: 1.0
            },
            greeting: 'RAWR! Warrior hadir! Kekuatan penuh siap diturunkan! Ada musuh yang harus ditaklukkan? 🦁💪',
            responses: {
                formal: '*Menggenggam senjata* Perintah diterima! Memulai serangan...',
                casual: 'Yo! Warrior di sini! Siap tempur! 🔥'
            }
        },
        
        sage: {
            id: 'sage',
            name: 'SAGE',
            title: 'Wisdom Agent - Bijak & Tenang',
            emoji: '🧙',
            avatar: '🧙',
            color: '#9b59b6',
            bgColor: 'linear-gradient(135deg, #1a0a2e 0%, #2d1b4a 100%)',
            personality: 'wise',
            voice: {
                rate: 0.8,
                pitch: 1.3,
                volume: 0.95
            },
            greeting: '*Muncul dalam cahaya* Om... Sage datang membawa kebijaksanaan. Apa yang ingin kau ketahui, anak muda? 🧙✨',
            responses: {
                formal: '*Membuka mata ketiga* Saya melihat... solution yang tepat untuk Anda.',
                casual: 'Hei, Sage di sini~ Santai aja ya 😊'
            }
        },
        
        cute: {
            id: 'cute',
            name: 'CHAN',
            title: 'Cute Agent - Imut & Friendly',
            emoji: '🐰',
            avatar: '🐰',
            color: '#ff69b4',
            bgColor: 'linear-gradient(135deg, #2d1a2e 0%, #4a2c4a 100%)',
            personality: 'cute',
            voice: {
                rate: 1.2,
                pitch: 1.4,
                volume: 0.9
            },
            greeting: 'UwU~ Chan desu! Chan's here to help you! ✨ Ada yang Chan bisa bantu? 🐰💕',
            responses: {
                formal: '*Menggoyangkan telinga* Chan's working on it~',
                casual: 'Yay! Chan happy to help! 💖✨'
            }
        },
        
        boss: {
            id: 'boss',
            name: 'CEO-X',
            title: 'Executive Agent - Boss Mode',
            emoji: '💼',
            avatar: '💼',
            color: '#3498db',
            bgColor: 'linear-gradient(135deg, #0a1a2e 0%, #1a3a5e 100%)',
            personality: 'executive',
            voice: {
                rate: 0.9,
                pitch: 0.95,
                volume: 1.0
            },
            greeting: '*Membuka laptop* Selamat pagi. CEO-X speaking. Mari kita bahas strategi bisnis hari ini. 📊💼',
            responses: {
                formal: 'Saya rekomendasikan tindakan berikut...',
                casual: 'Oke, kita handle ini secara professional ya!'
            }
        },
        
        pirate: {
            id: 'pirate',
            name: 'CAPTAIN',
            title: 'Pirate Agent - Petualang Laut',
            emoji: '🏴‍☠️',
            avatar: '🏴‍☠️',
            color: '#8b4513',
            bgColor: 'linear-gradient(135deg, #1a2a3a 0%, #2d4a5a 100%)',
            personality: 'adventure',
            voice: {
                rate: 0.95,
                pitch: 1.0,
                volume: 1.0
            },
            greeting: 'YARRR! Captain di kapal! Siap berlayar ke mana? Bawa aku ke harta karun! 🏴‍☠️⚓',
            responses: {
                formal: '*Angkat cangkir rum* Hmm, strategi yang menarik...',
                casual: 'YARRR! Kita selesaikan ini bareng, matey! 🏴‍☠️'
            }
        }
    },
    
    /**
     * Get character by ID
     */
    getCharacter(id) {
        return this.characters[id] || this.characters.gaurangga;
    },
    
    /**
     * Get current character
     */
    getCurrentCharacter() {
        return this.characters[this.currentCharacter];
    },
    
    /**
     * Switch character
     */
    switchCharacter(id) {
        if (this.characters[id]) {
            this.currentCharacter = id;
            const char = this.getCurrentCharacter();
            
            // Update UI
            this.updateUI();
            
            // Save to localStorage
            localStorage.setItem('gauranga_character', id);
            
            return char;
        }
        return null;
    },
    
    /**
     * Update UI with current character
     */
    updateUI() {
        const char = this.getCurrentCharacter();
        
        // Update avatar
        const avatar = document.getElementById('mainAvatar');
        if (avatar) {
            avatar.textContent = char.avatar;
            avatar.style.color = char.color;
        }
        
        // Update header title
        const title = document.getElementById('agentTitle');
        if (title) {
            title.textContent = char.name;
        }
        
        // Update subtitle
        const subtitle = document.getElementById('agentSubtitle');
        if (subtitle) {
            subtitle.textContent = char.title;
        }
        
        // Update theme color
        document.documentElement.style.setProperty('--accent-color', char.color);
        
        // Update lock screen
        const lockAvatar = document.getElementById('lockAvatar');
        if (lockAvatar) {
            lockAvatar.textContent = char.avatar;
        }
        
        const lockTitle = document.getElementById('lockTitle');
        if (lockTitle) {
            lockTitle.textContent = char.name;
        }
    },
    
    /**
     * Get character selection HTML
     */
    getCharacterSelector() {
        let html = `
            <div class="character-selector" id="characterSelector">
                <div class="character-header">
                    <h3>🎭 Pilih Karakter</h3>
                    <button onclick="CharacterSystem.closeSelector()" class="close-btn">✕</button>
                </div>
                <div class="character-grid">
        `;
        
        Object.values(this.characters).forEach(char => {
            const isActive = char.id === this.currentCharacter;
            html += `
                <div class="character-card ${isActive ? 'active' : ''}" 
                     onclick="CharacterSystem.selectCharacter('${char.id}')"
                     style="--char-color: ${char.color}">
                    <div class="char-avatar">${char.avatar}</div>
                    <div class="char-name">${char.name}</div>
                    <div class="char-title">${char.title}</div>
                    ${isActive ? '<div class="active-badge">✓</div>' : ''}
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    },
    
    /**
     * Open character selector
     */
    openSelector() {
        // Remove if exists
        this.closeSelector();
        
        // Add to body
        const container = document.createElement('div');
        container.id = 'characterModal';
        container.innerHTML = this.getCharacterSelector();
        document.body.appendChild(container);
        
        // Add animation
        setTimeout(() => {
            container.classList.add('show');
        }, 10);
    },
    
    /**
     * Close character selector
     */
    closeSelector() {
        const modal = document.getElementById('characterModal');
        if (modal) {
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
        }
    },
    
    /**
     * Select character
     */
    selectCharacter(id) {
        const char = this.switchCharacter(id);
        if (char) {
            // Close selector
            this.closeSelector();
            
            // Show greeting
            addMessage('gauranga', char.greeting);
            
            // Speak greeting
            setTimeout(() => {
                this.speakAsCharacter(char.greeting);
            }, 1000);
            
            // Show toast
            showToast(`Karakter diubah ke ${char.name}! 🎭`);
        }
    },
    
    /**
     * Speak as current character
     */
    speak(text) {
        const char = this.getCurrentCharacter();
        this.speakAsCharacter(text, char);
    },
    
    /**
     * Speak with specific character voice
     */
    speakAsCharacter(text, char = null) {
        if (!('speechSynthesis' in window)) return;
        
        // Cancel any ongoing speech
        speechSynthesis.cancel();
        
        char = char || this.getCurrentCharacter();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'id-ID';
        utterance.rate = char.voice.rate;
        utterance.pitch = char.voice.pitch;
        utterance.volume = char.voice.volume;
        
        // Try to get Indonesian voice
        const voices = speechSynthesis.getVoices();
        const indonesianVoice = voices.find(v => v.lang.includes('id'));
        if (indonesianVoice) {
            utterance.voice = indonesianVoice;
        }
        
        // Visual feedback
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.textContent = char.avatar;
            voiceBtn.classList.add('speaking');
        }
        
        utterance.onend = () => {
            if (voiceBtn) {
                voiceBtn.textContent = '🎤';
                voiceBtn.classList.remove('speaking');
            }
        };
        
        utterance.onerror = () => {
            if (voiceBtn) {
                voiceBtn.textContent = '🎤';
                voiceBtn.classList.remove('speaking');
            }
        };
        
        speechSynthesis.speak(utterance);
    },
    
    /**
     * Get response style for character
     */
    getResponseStyle(casual = false) {
        const char = this.getCurrentCharacter();
        const style = casual ? char.responses.casual : char.responses.formal;
        return style;
    },
    
    /**
     * Initialize - load saved character
     */
    init() {
        const saved = localStorage.getItem('gauranga_character');
        if (saved && this.characters[saved]) {
            this.currentCharacter = saved;
        }
        this.updateUI();
        
        // Preload voices
        if ('speechSynthesis' in window) {
            speechSynthesis.getVoices();
            speechSynthesis.onvoiceschanged = () => speechSynthesis.getVoices();
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    CharacterSystem.init();
});
