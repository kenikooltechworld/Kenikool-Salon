"""
Booking Reminder Service - Handles scheduled reminders for upcoming bookings
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from pymongo.database import Database as PyMongoDatabase
from bson import ObjectId

from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class BookingReminderService:
    """Service for scheduling and sending booking reminders"""

    # Reminder windows (in hours before booking)
    REMINDER_24H = 24
    REMINDER_2H = 2

    @staticmethod
    async def schedule_reminders(
        db: PyMongoDatabase,
        booking_id: str,
        guest_email: str,
        guest_name: str,
        guest_phone: str,
        service_name: str,
        stylist_name: str,
        booking_date: str,
        booking_time: str,
        preferred_contact: str = "email",
        salon_name: str = "Kenikool Salon",
        salon_address: str = "Lagos, Nigeria",
        salon_phone: str = "+234 (0) 123 456 7890",
    ) -> dict:
        """
        Schedule reminders for a booking
        
        Args:
            db: Database connection
            booking_id: Booking ID
            guest_email: Guest email
            guest_name: Guest name
            guest_phone: Guest phone
            service_name: Service name
            stylist_name: Stylist name
            booking_date: Booking date (formatted)
            booking_time: Booking time (formatted)
            preferred_contact: Preferred contact method
            salon_name: Salon name
            salon_address: Salon address
            salon_phone: Salon phone
        
        Returns:
            Dict with scheduled reminders
        """
        result = {
            "booking_id": booking_id,
            "reminders_scheduled": [],
            "errors": []
        }

        try:
            # Create reminder records in database
            reminders = [
                {
                    "booking_id": booking_id,
                    "guest_email": guest_email,
                    "guest_name": guest_name,
                    "guest_phone": guest_phone,
                    "service_name": service_name,
                    "stylist_name": stylist_name,
                    "booking_date": booking_date,
                    "booking_time": booking_time,
                    "preferred_contact": preferred_contact,
                    "salon_name": salon_name,
                    "salon_address": salon_address,
                    "salon_phone": salon_phone,
                    "reminder_type": "24h",
                    "hours_before": BookingReminderService.REMINDER_24H,
                    "status": "scheduled",
                    "created_at": datetime.utcnow(),
                    "scheduled_for": None,  # Will be calculated by scheduler
                    "sent_at": None,
                    "retry_count": 0,
                    "max_retries": 3,
                },
                {
                    "booking_id": booking_id,
                    "guest_email": guest_email,
                    "guest_name": guest_name,
                    "guest_phone": guest_phone,
                    "service_name": service_name,
                    "stylist_name": stylist_name,
                    "booking_date": booking_date,
                    "booking_time": booking_time,
                    "preferred_contact": preferred_contact,
                    "salon_name": salon_name,
                    "salon_address": salon_address,
                    "salon_phone": salon_phone,
                    "reminder_type": "2h",
                    "hours_before": BookingReminderService.REMINDER_2H,
                    "status": "scheduled",
                    "created_at": datetime.utcnow(),
                    "scheduled_for": None,  # Will be calculated by scheduler
                    "sent_at": None,
                    "retry_count": 0,
                    "max_retries": 3,
                }
            ]

            for reminder in reminders:
                inserted = db.booking_reminders.insert_one(reminder)
                result["reminders_scheduled"].append({
                    "reminder_id": str(inserted.inserted_id),
                    "type": reminder["reminder_type"],
                    "hours_before": reminder["hours_before"]
                })
                logger.info(f"Reminder scheduled for booking {booking_id}: {reminder['reminder_type']}")

        except Exception as e:
            logger.error(f"Error scheduling reminders: {str(e)}")
            result["errors"].append(f"Scheduling error: {str(e)}")

        return result

    @staticmethod
    async def send_reminder(
        db: PyMongoDatabase,
        reminder_id: str,
    ) -> bool:
        """
        Send a scheduled reminder
        
        Args:
            db: Database connection
            reminder_id: Reminder ID
        
        Returns:
            True if reminder sent successfully
        """
        try:
            reminder = db.booking_reminders.find_one({"_id": ObjectId(reminder_id)})
            
            if not reminder:
                logger.error(f"Reminder not found: {reminder_id}")
                return False

            if reminder["status"] != "scheduled":
                logger.info(f"Reminder already processed: {reminder_id}")
                return False

            # Send reminder via preferred contact method
            sent = False
            if reminder["preferred_contact"] in ["email", "phone"]:
                sent = await BookingReminderService._send_reminder_email(
                    guest_email=reminder["guest_email"],
                    guest_name=reminder["guest_name"],
                    service_name=reminder["service_name"],
                    stylist_name=reminder["stylist_name"],
                    booking_date=reminder["booking_date"],
                    booking_time=reminder["booking_time"],
                    reminder_type=reminder["reminder_type"],
                    salon_name=reminder["salon_name"],
                    salon_address=reminder["salon_address"],
                    salon_phone=reminder["salon_phone"],
                )

            if sent:
                # Update reminder status
                db.booking_reminders.update_one(
                    {"_id": ObjectId(reminder_id)},
                    {
                        "$set": {
                            "status": "sent",
                            "sent_at": datetime.utcnow(),
                            "retry_count": 0
                        }
                    }
                )
                logger.info(f"Reminder sent: {reminder_id}")
                return True
            else:
                # Increment retry count
                new_retry_count = reminder.get("retry_count", 0) + 1
                if new_retry_count >= reminder.get("max_retries", 3):
                    db.booking_reminders.update_one(
                        {"_id": ObjectId(reminder_id)},
                        {
                            "$set": {
                                "status": "failed",
                                "retry_count": new_retry_count
                            }
                        }
                    )
                    logger.error(f"Reminder failed after retries: {reminder_id}")
                else:
                    db.booking_reminders.update_one(
                        {"_id": ObjectId(reminder_id)},
                        {
                            "$set": {
                                "retry_count": new_retry_count
                            }
                        }
                    )
                    logger.warning(f"Reminder send failed, will retry: {reminder_id}")
                return False

        except Exception as e:
            logger.error(f"Error sending reminder: {str(e)}")
            return False

    @staticmethod
    async def _send_reminder_email(
        guest_email: str,
        guest_name: str,
        service_name: str,
        stylist_name: str,
        booking_date: str,
        booking_time: str,
        reminder_type: str,
        salon_name: str,
        salon_address: str,
        salon_phone: str,
    ) -> bool:
        """Send reminder email to guest"""
        
        if reminder_type == "24h":
            subject = f"Reminder: Your appointment tomorrow at {salon_name}"
            time_text = "tomorrow"
        else:  # 2h
            subject = f"Reminder: Your appointment in 2 hours at {salon_name}"
            time_text = "in 2 hours"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Appointment Reminder</title>
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
                                    <h2 style="margin: 0 0 20px 0; color: #1f2937; font-size: 24px;">Appointment Reminder</h2>
                                    <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        Hi {guest_name},
                                    </p>
                                    <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        This is a friendly reminder that you have an appointment {time_text}!
                                    </p>
                                    
                                    <!-- Appointment Details -->
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
                                                        <td style="padding: 10px 0;">
                                                            <p style="margin: 0; color: #6b7280; font-size: 14px;">Date & Time</p>
                                                            <p style="margin: 5px 0 0 0; color: #1f2937; font-size: 16px; font-weight: bold;">{booking_date} at {booking_time}</p>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <!-- Important Info -->
                                    <div style="background-color: #fef3c7; border: 1px solid #fcd34d; border-radius: 6px; padding: 20px; margin-bottom: 30px;">
                                        <p style="margin: 0 0 10px 0; color: #92400e; font-size: 14px; font-weight: bold;">📌 Please Note</p>
                                        <ul style="margin: 0; padding-left: 20px; color: #92400e; font-size: 14px;">
                                            <li style="margin-bottom: 8px;">Please arrive 10 minutes early</li>
                                            <li>If you need to reschedule or cancel, please contact us as soon as possible</li>
                                        </ul>
                                    </div>
                                    
                                    <!-- Salon Info -->
                                    <div style="background-color: #f3f4f6; border-radius: 6px; padding: 20px;">
                                        <p style="margin: 0 0 15px 0; color: #1f2937; font-size: 14px; font-weight: bold;">Salon Information</p>
                                        <p style="margin: 0 0 8px 0; color: #4b5563; font-size: 14px;">
                                            <strong>Address:</strong> {salon_address}
                                        </p>
                                        <p style="margin: 0; color: #4b5563; font-size: 14px;">
                                            <strong>Phone:</strong> {salon_phone}
                                        </p>
                                    </div>
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
        Appointment Reminder - {salon_name}
        
        Hi {guest_name},
        
        This is a friendly reminder that you have an appointment {time_text}!
        
        APPOINTMENT DETAILS:
        Service: {service_name}
        Stylist: {stylist_name}
        Date & Time: {booking_date} at {booking_time}
        
        PLEASE NOTE:
        - Please arrive 10 minutes early
        - If you need to reschedule or cancel, please contact us as soon as possible
        
        SALON INFORMATION:
        Address: {salon_address}
        Phone: {salon_phone}
        
        Thank you!
        
        © {datetime.now().year} {salon_name}
        """

        return await email_service.send_email(
            to=guest_email,
            subject=subject,
            html=html,
            text=text
        )

    @staticmethod
    async def get_pending_reminders(
        db: PyMongoDatabase,
        limit: int = 100
    ) -> List[dict]:
        """
        Get pending reminders that need to be sent
        
        Args:
            db: Database connection
            limit: Maximum number of reminders to retrieve
        
        Returns:
            List of pending reminders
        """
        try:
            reminders = list(
                db.booking_reminders.find({
                    "status": "scheduled",
                    "retry_count": {"$lt": 3}
                }).limit(limit)
            )
            return reminders
        except Exception as e:
            logger.error(f"Error retrieving pending reminders: {str(e)}")
            return []
