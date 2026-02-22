import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from app.services.voice_assistant_service import VoiceAssistantService
from app.schemas.voice import Intent


@pytest.fixture
def voice_service():
    """Create voice assistant service for testing"""
    with patch('app.services.voice_assistant_service.WhisperClient'), \
         patch('app.services.voice_assistant_service.LanguageDetector'), \
         patch('app.services.voice_assistant_service.NLUHandler'), \
         patch('app.services.voice_assistant_service.TTSClient'), \
         patch('app.services.voice_assistant_service.ContextManager'), \
         patch('app.services.voice_assistant_service.ActionExecutor'), \
         patch('app.services.voice_assistant_service.PrivacySecurityService'), \
         patch('app.services.voice_assistant_service.PerformanceMonitoringService'), \
         patch('app.services.voice_assistant_service.VoiceShortcutsService'), \
         patch('app.services.voice_assistant_service.HelpTutorialService'):
        service = VoiceAssistantService()
        
        # Mock all components
        service.whisper_client = AsyncMock()
        service.language_detector = AsyncMock()
        service.nlu_handler = AsyncMock()
        service.tts_client = AsyncMock()
        service.context_manager = AsyncMock()
        service.action_executor = AsyncMock()
        service.privacy_security = Mock()
        service.performance_monitoring = Mock()
        service.voice_shortcuts = AsyncMock()
        service.help_tutorial = Mock()
        
        return service


@pytest.mark.asyncio
async def test_complete_voice_pipeline_english(voice_service):
    """Test complete STT → Language Detection → NLU → Action → TTS flow"""
    # Setup mocks
    voice_service.whisper_client.transcribe = AsyncMock(return_value="book appointment for sarah")
    voice_service.language_detector.detect_language = AsyncMock(
        return_value={"language": "en", "confidence": 0.95}
    )
    voice_service.nlu_handler.understand = AsyncMock(
        return_value={
            "intent": Intent.BOOK_APPOINTMENT,
            "entities": {"PERSON": ["Sarah"]},
            "requires_clarification": False
        }
    )
    voice_service.action_executor.execute = AsyncMock(
        return_value=Mock(success=True, message="Booked appointment")
    )
    voice_service.tts_client.synthesize = AsyncMock(return_value=b"audio_data")
    voice_service.context_manager.get_context = AsyncMock(return_value=None)
    voice_service.context_manager.update_context = AsyncMock()

    # Execute pipeline
    response = await voice_service.process_voice_command(
        audio_data=b"audio_bytes",
        user_id="user123",
        session_id="session123",
        preferred_language="en"
    )

    # Verify pipeline
    assert response.transcript == "book appointment for sarah"
    assert response.detected_language == "en"
    assert response.intent == Intent.BOOK_APPOINTMENT
    assert response.action_result.success is True


@pytest.mark.asyncio
async def test_multilingual_conversation_flow(voice_service):
    """Test multilingual conversation flows"""
    languages = ["en", "yo", "ig", "ha", "pcm"]
    
    for lang in languages:
        voice_service.whisper_client.transcribe = AsyncMock(return_value="test command")
        voice_service.language_detector.detect_language = AsyncMock(
            return_value={"language": lang, "confidence": 0.9}
        )
        voice_service.nlu_handler.understand = AsyncMock(
            return_value={
                "intent": Intent.HELP,
                "entities": {},
                "requires_clarification": False
            }
        )
        voice_service.action_executor.execute = AsyncMock(
            return_value=Mock(success=True, message="Help provided")
        )
        voice_service.tts_client.synthesize = AsyncMock(return_value=b"audio")
        voice_service.context_manager.get_context = AsyncMock(return_value=None)
        voice_service.context_manager.update_context = AsyncMock()

        response = await voice_service.process_voice_command(
            audio_data=b"audio",
            user_id="user123",
            session_id=f"session_{lang}",
            preferred_language=lang
        )

        assert response.detected_language == lang


@pytest.mark.asyncio
async def test_context_preservation_across_turns(voice_service):
    """Test context preservation across multiple turns"""
    from app.schemas.voice import ConversationContext
    from datetime import datetime
    
    # First turn
    context1 = ConversationContext(
        session_id="session123",
        user_id="user123",
        language="en",
        history=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    voice_service.context_manager.get_context = AsyncMock(return_value=context1)
    voice_service.context_manager.update_context = AsyncMock()
    voice_service.whisper_client.transcribe = AsyncMock(return_value="book appointment")
    voice_service.language_detector.detect_language = AsyncMock(
        return_value={"language": "en", "confidence": 0.95}
    )
    voice_service.nlu_handler.understand = AsyncMock(
        return_value={
            "intent": Intent.BOOK_APPOINTMENT,
            "entities": {"PERSON": ["Sarah"]},
            "requires_clarification": False
        }
    )
    voice_service.action_executor.execute = AsyncMock(
        return_value=Mock(success=True, message="Booked")
    )
    voice_service.tts_client.synthesize = AsyncMock(return_value=b"audio")

    # Execute first turn
    response1 = await voice_service.process_voice_command(
        audio_data=b"audio",
        user_id="user123",
        session_id="session123"
    )

    # Verify context was updated
    voice_service.context_manager.update_context.assert_called()


@pytest.mark.asyncio
async def test_error_recovery_scenarios(voice_service):
    """Test error recovery scenarios"""
    # Test STT error recovery
    voice_service.whisper_client.transcribe = AsyncMock(
        side_effect=Exception("STT failed")
    )
    voice_service.language_detector.detect_language = AsyncMock(
        return_value={"language": "en", "confidence": 0.5}
    )
    voice_service.nlu_handler.understand = AsyncMock(
        return_value={"intent": Intent.UNKNOWN, "entities": {}}
    )
    voice_service.action_executor.execute = AsyncMock(
        return_value=Mock(success=False, message="Error")
    )
    voice_service.tts_client.synthesize = AsyncMock(return_value=b"audio")
    voice_service.context_manager.get_context = AsyncMock(return_value=None)

    response = await voice_service.process_voice_command(
        audio_data=b"audio",
        user_id="user123",
        session_id="session123"
    )

    # Should handle error gracefully
    assert response.action_result.success is False


@pytest.mark.asyncio
async def test_concurrent_user_sessions(voice_service):
    """Test concurrent user sessions"""
    voice_service.whisper_client.transcribe = AsyncMock(return_value="test")
    voice_service.language_detector.detect_language = AsyncMock(
        return_value={"language": "en", "confidence": 0.95}
    )
    voice_service.nlu_handler.understand = AsyncMock(
        return_value={"intent": Intent.HELP, "entities": {}}
    )
    voice_service.action_executor.execute = AsyncMock(
        return_value=Mock(success=True, message="Help")
    )
    voice_service.tts_client.synthesize = AsyncMock(return_value=b"audio")
    voice_service.context_manager.get_context = AsyncMock(return_value=None)
    voice_service.context_manager.update_context = AsyncMock()

    # Simulate concurrent requests
    tasks = [
        voice_service.process_voice_command(
            audio_data=b"audio",
            user_id=f"user{i}",
            session_id=f"session{i}"
        )
        for i in range(5)
    ]

    responses = await asyncio.gather(*tasks)
    
    # All should complete successfully
    assert len(responses) == 5
    assert all(r.action_result.success for r in responses)
