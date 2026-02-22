"""
Service History Service - Business logic for client service history
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class ServiceHistoryService:
    """Service history service for retrieving client service history"""
    
    @staticmethod
    def get_client_history(
        client_id: str,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        service_type: Optional[str] = None,
        stylist_id: Optional[str] = None,
        offset: int = 0,
        limit: int = 20
    ) -> Dict:
        """
        Get service history for a client with filtering and pagination
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            start_date: Filter from this date
            end_date: Filter until this date
            service_type: Filter by service category
            stylist_id: Filter by stylist
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            Dict with service history items and pagination info
        """
        db = Database.get_db()
        
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if not client:
            raise NotFoundException("Client not found")
        
        # Build query
        query = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "status": "completed"
        }
        
        # Add date filters
        if start_date or end_date:
            query["booking_date"] = {}
            if start_date:
                query["booking_date"]["$gte"] = start_date
            if end_date:
                query["booking_date"]["$lte"] = end_date
        
        # Add stylist filter
        if stylist_id:
            query["stylist_id"] = stylist_id
        
        # Get total count
        total = db.bookings.count_documents(query)
        
        # Get bookings
        bookings = list(db.bookings.find(query)
                       .sort("booking_date", -1)
                       .skip(offset)
                       .limit(limit))
        
        # Enrich with service and stylist details
        history_items = []
        
        for booking in bookings:
            # Get service details
            service = db.services.find_one({"_id": ObjectId(booking["service_id"])})
            
            # Get stylist details
            stylist = db.users.find_one({"_id": ObjectId(booking["stylist_id"])})
            
            # Filter by service type if specified
            if service_type and service and service.get("category") != service_type:
                continue
            
            # Get photos for this booking
            photos = []
            client_photos = client.get("photos", [])
            for photo in client_photos:
                # Link photos by date proximity (same day as booking)
                if photo.get("uploaded_at"):
                    photo_date = photo["uploaded_at"].date()
                    booking_date = booking["booking_date"].date()
                    if photo_date == booking_date:
                        photos.append(photo["photo_url"])
            
            # Get payment for cost
            payment = db.payments.find_one({
                "tenant_id": tenant_id,
                "booking_id": str(booking["_id"]),
                "status": "completed"
            })
            
            cost = payment.get("amount", 0) if payment else 0
            
            history_item = {
                "bookingId": str(booking["_id"]),
                "serviceId": booking["service_id"],
                "serviceName": service["name"] if service else "Unknown Service",
                "stylistId": booking["stylist_id"],
                "stylistName": stylist["name"] if stylist else "Unknown Stylist",
                "bookingDate": booking["booking_date"],
                "durationMinutes": service["duration_minutes"] if service else 0,
                "cost": float(cost),
                "status": booking["status"],
                "notes": booking.get("notes"),
                "photos": photos
            }
            
            history_items.append(history_item)
        
        return {
            "items": history_items,
            "total": total,
            "page_info": {
                "hasNextPage": offset + len(history_items) < total,
                "hasPreviousPage": offset > 0
            }
        }
    
    @staticmethod
    def get_service_frequency(client_id: str, tenant_id: str) -> Dict:
        """
        Calculate service frequency metrics for a client
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            
        Returns:
            Dict with service frequency metrics
        """
        db = Database.get_db()
        
        # Get all completed bookings
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "client_id": client_id,
            "status": "completed"
        }).sort("booking_date", 1))
        
        if len(bookings) < 2:
            return {
                "totalServices": len(bookings),
                "averageDaysBetween": None,
                "mostFrequentService": None,
                "serviceBreakdown": {}
            }
        
        # Calculate average days between visits
        gaps = []
        for i in range(1, len(bookings)):
            gap = (bookings[i]["booking_date"] - bookings[i-1]["booking_date"]).days
            gaps.append(gap)
        
        average_days = sum(gaps) / len(gaps) if gaps else None
        
        # Count services
        service_counts = {}
        for booking in bookings:
            service_id = booking["service_id"]
            service = db.services.find_one({"_id": ObjectId(service_id)})
            service_name = service["name"] if service else "Unknown"
            
            service_counts[service_name] = service_counts.get(service_name, 0) + 1
        
        # Find most frequent service
        most_frequent = max(service_counts.items(), key=lambda x: x[1]) if service_counts else (None, 0)
        
        return {
            "totalServices": len(bookings),
            "averageDaysBetween": round(average_days, 1) if average_days else None,
            "mostFrequentService": most_frequent[0],
            "serviceBreakdown": service_counts
        }


# Singleton instance
service_history_service = ServiceHistoryService()
