"""
Birthday Service
Handles birthday notifications and special occasions for clients
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bson import ObjectId
from app.database import Database
import logging

logger = logging.getLogger(__name__)


class BirthdayService:
    """Service for managing client birthdays and special occasions"""

    @staticmethod
    def get_upcoming_birthdays(
        tenant_id: str,
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get clients with upcoming birthdays
        
        Args:
            tenant_id: Tenant ID
            days_ahead: Number of days to look ahead (default 7)
            
        Returns:
            List of clients with upcoming birthdays
        """
        db = Database.get_db()
        
        today = datetime.now()
        
        # Get all clients with birthdays
        clients = list(db.clients.find({
            "tenant_id": tenant_id,
            "birthday": {"$exists": True, "$ne": None}
        }))
        
        upcoming = []
        
        for client in clients:
            birthday = client.get("birthday")
            if not birthday:
                continue
            
            # Calculate next birthday
            next_birthday = birthday.replace(year=today.year)
            
            # If birthday already passed this year, use next year
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            
            # Check if within the days_ahead window
            days_until = (next_birthday - today).days
            
            if 0 <= days_until <= days_ahead:
                upcoming.append({
                    "client_id": str(client["_id"]),
                    "name": client.get("name", "Unknown"),
                    "phone": client.get("phone"),
                    "email": client.get("email"),
                    "birthday": birthday,
                    "next_birthday": next_birthday,
                    "days_until": days_until,
                    "age": today.year - birthday.year
                })
        
        # Sort by days_until
        upcoming.sort(key=lambda x: x["days_until"])
        
        return upcoming
    
    @staticmethod
    def get_birthdays_by_month(
        tenant_id: str,
        month: int
    ) -> List[Dict[str, Any]]:
        """
        Get clients with birthdays in a specific month
        
        Args:
            tenant_id: Tenant ID
            month: Month number (1-12)
            
        Returns:
            List of clients with birthdays in the month
        """
        db = Database.get_db()
        
        # Get all clients with birthdays
        clients = list(db.clients.find({
            "tenant_id": tenant_id,
            "birthday": {"$exists": True, "$ne": None}
        }))
        
        birthdays = []
        
        for client in clients:
            birthday = client.get("birthday")
            if not birthday:
                continue
            
            if birthday.month == month:
                birthdays.append({
                    "client_id": str(client["_id"]),
                    "name": client.get("name", "Unknown"),
                    "phone": client.get("phone"),
                    "email": client.get("email"),
                    "birthday": birthday,
                    "day": birthday.day
                })
        
        # Sort by day
        birthdays.sort(key=lambda x: x["day"])
        
        return birthdays
    
    @staticmethod
    async def send_birthday_greeting(
        client_id: str,
        tenant_id: str,
        channel: str = "sms",
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send birthday greeting to a client
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            channel: Communication channel (sms, email, whatsapp)
            custom_message: Custom message (optional)
            
        Returns:
            Result dictionary with success status
        """
        db = Database.get_db()
        
        # Get client
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if not client:
            return {"success": False, "error": "Client not found"}
        
        # Get tenant for business name
        tenant = db.tenants.find_one({"_id": tenant_id})
        business_name = tenant.get("business_name", "Salon") if tenant else "Salon"
        
        # Create birthday message
        if custom_message:
            message = custom_message
        else:
            message = f"Happy Birthday {client.get('name', '')}! 🎉🎂 Wishing you a wonderful day filled with joy. From all of us at {business_name}!"
        
        # Determine recipient
        if channel == "email":
            if not client.get("email"):
                return {"success": False, "error": "Client has no email address"}
            recipient = client["email"]
        else:  # sms or whatsapp
            recipient = client["phone"]
        
        # Log communication
        from app.services.communication_service import CommunicationService
        
        communication = CommunicationService.log_communication(
            client_id=client_id,
            tenant_id=tenant_id,
            channel=channel,
            message_type="birthday_greeting",
            content=message,
            recipient=recipient,
            direction="outbound"
        )
        
        # Send the message
        try:
            if channel == "sms":
                from app.services.termii_service import send_sms
                success = await send_sms(recipient, message)
            elif channel == "whatsapp":
                from app.services.termii_service import send_whatsapp
                success = await send_whatsapp(recipient, message)
            elif channel == "email":
                from app.services.email_service import email_service
                success = await email_service.send_email(
                    to=recipient,
                    subject=f"Happy Birthday from {business_name}! 🎉",
                    html=f"<p>{message}</p>",
                    text=message
                )
            else:
                return {"success": False, "error": "Invalid channel"}
            
            # Update communication status
            CommunicationService.update_communication_status(
                communication_id=str(communication["_id"]),
                status="sent" if success else "failed",
                error_message=None if success else "Failed to send message"
            )
            
            # Log activity
            db.client_activities.insert_one({
                "tenant_id": tenant_id,
                "client_id": client_id,
                "activity_type": "birthday_greeting_sent",
                "description": f"Birthday greeting sent via {channel}",
                "metadata": {
                    "channel": channel,
                    "communication_id": str(communication["_id"])
                },
                "created_at": datetime.now(),
                "created_by": "system"
            })
            
            return {
                "success": success,
                "communication_id": str(communication["_id"]),
                "message": "Birthday greeting sent successfully" if success else "Failed to send greeting"
            }
            
        except Exception as e:
            logger.error(f"Error sending birthday greeting: {e}")
            CommunicationService.update_communication_status(
                communication_id=str(communication["_id"]),
                status="failed",
                error_message=str(e)
            )
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def send_bulk_birthday_greetings(
        tenant_id: str,
        client_ids: List[str],
        channel: str = "sms",
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send birthday greetings to multiple clients
        
        Args:
            tenant_id: Tenant ID
            client_ids: List of client IDs
            channel: Communication channel
            custom_message: Custom message (optional)
            
        Returns:
            Result dictionary with success/failure counts
        """
        results = {
            "total": len(client_ids),
            "success": 0,
            "failed": 0,
            "errors": []
        }
        
        for client_id in client_ids:
            result = await BirthdayService.send_birthday_greeting(
                client_id=client_id,
                tenant_id=tenant_id,
                channel=channel,
                custom_message=custom_message
            )
            
            if result["success"]:
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "client_id": client_id,
                    "error": result.get("error", "Unknown error")
                })
        
        return results
    
    @staticmethod
    def check_and_send_birthday_notifications(tenant_id: str) -> Dict[str, Any]:
        """
        Check for today's birthdays and send notifications
        This is called by the background job
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Result dictionary
        """
        # Get today's birthdays
        birthdays_today = BirthdayService.get_upcoming_birthdays(tenant_id, days_ahead=0)
        
        if not birthdays_today:
            return {"message": "No birthdays today", "count": 0}
        
        logger.info(f"Found {len(birthdays_today)} birthdays today for tenant {tenant_id}")
        
        # Send greetings (this will be called asynchronously by Celery)
        return {
            "message": f"Found {len(birthdays_today)} birthdays",
            "count": len(birthdays_today),
            "clients": [b["client_id"] for b in birthdays_today]
        }
