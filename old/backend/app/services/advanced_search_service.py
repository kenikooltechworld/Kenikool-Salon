"""
Advanced Search and Filtering Service - Task 17
"""
from typing import Dict, List, Optional
from bson import ObjectId
import logging

from app.database import Database

logger = logging.getLogger(__name__)


class AdvancedSearchService:
    """Service for advanced search and filtering"""
    
    @staticmethod
    async def search_services(
        salon_id: str,
        query: str = "",
        category: Optional[str] = None,
        min_price: float = 0,
        max_price: float = float('inf'),
        min_duration: int = 0,
        max_duration: int = float('inf'),
        skip: int = 0,
        limit: int = 50
    ) -> Dict:
        """Search services with filters - Requirements: 18"""
        db = Database.get_db()
        
        filters = {"tenant_id": salon_id}
        
        # Text search
        if query:
            filters["$text"] = {"$search": query}
        
        # Category filter
        if category:
            filters["category"] = category
        
        # Price range filter
        if min_price > 0 or max_price < float('inf'):
            filters["price"] = {}
            if min_price > 0:
                filters["price"]["$gte"] = min_price
            if max_price < float('inf'):
                filters["price"]["$lte"] = max_price
        
        # Duration filter
        if min_duration > 0 or max_duration < float('inf'):
            filters["duration_minutes"] = {}
            if min_duration > 0:
                filters["duration_minutes"]["$gte"] = min_duration
            if max_duration < float('inf'):
                filters["duration_minutes"]["$lte"] = max_duration
        
        services = list(db.services.find(filters).skip(skip).limit(limit))
        total = db.services.count_documents(filters)
        
        return {
            "query": query,
            "filters": {
                "category": category,
                "price_range": {"min": min_price, "max": max_price},
                "duration_range": {"min": min_duration, "max": max_duration}
            },
            "total": total,
            "results": services,
            "skip": skip,
            "limit": limit
        }
    
    @staticmethod
    async def search_stylists(
        salon_id: str,
        query: str = "",
        specialty: Optional[str] = None,
        min_rating: float = 0,
        availability: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Dict:
        """Search stylists with filters - Requirements: 18"""
        db = Database.get_db()
        
        filters = {"tenant_id": salon_id}
        
        # Text search
        if query:
            filters["$text"] = {"$search": query}
        
        # Specialty filter
        if specialty:
            filters["specialties"] = specialty
        
        # Rating filter
        if min_rating > 0:
            filters["average_rating"] = {"$gte": min_rating}
        
        # Availability filter
        if availability:
            filters["availability_status"] = availability
        
        stylists = list(db.stylists.find(filters).skip(skip).limit(limit))
        total = db.stylists.count_documents(filters)
        
        return {
            "query": query,
            "filters": {
                "specialty": specialty,
                "min_rating": min_rating,
                "availability": availability
            },
            "total": total,
            "results": stylists,
            "skip": skip,
            "limit": limit
        }
    
    @staticmethod
    async def get_service_categories(salon_id: str) -> List[str]:
        """Get all service categories - Requirements: 18"""
        db = Database.get_db()
        
        categories = db.services.distinct("category", {"tenant_id": salon_id})
        return sorted(categories)
    
    @staticmethod
    async def get_stylist_specialties(salon_id: str) -> List[str]:
        """Get all stylist specialties - Requirements: 18"""
        db = Database.get_db()
        
        specialties = db.stylists.distinct("specialties", {"tenant_id": salon_id})
        return sorted(specialties)
    
    @staticmethod
    async def get_price_range(salon_id: str) -> Dict:
        """Get min and max prices for services - Requirements: 18"""
        db = Database.get_db()
        
        services = list(db.services.find(
            {"tenant_id": salon_id},
            {"price": 1}
        ).sort("price", 1).limit(1))
        
        min_price = services[0]["price"] if services else 0
        
        services = list(db.services.find(
            {"tenant_id": salon_id},
            {"price": 1}
        ).sort("price", -1).limit(1))
        
        max_price = services[0]["price"] if services else 0
        
        return {
            "min": min_price,
            "max": max_price
        }
    
    @staticmethod
    async def get_duration_range(salon_id: str) -> Dict:
        """Get min and max durations for services - Requirements: 18"""
        db = Database.get_db()
        
        services = list(db.services.find(
            {"tenant_id": salon_id},
            {"duration_minutes": 1}
        ).sort("duration_minutes", 1).limit(1))
        
        min_duration = services[0]["duration_minutes"] if services else 0
        
        services = list(db.services.find(
            {"tenant_id": salon_id},
            {"duration_minutes": 1}
        ).sort("duration_minutes", -1).limit(1))
        
        max_duration = services[0]["duration_minutes"] if services else 0
        
        return {
            "min": min_duration,
            "max": max_duration
        }


advanced_search_service = AdvancedSearchService()
