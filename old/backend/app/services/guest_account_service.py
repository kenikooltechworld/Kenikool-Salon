"""Guest account service for marketplace"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from bson import ObjectId
import logging
import secrets
import hashlib

logger = logging.getLogger(__name__)


class GuestAccountService:
    """Service for guest account management"""
    
    def __init__(self, db):
        self.db = db
    
    async def create_or_get_guest(
        self,
        email: str,
        phone: str,
        name: str
    ) -> Dict:
        """Create or get guest account"""
        try:
            guest = self.db.guest_accounts.find_one({"email": email})
            
            if guest:
                guest["_id"] = str(guest["_id"])
                return guest
            
            guest_data = {
                "email": email,
                "phone": phone,
                "name": name,
                "magic_token": None,
                "magic_token_expires": None,
                "is_authenticated": False,
                "bookings": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": None
            }
            
            result = self.db.guest_accounts.insert_one(guest_data)
            guest_data["_id"] = str(result.inserted_id)
            
            return guest_data
        
        except Exception as e:
            logger.error(f"Error creating/getting guest: {e}")
            raise Exception(f"Failed to create/get guest: {str(e)}")
    
    async def generate_magic_link(self, email: str) -> Dict:
        """Generate magic link for guest"""
        try:
            guest = self.db.guest_accounts.find_one({"email": email})
            
            if not guest:
                raise ValueError("Guest not found")
            
            # Check rate limiting
            if guest.get("magic_token_expires"):
                if datetime.utcnow() < guest["magic_token_expires"]:
                    raise ValueError("Magic link already sent. Please wait before requesting another.")
            
            magic_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            self.db.guest_accounts.update_one(
                {"_id": guest["_id"]},
                {
                    "$set": {
                        "magic_token": magic_token,
                        "magic_token_expires": expires_at,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "email": email,
                "magic_token": magic_token,
                "expires_at": expires_at.isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error generating magic link: {e}")
            raise Exception(f"Failed to generate magic link: {str(e)}")
    
    async def authenticate_guest(self, email: str, magic_token: str) -> Dict:
        """Authenticate guest with magic token"""
        try:
            guest = self.db.guest_accounts.find_one({"email": email})
            
            if not guest:
                raise ValueError("Guest not found")
            
            if not guest.get("magic_token"):
                raise ValueError("No magic token found")
            
            if guest["magic_token"] != magic_token:
                raise ValueError("Invalid magic token")
            
            if datetime.utcnow() > guest["magic_token_expires"]:
                raise ValueError("Magic token expired")
            
            self.db.guest_accounts.update_one(
                {"_id": guest["_id"]},
                {
                    "$set": {
                        "is_authenticated": True,
                        "magic_token": None,
                        "magic_token_expires": None,
                        "last_login": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            guest["_id"] = str(guest["_id"])
            guest["is_authenticated"] = True
            
            return guest
        
        except Exception as e:
            logger.error(f"Error authenticating guest: {e}")
            raise Exception(f"Failed to authenticate guest: {str(e)}")
    
    async def get_guest_bookings(self, email: str) -> list:
        """Get all bookings for a guest"""
        try:
            guest = self.db.guest_accounts.find_one({"email": email})
            
            if not guest:
                return []
            
            booking_ids = guest.get("bookings", [])
            bookings = []
            
            for booking_id in booking_ids:
                booking = self.db.marketplace_bookings.find_one({"_id": ObjectId(booking_id)})
                if booking:
                    booking["_id"] = str(booking["_id"])
                    bookings.append(booking)
            
            return bookings
        
        except Exception as e:
            logger.error(f"Error getting guest bookings: {e}")
            return []
