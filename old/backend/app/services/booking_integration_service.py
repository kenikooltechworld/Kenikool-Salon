"""
Booking Integration Service - Manages conversion of waitlist entries to bookings
"""
from datetime import datetime
from typing import Dict, Optional
from bson import ObjectId
from app.database import Database
import logging

logger = logging.getLogger(__name__)


class WaitlistBookingIntegration:
    """Service for integrating waitlist entries with booking system"""
    
    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()
    
    @staticmethod
    def create_booking_from_waitlist(
        waitlist_id: str,
        tenant_id: str,
        booking_date: datetime,
        booking_time: str,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Create a booking from a waitlist entry.
        
        Args:
            waitlist_id: Waitlist entry ID
            tenant_id: Tenant ID
            booking_date: Date for the booking
            booking_time: Time for the booking (HH:MM format)
            notes: Optional booking notes
            
        Returns:
            Dict with booking creation result
            
        Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
        """
        db = WaitlistBookingIntegration._get_db()
        
        try:
            # Validate ObjectId format
            try:
                obj_id = ObjectId(waitlist_id)
            except Exception:
                return {
                    "success": False,
                    "error": "Invalid waitlist ID format"
                }
            
            # Get waitlist entry
            waitlist_entry = db.waitlist.find_one({
                "_id": obj_id,
                "tenant_id": tenant_id
            })
            
            if not waitlist_entry:
                return {
                    "success": False,
                    "error": "Waitlist entry not found"
                }
            
            # Check if already booked or cancelled
            if waitlist_entry.get("status") in ["booked", "cancelled"]:
                return {
                    "success": False,
                    "error": f"Cannot book: entry is already {waitlist_entry.get('status')}"
                }
            
            # Prepare booking data
            booking_data = WaitlistBookingIntegration._prepare_booking_data(
                waitlist_entry,
                booking_date,
                booking_time,
                notes
            )
            
            # Create booking in bookings collection
            booking_result = db.bookings.insert_one(booking_data)
            booking_id = str(booking_result.inserted_id)
            
            # Update waitlist entry
            WaitlistBookingIntegration._update_waitlist_after_booking(
                obj_id,
                booking_id
            )
            
            logger.info(f"Created booking {booking_id} from waitlist entry {waitlist_id}")
            
            return {
                "success": True,
                "booking_id": booking_id,
                "message": "Booking created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating booking from waitlist: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def _prepare_booking_data(
        waitlist_entry: Dict,
        booking_date: datetime,
        booking_time: str,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Prepare booking data from waitlist entry.
        
        Args:
            waitlist_entry: Waitlist entry data
            booking_date: Date for the booking
            booking_time: Time for the booking
            notes: Optional booking notes
            
        Returns:
            Dict with booking data
            
        Requirements: 8.2, 8.3
        """
        # Parse time (HH:MM format)
        time_parts = booking_time.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        # Create datetime for booking
        booking_datetime = booking_date.replace(hour=hour, minute=minute, second=0)
        
        # Build booking data
        booking_data = {
            "tenant_id": waitlist_entry.get("tenant_id"),
            "client_id": waitlist_entry.get("client_id"),
            "client_name": waitlist_entry.get("client_name"),
            "client_phone": waitlist_entry.get("client_phone"),
            "client_email": waitlist_entry.get("client_email"),
            "service_id": waitlist_entry.get("service_id"),
            "service_name": waitlist_entry.get("service_name"),
            "stylist_id": waitlist_entry.get("stylist_id"),
            "stylist_name": waitlist_entry.get("stylist_name"),
            "location_id": waitlist_entry.get("location_id"),
            "location_name": waitlist_entry.get("location_name"),
            "booking_date": booking_date,
            "booking_time": booking_time,
            "booking_datetime": booking_datetime,
            "status": "confirmed",
            "source": "waitlist",
            "waitlist_id": str(waitlist_entry.get("_id")),
            "notes": notes or f"Converted from waitlist entry",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        return booking_data
    
    @staticmethod
    def _update_waitlist_after_booking(
        waitlist_id: ObjectId,
        booking_id: str
    ) -> bool:
        """
        Update waitlist entry after booking creation.
        
        Args:
            waitlist_id: Waitlist entry ID
            booking_id: Created booking ID
            
        Returns:
            True if update successful
            
        Requirements: 8.1, 8.4
        """
        db = WaitlistBookingIntegration._get_db()
        
        try:
            # Update waitlist entry
            result = db.waitlist.update_one(
                {"_id": waitlist_id},
                {
                    "$set": {
                        "status": "booked",
                        "booking_id": booking_id,
                        "booked_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated waitlist entry {waitlist_id} with booking {booking_id}")
                return True
            else:
                logger.warning(f"Failed to update waitlist entry {waitlist_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating waitlist after booking: {e}")
            return False


# Create singleton instance
booking_integration_service = WaitlistBookingIntegration()
