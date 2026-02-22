"""
Celery tasks for booking reminders
"""
from celery import Task
from app.celery_app import celery_app
from app.database import Database
from app.services.termii_service import send_booking_reminder
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)


class AsyncTask(Task):
    """Base task class that handles async functions"""
    
    def __call__(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run(*args, **kwargs))
    
    async def run(self, *args, **kwargs):
        raise NotImplementedError()


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def send_24_hour_reminders(self):
    """
    Send reminders for bookings 24 hours in advance
    Runs daily at 9 AM
    """
    try:
        db = Database.get_db()
        
        # Calculate time window (24 hours from now, +/- 30 minutes)
        now = datetime.utcnow()
        target_time = now + timedelta(hours=24)
        start_window = target_time - timedelta(minutes=30)
        end_window = target_time + timedelta(minutes=30)
        
        # Find bookings in the time window
        bookings = await db.bookings.find({
            "booking_date": {
                "$gte": start_window,
                "$lte": end_window
            },
            "status": {"$in": ["pending", "confirmed"]},
            "reminder_24h_sent": {"$ne": True}
        }).to_list(length=None)
        
        sent_count = 0
        failed_count = 0
        
        for booking in bookings:
            try:
                # Send reminder
                success = await send_booking_reminder(booking, hours_before=24)
                
                if success:
                    # Mark reminder as sent
                    await db.bookings.update_one(
                        {"_id": booking["_id"]},
                        {
                            "$set": {
                                "reminder_24h_sent": True,
                                "reminder_24h_sent_at": datetime.utcnow()
                            }
                        }
                    )
                    sent_count += 1
                    logger.info(f"24-hour reminder sent for booking {booking['_id']}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to send 24-hour reminder for booking {booking['_id']}")
            
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending 24-hour reminder for booking {booking['_id']}: {e}")
        
        logger.info(f"24-hour reminders: {sent_count} sent, {failed_count} failed")
        return {"sent": sent_count, "failed": failed_count}
    
    except Exception as e:
        logger.error(f"Error in send_24_hour_reminders task: {e}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def send_2_hour_reminders(self):
    """
    Send reminders for bookings 2 hours in advance
    Runs every 30 minutes
    """
    try:
        db = Database.get_db()
        
        # Calculate time window (2 hours from now, +/- 15 minutes)
        now = datetime.utcnow()
        target_time = now + timedelta(hours=2)
        start_window = target_time - timedelta(minutes=15)
        end_window = target_time + timedelta(minutes=15)
        
        # Find bookings in the time window
        bookings = await db.bookings.find({
            "booking_date": {
                "$gte": start_window,
                "$lte": end_window
            },
            "status": {"$in": ["pending", "confirmed"]},
            "reminder_2h_sent": {"$ne": True}
        }).to_list(length=None)
        
        sent_count = 0
        failed_count = 0
        
        for booking in bookings:
            try:
                # Send reminder
                success = await send_booking_reminder(booking, hours_before=2)
                
                if success:
                    # Mark reminder as sent
                    await db.bookings.update_one(
                        {"_id": booking["_id"]},
                        {
                            "$set": {
                                "reminder_2h_sent": True,
                                "reminder_2h_sent_at": datetime.utcnow()
                            }
                        }
                    )
                    sent_count += 1
                    logger.info(f"2-hour reminder sent for booking {booking['_id']}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to send 2-hour reminder for booking {booking['_id']}")
            
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending 2-hour reminder for booking {booking['_id']}: {e}")
        
        logger.info(f"2-hour reminders: {sent_count} sent, {failed_count} failed")
        return {"sent": sent_count, "failed": failed_count}
    
    except Exception as e:
        logger.error(f"Error in send_2_hour_reminders task: {e}")
        raise self.retry(exc=e, countdown=60)  # Retry after 1 minute


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def send_immediate_confirmation(booking_id: str):
    """
    Send immediate booking confirmation
    Called when a booking is created or confirmed
    """
    try:
        db = Database.get_db()
        
        # Get booking
        from bson import ObjectId
        booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
        
        if booking is None:
            logger.error(f"Booking {booking_id} not found")
            return {"success": False, "error": "Booking not found"}
        
        # Send confirmation
        from app.services.termii_service import send_booking_confirmation
        success = await send_booking_confirmation(booking)
        
        if success:
            # Mark confirmation as sent
            await db.bookings.update_one(
                {"_id": ObjectId(booking_id)},
                {
                    "$set": {
                        "confirmation_sent": True,
                        "confirmation_sent_at": datetime.utcnow()
                    }
                }
            )
            logger.info(f"Confirmation sent for booking {booking_id}")
            return {"success": True}
        else:
            logger.warning(f"Failed to send confirmation for booking {booking_id}")
            return {"success": False, "error": "Failed to send message"}
    
    except Exception as e:
        logger.error(f"Error in send_immediate_confirmation task: {e}")
        raise self.retry(exc=e, countdown=60)  # Retry after 1 minute
