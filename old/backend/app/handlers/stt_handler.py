"""
Speech-to-Text Handler
Handles audio transcription using Whisper Docker container
"""

import logging
from typing import Optional
from ..clients.client_factory import get_client_factory
from ..models.voice_models import TranscriptionResult
from ..utils.audio_preprocessing import AudioPreprocessor
from ..middleware.voice_error_handler import STTError

logger = logging.getLogger(__name__)


class STTHandler:
    """Handler for speech-to-text operations"""
    
    def __init__(self):
        """Initialize STT handler"""
        self.client_factory = get_client_factory()
        self.whisper_client = self.client_factory.get_whisper_client()
        self.audio_preprocessor = AudioPreprocessor()
        
        logger.info("STT Handler initialized")
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        source_format: str = 'webm'
    ) -> TranscriptionResult:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Raw audio bytes
            language: Optional language hint
            source_format: Source audio format
            
        Returns:
            TranscriptionResult with text and metadata
            
        Raises:
            STTError: If transcription fails
        """
        try:
            logger.info(f"Transcribing {len(audio_data)} bytes of audio")
            
            # Step 1: Validate audio
            is_valid, error_msg = self.audio_preprocessor.validate_audio(audio_data)
            if not is_valid:
                raise STTError(
                    message=f"Invalid audio: {error_msg}",
                    details={'validation_error': error_msg}
                )
            
            # Step 2: Preprocess audio
            try:
                processed_audio = self.preprocess_audio(audio_data, source_format)
            except Exception as e:
                logger.error(f"Audio preprocessing failed: {e}")
                # Try with original audio if preprocessing fails
                processed_audio = audio_data
            
            # Step 3: Get audio duration
            duration = self.audio_preprocessor.get_audio_duration(processed_audio)
            
            # Step 4: Call Whisper for transcription
            result = await self.whisper_client.transcribe(
                audio_data=processed_audio,
                language=language,
                task='transcribe'
            )
            
            # Step 5: Build transcription result
            transcription = TranscriptionResult(
                text=result['text'].strip(),
                confidence=result.get('confidence', 0.0),
                language=result.get('language'),
                duration=duration
            )
            
            logger.info(
                f"Transcription complete: '{transcription.text}' "
                f"(confidence: {transcription.confidence:.2f}, "
                f"language: {transcription.language})"
            )
            
            # Step 6: Validate transcription
            if not transcription.text:
                raise STTError(
                    message="No speech detected in audio",
                    details={'duration': duration}
                )
            
            if transcription.confidence < 0.3:
                logger.warning(f"Low confidence transcription: {transcription.confidence}")
            
            return transcription
            
        except STTError:
            raise
        except Exception as e:
            logger.error(f"STT transcription failed: {e}", exc_info=True)
            raise STTError(
                message="Failed to transcribe audio",
                details={'error': str(e)}
            )
    
    def preprocess_audio(
        self,
        audio_data: bytes,
        source_format: str = 'webm'
    ) -> bytes:
        """
        Preprocess audio for optimal STT performance
        
        Args:
            audio_data: Raw audio bytes
            source_format: Source audio format
            
        Returns:
            Preprocessed audio bytes
        """
        try:
            # Apply full preprocessing pipeline
            processed = self.audio_preprocessor.preprocess_for_stt(
                audio_data=audio_data,
                source_format=source_format,
                apply_noise_reduction=True
            )
            
            logger.debug(f"Audio preprocessed: {len(audio_data)} -> {len(processed)} bytes")
            
            return processed
            
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            raise
    
    async def detect_language_from_audio(
        self,
        audio_data: bytes,
        source_format: str = 'webm'
    ) -> dict:
        """
        Detect language from audio
        
        Args:
            audio_data: Raw audio bytes
            source_format: Source audio format
            
        Returns:
            dict with language and confidence
        """
        try:
            # Preprocess audio
            processed_audio = self.preprocess_audio(audio_data, source_format)
            
            # Call Whisper for language detection
            result = await self.whisper_client.detect_language(processed_audio)
            
            logger.info(f"Detected language from audio: {result['language']} ({result['confidence']:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Audio language detection failed: {e}")
            raise STTError(
                message="Failed to detect language from audio",
                details={'error': str(e)}
            )
    
    async def transcribe_with_timestamps(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        source_format: str = 'webm'
    ) -> dict:
        """
        Transcribe audio with word-level timestamps
        
        Args:
            audio_data: Raw audio bytes
            language: Optional language hint
            source_format: Source audio format
            
        Returns:
            dict with text and timestamps
        """
        try:
            # Preprocess audio
            processed_audio = self.preprocess_audio(audio_data, source_format)
            
            # Call Whisper with timestamp option
            result = await self.whisper_client.transcribe(
                audio_data=processed_audio,
                language=language,
                task='transcribe'
            )
            
            return {
                'text': result['text'],
                'segments': result.get('segments', []),
                'language': result.get('language')
            }
            
        except Exception as e:
            logger.error(f"Transcription with timestamps failed: {e}")
            raise STTError(
                message="Failed to transcribe with timestamps",
                details={'error': str(e)}
            )
    
    async def health_check(self) -> bool:
        """
        Check if STT service is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            return await self.whisper_client.health_check()
        except Exception as e:
            logger.error(f"STT health check failed: {e}")
            return False
