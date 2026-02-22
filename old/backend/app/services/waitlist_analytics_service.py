"""
Waitlist Analytics Service - Provides analytics and insights for waitlist management
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from bson import ObjectId
from app.database import Database
import logging

logger = logging.getLogger(__name__)


class WaitlistAnalyticsService:
    """Service for waitlist analytics and reporting"""
    
    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()
    
    @staticmethod
    def get_waitlist_stats(
        tenant_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict:
        """
        Get overall waitlist statistics.
        
        Args:
            tenant_id: Tenant ID
            date_from: Optional start date for filtering
            date_to: Optional end date for filtering
            
        Returns:
            Dict with overall statistics
            
        Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
        """
        db = WaitlistAnalyticsService._get_db()
        
        # Build query
        query = {"tenant_id": tenant_id}
        
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = date_from
            if date_to:
                date_query["$lte"] = date_to
            query["created_at"] = date_query
        
        # Get all entries
        entries = list(db.waitlist.find(query))
        
        # Calculate statistics
        total_entries = len(entries)
        
        # Count by status
        status_counts = {}
        for entry in entries:
            status = entry.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate average wait time (in days)
        wait_times = []
        for entry in entries:
            if entry.get("status") in ["notified", "booked", "expired"]:
                created_at = entry.get("created_at")
                if created_at:
                    if entry.get("status") == "booked":
                        end_time = entry.get("booked_at", datetime.utcnow())
                    elif entry.get("status") == "expired":
                        end_time = entry.get("updated_at", datetime.utcnow())
                    else:
                        end_time = entry.get("notified_at", datetime.utcnow())
                    
                    wait_time = (end_time - created_at).days
                    wait_times.append(wait_time)
        
        avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
        
        return {
            "total_entries": total_entries,
            "by_status": status_counts,
            "average_wait_time_days": round(avg_wait_time, 2),
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }
    
    @staticmethod
    def get_service_demand(
        tenant_id: str,
        limit: int = 10,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get top requested services.
        
        Args:
            tenant_id: Tenant ID
            limit: Number of top services to return
            date_from: Optional start date for filtering
            date_to: Optional end date for filtering
            
        Returns:
            List of services with request counts
            
        Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
        """
        db = WaitlistAnalyticsService._get_db()
        
        # Build query
        query = {"tenant_id": tenant_id}
        
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = date_from
            if date_to:
                date_query["$lte"] = date_to
            query["created_at"] = date_query
        
        # Get all entries
        entries = list(db.waitlist.find(query))
        
        # Count by service
        service_counts = {}
        for entry in entries:
            service_id = str(entry.get("service_id", "unknown"))
            service_name = entry.get("service_name", "Unknown Service")
            
            if service_id not in service_counts:
                service_counts[service_id] = {
                    "service_id": service_id,
                    "service_name": service_name,
                    "count": 0
                }
            
            service_counts[service_id]["count"] += 1
        
        # Sort by count and return top N
        sorted_services = sorted(
            service_counts.values(),
            key=lambda x: x["count"],
            reverse=True
        )
        
        return sorted_services[:limit]
    
    @staticmethod
    def get_stylist_demand(
        tenant_id: str,
        limit: int = 10,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get top requested stylists.
        
        Args:
            tenant_id: Tenant ID
            limit: Number of top stylists to return
            date_from: Optional start date for filtering
            date_to: Optional end date for filtering
            
        Returns:
            List of stylists with request counts
            
        Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
        """
        db = WaitlistAnalyticsService._get_db()
        
        # Build query
        query = {"tenant_id": tenant_id}
        
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = date_from
            if date_to:
                date_query["$lte"] = date_to
            query["created_at"] = date_query
        
        # Get all entries
        entries = list(db.waitlist.find(query))
        
        # Count by stylist
        stylist_counts = {}
        for entry in entries:
            stylist_id = str(entry.get("stylist_id", "any"))
            stylist_name = entry.get("stylist_name", "Any Stylist")
            
            if stylist_id not in stylist_counts:
                stylist_counts[stylist_id] = {
                    "stylist_id": stylist_id,
                    "stylist_name": stylist_name,
                    "count": 0
                }
            
            stylist_counts[stylist_id]["count"] += 1
        
        # Sort by count and return top N
        sorted_stylists = sorted(
            stylist_counts.values(),
            key=lambda x: x["count"],
            reverse=True
        )
        
        return sorted_stylists[:limit]
    
    @staticmethod
    def get_conversion_metrics(
        tenant_id: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict:
        """
        Get conversion rate analysis.
        
        Args:
            tenant_id: Tenant ID
            date_from: Optional start date for filtering
            date_to: Optional end date for filtering
            
        Returns:
            Dict with conversion metrics
            
        Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
        """
        db = WaitlistAnalyticsService._get_db()
        
        # Build query
        query = {"tenant_id": tenant_id}
        
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = date_from
            if date_to:
                date_query["$lte"] = date_to
            query["created_at"] = date_query
        
        # Get all entries
        entries = list(db.waitlist.find(query))
        
        total_entries = len(entries)
        
        # Count conversions (booked status)
        booked_count = sum(1 for e in entries if e.get("status") == "booked")
        notified_count = sum(1 for e in entries if e.get("status") == "notified")
        expired_count = sum(1 for e in entries if e.get("status") == "expired")
        waiting_count = sum(1 for e in entries if e.get("status") == "waiting")
        
        # Calculate conversion rates
        conversion_rate = (booked_count / total_entries * 100) if total_entries > 0 else 0
        notification_rate = (notified_count / total_entries * 100) if total_entries > 0 else 0
        expiration_rate = (expired_count / total_entries * 100) if total_entries > 0 else 0
        
        return {
            "total_entries": total_entries,
            "booked": booked_count,
            "notified": notified_count,
            "expired": expired_count,
            "waiting": waiting_count,
            "conversion_rate_percent": round(conversion_rate, 2),
            "notification_rate_percent": round(notification_rate, 2),
            "expiration_rate_percent": round(expiration_rate, 2),
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }


# Create singleton instance
waitlist_analytics_service = WaitlistAnalyticsService()
