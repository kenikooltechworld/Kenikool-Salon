"""
Payment Notification Service - Payment-related notifications
Handles payment notifications, reminders, and summaries
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class PaymentNotificationService:
    """Service for payment-related notifications"""
    
    @staticmethod
    def create_payment_notification(
        tenant_id: str,
        payment_id: str,
        notification_type: str,
        recipient_id: str,
        recipient_type: str = "user"
    ) -> Dict:
        """
        Create a notification for a payment event
        
        Args:
            tenant_id: Tenant ID
            payment_id: Payment ID
            notification_type: Type of notification (completed, failed, refunded, manual_recorded, large_payment)
            recipient_id: User or customer ID to notify
            recipient_type: Type of recipient (user, customer)
            
        Returns:
            Dict with notification details
            
        Raises:
            NotFoundException: If payment not found
            BadRequestException: If notification type is invalid
        """
        db = Database.get_db()
        
        try:
            payment_oid = ObjectId(payment_id)
        except Exception:
            raise BadRequestException("Invalid payment ID format")
        
        # Fetch payment
        payment = db.payments.find_one({
            "_id": payment_oid,
            "tenant_id": tenant_id
        })
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        # Validate notification type
        valid_types = ["completed", "failed", "refunded", "manual_recorded", "large_payment"]
        if notification_type not in valid_types:
            raise BadRequestException(f"Invalid notification type: {notification_type}")
        
        # Generate notification message and title
        title, message = PaymentNotificationService._generate_notification_message(
            notification_type, payment
        )
        
        # Create notification record
        notification_data = {
            "tenant_id": tenant_id,
            "payment_id": payment_id,
            "notification_type": notification_type,
            "recipient_id": recipient_id,
            "recipient_type": recipient_type,
            "title": title,
            "message": message,
            "status": "unread",
            "created_at": datetime.utcnow(),
            "read_at": None,
            "sent_at": None
        }
        
        result = db.notifications.insert_one(notification_data)
        notification_id = str(result.inserted_id)
        
        logger.info(
            f"Payment notification created: {notification_id}, "
            f"type: {notification_type}, payment: {payment_id}"
        )
        
        return {
            "notification_id": notification_id,
            "payment_id": payment_id,
            "notification_type": notification_type,
            "title": title,
            "message": message,
            "created_at": notification_data["created_at"]
        }
    
    @staticmethod
    def create_refund_notification(
        tenant_id: str,
        payment_id: str,
        refund_amount: float,
        refund_type: str,
        recipient_id: str,
        recipient_type: str = "user"
    ) -> Dict:
        """
        Create a notification for a refund event
        
        Args:
            tenant_id: Tenant ID
            payment_id: Payment ID
            refund_amount: Amount refunded
            refund_type: Type of refund (full, partial)
            recipient_id: User or customer ID to notify
            recipient_type: Type of recipient (user, customer)
            
        Returns:
            Dict with notification details
        """
        db = Database.get_db()
        
        try:
            payment_oid = ObjectId(payment_id)
        except Exception:
            raise BadRequestException("Invalid payment ID format")
        
        # Fetch payment
        payment = db.payments.find_one({
            "_id": payment_oid,
            "tenant_id": tenant_id
        })
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        # Generate notification message
        if refund_type == "full":
            title = "Full Refund Processed"
            message = f"A full refund of ₦{refund_amount} has been processed for payment {payment.get('reference')}"
        else:
            title = "Partial Refund Processed"
            message = f"A partial refund of ₦{refund_amount} has been processed for payment {payment.get('reference')}"
        
        # Create notification record
        notification_data = {
            "tenant_id": tenant_id,
            "payment_id": payment_id,
            "notification_type": "refund",
            "recipient_id": recipient_id,
            "recipient_type": recipient_type,
            "title": title,
            "message": message,
            "metadata": {
                "refund_amount": refund_amount,
                "refund_type": refund_type
            },
            "status": "unread",
            "created_at": datetime.utcnow(),
            "read_at": None,
            "sent_at": None
        }
        
        result = db.notifications.insert_one(notification_data)
        notification_id = str(result.inserted_id)
        
        logger.info(
            f"Refund notification created: {notification_id}, "
            f"payment: {payment_id}, amount: ₦{refund_amount}"
        )
        
        return {
            "notification_id": notification_id,
            "payment_id": payment_id,
            "notification_type": "refund",
            "title": title,
            "message": message,
            "created_at": notification_data["created_at"]
        }
    
    @staticmethod
    def send_payment_reminder(
        tenant_id: str,
        payment_id: str,
        recipient_id: str
    ) -> Dict:
        """
        Send a reminder notification for a pending payment
        
        Args:
            tenant_id: Tenant ID
            payment_id: Payment ID
            recipient_id: Customer ID to remind
            
        Returns:
            Dict with reminder notification details
        """
        db = Database.get_db()
        
        try:
            payment_oid = ObjectId(payment_id)
        except Exception:
            raise BadRequestException("Invalid payment ID format")
        
        # Fetch payment
        payment = db.payments.find_one({
            "_id": payment_oid,
            "tenant_id": tenant_id
        })
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        # Check if payment is pending
        if payment.get("status") != "pending":
            raise BadRequestException(f"Cannot send reminder for payment with status: {payment.get('status')}")
        
        # Generate reminder message
        title = "Payment Reminder"
        message = f"You have a pending payment of ₦{payment.get('amount')} for booking {payment.get('reference')}. Please complete the payment."
        
        # Create notification record
        notification_data = {
            "tenant_id": tenant_id,
            "payment_id": payment_id,
            "notification_type": "payment_reminder",
            "recipient_id": recipient_id,
            "recipient_type": "customer",
            "title": title,
            "message": message,
            "status": "unread",
            "created_at": datetime.utcnow(),
            "read_at": None,
            "sent_at": None
        }
        
        result = db.notifications.insert_one(notification_data)
        notification_id = str(result.inserted_id)
        
        logger.info(
            f"Payment reminder sent: {notification_id}, "
            f"payment: {payment_id}, customer: {recipient_id}"
        )
        
        return {
            "notification_id": notification_id,
            "payment_id": payment_id,
            "notification_type": "payment_reminder",
            "title": title,
            "message": message,
            "created_at": notification_data["created_at"]
        }
    
    @staticmethod
    def send_daily_payment_summary(
        tenant_id: str,
        recipient_id: str,
        summary_date: Optional[datetime] = None
    ) -> Dict:
        """
        Send a daily payment summary notification
        
        Args:
            tenant_id: Tenant ID
            recipient_id: User ID to send summary to
            summary_date: Date to summarize (default: yesterday)
            
        Returns:
            Dict with summary notification details
        """
        db = Database.get_db()
        
        if not summary_date:
            summary_date = datetime.utcnow() - timedelta(days=1)
        
        # Calculate date range (start of day to end of day)
        start_of_day = summary_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # Fetch payments for the day
        payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "created_at": {
                "$gte": start_of_day,
                "$lt": end_of_day
            }
        }))
        
        # Calculate summary statistics
        total_payments = len(payments)
        total_amount = sum(p.get("amount", 0) for p in payments)
        completed_count = len([p for p in payments if p.get("status") == "completed"])
        failed_count = len([p for p in payments if p.get("status") == "failed"])
        pending_count = len([p for p in payments if p.get("status") == "pending"])
        
        # Generate summary message
        title = f"Daily Payment Summary - {summary_date.strftime('%B %d, %Y')}"
        message = (
            f"Total Payments: {total_payments}\n"
            f"Total Amount: ₦{total_amount}\n"
            f"Completed: {completed_count}\n"
            f"Failed: {failed_count}\n"
            f"Pending: {pending_count}"
        )
        
        # Create notification record
        notification_data = {
            "tenant_id": tenant_id,
            "notification_type": "daily_summary",
            "recipient_id": recipient_id,
            "recipient_type": "user",
            "title": title,
            "message": message,
            "metadata": {
                "summary_date": summary_date.isoformat(),
                "total_payments": total_payments,
                "total_amount": total_amount,
                "completed_count": completed_count,
                "failed_count": failed_count,
                "pending_count": pending_count
            },
            "status": "unread",
            "created_at": datetime.utcnow(),
            "read_at": None,
            "sent_at": None
        }
        
        result = db.notifications.insert_one(notification_data)
        notification_id = str(result.inserted_id)
        
        logger.info(
            f"Daily payment summary sent: {notification_id}, "
            f"date: {summary_date.date()}, user: {recipient_id}"
        )
        
        return {
            "notification_id": notification_id,
            "notification_type": "daily_summary",
            "title": title,
            "message": message,
            "summary_date": summary_date.isoformat(),
            "statistics": {
                "total_payments": total_payments,
                "total_amount": total_amount,
                "completed_count": completed_count,
                "failed_count": failed_count,
                "pending_count": pending_count
            },
            "created_at": notification_data["created_at"]
        }
    
    @staticmethod
    def get_pending_payment_reminders(
        tenant_id: str,
        days_threshold: int = 3
    ) -> List[Dict]:
        """
        Get list of pending payments that should be reminded
        
        Args:
            tenant_id: Tenant ID
            days_threshold: Number of days old before sending reminder
            
        Returns:
            List of pending payments
        """
        db = Database.get_db()
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
        
        # Find pending payments older than threshold
        pending_payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "status": "pending",
            "created_at": {"$lt": cutoff_date}
        }).sort("created_at", 1))
        
        return [
            {
                "id": str(p["_id"]),
                "payment_id": str(p["_id"]),
                "client_id": p.get("client_id"),
                "amount": p.get("amount"),
                "reference": p.get("reference"),
                "created_at": p.get("created_at"),
                "days_pending": (datetime.utcnow() - p.get("created_at")).days
            }
            for p in pending_payments
        ]
    
    @staticmethod
    def _generate_notification_message(notification_type: str, payment: Dict) -> tuple:
        """
        Generate notification title and message based on type
        
        Args:
            notification_type: Type of notification
            payment: Payment document
            
        Returns:
            Tuple of (title, message)
        """
        messages = {
            "completed": (
                "Payment Completed",
                f"Payment of ₦{payment.get('amount')} has been completed successfully. Reference: {payment.get('reference')}"
            ),
            "failed": (
                "Payment Failed",
                f"Payment of ₦{payment.get('amount')} failed. Reference: {payment.get('reference')}. Please try again."
            ),
            "refunded": (
                "Payment Refunded",
                f"Payment of ₦{payment.get('amount')} has been refunded. Reference: {payment.get('reference')}"
            ),
            "manual_recorded": (
                "Manual Payment Recorded",
                f"Manual payment of ₦{payment.get('amount')} has been recorded. Reference: {payment.get('reference')}"
            ),
            "large_payment": (
                "Large Payment Received",
                f"A large payment of ₦{payment.get('amount')} has been received. Reference: {payment.get('reference')}"
            )
        }
        
        return messages.get(notification_type, ("Payment Notification", "A payment event has occurred"))


# Singleton instance
payment_notification_service = PaymentNotificationService()
