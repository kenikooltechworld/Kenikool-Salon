"""
Marketplace booking service
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from bson import ObjectId
import logging
import secrets

logger = logging.getLogger(__name__)


class MarketplaceBookingService:
    """Service for marketplace bookings"""
    
    def __init__(self, db):
        self.db = db
    
    async def create_booking(
        self,
        tenant_id: str,
        guest_email: str,
        guest_phone: str,
        guest_name: str,
        service_id: str,
        service_name: str,
        booking_date: str,
        booking_time: str,
        duration_minutes: int,
        price: float,
        payment_method: str,
        stylist_id: Optional[str] = None,
        stylist_name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """Create a new marketplace booking"""
        try:
            reference_number = f"MB{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{secrets.token_hex(3).upper()}"
            magic_token = secrets.token_urlsafe(32)
            
            settings = await self._get_marketplace_settings(tenant_id)
            discount_percentage = 0.0
            final_price = price
            
            if payment_method == "online":
                discount_percentage = settings.get("online_payment_discount", 0.05)
                final_price = price * (1 - discount_percentage)
            
            booking_data = {
                "tenant_id": tenant_id,
                "guest_email": guest_email,
                "guest_phone": guest_phone,
                "guest_name": guest_name,
                "service_id": service_id,
                "service_name": service_name,
                "stylist_id": stylist_id,
                "stylist_name": stylist_name,
                "booking_date": booking_date,
                "booking_time": booking_time,
                "duration_minutes": duration_minutes,
                "price": price,
                "discount_percentage": discount_percentage,
                "final_price": final_price,
                "payment_method": payment_method,
                "payment_status": "pending",
                "booking_status": "confirmed",
                "reference_number": reference_number,
                "magic_token": magic_token,
                "notes": notes,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.marketplace_bookings.insert_one(booking_data)
            booking_data["_id"] = str(result.inserted_id)
            
            await self._create_or_update_guest(
                guest_email, guest_phone, guest_name, magic_token, str(result.inserted_id)
            )
            
            return booking_data
        
        except Exception as e:
            logger.error(f"Error creating marketplace booking: {e}")
            raise Exception(f"Failed to create booking: {str(e)}")
    
    async def get_booking_by_reference(self, reference_number: str, tenant_id: str) -> Optional[Dict]:
        """Get booking by reference number"""
        try:
            booking = self.db.marketplace_bookings.find_one({
                "reference_number": reference_number,
                "tenant_id": tenant_id
            })
            
            if booking:
                booking["_id"] = str(booking["_id"])
            
            return booking
        
        except Exception as e:
            logger.error(f"Error getting booking: {e}")
            return None
    
    async def reschedule_booking(
        self,
        booking_id: str,
        new_date: str,
        new_time: str,
        tenant_id: str
    ) -> Dict:
        """Reschedule a booking"""
        try:
            booking = self.db.marketplace_bookings.find_one({
                "_id": ObjectId(booking_id),
                "tenant_id": tenant_id
            })
            
            if not booking:
                raise ValueError("Booking not found")
            
            self.db.marketplace_bookings.update_one(
                {"_id": ObjectId(booking_id)},
                {
                    "$set": {
                        "booking_date": new_date,
                        "booking_time": new_time,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            updated_booking = self.db.marketplace_bookings.find_one({"_id": ObjectId(booking_id)})
            updated_booking["_id"] = str(updated_booking["_id"])
            
            return updated_booking
        
        except Exception as e:
            logger.error(f"Error rescheduling booking: {e}")
            raise Exception(f"Failed to reschedule booking: {str(e)}")
    
    async def cancel_booking(self, booking_id: str, tenant_id: str) -> bool:
        """Cancel a booking"""
        try:
            booking = self.db.marketplace_bookings.find_one({
                "_id": ObjectId(booking_id),
                "tenant_id": tenant_id
            })
            
            if not booking:
                raise ValueError("Booking not found")
            
            self.db.marketplace_bookings.update_one(
                {"_id": ObjectId(booking_id)},
                {
                    "$set": {
                        "booking_status": "cancelled",
                        "cancelled_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return True
        
        except Exception as e:
            logger.error(f"Error cancelling booking: {e}")
            raise Exception(f"Failed to cancel booking: {str(e)}")
    
    async def check_availability(
        self,
        tenant_id: str,
        booking_date: str,
        booking_time: str,
        duration_minutes: int,
        stylist_id: Optional[str] = None
    ) -> bool:
        """Check if time slot is available"""
        try:
            booking_start = datetime.strptime(f"{booking_date} {booking_time}", "%Y-%m-%d %H:%M")
            booking_end = booking_start + timedelta(minutes=duration_minutes)
            
            query = {
                "tenant_id": tenant_id,
                "booking_date": booking_date,
                "booking_status": {"$in": ["confirmed", "completed"]}
            }
            
            if stylist_id:
                query["stylist_id"] = stylist_id
            
            conflicting_bookings = list(self.db.marketplace_bookings.find(query))
            
            for booking in conflicting_bookings:
                existing_start = datetime.strptime(
                    f"{booking['booking_date']} {booking['booking_time']}", 
                    "%Y-%m-%d %H:%M"
                )
                existing_end = existing_start + timedelta(minutes=booking["duration_minutes"])
                
                if booking_start < existing_end and booking_end > existing_start:
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return False
    
    async def _create_or_update_guest(
        self,
        email: str,
        phone: str,
        name: str,
        magic_token: str,
        booking_id: str
    ) -> None:
        """Create or update guest account"""
        try:
            guest = self.db.guest_accounts.find_one({"email": email})
            
            if guest:
                self.db.guest_accounts.update_one(
                    {"_id": guest["_id"]},
                    {
                        "$set": {
                            "magic_token": magic_token,
                            "magic_token_expires": datetime.utcnow() + timedelta(hours=24),
                            "updated_at": datetime.utcnow()
                        },
                        "$push": {"bookings": booking_id}
                    }
                )
            else:
                self.db.guest_accounts.insert_one({
                    "email": email,
                    "phone": phone,
                    "name": name,
                    "magic_token": magic_token,
                    "magic_token_expires": datetime.utcnow() + timedelta(hours=24),
                    "is_authenticated": False,
                    "bookings": [booking_id],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
        
        except Exception as e:
            logger.error(f"Error creating/updating guest: {e}")
    
    async def _get_marketplace_settings(self, tenant_id: str) -> Dict:
        """Get marketplace settings for tenant"""
        try:
            settings = self.db.marketplace_settings.find_one({"tenant_id": tenant_id})
            
            if not settings:
                return {
                    "online_payment_discount": 0.05,
                    "commission_rate": 0.15
                }
            
            return settings
        
        except Exception as e:
            logger.error(f"Error getting marketplace settings: {e}")
            return {
                "online_payment_discount": 0.05,
                "commission_rate": 0.15
            }
