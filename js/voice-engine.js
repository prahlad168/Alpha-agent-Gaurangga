/**
 * GAURANGA VOICE ENGINE v2.0
 * Advanced Voice Interface for Alpha Gaurangga
 * 
 * Features:
 * - Wake Word Detection
 * - Voice Input with Web Speech API
 * - Text-to-Speech with multiple voice options
 * - Audio visualizer
 * - Continuous listening mode
 */

class GaurangaVoiceEngine {
    constructor() {
        // State
        this.isListening = false;
        this.isSpeaking = false;
        this.isHotwordActive = false;
        this.recognition = null;
        this.hotwordRecognition = null;
        this.audioContext = null;
        this.analyser = null;
        
        // Config
        this.config = {
            language: 'id-ID',
            continuous: false,
            interimResults: true,
            wakeWords: ['hey gauranga', 'gauranga', 'ei gauranga', 'halo gauranga', 'ok gauranga'],
            ttsRate: 1.0,
            ttsPitch: 1.0,
            ttsVolume: 1.0
        };
        
        // Callbacks
        this.onTranscript = null;
        this.onWakeWord = null;
        this.onListeningStart = null;
        this.onListeningEnd = null;
        this.onSpeakingStart = null;
        this.onSpeakingEnd = null;
        this.onError = null;
        
        this.init();
    }
    
    init() {
        this.checkBrowserSupport();
        this.setupSpeechRecognition();
        this.setupAudioContext();
    }
    
    checkBrowserSupport() {
        const speechRecognition = 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
        const speechSynthesis = 'speechSynthesis' in window;
        
        if (!speechRecognition) {
            console.warn('Speech Recognition not supported');
            this.onError?.('Speech Recognition not supported in this browser');
        }
        
        if (!speechSynthesis) {
            console.warn('Speech Synthesis not supported');
            this.onError?.('Speech Synthesis not supported in this browser');
        }
        
        return speechRecognition && speechSynthesis;
    }
    
    setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return;
        
        this.recognition = new SpeechRecognition();
        this.recognition.lang = this.config.language;
        this.recognition.continuous = this.config.continuous;
        this.recognition.interimResults = this.config.interimResults;
        this.recognition.maxAlternatives = 1;
        
        this.recognition.onstart = () => {
            this.isListening = true;
            this.onListeningStart?.();
            this.updateUI('listening');
            this.showVoiceMode('listening');
        };
        
        this.recognition.onresult = (event) => {
            const results = Array.from(event.results);
            const transcript = results.map(r => r[0].transcript).join('');
            const isFinal = event.results[event.results.length - 1].isFinal;
            
            // Update interim transcript
            this.onTranscript?.(transcript, isFinal);
            this.updateTranscriptUI(transcript);
            
            if (!isFinal) {
                this.showVoiceMode('processing');
            }
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.onError?.(event.error);
            this.stopListening();
        };
        
