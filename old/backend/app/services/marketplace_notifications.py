"""Marketplace notification service"""
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class MarketplaceNotificationService:
    """Service for marketplace notifications"""
    
    def __init__(self, db, notification_service):
        self.db = db
        self.notification_service = notification_service
    
    async def send_booking_confirmation(
        self,
        booking_id: str,
        guest_email: str,
        guest_name: str,
        salon_name: str,
        booking_date: str,
        booking_time: str,
        service_name: str
    ) -> bool:
        """Send booking confirmation email"""
        try:
            subject = f"Booking Confirmation - {salon_name}"
            
            html_content = f"""
            <h2>Booking Confirmed!</h2>
            <p>Hi {guest_name},</p>
            <p>Your booking at {salon_name} has been confirmed.</p>
            <p><strong>Booking Details:</strong></p>
            <ul>
                <li>Service: {service_name}</li>
                <li>Date: {booking_date}</li>
                <li>Time: {booking_time}</li>
            </ul>
            <p>Thank you for booking with us!</p>
            """
            
            await self.notification_service.send_email(
                guest_email,
                subject,
                html_content
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending booking confirmation: {e}")
            return False
    
    async def send_magic_link_email(
        self,
        guest_email: str,
        guest_name: str,
        magic_link: str
    ) -> bool:
        """Send magic link email"""
        try:
            subject = "Your Magic Link - Access Your Bookings"
            
            html_content = f"""
            <h2>Access Your Bookings</h2>
            <p>Hi {guest_name},</p>
            <p>Click the link below to access your bookings:</p>
            <p><a href="{magic_link}">Access Your Bookings</a></p>
            <p>This link expires in 24 hours.</p>
            """
            
            await self.notification_service.send_email(
                guest_email,
                subject,
                html_content
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending magic link: {e}")
            return False
    
    async def send_booking_reminder(
        self,
        guest_email: str,
        guest_name: str,
        salon_name: str,
        booking_date: str,
        booking_time: str
    ) -> bool:
        """Send booking reminder SMS/Email"""
        try:
            subject = f"Reminder: Your booking at {salon_name}"
            
            html_content = f"""
            <h2>Booking Reminder</h2>
            <p>Hi {guest_name},</p>
            <p>This is a reminder about your upcoming booking:</p>
            <p><strong>{salon_name}</strong></p>
            <p>Date: {booking_date}</p>
            <p>Time: {booking_time}</p>
            <p>See you soon!</p>
            """
            
            await self.notification_service.send_email(
                guest_email,
                subject,
                html_content
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            return False
    
    async def send_cancellation_notification(
        self,
        guest_email: str,
        guest_name: str,
        salon_name: str,
        booking_date: str
    ) -> bool:
        """Send booking cancellation notification"""
        try:
            subject = f"Booking Cancelled - {salon_name}"
            
            html_content = f"""
            <h2>Booking Cancelled</h2>
            <p>Hi {guest_name},</p>
            <p>Your booking at {salon_name} on {booking_date} has been cancelled.</p>
            <p>If you have any questions, please contact us.</p>
            """
            
            await self.notification_service.send_email(
                guest_email,
                subject,
                html_content
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending cancellation: {e}")
            return False
