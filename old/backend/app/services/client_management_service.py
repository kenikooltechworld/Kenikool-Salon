from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
from app.database import Database


class ClientManagementService:
    
    @staticmethod
    def get_client_profile(tenant_id: str, client_id: str) -> Dict:
        """Get comprehensive client profile"""
        db = Database.get_db()
        
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if not client:
            raise ValueError("Client not found")
        
        # Get booking history
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        }).sort("booking_date", -1).limit(10))
        
        # Get loyalty account
        loyalty = db.loyalty_accounts.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        })
        
        # Get reviews
        reviews = list(db.reviews.find({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        }))
        
        return {
            "client": client,
            "bookings": bookings,
            "loyalty": loyalty,
            "reviews": reviews,
            "total_bookings": len(bookings),
            "total_spent": client.get("total_spent", 0),
            "average_rating": sum(r.get("rating", 0) for r in reviews) / len(reviews) if reviews else 0
        }
    
    @staticmethod
    def segment_clients(tenant_id: str, segment_type: str) -> List[Dict]:
        """Segment clients by type"""
        db = Database.get_db()
        
        if segment_type == "vip":
            # Clients with high spending
            clients = list(db.clients.find({
                "tenant_id": tenant_id,
                "total_spent": {"$gte": 5000}
            }))
        elif segment_type == "regular":
            # Clients with moderate spending
            clients = list(db.clients.find({
                "tenant_id": tenant_id,
                "total_spent": {"$gte": 1000, "$lt": 5000}
            }))
        elif segment_type == "new":
            # Clients with few bookings
            clients = list(db.clients.find({
                "tenant_id": tenant_id,
                "total_visits": {"$lte": 3}
            }))
        elif segment_type == "inactive":
            # Clients with no recent bookings
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            clients = list(db.clients.find({
                "tenant_id": tenant_id,
                "last_visit_date": {"$lt": cutoff_date}
            }))
        else:
            clients = []
        
        return clients
    
    @staticmethod
    def get_client_preferences(tenant_id: str, client_id: str) -> Dict:
        """Get client preferences"""
        db = Database.get_db()
        
        # Get most booked services
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id)
        }))
        
        service_counts = {}
        for booking in bookings:
            service_id = str(booking.get("service_id"))
            service_counts[service_id] = service_counts.get(service_id, 0) + 1
        
        # Get most booked stylists
        stylist_counts = {}
        for booking in bookings:
            stylist_id = str(booking.get("stylist_id"))
            stylist_counts[stylist_id] = stylist_counts.get(stylist_id, 0) + 1
        
        return {
            "preferred_services": sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "preferred_stylists": sorted(stylist_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    @staticmethod
    def update_client_notes(tenant_id: str, client_id: str, notes: str) -> Dict:
        """Update client notes"""
        db = Database.get_db()
        
        result = db.clients.update_one(
            {
                "_id": ObjectId(client_id),
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    "notes": notes,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise ValueError("Client not found")
        
        return {"status": "updated"}
    
    @staticmethod
    def get_client_lifetime_value(tenant_id: str, client_id: str) -> Dict:
        """Calculate client lifetime value"""
        db = Database.get_db()
        
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if not client:
            raise ValueError("Client not found")
        
        total_spent = client.get("total_spent", 0)
        total_visits = client.get("total_visits", 0)
        
        avg_transaction = total_spent / total_visits if total_visits > 0 else 0
        
        return {
            "total_spent": total_spent,
            "total_visits": total_visits,
            "average_transaction_value": avg_transaction,
            "lifetime_value": total_spent
        }