        this.recognition.onend = () => {
            if (this.isListening) {
                // Restart recognition if still in listening mode
                try {
                    this.recognition.start();
                } catch (e) {
                    this.stopListening();
                }
            } else {
                this.showVoiceMode(null);
            }
        };
    }
    
    setupAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
        } catch (e) {
            console.warn('Audio context not available');
        }
    }
    
    setupHotwordDetection() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return;
        
        this.hotwordRecognition = new SpeechRecognition();
        this.hotwordRecognition.lang = this.config.language;
        this.hotwordRecognition.continuous = true;
        this.hotwordRecognition.interimResults = false;
        
        this.hotwordRecognition.onresult = (event) => {
            const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
            
            // Check for wake words
            for (const wakeWord of this.config.wakeWords) {
                if (transcript.includes(wakeWord)) {
                    this.onWakeWord?.(wakeWord);
                    this.activateGauranga();
                    break;
                }
            }
        };
        
        this.hotwordRecognition.onerror = (event) => {
            if (event.error !== 'no-speech') {
                console.error('Hotword detection error:', event.error);
            }
        };
        
        this.hotwordRecognition.onend = () => {
            // Restart hotword detection if active
            if (this.isHotwordActive) {
                try {
                    this.hotwordRecognition.start();
                } catch (e) {
                    console.warn('Could not restart hotword detection');
                }
            }
        };
    }
    
    // ========================================
    // PUBLIC METHODS
    // ========================================
    
    startListening() {
        if (!this.recognition) {
            this.onError?.('Speech recognition not available');
            return false;
        }
        
        if (this.isListening) return true;
        
        try {
            this.recognition.start();
            return true;
        } catch (e) {
            console.error('Failed to start recognition:', e);
            return false;
        }
    }
    
    stopListening() {
        this.isListening = false;
        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (e) {
                console.warn('Recognition already stopped');
            }
        }
        this.onListeningEnd?.();
        this.updateUI('idle');
    }
    
    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }
    
    startHotwordDetection() {
        if (!this.hotwordRecognition) {
            this.setupHotwordDetection();
        }
        
        this.isHotwordActive = true;
        try {
            this.hotwordRecognition.start();
            this.updateHotwordUI(true);
        } catch (e) {
            console.warn('Hotword detection already running');
        }
    }
    
    stopHotwordDetection() {
        this.isHotwordActive = false;
        if (this.hotwordRecognition) {
            try {
                this.hotwordRecognition.stop();
            } catch (e) {
                console.warn('Hotword recognition already stopped');
            }
        }
        this.updateHotwordUI(false);
    }
    
    // Text-to-Speech
    speak(text, options = {}) {
        if (!('speechSynthesis' in window)) {
            this.onError?.('Speech synthesis not available');
            return;
        }
        
        // Cancel any ongoing speech
        speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = options.lang || 'id-ID';
        utterance.rate = options.rate || this.config.ttsRate;
        utterance.pitch = options.pitch || this.config.ttsPitch;
        utterance.volume = options.volume || this.config.ttsVolume;
        
        // Try to get Indonesian voice
        const voices = speechSynthesis.getVoices();
        const indonesianVoice = voices.find(v => v.lang.includes('id'));
        if (indonesianVoice) {
            utterance.voice = indonesianVoice;
        }
        
        utterance.onstart = () => {
            this.isSpeaking = true;
            this.onSpeakingStart?.();
            this.updateSpeakingUI(true);
            this.showVoiceMode('speaking');
        };
        
        utterance.onend = () => {
            this.isSpeaking = false;
            this.onSpeakingEnd?.();
            this.updateSpeakingUI(false);
            this.showVoiceMode(null);
        };
        
        utterance.onerror = (event) => {
            console.error('TTS error:', event.error);
            this.isSpeaking = false;
            this.onSpeakingEnd?.();
            this.updateSpeakingUI(false);
            this.showVoiceMode(null);
        };
        
        speechSynthesis.speak(utterance);
    }
    
    stopSpeaking() {
        speechSynthesis.cancel();
        this.isSpeaking = false;
        this.onSpeakingEnd?.();
        this.updateSpeakingUI(false);
        this.showVoiceMode(null);
    }
    
    activateGauranga() {
        // Called when wake word is detected
        this.speak('Ya, saya di sini Pak Pur. Ada yang bisa saya bantu?');
        
        // Open voice input after speaking
        setTimeout(() => {
            this.startListening();
        }, 2000);
    }
    
    // ========================================
    // UI UPDATES
    // ========================================
    
    updateUI(state) {
        // Update voice button
        const voiceBtn = document.getElementById('voiceBtn');
        const voiceIcon = document.getElementById('voiceIcon');
        const voiceVisualizer = document.getElementById('voiceVisualizer');
        
        if (voiceBtn && voiceIcon) {
            if (state === 'listening') {
                voiceBtn.classList.add('active');
                voiceIcon.className = 'fas fa-stop';
            } else {
                voiceBtn.classList.remove('active');
                voiceIcon.className = 'fas fa-microphone';
            }
        }
        
        if (voiceVisualizer) {
            if (state === 'listening') {
                voiceVisualizer.classList.remove('hidden');
            } else {
                voiceVisualizer.classList.add('hidden');
            }
        }
    }
    
    updateHotwordUI(isActive) {
        const wakeIndicator = document.getElementById('wakeIndicator');
        const wakeText = document.getElementById('wakeText');
        
        if (wakeIndicator) {
            if (isActive) {
                wakeIndicator.classList.add('listening');
            } else {
                wakeIndicator.classList.remove('listening');
            }
        }
        
        if (wakeText) {
            wakeText.textContent = isActive ? 'Say "Hey GAURANGA"' : 'Hotword inactive';
        }
    }
    
    updateSpeakingUI(isSpeaking) {
        const wakeIndicator = document.getElementById('wakeIndicator');
        const wakeText = document.getElementById('wakeText');
        
        if (wakeIndicator) {
            if (isSpeaking) {
                wakeIndicator.classList.add('speaking');
                wakeIndicator.style.borderColor = '#00d4ff';
            } else {
                wakeIndicator.classList.remove('speaking');
                wakeIndicator.style.borderColor = '';
            }
        }
        
        if (wakeText) {
            wakeText.textContent = isSpeaking ? 'Speaking...' : 'Say "Hey GAURANGA"';
        }
    }
    
    updateTranscriptUI(transcript) {
        const voiceStatus = document.getElementById('voiceStatus');
        const voiceModeText = document.getElementById('voiceModeText');
        
        if (voiceStatus) {
            voiceStatus.textContent = `Mendengar: "${transcript.substring(0, 50)}${transcript.length > 50 ? '...' : ''}"`;
        }
        
        if (voiceModeText) {
            voiceModeText.textContent = `"${transcript.substring(0, 30)}${transcript.length > 30 ? '...' : ''}"`;
        }
        
        // Animate sound wave
        this.animateSoundWave(transcript.length);
    }
    
    animateSoundWave(intensity) {
        const soundBars = document.querySelectorAll('.sound-bar');
        soundBars.forEach((bar, i) => {
            const height = Math.min(30, 5 + (intensity % 20) + (i * 3));
            bar.style.height = height + 'px';
        });
    }
    
    showVoiceMode(mode) {
        const voiceMode = document.getElementById('voiceMode');
        const voiceModeText = document.getElementById('voiceModeText');
        
        if (voiceMode) {
            if (mode === 'listening') {
                voiceMode.classList.remove('hidden');
                if (voiceModeText) voiceModeText.textContent = 'Mendengarkan...';
                this.animateSoundWave(50);
            } else if (mode === 'processing') {
                if (voiceModeText) voiceModeText.textContent = 'Memproses...';
            } else if (mode === 'speaking') {
                if (voiceModeText) voiceModeText.textContent = 'Menjawab...';
                const voiceModeIcon = voiceMode.querySelector('.voice-mode-icon i');
                if (voiceModeIcon) voiceModeIcon.className = 'fas fa-comment-dots';
            } else {
                voiceMode.classList.add('hidden');
            }
        }
    }
    
    // ========================================
    // VISUALIZER
    // ========================================
    
    getAnalyserData() {
        if (!this.analyser) return null;
        const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
        this.analyser.getByteFrequencyData(dataArray);
        return dataArray;
    }
}

