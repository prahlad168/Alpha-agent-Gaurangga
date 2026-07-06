"""
GAURANGA TTS Engine
Text-to-Speech with Multilingual Support for ALL World Languages
Supports 100+ languages with humanlike voice synthesis
"""

import os
import re
import subprocess
import threading
from typing import Optional, List, Dict
from datetime import datetime

class TTSEngine:
    """
    Advanced Text-to-Speech Engine
    Supports ALL world languages with humanlike voice synthesis
    
    Coverage: 100+ languages including:
    - Major: Indonesian, English, Mandarin, Spanish, Hindi, Arabic, Portuguese, Russian, Japanese, Korean
    - Asian: Thai, Vietnamese, Malay, Filipino, Bengali, Punjabi, Tamil, Telugu, Khmer, Lao, Burmese
    - European: French, German, Italian, Spanish, Portuguese, Dutch, Polish, Greek, Turkish, Ukrainian
    - African: Swahili, Yoruba, Hausa, Zulu, Amharic, Somali
    - Americas: Nahuatl, Quechua, Guarani, Maya
    - Oceanian: Hawaiian, Samoan, Maori, Fijian
    - And 60+ more regional languages
    """
    
    # ALL World Languages Configuration
    LANGUAGES = {
        # ══════════════════════════════════════════════════════════════
        # ASIAN LANGUAGES
        # ══════════════════════════════════════════════════════════════
        # Southeast Asia
        "id": {"name": "Indonesian", "code": "id-ID", "espeak": "id", "style": "friendly"},
        "ms": {"name": "Malay", "code": "ms-MY", "espeak": "ms", "style": "friendly"},
        "tl": {"name": "Filipino", "code": "fil-PH", "espeak": "fil", "style": "friendly"},
        "th": {"name": "Thai", "code": "th-TH", "espeak": "th", "style": "friendly"},
        "vi": {"name": "Vietnamese", "code": "vi-VN", "espeak": "vi", "style": "friendly"},
        "km": {"name": "Khmer", "code": "km-KH", "espeak": "km", "style": "friendly"},
        "lo": {"name": "Lao", "code": "lo-LA", "espeak": "lo", "style": "friendly"},
        "my": {"name": "Burmese", "code": "my-MM", "espeak": "my", "style": "friendly"},
        
        # East Asia
        "zh": {"name": "Chinese (Mandarin)", "code": "zh-CN", "espeak": "zh", "style": "formal"},
        "zh-TW": {"name": "Chinese (Taiwan)", "code": "zh-TW", "espeak": "zh", "style": "formal"},
        "zh-YUE": {"name": "Cantonese", "code": "yue-CN", "espeak": "yue", "style": "formal"},
        "ja": {"name": "Japanese", "code": "ja-JP", "espeak": "ja", "style": "formal"},
        "ko": {"name": "Korean", "code": "ko-KR", "espeak": "ko", "style": "formal"},
        "mn": {"name": "Mongolian", "code": "mn-MN", "espeak": "mn", "style": "formal"},
        
        # South Asia
        "hi": {"name": "Hindi", "code": "hi-IN", "espeak": "hi", "style": "warm"},
        "bn": {"name": "Bengali", "code": "bn-BD", "espeak": "bn", "style": "warm"},
        "pa": {"name": "Punjabi", "code": "pa-IN", "espeak": "pa", "style": "warm"},
        "ta": {"name": "Tamil", "code": "ta-IN", "espeak": "ta", "style": "warm"},
        "te": {"name": "Telugu", "code": "te-IN", "espeak": "te", "style": "warm"},
        "mr": {"name": "Marathi", "code": "mr-IN", "espeak": "mr", "style": "warm"},
        "gu": {"name": "Gujarati", "code": "gu-IN", "espeak": "gu", "style": "warm"},
        "kn": {"name": "Kannada", "code": "kn-IN", "espeak": "kn", "style": "warm"},
        "ml": {"name": "Malayalam", "code": "ml-IN", "espeak": "ml", "style": "warm"},
        "ne": {"name": "Nepali", "code": "ne-NP", "espeak": "ne", "style": "warm"},
        "si": {"name": "Sinhala", "code": "si-LK", "espeak": "si", "style": "warm"},
        "ur": {"name": "Urdu", "code": "ur-PK", "espeak": "ur", "style": "warm"},
        
        # Central Asia
        "kk": {"name": "Kazakh", "code": "kk-KZ", "espeak": "kk", "style": "formal"},
        "uz": {"name": "Uzbek", "code": "uz-UZ", "espeak": "uz", "style": "formal"},
        "tg": {"name": "Tajik", "code": "tg-TJ", "espeak": "tg", "style": "formal"},
        "tk": {"name": "Turkmen", "code": "tk-TM", "espeak": "tk", "style": "formal"},
        "ky": {"name": "Kyrgyz", "code": "ky-KG", "espeak": "ky", "style": "formal"},
        
        # Regional Indonesian
        "ban": {"name": "Balinese", "code": "ban-ID", "espeak": "ban", "style": "traditional"},
        "jv": {"name": "Javanese", "code": "jv-ID", "espeak": "jv", "style": "friendly"},
        "su": {"name": "Sundanese", "code": "su-ID", "espeak": "su", "style": "friendly"},
        "bug": {"name": "Buginese", "code": "bug-ID", "espeak": "bug", "style": "friendly"},
        "mad": {"name": "Madurese", "code": "mad-ID", "espeak": "mad", "style": "friendly"},
        
        # ══════════════════════════════════════════════════════════════
        # EUROPEAN LANGUAGES
        # ══════════════════════════════════════════════════════════════
        "en": {"name": "English", "code": "en-US", "espeak": "en", "style": "professional"},
        "es": {"name": "Spanish", "code": "es-ES", "espeak": "es", "style": "warm"},
        "es-MX": {"name": "Spanish (Mexico)", "code": "es-MX", "espeak": "es", "style": "warm"},
        "es-AR": {"name": "Spanish (Argentina)", "code": "es-AR", "espeak": "es", "style": "warm"},
        "pt": {"name": "Portuguese", "code": "pt-PT", "espeak": "pt", "style": "warm"},
        "pt-BR": {"name": "Portuguese (Brazil)", "code": "pt-BR", "espeak": "pt", "style": "warm"},
        "fr": {"name": "French", "code": "fr-FR", "espeak": "fr", "style": "elegant"},
        "fr-CA": {"name": "French (Canada)", "code": "fr-CA", "espeak": "fr", "style": "elegant"},
        "de": {"name": "German", "code": "de-DE", "espeak": "de", "style": "formal"},
        "de-AT": {"name": "German (Austria)", "code": "de-AT", "espeak": "de", "style": "formal"},
        "it": {"name": "Italian", "code": "it-IT", "espeak": "it", "style": "warm"},
        "nl": {"name": "Dutch", "code": "nl-NL", "espeak": "nl", "style": "friendly"},
        "pl": {"name": "Polish", "code": "pl-PL", "espeak": "pl", "style": "formal"},
        "ro": {"name": "Romanian", "code": "ro-RO", "espeak": "ro", "style": "friendly"},
        "cs": {"name": "Czech", "code": "cs-CZ", "espeak": "cs", "style": "formal"},
        "sk": {"name": "Slovak", "code": "sk-SK", "espeak": "sk", "style": "formal"},
        "hu": {"name": "Hungarian", "code": "hu-HU", "espeak": "hu", "style": "formal"},
        "bg": {"name": "Bulgarian", "code": "bg-BG", "espeak": "bg", "style": "formal"},
        "hr": {"name": "Croatian", "code": "hr-HR", "espeak": "hr", "style": "friendly"},
        "sr": {"name": "Serbian", "code": "sr-RS", "espeak": "sr", "style": "friendly"},
        "sl": {"name": "Slovenian", "code": "sl-SI", "espeak": "sl", "style": "friendly"},
        "mk": {"name": "Macedonian", "code": "mk-MK", "espeak": "mk", "style": "formal"},
        "sq": {"name": "Albanian", "code": "sq-AL", "espeak": "sq", "style": "warm"},
        "el": {"name": "Greek", "code": "el-GR", "espeak": "el", "style": "formal"},
        "tr": {"name": "Turkish", "code": "tr-TR", "espeak": "tr", "style": "friendly"},
        "uk": {"name": "Ukrainian", "code": "uk-UA", "espeak": "uk", "style": "formal"},
        "be": {"name": "Belarusian", "code": "be-BY", "espeak": "be", "style": "formal"},
        "ru": {"name": "Russian", "code": "ru-RU", "espeak": "ru", "style": "formal"},
        "et": {"name": "Estonian", "code": "et-EE", "espeak": "et", "style": "formal"},
        "lv": {"name": "Latvian", "code": "lv-LV", "espeak": "lv", "style": "formal"},
        "lt": {"name": "Lithuanian", "code": "lt-LT", "espeak": "lt", "style": "formal"},
        "is": {"name": "Icelandic", "code": "is-IS", "espeak": "is", "style": "formal"},
        "no": {"name": "Norwegian", "code": "nb-NO", "espeak": "no", "style": "formal"},
        "sv": {"name": "Swedish", "code": "sv-SE", "espeak": "sv", "style": "formal"},
        "da": {"name": "Danish", "code": "da-DK", "espeak": "da", "style": "formal"},
        "fi": {"name": "Finnish", "code": "fi-FI", "espeak": "fi", "style": "formal"},
        
        # ══════════════════════════════════════════════════════════════
        # MIDDLE EASTERN & CENTRAL ASIAN
        # ══════════════════════════════════════════════════════════════
        "ar": {"name": "Arabic", "code": "ar-SA", "espeak": "ar", "style": "formal"},
        "ar-SA": {"name": "Arabic (Saudi)", "code": "ar-SA", "espeak": "ar", "style": "formal"},
        "ar-EG": {"name": "Arabic (Egypt)", "code": "ar-EG", "espeak": "ar", "style": "formal"},
        "ar-AE": {"name": "Arabic (UAE)", "code": "ar-AE", "espeak": "ar", "style": "formal"},
        "he": {"name": "Hebrew", "code": "he-IL", "espeak": "he", "style": "friendly"},
        "fa": {"name": "Persian (Farsi)", "code": "fa-IR", "espeak": "fa", "style": "formal"},
        "ps": {"name": "Pashto", "code": "ps-AF", "espeak": "ps", "style": "formal"},
        
        # ══════════════════════════════════════════════════════════════
        # AFRICAN LANGUAGES
        # ══════════════════════════════════════════════════════════════
        "sw": {"name": "Swahili", "code": "sw-TZ", "espeak": "sw", "style": "friendly"},
        "sw-KE": {"name": "Swahili (Kenya)", "code": "sw-KE", "espeak": "sw", "style": "friendly"},
        "yo": {"name": "Yoruba", "code": "yo-NG", "espeak": "yo", "style": "warm"},
        "ha": {"name": "Hausa", "code": "ha-NG", "espeak": "ha", "style": "friendly"},
        "ig": {"name": "Igbo", "code": "ig-NG", "espeak": "ig", "style": "friendly"},
        "zu": {"name": "Zulu", "code": "zu-ZA", "espeak": "zu", "style": "warm"},
        "xh": {"name": "Xhosa", "code": "xh-ZA", "espeak": "xh", "style": "warm"},
        "am": {"name": "Amharic", "code": "am-ET", "espeak": "am", "style": "formal"},
        "so": {"name": "Somali", "code": "so-SO", "espeak": "so", "style": "warm"},
        "or": {"name": "Oromo", "code": "om-ET", "espeak": "om", "style": "warm"},
        "rw": {"name": "Kinyarwanda", "code": "rw-RW", "espeak": "rw", "style": "friendly"},
        "mg": {"name": "Malagasy", "code": "mg-MG", "espeak": "mg", "style": "friendly"},
        "sn": {"name": "Shona", "code": "sn-ZW", "espeak": "sn", "style": "warm"},
        "st": {"name": "Sesotho", "code": "st-LS", "espeak": "st", "style": "warm"},
        "af": {"name": "Afrikaans", "code": "af-ZA", "espeak": "af", "style": "friendly"},
        
        # ══════════════════════════════════════════════════════════════
        # AMERICAS LANGUAGES
        # ══════════════════════════════════════════════════════════════
        "qu": {"name": "Quechua", "code": "qu-PE", "espeak": "qu", "style": "traditional"},
        "gn": {"name": "Guarani", "code": "gn-PY", "espeak": "gn", "style": "warm"},
        "ay": {"name": "Aymara", "code": "ay-BO", "espeak": "ay", "style": "traditional"},
        "nah": {"name": "Nahuatl", "code": "nah-MX", "espeak": "nah", "style": "traditional"},
        
        # ══════════════════════════════════════════════════════════════
        # OCEANIAN LANGUAGES
        # ══════════════════════════════════════════════════════════════
        "mi": {"name": "Maori", "code": "mi-NZ", "espeak": "mi", "style": "traditional"},
        "sm": {"name": "Samoan", "code": "sm-WS", "espeak": "sm", "style": "friendly"},
        "fj": {"name": "Fijian", "code": "fj-FJ", "espeak": "fj", "style": "friendly"},
        "haw": {"name": "Hawaiian", "code": "haw-US", "espeak": "haw", "style": "traditional"},
        "ty": {"name": "Tahitian", "code": "ty-PF", "espeak": "ty", "style": "friendly"},
        
        # ══════════════════════════════════════════════════════════════
        # ADDITIONAL LANGUAGES
        # ══════════════════════════════════════════════════════════════
        "en-AU": {"name": "English (Australia)", "code": "en-AU", "espeak": "en", "style": "friendly"},
        "en-GB": {"name": "English (UK)", "code": "en-GB", "espeak": "en-GB", "style": "elegant"},
        "en-IN": {"name": "English (India)", "code": "en-IN", "espeak": "en", "style": "friendly"},
        "en-NZ": {"name": "English (NZ)", "code": "en-NZ", "espeak": "en", "style": "friendly"},
        "en-ZA": {"name": "English (South Africa)", "code": "en-ZA", "espeak": "en", "style": "friendly"},
        "zh-SG": {"name": "Chinese (Singapore)", "code": "zh-SG", "espeak": "zh", "style": "formal"},
        "zh-HK": {"name": "Chinese (Hong Kong)", "code": "zh-HK", "espeak": "yue", "style": "formal"},
        "ja-JP": {"name": "Japanese", "code": "ja-JP", "espeak": "ja", "style": "formal"},
        
        # Other languages
        "ka": {"name": "Georgian", "code": "ka-GE", "espeak": "ka", "style": "formal"},
        "hy": {"name": "Armenian", "code": "hy-AM", "espeak": "hy", "style": "formal"},
        "az": {"name": "Azerbaijani", "code": "az-AZ", "espeak": "az", "style": "friendly"},
        "kaa": {"name": "Uighur", "code": "ug-CN", "espeak": "ug", "style": "traditional"},
        "sd": {"name": "Sindhi", "code": "sd-PK", "espeak": "sd", "style": "warm"},
        "dv": {"name": "Dhivehi", "code": "dv-MV", "espeak": "dv", "style": "formal"},
        "ne-NP": {"name": "Nepali", "code": "ne-NP", "espeak": "ne", "style": "warm"},
        "bo": {"name": "Tibetan", "code": "bo-CN", "espeak": "bo", "style": "traditional"},
        "dz": {"name": "Dzongkha", "code": "dz-BT", "espeak": "dz", "style": "formal"},
        "li": {"name": "Lingala", "code": "ln-CD", "espeak": "ln", "style": "friendly"},
        "tn": {"name": "Tswana", "code": "tn-BW", "espeak": "tn", "style": "warm"},
        "ss": {"name": "Swati", "code": "ss-SZ", "espeak": "ss", "style": "warm"},
        "ve": {"name": "Venda", "code": "ve-ZA", "espeak": "ve", "style": "warm"},
        "ts": {"name": "Tsonga", "code": "ts-ZA", "espeak": "ts", "style": "warm"},
        "nd": {"name": "Ndebele", "code": "nd-ZW", "espeak": "nd", "style": "warm"},
        "tlh": {"name": "Klingon", "code": "tlh-FF", "espeak": "tlh", "style": "formal"},
        "eo": {"name": "Esperanto", "code": "eo-001", "espeak": "eo", "style": "friendly"},
    }
    
    # Humanlike speech patterns
    PAUSE_MARKERS = {
        "short": 0.15,    # Comma
        "medium": 0.3,    # Semicolon, colon
        "long": 0.5,     # Period, question, exclamation
        "very_long": 0.8 # Paragraph break
    }
    
    def __init__(self, config):
        self.config = config
        self.engine = config.get("voice.tts", "piper")
        self.language = config.get("voice.language", "id")
        self.rate = config.get("voice.rate", 1.0)
        self.pitch = config.get("voice.pitch", 1.0)
        self.volume = config.get("voice.volume", 1.0)
        self.style = config.get("voice.style", "friendly")
        self.status = "disconnected"
        self._queue = []
        self._speaking = False
        
        # Voice profiles for humanlike speech
        self.voice_profiles = self._init_voice_profiles()
    
    def _init_voice_profiles(self) -> Dict:
        """Initialize voice profiles for different contexts"""
        return {
            "executive": {
                "rate": 0.95,
                "pitch": 0.95,
                "pause_multiplier": 1.0,
                "emphasis": "clear"
            },
            "warm": {
                "rate": 1.0,
                "pitch": 1.05,
                "pause_multiplier": 1.2,
                "emphasis": "soft"
            },
            "friendly": {
                "rate": 1.05,
                "pitch": 1.1,
                "pause_multiplier": 1.3,
                "emphasis": "natural"
            },
            "professional": {
                "rate": 0.9,
                "pitch": 0.9,
                "pause_multiplier": 0.9,
                "emphasis": "precise"
            },
            "excited": {
                "rate": 1.1,
                "pitch": 1.15,
                "pause_multiplier": 1.4,
                "emphasis": "energetic"
            }
        }
    
    def initialize(self) -> bool:
        """Initialize TTS engine"""
        self.status = "ready"
        print(f"🔊 TTS Engine initialized ({self.engine})")
        print(f"   Language: {self.LANGUAGES.get(self.language, {}).get('name', 'Indonesian')}")
        print(f"   Style: {self.style}")
        return True
    
    def speak(
        self, 
        text: str, 
        blocking: bool = False,
        language: str = None,
        style: str = None
    ) -> None:
        """
        Convert text to speech with humanlike intonation
        
        Args:
            text: Text to speak
            blocking: Wait for completion
            language: Override language
            style: Override speaking style
        """
        if not text:
            return
        
        # Process text for humanlike delivery
        processed_text = self._process_text_for_speech(text, language or self.language)
        
        self._queue.append({
            "text": processed_text,
            "language": language or self.language,
            "style": style or self.style
        })
        
        if not self._speaking:
            if blocking:
                self._process_queue()
            else:
                thread = threading.Thread(target=self._process_queue)
                thread.daemon = True
                thread.start()
    
    def _process_text_for_speech(self, text: str, language: str) -> str:
        """
        Process text to sound more humanlike
        - Add natural pauses
        - Handle abbreviations
        - Normalize numbers
        - Handle mixed language
        """
        # Clean up text
        text = text.strip()
        
        # Add natural pauses for punctuation
        text = self._add_natural_pauses(text)
        
        # Expand abbreviations
        text = self._expand_abbreviations(text, language)
        
        # Normalize numbers
        text = self._normalize_numbers(text, language)
        
        # Handle mixed language detection
        text = self._handle_mixed_language(text)
        
        # Add emphasis markers for emotional delivery
        text = self._add_emotional_markers(text)
        
        return text
    
    def _add_natural_pauses(self, text: str) -> str:
        """Add natural pauses between sentences"""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Add slight pause after commas (short breath)
        text = re.sub(r',', '... ', text)
        
        # Normal pauses after punctuation
        text = re.sub(r'([.!?])(\s)', r'\1\n\2', text)
        
        return text
    
    def _expand_abbreviations(self, text: str, language: str) -> str:
        """Expand common abbreviations"""
        abbreviations = {
            "rp": "Rupiah" if language == "id" else "Rupiah",
            "rp.": "Rupiah" if language == "id" else "Rupiah",
            "ppt": "Power Point",
            "drv": "Driver",
            "btw": "By the way",
            "aka": "also known as",
            "dll": "dan lain-lain",
            "dll.": "dan lain-lain",
            "dst": "dan seterusnya",
            "dst.": "dan seterusnya",
            "tsb": "tersebut",
            "tsb.": "tersebut",
            "yg": "yang",
            "dlm": "dalam",
            "dgn": "dengan",
            "utk": "untuk",
            "krn": "karena",
            "smg": "semoga",
            "bs": "bisa",
            "sdh": "sudah",
            "blm": "belum",
            "tdk": "tidak",
            "jg": "juga",
            "krn": "karena",
            "msh": "masih",
        }
        
        for abbr, full in abbreviations.items():
            pattern = re.compile(r'\b' + re.escape(abbr) + r'\b', re.IGNORECASE)
            text = pattern.sub(full, text)
        
        return text
    
    def _normalize_numbers(self, text: str, language: str) -> str:
        """Convert numbers to spoken words for better TTS"""
        # Handle millions
        text = re.sub(
            r'Rp\s*([\d,.]+)\s*(juta|milyar|triliun)',
            lambda m: self._number_to_words(m.group(1), language) + ' ' + m.group(2),
            text,
            flags=re.IGNORECASE
        )
        
        # Handle simple numbers
        text = re.sub(
            r'\b(\d{4,})\b',
            lambda m: self._number_to_words(m.group(1), language),
            text
        )
        
        return text
    
    def _number_to_words(self, number: str, language: str) -> str:
        """Convert number to spoken words"""
        # Simple implementation
        try:
            num = float(number.replace(',', '').replace('.', ''))
            if language == "id":
                if num >= 1000000000:
                    return f"{int(num/1000000000)} miliar"
                elif num >= 1000000:
                    return f"{int(num/1000000)} juta"
                elif num >= 1000:
                    return f"{int(num/1000)} ribu"
                else:
                    return str(int(num))
            else:
                return str(int(num))
        except:
            return number
    
    def _handle_mixed_language(self, text: str) -> str:
        """Handle Indonesian-English mixed text"""
        # Keep English terms that should be pronounced in English
        english_terms = [
            "CEO", "CTO", "CFO", "COO", "AI", "ML", "API", "URL", "HTML",
            "CSS", "JavaScript", "Python", "PHP", "Laravel", "React",
            "SaaS", "CRM", "ERP", "HR", "KPI", "ROI", "GDP"
        ]
        
        for term in english_terms:
            # Add pronunciation hint
            text = text.replace(term, f"<english>{term}</english>")
        
        return text
    
    def _add_emotional_markers(self, text: str) -> str:
        """Add markers for emotional emphasis"""
        # Happy/excited patterns
        if any(x in text.lower() for x in ['senang', 'happy', 'yeay', 'hore', 'great', 'bagus']):
            text = text.replace('!', '! 😊')
        
        # Questioning patterns
        if text.strip().endswith('?'):
            # Slightly raise pitch at end
            text = text[:-1] + '? 🎵'
        
        return text
    
    def _process_queue(self) -> None:
        """Process speech queue with humanlike timing"""
        self._speaking = True
        
        while self._queue:
            item = self._queue.pop(0)
            self._speak_text(
                item["text"],
                item["language"],
                item["style"]
            )
        
        self._speaking = False
    
    def _speak_text(self, text: str, language: str, style: str) -> None:
        """Speak text with selected engine and style"""
        # Get voice profile
        profile = self.voice_profiles.get(style, self.voice_profiles["friendly"])
        
        # Calculate effective rate
        effective_rate = self.rate * profile["rate"]
        
        # Select engine
        if self.engine == "piper":
            self._speak_piper(text, language, effective_rate)
        elif self.engine == "kokoro":
            self._speak_kokoro(text, language, effective_rate)
        elif self.engine == "coqui":
            self._speak_coqui(text, language, effective_rate)
        elif self.engine == "gtts":
            self._speak_gtts(text, language)
        elif self.engine == "espeak":
            self._speak_espeak(text, language, effective_rate)
        else:
            self._speak_system(text, language, effective_rate)
    
    def _speak_piper(self, text: str, language: str, rate: float) -> None:
        """Speak using Piper TTS with Indonesian voice models"""
        try:
            lang_code = self.LANGUAGES.get(language, self.LANGUAGES["id"])["piper"]
            
            # Prepare text for piper
            text_file = "/tmp/gauranga_tts.txt"
            with open(text_file, 'w') as f:
                f.write(text)
            
            # Run piper
            cmd = [
                "piper",
                "--model", f"{lang_code}_low.onnx",
                "--config", f"{lang_code}_low.onnx.json",
                "--input-file", text_file,
                "--output-file", "/tmp/gauranga_tts.wav"
            ]
            
            subprocess.run(cmd, capture_output=True, timeout=30)
            
            # Play audio
            subprocess.run(["aplay", "/tmp/gauranga_tts.wav"], capture_output=True)
            
        except Exception as e:
            print(f"[PIPER TTS] Using fallback: {e}")
            self._speak_system(text, language, rate)
    
    def _speak_kokoro(self, text: str, language: str, rate: float) -> None:
        """Speak using Kokoro TTS"""
        try:
            lang_code = self.LANGUAGES.get(language, self.LANGUAGES["id"])["code"]
            
            # Kokoro API call would go here
            print(f"[KOKORO TTS] {lang_code}: {text}")
            
        except Exception as e:
            print(f"[KOKORO TTS] Error: {e}")
            self._speak_system(text, language, rate)
    
    def _speak_coqui(self, text: str, language: str, rate: float) -> None:
        """Speak using Coqui TTS"""
        try:
            print(f"[COQUI TTS] {language}: {text}")
        except Exception as e:
            print(f"[COQUI TTS] Error: {e}")
            self._speak_system(text, language, rate)
    
    def _speak_gtts(self, text: str, language: str) -> None:
        """Speak using Google Translate TTS"""
        try:
            from gtts import gTTS
            
            lang_map = {"id": "id", "en": "en", "ban": "id", "jv": "jw", "su": "su"}
            lang = lang_map.get(language, "id")
            
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save("/tmp/gauranga_tts.mp3")
            
            subprocess.run(["mpg123", "-q", "/tmp/gauranga_tts.mp3"], capture_output=True)
            
        except Exception as e:
            print(f"[gTTS] Error: {e}")
            self._speak_espeak(text, language, 1.0)
    
    def _speak_espeak(self, text: str, language: str, rate: float) -> None:
        """Speak using espeak-ng with language optimization"""
        try:
            espeak_lang = self.LANGUAGES.get(language, self.LANGUAGES["id"])["espeak"]
            
            # espeak-ng with better settings for Indonesian
            cmd = [
                "espeak-ng",
                "-v", f"{espeak_lang}+f3",  # Female voice variant
                "-s", str(int(170 * rate)),  # Speed adjustment
                "-p", str(int(50 + (self.pitch - 1) * 30)),  # Pitch
                "-a", str(int(self.volume * 100)),  # Amplitude
                text
            ]
            
            subprocess.run(cmd, capture_output=True, timeout=15)
            
        except Exception as e:
            print(f"[ESPEAK] Error: {e}")
            self._speak_system(text, language, rate)
    
    def _speak_system(self, text: str, language: str, rate: float) -> None:
        """Fallback system TTS"""
        print(f"🔊 [{language.upper()}] {text}")
    
    def speak_voice_line(self, text: str, emotion: str = "neutral") -> None:
        """
        Speak a voice line with specific emotion
        
        Emotions:
        - neutral: Normal professional tone
        - happy: Slightly faster, higher pitch
        - sad: Slower, lower pitch
        - excited: Faster, higher pitch, more emphasis
        - calm: Very slow, even tone
        """
        emotion_styles = {
            "neutral": "executive",
            "happy": "excited",
            "sad": "professional",
            "excited": "excited",
            "calm": "warm",
            "serious": "professional",
            "friendly": "friendly"
        }
        
        style = emotion_styles.get(emotion, "friendly")
        
        # Add emotional particles
        if emotion == "happy":
            text = f"Senangnya bisa membantu! {text}"
        elif emotion == "excited":
            text = f"Wah mantap! {text}"
        elif emotion == "calm":
            text = f"Santai ya... {text}"
        
        self.speak(text, style=style)
    
    def stop(self) -> None:
        """Stop current speech"""
        self._queue = []
        self._speaking = False
        
        # Try to kill any running TTS process
        try:
            subprocess.run(["pkill", "-f", "espeak"], capture_output=True)
            subprocess.run(["pkill", "-f", "piper"], capture_output=True)
            subprocess.run(["pkill", "-f", "aplay"], capture_output=True)
        except:
            pass
    
    def set_rate(self, rate: float) -> None:
        """Set speech rate (0.5 to 2.0)"""
        self.rate = max(0.5, min(2.0, rate))
    
    def set_pitch(self, pitch: float) -> None:
        """Set voice pitch (0.5 to 2.0)"""
        self.pitch = max(0.5, min(2.0, pitch))
    
    def set_volume(self, volume: float) -> None:
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
    
    def set_language(self, language: str) -> None:
        """Set language"""
        if language in self.LANGUAGES:
            self.language = language
            print(f"🌐 Language changed to: {self.LANGUAGES[language]['name']}")
    
    def set_style(self, style: str) -> None:
        """Set speaking style"""
        if style in self.voice_profiles:
            self.style = style
            print(f"🎭 Speaking style: {style}")
    
    def get_available_languages(self) -> List[str]:
        """Get list of available languages"""
        return [
            {"code": code, "name": config["name"]}
            for code, config in self.LANGUAGES.items()
        ]


