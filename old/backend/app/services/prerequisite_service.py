"""
Prerequisite Service
"""
from typing import List, Optional
from datetime import datetime


class PrerequisiteService:
    """Service for managing service prerequisites"""
    
    @staticmethod
    def add_prerequisite(db, tenant_id: str, service_id: str, 
                        prerequisite_service_id: str, is_required: bool = True) -> dict:
        """Add a prerequisite to a service"""
        prerequisite_data = {
            "tenant_id": tenant_id,
            "service_id": service_id,
            "prerequisite_service_id": prerequisite_service_id,
            "is_required": is_required,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = db["prerequisites"].insert_one(prerequisite_data)
        return {"id": str(result.inserted_id), **prerequisite_data}
    
    @staticmethod
    def get_service_prerequisites(db, tenant_id: str, service_id: str) -> List[dict]:
        """Get all prerequisites for a service"""
        return list(db["prerequisites"].find({
            "tenant_id": tenant_id,
            "service_id": service_id
        }))
    
    @staticmethod
    def check_prerequisites_completed(db, tenant_id: str, client_id: str, 
                                     service_id: str) -> bool:
        """Check if client has completed all prerequisites for a service"""
        prerequisites = db["prerequisites"].find({
            "tenant_id": tenant_id,
            "service_id": service_id,
            "is_required": True
        })
        
        for prereq in prerequisites:
            completed = db["bookings"].find_one({
                "tenant_id": tenant_id,
                "client_id": client_id,
                "service_id": prereq["prerequisite_service_id"],
                "status": "completed"
            })
            if not completed:
                return False
        return True
    
    @staticmethod
    def get_client_completed_services(db, tenant_id: str, client_id: str) -> List[str]:
        """Get list of services completed by client"""
        bookings = db["bookings"].find({
            "tenant_id": tenant_id,
            "client_id": client_id,
            "status": "completed"
        })
        return list(set([b["service_id"] for b in bookings]))
