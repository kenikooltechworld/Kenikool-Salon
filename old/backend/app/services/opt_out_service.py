"""
Opt-Out Management Service
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pymongo import ASCENDING
from app.database import Database
import uuid


class OptOutService:
    """Service for managing client opt-out preferences"""

    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()

    def __init__(self):
        self.collection = OptOutService._get_db().opt_out_preferences
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create necessary indexes"""
        self.collection.create_index([("tenant_id", ASCENDING)])
        self.collection.create_index([("client_id", ASCENDING)])
        self.collection.create_index([("channels.sms", ASCENDING)])
        self.collection.create_index([("channels.whatsapp", ASCENDING)])
        self.collection.create_index([("channels.email", ASCENDING)])

    async def create_opt_out(
        self,
        client_id: str,
        tenant_id: str,
        channels: Dict[str, bool],
        reason: Optional[str] = None,
        opted_out_via: str = "manual"
    ) -> Dict[str, Any]:
        """Create or update opt-out preference"""
        opt_out = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "channels": channels,
            "reason": reason,
            "opted_out_via": opted_out_via,
            "opted_out_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Upsert
        result = await self.collection.update_one(
            {"client_id": client_id, "tenant_id": tenant_id},
            {"$set": opt_out},
            upsert=True
        )
        
        # Return the document
        return await self.collection.find_one({
            "client_id": client_id,
            "tenant_id": tenant_id
        })

    async def get_opt_out(self, client_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get opt-out preferences for a client"""
        return await self.collection.find_one({
            "client_id": client_id,
            "tenant_id": tenant_id
        })

    async def get_opt_outs(
        self,
        tenant_id: str,
        offset: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get all opt-out preferences for a tenant"""
        opt_outs = await self.collection.find({
            "tenant_id": tenant_id
        }).skip(offset).limit(limit).to_list(None)
        return opt_outs

    async def delete_opt_out(self, client_id: str, tenant_id: str) -> bool:
        """Remove client from opt-out list"""
        result = await self.collection.delete_one({
            "client_id": client_id,
            "tenant_id": tenant_id
        })
        return result.deleted_count > 0

    async def update_opt_out(
        self,
        client_id: str,
        tenant_id: str,
        channels: Dict[str, bool]
    ) -> Optional[Dict[str, Any]]:
        """Update opt-out preferences"""
        result = await self.collection.find_one_and_update(
            {"client_id": client_id, "tenant_id": tenant_id},
            {
                "$set": {
                    "channels": channels,
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        return result

    async def is_opted_out(
        self,
        client_id: str,
        tenant_id: str,
        channel: str
    ) -> bool:
        """Check if client is opted out of a specific channel"""
        opt_out = await self.get_opt_out(client_id, tenant_id)
        if not opt_out:
            return False
        
        channels = opt_out.get("channels", {})
        return channels.get(channel, False)

    async def filter_opted_out_clients(
        self,
        client_ids: List[str],
        tenant_id: str,
        channel: str
    ) -> List[str]:
        """Filter out opted-out clients for a specific channel"""
        opt_outs = await self.collection.find({
            "client_id": {"$in": client_ids},
            "tenant_id": tenant_id,
            f"channels.{channel}": True
        }).to_list(None)
        
        opted_out_ids = {opt["client_id"] for opt in opt_outs}
        return [cid for cid in client_ids if cid not in opted_out_ids]

    async def generate_unsubscribe_link(
        self,
        client_id: str,
        tenant_id: str,
        channel: str
    ) -> str:
        """Generate unsubscribe link token"""
        token = str(uuid.uuid4())
        
        # Store token in database
        await db.unsubscribe_tokens.insert_one({
            "token": token,
            "client_id": client_id,
            "tenant_id": tenant_id,
            "channel": channel,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + __import__('datetime').timedelta(days=30)
        })
        
        return token

    async def process_unsubscribe(
        self,
        token: str,
        tenant_id: str
    ) -> bool:
        """Process unsubscribe link click"""
        # Find token
        token_doc = await db.unsubscribe_tokens.find_one({
            "token": token,
            "tenant_id": tenant_id
        })
        
        if not token_doc:
            return False
        
        # Check if expired
        if token_doc.get("expires_at") < datetime.utcnow():
            return False
        
        client_id = token_doc.get("client_id")
        channel = token_doc.get("channel")
        
        # Update opt-out
        opt_out = await self.get_opt_out(client_id, tenant_id)
        if opt_out:
            channels = opt_out.get("channels", {})
            channels[channel] = True
            await self.update_opt_out(client_id, tenant_id, channels)
        else:
            channels = {"sms": False, "whatsapp": False, "email": False}
            channels[channel] = True
            await self.create_opt_out(
                client_id=client_id,
                tenant_id=tenant_id,
                channels=channels,
                opted_out_via="link"
            )
        
        # Delete token
        await db.unsubscribe_tokens.delete_one({"token": token})
        
        return True

    async def get_opt_out_count(self, tenant_id: str) -> int:
        """Get total opt-out count for tenant"""
        return await self.collection.count_documents({"tenant_id": tenant_id})


# Lazy-loaded singleton instance
_opt_out_service = None

def get_opt_out_service():
    """Get or create the opt-out service"""
    global _opt_out_service
    if _opt_out_service is None:
        _opt_out_service = OptOutService()
    return _opt_out_service

# For backward compatibility
class _LazyOptOutService:
    def __getattr__(self, name):
        return getattr(get_opt_out_service(), name)

opt_out_service = _LazyOptOutService()

