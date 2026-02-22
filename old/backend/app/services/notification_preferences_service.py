"""
Notification Preferences Service - Manage user notification settings
"""
from datetime import datetime
from typing import Dict, Optional
from bson import ObjectId
import logging

from app.database import Database
from app.api.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class NotificationPreferencesService:
    """Service for managing notification preferences"""
    
    @staticmethod
    async def get_preferences(
        user_id: str,
        tenant_id: str
    ) -> Dict:
        """Get notification preferences for a user"""
        db = Database.get_db()
        
        # Handle both valid ObjectIds and string IDs
        try:
            user_id_query = ObjectId(user_id) if len(user_id) == 24 else user_id
        except:
            user_id_query = user_id
        
        prefs = db.notification_preferences.find_one({
            "user_id": user_id_query,
            "tenant_id": tenant_id
        })
        
        if not prefs:
            # Return default preferences
            return {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "email_notifications": True,
                "sms_notifications": True,
                "push_notifications": True,
                "booking_confirmations": True,
                "booking_reminders": True,
                "promotions": True,
                "cancellations": True,
                "preferred_contact_method": "email",
                "reminder_times": [24, 2],  # 24 hours and 2 hours before
                "quiet_hours_enabled": False,
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "08:00"
            }
        
        return prefs
    
    @staticmethod
    async def update_preferences(
        user_id: str,
        tenant_id: str,
        preferences: Dict
    ) -> Dict:
        """Update notification preferences"""
        db = Database.get_db()
        
        # Handle both valid ObjectIds and string IDs
        try:
            user_id_query = ObjectId(user_id) if len(user_id) == 24 else user_id
        except:
            user_id_query = user_id
        
        preferences["updated_at"] = datetime.utcnow()
        
        result = db.notification_preferences.find_one_and_update(
            {
                "user_id": user_id_query,
                "tenant_id": tenant_id
            },
            {"$set": preferences},
            upsert=True,
            return_document=True
        )
        
        logger.info(f"Updated notification preferences for user {user_id}")
        return result
    
    @staticmethod
    async def opt_in_email(user_id: str, tenant_id: str) -> Dict:
        """Opt in to email notifications"""
        return await NotificationPreferencesService.update_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences={"email_notifications": True}
        )
    
    @staticmethod
    async def opt_out_email(user_id: str, tenant_id: str) -> Dict:
        """Opt out of email notifications"""
        return await NotificationPreferencesService.update_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences={"email_notifications": False}
        )
    
    @staticmethod
    async def opt_in_sms(user_id: str, tenant_id: str) -> Dict:
        """Opt in to SMS notifications"""
        return await NotificationPreferencesService.update_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences={"sms_notifications": True}
        )
    
    @staticmethod
    async def opt_out_sms(user_id: str, tenant_id: str) -> Dict:
        """Opt out of SMS notifications"""
        return await NotificationPreferencesService.update_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences={"sms_notifications": False}
        )
    
    @staticmethod
    async def set_preferred_contact_method(
        user_id: str,
        tenant_id: str,
        method: str
    ) -> Dict:
        """Set preferred contact method (email, sms, push)"""
        if method not in ["email", "sms", "push"]:
            raise ValueError("Invalid contact method")
        
        return await NotificationPreferencesService.update_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences={"preferred_contact_method": method}
        )
    
    @staticmethod
    async def set_reminder_times(
        user_id: str,
        tenant_id: str,
        reminder_times: list
    ) -> Dict:
        """Set reminder times (in hours before appointment)"""
        return await NotificationPreferencesService.update_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences={"reminder_times": reminder_times}
        )
    
    @staticmethod
    async def enable_quiet_hours(
        user_id: str,
        tenant_id: str,
        start_time: str,
        end_time: str
    ) -> Dict:
        """Enable quiet hours (no notifications during this time)"""
        return await NotificationPreferencesService.update_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences={
                "quiet_hours_enabled": True,
                "quiet_hours_start": start_time,
                "quiet_hours_end": end_time
            }
        )
    
    @staticmethod
    async def disable_quiet_hours(
        user_id: str,
        tenant_id: str
    ) -> Dict:
        """Disable quiet hours"""
        return await NotificationPreferencesService.update_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences={"quiet_hours_enabled": False}
        )


# Singleton instance
notification_preferences_service = NotificationPreferencesService()
