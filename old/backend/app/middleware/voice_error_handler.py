"""
Voice Assistant Error Handling Middleware
Centralized error handling for voice command processing
"""

import logging
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import traceback

logger = logging.getLogger(__name__)


class VoiceErrorType:
    """Error type constants"""
    AUDIO_PROCESSING_ERROR = "audio_processing_error"
    STT_ERROR = "stt_error"
    LANGUAGE_DETECTION_ERROR = "language_detection_error"
    NLU_ERROR = "nlu_error"
    ACTION_EXECUTION_ERROR = "action_execution_error"
    TTS_ERROR = "tts_error"
    CONTEXT_ERROR = "context_error"
    DOCKER_CONTAINER_ERROR = "docker_container_error"
    VALIDATION_ERROR = "validation_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"


class VoiceAssistantException(Exception):
    """Base exception for voice assistant errors"""
    
    def __init__(
        self,
        message: str,
        error_type: str = VoiceErrorType.UNKNOWN_ERROR,
        details: Dict[str, Any] = None,
        recoverable: bool = True
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        self.recoverable = recoverable


class AudioProcessingError(VoiceAssistantException):
    """Audio processing errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_type=VoiceErrorType.AUDIO_PROCESSING_ERROR,
            details=details,
            recoverable=True
        )


class STTError(VoiceAssistantException):
    """Speech-to-text errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_type=VoiceErrorType.STT_ERROR,
            details=details,
            recoverable=True
        )


class NLUError(VoiceAssistantException):
    """Natural language understanding errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_type=VoiceErrorType.NLU_ERROR,
            details=details,
            recoverable=True
        )


class ActionExecutionError(VoiceAssistantException):
    """Action execution errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_type=VoiceErrorType.ACTION_EXECUTION_ERROR,
            details=details,
            recoverable=True
        )


class DockerContainerError(VoiceAssistantException):
    """Docker container communication errors"""
    def __init__(self, message: str, container: str, details: Dict[str, Any] = None):
        details = details or {}
        details['container'] = container
        super().__init__(
            message=message,
            error_type=VoiceErrorType.DOCKER_CONTAINER_ERROR,
            details=details,
            recoverable=True
        )


async def voice_error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to handle voice assistant errors
    
    Args:
        request: FastAPI request
        call_next: Next middleware/handler
        
    Returns:
        Response with error handling
    """
    try:
        response = await call_next(request)
        return response
        
    except VoiceAssistantException as e:
        logger.error(
            f"Voice assistant error: {e.error_type} - {e.message}",
            extra={'details': e.details}
        )
        
        return JSONResponse(
            status_code=400 if e.recoverable else 500,
            content={
                'error': e.error_type,
                'message': e.message,
                'details': e.details,
                'recoverable': e.recoverable
            }
        )
        
    except Exception as e:
        logger.error(
            f"Unexpected error in voice assistant: {str(e)}",
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                'error': VoiceErrorType.UNKNOWN_ERROR,
                'message': 'An unexpected error occurred',
                'details': {'error': str(e)},
                'recoverable': False
            }
        )


def get_error_message(error_type: str, language: str = 'en') -> str:
    """
    Get user-friendly error message in specified language
    
    Args:
        error_type: Type of error
        language: Language code
        
    Returns:
        Localized error message
    """
    messages = {
        VoiceErrorType.AUDIO_PROCESSING_ERROR: {
            'en': "I couldn't process the audio. Please try recording again.",
            'yo': "Mi o le ṣe audio naa. Jowo gbiyanju lati gbasilẹ lẹẹkansi.",
            'ig': "Enweghị m ike ịhazi ụda ahụ. Biko nwaa ịdekọ ọzọ.",
            'ha': "Ban iya sarrafa sautin. Da fatan a sake yin rikodin.",
            'pcm': "I no fit process di audio. Abeg try record again."
        },
        VoiceErrorType.STT_ERROR: {
            'en': "I couldn't understand what you said. Please speak clearly and try again.",
            'yo': "Mi o le loye ohun ti o sọ. Jowo sọ ni kedere ki o si gbiyanju lẹẹkansi.",
            'ig': "Aghọtaghị m ihe ị kwuru. Biko kwuo nke ọma ma nwaa ọzọ.",
            'ha': "Ban fahimci abin da kuka ce. Da fatan a yi magana a fili kuma a sake gwadawa.",
            'pcm': "I no understand wetin you talk. Abeg talk well and try again."
        },
        VoiceErrorType.NLU_ERROR: {
            'en': "I didn't understand your request. Could you rephrase it?",
            'yo': "Mi o loye ibeere rẹ. Ṣe o le tun sọ ni ọna miiran?",
            'ig': "Aghọtaghị m arịrịọ gị. Ị nwere ike ikwughachi ya?",
            'ha': "Ban fahimci bukatarka. Za ku iya sake faɗi shi?",
            'pcm': "I no understand your request. You fit talk am another way?"
        },
        VoiceErrorType.ACTION_EXECUTION_ERROR: {
            'en': "I couldn't complete that action. Please try again or contact support.",
            'yo': "Mi o le pari iṣẹ naa. Jowo gbiyanju lẹẹkansi tabi kan si atilẹyin.",
            'ig': "Enweghị m ike ịmecha omume ahụ. Biko nwaa ọzọ ma ọ bụ kpọtụrụ nkwado.",
            'ha': "Ban iya kammala wannan aikin. Da fatan a sake gwadawa ko kuma ku tuntubi tallafi.",
            'pcm': "I no fit complete dat action. Abeg try again or call support."
        },
        VoiceErrorType.DOCKER_CONTAINER_ERROR: {
            'en': "The AI service is temporarily unavailable. Please try again in a moment.",
            'yo': "Iṣẹ AI ko wa fun igba diẹ. Jowo gbiyanju lẹẹkansi ni akoko diẹ.",
            'ig': "Ọrụ AI adịghị ugbu a. Biko nwaa ọzọ n'oge na-adịghị anya.",
            'ha': "Sabis na AI ba ya samuwa a yanzu. Da fatan a sake gwadawa nan da ɗan lokaci.",
            'pcm': "Di AI service no dey available now. Abeg try again small time."
        },
        VoiceErrorType.TIMEOUT_ERROR: {
            'en': "The request took too long. Please try again.",
            'yo': "Ibeere naa gba akoko pupọ. Jowo gbiyanju lẹẹkansi.",
            'ig': "Arịrịọ ahụ were ogologo oge. Biko nwaa ọzọ.",
            'ha': "Bukatarka ta ɗauki lokaci mai tsawo. Da fatan a sake gwadawa.",
            'pcm': "Di request take too long. Abeg try again."
        }
    }
    
    error_messages = messages.get(error_type, messages[VoiceErrorType.UNKNOWN_ERROR])
    return error_messages.get(language, error_messages['en'])


class ErrorRecoveryStrategy:
    """Strategies for recovering from errors"""
    
    @staticmethod
    async def retry_with_fallback(
        primary_func: Callable,
        fallback_func: Callable,
        max_retries: int = 2
    ) -> Any:
        """
        Retry primary function, fall back to alternative if it fails
        
        Args:
            primary_func: Primary function to try
            fallback_func: Fallback function if primary fails
            max_retries: Maximum retry attempts
            
        Returns:
            Result from primary or fallback function
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await primary_func()
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
        
        # Try fallback
        try:
            logger.info("Trying fallback strategy")
            return await fallback_func()
        except Exception as e:
            logger.error(f"Fallback also failed: {e}")
            raise last_error
