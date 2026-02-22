"""
Language Detector for Multilingual Voice Assistant
Detects and manages language switching for English, Yoruba, Igbo, Hausa, and Nigerian Pidgin
"""

import logging
from typing import Optional, Dict, List, Tuple
from ..clients.qwen_client import QwenClient
from ..models.voice_models import LanguageDetectionResult

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Language detection system with automatic switching and confidence scoring
    Supports: English, Yoruba, Igbo, Hausa, Nigerian Pidgin
    """
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'yo': 'Yoruba',
        'ig': 'Igbo',
        'ha': 'Hausa',
        'pcm': 'Nigerian Pidgin'
    }
    
    # Confidence threshold for automatic language switching
    CONFIDENCE_THRESHOLD = 0.6
    
    def __init__(self, qwen_client: QwenClient):
        """
        Initialize language detector
        
        Args:
            qwen_client: Qwen3-Reranker client for language detection
        """
        self.qwen_client = qwen_client
        logger.info("Language Detector initialized")
    
    async def detect_language(
        self,
        text: str,
        preferred_language: Optional[str] = None
    ) -> LanguageDetectionResult:
        """
        Detect language from text with confidence scoring
        
        Args:
            text: Input text to analyze
            preferred_language: User's preferred language (fallback)
            
        Returns:
            LanguageDetectionResult with detected language and confidence
        """
        try:
            # Use Qwen client for AI-powered detection
            result = await self.qwen_client.detect_language(text)
            
            detected_lang = result['language']
            confidence = result['confidence']
            alternatives = result['alternatives']
            
            # If confidence is low, use preferred language
            if confidence < self.CONFIDENCE_THRESHOLD and preferred_language:
                logger.warning(
                    f"Low confidence ({confidence:.2f}) for detected language '{detected_lang}'. "
                    f"Using preferred language '{preferred_language}'"
                )
                detected_lang = preferred_language
                confidence = 0.5  # Medium confidence for fallback
            
            # Validate detected language is supported
            if detected_lang not in self.SUPPORTED_LANGUAGES:
                logger.warning(f"Unsupported language '{detected_lang}'. Defaulting to English")
                detected_lang = 'en'
                confidence = 0.5
            
            logger.info(f"Detected language: {detected_lang} ({self.SUPPORTED_LANGUAGES[detected_lang]}) - Confidence: {confidence:.2f}")
            
            return LanguageDetectionResult(
                language=detected_lang,
                confidence=confidence,
                alternatives=alternatives
            )
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            # Fallback to heuristic detection
            return await self._fallback_detection(text, preferred_language)
    
    async def _fallback_detection(
        self,
        text: str,
        preferred_language: Optional[str] = None
    ) -> LanguageDetectionResult:
        """
        Fallback language detection using keyword heuristics
        
        Args:
            text: Input text
            preferred_language: User's preferred language
            
        Returns:
            LanguageDetectionResult with best guess
        """
        logger.info("Using fallback language detection")
        
        text_lower = text.lower()
        
        # Language-specific keywords and patterns
        language_scores = {
            'yo': self._score_yoruba(text_lower),
            'ig': self._score_igbo(text_lower),
            'ha': self._score_hausa(text_lower),
            'pcm': self._score_pidgin(text_lower),
            'en': self._score_english(text_lower)
        }
        
        # Find language with highest score
        detected_lang = max(language_scores, key=language_scores.get)
        max_score = language_scores[detected_lang]
        
        # Normalize confidence
        total_score = sum(language_scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.5
        
        # If confidence is too low and we have a preferred language, use it
        if confidence < self.CONFIDENCE_THRESHOLD and preferred_language:
            detected_lang = preferred_language
            confidence = 0.5
        
        # Get alternatives
        sorted_langs = sorted(
            language_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        alternatives = [
            (lang, score / total_score if total_score > 0 else 0.0)
            for lang, score in sorted_langs[1:4]
        ]
        
        logger.info(f"Fallback detected: {detected_lang} (confidence: {confidence:.2f})")
        
        return LanguageDetectionResult(
            language=detected_lang,
            confidence=confidence,
            alternatives=alternatives
        )
    
    def _score_yoruba(self, text: str) -> float:
        """Score text for Yoruba language indicators"""
        score = 0.0
        
        # Yoruba-specific characters
        yoruba_chars = ['ṣ', 'ẹ', 'ọ', 'ń', 'ǹ', 'ḿ']
        score += sum(5 for char in yoruba_chars if char in text)
        
        # Common Yoruba words
        yoruba_words = [
            'ṣe', 'ni', 'ti', 'naa', 'wa', 'ko', 'si', 'bi', 'je', 'lo',
            'bawo', 'nibo', 'nigbati', 'gbogbo', 'ati', 'fun', 'lati',
            'ẹni', 'ohun', 'nkan', 'ojo', 'ile', 'owo', 'ọmọ', 'baba'
        ]
        score += sum(3 for word in yoruba_words if word in text)
        
        # Yoruba question words
        yoruba_questions = ['bawo', 'nibo', 'nigbawo', 'kilode', 'tani']
        score += sum(5 for word in yoruba_questions if word in text)
        
        return score
    
    def _score_igbo(self, text: str) -> float:
        """Score text for Igbo language indicators"""
        score = 0.0
        
        # Igbo-specific characters
        igbo_chars = ['ị', 'ọ', 'ụ', 'ṅ', 'ṃ']
        score += sum(5 for char in igbo_chars if char in text)
        
        # Common Igbo words
        igbo_words = [
            'nke', 'na', 'ya', 'ka', 'ga', 'bu', 'nwere', 'oge', 'ụbọchị',
            'kedu', 'gini', 'ebee', 'mgbe', 'onye', 'ihe', 'aha', 'ego',
            'ụlọ', 'nwa', 'nna', 'nne', 'ọrụ', 'mmadụ', 'ụwa'
        ]
        score += sum(3 for word in igbo_words if word in text)
        
        # Igbo question words
        igbo_questions = ['kedu', 'gini', 'ebee', 'mgbe', 'onye']
        score += sum(5 for word in igbo_questions if word in text)
        
        return score
    
    def _score_hausa(self, text: str) -> float:
        """Score text for Hausa language indicators"""
        score = 0.0
        
        # Hausa-specific characters (with diacritics)
        hausa_chars = ['ƙ', 'ɓ', 'ɗ', 'ƴ']
        score += sum(5 for char in hausa_chars if char in text)
        
        # Common Hausa words
        hausa_words = [
            'da', 'na', 'ya', 'ta', 'ka', 'ba', 'ne', 'ce', 'ko', 'amma',
            'yaya', 'ina', 'lokacin', 'duk', 'don', 'wani', 'wannan',
            'mutum', 'gida', 'kudi', 'yaro', 'uba', 'uwa', 'aiki', 'duniya'
        ]
        score += sum(3 for word in hausa_words if word in text)
        
        # Hausa question words
        hausa_questions = ['yaya', 'ina', 'yaushe', 'me', 'wane', 'wace']
        score += sum(5 for word in hausa_questions if word in text)
        
        return score
    
    def _score_pidgin(self, text: str) -> float:
        """Score text for Nigerian Pidgin indicators"""
        score = 0.0
        
        # Common Pidgin words and phrases
        pidgin_words = [
            'wetin', 'dey', 'no', 'go', 'fit', 'make', 'don', 'wey', 'sef',
            'abeg', 'abi', 'shey', 'na', 'dem', 'una', 'pikin', 'wahala',
            'chop', 'yarn', 'sabi', 'comot', 'enter', 'carry', 'gist'
        ]
        score += sum(4 for word in pidgin_words if word in text)
        
        # Pidgin question words
        pidgin_questions = ['wetin', 'which', 'how', 'where', 'when', 'who']
        score += sum(5 for word in pidgin_questions if word in text)
        
        # Pidgin-specific patterns
        pidgin_patterns = ['no be', 'na so', 'e dey', 'i go', 'make i']
        score += sum(6 for pattern in pidgin_patterns if pattern in text)
        
        return score
    
    def _score_english(self, text: str) -> float:
        """Score text for English language indicators"""
        score = 1.0  # Base score for English (default)
        
        # Common English words
        english_words = [
            'the', 'is', 'are', 'was', 'were', 'have', 'has', 'had',
            'what', 'when', 'where', 'who', 'why', 'how', 'can', 'will',
            'would', 'should', 'could', 'this', 'that', 'these', 'those'
        ]
        score += sum(2 for word in english_words if f' {word} ' in f' {text} ')
        
        # English question words
        english_questions = ['what', 'when', 'where', 'who', 'why', 'how']
        score += sum(3 for word in english_questions if word in text)
        
        return score
    
    def should_switch_language(
        self,
        detected_language: str,
        current_language: str,
        confidence: float
    ) -> bool:
        """
        Determine if language should be switched
        
        Args:
            detected_language: Newly detected language
            current_language: Current conversation language
            confidence: Detection confidence score
            
        Returns:
            True if language should be switched
        """
        # Don't switch if languages are the same
        if detected_language == current_language:
            return False
        
        # Only switch if confidence is high enough
        if confidence < self.CONFIDENCE_THRESHOLD:
            logger.info(
                f"Not switching language: confidence {confidence:.2f} below threshold {self.CONFIDENCE_THRESHOLD}"
            )
            return False
        
        logger.info(
            f"Switching language from {current_language} to {detected_language} "
            f"(confidence: {confidence:.2f})"
        )
        return True
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get full language name from code
        
        Args:
            language_code: ISO language code
            
        Returns:
            Full language name
        """
        return self.SUPPORTED_LANGUAGES.get(language_code, 'Unknown')
    
    def is_supported(self, language_code: str) -> bool:
        """
        Check if language is supported
        
        Args:
            language_code: ISO language code
            
        Returns:
            True if language is supported
        """
        return language_code in self.SUPPORTED_LANGUAGES
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get all supported languages
        
        Returns:
            Dictionary of language codes to names
        """
        return self.SUPPORTED_LANGUAGES.copy()
    
    async def detect_from_audio(
        self,
        audio_data: bytes,
        preferred_language: Optional[str] = None
    ) -> LanguageDetectionResult:
        """
        Detect language directly from audio using Whisper
        
        Args:
            audio_data: Audio file bytes
            preferred_language: User's preferred language
            
        Returns:
            LanguageDetectionResult
        """
        try:
            # Use Whisper's language detection capability
            from ..clients.client_factory import get_client_factory
            
            factory = get_client_factory()
            whisper_client = factory.get_whisper_client()
            
            result = await whisper_client.detect_language(audio_data)
            
            detected_lang = result['language']
            confidence = result['confidence']
            
            # Validate and fallback if needed
            if detected_lang not in self.SUPPORTED_LANGUAGES:
                logger.warning(f"Whisper detected unsupported language: {detected_lang}")
                if preferred_language:
                    detected_lang = preferred_language
                else:
                    detected_lang = 'en'
                confidence = 0.5
            
            logger.info(f"Audio language detection: {detected_lang} (confidence: {confidence:.2f})")
            
            return LanguageDetectionResult(
                language=detected_lang,
                confidence=confidence,
                alternatives=[]
            )
            
        except Exception as e:
            logger.error(f"Audio language detection failed: {e}")
            # Fallback to preferred or default language
            fallback_lang = preferred_language or 'en'
            return LanguageDetectionResult(
                language=fallback_lang,
                confidence=0.5,
                alternatives=[]
            )
