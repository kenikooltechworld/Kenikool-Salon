"""
Conversation Context Manager
Manages conversation context and session storage using Redis
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import redis.asyncio as redis
from app.models.voice_models import (
    ConversationContext,
    ConversationTurn,
    Intent
)
from app.config import settings

logger = logging.getLogger(__name__)


class ContextManager:
    """Manages conversation context for voice assistant sessions"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize context manager
        
        Args:
            redis_url: Redis connection URL (defaults to settings)
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client: Optional[redis.Redis] = None
        self.default_ttl = 3600  # 1 hour default TTL
        
        logger.info(f"Context manager initialized with Redis: {self.redis_url}")
    
    async def connect(self):
        """Establish Redis connection"""
        if self.redis_client is None:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Connected to Redis for context management")
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Closed Redis connection")

    
    def _get_context_key(self, session_id: str) -> str:
        """Generate Redis key for session context"""
        return f"voice_context:{session_id}"
    
    async def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """
        Retrieve conversation context for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationContext if exists, None otherwise
        """
        try:
            await self.connect()
            
            key = self._get_context_key(session_id)
            data = await self.redis_client.get(key)
            
            if not data:
                logger.debug(f"No context found for session {session_id}")
                return None
            
            # Parse JSON data
            context_dict = json.loads(data)
            
            # Convert to ConversationContext model
            context = ConversationContext(**context_dict)
            
            logger.debug(f"Retrieved context for session {session_id}: {len(context.history)} turns")
            return context
            
        except Exception as e:
            logger.error(f"Failed to get context for {session_id}: {e}")
            return None

    
    async def create_context(
        self,
        session_id: str,
        user_id: str,
        language: str = "en"
    ) -> ConversationContext:
        """
        Create new conversation context
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            language: Initial language
            
        Returns:
            New ConversationContext
        """
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            language=language,
            history=[],
            last_intent=None,
            last_entities={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await self._save_context(context)
        
        logger.info(f"Created new context for session {session_id}")
        return context

    
    async def update_context(
        self,
        session_id: str,
        intent: Intent,
        entities: Dict[str, Any],
        user_input: str,
        response: str
    ) -> None:
        """
        Update conversation context with new turn
        
        Args:
            session_id: Session identifier
            intent: Recognized intent
            entities: Extracted entities
            user_input: User's input text
            response: System's response
        """
        try:
            await self.connect()
            
            # Get existing context or create new one
            context = await self.get_context(session_id)
            if context is None:
                logger.warning(f"Context not found for {session_id}, creating new one")
                # Cannot create without user_id, so return
                return
            
            # Create new conversation turn
            turn = ConversationTurn(
                user_input=user_input,
                intent=intent,
                entities=entities,
                response=response,
                timestamp=datetime.utcnow()
            )
            
            # Update context
            context.history.append(turn)
            context.last_intent = intent
            context.last_entities = entities
            context.updated_at = datetime.utcnow()
            
            # Keep only last 10 turns to limit memory
            if len(context.history) > 10:
                context.history = context.history[-10:]
            
            # Save updated context
            await self._save_context(context)
            
            logger.debug(f"Updated context for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to update context for {session_id}: {e}")

    
    async def _save_context(self, context: ConversationContext) -> None:
        """
        Save context to Redis
        
        Args:
            context: ConversationContext to save
        """
        try:
            await self.connect()
            
            key = self._get_context_key(context.session_id)
            
            # Convert to dict and then JSON
            context_dict = context.model_dump(mode='json')
            data = json.dumps(context_dict, default=str)
            
            # Save with TTL
            await self.redis_client.setex(
                key,
                self.default_ttl,
                data
            )
            
            logger.debug(f"Saved context for session {context.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to save context: {e}")
            raise

    
    async def clear_context(self, session_id: str) -> None:
        """
        Clear conversation context for a session
        
        Args:
            session_id: Session identifier
        """
        try:
            await self.connect()
            
            key = self._get_context_key(session_id)
            await self.redis_client.delete(key)
            
            logger.info(f"Cleared context for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to clear context for {session_id}: {e}")
    
    async def extend_ttl(self, session_id: str, ttl: Optional[int] = None) -> None:
        """
        Extend TTL for a session context
        
        Args:
            session_id: Session identifier
            ttl: Time to live in seconds (defaults to default_ttl)
        """
        try:
            await self.connect()
            
            key = self._get_context_key(session_id)
            ttl = ttl or self.default_ttl
            
            await self.redis_client.expire(key, ttl)
            
            logger.debug(f"Extended TTL for session {session_id} to {ttl}s")
            
        except Exception as e:
            logger.error(f"Failed to extend TTL for {session_id}: {e}")

    
    async def get_or_create_context(
        self,
        session_id: str,
        user_id: str,
        language: str = "en"
    ) -> ConversationContext:
        """
        Get existing context or create new one
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            language: Language code
            
        Returns:
            ConversationContext
        """
        context = await self.get_context(session_id)
        
        if context is None:
            context = await self.create_context(session_id, user_id, language)
        
        return context
    
    async def get_last_entities(self, session_id: str) -> Dict[str, Any]:
        """
        Get last entities from context
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary of last entities
        """
        context = await self.get_context(session_id)
        
        if context:
            return context.last_entities
        
        return {}
    
    async def get_last_intent(self, session_id: str) -> Optional[Intent]:
        """
        Get last intent from context
        
        Args:
            session_id: Session identifier
            
        Returns:
            Last Intent or None
        """
        context = await self.get_context(session_id)
        
        if context:
            return context.last_intent
        
        return None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
