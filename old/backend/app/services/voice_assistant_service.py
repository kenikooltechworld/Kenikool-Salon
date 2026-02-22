import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.clients.whisper_client import WhisperClient
from app.clients.language_detector import LanguageDetector
from app.clients.nlu_handler import NLUHandler
from app.clients.tts_client import TTSClient
from app.services.context_manager import ContextManager
from app.services.action_executor import ActionExecutor
from app.services.privacy_security_service import PrivacySecurityService
from app.services.performance_monitoring_service import PerformanceMonitoringService
from app.services.voice_shortcuts_service import VoiceShortcutsService
from app.services.help_tutorial_service import HelpTutorialService
from app.services.pattern_analyzer import PatternAnalyzer
from app.services.prediction_engine import PredictionEngine
from app.services.suggestion_generator import SuggestionGenerator
from app.services.insight_generator import InsightGenerator
from app.services.proactive_alerter import ProactiveAlerter
from app.services.learning_model import LearningModel
from app.services.ai_voice_commands import AIVoiceCommands
from app.schemas.voice import (
    VoiceResponse, ActionResult, ConversationContext, 
    ConversationTurn, Intent, TranscriptionResult,
    LanguageDetectionResult, NLUResult
)

logger = logging.getLogger(__name__)


class VoiceAssistantService:
    """Main voice assistant orchestrator"""

    def __init__(self):
        """Initialize voice assistant service"""
        self.whisper_client = None
        self.language_detector = None
        self.nlu_handler = None
        self.tts_client = None
        self.context_manager = None
        self.action_executor = None
        self.privacy_security = None
        self.performance_monitoring = None
        self.voice_shortcuts = None
        self.help_tutorial = None
        self.pattern_analyzer = None
        self.prediction_engine = None
        self.suggestion_generator = None
        self.insight_generator = None
        self.proactive_alerter = None
        self.learning_model = None
        self.ai_voice_commands = None
        self._initialize()

    def _initialize(self):
        """Initialize all components"""
        try:
            logger.info("Initializing Voice Assistant Service...")
            self.whisper_client = WhisperClient(model_name="base")
            self.language_detector = LanguageDetector()
            self.nlu_handler = NLUHandler()
            self.tts_client = TTSClient()
            self.context_manager = ContextManager()
            self.privacy_security = PrivacySecurityService()
            self.performance_monitoring = PerformanceMonitoringService()
            self.voice_shortcuts = VoiceShortcutsService()
            self.help_tutorial = HelpTutorialService()
            
            # Initialize AI learning services
            self.pattern_analyzer = PatternAnalyzer()
            self.prediction_engine = PredictionEngine()
            self.suggestion_generator = SuggestionGenerator()
            self.insight_generator = InsightGenerator()
            self.proactive_alerter = ProactiveAlerter()
            self.learning_model = LearningModel()
            
            # Initialize AI voice commands with all services
            self.ai_voice_commands = AIVoiceCommands(
                pattern_analyzer=self.pattern_analyzer,
                prediction_engine=self.prediction_engine,
                suggestion_generator=self.suggestion_generator,
                insight_generator=self.insight_generator,
                proactive_alerter=self.proactive_alerter
            )
            
            # Initialize action executor with AI commands
            self.action_executor = ActionExecutor(ai_commands=self.ai_voice_commands)
            
            logger.info("Voice Assistant Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Voice Assistant Service: {e}")
            raise

    async def process_voice_command(
        self,
        audio_data: bytes,
        user_id: str,
        session_id: str,
        preferred_language: Optional[str] = None
    ) -> VoiceResponse:
        """
        Process complete voice command pipeline
        
        Args:
            audio_data: Audio bytes from microphone
            user_id: User ID
            session_id: Conversation session ID
            preferred_language: User's preferred language
            
        Returns:
            Complete voice response
        """
        try:
            # Step 1: Speech-to-Text
            transcript = await self.whisper_client.transcribe(audio_data)
            logger.info(f"Transcribed: {transcript}")

            # Step 2: Language Detection
            lang_result = await self.language_detector.detect_language(
                transcript,
                fallback_language=preferred_language or "en"
            )
            detected_language = lang_result["language"]
            logger.info(f"Detected language: {detected_language}")

            # Step 3: Natural Language Understanding
            nlu_result = await self.nlu_handler.understand(
                transcript,
                language=detected_language
            )
            intent = nlu_result["intent"]
            entities = nlu_result["entities"]
            logger.info(f"Detected intent: {intent}")

            # Step 4: Get or create conversation context
            context = await self._get_or_create_context(
                session_id, user_id, detected_language
            )

            # Step 5: Execute action
            action_result = await self._execute_action(
                intent, entities, user_id, context, command_text=transcript
            )

            # Step 6: Generate response
            response_text = self._generate_response(
                intent, action_result, detected_language
            )

            # Step 7: Text-to-Speech
            audio_url = None
            try:
                audio_data = await self.tts_client.synthesize(
                    response_text,
                    language=detected_language
                )
                # In production, save to storage and get URL
                audio_url = f"/api/voice/audio/{uuid.uuid4()}"
            except Exception as e:
                logger.warning(f"TTS failed: {e}")

            # Step 8: Update context
            await self._update_context(
                context, intent, entities, response_text
            )

            return VoiceResponse(
                transcript=transcript,
                detected_language=detected_language,
                intent=intent,
                response_text=response_text,
                audio_url=audio_url,
                action_result=action_result,
                requires_followup=nlu_result.get("requires_clarification", False)
            )

        except Exception as e:
            logger.error(f"Voice command processing failed: {e}")
            return VoiceResponse(
                transcript="",
                detected_language=preferred_language or "en",
                intent=Intent.UNKNOWN,
                response_text="Sorry, I encountered an error processing your request.",
                audio_url=None,
                action_result=ActionResult(
                    success=False,
                    message="Error processing voice command",
                    error=str(e)
                ),
                requires_followup=True
            )

    async def _get_or_create_context(
        self,
        session_id: str,
        user_id: str,
        language: str
    ) -> ConversationContext:
        """Get existing context or create new one"""
        context = await self.context_manager.get_context(session_id)
        
        if context:
            return context

        # Create new context
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            language=language,
            history=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return context

    async def _update_context(
        self,
        context: ConversationContext,
        intent: Intent,
        entities: Dict[str, Any],
        response: str
    ):
        """Update conversation context"""
        await self.context_manager.update_context(
            session_id=context.session_id,
            user_id=context.user_id,
            language=context.language,
            intent=intent,
            entities=entities,
            response=response
        )

    async def _execute_action(
        self,
        intent: Intent,
        entities: Dict[str, Any],
        user_id: str,
        context: ConversationContext,
        command_text: Optional[str] = None
    ) -> ActionResult:
        """Execute action based on intent using ActionExecutor"""
        try:
            return await self.action_executor.execute(
                intent=intent,
                entities=entities,
                user_id=user_id,
                context=context,
                command_text=command_text
            )
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return ActionResult(
                success=False,
                message="Failed to execute action",
                error=str(e)
            )

    def _generate_response(
        self,
        intent: Intent,
        action_result: ActionResult,
        language: str
    ) -> str:
        """Generate natural language response"""
        if not action_result.success:
            return action_result.error or "An error occurred"

        responses = {
            Intent.HELP: "Here are the available commands you can use.",
            Intent.SHOW_APPOINTMENTS: "Here are your upcoming appointments.",
            Intent.BOOK_APPOINTMENT: "I've booked your appointment.",
            Intent.CANCEL_APPOINTMENT: "I've cancelled your appointment.",
            Intent.SHOW_REVENUE: "Here's your revenue information.",
            Intent.CHECK_INVENTORY: "Here's your inventory status.",
        }

        return responses.get(intent, action_result.message)

    async def clear_context(self, session_id: str):
        """Clear conversation context"""
        await self.context_manager.clear_context(session_id)

    async def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """Get conversation context"""
        return await self.context_manager.get_context(session_id)
