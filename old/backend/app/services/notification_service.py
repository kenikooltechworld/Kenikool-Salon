"""
Notification service - Manages notification rules and delivery
"""
from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId
import logging

from app.database import Database

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications and notification rules"""
    
    # Supported triggers
    SUPPORTED_TRIGGERS = [
        "booking_created",
        "booking_completed",
        "booking_cancelled",
        "payment_received",
        "review_submitted",
        "birthday",
        "anniversary",
        "inactive_client",
        "custom"
    ]
    
    # Supported channels
    SUPPORTED_CHANNELS = ["sms", "email", "whatsapp", "push"]
    
    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()
    
    @staticmethod
    def create_notification_rule(
        tenant_id: str,
        name: str,
        trigger: str,
        channels: List[str],
        message_template: str,
        enabled: bool = True,
        conditions: Optional[Dict] = None
    ) -> Dict:
        """
        Create notification rule
        
        Args:
            tenant_id: Tenant ID
            name: Rule name
            trigger: Trigger event
            channels: List of channels to send via
            message_template: Message template
            enabled: Whether rule is enabled
            conditions: Optional conditions for rule
            
        Returns:
            Notification rule
        """
        db = NotificationService._get_db()
        
        # Validate trigger
        if trigger not in NotificationService.SUPPORTED_TRIGGERS:
            raise ValueError(f"Unsupported trigger: {trigger}")
        
        # Validate channels
        for channel in channels:
            if channel not in NotificationService.SUPPORTED_CHANNELS:
                raise ValueError(f"Unsupported channel: {channel}")
        
        rule = {
            "tenant_id": tenant_id,
            "name": name,
            "trigger": trigger,
            "channels": channels,
            "message_template": message_template,
            "enabled": enabled,
            "conditions": conditions or {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.notification_rules.insert_one(rule)
        rule["_id"] = str(result.inserted_id)
        
        logger.info(f"Created notification rule {name} for tenant {tenant_id}")
        
        return rule
    
    @staticmethod
    def get_notification_rules(
        tenant_id: str,
        trigger: Optional[str] = None,
        enabled_only: bool = False
    ) -> List[Dict]:
        """
        Get notification rules for tenant
        
        Args:
            tenant_id: Tenant ID
            trigger: Optional filter by trigger
            enabled_only: Only return enabled rules
            
        Returns:
            List of notification rules
        """
        db = NotificationService._get_db()
        
        query = {"tenant_id": tenant_id}
        
        if trigger:
            query["trigger"] = trigger
        if enabled_only:
            query["enabled"] = True
        
        rules = list(db.notification_rules.find(query).sort("created_at", -1))
        
        return [
            {
                **r,
                "_id": str(r["_id"]),
                "created_at": r["created_at"].isoformat(),
                "updated_at": r["updated_at"].isoformat()
            }
            for r in rules
        ]
    
    @staticmethod
    def update_notification_rule(
        rule_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        channels: Optional[List[str]] = None,
        message_template: Optional[str] = None,
        enabled: Optional[bool] = None,
        conditions: Optional[Dict] = None
    ) -> Dict:
        """
        Update notification rule
        
        Args:
            rule_id: Rule ID
            tenant_id: Tenant ID
            name: New name
            channels: New channels
            message_template: New message template
            enabled: New enabled status
            conditions: New conditions
            
        Returns:
            Updated rule
        """
        db = NotificationService._get_db()
        
        rule = db.notification_rules.find_one({
            "_id": ObjectId(rule_id),
            "tenant_id": tenant_id
        })
        
        if not rule:
            raise ValueError("Notification rule not found")
        
        # Validate channels if provided
        if channels:
            for channel in channels:
                if channel not in NotificationService.SUPPORTED_CHANNELS:
                    raise ValueError(f"Unsupported channel: {channel}")
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if name is not None:
            update_data["name"] = name
        if channels is not None:
            update_data["channels"] = channels
        if message_template is not None:
            update_data["message_template"] = message_template
        if enabled is not None:
            update_data["enabled"] = enabled
        if conditions is not None:
            update_data["conditions"] = conditions
        
        # Update rule
        db.notification_rules.update_one(
            {"_id": ObjectId(rule_id)},
            {"$set": update_data}
        )
        
        # Get updated rule
        updated = db.notification_rules.find_one({"_id": ObjectId(rule_id)})
        updated["_id"] = str(updated["_id"])
        updated["created_at"] = updated["created_at"].isoformat()
        updated["updated_at"] = updated["updated_at"].isoformat()
        
        return updated
    
    @staticmethod
    def delete_notification_rule(rule_id: str, tenant_id: str) -> Dict:
        """
        Delete notification rule
        
        Args:
            rule_id: Rule ID
            tenant_id: Tenant ID
            
        Returns:
            Deleted rule info
        """
        db = NotificationService._get_db()
        
        rule = db.notification_rules.find_one({
            "_id": ObjectId(rule_id),
            "tenant_id": tenant_id
        })
        
        if not rule:
            raise ValueError("Notification rule not found")
        
        db.notification_rules.delete_one({"_id": ObjectId(rule_id)})
        
        logger.info(f"Deleted notification rule {rule_id}")
        
        return {
            "id": str(rule["_id"]),
            "name": rule["name"],
            "deleted_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def send_notification(
        client_id: str,
        tenant_id: str,
        channels: List[str],
        message: str,
        notification_type: str = "manual"
    ) -> Dict:
        """
        Send notification to client
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            channels: Channels to send via
            message: Message to send
            notification_type: Type of notification
            
        Returns:
            Notification record
        """
        db = NotificationService._get_db()
        
        # Get client
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if not client:
            raise ValueError("Client not found")
        
        # Create notification record
        notification = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "channels": channels,
            "message": message,
            "notification_type": notification_type,
            "status": "pending",
            "sent_at": None,
            "delivery_status": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Send via each channel
        for channel in channels:
            try:
                # In production, integrate with actual messaging services
                # For now, just mark as sent
                notification["delivery_status"][channel] = {
                    "status": "sent",
                    "sent_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                logger.error(f"Error sending notification via {channel}: {e}")
                notification["delivery_status"][channel] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Update notification status
        notification["status"] = "sent"
        notification["sent_at"] = datetime.utcnow()
        
        # Insert notification
        result = db.notifications.insert_one(notification)
        notification["_id"] = str(result.inserted_id)
        
        logger.info(f"Sent notification to client {client_id} via {channels}")
        
        return notification
    
    @staticmethod
    def get_notification_history(
        tenant_id: str,
        client_id: Optional[str] = None,
        notification_type: Optional[str] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get notification history
        
        Args:
            tenant_id: Tenant ID
            client_id: Optional filter by client
            notification_type: Optional filter by type
            status: Optional filter by status
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of notifications
        """
        db = NotificationService._get_db()
        
        query = {"tenant_id": tenant_id}
        
        if client_id:
            query["client_id"] = client_id
        if notification_type:
            query["notification_type"] = notification_type
        if status:
            query["status"] = status
        
        notifications = list(
            db.notifications.find(query)
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        
        return [
            {
                **n,
                "_id": str(n["_id"]),
                "created_at": n["created_at"].isoformat(),
                "updated_at": n["updated_at"].isoformat(),
                "sent_at": n["sent_at"].isoformat() if n.get("sent_at") else None
            }
            for n in notifications
        ]
    
    @staticmethod
    def process_notification_rules(
        tenant_id: str,
        trigger: str,
        client_id: str,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Process notification rules for a trigger event
        
        Args:
            tenant_id: Tenant ID
            trigger: Trigger event
            client_id: Client ID
            context: Additional context for rule evaluation
            
        Returns:
            List of sent notifications
        """
        db = NotificationService._get_db()
        
        # Get enabled rules for this trigger
        rules = db.notification_rules.find({
            "tenant_id": tenant_id,
            "trigger": trigger,
            "enabled": True
        })
        
        sent_notifications = []
        
        for rule in rules:
            try:
                # Evaluate conditions if any
                if rule.get("conditions"):
                    # In production, implement proper condition evaluation
                    pass
                
                # Send notification
                notification = NotificationService.send_notification(
                    client_id=client_id,
                    tenant_id=tenant_id,
                    channels=rule["channels"],
                    message=rule["message_template"],
                    notification_type=f"rule_{rule['_id']}"
                )
                
                sent_notifications.append(notification)
            except Exception as e:
                logger.error(f"Error processing notification rule {rule['_id']}: {e}")
        
        return sent_notifications
    
    @staticmethod
    def notify_waitlist_client(
        waitlist_id: str,
        tenant_id: str,
        template_id: Optional[str] = None
    ) -> bool:
        """
        Send notification to waitlist client with optional template support.
        
        Args:
            waitlist_id: Waitlist entry ID
            tenant_id: Tenant ID
            template_id: Optional notification template ID
            
        Returns:
            True if notification sent successfully
            
        Requirements: 12.2, 12.3, 12.5
        """
        db = NotificationService._get_db()
        
        # Get waitlist entry
        try:
            waitlist_entry = db.waitlist.find_one({
                "_id": ObjectId(waitlist_id),
                "tenant_id": tenant_id
            })
        except Exception:
            logger.error(f"Invalid waitlist ID: {waitlist_id}")
            return False
        
        if not waitlist_entry:
            logger.error(f"Waitlist entry not found: {waitlist_id}")
            return False
        
        # Get template or use default
        template = None
        if template_id:
            try:
                template = db.notification_templates.find_one({
                    "_id": ObjectId(template_id),
                    "tenant_id": tenant_id
                })
            except Exception:
                logger.warning(f"Invalid template ID: {template_id}, using default")
        
        # If no template found, get default or create one
        if not template:
            template = db.notification_templates.find_one({
                "tenant_id": tenant_id,
                "is_default": True
            })
        
        # If still no template, create default
        if not template:
            template = NotificationService._create_default_template(tenant_id)
        
        # Render template with waitlist data
        message = NotificationService._render_template(template["message"], waitlist_entry, tenant_id)
        
        # Send notification via SMS and email if available
        channels = ["sms"]
        if waitlist_entry.get("client_email"):
            channels.append("email")
        
        try:
            notification = NotificationService.send_notification(
                client_id=waitlist_entry.get("client_id", ""),
                tenant_id=tenant_id,
                channels=channels,
                message=message,
                notification_type="waitlist_notification"
            )
            
            logger.info(f"Sent waitlist notification to {waitlist_entry.get('client_phone')}")
            return True
        except Exception as e:
            logger.error(f"Error sending waitlist notification: {e}")
            return False
    
    @staticmethod
    def _render_template(
        template_message: str,
        waitlist_entry: Dict,
        tenant_id: str
    ) -> str:
        """
        Render template by replacing variables with actual values.
        
        Args:
            template_message: Template message with placeholders
            waitlist_entry: Waitlist entry data
            tenant_id: Tenant ID
            
        Returns:
            Rendered message
            
        Requirements: 12.3
        """
        db = NotificationService._get_db()
        
        # Get tenant info for salon_name and salon_phone
        tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        salon_name = tenant.get("business_name", "Our Salon") if tenant else "Our Salon"
        salon_phone = tenant.get("phone", "") if tenant else ""
        
        # Get service name
        service_name = waitlist_entry.get("service_name", "")
        if not service_name and waitlist_entry.get("service_id"):
            try:
                service = db.services.find_one({"_id": ObjectId(waitlist_entry["service_id"])})
                service_name = service.get("name", "") if service else ""
            except Exception:
                pass
        
        # Build variables dict
        variables = {
            "client_name": waitlist_entry.get("client_name", ""),
            "salon_name": salon_name,
            "service_name": service_name,
            "salon_phone": salon_phone
        }
        
        # Replace all variables in template
        message = template_message
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            message = message.replace(placeholder, str(var_value))
        
        return message
    
    @staticmethod
    def _create_default_template(tenant_id: str) -> Dict:
        """
        Create default notification template if none exists.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Default template
            
        Requirements: 12.5
        """
        db = NotificationService._get_db()
        
        default_template = {
            "tenant_id": tenant_id,
            "name": "Default Waitlist Notification",
            "message": "Hi {client_name}! Good news from {salon_name} - we now have availability for {service_name}. Please call us at {salon_phone} or book online to secure your appointment. Reply STOP to unsubscribe.",
            "variables": ["client_name", "salon_name", "service_name", "salon_phone"],
            "is_default": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.notification_templates.insert_one(default_template)
        default_template["_id"] = str(result.inserted_id)
        
        logger.info(f"Created default notification template for tenant {tenant_id}")
        
        return default_template
    
    @staticmethod
    def bulk_notify(
        waitlist_ids: List[str],
        tenant_id: str,
        template_id: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Send notifications to multiple waitlist clients and update their status.
        
        Args:
            waitlist_ids: List of waitlist entry IDs to notify
            tenant_id: Tenant ID for isolation
            template_id: Optional notification template ID
            
        Returns:
            Dict with success_count, failure_count, and failures list
            
        Requirements: 9.3, 9.5
        """
        db = NotificationService._get_db()
        
        success_count = 0
        failure_count = 0
        failures = []
        
        # Process each waitlist entry independently
        for waitlist_id in waitlist_ids:
            try:
                # Validate ObjectId format
                try:
                    obj_id = ObjectId(waitlist_id)
                except Exception:
                    failures.append({
                        "id": waitlist_id,
                        "error": "Invalid waitlist ID format"
                    })
                    failure_count += 1
                    continue
                
                # Get waitlist entry
                waitlist_entry = db.waitlist.find_one({
                    "_id": obj_id,
                    "tenant_id": tenant_id
                })
                
                if not waitlist_entry:
                    failures.append({
                        "id": waitlist_id,
                        "error": "Entry not found or does not belong to tenant"
                    })
                    failure_count += 1
                    continue
                
                # Send notification
                notification_sent = NotificationService.notify_waitlist_client(
                    waitlist_id=waitlist_id,
                    tenant_id=tenant_id,
                    template_id=template_id
                )
                
                if notification_sent:
                    # Update entry status to "notified"
                    db.waitlist.update_one(
                        {"_id": obj_id},
                        {
                            "$set": {
                                "status": "notified",
                                "notified_at": datetime.utcnow(),
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    success_count += 1
                else:
                    failures.append({
                        "id": waitlist_id,
                        "error": "Failed to send notification"
                    })
                    failure_count += 1
                    
            except Exception as e:
                failures.append({
                    "id": waitlist_id,
                    "error": str(e)
                })
                failure_count += 1
        
        logger.info(f"Bulk notify completed: {success_count} succeeded, {failure_count} failed")
        
        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "failures": failures
        }


    @staticmethod
    def send_referral_tracked_notification(
        referrer_id: str,
        referred_client_name: str,
        tenant_id: str
    ) -> Dict:
        """
        Send notification when referral is tracked
        
        Args:
            referrer_id: Referrer client ID
            referred_client_name: Name of referred client
            tenant_id: Tenant ID
            
        Returns:
            Notification record
            
        Validates: REQ-10
        """
        message = f"Great news! {referred_client_name} just signed up using your referral link. You'll earn a reward when they complete their first booking!"
        
        return NotificationService.send_notification(
            client_id=referrer_id,
            tenant_id=tenant_id,
            channels=["email", "sms"],
            message=message,
            notification_type="referral_tracked"
        )
    
    @staticmethod
    def send_reward_earned_notification(
        referrer_id: str,
        referred_client_name: str,
        reward_amount: float,
        tenant_id: str
    ) -> Dict:
        """
        Send notification when reward is earned
        
        Args:
            referrer_id: Referrer client ID
            referred_client_name: Name of referred client
            reward_amount: Reward amount earned
            tenant_id: Tenant ID
            
        Returns:
            Notification record
            
        Validates: REQ-10
        """
        message = f"Congratulations! {referred_client_name} completed their first booking. You've earned ₦{reward_amount:.2f} in referral rewards!"
        
        return NotificationService.send_notification(
            client_id=referrer_id,
            tenant_id=tenant_id,
            channels=["email", "sms"],
            message=message,
            notification_type="reward_earned"
        )
    
    @staticmethod
    def send_rewards_redeemed_notification(
        client_id: str,
        redeemed_amount: float,
        new_balance: float,
        tenant_id: str
    ) -> Dict:
        """
        Send notification when rewards are redeemed
        
        Args:
            client_id: Client ID
            redeemed_amount: Amount redeemed
            new_balance: New pending balance
            tenant_id: Tenant ID
            
        Returns:
            Notification record
            
        Validates: REQ-10
        """
        message = f"Your referral rewards of ₦{redeemed_amount:.2f} have been successfully redeemed and applied to your account. Remaining balance: ₦{new_balance:.2f}"
        
        return NotificationService.send_notification(
            client_id=client_id,
            tenant_id=tenant_id,
            channels=["email", "sms"],
            message=message,
            notification_type="rewards_redeemed"
        )


# Create singleton instance
notification_service = NotificationService()
