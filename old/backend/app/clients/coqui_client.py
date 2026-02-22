"""
Coqui TTS Client for Text-to-Speech
Communicates with Coqui TTS Docker container for speech synthesis
"""

import logging
from typing import Optional
from .base_client import BaseDockerClient

logger = logging.getLogger(__name__)


class CoquiClient(BaseDockerClient):
    """Client for Coqui TTS Docker container"""
    
    # Voice mappings for different languages
    VOICE_MAPPINGS = {
        'en': 'tts_models/en/ljspeech/tacotron2-DDC',
        'yo': 'tts_models/multilingual/multi-dataset/your_tts',  # Multilingual model
        'ig': 'tts_models/multilingual/multi-dataset/your_tts',
        'ha': 'tts_models/multilingual/multi-dataset/your_tts',
        'pcm': 'tts_models/en/ljspeech/tacotron2-DDC',  # Use English model for Pidgin
    }
    
    async def synthesize(
        self,
        text: str,
        language: str = 'en',
        speaker_id: Optional[str] = None,
        speed: float = 1.0
    ) -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Text to synthesize
            language: Language code
            speaker_id: Optional speaker ID for multi-speaker models
            speed: Speech speed multiplier
            
        Returns:
            Audio data as bytes (WAV format)
            
        Raises:
            httpx.HTTPError: If synthesis fails
        """
        try:
            # Get appropriate voice model for language
            model_name = self.VOICE_MAPPINGS.get(language, self.VOICE_MAPPINGS['en'])
            
            payload = {
                'text': text,
                'model_name': model_name,
                'speed': speed
            }
            
            if speaker_id:
                payload['speaker_id'] = speaker_id
            
            # For multilingual models, specify language
            if language in ['yo', 'ig', 'ha']:
                payload['language_idx'] = language
            
            response = await self._post(
                '/api/tts',
                json_data=payload
            )
            
            # Response is audio bytes
            audio_data = response.content
            
            logger.info(f"Synthesized {len(text)} chars -> {len(audio_data)} bytes audio ({language})")
            
            return audio_data
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise
    
    async def get_available_models(self) -> list:
        """
        Get list of available TTS models
        
        Returns:
            List of model names
        """
        try:
            response = await self._get('/api/models')
            result = response.json()
            return result.get('models', [])
            
        except Exception as e:
            logger.error(f"Failed to get TTS models: {e}")
            return []
    
    async def get_speakers(self, model_name: str) -> list:
        """
        Get available speakers for a model
        
        Args:
            model_name: TTS model name
            
        Returns:
            List of speaker IDs
        """
        try:
            response = await self._get(
                '/api/speakers',
                params={'model_name': model_name}
            )
            result = response.json()
            return result.get('speakers', [])
            
        except Exception as e:
            logger.error(f"Failed to get speakers: {e}")
            return []
    
    def get_voice_for_language(self, language: str) -> str:
        """
        Get appropriate voice model for language
        
        Args:
            language: Language code
            
        Returns:
            Voice model name
        """
        return self.VOICE_MAPPINGS.get(language, self.VOICE_MAPPINGS['en'])
