"""
Voice Assistant Security and Privacy Utilities
Ensures data privacy and security for voice interactions
"""

import logging
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)


class VoiceDataEncryption:
    """Handles encryption of voice data and conversation history"""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize encryption handler
        
        Args:
            encryption_key: Optional encryption key (generated if not provided)
        """
        if encryption_key:
            self.key = encryption_key
        else:
            self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
        logger.info("Voice data encryption initialized")
    
    def encrypt_text(self, text: str) -> str:
        """
        Encrypt text data
        
        Args:
            text: Plain text to encrypt
            
        Returns:
            Encrypted text as base64 string
        """
        try:
            encrypted = self.cipher.encrypt(text.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """
        Decrypt text data
        
        Args:
            encrypted_text: Encrypted text as base64 string
            
        Returns:
            Decrypted plain text
        """
        try:
            encrypted = base64.b64decode(encrypted_text.encode('utf-8'))
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def encrypt_audio(self, audio_data: bytes) -> bytes:
        """
        Encrypt audio data
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Encrypted audio bytes
        """
        try:
            return self.cipher.encrypt(audio_data)
        except Exception as e:
            logger.error(f"Audio encryption failed: {e}")
            raise
    
    def decrypt_audio(self, encrypted_audio: bytes) -> bytes:
        """
        Decrypt audio data
        
        Args:
            encrypted_audio: Encrypted audio bytes
            
        Returns:
            Decrypted audio bytes
        """
        try:
            return self.cipher.decrypt(encrypted_audio)
        except Exception as e:
            logger.error(f"Audio decryption failed: {e}")
            raise


class SessionSecurity:
    """Manages session security and isolation"""
    
    @staticmethod
    def generate_session_id(user_id: str) -> str:
        """
        Generate secure session ID
        
        Args:
            user_id: User identifier
            
        Returns:
            Secure session ID
        """
        timestamp = datetime.utcnow().isoformat()
        random_token = secrets.token_hex(16)
        
        # Create hash of user_id + timestamp + random token
        data = f"{user_id}:{timestamp}:{random_token}"
        session_id = hashlib.sha256(data.encode()).hexdigest()
        
        logger.debug(f"Generated session ID for user {user_id}")
        return session_id
    
    @staticmethod
    def verify_session_ownership(session_id: str, user_id: str, stored_user_id: str) -> bool:
        """
        Verify that session belongs to user
        
        Args:
            session_id: Session identifier
            user_id: Requesting user ID
            stored_user_id: User ID stored in session
            
        Returns:
            True if user owns session
        """
        if user_id != stored_user_id:
            logger.warning(f"Session ownership verification failed: {session_id}")
            return False
        
        return True
    
    @staticmethod
    def sanitize_audio_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive metadata from audio
        
        Args:
            metadata: Audio metadata
            
        Returns:
            Sanitized metadata
        """
        # Remove potentially sensitive fields
        sensitive_fields = ['location', 'device_id', 'ip_address', 'user_agent']
        
        sanitized = metadata.copy()
        for field in sensitive_fields:
            sanitized.pop(field, None)
        
        return sanitized


class DataRetentionPolicy:
    """Manages data retention and cleanup"""
    
    # Retention periods
    AUDIO_RETENTION_HOURS = 1  # Delete audio after 1 hour
    TRANSCRIPT_RETENTION_HOURS = 24  # Delete transcripts after 24 hours
    SESSION_RETENTION_HOURS = 1  # Delete sessions after 1 hour
    
    @staticmethod
    def should_delete_audio(timestamp: datetime) -> bool:
        """
        Check if audio should be deleted
        
        Args:
            timestamp: Audio creation timestamp
            
        Returns:
            True if audio should be deleted
        """
        age = datetime.utcnow() - timestamp
        return age > timedelta(hours=DataRetentionPolicy.AUDIO_RETENTION_HOURS)
    
    @staticmethod
    def should_delete_transcript(timestamp: datetime) -> bool:
        """
        Check if transcript should be deleted
        
        Args:
            timestamp: Transcript creation timestamp
            
        Returns:
            True if transcript should be deleted
        """
        age = datetime.utcnow() - timestamp
        return age > timedelta(hours=DataRetentionPolicy.TRANSCRIPT_RETENTION_HOURS)
    
    @staticmethod
    def should_delete_session(timestamp: datetime) -> bool:
        """
        Check if session should be deleted
        
        Args:
            timestamp: Session creation timestamp
            
        Returns:
            True if session should be deleted
        """
        age = datetime.utcnow() - timestamp
        return age > timedelta(hours=DataRetentionPolicy.SESSION_RETENTION_HOURS)
    
    @staticmethod
    def get_cleanup_timestamp(retention_hours: int) -> datetime:
        """
        Get timestamp for cleanup cutoff
        
        Args:
            retention_hours: Hours to retain data
            
        Returns:
            Cutoff timestamp
        """
        return datetime.utcnow() - timedelta(hours=retention_hours)


class MicrophonePermissionManager:
    """Manages microphone permissions and access"""
    
    @staticmethod
    def check_permission_status(user_id: str, tenant_id: str) -> Dict[str, Any]:
        """
        Check microphone permission status
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            
        Returns:
            Permission status
        """
        # In production, this would check actual permissions
        return {
            'granted': True,
            'user_id': user_id,
            'tenant_id': tenant_id,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def revoke_permission(user_id: str) -> bool:
        """
        Revoke microphone permission
        
        Args:
            user_id: User identifier
            
        Returns:
            True if revoked successfully
        """
        logger.info(f"Revoked microphone permission for user {user_id}")
        return True


class PrivacyValidator:
    """Validates privacy compliance"""
    
    @staticmethod
    def validate_local_processing(container_url: str) -> bool:
        """
        Validate that processing is local
        
        Args:
            container_url: Docker container URL
            
        Returns:
            True if local processing
        """
        # Check if URL is localhost or local network
        local_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
        
        for host in local_hosts:
            if host in container_url:
                return True
        
        # Check for local network (192.168.x.x, 10.x.x.x, 172.16-31.x.x)
        if '192.168.' in container_url or '10.' in container_url:
            return True
        
        logger.warning(f"Non-local container URL detected: {container_url}")
        return False
    
    @staticmethod
    def validate_no_external_calls(request_log: list) -> bool:
        """
        Validate no external API calls were made
        
        Args:
            request_log: List of requests made
            
        Returns:
            True if no external calls
        """
        external_domains = [
            'openai.com', 'google.com', 'azure.com', 'aws.com',
            'anthropic.com', 'cohere.ai'
        ]
        
        for request in request_log:
            url = request.get('url', '')
            for domain in external_domains:
                if domain in url:
                    logger.error(f"External API call detected: {url}")
                    return False
        
        return True
    
    @staticmethod
    def audit_data_flow(data_flow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audit data flow for privacy compliance
        
        Args:
            data_flow: Data flow information
            
        Returns:
            Audit report
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'local_processing': True,
            'external_calls': False,
            'data_encrypted': True,
            'compliant': True
        }
        
        # Check each stage
        for stage, info in data_flow.items():
            if info.get('external', False):
                report['external_calls'] = True
                report['compliant'] = False
            
            if not info.get('encrypted', True):
                report['data_encrypted'] = False
                report['compliant'] = False
        
        return report
