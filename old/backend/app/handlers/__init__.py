"""
Voice Assistant Handlers
Handlers for different stages of voice command processing
"""

from .stt_handler import STTHandler
from .language_detector import LanguageDetector
from .nlu_handler import NLUHandler, IntentClassifier, EntityExtractor
from .context_manager import ContextManager
from .intent_patterns import IntentPatterns, INTENT_ACTION_MAP, INTENT_REQUIRED_ENTITIES
from .action_executor import ActionExecutor
from .tts_handler import TTSHandler
from .response_templates import ResponseTemplates

__all__ = [
    "STTHandler",
    "LanguageDetector",
    "NLUHandler",
    "IntentClassifier",
    "EntityExtractor",
    "ContextManager",
    "IntentPatterns",
    "INTENT_ACTION_MAP",
    "INTENT_REQUIRED_ENTITIES",
    "ActionExecutor",
    "TTSHandler",
    "ResponseTemplates",
]
