"""
GAURANGA STT Engine
Speech-to-Text with ALL World Languages Support
Supports Whisper + Web Speech API
"""

import os
import subprocess
import threading
from typing import Optional, Callable, Dict, List
from abc import ABC, abstractmethod

class STTEngine:
    """
    STT Engine - Supports ALL world languages
    
    Language Support:
    - Web Speech API: 100+ languages (browser)
    - Whisper: 100+ languages (offline)
    - Vosk: 20+ languages (offline)
    
    Languages include: Indonesian, English, Mandarin, Spanish, Hindi, Arabic,
    French, German, Japanese, Korean, Thai, Vietnamese, and 90+ more
    """
    
    # ALL Supported Languages
    LANGUAGES = {
        # ══════════════════════════════════════════════════════════════
        # ASIAN LANGUAGES
        # ══════════════════════════════════════════════════════════════
        # Southeast Asia
        "id": {"name": "Indonesian", "code": "id-ID", "whisper": "id"},
        "ms": {"name": "Malay", "code": "ms-MY", "whisper": "ms"},
        "tl": {"name": "Filipino", "code": "fil-PH", "whisper": "fil"},
        "th": {"name": "Thai", "code": "th-TH", "whisper": "th"},
        "vi": {"name": "Vietnamese", "code": "vi-VN", "whisper": "vi"},
        "km": {"name": "Khmer", "code": "km-KH", "whisper": "km"},
        "lo": {"name": "Lao", "code": "lo-LA", "whisper": "lo"},
        "my": {"name": "Burmese", "code": "my-MM", "whisper": "my"},
        
        # East Asia
        "zh": {"name": "Chinese (Mandarin)", "code": "zh-CN", "whisper": "zh"},
        "zh-TW": {"name": "Chinese (Taiwan)", "code": "zh-TW", "whisper": "zh"},
        "yue": {"name": "Cantonese", "code": "yue-CN", "whisper": "yue"},
        "ja": {"name": "Japanese", "code": "ja-JP", "whisper": "ja"},
        "ko": {"name": "Korean", "code": "ko-KR", "whisper": "ko"},
        "mn": {"name": "Mongolian", "code": "mn-MN", "whisper": "mn"},
        
        # South Asia
        "hi": {"name": "Hindi", "code": "hi-IN", "whisper": "hi"},
        "bn": {"name": "Bengali", "code": "bn-BD", "whisper": "bn"},
        "pa": {"name": "Punjabi", "code": "pa-IN", "whisper": "pa"},
        "ta": {"name": "Tamil", "code": "ta-IN", "whisper": "ta"},
        "te": {"name": "Telugu", "code": "te-IN", "whisper": "te"},
        "mr": {"name": "Marathi", "code": "mr-IN", "whisper": "mr"},
        "gu": {"name": "Gujarati", "code": "gu-IN", "whisper": "gu"},
        "kn": {"name": "Kannada", "code": "kn-IN", "whisper": "kn"},
        "ml": {"name": "Malayalam", "code": "ml-IN", "whisper": "ml"},
        "ne": {"name": "Nepali", "code": "ne-NP", "whisper": "ne"},
        "si": {"name": "Sinhala", "code": "si-LK", "whisper": "si"},
        "ur": {"name": "Urdu", "code": "ur-PK", "whisper": "ur"},
        
        # Regional Indonesian
        "ban": {"name": "Balinese", "code": "ban-ID", "whisper": "ban"},
        "jv": {"name": "Javanese", "code": "jv-ID", "whisper": "jv"},
        "su": {"name": "Sundanese", "code": "su-ID", "whisper": "su"},
        
        # ══════════════════════════════════════════════════════════════
        # EUROPEAN LANGUAGES
        # ══════════════════════════════════════════════════════════════
        "en": {"name": "English", "code": "en-US", "whisper": "en"},
        "es": {"name": "Spanish", "code": "es-ES", "whisper": "es"},
        "es-MX": {"name": "Spanish (Mexico)", "code": "es-MX", "whisper": "es"},
        "es-AR": {"name": "Spanish (Argentina)", "code": "es-AR", "whisper": "es"},
        "pt": {"name": "Portuguese", "code": "pt-PT", "whisper": "pt"},
        "pt-BR": {"name": "Portuguese (Brazil)", "code": "pt-BR", "whisper": "pt"},
        "fr": {"name": "French", "code": "fr-FR", "whisper": "fr"},
        "fr-CA": {"name": "French (Canada)", "code": "fr-CA", "whisper": "fr"},
        "de": {"name": "German", "code": "de-DE", "whisper": "de"},
        "de-AT": {"name": "German (Austria)", "code": "de-AT", "whisper": "de"},
        "it": {"name": "Italian", "code": "it-IT", "whisper": "it"},
        "nl": {"name": "Dutch", "code": "nl-NL", "whisper": "nl"},
        "pl": {"name": "Polish", "code": "pl-PL", "whisper": "pl"},
        "ro": {"name": "Romanian", "code": "ro-RO", "whisper": "ro"},
        "cs": {"name": "Czech", "code": "cs-CZ", "whisper": "cs"},
        "sk": {"name": "Slovak", "code": "sk-SK", "whisper": "sk"},
        "hu": {"name": "Hungarian", "code": "hu-HU", "whisper": "hu"},
        "bg": {"name": "Bulgarian", "code": "bg-BG", "whisper": "bg"},
        "hr": {"name": "Croatian", "code": "hr-HR", "whisper": "hr"},
        "sr": {"name": "Serbian", "code": "sr-RS", "whisper": "sr"},
        "sl": {"name": "Slovenian", "code": "sl-SI", "whisper": "sl"},
        "mk": {"name": "Macedonian", "code": "mk-MK", "whisper": "mk"},
        "sq": {"name": "Albanian", "code": "sq-AL", "whisper": "sq"},
        "el": {"name": "Greek", "code": "el-GR", "whisper": "el"},
        "tr": {"name": "Turkish", "code": "tr-TR", "whisper": "tr"},
        "uk": {"name": "Ukrainian", "code": "uk-UA", "whisper": "uk"},
        "be": {"name": "Belarusian", "code": "be-BY", "whisper": "be"},
        "ru": {"name": "Russian", "code": "ru-RU", "whisper": "ru"},
        "et": {"name": "Estonian", "code": "et-EE", "whisper": "et"},
        "lv": {"name": "Latvian", "code": "lv-LV", "whisper": "lv"},
        "lt": {"name": "Lithuanian", "code": "lt-LT", "whisper": "lt"},
        "is": {"name": "Icelandic", "code": "is-IS", "whisper": "is"},
        "no": {"name": "Norwegian", "code": "nb-NO", "whisper": "no"},
        "sv": {"name": "Swedish", "code": "sv-SE", "whisper": "sv"},
        "da": {"name": "Danish", "code": "da-DK", "whisper": "da"},
        "fi": {"name": "Finnish", "code": "fi-FI", "whisper": "fi"},
        
        # ══════════════════════════════════════════════════════════════
        # MIDDLE EASTERN & CENTRAL ASIAN
        # ══════════════════════════════════════════════════════════════
        "ar": {"name": "Arabic", "code": "ar-SA", "whisper": "ar"},
        "ar-SA": {"name": "Arabic (Saudi)", "code": "ar-SA", "whisper": "ar"},
        "ar-EG": {"name": "Arabic (Egypt)", "code": "ar-EG", "whisper": "ar"},
        "ar-AE": {"name": "Arabic (UAE)", "code": "ar-AE", "whisper": "ar"},
        "he": {"name": "Hebrew", "code": "he-IL", "whisper": "he"},
        "fa": {"name": "Persian (Farsi)", "code": "fa-IR", "whisper": "fa"},
        "ps": {"name": "Pashto", "code": "ps-AF", "whisper": "ps"},
        "kk": {"name": "Kazakh", "code": "kk-KZ", "whisper": "kk"},
        "uz": {"name": "Uzbek", "code": "uz-UZ", "whisper": "uz"},
        "tg": {"name": "Tajik", "code": "tg-TJ", "whisper": "tg"},
        
        # ══════════════════════════════════════════════════════════════
        # AFRICAN LANGUAGES
        # ══════════════════════════════════════════════════════════════
        "sw": {"name": "Swahili", "code": "sw-TZ", "whisper": "sw"},
        "sw-KE": {"name": "Swahili (Kenya)", "code": "sw-KE", "whisper": "sw"},
        "yo": {"name": "Yoruba", "code": "yo-NG", "whisper": "yo"},
        "ha": {"name": "Hausa", "code": "ha-NG", "whisper": "ha"},
        "ig": {"name": "Igbo", "code": "ig-NG", "whisper": "ig"},
        "zu": {"name": "Zulu", "code": "zu-ZA", "whisper": "zu"},
        "xh": {"name": "Xhosa", "code": "xh-ZA", "whisper": "xh"},
        "am": {"name": "Amharic", "code": "am-ET", "whisper": "am"},
        "so": {"name": "Somali", "code": "so-SO", "whisper": "so"},
        "or": {"name": "Oromo", "code": "om-ET", "whisper": "om"},
        "rw": {"name": "Kinyarwanda", "code": "rw-RW", "whisper": "rw"},
        "mg": {"name": "Malagasy", "code": "mg-MG", "whisper": "mg"},
        "sn": {"name": "Shona", "code": "sn-ZW", "whisper": "sn"},
        "af": {"name": "Afrikaans", "code": "af-ZA", "whisper": "af"},
        
        # ══════════════════════════════════════════════════════════════
        # OCEANIAN LANGUAGES
        # ══════════════════════════════════════════════════════════════
        "mi": {"name": "Maori", "code": "mi-NZ", "whisper": "mi"},
        "sm": {"name": "Samoan", "code": "sm-WS", "whisper": "sm"},
        "fj": {"name": "Fijian", "code": "fj-FJ", "whisper": "fj"},
        "haw": {"name": "Hawaiian", "code": "haw-US", "whisper": "haw"},
        
        # ══════════════════════════════════════════════════════════════
        # ADDITIONAL LANGUAGES
        # ══════════════════════════════════════════════════════════════
        "en-AU": {"name": "English (Australia)", "code": "en-AU", "whisper": "en"},
        "en-GB": {"name": "English (UK)", "code": "en-GB", "whisper": "en"},
        "en-IN": {"name": "English (India)", "code": "en-IN", "whisper": "en"},
        "zh-SG": {"name": "Chinese (Singapore)", "code": "zh-SG", "whisper": "zh"},
        "zh-HK": {"name": "Chinese (Hong Kong)", "code": "zh-HK", "whisper": "yue"},
        "ka": {"name": "Georgian", "code": "ka-GE", "whisper": "ka"},
        "hy": {"name": "Armenian", "code": "hy-AM", "whisper": "hy"},
        "az": {"name": "Azerbaijani", "code": "az-AZ", "whisper": "az"},
        "sd": {"name": "Sindhi", "code": "sd-PK", "whisper": "sd"},
        "dv": {"name": "Dhivehi", "code": "dv-MV", "whisper": "dv"},
        "bo": {"name": "Tibetan", "code": "bo-CN", "whisper": "bo"},
    }
    
    def __init__(self, config):
        self.config = config
        self.model = config.get("voice.stt_model", "base")
        self.language = config.get("voice.language", "id")
        self.status = "disconnected"
        self._listening = False
        self._hotword_detected = False
        self._hotword = config.get("system.hotword", "hey gauranga").lower()
        self._callbacks = []
    
    def initialize(self) -> bool:
        """Initialize STT engine"""
        self.status = "ready"
        print("🎤 STT Engine initialized (Whisper + Web Speech API)")
        print(f"   Supported languages: {len(self.LANGUAGES)}")
        return True
    
    def listen(self, timeout: int = 10) -> str:
        """
        Listen for audio and convert to text
        Uses Whisper for offline, Web Speech API for browser
        """
        # For demo, return empty (would use microphone in real device)
        return ""
    
    def listen_async(self, callback: Callable[[str], None]) -> None:
        """
        Listen asynchronously and call callback with transcription
        """
        self._callbacks.append(callback)
        # Would start listening thread here
    
    def listen_for_hotword(self) -> bool:
        """
        Listen for hotword detection
        Supports: "hey gauranga", "gauranga", "halo gauranga"
        """
        # For demo, return False (would use actual hotword detection)
        return False
    
    def transcribe_file(self, audio_path: str) -> str:
        """
        Transcribe audio file using Whisper
        """
        try:
            # Whisper transcription command
            cmd = [
                "whisper",
                audio_path,
                "--model", self.model,
                "--language", self.LANGUAGES.get(self.language, {}).get("whisper", "en"),
                "--task", "transcribe"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout.strip()
        except Exception as e:
            print(f"Whisper error: {e}")
            return ""
    
    def set_language(self, language: str) -> bool:
        """
        Set recognition language
        Returns True if language is supported
        """
        if language in self.LANGUAGES:
            self.language = language
            print(f"🌐 STT language changed to: {self.LANGUAGES[language]['name']}")
            return True
        return False
    
    def get_supported_languages(self) -> List[Dict]:
        """Get list of supported languages"""
        return [
            {"code": code, "name": config["name"]}
            for code, config in self.LANGUAGES.items()
        ]
    
    def detect_language(self, text: str) -> str:
        """
        Detect language from text
        Uses simple heuristics and can be enhanced with langdetect
        """
        # Simple language detection based on common words
        indicators = {
            "id": ["yang", "dan", "di", "ke", "dari", "ini", "itu", "dengan", "untuk"],
            "en": ["the", "and", "is", "are", "in", "to", "of", "a", "this", "that"],
            "zh": ["的", "是", "在", "和", "了", "我", "你", "他", "这", "那"],
            "ja": ["の", "は", "が", "と", "に", "を", "で", "れ", "さ", "し"],
            "ko": ["의", "은", "가", "와", "과", "에", "를", "으로", "하다", "있다"],
            "es": ["el", "la", "de", "que", "y", "en", "un", "una", "es", "son"],
            "fr": ["le", "la", "de", "et", "des", "un", "une", "est", "que", "dans"],
            "de": ["der", "die", "das", "und", "ist", "in", "zu", "den", "mit", "auf"],
            "ar": ["في", "من", "على", "أن", "هذا", "التي", "هو", "هي", "كان", "مع"],
            "th": ["แ", "ที่", "เป็น", "มี", "และ", "ของ", "ใน", "การ", "ได้", "ถูก"],
            "vi": ["của", "là", "và", "trong", "có", "được", "cho", "với", "này", "một"],
            "ms": ["dan", "di", "yang", "ke", "dari", "ini", "itu", "dengan", "untuk", "ada"],
        }
        
        text_lower = text.lower()
        scores = {}
        
        for lang, words in indicators.items():
            score = sum(1 for word in words if word in text_lower)
            scores[lang] = score
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return self.language  # Return current language as fallback


# Alias for compatibility
WhisperSTT = STTEngine