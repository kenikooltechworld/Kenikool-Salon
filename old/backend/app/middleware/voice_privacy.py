"""
Voice Privacy Middleware
Enforces privacy and security policies for voice interactions
"""

import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from app.utils.voice_security import PrivacyValidator, SessionSecurity

logger = logging.getLogger(__name__)


class VoicePrivacyMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce voice privacy policies"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request with privacy checks
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler
            
        Returns:
            HTTP response
        """
        # Only apply to voice endpoints
        if not request.url.path.startswith('/api/voice'):
            return await call_next(request)
        
        # Skip for health and languages endpoints (public)
        if request.url.path in ['/api/voice/health', '/api/voice/languages']:
            return await call_next(request)
        
        # Verify user authentication
        user = getattr(request.state, 'user', None)
        if not user:
            logger.warning(f"Unauthenticated voice request: {request.url.path}")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Log request for audit
        logger.info(f"Voice request: {request.method} {request.url.path} by user {user.get('id')}")
        
        # Process request
        response = await call_next(request)
        
        # Add privacy headers
        response.headers['X-Voice-Privacy'] = 'local-processing'
        response.headers['X-Data-Retention'] = '1-hour'
        response.headers['X-No-External-Calls'] = 'true'
        
        return response


async def cleanup_on_logout(user_id: str, session_manager):
    """
    Cleanup voice data on user logout
    
    Args:
        user_id: User identifier
        session_manager: Session management instance
    """
    try:
        # Get all sessions for user
        sessions = await session_manager.get_user_sessions(user_id)
        
        # Clear each session
        for session_id in sessions:
            await session_manager.clear_context(session_id)
            logger.info(f"Cleared session {session_id} for user {user_id}")
        
        logger.info(f"Completed logout cleanup for user {user_id}")
        
    except Exception as e:
        logger.error(f"Logout cleanup failed for user {user_id}: {e}")


async def enforce_session_isolation(session_id: str, user_id: str, context_manager) -> bool:
    """
    Enforce session isolation between users
    
    Args:
        session_id: Session identifier
        user_id: Requesting user ID
        context_manager: Context manager instance
        
    Returns:
        True if session belongs to user
    """
    try:
        context = await context_manager.get_context(session_id)
        
        if not context:
            return True  # New session
        
        # Verify ownership
        if context.user_id != user_id:
            logger.warning(f"Session isolation violation: user {user_id} accessing session {session_id}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Session isolation check failed: {e}")
        return False
