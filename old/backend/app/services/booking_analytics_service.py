from datetime import datetime, timedelta
from typing import Dict, List
from bson import ObjectId
from app.database import Database


class BookingAnalyticsService:
    
    @staticmethod
    def get_booking_stats(tenant_id: str, days: int = 30) -> Dict:
        """Get booking statistics for period"""
        db = Database.get_db()
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date}
        }))
        
        total_bookings = len(bookings)
        completed = len([b for b in bookings if b.get("status") == "completed"])
        cancelled = len([b for b in bookings if b.get("status") == "cancelled"])
        pending = len([b for b in bookings if b.get("status") == "pending"])
        
        total_revenue = sum(b.get("service_price", 0) for b in bookings if b.get("status") == "completed")
        
        return {
            "total_bookings": total_bookings,
            "completed": completed,
            "cancelled": cancelled,
            "pending": pending,
            "total_revenue": total_revenue,
            "average_booking_value": total_revenue / completed if completed > 0 else 0,
            "cancellation_rate": (cancelled / total_bookings * 100) if total_bookings > 0 else 0
        }
    
    @staticmethod
    def get_stylist_performance(tenant_id: str, stylist_id: str, days: int = 30) -> Dict:
        """Get stylist performance metrics"""
        db = Database.get_db()
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "stylist_id": ObjectId(stylist_id),
            "created_at": {"$gte": start_date}
        }))
        
        completed = len([b for b in bookings if b.get("status") == "completed"])
        total_revenue = sum(b.get("service_price", 0) for b in bookings if b.get("status") == "completed")
        
        reviews = list(db.reviews.find({
            "tenant_id": tenant_id,
            "stylist_id": ObjectId(stylist_id),
            "is_approved": True
        }))
        
        avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews) if reviews else 0
        
        return {
            "total_bookings": len(bookings),
            "completed_bookings": completed,
            "total_revenue": total_revenue,
            "average_booking_value": total_revenue / completed if completed > 0 else 0,
            "average_rating": round(avg_rating, 2),
            "total_reviews": len(reviews)
        }
    
    @staticmethod
    def get_service_performance(tenant_id: str, service_id: str, days: int = 30) -> Dict:
        """Get service performance metrics"""
        db = Database.get_db()
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "service_id": ObjectId(service_id),
            "created_at": {"$gte": start_date}
        }))
        
        completed = len([b for b in bookings if b.get("status") == "completed"])
        total_revenue = sum(b.get("service_price", 0) for b in bookings if b.get("status") == "completed")
        
        reviews = list(db.reviews.find({
            "tenant_id": tenant_id,
            "service_id": ObjectId(service_id),
            "is_approved": True
        }))
        
        avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews) if reviews else 0
        
        return {
            "total_bookings": len(bookings),
            "completed_bookings": completed,
            "total_revenue": total_revenue,
            "average_booking_value": total_revenue / completed if completed > 0 else 0,
            "average_rating": round(avg_rating, 2),
            "total_reviews": len(reviews)
        }
    
    @staticmethod
    def get_client_analytics(tenant_id: str, client_id: str) -> Dict:
        """Get client analytics"""
        db = Database.get_db()
        
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        }))
        
        completed = len([b for b in bookings if b.get("status") == "completed"])
        total_spent = sum(b.get("service_price", 0) for b in bookings if b.get("status") == "completed")
        
        first_booking = min((b.get("created_at") for b in bookings), default=None)
        last_booking = max((b.get("created_at") for b in bookings), default=None)
        
        return {
            "total_bookings": len(bookings),
            "completed_bookings": completed,
            "total_spent": total_spent,
            "average_booking_value": total_spent / completed if completed > 0 else 0,
            "first_booking_date": first_booking,
            "last_booking_date": last_booking,
            "customer_lifetime_value": total_spent
        }
    
    @staticmethod
    def get_revenue_by_date(tenant_id: str, days: int = 30) -> List[Dict]:
        """Get daily revenue for period"""
        db = Database.get_db()
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "status": "completed",
                    "created_at": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "revenue": {"$sum": "$service_price"},
                    "bookings": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        return list(db.bookings.aggregate(pipeline))
    
    @staticmethod
    def get_peak_hours(tenant_id: str, days: int = 30) -> List[Dict]:
        """Get peak booking hours"""
        db = Database.get_db()
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "created_at": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$hour": "$booking_date"
                    },
                    "bookings": {"$sum": 1}
                }
            },
            {
                "$sort": {"bookings": -1}
            }
        ]
        
        return list(db.bookings.aggregate(pipeline))
