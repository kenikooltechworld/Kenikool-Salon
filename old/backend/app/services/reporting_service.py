from datetime import datetime, timedelta
from typing import Dict, List
from bson import ObjectId
from app.database import Database


class ReportingService:
    
    @staticmethod
    def get_dashboard_summary(tenant_id: str) -> Dict:
        """Get dashboard summary"""
        db = Database.get_db()
        
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Today's bookings
        today_bookings = db.bookings.count_documents({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": today}
        })
        
        # This week's revenue
        week_revenue = sum(b.get("service_price", 0) for b in db.bookings.find({
            "tenant_id": tenant_id,
            "status": "completed",
            "booking_date": {"$gte": week_ago}
        }))
        
        # This month's bookings
        month_bookings = db.bookings.count_documents({
            "tenant_id": tenant_id,
            "booking_date": {"$gte": month_ago}
        })
        
        # New clients this month
        new_clients = db.clients.count_documents({
            "tenant_id": tenant_id,
            "created_at": {"$gte": month_ago}
        })
        
        return {
            "today_bookings": today_bookings,
            "week_revenue": week_revenue,
            "month_bookings": month_bookings,
            "new_clients": new_clients
        }
    
    @staticmethod
    def get_revenue_report(tenant_id: str, days: int = 30) -> Dict:
        """Get revenue report"""
        db = Database.get_db()
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "status": "completed",
                    "booking_date": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$booking_date"
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
        
        daily_revenue = list(db.bookings.aggregate(pipeline))
        total_revenue = sum(d["revenue"] for d in daily_revenue)
        
        return {
            "total_revenue": total_revenue,
            "daily_revenue": daily_revenue,
            "average_daily_revenue": total_revenue / len(daily_revenue) if daily_revenue else 0
        }
    
    @staticmethod
    def get_service_report(tenant_id: str) -> List[Dict]:
        """Get service performance report"""
        db = Database.get_db()
        
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "status": "completed"
                }
            },
            {
                "$group": {
                    "_id": "$service_id",
                    "bookings": {"$sum": 1},
                    "revenue": {"$sum": "$service_price"}
                }
            },
            {
                "$sort": {"revenue": -1}
            }
        ]
        
        services = list(db.bookings.aggregate(pipeline))
        
        # Enrich with service names
        for service in services:
            service_doc = db.services.find_one({"_id": service["_id"]})
            service["service_name"] = service_doc.get("name") if service_doc else "Unknown"
        
        return services
    
    @staticmethod
    def get_stylist_report(tenant_id: str) -> List[Dict]:
        """Get stylist performance report"""
        db = Database.get_db()
        
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "status": "completed"
                }
            },
            {
                "$group": {
                    "_id": "$stylist_id",
                    "bookings": {"$sum": 1},
                    "revenue": {"$sum": "$service_price"}
                }
            },
            {
                "$sort": {"revenue": -1}
            }
        ]
        
        stylists = list(db.bookings.aggregate(pipeline))
        
        # Enrich with stylist names and ratings
        for stylist in stylists:
            stylist_doc = db.stylists.find_one({"_id": stylist["_id"]})
            stylist["stylist_name"] = stylist_doc.get("name") if stylist_doc else "Unknown"
            stylist["rating"] = stylist_doc.get("average_rating", 0) if stylist_doc else 0
        
        return stylists
    
    @staticmethod
    def get_client_report(tenant_id: str) -> Dict:
        """Get client analytics report"""
        db = Database.get_db()
        
        total_clients = db.clients.count_documents({"tenant_id": tenant_id})
        
        # Clients by spending
        high_value = db.clients.count_documents({
            "tenant_id": tenant_id,
            "total_spent": {"$gte": 5000}
        })
        
        medium_value = db.clients.count_documents({
            "tenant_id": tenant_id,
            "total_spent": {"$gte": 1000, "$lt": 5000}
        })
        
        low_value = db.clients.count_documents({
            "tenant_id": tenant_id,
            "total_spent": {"$lt": 1000}
        })
        
        # Average metrics
        clients = list(db.clients.find({"tenant_id": tenant_id}))
        avg_spent = sum(c.get("total_spent", 0) for c in clients) / total_clients if total_clients > 0 else 0
        avg_visits = sum(c.get("total_visits", 0) for c in clients) / total_clients if total_clients > 0 else 0
        
        return {
            "total_clients": total_clients,
            "high_value_clients": high_value,
            "medium_value_clients": medium_value,
            "low_value_clients": low_value,
            "average_spent_per_client": avg_spent,
            "average_visits_per_client": avg_visits
        }
