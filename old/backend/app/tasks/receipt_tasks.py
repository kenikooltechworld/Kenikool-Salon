"""
Celery tasks for receipt delivery
"""
from celery import Task
from app.celery_app import celery_app
from app.database import Database
from app.services.receipt_service import generate_receipt_text
from app.services.termii_service import send_whatsapp
from bson import ObjectId
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
async def send_receipt(self, payment_id: str):
    """
    Send receipt via WhatsApp/SMS after payment
    """
    try:
        db = Database.get_db()
        
        # Get payment
        payment = await db.payments.find_one({"_id": ObjectId(payment_id)})
        if payment is None:
            logger.error(f"Payment {payment_id} not found")
            return {"success": False, "error": "Payment not found"}
        
        # Get booking
        booking = await db.bookings.find_one({"_id": ObjectId(payment["booking_id"])})
        if booking is None:
            logger.error(f"Booking {payment['booking_id']} not found")
            return {"success": False, "error": "Booking not found"}
        
        # Get tenant
        tenant = await db.tenants.find_one({"_id": ObjectId(payment["tenant_id"])})
        if tenant is None:
            logger.error(f"Tenant {payment['tenant_id']} not found")
            return {"success": False, "error": "Tenant not found"}
        
        # Generate text receipt
        receipt_text = generate_receipt_text(booking, payment, tenant)
        
        # Send via WhatsApp/SMS
        success = await send_whatsapp(booking["client_phone"], receipt_text)
        
        if success:
            # Mark receipt as sent
            await db.payments.update_one(
                {"_id": ObjectId(payment_id)},
                {
                    "$set": {
                        "receipt_sent": True,
                        "receipt_sent_at": datetime.utcnow()
                    }
                }
            )
            logger.info(f"Receipt sent for payment {payment_id}")
            return {"success": True}
        else:
            logger.warning(f"Failed to send receipt for payment {payment_id}")
            return {"success": False, "error": "Failed to send message"}
    
    except Exception as e:
        logger.error(f"Error in send_receipt task: {e}")
        raise self.retry(exc=e, countdown=60)  # Retry after 1 minute


from datetime import datetime
