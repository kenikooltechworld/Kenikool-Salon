"""
Termii SMS and WhatsApp service
"""
import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def send_sms(phone: str, message: str) -> bool:
    """
    Send SMS via Termii
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.TERMII_API_URL}/sms/send",
                json={
                    "to": phone,
                    "from": settings.TERMII_SENDER_ID,
                    "sms": message,
                    "type": "plain",
                    "channel": "generic",
                    "api_key": settings.TERMII_API_KEY
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info(f"SMS sent successfully to {phone}")
                return True
            else:
                logger.error(f"Failed to send SMS: {response.text}")
                return False
    except Exception as e:
        logger.error(f"Error sending SMS: {e}")
        return False


async def send_whatsapp(phone: str, message: str) -> bool:
    """
    Send WhatsApp message via Termii
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.TERMII_API_URL}/sms/send",
                json={
                    "to": phone,
                    "from": settings.TERMII_SENDER_ID,
                    "sms": message,
                    "type": "plain",
                    "channel": "whatsapp",
                    "api_key": settings.TERMII_API_KEY
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent successfully to {phone}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp message: {response.text}")
                # Fallback to SMS
                return await send_sms(phone, message)
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        # Fallback to SMS
        return await send_sms(phone, message)


async def send_booking_confirmation(booking: dict) -> bool:
    """
    Send booking confirmation message
    """
    message = f"""
Hello {booking['client_name']}!

Your booking has been confirmed:
Service: {booking['service_name']}
Stylist: {booking['stylist_name']}
Date: {booking['booking_date'].strftime('%B %d, %Y at %I:%M %p')}

Thank you for choosing us!
"""
    
    return await send_whatsapp(booking['client_phone'], message.strip())


async def send_booking_reminder(booking: dict, hours_before: int) -> bool:
    """
    Send booking reminder message
    """
    message = f"""
Reminder: You have an appointment in {hours_before} hours!

Service: {booking['service_name']}
Stylist: {booking['stylist_name']}
Date: {booking['booking_date'].strftime('%B %d, %Y at %I:%M %p')}

See you soon!
"""
    
    return await send_whatsapp(booking['client_phone'], message.strip())


async def send_waitlist_notification(waitlist: dict, available_slot: str) -> bool:
    """
    Send waitlist notification when slot becomes available
    """
    message = f"""
Good news {waitlist['client_name']}!

A slot is now available for {waitlist['service_name']}.
Available time: {available_slot}

Book now before it's taken!
"""
    
    return await send_whatsapp(waitlist['client_phone'], message.strip())
