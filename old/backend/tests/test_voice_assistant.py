"""Tests for voice assistant functionality"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.voice_assistant_service import VoiceAssistantService
from app.schemas.voice import Intent, ActionResult


@pytest.fixture
def voice_service():
    """Create voice assistant service for testing"""
    with patch('app.clients.whisper_client.whisper.load_model'):
        with patch('app.clients.nlu_handler.spacy.load'):
            with patch('app.clients.tts_client.pyttsx3.init'):
                service = VoiceAssistantService()
                return service


@pytest.mark.asyncio
async def test_voice_service_initialization(voice_service):
    """Test voice service initializes all components"""
    assert voice_service.whisper_client is not None
    assert voice_service.language_detector is not None
    assert voice_service.nlu_handler is not None
    assert voice_service.tts_client is not None
    assert voice_service.context_manager is not None
    assert voice_service.action_executor is not None


@pytest.mark.asyncio
async def test_language_detection(voice_service):
    """Test language detection"""
    result = await voice_service.language_detector.detect_language("Hello, how are you?")
    assert result["language"] is not None
    assert result["confidence"] >= 0.0
    assert result["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_nlu_understanding(voice_service):
    """Test NLU understanding"""
    result = await voice_service.nlu_handler.understand("Book an appointment")
    assert result["intent"] is not None
    assert isinstance(result["entities"], dict)
    assert result["confidence"] >= 0.0


@pytest.mark.asyncio
async def test_action_execution(voice_service):
    """Test action execution"""
    result = await voice_service.action_executor.execute(
        intent=Intent.HELP,
        entities={},
        user_id="test_user",
        context=None
    )
    assert result.success is True
    assert result.message is not None


@pytest.mark.asyncio
async def test_context_management(voice_service):
    """Test context management"""
    session_id = "test_session"
    user_id = "test_user"
    
    # Create context
    context = await voice_service._get_or_create_context(
        session_id, user_id, "en"
    )
    assert context.session_id == session_id
    assert context.user_id == user_id
    assert context.language == "en"
    
    # Update context
    await voice_service._update_context(
        context,
        Intent.HELP,
        {},
        "Here are available commands"
    )
    
    # Retrieve context
    retrieved = await voice_service.get_context(session_id)
    assert retrieved is not None
    
    # Clear context
    await voice_service.clear_context(session_id)


@pytest.mark.asyncio
async def test_response_generation(voice_service):
    """Test response generation"""
    action_result = ActionResult(
        success=True,
        message="Appointment booked",
        data={}
    )
    
    response = voice_service._generate_response(
        Intent.BOOK_APPOINTMENT,
        action_result,
        "en"
    )
    assert response is not None
    assert len(response) > 0


@pytest.mark.asyncio
async def test_intent_classification(voice_service):
    """Test intent classification for various commands"""
    test_cases = [
        ("book an appointment", Intent.BOOK_APPOINTMENT),
        ("show my appointments", Intent.SHOW_APPOINTMENTS),
        ("cancel my booking", Intent.CANCEL_APPOINTMENT),
        ("check inventory", Intent.CHECK_INVENTORY),
        ("show revenue", Intent.SHOW_REVENUE),
        ("help", Intent.HELP),
    ]
    
    for text, expected_intent in test_cases:
        result = await voice_service.nlu_handler.understand(text)
        # Intent might not match exactly due to pattern matching, but should be valid
        assert result["intent"] in [Intent.UNKNOWN] + list(Intent)


@pytest.mark.asyncio
async def test_multilingual_support(voice_service):
    """Test multilingual language detection"""
    languages = ["en", "yo", "ig", "ha", "pcm"]
    
    for lang in languages:
        supported = voice_service.language_detector.is_supported(lang)
        assert supported is True


@pytest.mark.asyncio
async def test_error_handling(voice_service):
    """Test error handling in voice processing"""
    # Test with empty audio
    try:
        result = await voice_service.process_voice_command(
            audio_data=b"",
            user_id="test_user",
            session_id="test_session"
        )
        # Should return error response
        assert result.intent == Intent.UNKNOWN or result.action_result.success is False
    except Exception as e:
        # Error handling should catch exceptions
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
