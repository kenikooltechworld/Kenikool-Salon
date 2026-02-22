"""Integration tests for voice assistant pipeline"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.voice_assistant_service import VoiceAssistantService
from app.schemas.voice import Intent


@pytest.fixture
def mock_voice_service():
    """Create mocked voice service for integration testing"""
    with patch('app.clients.whisper_client.whisper.load_model'):
        with patch('app.clients.nlu_handler.spacy.load'):
            with patch('app.clients.tts_client.pyttsx3.init'):
                service = VoiceAssistantService()
                
                # Mock the transcription
                service.whisper_client.transcribe = MagicMock(
                    return_value="book an appointment"
                )
                
                # Mock language detection
                service.language_detector.detect_language = MagicMock(
                    return_value={
                        "language": "en",
                        "confidence": 0.95,
                        "alternatives": []
                    }
                )
                
                # Mock NLU
                service.nlu_handler.understand = MagicMock(
                    return_value={
                        "intent": Intent.BOOK_APPOINTMENT,
                        "entities": {"PERSON": ["John"]},
                        "confidence": 0.85,
                        "requires_clarification": False
                    }
                )
                
                # Mock TTS
                service.tts_client.synthesize = MagicMock(
                    return_value=b"audio_data"
                )
                
                return service


@pytest.mark.asyncio
async def test_complete_voice_pipeline(mock_voice_service):
    """Test complete voice command pipeline"""
    
    # Mock audio data
    audio_data = b"mock_audio_data"
    user_id = "test_user"
    session_id = "test_session"
    
    # Process voice command
    response = await mock_voice_service.process_voice_command(
        audio_data=audio_data,
        user_id=user_id,
        session_id=session_id,
        preferred_language="en"
    )
    
    # Verify response
    assert response.transcript == "book an appointment"
    assert response.detected_language == "en"
    assert response.intent == Intent.BOOK_APPOINTMENT
    assert response.response_text is not None
    assert response.action_result.success is True


@pytest.mark.asyncio
async def test_multilingual_pipeline(mock_voice_service):
    """Test voice pipeline with different languages"""
    
    languages = ["en", "yo", "ig", "ha", "pcm"]
    
    for lang in languages:
        # Update mock for language
        mock_voice_service.language_detector.detect_language = MagicMock(
            return_value={
                "language": lang,
                "confidence": 0.9,
                "alternatives": []
            }
        )
        
        response = await mock_voice_service.process_voice_command(
            audio_data=b"mock_audio",
            user_id="test_user",
            session_id=f"session_{lang}",
            preferred_language=lang
        )
        
        assert response.detected_language == lang


@pytest.mark.asyncio
async def test_context_persistence_across_turns(mock_voice_service):
    """Test context persistence across multiple turns"""
    
    session_id = "persistent_session"
    user_id = "test_user"
    
    # First turn
    response1 = await mock_voice_service.process_voice_command(
        audio_data=b"audio1",
        user_id=user_id,
        session_id=session_id
    )
    
    # Verify context was created
    context1 = await mock_voice_service.get_context(session_id)
    assert context1 is not None
    assert len(context1.history) > 0
    
    # Second turn
    response2 = await mock_voice_service.process_voice_command(
        audio_data=b"audio2",
        user_id=user_id,
        session_id=session_id
    )
    
    # Verify context was updated
    context2 = await mock_voice_service.get_context(session_id)
    assert context2 is not None
    assert len(context2.history) >= len(context1.history)


@pytest.mark.asyncio
async def test_action_execution_for_all_intents(mock_voice_service):
    """Test action execution for all supported intents"""
    
    intents_to_test = [
        Intent.BOOK_APPOINTMENT,
        Intent.CANCEL_APPOINTMENT,
        Intent.SHOW_APPOINTMENTS,
        Intent.CHECK_INVENTORY,
        Intent.SHOW_REVENUE,
        Intent.HELP,
    ]
    
    for intent in intents_to_test:
        # Mock NLU to return specific intent
        mock_voice_service.nlu_handler.understand = MagicMock(
            return_value={
                "intent": intent,
                "entities": {},
                "confidence": 0.9,
                "requires_clarification": False
            }
        )
        
        response = await mock_voice_service.process_voice_command(
            audio_data=b"mock_audio",
            user_id="test_user",
            session_id=f"session_{intent.value}"
        )
        
        assert response.intent == intent
        assert response.action_result is not None


@pytest.mark.asyncio
async def test_error_recovery(mock_voice_service):
    """Test error recovery in voice pipeline"""
    
    # Mock transcription failure
    mock_voice_service.whisper_client.transcribe = MagicMock(
        side_effect=Exception("Transcription failed")
    )
    
    response = await mock_voice_service.process_voice_command(
        audio_data=b"mock_audio",
        user_id="test_user",
        session_id="error_session"
    )
    
    # Should handle error gracefully
    assert response.intent == Intent.UNKNOWN
    assert response.action_result.success is False


@pytest.mark.asyncio
async def test_session_cleanup(mock_voice_service):
    """Test session cleanup"""
    
    session_id = "cleanup_session"
    
    # Create session
    await mock_voice_service.process_voice_command(
        audio_data=b"mock_audio",
        user_id="test_user",
        session_id=session_id
    )
    
    # Verify session exists
    context = await mock_voice_service.get_context(session_id)
    assert context is not None
    
    # Clear session
    await mock_voice_service.clear_context(session_id)
    
    # Verify session is cleared
    cleared_context = await mock_voice_service.get_context(session_id)
    assert cleared_context is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
