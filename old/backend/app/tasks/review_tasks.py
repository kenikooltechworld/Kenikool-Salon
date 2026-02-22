"""
Review request tasks
"""
from celery import shared_task
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_review_request(self, booking_id: str):
    """
    Send review request after service completion
    """
    try:
        from app.database import Database
        from app.services.termii_service import send_whatsapp_message, send_sms
        from bson import ObjectId
        import asyncio
        
        async def _send_request():
            db = Database.get_db()
            
            # Get booking
            booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
            
            if booking is None:
                logger.warning(f"Booking not found: {booking_id}")
                return
            
            # Check if already reviewed
            existing_review = await db.reviews.find_one({"booking_id": booking_id})
            if existing_review:
                logger.info(f"Booking already reviewed: {booking_id}")
                return
            
            # Get tenant
            tenant = await db.tenants.find_one({"_id": ObjectId(booking["tenant_id"])})
            
            if tenant is None:
                logger.warning(f"Tenant not found: {booking['tenant_id']}")
                return
            
            # Build review request message
            message = (
                f"Hi {booking['client_name']}! 👋\n\n"
                f"Thank you for visiting {tenant['salon_name']}. "
                f"We hope you enjoyed your {booking['service_name']} with {booking['stylist_name']}.\n\n"
                f"We'd love to hear your feedback! Please rate your experience:\n"
                f"Reply with a number from 1-5 (5 being excellent)\n\n"
                f"Your feedback helps us serve you better. 💇‍♀️✨"
            )
            
            # Try WhatsApp first, fallback to SMS
            success = await send_whatsapp_message(
                booking["client_phone"],
                message,
                booking["tenant_id"]
            )
            
            if not success:
                success = await send_sms(
                    booking["client_phone"],
                    message,
                    booking["tenant_id"]
                )
            
            if success:
                logger.info(f"Review request sent for booking: {booking_id}")
            else:
                logger.error(f"Failed to send review request for booking: {booking_id}")
                raise Exception("Failed to send review request")
        
        # Run async function
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(_send_request())
        else:
            loop.run_until_complete(_send_request())
    
    except Exception as e:
        logger.error(f"Error sending review request: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task
def send_pending_review_requests():
    """
    Send review requests for completed bookings (runs daily)
    Sends requests for bookings completed in the last 24 hours
    """
    try:
        from app.database import Database
        import asyncio
        
        async def _send_requests():
            db = Database.get_db()
            
            # Find completed bookings from last 24 hours without reviews
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            cursor = db.bookings.find({
                "status": "completed",
                "completed_at": {"$gte": yesterday}
            })
            
            count = 0
            async for booking in cursor:
                booking_id = str(booking["_id"])
                
                # Check if already reviewed
                existing_review = await db.reviews.find_one({"booking_id": booking_id})
                if existing_review:
                    continue
                
                # Queue review request
                send_review_request.delay(booking_id)
                count += 1
            
            logger.info(f"Queued {count} review requests")
        
        # Run async function
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(_send_requests())
        else:
            loop.run_until_complete(_send_requests())
    
    except Exception as e:
        logger.error(f"Error in send_pending_review_requests: {e}")

