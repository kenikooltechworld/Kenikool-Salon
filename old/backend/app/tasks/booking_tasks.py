"""
Celery tasks for booking management automation
Includes recurring bookings, inquiry expiration, waitlist notifications, and family payment reminders
"""
from celery import Task
from app.celery_app import celery_app
from app.database import Database
from datetime import datetime, timedelta
import logging
import asyncio
from bson import ObjectId
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AsyncTask(Task):
    """Base task class that handles async functions"""
    
    def __call__(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run(*args, **kwargs))
    
    async def run(self, *args, **kwargs):
        raise NotImplementedError()


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def send_booking_reminders(self):
    """
    Send reminders for bookings based on client preferences
    Runs every hour to check for bookings needing reminders
    Supports both 24h and 2h reminders
    """
    try:
        db = Database.get_db()
        now = datetime.utcnow()
        
        sent_count = 0
        failed_count = 0
        
        # Check for 24-hour reminders
        target_24h = now + timedelta(hours=24)
        start_24h = target_24h - timedelta(minutes=30)
        end_24h = target_24h + timedelta(minutes=30)
        
        bookings_24h = await db.bookings.find({
            "booking_date": {"$gte": start_24h, "$lte": end_24h},
            "status": {"$in": ["pending", "confirmed"]},
            "reminder_24h_sent": {"$ne": True}
        }).to_list(length=None)
        
        for booking in bookings_24h:
            try:
                # Get client preferences
                client = await db.clients.find_one({"_id": booking.get("client_id")})
                if not client:
                    continue
                
                # Send via preferred channel (SMS/WhatsApp)
                channel = client.get("preferred_contact_method", "sms")
                success = await _send_reminder_message(booking, client, channel, hours_before=24)
                
                if success:
                    await db.bookings.update_one(
                        {"_id": booking["_id"]},
                        {
                            "$set": {
                                "reminder_24h_sent": True,
                                "reminder_24h_sent_at": now
                            }
                        }
                    )
                    sent_count += 1
                    logger.info(f"24h reminder sent for booking {booking['_id']} via {channel}")
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending 24h reminder for booking {booking['_id']}: {e}")
        
        # Check for 2-hour reminders
        target_2h = now + timedelta(hours=2)
        start_2h = target_2h - timedelta(minutes=15)
        end_2h = target_2h + timedelta(minutes=15)
        
        bookings_2h = await db.bookings.find({
            "booking_date": {"$gte": start_2h, "$lte": end_2h},
            "status": {"$in": ["pending", "confirmed"]},
            "reminder_2h_sent": {"$ne": True}
        }).to_list(length=None)
        
        for booking in bookings_2h:
            try:
                client = await db.clients.find_one({"_id": booking.get("client_id")})
                if not client:
                    continue
                
                channel = client.get("preferred_contact_method", "sms")
                success = await _send_reminder_message(booking, client, channel, hours_before=2)
                
                if success:
                    await db.bookings.update_one(
                        {"_id": booking["_id"]},
                        {
                            "$set": {
                                "reminder_2h_sent": True,
                                "reminder_2h_sent_at": now
                            }
                        }
                    )
                    sent_count += 1
                    logger.info(f"2h reminder sent for booking {booking['_id']} via {channel}")
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending 2h reminder for booking {booking['_id']}: {e}")
        
        logger.info(f"Booking reminders: {sent_count} sent, {failed_count} failed")
        return {"sent": sent_count, "failed": failed_count}
    
    except Exception as e:
        logger.error(f"Error in send_booking_reminders task: {e}")
        raise self.retry(exc=e, countdown=300)


