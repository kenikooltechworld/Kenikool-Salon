"""Voice assistant clients package"""

from app.clients.whisper_client import WhisperClient
from app.clients.language_detector import LanguageDetector
from app.clients.nlu_handler import NLUHandler
from app.clients.tts_client import TTSClient

__all__ = [
    "WhisperClient",
    "LanguageDetector",
    "NLUHandler",
    "TTSClient"
]
