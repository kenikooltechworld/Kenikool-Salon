"""
Gift Card Background Tasks
Celery tasks for gift card operations including email delivery, expiration management, and bulk creation
"""

from celery import shared_task
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging
from bson import ObjectId

from app.database import Database
from app.services.gift_card_email_service import GiftCardEmailService
from app.services.pos_service import POSService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_gift_card_email_task(self, card_id: str, tenant_id: str, recipient_email: str, 
                               recipient_name: Optional[str] = None, message: Optional[str] = None):
    """
    Send gift card email with retry logic
    
    Args:
        card_id: Gift card ID
        tenant_id: Tenant ID
        recipient_email: Recipient email address
        recipient_name: Optional recipient name
        message: Optional personal message
    """
    try:
        import asyncio
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            GiftCardEmailService.send_gift_card_delivery_email(
                card_id=card_id,
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                message=message
            )
        )
        
        loop.close()
        
        if result.get("success"):
            logger.info(f"Gift card email sent successfully: {card_id}")
            return result
        else:
            # Retry on failure
            raise Exception(f"Email delivery failed: {result.get('error')}")
            
    except Exception as exc:
        logger.error(f"Error sending gift card email: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_scheduled_gift_card_email_task(self, card_id: str, tenant_id: str):
    """
    Send scheduled gift card emails
    
    Args:
        card_id: Gift card ID
        tenant_id: Tenant ID
    """
    try:
        db = Database.get_db()
        
        # Get gift card
        gift_card = db.gift_cards.find_one({
            "_id": ObjectId(card_id),
            "tenant_id": tenant_id,
            "delivery_status": "scheduled"
        })
        
        if not gift_card:
            logger.warning(f"Gift card not found or not scheduled: {card_id}")
            return {"success": False, "error": "Card not found or not scheduled"}
        
        # Check if scheduled time has arrived
        scheduled_delivery = gift_card.get("scheduled_delivery")
        if scheduled_delivery and scheduled_delivery > datetime.now(timezone.utc):
            logger.info(f"Scheduled delivery not yet due: {card_id}")
            return {"success": False, "error": "Scheduled time not reached"}
        
        # Send email
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            GiftCardEmailService.send_gift_card_delivery_email(
                card_id=card_id,
                recipient_email=gift_card.get("recipient_email"),
                recipient_name=gift_card.get("recipient_name"),
                message=gift_card.get("message")
            )
        )
        
        loop.close()
        
        if result.get("success"):
            logger.info(f"Scheduled gift card email sent: {card_id}")
            return result
        else:
            raise Exception(f"Email delivery failed: {result.get('error')}")
            
    except Exception as exc:
        logger.error(f"Error sending scheduled gift card email: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def check_gift_card_expiration_task():
    """
    Daily task to check for expiring gift cards and send reminders
    Sends reminders at 30, 7, and 1 days before expiration
    """
    try:
        db = Database.get_db()
        
        # Calculate dates for reminders
        now = datetime.now(timezone.utc)
        reminder_dates = {
            30: now + timedelta(days=30),
            7: now + timedelta(days=7),
            1: now + timedelta(days=1)
        }
        
        for days, target_date in reminder_dates.items():
            # Find cards expiring on this date
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            expiring_cards = db.gift_cards.find({
                "expires_at": {"$gte": start_of_day, "$lte": end_of_day},
                "status": {"$in": ["active", "partially_redeemed"]},
                f"reminder_{days}d": {"$ne": True}  # Not already sent
            })
            
            for card in expiring_cards:
                try:
                    # Send reminder email
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    result = loop.run_until_complete(
                        GiftCardEmailService.send_expiration_reminder(
                            card_id=str(card["_id"]),
                            days_until_expiration=days
                        )
                    )
                    
                    loop.close()
                    
                    if result.get("success"):
                        logger.info(f"Expiration reminder sent for card {card['card_number']}")
                    else:
                        logger.error(f"Failed to send expiration reminder: {card['card_number']}")
                        
                except Exception as e:
                    logger.error(f"Error sending expiration reminder: {str(e)}")
                    continue
        
        # Mark expired cards
        expired_cards = db.gift_cards.find({
            "expires_at": {"$lt": now},
            "status": {"$ne": "expired"}
        })
        
        for card in expired_cards:
            db.gift_cards.update_one(
                {"_id": card["_id"]},
                {
                    "$set": {
                        "status": "expired",
                        "expired_at": now
                    },
                    "$push": {
                        "audit_log": {
                            "action": "card_expired",
                            "timestamp": now,
                            "details": {}
                        }
                    }
                }
            )
            logger.info(f"Card marked as expired: {card['card_number']}")
        
        logger.info("Gift card expiration check completed")
        return {"success": True, "message": "Expiration check completed"}
        
    except Exception as e:
        logger.error(f"Error in expiration check task: {str(e)}")
        return {"success": False, "error": str(e)}


@shared_task
def bulk_create_gift_cards_task(tenant_id: str, cards_data: List[Dict], created_by: str):
    """
    Bulk create gift cards from CSV data
    
    Args:
        tenant_id: Tenant ID
        cards_data: List of gift card data dictionaries
        created_by: User ID who initiated the bulk creation
    """
    try:
        db = Database.get_db()
        created_cards = []
        failed_cards = []
        
        for idx, card_data in enumerate(cards_data):
            try:
                # Create gift card
                gift_card = POSService.create_gift_card(
                    tenant_id=tenant_id,
                    amount=card_data.get("amount"),
                    card_type=card_data.get("card_type", "physical"),
                    recipient_name=card_data.get("recipient_name"),
                    recipient_email=card_data.get("recipient_email"),
                    message=card_data.get("message"),
                    expiration_months=card_data.get("expiration_months", 12),
                    created_by=created_by,
                    design_theme=card_data.get("design_theme", "default"),
                    activation_required=card_data.get("activation_required", False),
                    pin=card_data.get("pin")
                )
                
                created_cards.append({
                    "card_id": gift_card.get("id"),
                    "card_number": gift_card.get("card_number"),
                    "amount": gift_card.get("amount")
                })
                
                # If digital card with email, send immediately
                if card_data.get("card_type") == "digital" and card_data.get("recipient_email"):
                    send_gift_card_email_task.delay(
                        card_id=gift_card.get("id"),
                        tenant_id=tenant_id,
                        recipient_email=card_data.get("recipient_email"),
                        recipient_name=card_data.get("recipient_name"),
                        message=card_data.get("message")
                    )
                
                logger.info(f"Bulk create: Card {idx + 1}/{len(cards_data)} created successfully")
                
            except Exception as e:
                logger.error(f"Error creating card {idx + 1}: {str(e)}")
                failed_cards.append({
                    "index": idx + 1,
                    "error": str(e),
                    "data": card_data
                })
        
        # Store bulk creation result
        bulk_result = {
            "tenant_id": tenant_id,
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc),
            "total_requested": len(cards_data),
            "total_created": len(created_cards),
            "total_failed": len(failed_cards),
            "created_cards": created_cards,
            "failed_cards": failed_cards
        }
        
        db.gift_card_bulk_operations.insert_one(bulk_result)
        
        logger.info(f"Bulk creation completed: {len(created_cards)} created, {len(failed_cards)} failed")
        
        return {
            "success": True,
            "total_created": len(created_cards),
            "total_failed": len(failed_cards),
            "created_cards": created_cards,
            "failed_cards": failed_cards
        }
        
    except Exception as e:
        logger.error(f"Error in bulk create task: {str(e)}")
        return {"success": False, "error": str(e)}


@shared_task
def process_failed_deliveries_task():
    """
    Retry failed gift card email deliveries
    Processes cards with delivery_status = 'failed' and retries up to 3 times
    """
    try:
        db = Database.get_db()
        
        # Find cards with failed deliveries
        failed_cards = db.gift_cards.find({
            "delivery_status": "failed",
            "delivery_attempts": {"$lt": 3}
        })
        
        retry_count = 0
        for card in failed_cards:
            try:
                # Retry sending email
                send_gift_card_email_task.delay(
                    card_id=str(card["_id"]),
                    tenant_id=card["tenant_id"],
                    recipient_email=card.get("recipient_email"),
                    recipient_name=card.get("recipient_name"),
                    message=card.get("message")
                )
                
                retry_count += 1
                logger.info(f"Retry queued for card {card['card_number']}")
                
            except Exception as e:
                logger.error(f"Error queuing retry for card {card['card_number']}: {str(e)}")
        
        logger.info(f"Failed delivery retry task completed: {retry_count} retries queued")
        
        return {
            "success": True,
            "retries_queued": retry_count
        }
        
    except Exception as e:
        logger.error(f"Error in failed delivery retry task: {str(e)}")
        return {"success": False, "error": str(e)}


@shared_task
def cleanup_old_gift_cards_task():
    """
    Cleanup task for old/expired gift cards
    Archives cards older than 1 year
    """
    try:
        db = Database.get_db()
        
        # Calculate cutoff date (1 year ago)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=365)
        
        # Find old expired cards
        old_cards = db.gift_cards.find({
            "status": "expired",
            "expired_at": {"$lt": cutoff_date}
        })
        
        archived_count = 0
        for card in old_cards:
            try:
                # Move to archive collection
                db.gift_cards_archive.insert_one(card)
                
                # Delete from active collection
                db.gift_cards.delete_one({"_id": card["_id"]})
                
                archived_count += 1
                logger.info(f"Card archived: {card['card_number']}")
                
            except Exception as e:
                logger.error(f"Error archiving card {card['card_number']}: {str(e)}")
        
        logger.info(f"Cleanup task completed: {archived_count} cards archived")
        
        return {
            "success": True,
            "archived_count": archived_count
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        return {"success": False, "error": str(e)}


@shared_task
def generate_gift_card_certificates_task(card_id: str, tenant_id: str):
    """
    Generate PDF certificate for gift card
    
    Args:
        card_id: Gift card ID
        tenant_id: Tenant ID
    """
    try:
        from app.services.pdf_service import PDFService
        
        db = Database.get_db()
        
        # Get gift card
        gift_card = db.gift_cards.find_one({
            "_id": ObjectId(card_id),
            "tenant_id": tenant_id
        })
        
        if not gift_card:
            logger.error(f"Gift card not found: {card_id}")
            return {"success": False, "error": "Card not found"}
        
        # Generate certificate
        certificate_url = PDFService.generate_certificate(
            card_number=gift_card["card_number"],
            amount=gift_card.get("amount"),
            recipient_name=gift_card.get("recipient_name"),
            expiration_date=gift_card.get("expires_at"),
            design_theme=gift_card.get("design_theme", "default"),
            qr_code_data=gift_card.get("qr_code_data")
        )
        
        # Update gift card with certificate URL
        db.gift_cards.update_one(
            {"_id": ObjectId(card_id)},
            {
                "$set": {
                    "certificate_url": certificate_url,
                    "certificate_generated_at": datetime.now(timezone.utc)
                },
                "$push": {
                    "audit_log": {
                        "action": "certificate_generated",
                        "timestamp": datetime.now(timezone.utc),
                        "details": {"certificate_url": certificate_url}
                    }
                }
            }
        )
        
        logger.info(f"Certificate generated for card {gift_card['card_number']}")
        
        return {
            "success": True,
            "card_number": gift_card["card_number"],
            "certificate_url": certificate_url
        }
        
    except Exception as e:
        logger.error(f"Error generating certificate: {str(e)}")
        return {"success": False, "error": str(e)}


@shared_task(bind=True, max_retries=3)
def send_transfer_confirmation_emails(self, source_card_id: str, dest_card_id: str, amount: float, tenant_id: str):
    """
    Send transfer confirmation emails to both source and destination card holders
    
    Args:
        source_card_id: Source gift card ID
        dest_card_id: Destination gift card ID
        amount: Amount transferred
        tenant_id: Tenant ID
    """
    try:
        db = Database.get_db()
        
        # Get both cards
        source_card = db.gift_cards.find_one({"_id": ObjectId(source_card_id)})
        dest_card = db.gift_cards.find_one({"_id": ObjectId(dest_card_id)})
        
        if not source_card or not dest_card:
            logger.error(f"Cards not found for transfer confirmation")
            return {"success": False, "error": "Cards not found"}
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Send email to source card holder
        if source_card.get("recipient_email"):
            source_result = loop.run_until_complete(
                GiftCardEmailService.send_transfer_confirmation_email(
                    card_id=source_card_id,
                    card_number=source_card["card_number"],
                    recipient_email=source_card["recipient_email"],
                    recipient_name=source_card.get("recipient_name"),
                    transfer_type="sent",
                    amount=amount,
                    new_balance=source_card["balance"],
                    other_card_number=dest_card["card_number"]
                )
            )
            logger.info(f"Transfer confirmation sent to source card holder: {source_card['card_number']}")
        
        # Send email to destination card holder
        if dest_card.get("recipient_email"):
            dest_result = loop.run_until_complete(
                GiftCardEmailService.send_transfer_confirmation_email(
                    card_id=dest_card_id,
                    card_number=dest_card["card_number"],
                    recipient_email=dest_card["recipient_email"],
                    recipient_name=dest_card.get("recipient_name"),
                    transfer_type="received",
                    amount=amount,
                    new_balance=dest_card["balance"],
                    other_card_number=source_card["card_number"]
                )
            )
            logger.info(f"Transfer confirmation sent to destination card holder: {dest_card['card_number']}")
        
        loop.close()
        
        return {
            "success": True,
            "source_card": source_card["card_number"],
            "dest_card": dest_card["card_number"]
        }
        
    except Exception as exc:
        logger.error(f"Error sending transfer confirmation emails: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