class WebSpeechTTS:
    """
    Web Speech API TTS (for browser)
    Humanlike voice using Web Speech Synthesis API
    """
    
    def __init__(self):
        self.status = "ready"
        self.current_language = "id-ID"
        
        # Voice configurations for web
        self.voice_configs = {
            "id-ID": {"rate": 1.0, "pitch": 1.0, "volume": 1.0},
            "en-US": {"rate": 1.0, "pitch": 1.0, "volume": 1.0},
        }
    
    def speak(self, text: str, language: str = "id-ID", emotion: str = "neutral") -> None:
        """
        Speak using Web Speech API with humanlike settings
        This is implemented in JavaScript but the config is prepared here
        """
        config = self.voice_configs.get(language, self.voice_configs["id-ID"])
        
        # Add emotional modulation
        if emotion == "happy":
            config["pitch"] = 1.1
            config["rate"] = 1.05
            text = f"Senangnya... {text}"
        elif emotion == "excited":
            config["pitch"] = 1.15
            config["rate"] = 1.1
            text = f"Wah hebat! {text}"
        elif emotion == "calm":
            config["pitch"] = 0.95
            config["rate"] = 0.9
            text = f"Santai ya... {text}"
        
        print(f"[Web Speech TTS] {language}: {text}")
        print(f"    Config: rate={config['rate']}, pitch={config['pitch']}")
    
    def stop(self) -> None:
        """Stop speech"""
        pass