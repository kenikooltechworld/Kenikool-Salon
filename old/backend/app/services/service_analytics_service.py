"""
Service Analytics Service
Handles service performance analytics and statistics calculations
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ServiceAnalyticsService:
    """Service for calculating service analytics and statistics"""

    def __init__(self, db):
        self.db = db

    def calculate_service_statistics(
        self, service_id: str, tenant_id: str
    ) -> Dict:
        """
        Calculate comprehensive service statistics
        
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        # Get all bookings for service
        bookings = list(
            self.db.bookings.find({"service_id": service_id, "tenant_id": tenant_id})
        )

        total_bookings = len(bookings)
        completed = [b for b in bookings if b.get("status") == "completed"]
        cancelled = [b for b in bookings if b.get("status") == "cancelled"]

        completed_bookings = len(completed)
        cancelled_bookings = len(cancelled)

        # Calculate revenue
        total_revenue = sum(b.get("service_price", 0) for b in completed)
        avg_booking_value = (
            total_revenue / completed_bookings if completed_bookings > 0 else 0
        )

        # Calculate revenue trend
        revenue_trend = self._calculate_revenue_trend(service_id, tenant_id)

        # Get popularity rank
        popularity_rank = self._get_popularity_rank(service_id, tenant_id)

        # Get average rating
        avg_rating = self._get_average_rating(service_id, tenant_id)

        # Calculate conversion rate
        conversion_rate = self._calculate_conversion_rate(service_id, tenant_id)

        return {
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "total_revenue": total_revenue,
            "average_booking_value": avg_booking_value,
            "revenue_trend": revenue_trend,
            "popularity_rank": popularity_rank,
            "average_rating": avg_rating,
            "conversion_rate": conversion_rate,
        }

    def _calculate_revenue_trend(
        self, service_id: str, tenant_id: str
    ) -> Optional[float]:
        """Calculate revenue trend comparing current to previous period"""
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        sixty_days_ago = now - timedelta(days=60)

        # Recent period revenue (last 30 days)
        recent_bookings = list(
            self.db.bookings.find(
                {
                    "service_id": service_id,
                    "tenant_id": tenant_id,
                    "status": "completed",
                    "completed_at": {"$gte": thirty_days_ago, "$lte": now},
                }
            )
        )
        recent_revenue = sum(b.get("service_price", 0) for b in recent_bookings)

        # Previous period revenue (30-60 days ago)
        previous_bookings = list(
            self.db.bookings.find(
                {
                    "service_id": service_id,
                    "tenant_id": tenant_id,
                    "status": "completed",
                    "completed_at": {"$gte": sixty_days_ago, "$lt": thirty_days_ago},
                }
            )
        )
        previous_revenue = sum(b.get("service_price", 0) for b in previous_bookings)

        if previous_revenue == 0:
            return None

        trend = ((recent_revenue - previous_revenue) / previous_revenue) * 100
        return round(trend, 2)

    def _get_popularity_rank(self, service_id: str, tenant_id: str) -> int:
        """Get service popularity ranking among all services"""
        # Aggregate bookings by service
        pipeline = [
            {"$match": {"tenant_id": tenant_id, "status": "completed"}},
            {"$group": {"_id": "$service_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]

        results = list(self.db.bookings.aggregate(pipeline))

        # Find rank of current service
        for idx, result in enumerate(results, start=1):
            if result["_id"] == service_id:
                return idx

        return len(results) + 1  # Not found, return last rank

    def _get_average_rating(self, service_id: str, tenant_id: str) -> float:
        """Get average rating from reviews"""
        reviews = list(
            self.db.reviews.find({"service_id": service_id, "tenant_id": tenant_id})
        )

        if not reviews:
            return 0.0

        total_rating = sum(r.get("rating", 0) for r in reviews)
        return round(total_rating / len(reviews), 2)

    def _calculate_conversion_rate(self, service_id: str, tenant_id: str) -> float:
        """Calculate conversion rate (placeholder - needs view tracking)"""
        # TODO: Implement view tracking to calculate actual conversion rate
        # For now, return 0 as placeholder
        return 0.0

    def get_revenue_chart_data(
        self, service_id: str, tenant_id: str, days: int = 30
    ) -> List[Dict]:
        """
        Get daily revenue data for chart
        
        Requirements: 2.1
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Aggregate revenue by day
        pipeline = [
            {
                "$match": {
                    "service_id": service_id,
                    "tenant_id": tenant_id,
                    "status": "completed",
                    "completed_at": {"$gte": start_date, "$lte": end_date},
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$completed_at"}
                    },
                    "revenue": {"$sum": "$service_price"},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        results = list(self.db.bookings.aggregate(pipeline))

        return [{"date": r["_id"], "revenue": r["revenue"]} for r in results]

    def get_booking_trend_data(
        self, service_id: str, tenant_id: str
    ) -> Dict:
        """
        Get booking trend comparing current month to previous month
        
        Requirements: 2.2
        """
        now = datetime.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Previous month
        if current_month_start.month == 1:
            previous_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
        else:
            previous_month_start = current_month_start.replace(month=current_month_start.month - 1)

        # Current month bookings
        current_count = self.db.bookings.count_documents(
            {
                "service_id": service_id,
                "tenant_id": tenant_id,
                "created_at": {"$gte": current_month_start},
            }
        )

        # Previous month bookings
        previous_count = self.db.bookings.count_documents(
            {
                "service_id": service_id,
                "tenant_id": tenant_id,
                "created_at": {
                    "$gte": previous_month_start,
                    "$lt": current_month_start,
                },
            }
        )

        trend = 0.0
        if previous_count > 0:
            trend = ((current_count - previous_count) / previous_count) * 100

        return {
            "current_month": current_count,
            "previous_month": previous_count,
            "trend": round(trend, 2),
        }

    def get_peak_booking_times(
        self, service_id: str, tenant_id: str
    ) -> Dict[str, int]:
        """
        Get heatmap of peak booking times
        
        Requirements: 2.6
        """
        bookings = list(
            self.db.bookings.find(
                {"service_id": service_id, "tenant_id": tenant_id}
            )
        )

        # Count bookings by hour and day of week
        heatmap = {}
        for booking in bookings:
            booking_date = booking.get("booking_date")
            if booking_date:
                if isinstance(booking_date, str):
                    try:
                        booking_date = datetime.fromisoformat(booking_date.replace('Z', '+00:00'))
                    except:
                        continue
                
                day_of_week = booking_date.strftime("%A")
                hour = booking_date.hour
                key = f"{day_of_week}_{hour}"
                heatmap[key] = heatmap.get(key, 0) + 1

        return heatmap


# Singleton instance
service_analytics_service = None


def get_service_analytics_service(db):
    """Get or create service analytics service instance"""
    global service_analytics_service
    if service_analytics_service is None:
        service_analytics_service = ServiceAnalyticsService(db)
    return service_analytics_service
