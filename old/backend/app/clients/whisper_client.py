import speech_recognition as sr
import tempfile
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class WhisperClient:
    """Client for speech-to-text using SpeechRecognition library"""

    def __init__(self, model_name: str = "base"):
        """
        Initialize speech recognition client
        
        Args:
            model_name: Model size (not used, kept for compatibility)
        """
        self.model_name = model_name
        self.recognizer = sr.Recognizer()
        logger.info("Speech recognition client initialized")

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None
    ) -> str:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio bytes
            language: Language code (e.g., 'en', 'yo')
            
        Returns:
            Transcribed text
        """
        temp_file = None
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                temp_file = f.name

            # Load audio file
            with sr.AudioFile(temp_file) as source:
                audio = self.recognizer.record(source)

            # Transcribe using Google Speech Recognition (free, no API key needed)
            try:
                # Map language codes to Google's language codes
                lang_map = {
                    "en": "en-US",
                    "yo": "yo-NG",  # Yoruba
                    "ig": "ig-NG",  # Igbo
                    "ha": "ha-NG",  # Hausa
                    "pcm": "en-NG",  # Nigerian Pidgin (use English Nigerian)
                }
                google_lang = lang_map.get(language, "en-US")
                
                text = self.recognizer.recognize_google(audio, language=google_lang)
                return text
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return ""
            except sr.RequestError as e:
                logger.error(f"Speech recognition error: {e}")
                # Return empty string instead of raising to allow graceful degradation
                return ""

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
        finally:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)

    async def get_supported_languages(self) -> dict:
        """Get supported languages"""
        return {
            "en": "English",
            "yo": "Yoruba",
            "ig": "Igbo",
            "ha": "Hausa",
            "pcm": "Nigerian Pidgin"
        }
