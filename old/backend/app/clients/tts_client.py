import pyttsx3
import tempfile
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TTSClient:
    """Text-to-speech using pyttsx3"""

    def __init__(self):
        """Initialize TTS engine"""
        self.engine = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize pyttsx3 engine"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            logger.info("TTS engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise

    async def synthesize(
        self,
        text: str,
        language: str = "en"
    ) -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Text to synthesize
            language: Language code
            
        Returns:
            Audio bytes in WAV format
        """
        temp_file = None
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_file = f.name

            # Save to file
            self.engine.save_to_file(text, temp_file)
            self.engine.runAndWait()

            # Read audio data
            with open(temp_file, 'rb') as f:
                audio_data = f.read()

            return audio_data

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass

    async def get_supported_languages(self) -> dict:
        """Get supported languages"""
        return {
            "en": "English",
            "yo": "Yoruba",
            "ig": "Igbo",
            "ha": "Hausa",
            "pcm": "Nigerian Pidgin"
        }

    def set_voice_properties(self, rate: int = 150, volume: float = 0.9):
        """
        Set voice properties
        
        Args:
            rate: Speech rate (50-300)
            volume: Volume (0.0-1.0)
        """
        if self.engine:
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
