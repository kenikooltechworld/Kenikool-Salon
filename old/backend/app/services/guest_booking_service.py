from datetime import datetime
from typing import Dict, Optional, List
from bson import ObjectId
from app.database import Database


class GuestBookingService:
    
    @staticmethod
    def create_guest_booking(
        tenant_id: str,
        guest_name: str,
        guest_email: str,
        guest_phone: str,
        service_id: str,
        stylist_id: str,
        booking_date: str,
        notes: Optional[str] = None
    ) -> Dict:
        """Create booking for guest (no account required)"""
        db = Database.get_db()
        
        from datetime import datetime as dt
        booking_datetime = dt.fromisoformat(booking_date.replace('Z', '+00:00'))
        
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise ValueError("Service not found")
        
        booking = {
            "tenant_id": tenant_id,
            "guest_name": guest_name,
            "guest_email": guest_email,
            "guest_phone": guest_phone,
            "service_id": ObjectId(service_id),
            "service_name": service.get("name"),
            "service_price": service.get("price", 0),
            "stylist_id": ObjectId(stylist_id),
            "booking_date": booking_datetime,
            "status": "pending",
            "payment_status": "unpaid",
            "notes": notes,
            "is_guest": True,
            "created_at": dt.utcnow()
        }
        
        result = db.guest_bookings.insert_one(booking)
        booking["_id"] = str(result.inserted_id)
        
        return booking
    
    @staticmethod
    def get_guest_booking_by_email(tenant_id: str, email: str) -> List[Dict]:
        """Get all bookings for a guest email"""
        db = Database.get_db()
        
        bookings = list(db.guest_bookings.find({
            "tenant_id": tenant_id,
            "guest_email": email
        }).sort("created_at", -1))
        
        return bookings
    
    @staticmethod
    def detect_returning_guest(tenant_id: str, email: str) -> Optional[Dict]:
        """Detect if guest has booked before"""
        db = Database.get_db()
        
        guest = db.guest_bookings.find_one({
            "tenant_id": tenant_id,
            "guest_email": email
        })
        
        if guest:
            booking_count = db.guest_bookings.count_documents({
                "tenant_id": tenant_id,
                "guest_email": email
            })
            
            return {
                "is_returning": True,
                "booking_count": booking_count,
                "guest_name": guest.get("guest_name"),
                "guest_phone": guest.get("guest_phone")
            }
        
        return {"is_returning": False}
    
    @staticmethod
    def convert_guest_to_account(
        tenant_id: str,
        guest_email: str,
        password: str,
        user_data: Dict
    ) -> Dict:
        """Convert guest bookings to registered account"""
        db = Database.get_db()
        
        from app.services.auth_service import hash_password
        
        # Create user account
        user = {
            "tenant_id": tenant_id,
            "email": guest_email,
            "password": hash_password(password),
            "name": user_data.get("name"),
            "phone": user_data.get("phone"),
            "created_at": datetime.utcnow()
        }
        
        result = db.users.insert_one(user)
        user_id = str(result.inserted_id)
        
        # Link guest bookings to new account
        db.guest_bookings.update_many(
            {
                "tenant_id": tenant_id,
                "guest_email": guest_email
            },
            {
                "$set": {
                    "user_id": ObjectId(user_id),
                    "is_guest": False
                }
            }
        )
        
        return {
            "user_id": user_id,
            "email": guest_email,
            "status": "account_created"
        }
    
    @staticmethod
    def get_guest_booking_history(tenant_id: str, email: str) -> Dict:
        """Get complete booking history for guest"""
        db = Database.get_db()
        
        bookings = list(db.guest_bookings.find({
            "tenant_id": tenant_id,
            "guest_email": email
        }).sort("booking_date", -1))
        
        completed = len([b for b in bookings if b.get("status") == "completed"])
        total_spent = sum(b.get("service_price", 0) for b in bookings if b.get("status") == "completed")
        
        return {
            "total_bookings": len(bookings),
            "completed_bookings": completed,
            "total_spent": total_spent,
            "bookings": bookings
        }