async def _send_reminder_message(booking: Dict[str, Any], client: Dict[str, Any], channel: str, hours_before: int) -> bool:
    """Helper function to send reminder message via SMS or WhatsApp"""
    try:
        # Get service and stylist details
        db = Database.get_db()
        service = await db.services.find_one({"_id": booking.get("service_id")})
        stylist = await db.stylists.find_one({"_id": booking.get("stylist_id")})
        
        # Format booking date
        booking_date = booking.get("booking_date")
        if isinstance(booking_date, str):
            booking_date = datetime.fromisoformat(booking_date.replace('Z', '+00:00'))
        
        date_str = booking_date.strftime("%B %d, %Y at %I:%M %p")
        
        # Create message
        message = f"Hi {client.get('name', 'there')}! "
        if hours_before == 24:
            message += f"This is a reminder that you have an appointment tomorrow ({date_str}) "
        else:
            message += f"Your appointment is in 2 hours ({date_str}) "
        
        if service:
            message += f"for {service.get('name')} "
        if stylist:
            message += f"with {stylist.get('name')} "
        
        message += "at our salon. See you soon!"
        
        # Send via appropriate channel
        if channel == "whatsapp":
            from app.services.termii_service import send_whatsapp
            return await send_whatsapp(client.get("phone"), message)
        else:
            from app.services.termii_service import send_sms
            return await send_sms(client.get("phone"), message)
            
    except Exception as e:
        logger.error(f"Error sending reminder message: {e}")
        return False


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def process_recurring_bookings(self):
    """
    Generate upcoming recurring bookings
    Runs daily to create bookings for the next period
    """
    try:
        db = Database.get_db()
        now = datetime.utcnow()
        
        # Find active recurring booking templates
        templates = await db.recurring_booking_templates.find({
            "is_active": True,
            "$or": [
                {"end_date": {"$exists": False}},
                {"end_date": None},
                {"end_date": {"$gte": now}}
            ]
        }).to_list(length=None)
        
        created_count = 0
        skipped_count = 0
        failed_count = 0
        
        for template in templates:
            try:
                # Calculate next occurrence date
                last_occurrence = template.get("last_occurrence_date", template.get("start_date"))
                if isinstance(last_occurrence, str):
                    last_occurrence = datetime.fromisoformat(last_occurrence.replace('Z', '+00:00'))
                
                frequency = template.get("frequency", "weekly")
                
                # Calculate next date based on frequency
                if frequency == "daily":
                    next_date = last_occurrence + timedelta(days=1)
                elif frequency == "weekly":
                    next_date = last_occurrence + timedelta(weeks=1)
                elif frequency == "monthly":
                    # Add one month (approximate)
                    next_date = last_occurrence + timedelta(days=30)
                else:
                    logger.warning(f"Unknown frequency {frequency} for template {template['_id']}")
                    continue
                
                # Check if we should create this occurrence
                # Only create if next_date is within the next 7 days
                if next_date > now + timedelta(days=7):
                    continue
                
                # Check if end date has passed
                end_date = template.get("end_date")
                if end_date:
                    if isinstance(end_date, str):
                        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    if next_date > end_date:
                        # Deactivate template
                        await db.recurring_booking_templates.update_one(
                            {"_id": template["_id"]},
                            {"$set": {"is_active": False}}
                        )
                        continue
                
                # Check for conflicts
                from app.services.conflict_detection_service import conflict_detection_service
                conflicts = await conflict_detection_service.check_conflicts(
                    stylist_id=str(template.get("stylist_id")),
                    booking_date=next_date,
                    duration=template.get("duration", 60),
                    exclude_booking_id=None
                )
                
                if conflicts:
                    # Handle based on skip_conflicts setting
                    if template.get("skip_conflicts", False):
                        skipped_count += 1
                        logger.info(f"Skipped conflicting occurrence for template {template['_id']}")
                        # Update last occurrence date to skip this one
                        await db.recurring_booking_templates.update_one(
                            {"_id": template["_id"]},
                            {"$set": {"last_occurrence_date": next_date}}
                        )
                        continue
                    else:
                        # Notify salon owner about conflict
                        logger.warning(f"Conflict detected for template {template['_id']}, skipping")
                        skipped_count += 1
                        continue
                
                # Create the booking
                booking_data = {
                    "client_id": template.get("client_id"),
                    "service_id": template.get("service_id"),
                    "stylist_id": template.get("stylist_id"),
                    "booking_date": next_date,
                    "duration": template.get("duration", 60),
                    "status": "confirmed",
                    "notes": template.get("notes", ""),
                    "recurring_template_id": template["_id"],
                    "created_at": now,
                    "updated_at": now
                }
                
                result = await db.bookings.insert_one(booking_data)
                
                # Update template's last occurrence date
                await db.recurring_booking_templates.update_one(
                    {"_id": template["_id"]},
                    {
                        "$set": {"last_occurrence_date": next_date},
                        "$inc": {"occurrences_created": 1}
                    }
                )
                
                created_count += 1
                logger.info(f"Created recurring booking {result.inserted_id} from template {template['_id']}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error processing template {template['_id']}: {e}")
        
        logger.info(f"Recurring bookings: {created_count} created, {skipped_count} skipped, {failed_count} failed")
        return {"created": created_count, "skipped": skipped_count, "failed": failed_count}
    
    except Exception as e:
        logger.error(f"Error in process_recurring_bookings task: {e}")
        raise self.retry(exc=e, countdown=300)


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def expire_old_inquiries(self):
    """
    Expire service inquiries older than 7 days
    Runs daily to clean up pending inquiries
    """
    try:
        db = Database.get_db()
        now = datetime.utcnow()
        cutoff_date = now - timedelta(days=7)
        
        # Find pending inquiries older than 7 days
        old_inquiries = await db.service_inquiries.find({
            "status": "pending",
            "created_at": {"$lt": cutoff_date}
        }).to_list(length=None)
        
        expired_count = 0
        notified_count = 0
        
        for inquiry in old_inquiries:
            try:
                # Mark as expired
                await db.service_inquiries.update_one(
                    {"_id": inquiry["_id"]},
                    {
                        "$set": {
                            "status": "expired",
                            "expired_at": now
                        }
                    }
                )
                expired_count += 1
                
                # Send notification to client
                client = await db.clients.find_one({"_id": inquiry.get("client_id")})
                if client and client.get("phone"):
                    message = (
                        f"Hi {client.get('name', 'there')}! Your service inquiry from "
                        f"{inquiry.get('created_at').strftime('%B %d')} has expired. "
                        f"Please submit a new inquiry if you're still interested."
                    )
                    
                    try:
                        from app.services.termii_service import send_sms
                        success = await send_sms(client.get("phone"), message)
                        if success:
                            notified_count += 1
                    except Exception as e:
                        logger.error(f"Error sending expiry notification: {e}")
                
                logger.info(f"Expired inquiry {inquiry['_id']}")
                
            except Exception as e:
                logger.error(f"Error expiring inquiry {inquiry['_id']}: {e}")
        
        logger.info(f"Expired inquiries: {expired_count} expired, {notified_count} notified")
        return {"expired": expired_count, "notified": notified_count}
    
    except Exception as e:
        logger.error(f"Error in expire_old_inquiries task: {e}")
        raise self.retry(exc=e, countdown=300)


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def sync_waitlist_notifications(self, cancelled_booking_id: str):
    """
    Notify waitlisted clients when a booking is cancelled
    Triggered when a booking is cancelled
    """
    try:
        db = Database.get_db()
        
        # Get cancelled booking details
        booking = await db.bookings.find_one({"_id": ObjectId(cancelled_booking_id)})
        if not booking:
            logger.error(f"Booking {cancelled_booking_id} not found")
            return {"success": False, "error": "Booking not found"}
        
        # Find matching waitlist entries
        # Match by service, date range, and stylist (if specified)
        booking_date = booking.get("booking_date")
        if isinstance(booking_date, str):
            booking_date = datetime.fromisoformat(booking_date.replace('Z', '+00:00'))
        
        # Look for waitlist entries within +/- 3 days
        date_start = booking_date - timedelta(days=3)
        date_end = booking_date + timedelta(days=3)
        
        query = {
            "status": "active",
            "service_id": booking.get("service_id"),
            "preferred_date": {"$gte": date_start, "$lte": date_end}
        }
        
        # If stylist was specified in booking, match it
        if booking.get("stylist_id"):
            query["$or"] = [
                {"stylist_id": booking.get("stylist_id")},
                {"stylist_id": {"$exists": False}}
            ]
        
        waitlist_entries = await db.waitlist.find(query).sort("priority", -1).to_list(length=10)
        
        notified_count = 0
        
        for entry in waitlist_entries:
            try:
                # Get client details
                client = await db.clients.find_one({"_id": entry.get("client_id")})
                if not client or not client.get("phone"):
                    continue
                
                # Get service details
                service = await db.services.find_one({"_id": entry.get("service_id")})
                service_name = service.get("name", "your requested service") if service else "your requested service"
                
                # Send notification
                message = (
                    f"Hi {client.get('name', 'there')}! Good news! "
                    f"A slot has opened up for {service_name} on {booking_date.strftime('%B %d, %Y')}. "
                    f"Book now before it's taken!"
                )
                
                from app.services.termii_service import send_sms
                success = await send_sms(client.get("phone"), message)
                
                if success:
                    # Update waitlist entry
                    await db.waitlist.update_one(
                        {"_id": entry["_id"]},
                        {
                            "$set": {
                                "notified_at": datetime.utcnow(),
                                "notification_count": entry.get("notification_count", 0) + 1
                            }
                        }
                    )
                    notified_count += 1
                    logger.info(f"Notified waitlist entry {entry['_id']}")
                
            except Exception as e:
                logger.error(f"Error notifying waitlist entry {entry['_id']}: {e}")
        
        logger.info(f"Waitlist notifications: {notified_count} sent for booking {cancelled_booking_id}")
        return {"notified": notified_count}
    
    except Exception as e:
        logger.error(f"Error in sync_waitlist_notifications task: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def send_family_payment_reminders(self):
    """
    Send payment reminders to family accounts with outstanding balance
    Runs weekly to remind families about unpaid bookings
    """
    try:
        db = Database.get_db()
        now = datetime.utcnow()
        
        # Find family accounts with outstanding balance above threshold
        threshold = 100.0  # Minimum balance to trigger reminder
        
        family_accounts = await db.family_accounts.find({
            "is_active": True
        }).to_list(length=None)
        
        sent_count = 0
        failed_count = 0
        
        for account in family_accounts:
            try:
                # Calculate outstanding balance
                from app.services.family_account_service import family_account_service
                balance = await family_account_service.get_outstanding_balance(str(account["_id"]))
                
                if balance < threshold:
                    continue
                
                # Get unpaid bookings
                unpaid_bookings = await db.bookings.find({
                    "family_account_id": account["_id"],
                    "payment_status": {"$in": ["pending", "deferred"]},
                    "status": {"$in": ["completed", "confirmed"]}
                }).to_list(length=None)
                
                if not unpaid_bookings:
                    continue
                
                # Get primary account holder
                primary_member_id = account.get("primary_member_id")
                primary_client = await db.clients.find_one({"_id": primary_member_id})
                
                if not primary_client or not primary_client.get("phone"):
                    continue
                
                # Create breakdown message
                booking_count = len(unpaid_bookings)
                message = (
                    f"Hi {primary_client.get('name', 'there')}! "
                    f"Your family account has {booking_count} unpaid booking(s) "
                    f"with a total balance of ${balance:.2f}. "
                    f"Please visit our salon or call us to settle your account. Thank you!"
                )
                
                # Send reminder
                from app.services.termii_service import send_sms
                success = await send_sms(primary_client.get("phone"), message)
                
                if success:
                    # Update last reminder date
                    await db.family_accounts.update_one(
                        {"_id": account["_id"]},
                        {
                            "$set": {
                                "last_payment_reminder": now
                            }
                        }
                    )
                    sent_count += 1
                    logger.info(f"Payment reminder sent to family account {account['_id']}")
                else:
                    failed_count += 1
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending reminder to family account {account['_id']}: {e}")
        
        logger.info(f"Family payment reminders: {sent_count} sent, {failed_count} failed")
        return {"sent": sent_count, "failed": failed_count}
    
    except Exception as e:
        logger.error(f"Error in send_family_payment_reminders task: {e}")
        raise self.retry(exc=e, countdown=300)


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def update_family_loyalty_points(self, booking_id: str):
    """
    Update family loyalty points after a completed booking
    Triggered when a booking is marked as completed
    """
    try:
        db = Database.get_db()
        
        # Get booking details
        booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            logger.error(f"Booking {booking_id} not found")
            return {"success": False, "error": "Booking not found"}
        
        # Check if booking is associated with a family account
        family_account_id = booking.get("family_account_id")
        if not family_account_id:
            return {"success": True, "message": "Not a family booking"}
        
        # Calculate points (e.g., 1 point per dollar spent)
        amount = booking.get("total_price", 0)
        points = int(amount)
        
        # Update family account points
        await db.family_accounts.update_one(
            {"_id": family_account_id},
            {
                "$inc": {"loyalty_points": points}
            }
        )
        
        # Get family account details
        family_account = await db.family_accounts.find_one({"_id": family_account_id})
        if not family_account:
            return {"success": False, "error": "Family account not found"}
        
        new_balance = family_account.get("loyalty_points", 0) + points
        
        # Notify family members
        members = family_account.get("members", [])
        for member in members:
            try:
                client = await db.clients.find_one({"_id": member.get("client_id")})
                if client and client.get("phone"):
                    message = (
                        f"Hi {client.get('name', 'there')}! "
                        f"Your family earned {points} loyalty points. "
                        f"Total points: {new_balance}. Keep booking to earn more rewards!"
                    )
                    
                    from app.services.termii_service import send_sms
                    await send_sms(client.get("phone"), message)
            except Exception as e:
                logger.error(f"Error notifying family member: {e}")
        
        logger.info(f"Updated loyalty points for family account {family_account_id}: +{points}")
        return {"success": True, "points_added": points, "new_balance": new_balance}
    
    except Exception as e:
        logger.error(f"Error in update_family_loyalty_points task: {e}")
        raise self.retry(exc=e, countdown=60)



@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def send_feedback_requests(self):
    """
    Send feedback requests to clients after completed bookings
    Runs daily to find recently completed bookings
    """
    try:
        db = Database.get_db()
        now = datetime.utcnow()
        
        # Find completed bookings from the last 24 hours that haven't received feedback request
        yesterday = now - timedelta(days=1)
        
        bookings = await db.bookings.find({
            "status": "completed",
            "completed_at": {"$gte": yesterday, "$lte": now},
            "feedback_request_sent": {"$ne": True}
        }).to_list(length=None)
        
        sent_count = 0
        failed_count = 0
        
        for booking in bookings:
            try:
                # Get client details
                client = await db.clients.find_one({"_id": booking.get("client_id")})
                if not client or not client.get("phone"):
                    continue
                
                # Create feedback request message
                service_name = booking.get("service_name", "your service")
                message = (
                    f"Hi {client.get('name', 'there')}! "
                    f"Thank you for choosing us for {service_name}. "
                    f"We'd love to hear your feedback! "
                    f"Please rate your experience and help us serve you better."
                )
                
                # Send via preferred channel
                channel = client.get("preferred_contact_method", "sms")
                from app.services.termii_service import send_sms, send_whatsapp
                
                if channel == "whatsapp":
                    success = await send_whatsapp(client.get("phone"), message)
                else:
                    success = await send_sms(client.get("phone"), message)
                
                if success:
                    await db.bookings.update_one(
                        {"_id": booking["_id"]},
                        {
                            "$set": {
                                "feedback_request_sent": True,
                                "feedback_request_sent_at": now
                            }
                        }
                    )
                    sent_count += 1
                    logger.info(f"Feedback request sent for booking {booking['_id']}")
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending feedback request for booking {booking['_id']}: {e}")
        
        logger.info(f"Feedback requests: {sent_count} sent, {failed_count} failed")
        return {"sent": sent_count, "failed": failed_count}
    
    except Exception as e:
        logger.error(f"Error in send_feedback_requests task: {e}")
        raise self.retry(exc=e, countdown=300)


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def send_birthday_greetings(self):
    """
    Send birthday greetings to clients on their birthday
    Runs daily to check for birthdays
    """
    try:
        db = Database.get_db()
        now = datetime.utcnow()
        today = now.date()
        
        # Find clients with birthday today
        clients = await db.clients.find({
            "date_of_birth": {"$exists": True}
        }).to_list(length=None)
        
        sent_count = 0
        failed_count = 0
        
        for client in clients:
            try:
                dob = client.get("date_of_birth")
                if not dob or not client.get("phone"):
                    continue
                
                # Check if birthday is today
                if isinstance(dob, datetime):
                    dob_date = dob.date()
                elif isinstance(dob, str):
                    try:
                        dob_date = datetime.fromisoformat(dob).date()
                    except:
                        continue
                else:
                    continue
                
                if dob_date.month != today.month or dob_date.day != today.day:
                    continue
                
                # Check if greeting already sent this year
                last_greeting = client.get("last_birthday_greeting")
                if last_greeting and isinstance(last_greeting, datetime):
                    if last_greeting.year == now.year:
                        continue
                
                # Create birthday message with special offer
                message = (
                    f"🎉 Happy Birthday {client.get('name', 'there')}! 🎉 "
                    f"Celebrate your special day with us! "
                    f"Enjoy 20% off your next booking. "
                    f"We wish you a wonderful year ahead!"
                )
                
                # Send via preferred channel
                channel = client.get("preferred_contact_method", "sms")
                from app.services.termii_service import send_sms, send_whatsapp
                
                if channel == "whatsapp":
                    success = await send_whatsapp(client.get("phone"), message)
                else:
                    success = await send_sms(client.get("phone"), message)
                
                if success:
                    await db.clients.update_one(
                        {"_id": client["_id"]},
                        {
                            "$set": {
                                "last_birthday_greeting": now
                            }
                        }
                    )
                    sent_count += 1
                    logger.info(f"Birthday greeting sent to client {client['_id']}")
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending birthday greeting to client {client.get('_id')}: {e}")
        
        logger.info(f"Birthday greetings: {sent_count} sent, {failed_count} failed")
        return {"sent": sent_count, "failed": failed_count}
    
    except Exception as e:
        logger.error(f"Error in send_birthday_greetings task: {e}")
        raise self.retry(exc=e, countdown=300)


@celery_app.task(base=AsyncTask, bind=True, max_retries=3)
async def send_reengagement_messages(self):
    """
    Send re-engagement messages to inactive clients
    Runs weekly to find clients who haven't booked in 60+ days
    """
    try:
        db = Database.get_db()
        now = datetime.utcnow()
        
        # Find clients inactive for 60+ days
        inactive_threshold = now - timedelta(days=60)
        
        clients = await db.clients.find({
            "last_visit_date": {"$lt": inactive_threshold},
            "last_reengagement_message": {"$not": {"$gte": now - timedelta(days=30)}}
        }).to_list(length=100)  # Limit to 100 per run
        
        sent_count = 0
        failed_count = 0
        
        for client in clients:
            try:
                if not client.get("phone"):
                    continue
                
                # Calculate days since last visit
                last_visit = client.get("last_visit_date")
                if not last_visit:
                    continue
                
                days_inactive = (now - last_visit).days
                
                # Create personalized re-engagement message
                message = (
                    f"Hi {client.get('name', 'there')}! "
                    f"We miss you! It's been {days_inactive} days since your last visit. "
                    f"Book your next appointment and enjoy 15% off! "
                    f"We'd love to see you again soon."
                )
                
                # Send via preferred channel
                channel = client.get("preferred_contact_method", "sms")
                from app.services.termii_service import send_sms, send_whatsapp
                
                if channel == "whatsapp":
                    success = await send_whatsapp(client.get("phone"), message)
                else:
                    success = await send_sms(client.get("phone"), message)
                
                if success:
                    await db.clients.update_one(
                        {"_id": client["_id"]},
                        {
                            "$set": {
                                "last_reengagement_message": now
                            }
                        }
                    )
                    sent_count += 1
                    logger.info(f"Re-engagement message sent to client {client['_id']}")
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending re-engagement message to client {client.get('_id')}: {e}")
        
        logger.info(f"Re-engagement messages: {sent_count} sent, {failed_count} failed")
        return {"sent": sent_count, "failed": failed_count}
    
    except Exception as e:
        logger.error(f"Error in send_reengagement_messages task: {e}")
        raise self.retry(exc=e, countdown=300)
