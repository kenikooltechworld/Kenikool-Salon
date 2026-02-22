import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import redis

from app.schemas.voice import ConversationContext, ConversationTurn, Intent

logger = logging.getLogger(__name__)


class ContextManager:
    """Manages conversation context using Redis"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize context manager
        
        Args:
            redis_url: Redis connection URL
        """
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using in-memory storage")
            self.redis_client = None
            self.memory_store: Dict[str, ConversationContext] = {}

    async def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """
        Retrieve conversation context
        
        Args:
            session_id: Session ID
            
        Returns:
            Conversation context or None
        """
        try:
            if self.redis_client:
                data = self.redis_client.get(f"context:{session_id}")
                if data:
                    context_dict = json.loads(data)
                    return self._dict_to_context(context_dict)
            else:
                return self.memory_store.get(session_id)
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
        
        return None

    async def update_context(
        self,
        session_id: str,
        user_id: str,
        language: str,
        intent: Intent,
        entities: Dict[str, Any],
        response: str,
        ttl: int = 3600
    ) -> ConversationContext:
        """
        Update conversation context
        
        Args:
            session_id: Session ID
            user_id: User ID
            language: Language code
            intent: Detected intent
            entities: Extracted entities
            response: Assistant response
            ttl: Time to live in seconds
            
        Returns:
            Updated context
        """
        try:
            # Get existing context or create new
            context = await self.get_context(session_id)
            
            if not context:
                context = ConversationContext(
                    session_id=session_id,
                    user_id=user_id,
                    language=language,
                    history=[],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            
            # Add new turn
            turn = ConversationTurn(
                user_input="",
                intent=intent,
                entities=entities,
                response=response,
                timestamp=datetime.utcnow()
            )
            context.history.append(turn)
            context.last_intent = intent
            context.last_entities = entities
            context.updated_at = datetime.utcnow()
            
            # Store context
            if self.redis_client:
                context_dict = self._context_to_dict(context)
                self.redis_client.setex(
                    f"context:{session_id}",
                    ttl,
                    json.dumps(context_dict)
                )
            else:
                self.memory_store[session_id] = context
            
            return context

        except Exception as e:
            logger.error(f"Failed to update context: {e}")
            raise

    async def clear_context(self, session_id: str) -> bool:
        """
        Clear conversation context
        
        Args:
            session_id: Session ID
            
        Returns:
            True if cleared successfully
        """
        try:
            if self.redis_client:
                self.redis_client.delete(f"context:{session_id}")
            else:
                if session_id in self.memory_store:
                    del self.memory_store[session_id]
            
            logger.info(f"Context cleared for session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to clear context: {e}")
            return False

    def _context_to_dict(self, context: ConversationContext) -> Dict:
        """Convert context to dictionary for storage"""
        return {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "language": context.language,
            "history": [
                {
                    "user_input": turn.user_input,
                    "intent": turn.intent.value,
                    "entities": turn.entities,
                    "response": turn.response,
                    "timestamp": turn.timestamp.isoformat()
                }
                for turn in context.history
            ],
            "last_intent": context.last_intent.value if context.last_intent else None,
            "last_entities": context.last_entities,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat()
        }

    def _dict_to_context(self, data: Dict) -> ConversationContext:
        """Convert dictionary to context object"""
        history = [
            ConversationTurn(
                user_input=turn["user_input"],
                intent=Intent(turn["intent"]),
                entities=turn["entities"],
                response=turn["response"],
                timestamp=datetime.fromisoformat(turn["timestamp"])
            )
            for turn in data.get("history", [])
        ]
        
        return ConversationContext(
            session_id=data["session_id"],
            user_id=data["user_id"],
            language=data["language"],
            history=history,
            last_intent=Intent(data["last_intent"]) if data.get("last_intent") else None,
            last_entities=data.get("last_entities", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
