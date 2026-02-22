"""
Location Analytics Service - Calculate location performance metrics
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from app.database import Database

logger = logging.getLogger(__name__)


class LocationAnalyticsService:
    """Service for calculating location-based analytics and metrics"""
    
    @staticmethod
    def get_location_metrics(
        location_id: str,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Calculate all location metrics for a given date range
        
        Requirements: 7.1-7.7
        
        Args:
            location_id: Location ID
            tenant_id: Tenant ID
            start_date: Start date for metrics (default: 30 days ago)
            end_date: End date for metrics (default: today)
            
        Returns:
            Dict with all location metrics
        """
        db = Database.get_db()
        
        # Set default date range (last 30 days)
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Validate location exists
        location = db.locations.find_one({
            "_id": ObjectId(location_id),
            "tenant_id": tenant_id
        })
        
        if not location:
            raise ValueError(f"Location not found: {location_id}")
        
        # Calculate all metrics
        total_revenue = LocationAnalyticsService.calculate_revenue(
            location_id, tenant_id, start_date, end_date
        )
        
        total_bookings = LocationAnalyticsService.count_bookings(
            location_id, tenant_id, start_date, end_date
        )
        
        completed_bookings = LocationAnalyticsService.count_completed_bookings(
            location_id, tenant_id, start_date, end_date
        )
        
        occupancy_rate = LocationAnalyticsService.calculate_occupancy(
            location_id, tenant_id, start_date, end_date
        )
        
        top_services = LocationAnalyticsService.get_top_services(
            location_id, tenant_id, start_date, end_date
        )
        
        staff_performance = LocationAnalyticsService.get_staff_performance(
            location_id, tenant_id, start_date, end_date
        )
        
        average_booking_value = (
            total_revenue / total_bookings if total_bookings > 0 else 0
        )
        
        return {
            "location_id": location_id,
            "location_name": location.get("name", ""),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "revenue": {
                "total": total_revenue,
                "average_per_booking": average_booking_value
            },
            "bookings": {
                "total": total_bookings,
                "completed": completed_bookings,
                "completion_rate": (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
            },
            "occupancy": {
                "rate": occupancy_rate,
                "capacity": location.get("capacity", 0)
            },
            "top_services": top_services,
            "staff_performance": staff_performance
        }
    
    @staticmethod
    def calculate_revenue(
        location_id: str,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Calculate total revenue for a location
        
        Requirements: 7.1
        """
        db = Database.get_db()
        
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "location_id": location_id,
                    "status": "completed",
                    "completed_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$total_price"}
                }
            }
        ]
        
        result = list(db.bookings.aggregate(pipeline))
        return result[0]["total_revenue"] if result else 0.0
    
    @staticmethod
    def count_bookings(
        location_id: str,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """
        Count total bookings for a location
        
        Requirements: 7.2
        """
        db = Database.get_db()
        
        count = db.bookings.count_documents({
            "tenant_id": tenant_id,
            "location_id": location_id,
            "created_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
        
        return count
    
    @staticmethod
    def count_completed_bookings(
        location_id: str,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """
        Count completed bookings for a location
        """
        db = Database.get_db()
        
        count = db.bookings.count_documents({
            "tenant_id": tenant_id,
            "location_id": location_id,
            "status": "completed",
            "completed_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
        
        return count
    
    @staticmethod
    def calculate_occupancy(
        location_id: str,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Calculate occupancy rate for a location
        
        Requirements: 7.3
        """
        db = Database.get_db()
        
        # Get location capacity
        location = db.locations.find_one({
            "_id": ObjectId(location_id),
            "tenant_id": tenant_id
        })
        
        if not location or not location.get("capacity"):
            return 0.0
        
        capacity = location["capacity"]
        
        # Calculate number of days in range
        days = (end_date - start_date).days + 1
        
        # Get completed bookings
        completed_bookings = LocationAnalyticsService.count_completed_bookings(
            location_id, tenant_id, start_date, end_date
        )
        
        # Calculate occupancy rate
        max_possible_bookings = capacity * days
        occupancy_rate = (completed_bookings / max_possible_bookings * 100) if max_possible_bookings > 0 else 0.0
        
        return min(occupancy_rate, 100.0)  # Cap at 100%
    
    @staticmethod
    def get_top_services(
        location_id: str,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get top performing services for a location
        
        Requirements: 7.4
        """
        db = Database.get_db()
        
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "location_id": location_id,
                    "status": "completed",
                    "completed_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": "$service_id",
                    "service_name": {"$first": "$service_name"},
                    "count": {"$sum": 1},
                    "total_revenue": {"$sum": "$service_price"},
                    "average_price": {"$avg": "$service_price"}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        results = list(db.bookings.aggregate(pipeline))
        
        return [
            {
                "service_id": str(r["_id"]),
                "service_name": r.get("service_name", "Unknown"),
                "bookings": r["count"],
                "total_revenue": r["total_revenue"],
                "average_price": r["average_price"]
            }
            for r in results
        ]
    
    @staticmethod
    def get_staff_performance(
        location_id: str,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Get staff performance metrics for a location
        
        Requirements: 7.5
        """
        db = Database.get_db()
        
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "location_id": location_id,
                    "status": "completed",
                    "completed_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": "$stylist_id",
                    "stylist_name": {"$first": "$stylist_name"},
                    "bookings": {"$sum": 1},
                    "total_revenue": {"$sum": "$total_price"},
                    "average_rating": {"$avg": "$rating"},
                    "average_booking_value": {"$avg": "$total_price"}
                }
            },
            {
                "$sort": {"total_revenue": -1}
            }
        ]
        
        results = list(db.bookings.aggregate(pipeline))
        
        return [
            {
                "stylist_id": str(r["_id"]),
                "stylist_name": r.get("stylist_name", "Unknown"),
                "bookings": r["bookings"],
                "total_revenue": r["total_revenue"],
                "average_rating": round(r.get("average_rating", 0), 2),
                "average_booking_value": r["average_booking_value"]
            }
            for r in results
        ]