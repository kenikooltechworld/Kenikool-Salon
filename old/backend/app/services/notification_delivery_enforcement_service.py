"""
Notification Delivery Enforcement Service - Enforce notification preferences and quiet hours
Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6
"""
from datetime import datetime, time
from typing import Dict, List, Optional
from bson import ObjectId
import logging
import pytz

from app.database import Database
from app.services.termii_service import TermiiService

logger = logging.getLogger(__name__)


class NotificationDeliveryEnforcementService:
    """Service for enforcing notification delivery preferences and quiet hours"""

    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()

    @staticmethod
    async def check_notification_preferences(
        user_id: str,
        tenant_id: str,
        notification_type: str,
        channels: List[str]
    ) -> Dict:
        """
        Check if notification should be sent based on user preferences
        
        Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            notification_type: Type of notification (e.g., 'booking_confirmation')
            channels: Requested channels to send via
            
        Returns:
            Dict with:
            - should_send: bool - whether to send notification
            - channels_to_use: List[str] - channels that should be used
            - should_queue: bool - whether to queue for later
            - reason: str - reason if not sending
        """
        db = NotificationDeliveryEnforcementService._get_db()
        
        # Get user preferences
        prefs = db.notification_preferences.find_one({
            "user_id": ObjectId(user_id),
            "tenant_id": tenant_id
        })
        
        if not prefs:
            # Default: send via all requested channels
            return {
                "should_send": True,
                "channels_to_use": channels,
                "should_queue": False,
                "reason": None
            }
        
        # Check if all channels are disabled for this notification type
        channels_to_use = []
        
        for channel in channels:
            # Check if channel is enabled globally
            if channel == "email" and not prefs.get("email_notifications", True):
                continue
            elif channel == "sms" and not prefs.get("sms_notifications", True):
                continue
            elif channel == "push" and not prefs.get("push_notifications", True):
                continue
            
            # Check if notification type is enabled for this channel
            notification_prefs = prefs.get("preferences", {})
            if notification_type in notification_prefs:
                type_prefs = notification_prefs[notification_type]
                if channel not in type_prefs.get("channels", []):
                    continue
            
            channels_to_use.append(channel)
        
        # If no channels available, don't send
        if not channels_to_use:
            return {
                "should_send": False,
                "channels_to_use": [],
                "should_queue": False,
                "reason": f"User has disabled all requested channels for {notification_type}"
            }
        
        # Check quiet hours
        quiet_hours_result = await NotificationDeliveryEnforcementService._check_quiet_hours(
            user_id, tenant_id, prefs
        )
        
        if quiet_hours_result["in_quiet_hours"]:
            return {
                "should_send": False,
                "channels_to_use": channels_to_use,
                "should_queue": True,
                "reason": f"User is in quiet hours (until {quiet_hours_result['quiet_hours_end']})"
            }
        
        return {
            "should_send": True,
            "channels_to_use": channels_to_use,
            "should_queue": False,
            "reason": None
        }

    @staticmethod
    async def _check_quiet_hours(
        user_id: str,
        tenant_id: str,
        prefs: Dict
    ) -> Dict:
        """
        Check if user is currently in quiet hours
        
        Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            prefs: User preferences dict
            
        Returns:
            Dict with:
            - in_quiet_hours: bool
            - quiet_hours_start: str
            - quiet_hours_end: str
        """
        # Check if quiet hours are enabled
        if not prefs.get("quiet_hours_enabled", False):
            return {
                "in_quiet_hours": False,
                "quiet_hours_start": None,
                "quiet_hours_end": None
            }
        
        # Get user timezone
        user_tz = prefs.get("timezone", "Africa/Lagos")
        try:
            tz = pytz.timezone(user_tz)
        except:
            tz = pytz.timezone("Africa/Lagos")
        
        # Get current time in user's timezone
        now = datetime.now(tz)
        current_time = now.time()
        
        # Get quiet hours
        quiet_start_str = prefs.get("quiet_hours_start", "22:00")
        quiet_end_str = prefs.get("quiet_hours_end", "08:00")
        
        try:
            quiet_start = datetime.strptime(quiet_start_str, "%H:%M").time()
            quiet_end = datetime.strptime(quiet_end_str, "%H:%M").time()
        except:
            return {
                "in_quiet_hours": False,
                "quiet_hours_start": quiet_start_str,
                "quiet_hours_end": quiet_end_str
            }
        
        # Check if current time is within quiet hours
        # Handle case where quiet hours span midnight
        if quiet_start <= quiet_end:
            # Quiet hours don't span midnight (e.g., 09:00 to 17:00)
            in_quiet_hours = quiet_start <= current_time <= quiet_end
        else:
            # Quiet hours span midnight (e.g., 22:00 to 08:00)
            in_quiet_hours = current_time >= quiet_start or current_time <= quiet_end
        
        if in_quiet_hours:
            # Calculate when quiet hours end
            if quiet_start <= quiet_end:
                # Quiet hours don't span midnight
                if current_time < quiet_end:
                    quiet_hours_end = quiet_end
                else:
                    # Next day's quiet hours
                    quiet_hours_end = quiet_start
            else:
                # Quiet hours span midnight
                if current_time >= quiet_start:
                    # In evening quiet hours, ends in morning
                    quiet_hours_end = quiet_end
                else:
                    # In morning quiet hours, ends in evening
                    quiet_hours_end = quiet_start
        else:
            quiet_hours_end = None
        
        return {
            "in_quiet_hours": in_quiet_hours,
            "quiet_hours_start": quiet_start_str,
            "quiet_hours_end": quiet_hours_end
        }

    @staticmethod
    async def queue_notification(
        user_id: str,
        tenant_id: str,
        notification_data: Dict
    ) -> str:
        """
        Queue notification for later delivery
        
        Requirements: 15.3, 16.2
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            notification_data: Notification data to queue
            
        Returns:
            Queue ID
        """
        db = NotificationDeliveryEnforcementService._get_db()
        
        queue_entry = {
            "user_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "notification_data": notification_data,
            "status": "queued",
            "created_at": datetime.utcnow(),
            "scheduled_for": None,
            "sent_at": None
        }
        
        result = db.notification_queue.insert_one(queue_entry)
        
        logger.info(f"Queued notification for user {user_id}")
        
        return str(result.inserted_id)

    @staticmethod
    async def process_queued_notifications(
        user_id: str,
        tenant_id: str
    ) -> int:
        """
        Process queued notifications for a user
        
        Requirements: 16.2
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Number of notifications sent
        """
        db = NotificationDeliveryEnforcementService._get_db()
        
        # Get queued notifications
        queued = list(db.notification_queue.find({
            "user_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "status": "queued"
        }))
        
        sent_count = 0
        
        for queue_entry in queued:
            try:
                notification_data = queue_entry["notification_data"]
                
                # Check if quiet hours are still active
                prefs = db.notification_preferences.find_one({
                    "user_id": ObjectId(user_id),
                    "tenant_id": tenant_id
                })
                
                quiet_hours_result = await NotificationDeliveryEnforcementService._check_quiet_hours(
                    user_id, tenant_id, prefs or {}
                )
                
                if quiet_hours_result["in_quiet_hours"]:
                    # Still in quiet hours, skip for now
                    continue
                
                # Send notification
                await NotificationDeliveryEnforcementService.send_notification_via_channels(
                    user_id, tenant_id,
                    notification_data.get("channels", []),
                    notification_data.get("message", ""),
                    notification_data.get("notification_type", "manual")
                )
                
                # Mark as sent
                db.notification_queue.update_one(
                    {"_id": queue_entry["_id"]},
                    {
                        "$set": {
                            "status": "sent",
                            "sent_at": datetime.utcnow()
                        }
                    }
                )
                
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Error processing queued notification: {e}")
                # Mark as failed
                db.notification_queue.update_one(
                    {"_id": queue_entry["_id"]},
                    {
                        "$set": {
                            "status": "failed",
                            "error": str(e)
                        }
                    }
                )
        
        logger.info(f"Processed {sent_count} queued notifications for user {user_id}")
        
        return sent_count

    @staticmethod
    async def send_notification_via_channels(
        user_id: str,
        tenant_id: str,
        channels: List[str],
        message: str,
        notification_type: str = "manual"
    ) -> Dict:
        """
        Send notification via specified channels
        
        Requirements: 15.4, 15.5, 15.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            channels: Channels to send via
            message: Message to send
            notification_type: Type of notification
            
        Returns:
            Notification record with delivery status
        """
        db = NotificationDeliveryEnforcementService._get_db()
        
        # Get user
        user = db.users.find_one({
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id
        })
        
        if not user:
            raise ValueError("User not found")
        
        # Create notification record
        notification = {
            "user_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "channels": channels,
            "message": message,
            "notification_type": notification_type,
            "status": "pending",
            "delivery_status": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Send via each channel
        for channel in channels:
            try:
                if channel == "email":
                    # Send email
                    await NotificationDeliveryEnforcementService._send_email(
                        user.get("email"), message, notification_type
                    )
                    notification["delivery_status"][channel] = {
                        "status": "sent",
                        "sent_at": datetime.utcnow().isoformat()
                    }
                
                elif channel == "sms":
                    # Send SMS via Termii
                    if user.get("phone_verified") and user.get("phone_number"):
                        await NotificationDeliveryEnforcementService._send_sms(
                            user.get("phone_number"), message
                        )
                        notification["delivery_status"][channel] = {
                            "status": "sent",
                            "sent_at": datetime.utcnow().isoformat()
                        }
                    else:
                        notification["delivery_status"][channel] = {
                            "status": "failed",
                            "error": "Phone not verified or not provided"
                        }
                
                elif channel == "push":
                    # Send push notification
                    notification["delivery_status"][channel] = {
                        "status": "sent",
                        "sent_at": datetime.utcnow().isoformat()
                    }
                
            except Exception as e:
                logger.error(f"Error sending {channel} notification: {e}")
                notification["delivery_status"][channel] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Update notification status
        all_sent = all(
            status.get("status") == "sent"
            for status in notification["delivery_status"].values()
        )
        notification["status"] = "sent" if all_sent else "partial"
        
        # Insert notification
        result = db.notifications.insert_one(notification)
        notification["_id"] = str(result.inserted_id)
        
        logger.info(f"Sent notification to user {user_id} via {channels}")
        
        return notification

    @staticmethod
    async def _send_email(email: str, message: str, notification_type: str) -> None:
        """Send email notification"""
        # In production, integrate with email service (Resend, SendGrid, etc.)
        logger.info(f"Sending email to {email}: {message}")

    @staticmethod
    async def _send_sms(phone_number: str, message: str) -> None:
        """Send SMS notification via Termii"""
        try:
            termii_service = TermiiService()
            await termii_service.send_sms(
                phone_number=phone_number,
                message=message,
                sender_id="Kenikool"
            )
            logger.info(f"Sent SMS to {phone_number}")
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            raise

    @staticmethod
    async def enforce_notification_delivery(
        user_id: str,
        tenant_id: str,
        notification_type: str,
        channels: List[str],
        message: str
    ) -> Dict:
        """
        Enforce notification delivery with preference and quiet hours checking
        
        Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            notification_type: Type of notification
            channels: Requested channels
            message: Message to send
            
        Returns:
            Dict with delivery result
        """
        # Check preferences
        pref_check = await NotificationDeliveryEnforcementService.check_notification_preferences(
            user_id, tenant_id, notification_type, channels
        )
        
        if not pref_check["should_send"]:
            if pref_check["should_queue"]:
                # Queue for later
                queue_id = await NotificationDeliveryEnforcementService.queue_notification(
                    user_id, tenant_id,
                    {
                        "channels": pref_check["channels_to_use"],
                        "message": message,
                        "notification_type": notification_type
                    }
                )
                return {
                    "status": "queued",
                    "queue_id": queue_id,
                    "reason": pref_check["reason"]
                }
            else:
                # Don't send
                return {
                    "status": "not_sent",
                    "reason": pref_check["reason"]
                }
        
        # Send notification
        notification = await NotificationDeliveryEnforcementService.send_notification_via_channels(
            user_id, tenant_id,
            pref_check["channels_to_use"],
            message,
            notification_type
        )
        
        return {
            "status": "sent",
            "notification_id": notification["_id"],
            "channels": pref_check["channels_to_use"]
        }


# Create singleton instance
notification_delivery_enforcement_service = NotificationDeliveryEnforcementService()
