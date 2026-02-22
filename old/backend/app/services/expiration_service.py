"""
Expiration Service - Manages automatic expiration of waitlist entries
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from bson import ObjectId
from app.database import Database
from app.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)


class ExpirationService:
    """Service for managing waitlist entry expiration"""
    
    # Expiration thresholds (in days)
    WAITING_EXPIRATION_DAYS = 30
    NOTIFIED_EXPIRATION_DAYS = 7
    
    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()
    
    @staticmethod
    def check_and_expire_entries(tenant_id: Optional[str] = None) -> Dict[str, int]:
        """
        Check and expire old waitlist entries.
        
        Args:
            tenant_id: Optional tenant ID to limit expiration to specific tenant
            
        Returns:
            Dict with counts of expired entries by type
            
        Requirements: 7.1, 7.2, 7.3, 7.5
        """
        db = ExpirationService._get_db()
        
        # Expire waiting entries
        waiting_expired = ExpirationService._expire_waiting_entries(tenant_id)
        
        # Expire notified entries
        notified_expired = ExpirationService._expire_notified_entries(tenant_id)
        
        total_expired = waiting_expired + notified_expired
        
        logger.info(
            f"Expiration check completed: "
            f"{waiting_expired} waiting entries expired, "
            f"{notified_expired} notified entries expired"
        )
        
        return {
            "waiting_expired": waiting_expired,
            "notified_expired": notified_expired,
            "total_expired": total_expired
        }
    
    @staticmethod
    def _expire_waiting_entries(tenant_id: Optional[str] = None) -> int:
        """
        Expire entries in "waiting" status older than 30 days.
        
        Args:
            tenant_id: Optional tenant ID to limit to specific tenant
            
        Returns:
            Count of expired entries
            
        Requirements: 7.1
        """
        db = ExpirationService._get_db()
        
        # Calculate cutoff date (30 days ago)
        cutoff_date = datetime.utcnow() - timedelta(days=ExpirationService.WAITING_EXPIRATION_DAYS)
        
        # Build query
        query = {
            "status": "waiting",
            "created_at": {"$lt": cutoff_date}
        }
        
        if tenant_id:
            query["tenant_id"] = tenant_id
        
        # Find entries to expire
        entries_to_expire = list(db.waitlist.find(query))
        
        # Update each entry
        expired_count = 0
        for entry in entries_to_expire:
            try:
                # Update status to expired
                result = db.waitlist.update_one(
                    {"_id": entry["_id"]},
                    {
                        "$set": {
                            "status": "expired",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                if result.modified_count > 0:
                    expired_count += 1
                    
                    # Send expiration notification if enabled
                    ExpirationService._send_expiration_notification(entry)
                    
            except Exception as e:
                logger.error(f"Error expiring waiting entry {entry['_id']}: {e}")
        
        logger.info(f"Expired {expired_count} waiting entries")
        return expired_count
    
    @staticmethod
    def _expire_notified_entries(tenant_id: Optional[str] = None) -> int:
        """
        Expire entries in "notified" status older than 7 days.
        
        Args:
            tenant_id: Optional tenant ID to limit to specific tenant
            
        Returns:
            Count of expired entries
            
        Requirements: 7.2
        """
        db = ExpirationService._get_db()
        
        # Calculate cutoff date (7 days ago)
        cutoff_date = datetime.utcnow() - timedelta(days=ExpirationService.NOTIFIED_EXPIRATION_DAYS)
        
        # Build query
        query = {
            "status": "notified",
            "notified_at": {"$lt": cutoff_date}
        }
        
        if tenant_id:
            query["tenant_id"] = tenant_id
        
        # Find entries to expire
        entries_to_expire = list(db.waitlist.find(query))
        
        # Update each entry
        expired_count = 0
        for entry in entries_to_expire:
            try:
                # Update status to expired
                result = db.waitlist.update_one(
                    {"_id": entry["_id"]},
                    {
                        "$set": {
                            "status": "expired",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                if result.modified_count > 0:
                    expired_count += 1
                    
                    # Send expiration notification if enabled
                    ExpirationService._send_expiration_notification(entry)
                    
            except Exception as e:
                logger.error(f"Error expiring notified entry {entry['_id']}: {e}")
        
        logger.info(f"Expired {expired_count} notified entries")
        return expired_count
    
    @staticmethod
    def _send_expiration_notification(entry: Dict) -> bool:
        """
        Send expiration notification to client.
        
        Args:
            entry: Waitlist entry
            
        Returns:
            True if notification sent successfully
            
        Requirements: 7.5
        """
        try:
            # Build expiration message
            message = (
                f"Hi {entry.get('client_name', 'there')}, "
                f"your waitlist request has expired. "
                f"Please contact us if you'd like to rejoin the waitlist."
            )
            
            # Send notification
            channels = ["sms"]
            if entry.get("client_email"):
                channels.append("email")
            
            notification = NotificationService.send_notification(
                client_id=entry.get("client_id", ""),
                tenant_id=entry.get("tenant_id", ""),
                channels=channels,
                message=message,
                notification_type="waitlist_expiration"
            )
            
            logger.info(f"Sent expiration notification for entry {entry['_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending expiration notification: {e}")
            return False


# Create singleton instance
expiration_service = ExpirationService()
