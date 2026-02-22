"""
Client Factory for Docker AI Models
Centralized initialization and management of AI model clients
"""

import logging
import os
from typing import Optional
from .whisper_client import WhisperClient
from .kimi_client import KimiClient
from .qwen_client import QwenClient
from .coqui_client import CoquiClient
from .deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


class AIClientFactory:
    """Factory for creating and managing AI model clients"""
    
    def __init__(self):
        """Initialize client factory with environment configuration"""
        self.whisper_url = os.getenv('WHISPER_CONTAINER_URL', 'http://localhost:9000')
        self.kimi_url = os.getenv('KIMI_CONTAINER_URL', 'http://localhost:11434')
        self.qwen_url = os.getenv('QWEN_CONTAINER_URL', 'http://localhost:11434')
        self.coqui_url = os.getenv('COQUI_CONTAINER_URL', 'http://localhost:5002')
        self.deepseek_url = os.getenv('DEEPSEEK_CONTAINER_URL', 'http://localhost:11435')
        
        # Client instances (lazy initialization)
        self._whisper_client: Optional[WhisperClient] = None
        self._kimi_client: Optional[KimiClient] = None
        self._qwen_client: Optional[QwenClient] = None
        self._coqui_client: Optional[CoquiClient] = None
        self._deepseek_client: Optional[DeepSeekClient] = None
        
        logger.info("AI Client Factory initialized")
    
    def get_whisper_client(self) -> WhisperClient:
        """Get or create Whisper STT client"""
        if self._whisper_client is None:
            self._whisper_client = WhisperClient(
                container_url=self.whisper_url,
                timeout=30.0
            )
            logger.info(f"Created Whisper client: {self.whisper_url}")
        return self._whisper_client
    
    def get_kimi_client(self) -> KimiClient:
        """Get or create Kimi NLU client"""
        if self._kimi_client is None:
            self._kimi_client = KimiClient(
                container_url=self.kimi_url,
                timeout=30.0
            )
            logger.info(f"Created Kimi client: {self.kimi_url}")
        return self._kimi_client
    
    def get_qwen_client(self) -> QwenClient:
        """Get or create Qwen language detection client"""
        if self._qwen_client is None:
            self._qwen_client = QwenClient(
                container_url=self.qwen_url,
                timeout=15.0
            )
            logger.info(f"Created Qwen client: {self.qwen_url}")
        return self._qwen_client
    
    def get_coqui_client(self) -> CoquiClient:
        """Get or create Coqui TTS client"""
        if self._coqui_client is None:
            self._coqui_client = CoquiClient(
                container_url=self.coqui_url,
                timeout=30.0
            )
            logger.info(f"Created Coqui client: {self.coqui_url}")
        return self._coqui_client
    
    def get_deepseek_client(self) -> DeepSeekClient:
        """Get or create DeepSeek reasoning client"""
        if self._deepseek_client is None:
            self._deepseek_client = DeepSeekClient(
                container_url=self.deepseek_url,
                timeout=60.0  # Longer timeout for reasoning
            )
            logger.info(f"Created DeepSeek client: {self.deepseek_url}")
        return self._deepseek_client
    
    async def health_check_all(self) -> dict:
        """
        Check health of all AI model containers
        
        Returns:
            dict with health status of each container
        """
        results = {}
        
        clients = [
            ('whisper', self.get_whisper_client()),
            ('kimi', self.get_kimi_client()),
            ('qwen', self.get_qwen_client()),
            ('coqui', self.get_coqui_client()),
            ('deepseek', self.get_deepseek_client()),
        ]
        
        for name, client in clients:
            try:
                is_healthy = await client.health_check()
                results[name] = {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'url': client.container_url
                }
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'url': client.container_url,
                    'error': str(e)
                }
                logger.error(f"Health check failed for {name}: {e}")
        
        return results
    
    async def close_all(self):
        """Close all client connections"""
        clients = [
            self._whisper_client,
            self._kimi_client,
            self._qwen_client,
            self._coqui_client,
            self._deepseek_client
        ]
        
        for client in clients:
            if client is not None:
                try:
                    await client.close()
                except Exception as e:
                    logger.error(f"Error closing client: {e}")
        
        logger.info("All AI clients closed")


# Global factory instance
_factory: Optional[AIClientFactory] = None


def get_client_factory() -> AIClientFactory:
    """Get global AI client factory instance"""
    global _factory
    if _factory is None:
        _factory = AIClientFactory()
    return _factory
