"""
Celery tasks for waitlist management
"""
from celery import Task
from app.celery_app import celery_app
from app.database import Database
from app.services.termii_service import send_waitlist_notification
from app.services.availability_service import get_available_slots
from app.services.expiration_service import ExpirationService
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
async def check_waitlist_availability(self):
    """
    Check for available slots and notify waitlist entries
    Runs every 15 minutes
    """
    try:
        db = Database.get_db()
        
        # Get all waiting entries
        waitlist_entries = await db.waitlist.find({
            "status": "waiting"
        }).to_list(length=None)
        
        notified_count = 0
        
        for entry in waitlist_entries:
            try:
                # Check if preferred date is specified
                if not entry.get("preferred_date"):
                    # Check next 7 days
                    check_date = datetime.utcnow()
                else:
                    check_date = entry["preferred_date"]
                
                # Get available slots
                slots = await get_available_slots(
                    entry["stylist_id"] if entry.get("stylist_id") else None,
                    entry["service_id"],
                    check_date,
                    entry["tenant_id"]
                )
                
                if slots:
                    # Format first available slot
                    first_slot = slots[0]
                    slot_str = first_slot.strftime("%B %d, %Y at %I:%M %p")
                    
                    # Send notification
                    success = await send_waitlist_notification(entry, slot_str)
                    
                    if success:
                        # Update waitlist status
                        await db.waitlist.update_one(
                            {"_id": entry["_id"]},
                            {
                                "$set": {
                                    "status": "notified",
                                    "notified_at": datetime.utcnow()
                                }
                            }
                        )
                        notified_count += 1
                        logger.info(f"Waitlist notification sent for entry {entry['_id']}")
            
            except Exception as e:
                logger.error(f"Error checking waitlist entry {entry['_id']}: {e}")
        
        logger.info(f"Waitlist check complete: {notified_count} notifications sent")
        return {"notified": notified_count}
    
    except Exception as e:
        logger.error(f"Error in check_waitlist_availability task: {e}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


@celery_app.task(bind=True, max_retries=3)
def expire_old_waitlist_entries(self):
    """
    Expire waitlist entries older than 30 days (waiting) or 7 days (notified).
    Scheduled to run daily at 2:00 AM.
    
    Requirements: 7.4
    """
    try:
        # Call expiration service
        result = ExpirationService.check_and_expire_entries()
        
        logger.info(
            f"Expiration task completed: "
            f"{result['waiting_expired']} waiting entries expired, "
            f"{result['notified_expired']} notified entries expired, "
            f"Total: {result['total_expired']}"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Error in expire_old_waitlist_entries task: {e}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes

