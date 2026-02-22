"""
Booking Notification Service - Auto-send SMS/WhatsApp for bookings
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from bson import ObjectId
import logging
import asyncio

from app.database import Database
from app.services.termii_service import send_sms, send_whatsapp
from app.services.sms_credit_service import SMSCreditService

logger = logging.getLogger(__name__)


class BookingNotificationService:
    """Service for automated booking notifications"""
    
    @staticmethod
    def _get_db():
        return Database.get_db()
    
    @staticmethod
    async def send_booking_confirmation(booking_id: str, tenant_id: str, channel: str = "sms") -> bool:
        """Send booking confirmation message"""
        db = BookingNotificationService._get_db()
        
        try:
            booking = db.bookings.find_one({
                "_id": ObjectId(booking_id),
                "tenant_id": tenant_id
            })
            
            if not booking:
                logger.error(f"Booking {booking_id} not found")
                return False
            
            client = db.clients.find_one({
                "_id": ObjectId(booking.get("client_id")),
                "tenant_id": tenant_id
            })
            
            if not client:
                logger.error(f"Client {booking.get('client_id')} not found")
                return False
            
            # Check credits
            if not SMSCreditService.check_sufficient_credits(tenant_id, 1):
                logger.error(f"Insufficient credits for booking confirmation")
                return False
            
            # Get service and stylist info
            service = db.services.find_one({"_id": ObjectId(booking.get("service_id"))}) if booking.get("service_id") else {}
            stylist = db.staff_management.find_one({"_id": ObjectId(booking.get("stylist_id"))}) if booking.get("stylist_id") else {}
            
            # Format booking date
            booking_date = booking.get("booking_date")
            if isinstance(booking_date, str):
                booking_date = datetime.fromisoformat(booking_date)
            formatted_date = booking_date.strftime("%B %d, %Y at %I:%M %p")
            
            # Build message
            message = f"Hi {client.get('name', 'there')}!\n\n"
            message += f"Your booking has been confirmed:\n"
            message += f"Service: {service.get('name', 'Service')}\n"
            message += f"Stylist: {stylist.get('name', 'Our team')}\n"
            message += f"Date & Time: {formatted_date}\n\n"
            message += f"Thank you for choosing us!"
            
            # Send message
            recipient = client.get("phone") if channel == "sms" else client.get("phone")
            
            if not recipient:
                logger.error(f"No {channel} contact for client {client.get('_id')}")
                return False
            
            sent = False
            if channel == "sms":
                sent = await send_sms(recipient, message)
            elif channel == "whatsapp":
                sent = await send_whatsapp(recipient, message)
            
            if sent:
                # Deduct credits
                SMSCreditService.deduct_credits(
                    tenant_id,
                    1,
                    "booking_confirmation",
                    reference_id=booking_id
                )
                
                # Record communication
                db.communications.insert_one({
                    "client_id": str(client.get("_id")),
                    "tenant_id": tenant_id,
                    "channel": channel,
                    "direction": "outbound",
                    "message_type": "booking_confirmation",
                    "content": message,
                    "recipient": recipient,
                    "status": "sent",
                    "booking_id": booking_id,
                    "sent_at": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                })
                
                logger.info(f"Booking confirmation sent to {recipient} via {channel}")
                return True
            else:
                logger.error(f"Failed to send booking confirmation via {channel}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending booking confirmation: {e}")
            return False
    
    @staticmethod
    async def send_booking_reminder(booking_id: str, tenant_id: str, hours_before: int = 24, channel: str = "sms") -> bool:
        """Send booking reminder message"""
        db = BookingNotificationService._get_db()
        
        try:
            booking = db.bookings.find_one({
                "_id": ObjectId(booking_id),
                "tenant_id": tenant_id
            })
            
            if not booking:
                logger.error(f"Booking {booking_id} not found")
                return False
            
            client = db.clients.find_one({
                "_id": ObjectId(booking.get("client_id")),
                "tenant_id": tenant_id
            })
            
            if not client:
                logger.error(f"Client {booking.get('client_id')} not found")
                return False
            
            # Check credits
            if not SMSCreditService.check_sufficient_credits(tenant_id, 1):
                logger.error(f"Insufficient credits for booking reminder")
                return False
            
            # Get service and stylist info
            service = db.services.find_one({"_id": ObjectId(booking.get("service_id"))}) if booking.get("service_id") else {}
            stylist = db.staff_management.find_one({"_id": ObjectId(booking.get("stylist_id"))}) if booking.get("stylist_id") else {}
            
            # Format booking date
            booking_date = booking.get("booking_date")
            if isinstance(booking_date, str):
                booking_date = datetime.fromisoformat(booking_date)
            formatted_date = booking_date.strftime("%B %d, %Y at %I:%M %p")
            
            # Build message
            message = f"Reminder: You have an appointment in {hours_before} hours!\n\n"
            message += f"Service: {service.get('name', 'Service')}\n"
            message += f"Stylist: {stylist.get('name', 'Our team')}\n"
            message += f"Date & Time: {formatted_date}\n\n"
            message += f"See you soon!"
            
            # Send message
            recipient = client.get("phone") if channel == "sms" else client.get("phone")
            
            if not recipient:
                logger.error(f"No {channel} contact for client {client.get('_id')}")
                return False
            
            sent = False
            if channel == "sms":
                sent = await send_sms(recipient, message)
            elif channel == "whatsapp":
                sent = await send_whatsapp(recipient, message)
            
            if sent:
                # Deduct credits
                SMSCreditService.deduct_credits(
                    tenant_id,
                    1,
                    "booking_reminder",
                    reference_id=booking_id
                )
                
                # Record communication
                db.communications.insert_one({
                    "client_id": str(client.get("_id")),
                    "tenant_id": tenant_id,
                    "channel": channel,
                    "direction": "outbound",
                    "message_type": "booking_reminder",
                    "content": message,
                    "recipient": recipient,
                    "status": "sent",
                    "booking_id": booking_id,
                    "sent_at": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                })
                
                logger.info(f"Booking reminder sent to {recipient} via {channel}")
                return True
            else:
                logger.error(f"Failed to send booking reminder via {channel}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending booking reminder: {e}")
            return False
    
    @staticmethod
    async def send_review_request(client_id: str, tenant_id: str, booking_id: Optional[str] = None, channel: str = "sms") -> bool:
        """Send review request message"""
        db = BookingNotificationService._get_db()
        
        try:
            client = db.clients.find_one({
                "_id": ObjectId(client_id),
                "tenant_id": tenant_id
            })
            
            if not client:
                logger.error(f"Client {client_id} not found")
                return False
            
            # Check credits
            if not SMSCreditService.check_sufficient_credits(tenant_id, 1):
                logger.error(f"Insufficient credits for review request")
                return False
            
            # Get tenant info
            tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
            salon_name = tenant.get("business_name", "Our Salon") if tenant else "Our Salon"
            
            # Build message
            message = f"Hi {client.get('name', 'there')}!\n\n"
            message += f"We'd love to hear about your experience at {salon_name}.\n"
            message += f"Please take a moment to leave us a review.\n\n"
            message += f"Your feedback helps us improve!\n"
            message += f"Thank you!"
            
            # Send message
            recipient = client.get("phone") if channel == "sms" else client.get("phone")
            
            if not recipient:
                logger.error(f"No {channel} contact for client {client.get('_id')}")
                return False
            
            sent = False
            if channel == "sms":
                sent = await send_sms(recipient, message)
            elif channel == "whatsapp":
                sent = await send_whatsapp(recipient, message)
            
            if sent:
                # Deduct credits
                SMSCreditService.deduct_credits(
                    tenant_id,
                    1,
                    "review_request",
                    reference_id=client_id
                )
                
                # Record communication
                db.communications.insert_one({
                    "client_id": client_id,
                    "tenant_id": tenant_id,
                    "channel": channel,
                    "direction": "outbound",
                    "message_type": "review_request",
                    "content": message,
                    "recipient": recipient,
                    "status": "sent",
                    "booking_id": booking_id,
                    "sent_at": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                })
                
                logger.info(f"Review request sent to {recipient} via {channel}")
                return True
            else:
                logger.error(f"Failed to send review request via {channel}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending review request: {e}")
            return False


booking_notification_service = BookingNotificationService()
