"""
Review reminder tasks - Automated review reminders for completed bookings
"""
from celery import shared_task
from datetime import datetime, timedelta
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_review_reminders(self):
    """
    Send review reminders for completed bookings
    Runs hourly to check for bookings that need reminders
    """
    try:
        from app.database import get_db
        
        db = get_db()
        
        # Get all tenants with review reminders enabled
        settings = db.review_settings.find({"reminder_enabled": True})
        
        for setting in settings:
            tenant_id = setting["tenant_id"]
            reminder_delay_hours = setting.get("reminder_delay_hours", 24)
            
            # Calculate the time window for reminders
            # Look for bookings completed between (now - delay - 1 hour) and (now - delay)
            now = datetime.utcnow()
            reminder_time_start = now - timedelta(hours=reminder_delay_hours + 1)
            reminder_time_end = now - timedelta(hours=reminder_delay_hours)
            
            # Find completed bookings in this time window
            completed_bookings = db.bookings.find({
                "tenant_id": tenant_id,
                "status": "completed",
                "completed_at": {
                    "$gte": reminder_time_start,
                    "$lte": reminder_time_end
                }
            })
            
            for booking in completed_bookings:
                try:
                    process_booking_reminder(db, tenant_id, booking)
                except Exception as e:
                    logger.error(f"Error processing reminder for booking {booking['_id']}: {e}")
                    continue
        
        logger.info("Review reminders sent successfully")
        return {"status": "success", "message": "Review reminders processed"}
    
    except Exception as e:
        logger.error(f"Error in send_review_reminders: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


def process_booking_reminder(db, tenant_id: str, booking: dict):
    """
    Process reminder for a single booking
    """
    booking_id = str(booking["_id"])
    client_id = booking.get("client_id")
    client_email = booking.get("client_email")
    client_phone = booking.get("client_phone")
    
    # Check if review already exists
    existing_review = db.reviews.find_one({
        "booking_id": booking_id,
        "tenant_id": tenant_id
    })
    
    if existing_review:
        logger.info(f"Review already exists for booking {booking_id}")
        return
    
    # Check if reminder already sent
    reminder_record = db.review_reminders.find_one({
        "booking_id": booking_id,
        "tenant_id": tenant_id
    })
    
    if reminder_record and reminder_record.get("reminder_sent"):
        logger.info(f"Reminder already sent for booking {booking_id}")
        return
    
    # Get tenant settings
    settings = db.review_settings.find_one({"tenant_id": tenant_id})
    if not settings:
        logger.warning(f"No settings found for tenant {tenant_id}")
        return
    
    # Get client info
    client = db.clients.find_one({"_id": ObjectId(client_id)}) if client_id else None
    
    # Send email reminder
    if client_email:
        try:
            send_email_reminder(
                tenant_id=tenant_id,
                client_email=client_email,
                client_name=client.get("name") if client else "Valued Customer",
                booking_id=booking_id,
                settings=settings
            )
        except Exception as e:
            logger.error(f"Error sending email reminder: {e}")
    
    # Send SMS reminder
    if client_phone:
        try:
            send_sms_reminder(
                tenant_id=tenant_id,
                client_phone=client_phone,
                client_name=client.get("name") if client else "Valued Customer",
                booking_id=booking_id,
                settings=settings
            )
        except Exception as e:
            logger.error(f"Error sending SMS reminder: {e}")
    
    # Record reminder sent
    db.review_reminders.update_one(
        {"booking_id": booking_id, "tenant_id": tenant_id},
        {
            "$set": {
                "booking_id": booking_id,
                "tenant_id": tenant_id,
                "client_id": client_id,
                "reminder_sent": True,
                "reminder_sent_at": datetime.utcnow(),
                "email_sent": bool(client_email),
                "sms_sent": bool(client_phone)
            }
        },
        upsert=True
    )
    
    logger.info(f"Reminder processed for booking {booking_id}")


def send_email_reminder(
    tenant_id: str,
    client_email: str,
    client_name: str,
    booking_id: str,
    settings: dict
):
    """
    Send email reminder to client
    """
    from app.services.email_service import EmailService
    
    email_service = EmailService()
    
    # Get review link
    review_link = f"https://yourdomain.com/reviews/new?booking_id={booking_id}"
    
    # Get email template
    template = settings.get("reminder_email_template", "default")
    
    subject = "Share Your Experience - Leave a Review"
    
    body = f"""
    Hi {client_name},
    
    Thank you for visiting us! We'd love to hear about your experience.
    
    Your feedback helps us improve and helps other clients make informed decisions.
    
    Click here to leave a review: {review_link}
    
    Thank you!
    """
    
    try:
        email_service.send_email(
            to=client_email,
            subject=subject,
            body=body,
            html=True
        )
        logger.info(f"Email reminder sent to {client_email}")
    except Exception as e:
        logger.error(f"Failed to send email reminder: {e}")
        raise


def send_sms_reminder(
    tenant_id: str,
    client_phone: str,
    client_name: str,
    booking_id: str,
    settings: dict
):
    """
    Send SMS reminder to client
    """
    from app.services.sms_service import SMSService
    
    sms_service = SMSService()
    
    # Get review link (shortened)
    review_link = f"https://yourdomain.com/r/{booking_id}"
    
    message = f"Hi {client_name}, we'd love your feedback! Leave a review: {review_link}"
    
    try:
        sms_service.send_sms(
            phone=client_phone,
            message=message
        )
        logger.info(f"SMS reminder sent to {client_phone}")
    except Exception as e:
        logger.error(f"Failed to send SMS reminder: {e}")
        raise


@shared_task
def calculate_review_analytics():
    """
    Pre-calculate review analytics for faster loading
    Runs daily to aggregate review data
    """
    try:
        from app.database import get_db
        
        db = get_db()
        
        # Get all tenants
        tenants = db.tenants.find({})
        
        for tenant in tenants:
            tenant_id = str(tenant["_id"])
            
            try:
                # Calculate daily aggregations
                calculate_tenant_analytics(db, tenant_id)
            except Exception as e:
                logger.error(f"Error calculating analytics for tenant {tenant_id}: {e}")
                continue
        
        logger.info("Review analytics calculated successfully")
        return {"status": "success", "message": "Analytics calculated"}
    
    except Exception as e:
        logger.error(f"Error in calculate_review_analytics: {e}")
        raise


def calculate_tenant_analytics(db, tenant_id: str):
    """
    Calculate analytics for a single tenant
    """
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get reviews from last 30 days
    thirty_days_ago = today - timedelta(days=30)
    
    reviews = db.reviews.find({
        "tenant_id": tenant_id,
        "status": "approved",
        "created_at": {"$gte": thirty_days_ago}
    })
    
    reviews_list = list(reviews)
    
    if not reviews_list:
        return
    
    # Calculate metrics
    total_reviews = len(reviews_list)
    average_rating = sum(r.get("rating", 0) for r in reviews_list) / total_reviews if total_reviews > 0 else 0
    
    # Count by rating
    rating_distribution = {
        1: sum(1 for r in reviews_list if r.get("rating") == 1),
        2: sum(1 for r in reviews_list if r.get("rating") == 2),
        3: sum(1 for r in reviews_list if r.get("rating") == 3),
        4: sum(1 for r in reviews_list if r.get("rating") == 4),
        5: sum(1 for r in reviews_list if r.get("rating") == 5),
    }
    
    # Count responses
    reviews_with_response = sum(1 for r in reviews_list if r.get("response"))
    response_rate = (reviews_with_response / total_reviews * 100) if total_reviews > 0 else 0
    
    # Store analytics
    db.review_analytics.update_one(
        {"tenant_id": tenant_id, "date": today},
        {
            "$set": {
                "tenant_id": tenant_id,
                "date": today,
                "total_reviews": total_reviews,
                "average_rating": round(average_rating, 2),
                "rating_distribution": rating_distribution,
                "response_rate": round(response_rate, 2),
                "updated_at": now
            }
        },
        upsert=True
    )
    
    logger.info(f"Analytics calculated for tenant {tenant_id}")


@shared_task
def batch_review_notifications():
    """
    Send batched review notifications
    Runs every 6 hours to send digest emails
    """
    try:
        from app.database import get_db
        
        db = get_db()
        
        # Get all tenants with digest notifications enabled
        settings = db.review_settings.find({
            "notification_enabled": True,
            "notification_digest": True
        })
        
        for setting in settings:
            tenant_id = setting["tenant_id"]
            
            try:
                send_notification_digest(db, tenant_id)
            except Exception as e:
                logger.error(f"Error sending digest for tenant {tenant_id}: {e}")
                continue
        
        logger.info("Notification digests sent successfully")
        return {"status": "success", "message": "Digests sent"}
    
    except Exception as e:
        logger.error(f"Error in batch_review_notifications: {e}")
        raise


def send_notification_digest(db, tenant_id: str):
    """
    Send digest notification for new reviews
    """
    # Get new reviews from last 6 hours
    six_hours_ago = datetime.utcnow() - timedelta(hours=6)
    
    new_reviews = db.reviews.find({
        "tenant_id": tenant_id,
        "status": "pending",
        "created_at": {"$gte": six_hours_ago}
    })
    
    reviews_list = list(new_reviews)
    
    if not reviews_list:
        return
    
    # Get tenant owner email
    tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
    if not tenant or not tenant.get("owner_email"):
        return
    
    # Send digest email
    try:
        from app.services.email_service import EmailService
        
        email_service = EmailService()
        
        subject = f"New Reviews Digest - {len(reviews_list)} new review(s)"
        
        body = f"""
        You have {len(reviews_list)} new review(s) awaiting moderation.
        
        Reviews:
        """
        
        for review in reviews_list:
            body += f"\n- {review.get('client_name')}: {review.get('rating')} stars - {review.get('comment', '')[:100]}"
        
        body += f"\n\nReview them here: https://yourdomain.com/dashboard/reviews"
        
        email_service.send_email(
            to=tenant.get("owner_email"),
            subject=subject,
            body=body,
            html=True
        )
        
        logger.info(f"Digest sent to {tenant.get('owner_email')}")
    except Exception as e:
        logger.error(f"Failed to send digest: {e}")
        raise
