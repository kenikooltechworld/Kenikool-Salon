from langdetect import detect, detect_langs, LangDetectException
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class LanguageDetector:
    """Language detection using langdetect"""

    SUPPORTED_LANGUAGES = ["en", "yo", "ig", "ha", "pcm"]
    
    LANGUAGE_NAMES = {
        "en": "English",
        "yo": "Yoruba",
        "ig": "Igbo",
        "ha": "Hausa",
        "pcm": "Nigerian Pidgin"
    }

    async def detect_language(
        self,
        text: str,
        fallback_language: str = "en"
    ) -> dict:
        """
        Detect language from text
        
        Args:
            text: Text to analyze
            fallback_language: Language to use if detection fails
            
        Returns:
            Dictionary with detected language and confidence
        """
        try:
            if not text or len(text.strip()) < 3:
                return {
                    "language": fallback_language,
                    "confidence": 0.0,
                    "alternatives": []
                }

            detected = detect(text)
            probabilities = detect_langs(text)

            # Get confidence score
            confidence = max([p.prob for p in probabilities]) if probabilities else 0.0

            # Build alternatives list
            alternatives = []
            for p in probabilities:
                lang_code = str(p).split(":")[0]
                prob = p.prob
                alternatives.append((lang_code, prob))

            return {
                "language": detected,
                "confidence": confidence,
                "alternatives": alternatives
            }

        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}, using fallback")
            return {
                "language": fallback_language,
                "confidence": 0.0,
                "alternatives": []
            }
        except Exception as e:
            logger.error(f"Unexpected error in language detection: {e}")
            return {
                "language": fallback_language,
                "confidence": 0.0,
                "alternatives": []
            }

    async def get_supported_languages(self) -> dict:
        """Get supported languages"""
        return self.LANGUAGE_NAMES

    def is_supported(self, language: str) -> bool:
        """Check if language is supported"""
        return language in self.SUPPORTED_LANGUAGES