// ========================================
// HELPER FUNCTIONS (Global)
// ========================================

// Initialize voice engine
let gaurangaVoice = null;

function initVoiceEngine() {
    gaurangaVoice = new GaurangaVoiceEngine();
    
    // Setup callbacks
    gaurangaVoice.onTranscript = (transcript, isFinal) => {
        if (isFinal) {
            // Update chat input with final transcript
            const chatInput = document.getElementById('chatInput');
            if (chatInput) {
                chatInput.value = transcript;
            }
        }
    };
    
    gaurangaVoice.onListeningStart = () => {
        console.log('Voice listening started');
    };
    
    gaurangaVoice.onListeningEnd = () => {
        console.log('Voice listening ended');
        // Check if there's text to send
        const chatInput = document.getElementById('chatInput');
        if (chatInput && chatInput.value.trim()) {
            sendMessage();
        }
    };
    
    gaurangaVoice.onWakeWord = (word) => {
        console.log('Wake word detected:', word);
        showNotification('🎤 "Hey GAURANGA" - Saya siap, Pak Pur!');
    };
    
    gaurangaVoice.onSpeakingStart = () => {
        console.log('Speaking started');
    };
    
    gaurangaVoice.onSpeakingEnd = () => {
        console.log('Speaking ended');
    };
    
    gaurangaVoice.onError = (error) => {
        console.error('Voice error:', error);
        showNotification('⚠️ Voice error: ' + error);
    };
    
    return gaurangaVoice;
}

// Toggle voice input
function toggleVoice() {
    if (!gaurangaVoice) {
        initVoiceEngine();
    }
    gaurangaVoice.toggleListening();
}

// Start voice input
function startVoiceInput() {
    if (!gaurangaVoice) {
        initVoiceEngine();
    }
    gaurangaVoice.startListening();
}

// Stop voice input
function stopVoiceInput() {
    if (gaurangaVoice) {
        gaurangaVoice.stopListening();
    }
}

// Speak text
function speak(text) {
    if (!gaurangaVoice) {
        initVoiceEngine();
    }
    gaurangaVoice.speak(text);
}

// Start hotword detection
function startHotwordDetection() {
    if (!gaurangaVoice) {
        initVoiceEngine();
    }
    gaurangaVoice.startHotwordDetection();
}

// Stop hotword detection
function stopHotwordDetection() {
    if (gaurangaVoice) {
        gaurangaVoice.stopHotwordDetection();
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Voice engine will be initialized after boot sequence
    setTimeout(() => {
        initVoiceEngine();
        startHotwordDetection();
    }, 3500);
});

// Export for global access
window.GaurangaVoiceEngine = GaurangaVoiceEngine;
window.gaurangaVoice = gaurangaVoice;
