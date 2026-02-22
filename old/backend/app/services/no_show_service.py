"""
No-Show Service
"""
from typing import List, Optional
from datetime import datetime
from app.models.no_show import NoShowCreate, NoShowInDB


class NoShowService:
    """Service for managing no-show records"""
    
    @staticmethod
    def create_no_show(db, tenant_id: str, booking_id: str, client_id: str, 
                       recorded_by: str, fee_charged: Optional[float] = None,
                       notes: Optional[str] = None) -> dict:
        """Create a no-show record"""
        no_show_data = {
            "tenant_id": tenant_id,
            "booking_id": booking_id,
            "client_id": client_id,
            "recorded_by": recorded_by,
            "fee_charged": fee_charged,
            "notes": notes,
            "recorded_at": datetime.utcnow()
        }
        result = db["no_shows"].insert_one(no_show_data)
        return {"id": str(result.inserted_id), **no_show_data}
    
    @staticmethod
    def get_no_show(db, tenant_id: str, no_show_id: str) -> Optional[dict]:
        """Get a no-show record"""
        return db["no_shows"].find_one({
            "_id": no_show_id,
            "tenant_id": tenant_id
        })
    
    @staticmethod
    def get_client_no_shows(db, tenant_id: str, client_id: str) -> List[dict]:
        """Get all no-shows for a client"""
        return list(db["no_shows"].find({
            "tenant_id": tenant_id,
            "client_id": client_id
        }).sort("recorded_at", -1))
    
    @staticmethod
    def get_booking_no_show(db, tenant_id: str, booking_id: str) -> Optional[dict]:
        """Get no-show record for a booking"""
        return db["no_shows"].find_one({
            "tenant_id": tenant_id,
            "booking_id": booking_id
        })
    
    @staticmethod
    def calculate_no_show_fee(db, tenant_id: str, client_id: str) -> float:
        """Calculate no-show fee based on client history"""
        no_show_count = db["no_shows"].count_documents({
            "tenant_id": tenant_id,
            "client_id": client_id
        })
        base_fee = 25.0
        return base_fee * (1 + (no_show_count * 0.1))
