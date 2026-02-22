"""
Package Notification Service - Handles notifications for package-related events
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging

from app.database import Database
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class PackageNotificationService:
    """Service for sending package-related notifications"""

    # Notification templates
    TEMPLATES = {
        "purchase_confirmation": {
            "subject": "Package Purchase Confirmation",
            "template": "package_purchase_confirmation"
        },
        "expiration_warning": {
            "subject": "Your Package is Expiring Soon",
            "template": "package_expiration_warning"
        },
        "expiration_notice": {
            "subject": "Your Package Has Expired",
            "template": "package_expiration_notice"
        },
        "completion_notice": {
            "subject": "Package Fully Redeemed",
            "template": "package_completion_notice"
        },
        "gift_notification": {
            "subject": "You've Received a Gift Package",
            "template": "package_gift_notification"
        },
        "transfer_notification": {
            "subject": "Package Transfer Notification",
            "template": "package_transfer_notification"
        }
    }

    @staticmethod
    def send_purchase_confirmation(
        tenant_id: str,
        client_id: str,
        purchase_id: str,
        package_name: str,
        amount_paid: float,
        expiration_date: datetime
    ) -> bool:
        """
        Send purchase confirmation notification
        
        Requirements: 12.1
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            purchase_id: Package purchase ID
            package_name: Name of the package
            amount_paid: Amount paid for the package
            expiration_date: Expiration date of the package
            
        Returns:
            True if notification sent successfully
        """
        try:
            db = Database.get_db()
            
            # Get client info
            client = db.clients.find_one({"_id": ObjectId(client_id)})
            if not client:
                logger.warning(f"Client {client_id} not found for purchase confirmation")
                return False
            
            # Prepare notification data
            notification_data = {
                "client_id": client_id,
                "client_name": client.get("name"),
                "client_email": client.get("email"),
                "package_name": package_name,
                "amount_paid": amount_paid,
                "expiration_date": expiration_date.strftime("%B %d, %Y"),
                "purchase_id": purchase_id
            }
            
            # Send notification
            notification_service = NotificationService(db)
            notification_service.send_notification(
                tenant_id=tenant_id,
                client_id=client_id,
                notification_type="package_purchase",
                title=PackageNotificationService.TEMPLATES["purchase_confirmation"]["subject"],
                message=f"Thank you for purchasing {package_name}! Your package will expire on {expiration_date.strftime('%B %d, %Y')}.",
                data=notification_data
            )
            
            logger.info(f"Purchase confirmation sent for purchase {purchase_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending purchase confirmation: {e}")
            return False

    @staticmethod
    def send_expiration_warning(
        tenant_id: str,
        client_id: str,
        purchase_id: str,
        package_name: str,
        expiration_date: datetime,
        remaining_credits: Dict[str, int]
    ) -> bool:
        """
        Send expiration warning notification (7 days before expiration)
        
        Requirements: 6.4, 12.2
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            purchase_id: Package purchase ID
            package_name: Name of the package
            expiration_date: Expiration date of the package
            remaining_credits: Dict of remaining credits per service
            
        Returns:
            True if notification sent successfully
        """
        try:
            db = Database.get_db()
            
            # Get client info
            client = db.clients.find_one({"_id": ObjectId(client_id)})
            if not client:
                logger.warning(f"Client {client_id} not found for expiration warning")
                return False
            
            # Format remaining credits
            credits_text = ", ".join(
                [f"{count} {service}" for service, count in remaining_credits.items()]
            )
            
            # Prepare notification data
            notification_data = {
                "client_id": client_id,
                "client_name": client.get("name"),
                "client_email": client.get("email"),
                "package_name": package_name,
                "expiration_date": expiration_date.strftime("%B %d, %Y"),
                "remaining_credits": credits_text,
                "purchase_id": purchase_id
            }
            
            # Send notification
            notification_service = NotificationService(db)
            notification_service.send_notification(
                tenant_id=tenant_id,
                client_id=client_id,
                notification_type="package_expiration_warning",
                title=PackageNotificationService.TEMPLATES["expiration_warning"]["subject"],
                message=f"Your {package_name} package expires on {expiration_date.strftime('%B %d, %Y')}. You have {credits_text} remaining.",
                data=notification_data
            )
            
            logger.info(f"Expiration warning sent for purchase {purchase_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending expiration warning: {e}")
            return False

    @staticmethod
    def send_expiration_notice(
        tenant_id: str,
        client_id: str,
        purchase_id: str,
        package_name: str,
        expiration_date: datetime,
        unused_value: float
    ) -> bool:
        """
        Send expiration notice when package expires
        
        Requirements: 12.3
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            purchase_id: Package purchase ID
            package_name: Name of the package
            expiration_date: Expiration date of the package
            unused_value: Value of unused credits
            
        Returns:
            True if notification sent successfully
        """
        try:
            db = Database.get_db()
            
            # Get client info
            client = db.clients.find_one({"_id": ObjectId(client_id)})
            if not client:
                logger.warning(f"Client {client_id} not found for expiration notice")
                return False
            
            # Prepare notification data
            notification_data = {
                "client_id": client_id,
                "client_name": client.get("name"),
                "client_email": client.get("email"),
                "package_name": package_name,
                "expiration_date": expiration_date.strftime("%B %d, %Y"),
                "unused_value": unused_value,
                "purchase_id": purchase_id
            }
            
            # Send notification
            notification_service = NotificationService(db)
            notification_service.send_notification(
                tenant_id=tenant_id,
                client_id=client_id,
                notification_type="package_expired",
                title=PackageNotificationService.TEMPLATES["expiration_notice"]["subject"],
                message=f"Your {package_name} package expired on {expiration_date.strftime('%B %d, %Y')}. You had ${unused_value:.2f} in unused credits.",
                data=notification_data
            )
            
            logger.info(f"Expiration notice sent for purchase {purchase_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending expiration notice: {e}")
            return False

    @staticmethod
    def send_completion_notice(
        tenant_id: str,
        client_id: str,
        purchase_id: str,
        package_name: str
    ) -> bool:
        """
        Send completion notice when package is fully redeemed
        
        Requirements: 12.4
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            purchase_id: Package purchase ID
            package_name: Name of the package
            
        Returns:
            True if notification sent successfully
        """
        try:
            db = Database.get_db()
            
            # Get client info
            client = db.clients.find_one({"_id": ObjectId(client_id)})
            if not client:
                logger.warning(f"Client {client_id} not found for completion notice")
                return False
            
            # Prepare notification data
            notification_data = {
                "client_id": client_id,
                "client_name": client.get("name"),
                "client_email": client.get("email"),
                "package_name": package_name,
                "purchase_id": purchase_id
            }
            
            # Send notification
            notification_service = NotificationService(db)
            notification_service.send_notification(
                tenant_id=tenant_id,
                client_id=client_id,
                notification_type="package_completed",
                title=PackageNotificationService.TEMPLATES["completion_notice"]["subject"],
                message=f"Congratulations! You've fully redeemed your {package_name} package.",
                data=notification_data
            )
            
            logger.info(f"Completion notice sent for purchase {purchase_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending completion notice: {e}")
            return False

    @staticmethod
    def send_gift_notification(
        tenant_id: str,
        recipient_client_id: str,
        purchase_id: str,
        package_name: str,
        gift_from_name: str,
        gift_message: Optional[str] = None
    ) -> bool:
        """
        Send gift notification to recipient
        
        Requirements: 12.5, 20.4
        
        Args:
            tenant_id: Tenant ID
            recipient_client_id: Recipient client ID
            purchase_id: Package purchase ID
            package_name: Name of the package
            gift_from_name: Name of the gift giver
            gift_message: Optional gift message
            
        Returns:
            True if notification sent successfully
        """
        try:
            db = Database.get_db()
            
            # Get recipient info
            recipient = db.clients.find_one({"_id": ObjectId(recipient_client_id)})
            if not recipient:
                logger.warning(f"Recipient {recipient_client_id} not found for gift notification")
                return False
            
            # Prepare notification data
            notification_data = {
                "client_id": recipient_client_id,
                "client_name": recipient.get("name"),
                "client_email": recipient.get("email"),
                "package_name": package_name,
                "gift_from": gift_from_name,
                "gift_message": gift_message,
                "purchase_id": purchase_id
            }
            
            # Build message
            message = f"{gift_from_name} sent you a gift: {package_name} package!"
            if gift_message:
                message += f"\n\nMessage: {gift_message}"
            
            # Send notification
            notification_service = NotificationService(db)
            notification_service.send_notification(
                tenant_id=tenant_id,
                client_id=recipient_client_id,
                notification_type="package_gift",
                title=PackageNotificationService.TEMPLATES["gift_notification"]["subject"],
                message=message,
                data=notification_data
            )
            
            logger.info(f"Gift notification sent for purchase {purchase_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending gift notification: {e}")
            return False

    @staticmethod
    def send_transfer_notification(
        tenant_id: str,
        from_client_id: str,
        to_client_id: str,
        purchase_id: str,
        package_name: str
    ) -> bool:
        """
        Send transfer notification to both clients
        
        Requirements: 11.5
        
        Args:
            tenant_id: Tenant ID
            from_client_id: Client transferring the package
            to_client_id: Client receiving the package
            purchase_id: Package purchase ID
            package_name: Name of the package
            
        Returns:
            True if notifications sent successfully
        """
        try:
            db = Database.get_db()
            
            # Get client info
            from_client = db.clients.find_one({"_id": ObjectId(from_client_id)})
            to_client = db.clients.find_one({"_id": ObjectId(to_client_id)})
            
            if not from_client or not to_client:
                logger.warning(f"Client not found for transfer notification")
                return False
            
            notification_service = NotificationService(db)
            
            # Send notification to sender
            notification_service.send_notification(
                tenant_id=tenant_id,
                client_id=from_client_id,
                notification_type="package_transferred",
                title=PackageNotificationService.TEMPLATES["transfer_notification"]["subject"],
                message=f"Your {package_name} package has been transferred to {to_client.get('name')}.",
                data={
                    "client_id": from_client_id,
                    "package_name": package_name,
                    "transferred_to": to_client.get("name"),
                    "purchase_id": purchase_id
                }
            )
            
            # Send notification to recipient
            notification_service.send_notification(
                tenant_id=tenant_id,
                client_id=to_client_id,
                notification_type="package_received",
                title="Package Transfer Received",
                message=f"You've received a {package_name} package from {from_client.get('name')}.",
                data={
                    "client_id": to_client_id,
                    "package_name": package_name,
                    "transferred_from": from_client.get("name"),
                    "purchase_id": purchase_id
                }
            )
            
            logger.info(f"Transfer notifications sent for purchase {purchase_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending transfer notification: {e}")
            return False
