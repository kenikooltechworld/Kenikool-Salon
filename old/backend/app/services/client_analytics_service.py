"""
Client Analytics Service - Business logic for client analytics
"""
from bson import ObjectId
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional
import logging
from statistics import mean

from app.database import Database
from app.api.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class ClientAnalyticsService:
    """Client analytics service for calculating and retrieving client metrics"""
    
    @staticmethod
    def calculate_client_metrics(client_id: str, tenant_id: str) -> Dict:
        """
        Calculate comprehensive analytics metrics for a client
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            
        Returns:
            Dict with calculated analytics
        """
        db = Database.get_db()
        
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if not client:
            raise NotFoundException("Client not found")
        
        # Get all completed bookings for this client
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "client_id": client_id,
            "status": "completed"
        }).sort("booking_date", 1))
        
        # Get all payments for this client
        payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "booking_id": {"$in": [str(b["_id"]) for b in bookings]},
            "status": "completed"
        }))
        
        # Calculate visit metrics
        total_visits = len(bookings)
        first_visit_date = bookings[0]["booking_date"] if bookings else None
        last_visit_date = bookings[-1]["booking_date"] if bookings else None
        
        # Calculate average days between visits
        average_days_between_visits = None
        if len(bookings) >= 2:
            visit_gaps = []
            for i in range(1, len(bookings)):
                gap = (bookings[i]["booking_date"] - bookings[i-1]["booking_date"]).days
                visit_gaps.append(gap)
            average_days_between_visits = mean(visit_gaps) if visit_gaps else None
        
        # Predict next visit
        predicted_next_visit = None
        if last_visit_date and average_days_between_visits:
            predicted_next_visit = last_visit_date + timedelta(days=int(average_days_between_visits))
        
        # Calculate financial metrics
        total_spent = sum(p.get("amount", 0) for p in payments)
        average_transaction_value = total_spent / total_visits if total_visits > 0 else 0
        lifetime_value = total_spent  # Can be enhanced with predictive modeling
        
        # Calculate engagement metrics
        all_bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "client_id": client_id
        }))
        
        no_show_count = sum(1 for b in all_bookings if b.get("status") == "no_show")
        cancellation_count = sum(1 for b in all_bookings if b.get("status") == "cancelled")
        total_bookings = len(all_bookings)
        
        attendance_rate = 100.0
        if total_bookings > 0:
            attended = total_bookings - no_show_count - cancellation_count
            attendance_rate = (attended / total_bookings) * 100
        
        # Calculate retention metrics
        days_since_last_visit = 0
        is_at_risk = False
        churn_risk_score = 0.0
        
        if last_visit_date:
            days_since_last_visit = (datetime.utcnow() - last_visit_date).days
            
            # Simple churn risk calculation
            if average_days_between_visits:
                expected_return = average_days_between_visits * 1.5  # 50% buffer
                if days_since_last_visit > expected_return:
                    is_at_risk = True
                    # Calculate risk score (0-1)
                    churn_risk_score = min(1.0, days_since_last_visit / (expected_return * 2))
            else:
                # For clients with only one visit
                if days_since_last_visit > 90:  # 90 days threshold
                    is_at_risk = True
                    churn_risk_score = min(1.0, days_since_last_visit / 180)
        
        # Calculate service preferences
        service_counts = {}
        stylist_counts = {}
        
        for booking in bookings:
            service_id = booking.get("service_id")
            stylist_id = booking.get("stylist_id")
            
            if service_id:
                service_counts[service_id] = service_counts.get(service_id, 0) + 1
            if stylist_id:
                stylist_counts[stylist_id] = stylist_counts.get(stylist_id, 0) + 1
        
        # Get top 3 favorite services and stylists
        favorite_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        favorite_services = [s[0] for s in favorite_services]
        
        favorite_stylists = sorted(stylist_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        favorite_stylists = [s[0] for s in favorite_stylists]
        
        # Prepare analytics data
        analytics_data = {
            "client_id": client_id,
            "tenant_id": tenant_id,
            "total_visits": total_visits,
            "first_visit_date": first_visit_date,
            "last_visit_date": last_visit_date,
            "average_days_between_visits": average_days_between_visits,
            "predicted_next_visit": predicted_next_visit if predicted_next_visit else None,
            "total_spent": float(total_spent),
            "average_transaction_value": float(average_transaction_value),
            "lifetime_value": float(lifetime_value),
            "no_show_count": no_show_count,
            "cancellation_count": cancellation_count,
            "attendance_rate": float(attendance_rate),
            "is_at_risk": is_at_risk,
            "churn_risk_score": float(churn_risk_score),
            "days_since_last_visit": days_since_last_visit,
            "favorite_services": favorite_services,
            "favorite_stylists": favorite_stylists,
            "calculated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Upsert analytics data
        db.client_analytics.update_one(
            {"tenant_id": tenant_id, "client_id": client_id},
            {"$set": analytics_data},
            upsert=True
        )
        
        # Update client document with computed fields
        db.clients.update_one(
            {"_id": ObjectId(client_id)},
            {
                "$set": {
                    "total_visits": total_visits,
                    "total_spent": float(total_spent),
                    "last_visit_date": last_visit_date,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Analytics calculated for client: {client_id}")
        
        return analytics_data
    
    @staticmethod
    def get_client_analytics(client_id: str, tenant_id: str) -> Dict:
        """
        Get analytics for a specific client
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            
        Returns:
            Dict with client analytics
        """
        db = Database.get_db()
        
        # Check if analytics exist
        analytics = db.client_analytics.find_one({
            "tenant_id": tenant_id,
            "client_id": client_id
        })
        
        if not analytics:
            # Calculate analytics if they don't exist
            logger.info(f"Analytics not found for client {client_id}, calculating...")
            analytics = ClientAnalyticsService.calculate_client_metrics(client_id, tenant_id)
            analytics = db.client_analytics.find_one({
                "tenant_id": tenant_id,
                "client_id": client_id
            })
        
        # Format response
        return ClientAnalyticsService._format_analytics_response(analytics)
    
    @staticmethod
    def get_global_analytics(tenant_id: str) -> Dict:
        """
        Get global analytics for all clients in a tenant
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Dict with global analytics
        """
        db = Database.get_db()
        
        # Get all clients
        total_clients = db.clients.count_documents({"tenant_id": tenant_id})
        
        # Get clients with recent activity (last 90 days)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        active_clients = db.clients.count_documents({
            "tenant_id": tenant_id,
            "last_visit_date": {"$gte": ninety_days_ago}
        })
        
        # Get at-risk clients
        at_risk_clients = db.client_analytics.count_documents({
            "tenant_id": tenant_id,
            "is_at_risk": True
        })
        
        # Get new clients this month
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_clients_this_month = db.clients.count_documents({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_of_month}
        })
        
        # Calculate average metrics
        analytics_pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {"$group": {
                "_id": None,
                "avg_lifetime_value": {"$avg": "$lifetime_value"},
                "avg_visit_frequency": {"$avg": "$average_days_between_visits"},
                "total_revenue": {"$sum": "$total_spent"}
            }}
        ]
        
        avg_metrics = list(db.client_analytics.aggregate(analytics_pipeline))
        
        average_lifetime_value = 0.0
        average_visit_frequency = 0.0
        total_revenue = 0.0
        
        if avg_metrics:
            average_lifetime_value = avg_metrics[0].get("avg_lifetime_value", 0.0) or 0.0
            average_visit_frequency = avg_metrics[0].get("avg_visit_frequency", 0.0) or 0.0
            total_revenue = avg_metrics[0].get("total_revenue", 0.0) or 0.0
        
        # Get segment distribution
        segment_pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {"$group": {
                "_id": "$segment",
                "count": {"$sum": 1}
            }}
        ]
        
        segment_results = list(db.clients.aggregate(segment_pipeline))
        segment_distribution = {s["_id"]: s["count"] for s in segment_results}
        
        return {
            "totalClients": total_clients,
            "activeClients": active_clients,
            "atRiskClients": at_risk_clients,
            "newClientsThisMonth": new_clients_this_month,
            "averageLifetimeValue": float(average_lifetime_value),
            "averageVisitFrequency": float(average_visit_frequency),
            "totalRevenue": float(total_revenue),
            "segmentDistribution": segment_distribution
        }
    
    @staticmethod
    def predict_next_visit(client_id: str, tenant_id: str) -> Optional[date]:
        """
        Predict the next visit date for a client
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            
        Returns:
            Predicted next visit date or None
        """
        analytics = ClientAnalyticsService.get_client_analytics(client_id, tenant_id)
        return analytics.get("predictedNextVisit")
    
    @staticmethod
    def _format_analytics_response(analytics_doc: Dict) -> Dict:
        """Format analytics document for response"""
        if not analytics_doc:
            return {}
        
        return {
            "id": str(analytics_doc["_id"]),
            "clientId": analytics_doc["client_id"],
            "tenantId": analytics_doc["tenant_id"],
            "totalVisits": analytics_doc.get("total_visits", 0),
            "firstVisitDate": analytics_doc.get("first_visit_date"),
            "lastVisitDate": analytics_doc.get("last_visit_date"),
            "averageDaysBetweenVisits": analytics_doc.get("average_days_between_visits"),
            "predictedNextVisit": analytics_doc.get("predicted_next_visit"),
            "totalSpent": analytics_doc.get("total_spent", 0.0),
            "averageTransactionValue": analytics_doc.get("average_transaction_value", 0.0),
            "lifetimeValue": analytics_doc.get("lifetime_value", 0.0),
            "noShowCount": analytics_doc.get("no_show_count", 0),
            "cancellationCount": analytics_doc.get("cancellation_count", 0),
            "attendanceRate": analytics_doc.get("attendance_rate", 100.0),
            "isAtRisk": analytics_doc.get("is_at_risk", False),
            "churnRiskScore": analytics_doc.get("churn_risk_score", 0.0),
            "daysSinceLastVisit": analytics_doc.get("days_since_last_visit", 0),
            "favoriteServices": analytics_doc.get("favorite_services", []),
            "favoriteStylists": analytics_doc.get("favorite_stylists", []),
            "calculatedAt": analytics_doc.get("calculated_at"),
            "updatedAt": analytics_doc.get("updated_at")
        }


# Singleton instance
client_analytics_service = ClientAnalyticsService()
