"""
Performance Analytics Service - Enhanced analytics with trends and comparisons
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from bson import ObjectId
from collections import defaultdict
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class PerformanceAnalyticsService:
    """Service for comprehensive performance analytics"""

    @staticmethod
    def get_staff_performance(
        tenant_id: str,
        staff_id: str,
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[str]] = None
    ) -> Dict:
        """Get comprehensive performance data for a staff member"""
        db = Database.get_db()
        
        # Get staff
        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })
        
        if not staff:
            raise NotFoundException("Staff member not found")
        
        # Default metrics
        if not metrics:
            metrics = ["revenue", "bookings", "rating", "rebooking_rate", "avg_service_time", "utilization"]
        
        performance = {
            "staff_id": staff_id,
            "staff_name": staff.get("name"),
            "period_start": start_date,
            "period_end": end_date,
            "metrics": {}
        }
        
        # Get bookings for period
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "stylist_id": staff_id,
            "booking_date": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }))
        
        if "revenue" in metrics:
            total_revenue = sum(b.get("total_price", 0) for b in bookings)
            performance["metrics"]["revenue"] = {
                "total": total_revenue,
                "average_per_booking": total_revenue / len(bookings) if bookings else 0,
                "booking_count": len(bookings)
            }
        
        if "bookings" in metrics:
            performance["metrics"]["bookings"] = {
                "total": len(bookings),
                "by_service": PerformanceAnalyticsService._group_bookings_by_service(bookings)
            }
        
        if "rating" in metrics:
            reviews = list(db.reviews.find({
                "tenant_id": tenant_id,
                "stylist_id": staff_id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }))
            
            if reviews:
                avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews)
                performance["metrics"]["rating"] = {
                    "average": round(avg_rating, 2),
                    "review_count": len(reviews),
                    "distribution": PerformanceAnalyticsService._get_rating_distribution(reviews)
                }
            else:
                performance["metrics"]["rating"] = {
                    "average": 0,
                    "review_count": 0,
                    "distribution": {}
                }
        
        if "rebooking_rate" in metrics:
            rebooking_rate = PerformanceAnalyticsService._calculate_rebooking_rate(
                tenant_id, staff_id, start_date, end_date
            )
            performance["metrics"]["rebooking_rate"] = rebooking_rate
        
        if "avg_service_time" in metrics:
            avg_time = sum(b.get("duration_minutes", 0) for b in bookings) / len(bookings) if bookings else 0
            performance["metrics"]["avg_service_time"] = {
                "minutes": round(avg_time, 2),
                "booking_count": len(bookings)
            }
        
        if "utilization" in metrics:
            utilization = PerformanceAnalyticsService._calculate_utilization(
                tenant_id, staff_id, start_date, end_date
            )
            performance["metrics"]["utilization"] = utilization
        
        return performance

    @staticmethod
    def get_performance_trends(
        tenant_id: str,
        staff_id: str,
        metric: str,
        period: str = "daily",
        days: int = 30
    ) -> Dict:
        """Get performance trends over time"""
        db = Database.get_db()
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get bookings
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "stylist_id": staff_id,
            "booking_date": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }))
        
        trends = {
            "staff_id": staff_id,
            "metric": metric,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "data_points": []
        }
        
        if period == "daily":
            trends["data_points"] = PerformanceAnalyticsService._aggregate_by_day(
                bookings, metric, start_date, end_date
            )
        elif period == "weekly":
            trends["data_points"] = PerformanceAnalyticsService._aggregate_by_week(
                bookings, metric, start_date, end_date
            )
        elif period == "monthly":
            trends["data_points"] = PerformanceAnalyticsService._aggregate_by_month(
                bookings, metric, start_date, end_date
            )
        
        return trends

    @staticmethod
    def compare_staff_performance(
        tenant_id: str,
        staff_ids: List[str],
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[str]] = None
    ) -> Dict:
        """Compare performance metrics between staff members"""
        db = Database.get_db()
        
        if not metrics:
            metrics = ["revenue", "bookings", "rating", "utilization"]
        
        comparison = {
            "period_start": start_date,
            "period_end": end_date,
            "metrics": metrics,
            "staff_comparison": []
        }
        
        for staff_id in staff_ids:
            perf = PerformanceAnalyticsService.get_staff_performance(
                tenant_id, staff_id, start_date, end_date, metrics
            )
            comparison["staff_comparison"].append(perf)
        
        # Calculate rankings
        for metric in metrics:
            staff_with_metric = [
                s for s in comparison["staff_comparison"]
                if metric in s["metrics"]
            ]
            
            if metric == "revenue":
                staff_with_metric.sort(
                    key=lambda x: x["metrics"][metric].get("total", 0),
                    reverse=True
                )
            elif metric == "rating":
                staff_with_metric.sort(
                    key=lambda x: x["metrics"][metric].get("average", 0),
                    reverse=True
                )
            elif metric == "bookings":
                staff_with_metric.sort(
                    key=lambda x: x["metrics"][metric].get("total", 0),
                    reverse=True
                )
            elif metric == "utilization":
                staff_with_metric.sort(
                    key=lambda x: x["metrics"][metric].get("percentage", 0),
                    reverse=True
                )
            
            # Add rankings
            for rank, staff_perf in enumerate(staff_with_metric, 1):
                if "rankings" not in staff_perf:
                    staff_perf["rankings"] = {}
                staff_perf["rankings"][metric] = rank
        
        return comparison

    @staticmethod
    def set_performance_goal(
        tenant_id: str,
        staff_id: str,
        goal_type: str,
        target_value: float,
        period_start: datetime,
        period_end: datetime,
        created_by: str,
        notes: Optional[str] = None
    ) -> Dict:
        """Set a performance goal for a staff member"""
        db = Database.get_db()
        
        goal = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "goal_type": goal_type,
            "target_value": target_value,
            "current_value": 0,
            "period_start": period_start,
            "period_end": period_end,
            "status": "active",
            "achieved_at": None,
            "notes": notes,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.performance_goals.insert_one(goal)
        goal["_id"] = result.inserted_id
        return goal

    @staticmethod
    def update_goal_progress(
        tenant_id: str,
        goal_id: str,
        current_value: float
    ) -> Dict:
        """Update progress on a performance goal"""
        db = Database.get_db()
        
        goal = db.performance_goals.find_one({
            "_id": ObjectId(goal_id),
            "tenant_id": tenant_id
        })
        
        if not goal:
            raise NotFoundException("Performance goal not found")
        
        # Check if goal is achieved
        status = "active"
        achieved_at = None
        
        if current_value >= goal["target_value"]:
            status = "achieved"
            achieved_at = datetime.utcnow()
        
        db.performance_goals.update_one(
            {"_id": ObjectId(goal_id)},
            {
                "$set": {
                    "current_value": current_value,
                    "status": status,
                    "achieved_at": achieved_at,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return db.performance_goals.find_one({"_id": ObjectId(goal_id)})

    @staticmethod
    def get_performance_goals(
        tenant_id: str,
        staff_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get performance goals"""
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        if staff_id:
            query["staff_id"] = staff_id
        if status:
            query["status"] = status
        
        goals = list(db.performance_goals.find(query).sort("created_at", -1))
        return goals

    @staticmethod
    def generate_performance_report(
        tenant_id: str,
        staff_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Generate comprehensive performance report"""
        db = Database.get_db()
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        report = {
            "tenant_id": tenant_id,
            "period_start": start_date,
            "period_end": end_date,
            "generated_at": datetime.utcnow(),
            "staff_reports": []
        }
        
        # Get staff
        query = {"tenant_id": tenant_id, "is_active": True}
        if staff_id:
            query["_id"] = ObjectId(staff_id)
        
        staff_list = list(db.stylists.find(query))
        
        for staff in staff_list:
            staff_id_str = str(staff["_id"])
            perf = PerformanceAnalyticsService.get_staff_performance(
                tenant_id, staff_id_str, start_date, end_date
            )
            report["staff_reports"].append(perf)
        
        # Calculate summary statistics
        report["summary"] = PerformanceAnalyticsService._calculate_summary_stats(
            report["staff_reports"]
        )
        
        return report

    # Helper methods
    @staticmethod
    def _group_bookings_by_service(bookings: List[Dict]) -> Dict:
        """Group bookings by service"""
        grouped = defaultdict(int)
        for booking in bookings:
            service_id = booking.get("service_id", "unknown")
            grouped[service_id] += 1
        return dict(grouped)

    @staticmethod
    def _get_rating_distribution(reviews: List[Dict]) -> Dict:
        """Get distribution of ratings"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating = review.get("rating", 0)
            if rating in distribution:
                distribution[rating] += 1
        return distribution

    @staticmethod
    def _calculate_rebooking_rate(
        tenant_id: str,
        staff_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Calculate rebooking rate"""
        db = Database.get_db()
        
        # Get all bookings in period
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "stylist_id": staff_id,
            "booking_date": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }))
        
        if not bookings:
            return {"rate": 0, "rebooking_count": 0, "total_bookings": 0}
        
        # Get unique clients
        client_ids = set(b.get("client_id") for b in bookings if b.get("client_id"))
        
        # Count how many clients have multiple bookings
        rebooking_count = 0
        for client_id in client_ids:
            client_bookings = [b for b in bookings if b.get("client_id") == client_id]
            if len(client_bookings) > 1:
                rebooking_count += 1
        
        rate = (rebooking_count / len(client_ids) * 100) if client_ids else 0
        
        return {
            "rate": round(rate, 2),
            "rebooking_count": rebooking_count,
            "total_unique_clients": len(client_ids),
            "total_bookings": len(bookings)
        }

    @staticmethod
    def _calculate_utilization(
        tenant_id: str,
        staff_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Calculate staff utilization percentage"""
        db = Database.get_db()
        
        # Get bookings
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "stylist_id": staff_id,
            "booking_date": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }))
        
        # Get staff schedule
        staff = db.stylists.find_one({"_id": ObjectId(staff_id)})
        schedule = staff.get("schedule", {}) if staff else {}
        
        # Calculate available hours
        available_hours = PerformanceAnalyticsService._calculate_available_hours(
            schedule, start_date, end_date
        )
        
        # Calculate booked hours
        booked_hours = sum(b.get("duration_minutes", 0) for b in bookings) / 60
        
        utilization = (booked_hours / available_hours * 100) if available_hours > 0 else 0
        
        return {
            "percentage": round(utilization, 2),
            "booked_hours": round(booked_hours, 2),
            "available_hours": round(available_hours, 2),
            "idle_hours": round(available_hours - booked_hours, 2)
        }

    @staticmethod
    def _calculate_available_hours(
        schedule: Dict,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Calculate total available hours from schedule"""
        total_hours = 0
        current_date = start_date
        
        while current_date <= end_date:
            day_name = current_date.strftime("%A").lower()
            day_schedule = schedule.get(day_name, [])
            
            for slot in day_schedule:
                start_time = slot.get("start", "")
                end_time = slot.get("end", "")
                
                if start_time and end_time:
                    try:
                        start_hour = int(start_time.split(":")[0])
                        end_hour = int(end_time.split(":")[0])
                        total_hours += (end_hour - start_hour)
                    except:
                        pass
            
            current_date += timedelta(days=1)
        
        return total_hours

    @staticmethod
    def _aggregate_by_day(
        bookings: List[Dict],
        metric: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Aggregate metrics by day"""
        daily_data = defaultdict(lambda: {"revenue": 0, "bookings": 0})
        
        for booking in bookings:
            date_key = booking.get("booking_date", datetime.utcnow()).date()
            daily_data[date_key]["bookings"] += 1
            daily_data[date_key]["revenue"] += booking.get("total_price", 0)
        
        result = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            result.append({
                "date": current_date,
                "value": daily_data[current_date].get(metric, 0)
            })
            current_date += timedelta(days=1)
        
        return result

    @staticmethod
    def _aggregate_by_week(
        bookings: List[Dict],
        metric: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Aggregate metrics by week"""
        weekly_data = defaultdict(lambda: {"revenue": 0, "bookings": 0})
        
        for booking in bookings:
            date = booking.get("booking_date", datetime.utcnow())
            week_key = date.isocalendar()[1]
            weekly_data[week_key]["bookings"] += 1
            weekly_data[week_key]["revenue"] += booking.get("total_price", 0)
        
        result = []
        for week_num in sorted(weekly_data.keys()):
            result.append({
                "week": week_num,
                "value": weekly_data[week_num].get(metric, 0)
            })
        
        return result

    @staticmethod
    def _aggregate_by_month(
        bookings: List[Dict],
        metric: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Aggregate metrics by month"""
        monthly_data = defaultdict(lambda: {"revenue": 0, "bookings": 0})
        
        for booking in bookings:
            date = booking.get("booking_date", datetime.utcnow())
            month_key = date.strftime("%Y-%m")
            monthly_data[month_key]["bookings"] += 1
            monthly_data[month_key]["revenue"] += booking.get("total_price", 0)
        
        result = []
        for month in sorted(monthly_data.keys()):
            result.append({
                "month": month,
                "value": monthly_data[month].get(metric, 0)
            })
        
        return result

    @staticmethod
    def _calculate_summary_stats(staff_reports: List[Dict]) -> Dict:
        """Calculate summary statistics across all staff"""
        if not staff_reports:
            return {}
        
        total_revenue = sum(
            s.get("metrics", {}).get("revenue", {}).get("total", 0)
            for s in staff_reports
        )
        total_bookings = sum(
            s.get("metrics", {}).get("bookings", {}).get("total", 0)
            for s in staff_reports
        )
        avg_rating = sum(
            s.get("metrics", {}).get("rating", {}).get("average", 0)
            for s in staff_reports
        ) / len(staff_reports) if staff_reports else 0
        
        return {
            "total_revenue": total_revenue,
            "total_bookings": total_bookings,
            "average_rating": round(avg_rating, 2),
            "staff_count": len(staff_reports),
            "average_revenue_per_staff": round(total_revenue / len(staff_reports), 2) if staff_reports else 0
        }


# Singleton instance
performance_analytics_service = PerformanceAnalyticsService()
