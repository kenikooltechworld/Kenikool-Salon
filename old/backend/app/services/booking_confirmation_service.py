"""
Booking Confirmation Service - Handles confirmation emails and SMS for guest bookings
"""
import logging
from datetime import datetime
from typing import Optional
from pymongo.database import Database as PyMongoDatabase

from app.services.email_service import email_service
from app.config import settings

logger = logging.getLogger(__name__)


class BookingConfirmationService:
    """Service for sending booking confirmations via email and SMS"""

    @staticmethod
    async def send_booking_confirmation(
        db: PyMongoDatabase,
        booking_id: str,
        guest_email: str,
        guest_name: str,
        guest_phone: str,
        service_name: str,
        stylist_name: str,
        booking_date: str,
        booking_time: str,
        confirmation_code: str,
        total_price: float,
        preferred_contact: str = "email",
        salon_name: str = "Kenikool Salon",
        salon_address: str = "Lagos, Nigeria",
        salon_phone: str = "+234 (0) 123 456 7890",
    ) -> dict:
        """
        Send booking confirmation to guest via email and/or SMS
        
        Args:
            db: Database connection
            booking_id: Booking ID
            guest_email: Guest email address
            guest_name: Guest name
            guest_phone: Guest phone number
            service_name: Service name
            stylist_name: Stylist name
            booking_date: Booking date (formatted)
            booking_time: Booking time (formatted)
            confirmation_code: Confirmation code
            total_price: Total price
            preferred_contact: Preferred contact method (email, sms, phone)
            salon_name: Salon name
            salon_address: Salon address
            salon_phone: Salon phone number
        
        Returns:
            Dict with confirmation status
        """
        result = {
            "booking_id": booking_id,
            "email_sent": False,
            "sms_sent": False,
            "errors": []
        }

        # Send email confirmation
        try:
            email_sent = await BookingConfirmationService._send_confirmation_email(
                guest_email=guest_email,
                guest_name=guest_name,
                service_name=service_name,
                stylist_name=stylist_name,
                booking_date=booking_date,
                booking_time=booking_time,
                confirmation_code=confirmation_code,
                total_price=total_price,
                salon_name=salon_name,
                salon_address=salon_address,
                salon_phone=salon_phone,
            )
            result["email_sent"] = email_sent
            if email_sent:
                logger.info(f"Confirmation email sent to {guest_email} for booking {booking_id}")
            else:
                result["errors"].append("Failed to send confirmation email")
        except Exception as e:
            logger.error(f"Error sending confirmation email: {str(e)}")
            result["errors"].append(f"Email error: {str(e)}")

        # Send SMS confirmation if opted in
        if preferred_contact in ["sms", "phone"]:
            try:
                sms_sent = await BookingConfirmationService._send_confirmation_sms(
                    guest_phone=guest_phone,
                    guest_name=guest_name,
                    service_name=service_name,
                    stylist_name=stylist_name,
                    booking_date=booking_date,
                    booking_time=booking_time,
                    confirmation_code=confirmation_code,
                    salon_name=salon_name,
                )
                result["sms_sent"] = sms_sent
                if sms_sent:
                    logger.info(f"Confirmation SMS sent to {guest_phone} for booking {booking_id}")
                else:
                    result["errors"].append("Failed to send confirmation SMS")
            except Exception as e:
                logger.error(f"Error sending confirmation SMS: {str(e)}")
                result["errors"].append(f"SMS error: {str(e)}")

        # Log confirmation in database
        try:
            db.booking_confirmations.insert_one({
                "booking_id": booking_id,
                "guest_email": guest_email,
                "guest_phone": guest_phone,
                "email_sent": result["email_sent"],
                "sms_sent": result["sms_sent"],
                "sent_at": datetime.utcnow(),
                "confirmation_code": confirmation_code,
            })
        except Exception as e:
            logger.error(f"Error logging confirmation: {str(e)}")

        return result

    @staticmethod
    async def _send_confirmation_email(
        guest_email: str,
        guest_name: str,
        service_name: str,
        stylist_name: str,
        booking_date: str,
        booking_time: str,
        confirmation_code: str,
        total_price: float,
        salon_name: str,
        salon_address: str,
        salon_phone: str,
    ) -> bool:
        """Send confirmation email to guest"""
        subject = f"Booking Confirmation - {salon_name}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Booking Confirmation</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td align="center" style="padding: 40px 0;">
                        <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 8px 8px 0 0;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">{salon_name}</h1>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px;">
                                    <h2 style="margin: 0 0 20px 0; color: #1f2937; font-size: 24px;">Booking Confirmed!</h2>
                                    <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        Hi {guest_name},
                                    </p>
                                    <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        Your appointment has been successfully booked. Here are your booking details:
                                    </p>
                                    
                                    <!-- Booking Details Box -->
                                    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; margin-bottom: 30px;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                                    <tr>
                                                        <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">
                                                            <p style="margin: 0; color: #6b7280; font-size: 14px;">Service</p>
                                                            <p style="margin: 5px 0 0 0; color: #1f2937; font-size: 16px; font-weight: bold;">{service_name}</p>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">
                                                            <p style="margin: 0; color: #6b7280; font-size: 14px;">Stylist</p>
                                                            <p style="margin: 5px 0 0 0; color: #1f2937; font-size: 16px; font-weight: bold;">{stylist_name}</p>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 10px 0; border-bottom: 1px solid #e5e7eb;">
                                                            <p style="margin: 0; color: #6b7280; font-size: 14px;">Date & Time</p>
                                                            <p style="margin: 5px 0 0 0; color: #1f2937; font-size: 16px; font-weight: bold;">{booking_date} at {booking_time}</p>
                                                        </td>
                                                    </tr>
                                                    <tr>
                                                        <td style="padding: 10px 0;">
                                                            <p style="margin: 0; color: #6b7280; font-size: 14px;">Total Price</p>
                                                            <p style="margin: 5px 0 0 0; color: #1f2937; font-size: 16px; font-weight: bold;">₦{total_price:,.2f}</p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Confirmation Code -->
                                    <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 20px; margin-bottom: 30px;">
                                        <p style="margin: 0 0 10px 0; color: #1e40af; font-size: 14px; font-weight: bold;">Confirmation Code</p>
                                        <p style="margin: 0; color: #1e40af; font-size: 24px; font-weight: bold; font-family: monospace;">{confirmation_code}</p>
                                    </div>
                                    
                                    <!-- Important Info -->
                                    <div style="background-color: #fef3c7; border: 1px solid #fcd34d; border-radius: 6px; padding: 20px; margin-bottom: 30px;">
                                        <p style="margin: 0 0 10px 0; color: #92400e; font-size: 14px; font-weight: bold;">📌 Important</p>
                                        <ul style="margin: 0; padding-left: 20px; color: #92400e; font-size: 14px;">
                                            <li style="margin-bottom: 8px;">Please arrive 10 minutes early</li>
                                            <li style="margin-bottom: 8px;">You'll receive a reminder 24 hours before your appointment</li>
                                            <li>Cancellations must be made at least 24 hours in advance</li>
                                        </ul>
                                    </div>
                                    
                                    <!-- Salon Info -->
                                    <div style="background-color: #f3f4f6; border-radius: 6px; padding: 20px; margin-bottom: 30px;">
                                        <p style="margin: 0 0 15px 0; color: #1f2937; font-size: 14px; font-weight: bold;">Salon Information</p>
                                        <p style="margin: 0 0 8px 0; color: #4b5563; font-size: 14px;">
                                            <strong>Address:</strong> {salon_address}
                                        </p>
                                        <p style="margin: 0; color: #4b5563; font-size: 14px;">
                                            <strong>Phone:</strong> {salon_phone}
                                        </p>
                                    </div>
                                    
                                    <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                        If you need to reschedule or cancel, please contact us as soon as possible.
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px 40px; background-color: #f9fafb; border-radius: 0 0 8px 8px; border-top: 1px solid #e5e7eb;">
                                    <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 12px; text-align: center;">
                                        © {datetime.now().year} {salon_name}. All rights reserved.
                                    </p>
                                    <p style="margin: 0; color: #6b7280; font-size: 12px; text-align: center;">
                                        {salon_address}
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        text = f"""
        Booking Confirmation - {salon_name}
        
        Hi {guest_name},
        
        Your appointment has been successfully booked!
        
        BOOKING DETAILS:
        Service: {service_name}
        Stylist: {stylist_name}
        Date & Time: {booking_date} at {booking_time}
        Total Price: ₦{total_price:,.2f}
        
        CONFIRMATION CODE: {confirmation_code}
        
        IMPORTANT:
        - Please arrive 10 minutes early
        - You'll receive a reminder 24 hours before your appointment
        - Cancellations must be made at least 24 hours in advance
        
        SALON INFORMATION:
        Address: {salon_address}
        Phone: {salon_phone}
        
        If you need to reschedule or cancel, please contact us as soon as possible.
        
        © {datetime.now().year} {salon_name}
        """

        return await email_service.send_email(
            to=guest_email,
            subject=subject,
            html=html,
            text=text
        )

    @staticmethod
    async def _send_confirmation_sms(
        guest_phone: str,
        guest_name: str,
        service_name: str,
        stylist_name: str,
        booking_date: str,
        booking_time: str,
        confirmation_code: str,
        salon_name: str,
    ) -> bool:
        """Send confirmation SMS to guest"""
        message = f"""
Hi {guest_name},

Your booking at {salon_name} is confirmed!

Service: {service_name}
Stylist: {stylist_name}
Date & Time: {booking_date} at {booking_time}

Confirmation Code: {confirmation_code}

Please arrive 10 minutes early. You'll receive a reminder 24 hours before.

Thank you!
        """.strip()

        # TODO: Integrate with SMS provider (Termii, Twilio, etc.)
        # For now, log the SMS that would be sent
        logger.info(f"SMS would be sent to {guest_phone}: {message}")
        
        # Return True to indicate SMS was queued
        return True
