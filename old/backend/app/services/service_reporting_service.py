"""
Service reporting service - Generate performance reports for services
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from collections import defaultdict

from app.database import Database

logger = logging.getLogger(__name__)


class ServiceReportingService:
    """Service for generating service performance reports"""
    
    @staticmethod
    def generate_performance_report(
        service_id: str,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Generate comprehensive performance report for a service
        
        Args:
            service_id: Service ID
            tenant_id: Tenant ID
            start_date: Report start date (default: 30 days ago)
            end_date: Report end date (default: now)
            
        Returns:
            Dict with comprehensive performance metrics
        """
        db = Database.get_db()
        
        # Default date range: last 30 days
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get service
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            return {}
        
        # Get bookings in date range
        bookings = list(db.bookings.find({
            "service_id": service_id,
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        # Calculate metrics
        total_bookings = len(bookings)
        completed_bookings = [b for b in bookings if b.get("status") == "completed"]
        cancelled_bookings = [b for b in bookings if b.get("status") == "cancelled"]
        
        total_revenue = sum(b.get("total_price", 0) for b in completed_bookings)
        
        # Calculate profit (revenue - costs)
        # Assuming 30% cost for resources/overhead
        estimated_costs = total_revenue * 0.3
        profit = total_revenue - estimated_costs
        
        # Calculate utilization rate
        # Total possible slots vs actual bookings
        days_in_period = (end_date - start_date).days
        max_daily_bookings = service.get("max_concurrent_bookings", 10)
        if max_daily_bookings == 0:
            max_daily_bookings = 10  # Default
        
        total_possible_bookings = days_in_period * max_daily_bookings
        utilization_rate = (total_bookings / total_possible_bookings * 100) if total_possible_bookings > 0 else 0
        
        # Calculate profitability per booking
        profit_per_booking = profit / len(completed_bookings) if completed_bookings else 0
        
        # Calculate growth rate (compare to previous period)
        previous_start = start_date - (end_date - start_date)
        previous_bookings = list(db.bookings.find({
            "service_id": service_id,
            "tenant_id": tenant_id,
            "created_at": {"$gte": previous_start, "$lt": start_date}
        }))
        
        previous_revenue = sum(
            b.get("total_price", 0) 
            for b in previous_bookings 
            if b.get("status") == "completed"
        )
        
        revenue_growth = 0
        if previous_revenue > 0:
            revenue_growth = ((total_revenue - previous_revenue) / previous_revenue) * 100
        
        booking_growth = 0
        if len(previous_bookings) > 0:
            booking_growth = ((total_bookings - len(previous_bookings)) / len(previous_bookings)) * 100
        
        # Get top stylists
        stylist_performance = defaultdict(lambda: {"bookings": 0, "revenue": 0})
        for booking in completed_bookings:
            stylist_id = booking.get("stylist_id")
            if stylist_id:
                stylist_performance[stylist_id]["bookings"] += 1
                stylist_performance[stylist_id]["revenue"] += booking.get("total_price", 0)
        
        top_stylists = sorted(
            [
                {
                    "stylist_id": sid,
                    "bookings": data["bookings"],
                    "revenue": data["revenue"]
                }
                for sid, data in stylist_performance.items()
            ],
            key=lambda x: x["revenue"],
            reverse=True
        )[:5]
        
        # Get reviews
        reviews = list(db.reviews.find({
            "service_id": service_id,
            "tenant_id": tenant_id,
            "is_approved": True
        }))
        
        average_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews) if reviews else 0
        
        # Revenue by day
        revenue_by_day = defaultdict(float)
        for booking in completed_bookings:
            day = booking.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d")
            revenue_by_day[day] += booking.get("total_price", 0)
        
        revenue_trend = [
            {"date": date, "revenue": revenue}
            for date, revenue in sorted(revenue_by_day.items())
        ]
        
        return {
            "service_id": service_id,
            "service_name": service.get("name"),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days_in_period
            },
            "summary": {
                "total_bookings": total_bookings,
                "completed_bookings": len(completed_bookings),
                "cancelled_bookings": len(cancelled_bookings),
                "cancellation_rate": (len(cancelled_bookings) / total_bookings * 100) if total_bookings > 0 else 0,
                "total_revenue": total_revenue,
                "estimated_costs": estimated_costs,
                "profit": profit,
                "profit_margin": (profit / total_revenue * 100) if total_revenue > 0 else 0
            },
            "performance": {
                "utilization_rate": round(utilization_rate, 2),
                "profit_per_booking": round(profit_per_booking, 2),
                "average_rating": round(average_rating, 2),
                "total_reviews": len(reviews)
            },
            "growth": {
                "revenue_growth": round(revenue_growth, 2),
                "booking_growth": round(booking_growth, 2)
            },
            "top_stylists": top_stylists,
            "revenue_trend": revenue_trend,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def generate_multi_service_report(
        tenant_id: str,
        service_ids: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Generate comparative report for multiple services
        
        Args:
            tenant_id: Tenant ID
            service_ids: List of service IDs (None = all services)
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Dict with comparative metrics
        """
        db = Database.get_db()
        
        # Default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get services
        query = {"tenant_id": tenant_id, "is_active": True}
        if service_ids:
            query["_id"] = {"$in": [ObjectId(sid) for sid in service_ids]}
        
        services = list(db.services.find(query))
        
        # Generate report for each service
        service_reports = []
        for service in services:
            service_id = str(service["_id"])
            report = ServiceReportingService.generate_performance_report(
                service_id, tenant_id, start_date, end_date
            )
            if report:
                service_reports.append(report)
        
        # Calculate totals
        total_revenue = sum(r["summary"]["total_revenue"] for r in service_reports)
        total_bookings = sum(r["summary"]["total_bookings"] for r in service_reports)
        total_profit = sum(r["summary"]["profit"] for r in service_reports)
        
        # Rank services
        ranked_by_revenue = sorted(
            service_reports,
            key=lambda x: x["summary"]["total_revenue"],
            reverse=True
        )
        
        ranked_by_bookings = sorted(
            service_reports,
            key=lambda x: x["summary"]["total_bookings"],
            reverse=True
        )
        
        ranked_by_profit = sorted(
            service_reports,
            key=lambda x: x["summary"]["profit"],
            reverse=True
        )
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "summary": {
                "total_services": len(service_reports),
                "total_revenue": total_revenue,
                "total_bookings": total_bookings,
                "total_profit": total_profit,
                "average_revenue_per_service": total_revenue / len(service_reports) if service_reports else 0
            },
            "rankings": {
                "by_revenue": [
                    {
                        "service_id": r["service_id"],
                        "service_name": r["service_name"],
                        "revenue": r["summary"]["total_revenue"]
                    }
                    for r in ranked_by_revenue[:10]
                ],
                "by_bookings": [
                    {
                        "service_id": r["service_id"],
                        "service_name": r["service_name"],
                        "bookings": r["summary"]["total_bookings"]
                    }
                    for r in ranked_by_bookings[:10]
                ],
                "by_profit": [
                    {
                        "service_id": r["service_id"],
                        "service_name": r["service_name"],
                        "profit": r["summary"]["profit"]
                    }
                    for r in ranked_by_profit[:10]
                ]
            },
            "service_reports": service_reports,
            "generated_at": datetime.utcnow().isoformat()
        }


# Singleton instance
service_reporting_service = ServiceReportingService()
