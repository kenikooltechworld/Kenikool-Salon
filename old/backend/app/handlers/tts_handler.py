"""
Text-to-Speech Handler
Converts text responses to speech audio
"""

import logging
from typing import Optional
from app.clients.coqui_client import CoquiClient

logger = logging.getLogger(__name__)


class TTSHandler:
    """Handles text-to-speech conversion"""
    
    # Voice configurations for each language
    VOICE_CONFIG = {
        'en': {
            'model': 'tts_models/en/ljspeech/tacotron2-DDC',
            'speaker_id': None,
            'speed': 1.0
        },
        'yo': {
            'model': 'tts_models/multilingual/multi-dataset/your_tts',
            'speaker_id': 'yoruba_speaker',
            'speed': 0.95
        },
        'ig': {
            'model': 'tts_models/multilingual/multi-dataset/your_tts',
            'speaker_id': 'igbo_speaker',
            'speed': 0.95
        },
        'ha': {
            'model': 'tts_models/multilingual/multi-dataset/your_tts',
            'speaker_id': 'hausa_speaker',
            'speed': 0.95
        },
        'pcm': {
            'model': 'tts_models/en/ljspeech/tacotron2-DDC',
            'speaker_id': None,
            'speed': 1.0
        }
    }
    
    def __init__(self, coqui_client: CoquiClient):
        """
        Initialize TTS handler
        
        Args:
            coqui_client: Coqui TTS client
        """
        self.coqui_client = coqui_client
        logger.info("TTSHandler initialized")
    
    async def synthesize(
        self,
        text: str,
        language: str = 'en',
        speed: Optional[float] = None
    ) -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Text to synthesize
            language: Language code
            speed: Optional speed override
            
        Returns:
            Audio data as bytes
            
        Raises:
            Exception: If synthesis fails
        """
        try:
            # Get voice configuration for language
            config = self.get_voice_config(language)
            
            # Override speed if provided
            if speed is not None:
                config['speed'] = speed
            
            # Synthesize speech
            audio_data = await self.coqui_client.synthesize(
                text=text,
                language=language,
                speaker_id=config.get('speaker_id'),
                speed=config['speed']
            )
            
            logger.info(f"Synthesized {len(text)} chars to {len(audio_data)} bytes audio ({language})")
            
            return audio_data
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise

    
    def get_voice_config(self, language: str) -> dict:
        """
        Get voice configuration for language
        
        Args:
            language: Language code
            
        Returns:
            Voice configuration dict
        """
        return self.VOICE_CONFIG.get(language, self.VOICE_CONFIG['en'])
    
    def get_voice_for_language(self, language: str) -> str:
        """
        Get voice model name for language
        
        Args:
            language: Language code
            
        Returns:
            Voice model name
        """
        config = self.get_voice_config(language)
        return config['model']
    
    async def synthesize_with_fallback(
        self,
        text: str,
        language: str = 'en'
    ) -> Optional[bytes]:
        """
        Synthesize with fallback to English on failure
        
        Args:
            text: Text to synthesize
            language: Preferred language
            
        Returns:
            Audio data or None if all attempts fail
        """
        try:
            # Try primary language
            return await self.synthesize(text, language)
        except Exception as e:
            logger.warning(f"TTS failed for {language}, falling back to English: {e}")
            
            try:
                # Fallback to English
                return await self.synthesize(text, 'en')
            except Exception as e2:
                logger.error(f"TTS fallback also failed: {e2}")
                return None
    
    def optimize_text_for_speech(self, text: str, language: str) -> str:
        """
        Optimize text for better speech synthesis
        
        Args:
            text: Input text
            language: Language code
            
        Returns:
            Optimized text
        """
        # Remove excessive punctuation
        text = text.replace('...', '.')
        text = text.replace('..', '.')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Add pauses for better pacing
        text = text.replace('. ', '. ... ')
        text = text.replace('? ', '? ... ')
        text = text.replace('! ', '! ... ')
        
        # Language-specific optimizations
        if language == 'yo':
            # Ensure proper tone marks are preserved
            pass
        elif language == 'ig':
            # Ensure proper diacritics
            pass
        elif language == 'ha':
            # Ensure proper glottal stops
            pass
        
        return text.strip()
    
    async def synthesize_optimized(
        self,
        text: str,
        language: str = 'en'
    ) -> bytes:
        """
        Synthesize with text optimization
        
        Args:
            text: Text to synthesize
            language: Language code
            
        Returns:
            Audio data
        """
        optimized_text = self.optimize_text_for_speech(text, language)
        return await self.synthesize(optimized_text, language)
    
    def estimate_audio_duration(self, text: str, language: str = 'en') -> float:
        """
        Estimate audio duration in seconds
        
        Args:
            text: Text to synthesize
            language: Language code
            
        Returns:
            Estimated duration in seconds
        """
        # Rough estimate: ~150 words per minute
        words = len(text.split())
        duration = (words / 150) * 60
        
        # Adjust for language speed
        config = self.get_voice_config(language)
        duration = duration / config['speed']
        
        return duration
