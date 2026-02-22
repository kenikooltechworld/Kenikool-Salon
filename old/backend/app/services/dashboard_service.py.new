"""
Dashboard Service
Provides metrics and analytics for the dashboard
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard metrics and analytics"""
    
    def __init__(self, db):
        """Initialize with database connection"""
        self.db = db
    
    def calculate_trend(self, current: float, previous: float) -> Optional[float]:
        """
        Calculate percentage trend between current and previous values
        
        Args:
            current: Current period value
            previous: Previous period value
            
        Returns:
            Percentage change or None if previous is 0
        """
        if previous == 0:
            if current == 0:
                return None
            return -100.0 if current < previous else None
        
        change = ((current - previous) / previous) * 100
        return round(change, 1)
    
    def get_comparison_period(
        self,
        period: str,
        reference_date: Optional[datetime] = None
    ) -> Tuple[datetime, datetime, datetime, datetime]:
        """
        Get current and previous period date ranges for comparison
        
        Args:
            period: "day", "week", or "month"
            reference_date: Reference date (defaults to now)
            
        Returns:
            Tuple of (current_start, current_end, previous_start, previous_end)
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        if period == "day":
            # Current day: start of day to reference time
            current_start = reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
            current_end = reference_date
            
            # Previous day: same time range yesterday
            previous_start = current_start - timedelta(days=1)
            previous_end = current_end - timedelta(days=1)
            
        elif period == "week":
            # Current week: last 7 days
            current_end = reference_date
            current_start = current_end - timedelta(days=7)
            
            # Previous week: 7 days before that
            previous_end = current_start
            previous_start = previous_end - timedelta(days=7)
            
        else:  # month
            # Current month: last 30 days
            current_end = reference_date
            current_start = current_end - timedelta(days=30)
            
            # Previous month: 30 days before that
            previous_end = current_start
            previous_start = previous_end - timedelta(days=30)
        
        return current_start, current_end, previous_start, previous_end
    
    def calculate_revenue(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Calculate total revenue from bookings and POS transactions
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Total revenue
        """
        # Get booking revenue
        booking_pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "status": "completed",
                    "completed_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$service_price"}
                }
            }
        ]
        
        booking_results = list(self.db.bookings.aggregate(booking_pipeline))
        booking_revenue = float(booking_results[0]["total"]) if booking_results else 0.0
        
        # Get POS revenue
        pos_pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "status": "completed",
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$total"}
                }
            }
        ]
        
        pos_results = list(self.db.pos_transactions.aggregate(pos_pipeline))
        pos_revenue = float(pos_results[0]["total"]) if pos_results else 0.0
        
        return booking_revenue + pos_revenue
    
    def calculate_revenue_with_trend(
        self,
        tenant_id: str,
        period: str
    ) -> Dict[str, Any]:
        """
        Calculate revenue with trend comparison
        
        Args:
            tenant_id: Tenant ID
            period: "day", "week", or "month"
            
        Returns:
            Dictionary with total_revenue and revenue_trend
        """
        current_start, current_end, previous_start, previous_end = \
            self.get_comparison_period(period)
        
        current_revenue = self.calculate_revenue(tenant_id, current_start, current_end)
        previous_revenue = self.calculate_revenue(tenant_id, previous_start, previous_end)
        
        trend = self.calculate_trend(current_revenue, previous_revenue) or 0.0
        
        return {
            "total_revenue": round(current_revenue, 2),
            "revenue_trend": trend
        }
    
    def calculate_bookings_with_trend(
        self,
        tenant_id: str,
        period: str
    ) -> Dict[str, Any]:
        """
        Calculate bookings count with trend comparison
        
        Args:
            tenant_id: Tenant ID
            period: "day", "week", or "month"
            
        Returns:
            Dictionary with total_bookings and booking_trend
        """
        current_start, current_end, previous_start, previous_end = \
            self.get_comparison_period(period)
        
        current_bookings = self.db.bookings.count_documents({
            "tenant_id": tenant_id,
            "created_at": {"$gte": current_start, "$lte": current_end}
        })
        
        previous_bookings = self.db.bookings.count_documents({
            "tenant_id": tenant_id,
            "created_at": {"$gte": previous_start, "$lte": previous_end}
        })
        
        trend = self.calculate_trend(current_bookings, previous_bookings) or 0.0
        
        return {
            "total_bookings": current_bookings,
            "booking_trend": trend
        }
    
    def calculate_clients_with_trend(
        self,
        tenant_id: str,
        period: str
    ) -> Dict[str, Any]:
        """
        Calculate client count with trend comparison
        
        Args:
            tenant_id: Tenant ID
            period: "day", "week", or "month"
            
        Returns:
            Dictionary with total_clients, new_clients, and client_trend
        """
        current_start, current_end, previous_start, previous_end = \
            self.get_comparison_period(period)
        
        # Total clients
        total_clients = self.db.clients.count_documents({"tenant_id": tenant_id})
        
        # New clients in current period
        new_clients = self.db.clients.count_documents({
            "tenant_id": tenant_id,
            "created_at": {"$gte": current_start, "$lte": current_end}
        })
        
        # New clients in previous period
        previous_new_clients = self.db.clients.count_documents({
            "tenant_id": tenant_id,
            "created_at": {"$gte": previous_start, "$lte": previous_end}
        })
        
        trend = self.calculate_trend(new_clients, previous_new_clients) or 0.0
        
        return {
            "total_clients": total_clients,
            "new_clients": new_clients,
            "client_trend": trend
        }
    
    def calculate_retention_rate(self, tenant_id: str) -> float:
        """
        Calculate client retention rate
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Retention rate percentage (0-100)
        """
        # Get total clients
        total_clients = self.db.clients.count_documents({"tenant_id": tenant_id})
        
        if total_clients == 0:
            return 0.0
        
        # Get clients with bookings in last 90 days
        ninety_days_ago = datetime.now() - timedelta(days=90)
        
        active_clients = self.db.bookings.distinct(
            "client_id",
            {
                "tenant_id": tenant_id,
                "booking_date": {"$gte": ninety_days_ago}
            }
        )
        
        active_count = len(active_clients)
        retention_rate = (active_count / total_clients) * 100
        
        return round(min(retention_rate, 100.0), 1)
    
    def calculate_returning_client_percentage(self, tenant_id: str) -> float:
        """
        Calculate percentage of clients who have booked more than once
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Percentage of returning clients
        """
        # Get total clients
        total_clients = self.db.clients.count_documents({"tenant_id": tenant_id})
        
        if total_clients == 0:
            return 0.0
        
        # Count clients with more than one booking
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {
                "$group": {
                    "_id": "$client_id",
                    "booking_count": {"$sum": 1}
                }
            },
            {"$match": {"booking_count": {"$gt": 1}}}
        ]
        
        returning_clients = len(list(self.db.bookings.aggregate(pipeline)))
        
        percentage = (returning_clients / total_clients) * 100
        return round(percentage, 1)
    
    def calculate_profit_margin(
        self,
        revenue: float,
        expenses: float
    ) -> Optional[float]:
        """
        Calculate profit margin percentage
        
        Args:
            revenue: Total revenue
            expenses: Total expenses
            
        Returns:
            Profit margin percentage or None if revenue is 0
        """
        if revenue == 0:
            return None
        
        profit = revenue - expenses
        margin = (profit / revenue) * 100
        
        return round(margin, 1)
    
    def calculate_average_booking_value(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Calculate average booking value
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Average booking value
        """
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "status": "completed",
                    "completed_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_value": {"$avg": "$service_price"}
                }
            }
        ]
        
        results = list(self.db.bookings.aggregate(pipeline))
        
        if results and results[0].get("avg_value"):
            return round(float(results[0]["avg_value"]), 2)
        
        return 0.0
    
    def calculate_cancellation_rate(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Calculate cancellation rate
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Cancellation rate percentage
        """
        total_bookings = self.db.bookings.count_documents({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        })
        
        if total_bookings == 0:
            return 0.0
        
        cancelled_bookings = self.db.bookings.count_documents({
            "tenant_id": tenant_id,
            "status": "cancelled",
            "created_at": {"$gte": start_date, "$lte": end_date}
        })
        
        rate = (cancelled_bookings / total_bookings) * 100
        return round(rate, 1)
    
    def calculate_no_show_rate(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Calculate no-show rate
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date
            end_date: End date
            
        Returns:
            No-show rate percentage
        """
        total_bookings = self.db.bookings.count_documents({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        })
        
        if total_bookings == 0:
            return 0.0
        
        no_show_bookings = self.db.bookings.count_documents({
            "tenant_id": tenant_id,
            "status": "no_show",
            "created_at": {"$gte": start_date, "$lte": end_date}
        })
        
        rate = (no_show_bookings / total_bookings) * 100
        return round(rate, 1)
    
    def calculate_online_booking_percentage(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """
        Calculate percentage of online bookings
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Online booking percentage
        """
        total_bookings = self.db.bookings.count_documents({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        })
        
        if total_bookings == 0:
            return 0.0
        
        online_bookings = self.db.bookings.count_documents({
            "tenant_id": tenant_id,
            "booking_source": "online",
            "created_at": {"$gte": start_date, "$lte": end_date}
        })
        
        percentage = (online_bookings / total_bookings) * 100
        return round(percentage, 1)
    
    def calculate_staff_utilization(
        self,
        stylist_id: str,
        tenant_id: str
    ) -> float:
        """
        Calculate staff utilization percentage
        
        Args:
            stylist_id: Stylist ID
            tenant_id: Tenant ID
            
        Returns:
            Utilization percentage
        """
        # Get total available hours (assuming 8 hours per day, 5 days per week)
        # This is a simplified calculation
        total_hours = 40  # hours per week
        
        # Get hours worked this week
        week_start = datetime.now() - timedelta(days=7)
        
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "stylist_id": stylist_id,
                    "status": "completed",
                    "completed_at": {"$gte": week_start}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_duration": {"$sum": "$duration"}
                }
            }
        ]
        
        results = list(self.db.bookings.aggregate(pipeline))
        
        if results and results[0].get("total_duration"):
            hours_worked = results[0]["total_duration"] / 60  # Convert minutes to hours
            utilization = (hours_worked / total_hours) * 100
            return round(min(utilization, 100.0), 1)
        
        return 0.0
