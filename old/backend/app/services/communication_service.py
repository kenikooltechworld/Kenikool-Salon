"""
Communication Service
Handles tracking and logging of all client communications
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId
from app.database import Database
import logging

logger = logging.getLogger(__name__)


class CommunicationService:
    """Service for managing client communications"""

    @staticmethod
    def log_communication(
        client_id: str,
        tenant_id: str,
        channel: str,
        message_type: str,
        content: str,
        recipient: str,
        direction: str = "outbound",
        subject: Optional[str] = None,
        provider: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a communication record
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            channel: Communication channel (sms, email, whatsapp)
            message_type: Type of message (booking_confirmation, reminder, etc.)
            content: Message content
            recipient: Recipient phone/email
            direction: Direction (outbound, inbound)
            subject: Email subject (optional)
            provider: Provider name (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Created communication record
        """
        db = Database.get_db()
        
        communication = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "channel": channel.lower(),
            "direction": direction,
            "message_type": message_type,
            "subject": subject,
            "content": content,
            "recipient": recipient,
            "status": "pending",
            "provider": provider,
            "provider_message_id": None,
            "error_message": None,
            "metadata": metadata or {},
            "sent_at": None,
            "delivered_at": None,
            "read_at": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = db.communications.insert_one(communication)
        communication["_id"] = result.inserted_id
        
        logger.info(f"Logged {channel} communication for client {client_id}")
        
        return communication
    
    @staticmethod
    def update_communication_status(
        communication_id: str,
        status: str,
        provider_message_id: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update communication status
        
        Args:
            communication_id: Communication ID
            status: New status (sent, delivered, read, failed)
            provider_message_id: Provider's message ID
            error_message: Error message if failed
            
        Returns:
            True if updated successfully
        """
        db = Database.get_db()
        
        update_data = {
            "status": status,
            "updated_at": datetime.now()
        }
        
        if provider_message_id:
            update_data["provider_message_id"] = provider_message_id
        
        if error_message:
            update_data["error_message"] = error_message
        
        # Set timestamp based on status
        if status == "sent" and not db.communications.find_one({"_id": ObjectId(communication_id)}).get("sent_at"):
            update_data["sent_at"] = datetime.now()
        elif status == "delivered":
            update_data["delivered_at"] = datetime.now()
        elif status == "read":
            update_data["read_at"] = datetime.now()
        
        result = db.communications.update_one(
            {"_id": ObjectId(communication_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def get_client_communications(
        client_id: str,
        tenant_id: str,
        channel: Optional[str] = None,
        status: Optional[str] = None,
        message_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get communications for a client
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            channel: Filter by channel (optional)
            status: Filter by status (optional)
            message_type: Filter by message type (optional)
            date_from: Filter from date (optional)
            date_to: Filter to date (optional)
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            Dictionary with communications list and pagination info
        """
        db = Database.get_db()
        
        # Build query
        query = {
            "client_id": client_id,
            "tenant_id": tenant_id
        }
        
        if channel:
            query["channel"] = channel.lower()
        
        if status:
            query["status"] = status
        
        if message_type:
            query["message_type"] = message_type
        
        if date_from or date_to:
            query["created_at"] = {}
            if date_from:
                query["created_at"]["$gte"] = date_from
            if date_to:
                query["created_at"]["$lte"] = date_to
        
        # Get total count
        total_count = db.communications.count_documents(query)
        
        # Get communications
        communications = list(
            db.communications.find(query)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for comm in communications:
            comm["id"] = str(comm.pop("_id"))
        
        return {
            "items": communications,
            "total_count": total_count,
            "has_more": (offset + limit) < total_count
        }
    
    @staticmethod
    def get_communication_stats(client_id: str, tenant_id: str) -> Dict[str, Any]:
        """
        Get communication statistics for a client
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            
        Returns:
            Dictionary with communication statistics
        """
        db = Database.get_db()
        
        pipeline = [
            {
                "$match": {
                    "client_id": client_id,
                    "tenant_id": tenant_id
                }
            },
            {
                "$group": {
                    "_id": {
                        "channel": "$channel",
                        "status": "$status"
                    },
                    "count": {"$sum": 1}
                }
            }
        ]
        
        results = list(db.communications.aggregate(pipeline))
        
        # Organize stats
        stats = {
            "total_communications": 0,
            "by_channel": {},
            "by_status": {},
            "response_rate": 0
        }
        
        for result in results:
            channel = result["_id"]["channel"]
            status = result["_id"]["status"]
            count = result["count"]
            
            stats["total_communications"] += count
            
            if channel not in stats["by_channel"]:
                stats["by_channel"][channel] = 0
            stats["by_channel"][channel] += count
            
            if status not in stats["by_status"]:
                stats["by_status"][status] = 0
            stats["by_status"][status] += count
        
        # Calculate response rate (read / delivered)
        delivered = stats["by_status"].get("delivered", 0) + stats["by_status"].get("read", 0)
        read = stats["by_status"].get("read", 0)
        
        if delivered > 0:
            stats["response_rate"] = round((read / delivered) * 100, 1)
        
        return stats
    
    @staticmethod
    def get_recent_communications(
        tenant_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent communications for tenant
        
        Args:
            tenant_id: Tenant ID
            limit: Number of communications to return
            
        Returns:
            List of recent communications
        """
        db = Database.get_db()
        
        communications = list(
            db.communications.find({"tenant_id": tenant_id})
            .sort("created_at", -1)
            .limit(limit)
        )
        
        # Convert ObjectId to string and add client name
        for comm in communications:
            comm["id"] = str(comm.pop("_id"))
            
            # Get client name
            client = db.clients.find_one(
                {"_id": ObjectId(comm["client_id"]), "tenant_id": tenant_id},
                {"name": 1}
            )
            comm["client_name"] = client["name"] if client else "Unknown"
        
        return communications
