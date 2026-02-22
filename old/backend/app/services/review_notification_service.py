"""
Review Notification Service - Business logic for review notifications
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class ReviewNotificationService:
    """Service for managing review notifications"""
    
    def __init__(self, db):
        self.db = db
    
    async def send_new_review_notification(
        self,
        tenant_id: str,
        review_id: str,
        client_name: str,
        rating: int,
        service_name: str,
        comment: Optional[str] = None
    ) -> Dict:
        """Send notification for new review"""
        try:
            # Get tenant settings
            settings = self.db.review_settings.find_one({"tenant_id": tenant_id})
            
            if not settings or not settings.get("notification_enabled"):
                logger.info(f"Notifications disabled for tenant {tenant_id}")
                return {"sent": False, "reason": "Notifications disabled"}
            
            # Get tenant owner/admin users
            users = list(self.db.users.find({
                "tenant_id": tenant_id,
                "role": {"$in": ["owner", "admin"]}
            }))
            
            if not users:
                logger.warning(f"No admin users found for tenant {tenant_id}")
                return {"sent": False, "reason": "No admin users"}
            
            # Create notification message
            message = f"New {rating}-star review from {client_name} for {service_name}"
            if comment:
                message += f": {comment[:100]}..."
            
            # Send notifications
            sent_count = 0
            
            for user in users:
                # Check user notification preferences
                user_prefs = self.db.notification_preferences.find_one({
                    "user_id": user["_id"],
                    "tenant_id": tenant_id
                })
                
                if not user_prefs:
                    user_prefs = {
                        "email_enabled": settings.get("email_enabled", True),
                        "in_app_enabled": settings.get("in_app_enabled", True)
                    }
                
                # Send in-app notification
                if user_prefs.get("in_app_enabled", True):
                    await self._send_in_app_notification(
                        user_id=str(user["_id"]),
                        tenant_id=tenant_id,
                        title="New Review",
                        message=message,
                        review_id=review_id,
                        notification_type="new_review"
                    )
                    sent_count += 1
                
                # Send email notification
                if user_prefs.get("email_enabled", True):
                    await self._send_email_notification(
                        user_email=user.get("email"),
                        tenant_id=tenant_id,
                        subject=f"New {rating}-star review from {client_name}",
                        message=message,
                        review_id=review_id,
                        notification_type="new_review"
                    )
                    sent_count += 1
            
            logger.info(f"Sent {sent_count} notifications for new review {review_id}")
            
            return {
                "sent": True,
                "count": sent_count,
                "review_id": review_id
            }
        
        except Exception as e:
            logger.error(f"Error sending new review notification: {e}")
            raise Exception(f"Failed to send notification: {str(e)}")
    
    async def send_review_response_notification(
        self,
        tenant_id: str,
        review_id: str,
        client_email: str,
        client_name: str,
        responder_name: str,
        response_text: str
    ) -> Dict:
        """Send notification when review is responded to"""
        try:
            # Get tenant settings
            settings = self.db.review_settings.find_one({"tenant_id": tenant_id})
            
            if not settings or not settings.get("notification_enabled"):
                return {"sent": False, "reason": "Notifications disabled"}
            
            # Send email to client
            if settings.get("email_enabled", True):
                await self._send_email_notification(
                    user_email=client_email,
                    tenant_id=tenant_id,
                    subject=f"{responder_name} responded to your review",
                    message=f"Response: {response_text[:200]}...",
                    review_id=review_id,
                    notification_type="review_response"
                )
            
            logger.info(f"Sent response notification for review {review_id}")
            
            return {
                "sent": True,
                "review_id": review_id
            }
        
        except Exception as e:
            logger.error(f"Error sending review response notification: {e}")
            raise Exception(f"Failed to send notification: {str(e)}")
    
    async def send_review_edited_notification(
        self,
        tenant_id: str,
        review_id: str,
        client_email: str,
        client_name: str,
        new_comment: str
    ) -> Dict:
        """Send notification when review is edited"""
        try:
            # Get tenant settings
            settings = self.db.review_settings.find_one({"tenant_id": tenant_id})
            
            if not settings or not settings.get("notification_enabled"):
                return {"sent": False, "reason": "Notifications disabled"}
            
            # Send email to client
            if settings.get("email_enabled", True):
                await self._send_email_notification(
                    user_email=client_email,
                    tenant_id=tenant_id,
                    subject="Your review has been edited",
                    message=f"Updated review: {new_comment[:200]}...",
                    review_id=review_id,
                    notification_type="review_edited"
                )
            
            logger.info(f"Sent edit notification for review {review_id}")
            
            return {
                "sent": True,
                "review_id": review_id
            }
        
        except Exception as e:
            logger.error(f"Error sending review edited notification: {e}")
            raise Exception(f"Failed to send notification: {str(e)}")
    
    async def batch_review_notifications(
        self,
        tenant_id: str,
        hours: int = 1
    ) -> Dict:
        """Batch and send digest notifications for reviews"""
        try:
            # Get tenant settings
            settings = self.db.review_settings.find_one({"tenant_id": tenant_id})
            
            if not settings or not settings.get("digest_mode"):
                return {"sent": False, "reason": "Digest mode disabled"}
            
            # Get recent reviews
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_reviews = list(self.db.reviews.find({
                "tenant_id": tenant_id,
                "created_at": {"$gte": cutoff_time},
                "status": "pending"
            }))
            
            if not recent_reviews:
                return {"sent": False, "reason": "No recent reviews"}
            
            # Get admin users
            users = list(self.db.users.find({
                "tenant_id": tenant_id,
                "role": {"$in": ["owner", "admin"]}
            }))
            
            # Send digest to each admin
            sent_count = 0
            for user in users:
                await self._send_digest_email(
                    user_email=user.get("email"),
                    tenant_id=tenant_id,
                    reviews=recent_reviews,
                    digest_frequency=settings.get("digest_frequency", "daily")
                )
                sent_count += 1
            
            logger.info(f"Sent {sent_count} digest notifications for tenant {tenant_id}")
            
            return {
                "sent": True,
                "count": sent_count,
                "review_count": len(recent_reviews)
            }
        
        except Exception as e:
            logger.error(f"Error batching review notifications: {e}")
            raise Exception(f"Failed to batch notifications: {str(e)}")
    
    async def _send_in_app_notification(
        self,
        user_id: str,
        tenant_id: str,
        title: str,
        message: str,
        review_id: str,
        notification_type: str
    ) -> None:
        """Send in-app notification"""
        try:
            notification_data = {
                "user_id": ObjectId(user_id),
                "tenant_id": tenant_id,
                "title": title,
                "message": message,
                "type": notification_type,
                "reference_id": review_id,
                "reference_type": "review",
                "read": False,
                "created_at": datetime.utcnow()
            }
            
            self.db.notifications.insert_one(notification_data)
            logger.info(f"Sent in-app notification to user {user_id}")
        
        except Exception as e:
            logger.error(f"Error sending in-app notification: {e}")
    
    async def _send_email_notification(
        self,
        user_email: str,
        tenant_id: str,
        subject: str,
        message: str,
        review_id: str,
        notification_type: str
    ) -> None:
        """Send email notification"""
        try:
            # In production, integrate with email service (SendGrid, AWS SES, etc.)
            # For now, just log
            logger.info(f"Email notification sent to {user_email}: {subject}")
            
            # Store email notification record
            email_data = {
                "recipient": user_email,
                "tenant_id": tenant_id,
                "subject": subject,
                "message": message,
                "type": notification_type,
                "reference_id": review_id,
                "reference_type": "review",
                "sent_at": datetime.utcnow(),
                "status": "sent"
            }
            
            self.db.email_notifications.insert_one(email_data)
        
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    async def _send_digest_email(
        self,
        user_email: str,
        tenant_id: str,
        reviews: List[Dict],
        digest_frequency: str
    ) -> None:
        """Send digest email with multiple reviews"""
        try:
            # Build digest message
            digest_message = f"You have {len(reviews)} new reviews:\n\n"
            
            for review in reviews[:10]:  # Limit to 10 reviews per digest
                digest_message += f"- {review.get('rating')} stars from {review.get('client_name')}: "
                digest_message += f"{review.get('comment', '')[:100]}...\n"
            
            if len(reviews) > 10:
                digest_message += f"\n... and {len(reviews) - 10} more reviews"
            
            logger.info(f"Digest email sent to {user_email} ({digest_frequency})")
            
            # Store digest notification record
            digest_data = {
                "recipient": user_email,
                "tenant_id": tenant_id,
                "subject": f"Review Digest - {digest_frequency.capitalize()}",
                "message": digest_message,
                "type": "review_digest",
                "review_count": len(reviews),
                "frequency": digest_frequency,
                "sent_at": datetime.utcnow(),
                "status": "sent"
            }
            
            self.db.email_notifications.insert_one(digest_data)
        
        except Exception as e:
            logger.error(f"Error sending digest email: {e}")
