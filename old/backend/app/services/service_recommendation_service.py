"""
Service recommendation service - Analyzes booking patterns to suggest related services
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from collections import defaultdict, Counter

from app.database import Database

logger = logging.getLogger(__name__)


class ServiceRecommendationService:
    """Service for generating service recommendations based on booking patterns"""
    
    @staticmethod
    def analyze_booking_patterns(tenant_id: str, days: int = 90) -> Dict[str, List[str]]:
        """
        Analyze booking patterns to find services frequently booked together
        
        Args:
            tenant_id: Tenant ID
            days: Number of days to analyze (default 90)
            
        Returns:
            Dict mapping service_id to list of frequently co-booked service_ids
        """
        db = Database.get_db()
        
        # Get bookings from the last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "created_at": {"$gte": cutoff_date},
            "status": {"$in": ["confirmed", "completed"]}
        }))
        
        # Group bookings by client
        client_bookings = defaultdict(list)
        for booking in bookings:
            client_id = booking.get("client_id")
            service_id = booking.get("service_id")
            if client_id and service_id:
                client_bookings[client_id].append(service_id)
        
        # Find service pairs that are frequently booked together
        service_pairs = defaultdict(Counter)
        
        for client_id, service_ids in client_bookings.items():
            # Get unique services for this client
            unique_services = list(set(service_ids))
            
            # Create pairs
            for i, service_a in enumerate(unique_services):
                for service_b in unique_services[i+1:]:
                    service_pairs[service_a][service_b] += 1
                    service_pairs[service_b][service_a] += 1
        
        # Convert to recommendations (top 5 for each service)
        recommendations = {}
        for service_id, related_services in service_pairs.items():
            # Get top 5 most frequently co-booked services
            top_related = related_services.most_common(5)
            recommendations[service_id] = [svc_id for svc_id, count in top_related if count >= 2]
        
        return recommendations
    
    @staticmethod
    def get_recommendations(service_id: str, tenant_id: str, limit: int = 5) -> List[Dict]:
        """
        Get service recommendations for a specific service
        
        Args:
            service_id: Service ID to get recommendations for
            tenant_id: Tenant ID
            limit: Maximum number of recommendations (default 5)
            
        Returns:
            List of recommended service dicts with metadata
        """
        db = Database.get_db()
        
        # Check if service exists
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            return []
        
        # Get manual recommendations first
        manual_recs = service.get("recommended_services", [])
        
        # Get automatic recommendations from booking patterns
        patterns = ServiceRecommendationService.analyze_booking_patterns(tenant_id)
        auto_recs = patterns.get(service_id, [])
        
        # Combine manual and automatic (manual takes priority)
        all_rec_ids = []
        seen = set()
        
        # Add manual recommendations first
        for rec_id in manual_recs:
            if rec_id not in seen and rec_id != service_id:
                all_rec_ids.append(rec_id)
                seen.add(rec_id)
        
        # Add automatic recommendations
        for rec_id in auto_recs:
            if rec_id not in seen and rec_id != service_id and len(all_rec_ids) < limit:
                all_rec_ids.append(rec_id)
                seen.add(rec_id)
        
        # Fetch service details
        recommendations = []
        for rec_id in all_rec_ids[:limit]:
            try:
                rec_service = db.services.find_one({
                    "_id": ObjectId(rec_id),
                    "tenant_id": tenant_id,
                    "is_active": True
                })
                
                if rec_service:
                    recommendations.append({
                        "id": str(rec_service["_id"]),
                        "name": rec_service["name"],
                        "price": rec_service.get("price", 0),
                        "duration_minutes": rec_service.get("duration_minutes", 0),
                        "category": rec_service.get("category"),
                        "photo_url": rec_service.get("photo_url"),
                        "is_manual": rec_id in manual_recs
                    })
            except Exception as e:
                logger.error(f"Error fetching recommended service {rec_id}: {e}")
                continue
        
        return recommendations
    
    @staticmethod
    def add_manual_recommendation(
        service_id: str,
        recommended_service_id: str,
        tenant_id: str
    ) -> bool:
        """
        Add a manual recommendation for a service
        
        Args:
            service_id: Service ID to add recommendation to
            recommended_service_id: Service ID to recommend
            tenant_id: Tenant ID
            
        Returns:
            True if successful
        """
        db = Database.get_db()
        
        # Verify both services exist and belong to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        recommended_service = db.services.find_one({
            "_id": ObjectId(recommended_service_id),
            "tenant_id": tenant_id
        })
        
        if not service or not recommended_service:
            return False
        
        # Don't allow self-recommendation
        if service_id == recommended_service_id:
            return False
        
        # Add to recommended_services array (avoid duplicates)
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {
                "$addToSet": {"recommended_services": recommended_service_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"Added manual recommendation: {service_id} -> {recommended_service_id}")
        return True
    
    @staticmethod
    def remove_manual_recommendation(
        service_id: str,
        recommended_service_id: str,
        tenant_id: str
    ) -> bool:
        """
        Remove a manual recommendation for a service
        
        Args:
            service_id: Service ID to remove recommendation from
            recommended_service_id: Service ID to stop recommending
            tenant_id: Tenant ID
            
        Returns:
            True if successful
        """
        db = Database.get_db()
        
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            return False
        
        # Remove from recommended_services array
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {
                "$pull": {"recommended_services": recommended_service_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"Removed manual recommendation: {service_id} -> {recommended_service_id}")
        return True
    
    @staticmethod
    def track_recommendation_conversion(
        service_id: str,
        recommended_service_id: str,
        tenant_id: str,
        converted: bool = True
    ) -> None:
        """
        Track when a recommendation leads to a booking
        
        Args:
            service_id: Original service ID
            recommended_service_id: Recommended service that was booked
            tenant_id: Tenant ID
            converted: Whether the recommendation converted to a booking
        """
        db = Database.get_db()
        
        # Store conversion tracking data
        conversion_data = {
            "tenant_id": tenant_id,
            "service_id": service_id,
            "recommended_service_id": recommended_service_id,
            "converted": converted,
            "created_at": datetime.utcnow()
        }
        
        db.recommendation_conversions.insert_one(conversion_data)
        logger.info(f"Tracked recommendation conversion: {service_id} -> {recommended_service_id} (converted: {converted})")
    
    @staticmethod
    def get_recommendation_stats(service_id: str, tenant_id: str) -> Dict:
        """
        Get recommendation statistics for a service
        
        Args:
            service_id: Service ID
            tenant_id: Tenant ID
            
        Returns:
            Dict with recommendation statistics
        """
        db = Database.get_db()
        
        # Get conversion data
        conversions = list(db.recommendation_conversions.find({
            "tenant_id": tenant_id,
            "service_id": service_id
        }))
        
        total_shown = len(conversions)
        total_converted = sum(1 for c in conversions if c.get("converted", False))
        conversion_rate = (total_converted / total_shown * 100) if total_shown > 0 else 0
        
        # Get breakdown by recommended service
        by_service = defaultdict(lambda: {"shown": 0, "converted": 0})
        for conversion in conversions:
            rec_id = conversion.get("recommended_service_id")
            by_service[rec_id]["shown"] += 1
            if conversion.get("converted", False):
                by_service[rec_id]["converted"] += 1
        
        return {
            "total_shown": total_shown,
            "total_converted": total_converted,
            "conversion_rate": round(conversion_rate, 2),
            "by_service": dict(by_service)
        }


# Singleton instance
service_recommendation_service = ServiceRecommendationService()
