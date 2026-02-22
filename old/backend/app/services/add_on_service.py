"""
Add-On Service
"""
from typing import List, Optional
from datetime import datetime


class AddOnService:
    """Service for managing service add-ons"""
    
    @staticmethod
    def create_add_on(db, tenant_id: str, service_id: str, name: str, 
                     price: float, duration_minutes: int, 
                     description: Optional[str] = None) -> dict:
        """Create an add-on"""
        add_on_data = {
            "tenant_id": tenant_id,
            "service_id": service_id,
            "name": name,
            "description": description,
            "price": price,
            "duration_minutes": duration_minutes,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = db["add_ons"].insert_one(add_on_data)
        return {"id": str(result.inserted_id), **add_on_data}
    
    @staticmethod
    def get_service_add_ons(db, tenant_id: str, service_id: str) -> List[dict]:
        """Get all add-ons for a service"""
        return list(db["add_ons"].find({
            "tenant_id": tenant_id,
            "service_id": service_id,
            "is_active": True
        }))
    
    @staticmethod
    def get_add_on(db, tenant_id: str, add_on_id: str) -> Optional[dict]:
        """Get a specific add-on"""
        return db["add_ons"].find_one({
            "_id": add_on_id,
            "tenant_id": tenant_id
        })
    
    @staticmethod
    def calculate_add_ons_cost(db, tenant_id: str, add_on_ids: List[str]) -> float:
        """Calculate total cost of add-ons"""
        add_ons = db["add_ons"].find({
            "_id": {"$in": add_on_ids},
            "tenant_id": tenant_id
        })
        return sum(ao["price"] for ao in add_ons)
    
    @staticmethod
    def calculate_add_ons_duration(db, tenant_id: str, add_on_ids: List[str]) -> int:
        """Calculate total duration of add-ons"""
        add_ons = db["add_ons"].find({
            "_id": {"$in": add_on_ids},
            "tenant_id": tenant_id
        })
        return sum(ao["duration_minutes"] for ao in add_ons)
