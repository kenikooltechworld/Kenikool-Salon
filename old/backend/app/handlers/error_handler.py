"""
Comprehensive Error Handler for Voice Assistant
Handles all types of errors with appropriate recovery strategies
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Types of errors that can occur"""
    SPEECH_RECOGNITION = "speech_recognition"
    LANGUAGE_DETECTION = "language_detection"
    INTENT_RECOGNITION = "intent_recognition"
    ACTION_EXECUTION = "action_execution"
    DOCKER_CONTAINER = "docker_container"
    NETWORK = "network"
    VALIDATION = "validation"
    PERMISSION = "permission"
    RESOURCE_NOT_FOUND = "resource_not_found"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VoiceAssistantError(Exception):
    """Base exception for voice assistant errors"""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recoverable: bool = True,
        user_message: Optional[str] = None,
        suggested_action: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.severity = severity
        self.recoverable = recoverable
        self.user_message = user_message or message
        self.suggested_action = suggested_action
        self.original_error = original_error


class ErrorHandler:
    """Comprehensive error handler for voice assistant"""
    
    # Error messages by type and language
    ERROR_MESSAGES = {
        'en': {
            ErrorType.SPEECH_RECOGNITION: {
                'low_quality': "I couldn't hear you clearly. Please speak closer to the microphone.",
                'no_audio': "I didn't detect any audio. Please try speaking again.",
                'timeout': "The audio took too long to process. Please try again.",
                'general': "I had trouble understanding the audio. Please try again."
            },
            ErrorType.LANGUAGE_DETECTION: {
                'low_confidence': "I'm not sure which language you're speaking. Please try again.",
                'unsupported': "I don't support that language yet. Please use English, Yoruba, Igbo, Hausa, or Pidgin.",
                'general': "I had trouble detecting the language. Please try again."
            },
            ErrorType.INTENT_RECOGNITION: {
                'ambiguous': "I'm not sure what you want to do. Could you be more specific?",
                'unknown': "I didn't understand that command. Say 'help' to see what I can do.",
                'missing_info': "I need more information. {details}",
                'general': "I didn't understand that. Please try rephrasing."
            },
            ErrorType.ACTION_EXECUTION: {
                'permission': "You don't have permission to do that.",
                'not_found': "{resource} not found. Please check and try again.",
                'validation': "Invalid information: {details}",
                'conflict': "That conflicts with existing data: {details}",
                'general': "I couldn't complete that action. {details}"
            },
            ErrorType.DOCKER_CONTAINER: {
                'unavailable': "The AI service is temporarily unavailable. Switching to text mode.",
                'timeout': "The AI service is taking too long. Please try again.",
                'restart': "Restarting AI service. Please wait a moment.",
                'general': "AI service error. Please try again later."
            },
            ErrorType.NETWORK: {
                'connection': "Network connection lost. Please check your connection.",
                'timeout': "Request timed out. Please try again.",
                'general': "Network error occurred. Please try again."
            },
            ErrorType.TIMEOUT: {
                'general': "That took too long. Please try again."
            },
            ErrorType.UNKNOWN: {
                'general': "An unexpected error occurred. Please try again."
            }
        },
        'yo': {
            ErrorType.SPEECH_RECOGNITION: {
                'low_quality': "Mi o gbọ ọ daradara. Jọwọ sọ sunmọ microphone.",
                'no_audio': "Mi o gbọ ohun kankan. Jọwọ gbiyanju lẹẹkansi.",
                'timeout': "Ohun naa gba akoko pipẹ. Jọwọ gbiyanju lẹẹkansi.",
                'general': "Mo ni wahala lati loye ohun naa. Jọwọ gbiyanju lẹẹkansi."
            },
            ErrorType.LANGUAGE_DETECTION: {
                'low_confidence': "Mi o mọ ede ti o nsọ. Jọwọ gbiyanju lẹẹkansi.",
                'unsupported': "Mi o ṣe atilẹyin ede yẹn. Jọwọ lo English, Yoruba, Igbo, Hausa, tabi Pidgin.",
                'general': "Mo ni wahala lati mọ ede naa. Jọwọ gbiyanju lẹẹkansi."
            },
            ErrorType.INTENT_RECOGNITION: {
                'ambiguous': "Mi o mọ ohun ti o fẹ ṣe. Ṣe o le sọ ni kedere?",
                'unknown': "Mi o loye aṣẹ yẹn. Sọ 'iranlọwọ' lati wo ohun ti mo le ṣe.",
                'missing_info': "Mo nilo alaye diẹ sii. {details}",
                'general': "Mi o loye iyẹn. Jọwọ sọ ọ ni ọna miiran."
            },
            ErrorType.ACTION_EXECUTION: {
                'permission': "O ko ni aṣẹ lati ṣe iyẹn.",
                'not_found': "A ko ri {resource}. Jọwọ ṣayẹwo ki o gbiyanju lẹẹkansi.",
                'validation': "Alaye ti ko tọ: {details}",
                'conflict': "Iyẹn ko baamu pẹlu data ti o wa: {details}",
                'general': "Mi o le pari iṣẹ yẹn. {details}"
            },
            ErrorType.DOCKER_CONTAINER: {
                'unavailable': "Iṣẹ AI ko wa lọwọlọwọ. N yipada si ọna kikọ.",
                'timeout': "Iṣẹ AI gba akoko pipẹ. Jọwọ gbiyanju lẹẹkansi.",
                'restart': "N tun bẹrẹ iṣẹ AI. Jọwọ duro diẹ.",
                'general': "Aṣiṣe iṣẹ AI. Jọwọ gbiyanju nigbamii."
            },
            ErrorType.UNKNOWN: {
                'general': "Aṣiṣe ti a ko reti ṣẹlẹ. Jọwọ gbiyanju lẹẹkansi."
            }
        },
        'ig': {
            ErrorType.SPEECH_RECOGNITION: {
                'low_quality': "Anụghị m gị nke ọma. Biko kwuo nso na microphone.",
                'no_audio': "Anụghị m ihe ọ bụla. Biko nwaa ọzọ.",
                'timeout': "O were ogologo oge. Biko nwaa ọzọ.",
                'general': "Enwere m nsogbu ịghọta ụda ahụ. Biko nwaa ọzọ."
            },
            ErrorType.LANGUAGE_DETECTION: {
                'low_confidence': "Amaghị m asụsụ ị na-asụ. Biko nwaa ọzọ.",
                'unsupported': "Anaghị m akwado asụsụ ahụ. Biko jiri English, Yoruba, Igbo, Hausa, ma ọ bụ Pidgin.",
                'general': "Enwere m nsogbu ịchọpụta asụsụ ahụ. Biko nwaa ọzọ."
            },
            ErrorType.INTENT_RECOGNITION: {
                'ambiguous': "Amaghị m ihe ị chọrọ ime. Ị nwere ike ịkọwa ya?",
                'unknown': "Aghọtaghị m iwu ahụ. Kwuo 'enyemaka' ịhụ ihe m nwere ike ime.",
                'missing_info': "Achọrọ m ozi ndị ọzọ. {details}",
                'general': "Aghọtaghị m nke ahụ. Biko kwuo ya ọzọ."
            },
            ErrorType.ACTION_EXECUTION: {
                'permission': "I nweghị ikike ime nke ahụ.",
                'not_found': "Achọtaghị {resource}. Biko lelee ma nwaa ọzọ.",
                'validation': "Ozi ezighi ezi: {details}",
                'conflict': "Nke ahụ na-emegide data dị: {details}",
                'general': "Enweghị m ike imecha ọrụ ahụ. {details}"
            },
            ErrorType.DOCKER_CONTAINER: {
                'unavailable': "Ọrụ AI adịghị ugbu a. Na-agbanwe gaa n'ụdị ederede.",
                'timeout': "Ọrụ AI na-ewe ogologo oge. Biko nwaa ọzọ.",
                'restart': "Na-amalite ọrụ AI ọzọ. Biko chere ntakịrị.",
                'general': "Njehie ọrụ AI. Biko nwaa mgbe e mesịrị."
            },
            ErrorType.UNKNOWN: {
                'general': "Njehie a na-atụghị anya ya mere. Biko nwaa ọzọ."
            }
        },
        'ha': {
            ErrorType.SPEECH_RECOGNITION: {
                'low_quality': "Ban ji ku sosai ba. Don Allah ku yi magana kusa da microphone.",
                'no_audio': "Ban ji komai ba. Don Allah sake gwadawa.",
                'timeout': "Ya dauki lokaci mai tsawo. Don Allah sake gwadawa.",
                'general': "Ina da matsala wajen fahimtar sautin. Don Allah sake gwadawa."
            },
            ErrorType.LANGUAGE_DETECTION: {
                'low_confidence': "Ban san yaren da kuke magana ba. Don Allah sake gwadawa.",
                'unsupported': "Ba na goyan bayan wannan yare ba. Don Allah yi amfani da English, Yoruba, Igbo, Hausa, ko Pidgin.",
                'general': "Ina da matsala wajen gano yaren. Don Allah sake gwadawa."
            },
            ErrorType.INTENT_RECOGNITION: {
                'ambiguous': "Ban san abin da kuke son yi ba. Za ku iya bayyana?",
                'unknown': "Ban fahimci wannan umarnin ba. Ku ce 'taimako' don ganin abin da zan iya yi.",
                'missing_info': "Ina buƙatar ƙarin bayani. {details}",
                'general': "Ban fahimci wannan ba. Don Allah sake faɗi."
            },
            ErrorType.ACTION_EXECUTION: {
                'permission': "Ba ku da izinin yin wannan.",
                'not_found': "Ba a sami {resource} ba. Don Allah duba kuma sake gwadawa.",
                'validation': "Bayanan ba daidai ba ne: {details}",
                'conflict': "Wannan ya sabawa bayanan da ke akwai: {details}",
                'general': "Ba zan iya kammala wannan aikin ba. {details}"
            },
            ErrorType.DOCKER_CONTAINER: {
                'unavailable': "Sabis na AI ba ya samuwa a yanzu. Yana canzawa zuwa yanayin rubutu.",
                'timeout': "Sabis na AI yana ɗaukar lokaci mai tsawo. Don Allah sake gwadawa.",
                'restart': "Ana sake kunna sabis na AI. Don Allah jira kaɗan.",
                'general': "Kuskuren sabis na AI. Don Allah sake gwadawa daga baya."
            },
            ErrorType.UNKNOWN: {
                'general': "An sami kuskure da ba a zata ba. Don Allah sake gwadawa."
            }
        },
        'pcm': {
            ErrorType.SPEECH_RECOGNITION: {
                'low_quality': "I no hear you well well. Abeg talk near the microphone.",
                'no_audio': "I no hear anything. Abeg try again.",
                'timeout': "E take too long. Abeg try again.",
                'general': "I get problem to understand the sound. Abeg try again."
            },
            ErrorType.LANGUAGE_DETECTION: {
                'low_confidence': "I no know which language you dey speak. Abeg try again.",
                'unsupported': "I no dey support that language. Abeg use English, Yoruba, Igbo, Hausa, or Pidgin.",
                'general': "I get problem to detect the language. Abeg try again."
            },
            ErrorType.INTENT_RECOGNITION: {
                'ambiguous': "I no sure wetin you wan do. You fit explain am?",
                'unknown': "I no understand that command. Talk 'help' make you see wetin I fit do.",
                'missing_info': "I need more information. {details}",
                'general': "I no understand that one. Abeg talk am again."
            },
            ErrorType.ACTION_EXECUTION: {
                'permission': "You no get permission to do that.",
                'not_found': "{resource} no dey. Abeg check and try again.",
                'validation': "Wrong information: {details}",
                'conflict': "That one dey clash with existing data: {details}",
                'general': "I no fit complete that action. {details}"
            },
            ErrorType.DOCKER_CONTAINER: {
                'unavailable': "AI service no dey available now. Dey switch to text mode.",
                'timeout': "AI service dey take too long. Abeg try again.",
                'restart': "Dey restart AI service. Abeg wait small.",
                'general': "AI service get error. Abeg try again later."
            },
            ErrorType.UNKNOWN: {
                'general': "Something wey we no expect happen. Abeg try again."
            }
        }
    }

    
    @classmethod
    def handle_speech_recognition_error(
        cls,
        error: Exception,
        language: str = 'en'
    ) -> VoiceAssistantError:
        """Handle speech recognition errors"""
        error_str = str(error).lower()
        
        if 'timeout' in error_str:
            subtype = 'timeout'
        elif 'no audio' in error_str or 'silence' in error_str:
            subtype = 'no_audio'
        elif 'quality' in error_str or 'noise' in error_str:
            subtype = 'low_quality'
        else:
            subtype = 'general'
        
        messages = cls.ERROR_MESSAGES.get(language, cls.ERROR_MESSAGES['en'])
        user_message = messages[ErrorType.SPEECH_RECOGNITION].get(subtype)
        
        return VoiceAssistantError(
            message=f"Speech recognition failed: {error}",
            error_type=ErrorType.SPEECH_RECOGNITION,
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            user_message=user_message,
            suggested_action="Please try speaking again, closer to the microphone.",
            original_error=error
        )
    
    @classmethod
    def handle_language_detection_error(
        cls,
        error: Exception,
        language: str = 'en'
    ) -> VoiceAssistantError:
        """Handle language detection errors"""
        error_str = str(error).lower()
        
        if 'confidence' in error_str or 'uncertain' in error_str:
            subtype = 'low_confidence'
        elif 'unsupported' in error_str or 'not supported' in error_str:
            subtype = 'unsupported'
        else:
            subtype = 'general'
        
        messages = cls.ERROR_MESSAGES.get(language, cls.ERROR_MESSAGES['en'])
        user_message = messages[ErrorType.LANGUAGE_DETECTION].get(subtype)
        
        return VoiceAssistantError(
            message=f"Language detection failed: {error}",
            error_type=ErrorType.LANGUAGE_DETECTION,
            severity=ErrorSeverity.LOW,
            recoverable=True,
            user_message=user_message,
            suggested_action="Please try again in a supported language.",
            original_error=error
        )
    
    @classmethod
    def handle_intent_recognition_error(
        cls,
        error: Exception,
        language: str = 'en',
        details: Optional[str] = None
    ) -> VoiceAssistantError:
        """Handle intent recognition errors"""
        error_str = str(error).lower()
        
        if 'ambiguous' in error_str or 'unclear' in error_str:
            subtype = 'ambiguous'
        elif 'unknown' in error_str or 'not recognized' in error_str:
            subtype = 'unknown'
        elif 'missing' in error_str or 'required' in error_str:
            subtype = 'missing_info'
        else:
            subtype = 'general'
        
        messages = cls.ERROR_MESSAGES.get(language, cls.ERROR_MESSAGES['en'])
        user_message = messages[ErrorType.INTENT_RECOGNITION].get(subtype)
        
        if details and '{details}' in user_message:
            user_message = user_message.format(details=details)
        
        return VoiceAssistantError(
            message=f"Intent recognition failed: {error}",
            error_type=ErrorType.INTENT_RECOGNITION,
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            user_message=user_message,
            suggested_action="Please rephrase your command or say 'help' for assistance.",
            original_error=error
        )
    
    @classmethod
    def handle_action_execution_error(
        cls,
        error: Exception,
        language: str = 'en',
        resource: Optional[str] = None,
        details: Optional[str] = None
    ) -> VoiceAssistantError:
        """Handle action execution errors"""
        error_str = str(error).lower()
        
        if 'permission' in error_str or 'unauthorized' in error_str:
            subtype = 'permission'
            severity = ErrorSeverity.HIGH
        elif 'not found' in error_str or 'does not exist' in error_str:
            subtype = 'not_found'
            severity = ErrorSeverity.MEDIUM
        elif 'invalid' in error_str or 'validation' in error_str:
            subtype = 'validation'
            severity = ErrorSeverity.LOW
        elif 'conflict' in error_str or 'already exists' in error_str:
            subtype = 'conflict'
            severity = ErrorSeverity.MEDIUM
        else:
            subtype = 'general'
            severity = ErrorSeverity.MEDIUM
        
        messages = cls.ERROR_MESSAGES.get(language, cls.ERROR_MESSAGES['en'])
        user_message = messages[ErrorType.ACTION_EXECUTION].get(subtype)
        
        if resource and '{resource}' in user_message:
            user_message = user_message.format(resource=resource)
        elif details and '{details}' in user_message:
            user_message = user_message.format(details=details)
        
        return VoiceAssistantError(
            message=f"Action execution failed: {error}",
            error_type=ErrorType.ACTION_EXECUTION,
            severity=severity,
            recoverable=True,
            user_message=user_message,
            suggested_action="Please check your input and try again.",
            original_error=error
        )
    
    @classmethod
    def handle_docker_container_error(
        cls,
        error: Exception,
        language: str = 'en',
        container_name: Optional[str] = None
    ) -> VoiceAssistantError:
        """Handle Docker container errors"""
        error_str = str(error).lower()
        
        if 'timeout' in error_str:
            subtype = 'timeout'
            severity = ErrorSeverity.HIGH
        elif 'unavailable' in error_str or 'connection' in error_str:
            subtype = 'unavailable'
            severity = ErrorSeverity.CRITICAL
        elif 'restart' in error_str:
            subtype = 'restart'
            severity = ErrorSeverity.HIGH
        else:
            subtype = 'general'
            severity = ErrorSeverity.HIGH
        
        messages = cls.ERROR_MESSAGES.get(language, cls.ERROR_MESSAGES['en'])
        user_message = messages[ErrorType.DOCKER_CONTAINER].get(subtype)
        
        return VoiceAssistantError(
            message=f"Docker container error ({container_name}): {error}",
            error_type=ErrorType.DOCKER_CONTAINER,
            severity=severity,
            recoverable=subtype != 'unavailable',
            user_message=user_message,
            suggested_action="Please wait a moment and try again.",
            original_error=error
        )
    
    @classmethod
    def handle_network_error(
        cls,
        error: Exception,
        language: str = 'en'
    ) -> VoiceAssistantError:
        """Handle network errors"""
        error_str = str(error).lower()
        
        if 'timeout' in error_str:
            subtype = 'timeout'
        elif 'connection' in error_str:
            subtype = 'connection'
        else:
            subtype = 'general'
        
        messages = cls.ERROR_MESSAGES.get(language, cls.ERROR_MESSAGES['en'])
        user_message = messages[ErrorType.NETWORK].get(subtype)
        
        return VoiceAssistantError(
            message=f"Network error: {error}",
            error_type=ErrorType.NETWORK,
            severity=ErrorSeverity.HIGH,
            recoverable=True,
            user_message=user_message,
            suggested_action="Please check your network connection and try again.",
            original_error=error
        )
    
    @classmethod
    def handle_timeout_error(
        cls,
        error: Exception,
        language: str = 'en',
        operation: Optional[str] = None
    ) -> VoiceAssistantError:
        """Handle timeout errors"""
        messages = cls.ERROR_MESSAGES.get(language, cls.ERROR_MESSAGES['en'])
        user_message = messages[ErrorType.TIMEOUT]['general']
        
        return VoiceAssistantError(
            message=f"Timeout error ({operation}): {error}",
            error_type=ErrorType.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            user_message=user_message,
            suggested_action="Please try again.",
            original_error=error
        )
    
    @classmethod
    def handle_unknown_error(
        cls,
        error: Exception,
        language: str = 'en'
    ) -> VoiceAssistantError:
        """Handle unknown errors"""
        messages = cls.ERROR_MESSAGES.get(language, cls.ERROR_MESSAGES['en'])
        user_message = messages[ErrorType.UNKNOWN]['general']
        
        logger.error(f"Unknown error occurred: {error}", exc_info=True)
        
        return VoiceAssistantError(
            message=f"Unknown error: {error}",
            error_type=ErrorType.UNKNOWN,
            severity=ErrorSeverity.HIGH,
            recoverable=True,
            user_message=user_message,
            suggested_action="Please try again or contact support if the problem persists.",
            original_error=error
        )
    
    @classmethod
    def get_recovery_strategy(cls, error: VoiceAssistantError) -> Dict[str, Any]:
        """
        Get recovery strategy for an error
        
        Args:
            error: VoiceAssistantError instance
            
        Returns:
            Recovery strategy dict
        """
        strategies = {
            ErrorType.SPEECH_RECOGNITION: {
                'retry': True,
                'max_retries': 3,
                'fallback': 'text_input',
                'user_action': 'adjust_microphone'
            },
            ErrorType.LANGUAGE_DETECTION: {
                'retry': True,
                'max_retries': 2,
                'fallback': 'default_language',
                'user_action': 'specify_language'
            },
            ErrorType.INTENT_RECOGNITION: {
                'retry': True,
                'max_retries': 2,
                'fallback': 'clarification_prompt',
                'user_action': 'rephrase'
            },
            ErrorType.ACTION_EXECUTION: {
                'retry': False,
                'max_retries': 1,
                'fallback': 'error_message',
                'user_action': 'correct_input'
            },
            ErrorType.DOCKER_CONTAINER: {
                'retry': True,
                'max_retries': 3,
                'fallback': 'text_mode',
                'user_action': 'wait_and_retry'
            },
            ErrorType.NETWORK: {
                'retry': True,
                'max_retries': 3,
                'fallback': 'offline_mode',
                'user_action': 'check_connection'
            },
            ErrorType.TIMEOUT: {
                'retry': True,
                'max_retries': 2,
                'fallback': 'reduce_complexity',
                'user_action': 'simplify_request'
            }
        }
        
        return strategies.get(error.error_type, {
            'retry': True,
            'max_retries': 1,
            'fallback': 'error_message',
            'user_action': 'try_again'
        })
