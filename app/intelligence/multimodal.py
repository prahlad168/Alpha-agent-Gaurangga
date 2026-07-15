"""
MAHALAKSMI AIOS v2.0 - Volume II: Intelligence Suite
Chapter 15: Vision Engine | Chapter 16: Voice Engine | Chapter 17: NLP Engine
"""
import os
import sys
import json
import hashlib
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class SentimentType(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EntityType(Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    MONEY = "money"
    DATE = "date"
    PRODUCT = "product"
    BRAND = "brand"


@dataclass
class VisionResult:
    """Image analysis result."""
    success: bool
    description: str
    labels: List[Dict]
    text_extracted: str = ""
    confidence: float = 0.0
    objects_detected: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class VoiceResult:
    """Voice processing result."""
    success: bool
    transcript: str = ""
    command: str = ""
    intent: str = ""
    confidence: float = 0.0
    tts_output: str = ""
    language: str = "id-ID"


@dataclass
class NLPResult:
    """NLP analysis result."""
    success: bool
    sentiment: SentimentType = SentimentType.NEUTRAL
    sentiment_score: float = 0.0
    entities: List[Dict] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    summary: str = ""


# ============================================================================
# VISION ENGINE (Chapter 15)
# ============================================================================

class VisionEngine:
    """
    Vision Engine for image analysis, OCR, and structural extraction.
    Integrates with AI providers for image understanding.
    """
    
    def __init__(self):
        self.supported_formats = ["jpg", "jpeg", "png", "gif", "webp", "bmp"]
        logger.info("VisionEngine initialized")
    
    def analyze_image(
        self,
        image_data: str = None,
        image_url: str = None,
        prompt: str = "Describe this image in detail"
    ) -> VisionResult:
        """
        Analyze an image and extract information.
        
        Args:
            image_data: Base64 encoded image
            image_url: URL to image
            prompt: Analysis prompt
        
        Returns:
            VisionResult with analysis
        """
        # Demo mode - return simulated results
        result = VisionResult(
            success=True,
            description=f"Demo image analysis for prompt: {prompt}",
            labels=[
                {"label": "document", "confidence": 0.95},
                {"label": "text", "confidence": 0.90},
                {"label": "business", "confidence": 0.85}
            ],
            text_extracted="SAMPLE TEXT EXTRACTED FROM IMAGE",
            confidence=0.92,
            objects_detected=["text", "document", "paper"],
            metadata={
                "format": "demo",
                "size": "1920x1080",
                "analyzed_at": datetime.now().isoformat()
            }
        )
        
        logger.info(f"Vision analysis completed: {len(result.labels)} labels")
        return result
    
    def extract_text(self, image_data: str = None, image_url: str = None) -> str:
        """
        Extract text from image using OCR.
        
        Returns:
            Extracted text string
        """
        # Demo OCR result
        ocr_result = """
        MAHA LAKSHMI HOLDINGS
        
        Invoice Number: INV-2026-001
        Date: July 14, 2026
        Amount: Rp 5,000,000
        
        Bill To:
        PT Example Indonesia
        Jakarta, Indonesia
        """
        
        logger.info("OCR extraction completed")
        return ocr_result.strip()
    
    def detect_objects(self, image_data: str = None) -> List[str]:
        """Detect objects in image."""
        return ["document", "text", "paper", "business_card"]
    
    def classify_image(self, image_data: str = None) -> Dict:
        """Classify image content."""
        return {
            "primary_category": "document",
            "sub_categories": ["invoice", "business"],
            "confidence": 0.88
        }


# ============================================================================
# VOICE ENGINE (Chapter 16)
# ============================================================================

class VoiceEngine:
    """
    Voice Engine for voice commands, TTS, and STT.
    Provides speech interface capabilities.
    """
    
    def __init__(self):
        self.supported_languages = ["id-ID", "en-US"]
        self.command_patterns = {
            "laporan": "report",
            "jualan": "sales",
            "marketing": "marketing",
            "hr": "hr",
            "finance": "finance",
            "status": "status",
            "bantu": "help"
        }
        logger.info("VoiceEngine initialized")
    
    def process_voice_command(self, audio_data: str = None, language: str = "id-ID") -> VoiceResult:
        """
        Process voice command and extract intent.
        
        Args:
            audio_data: Base64 encoded audio
            language: Language code
        
        Returns:
            VoiceResult with command and intent
        """
        # Demo voice processing
        result = VoiceResult(
            success=True,
            transcript="Demo voice transcript",
            command="laporan pagi",
            intent="daily_report",
            confidence=0.95,
            tts_output="",
            language=language
        )
        
        logger.info(f"Voice command processed: {result.intent}")
        return result
    
    def text_to_speech(self, text: str, language: str = "id-ID") -> str:
        """
        Convert text to speech.
        
        Returns:
            Base64 encoded audio or URL
        """
        # Demo TTS - return placeholder
        return f"data:audio/mp3;base64,DEMO_TTS_OUTPUT_FOR_{hashlib.md5(text.encode()).hexdigest()[:8].upper()}"
    
    def speech_to_text(self, audio_data: str, language: str = "id-ID") -> str:
        """
        Convert speech to text.
        
        Returns:
            Transcribed text
        """
        # Demo STT
        return "Demo transcribed text from audio"
    
    def synthesize_voice_response(self, text: str, emotion: str = "neutral") -> str:
        """
        Synthesize voice with emotion.
        
        Args:
            text: Response text
            emotion: Emotion type
        
        Returns:
            Voice audio data
        """
        emotion_prefix = {
            "happy": "Senang sekali! ",
            "neutral": "",
            "urgent": "Penting! ",
            "sad": "Mohon maaf... "
        }
        
        full_text = emotion_prefix.get(emotion, "") + text
        return self.text_to_speech(full_text)


# ============================================================================
# NLP ENGINE (Chapter 17)
# ============================================================================

class NLPEngine:
    """
    NLP Engine for sentiment analysis, entity extraction, and categorization.
    Processes business communications automatically.
    """
    
    def __init__(self):
        self.positive_keywords = [
            "bagus", "baik", "senang", "puas", "sukses", "berhasil", 
            "good", "great", "excellent", "happy", "satisfied", "success"
        ]
        self.negative_keywords = [
            "buruk", "jelek", "kecewa", "gagal", "masalah", "error",
            "bad", "poor", "disappointed", "failed", "problem", "issue"
        ]
        logger.info("NLPEngine initialized")
    
    def analyze_sentiment(self, text: str) -> NLPResult:
        """
        Analyze sentiment of text.
        
        Returns:
            NLPResult with sentiment analysis
        """
        text_lower = text.lower()
        
        positive_count = sum(1 for kw in self.positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in self.negative_keywords if kw in text_lower)
        
        total = positive_count + negative_count
        
        if total == 0:
            sentiment = SentimentType.NEUTRAL
            score = 0.0
        elif positive_count > negative_count:
            sentiment = SentimentType.POSITIVE
            score = positive_count / total
        else:
            sentiment = SentimentType.NEGATIVE
            score = negative_count / total
        
        result = NLPResult(
            success=True,
            sentiment=sentiment,
            sentiment_score=score,
            entities=[],
            categories=[],
            keywords=[],
            summary=""
        )
        
        logger.info(f"Sentiment analysis: {sentiment.value} ({score:.2f})")
        return result
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from text.
        
        Returns:
            List of extracted entities
        """
        entities = []
        
        # Extract money amounts
        money_pattern = r"Rp\s?[\d,.]+|IDR\s?[\d,.]+|\$[\d,.]+"
        money_matches = re.findall(money_pattern, text)
        for match in money_matches:
            entities.append({
                "type": EntityType.MONEY.value,
                "value": match,
                "text": match
            })
        
        # Extract dates
        date_pattern = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}"
        date_matches = re.findall(date_pattern, text)
        for match in date_matches:
            entities.append({
                "type": EntityType.DATE.value,
                "value": match,
                "text": match
            })
        
        # Extract emails
        email_pattern = r"[\w.-]+@[\w.-]+\.\w+"
        email_matches = re.findall(email_pattern, text)
        for match in email_matches:
            entities.append({
                "type": "email",
                "value": match,
                "text": match
            })
        
        # Extract phone numbers
        phone_pattern = r"08\d{9,11}|628\d{9,11}|\+62\d{9,11}"
        phone_matches = re.findall(phone_pattern, text)
        for match in phone_matches:
            entities.append({
                "type": "phone",
                "value": match,
                "text": match
            })
        
        logger.info(f"Extracted {len(entities)} entities")
        return entities
    
    def categorize_text(self, text: str) -> List[str]:
        """
        Categorize text content.
        
        Returns:
            List of categories
        """
        categories = []
        text_lower = text.lower()
        
        # Business categories
        category_keywords = {
            "finance": ["uang", "pembayaran", "invoice", "revenue", "payment", "transfer", "Rp"],
            "sales": ["jualan", "sales", "customer", "pelanggan", "order", "pemesanan"],
            "marketing": ["marketing", "promosi", "campaign", "iklan", "ads"],
            "hr": ["karyawan", "employee", "cuti", "leave", "gaji", "payroll"],
            "operations": ["operasional", "operations", "logistics", "delivery"],
            "technical": ["error", "bug", "system", "server", "api", "code"],
            "customer_service": ["complaint", "complaint", "support", "bantuan", "ticket"]
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in text_lower for kw in keywords):
                categories.append(category)
        
        if not categories:
            categories.append("general")
        
        logger.info(f"Text categorized as: {categories}")
        return categories
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Filter stopwords
        stopwords = {'yang', 'untuk', 'dengan', 'pada', 'dan', 'the', 'and', 'for', 'with', 'this', 'that'}
        keywords = [w for w in words if w not in stopwords]
        
        # Get most common
        from collections import Counter
        keyword_counts = Counter(keywords)
        return [kw for kw, _ in keyword_counts.most_common(max_keywords)]
    
    def full_analysis(self, text: str) -> NLPResult:
        """
        Perform full NLP analysis.
        
        Returns:
            Complete NLPResult
        """
        sentiment = self.analyze_sentiment(text)
        entities = self.extract_entities(text)
        categories = self.categorize_text(text)
        keywords = self.extract_keywords(text)
        
        result = NLPResult(
            success=True,
            sentiment=sentiment.sentiment,
            sentiment_score=sentiment.sentiment_score,
            entities=entities,
            categories=categories,
            keywords=keywords,
            summary=f"Text expresses {sentiment.sentiment.value} sentiment with {len(entities)} entities"
        )
        
        return result


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

_vision_engine: Optional[VisionEngine] = None
_voice_engine: Optional[VoiceEngine] = None
_nlp_engine: Optional[NLPEngine] = None


def get_vision_engine() -> VisionEngine:
    """Get or create global Vision engine."""
    global _vision_engine
    if _vision_engine is None:
        _vision_engine = VisionEngine()
    return _vision_engine


def get_voice_engine() -> VoiceEngine:
    """Get or create global Voice engine."""
    global _voice_engine
    if _voice_engine is None:
        _voice_engine = VoiceEngine()
    return _voice_engine


def get_nlp_engine() -> NLPEngine:
    """Get or create global NLP engine."""
    global _nlp_engine
    if _nlp_engine is None:
        _nlp_engine = NLPEngine()
    return _nlp_engine
