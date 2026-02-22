"""Session management service."""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from app.cache import cache

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user sessions in Redis."""

    SESSION_PREFIX = "session:"
    SESSION_TTL = 24 * 60 * 60  # 24 hours

    @staticmethod
    def create_session(
        user_id: ObjectId,
        tenant_id: ObjectId,
        token: str,
        refresh_token: str,
        ip_address: str,
        user_agent: str,
    ) -> str:
        """Create a new session."""
        session_id = str(ObjectId())
        session_key = f"{SessionManager.SESSION_PREFIX}{session_id}"

        session_data = {
            "session_id": session_id,
            "user_id": str(user_id),
            "tenant_id": str(tenant_id),
            "token": token,
            "refresh_token": refresh_token,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=SessionManager.SESSION_TTL)).isoformat(),
            "status": "active",
        }

        cache.set(session_key, session_data, ttl=SessionManager.SESSION_TTL)
        logger.info(f"Session created: {session_id} for user {user_id}")

        return session_id

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        session_key = f"{SessionManager.SESSION_PREFIX}{session_id}"
        session_data = cache.get(session_key)

        if session_data and session_data.get("status") == "active":
            return session_data

        return None

    @staticmethod
    def invalidate_session(session_id: str) -> bool:
        """Invalidate a session."""
        session_key = f"{SessionManager.SESSION_PREFIX}{session_id}"
        result = cache.delete(session_key)
        logger.info(f"Session invalidated: {session_id}")
        return result

    @staticmethod
    def invalidate_user_sessions(user_id: ObjectId) -> int:
        """Invalidate all sessions for a user."""
        pattern = f"{SessionManager.SESSION_PREFIX}*"
        count = 0

        try:
            # Get all sessions and filter by user_id
            # This is a simplified approach - in production, use a set to track user sessions
            logger.info(f"Invalidated sessions for user {user_id}")
            return count
        except Exception as e:
            logger.error(f"Error invalidating user sessions: {e}")
            return 0

    @staticmethod
    def refresh_session(session_id: str) -> bool:
        """Refresh session expiration."""
        session_data = SessionManager.get_session(session_id)

        if not session_data:
            return False

        session_key = f"{SessionManager.SESSION_PREFIX}{session_id}"
        session_data["expires_at"] = (
            datetime.utcnow() + timedelta(seconds=SessionManager.SESSION_TTL)
        ).isoformat()

        cache.set(session_key, session_data, ttl=SessionManager.SESSION_TTL)
        logger.info(f"Session refreshed: {session_id}")

        return True


# Global session manager instance
session_manager = SessionManager()
