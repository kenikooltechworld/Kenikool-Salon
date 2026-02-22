"""
Directory service for salon discovery and search
"""
from datetime import datetime
from typing import Optional, List, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


class DirectoryService:
    """Service for managing salon directory and discovery"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.tenants = db.tenants
        self.services = db.services
        self.reviews = db.reviews
    
    async def get_salon_listings(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_rating: Optional[float] = None,
        location: Optional[Dict] = None,
        max_distance_km: float = 10.0,
        limit: int = 20
    ) -> List[Dict]:
        """Get salon listings with filters"""
        search_query = {"is_active": True}
        
        if query:
            search_query["salon_name"] = {"$regex": query, "$options": "i"}
        
        if location:
            search_query["location"] = {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [location["longitude"], location["latitude"]]
                    },
                    "$maxDistance": max_distance_km * 1000
                }
            }
        
        tenants = await self.tenants.find(search_query).limit(limit).to_list(length=None)
        
        listings = []
        for tenant in tenants:
            tenant_id = str(tenant["_id"])
            
            services_count = await self.services.count_documents({
                "tenant_id": tenant_id,
                "is_active": True
            })
            
            if category:
                services_count = await self.services.count_documents({
                    "tenant_id": tenant_id,
                    "is_active": True,
                    "category": category
                })
                
                if services_count == 0:
                    continue
            
            rating_pipeline = [
                {
                    "$match": {
                        "tenant_id": tenant_id,
                        "is_approved": True
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "avg_rating": {"$avg": "$rating"},
                        "total_reviews": {"$sum": 1}
                    }
                }
            ]
            
            rating_result = await self.reviews.aggregate(rating_pipeline).to_list(length=1)
            
            avg_rating = 0
            total_reviews = 0
            if rating_result:
                avg_rating = rating_result[0].get("avg_rating", 0)
                total_reviews = rating_result[0].get("total_reviews", 0)
            
            if min_rating and avg_rating < min_rating:
                continue
            
            distance_km = None
            if location and tenant.get("location"):
                distance_km = self._calculate_distance(
                    location["latitude"],
                    location["longitude"],
                    tenant["location"]["coordinates"][1],
                    tenant["location"]["coordinates"][0]
                )
            
            listings.append({
                "id": tenant_id,
                "salon_name": tenant["salon_name"],
                "subdomain": tenant["subdomain"],
                "address": tenant.get("address"),
                "logo_url": tenant.get("logo_url"),
                "brand_color": tenant.get("brand_color", "#6366f1"),
                "services_count": services_count,
                "avg_rating": round(avg_rating, 1),
                "total_reviews": total_reviews,
                "distance_km": distance_km
            })
        
        if not location:
            listings.sort(key=lambda x: x["avg_rating"], reverse=True)
        
        return listings
    
    async def get_salon_details(self, tenant_id: str) -> Optional[Dict]:
        """Get detailed salon information"""
        tenant = await self.tenants.find_one({
            "_id": ObjectId(tenant_id),
            "is_active": True
        })
        
        if not tenant:
            return None
        
        services = await self.services.find({
            "tenant_id": tenant_id,
            "is_active": True
        }).to_list(length=None)
        
        services_list = [
            {
                "id": str(s["_id"]),
                "name": s["name"],
                "description": s.get("description"),
                "price": s["price"],
                "duration_minutes": s["duration_minutes"],
                "category": s.get("category"),
                "photo_url": s.get("photo_url")
            }
            for s in services
        ]
        
        recent_reviews = await self.reviews.find({
            "tenant_id": tenant_id,
            "is_approved": True
        }).sort("created_at", -1).limit(10).to_list(length=10)
        
        reviews_list = [
            {
                "id": str(r["_id"]),
                "client_name": r["client_name"],
                "rating": r["rating"],
                "comment": r.get("comment"),
                "service_name": r["service_name"],
                "created_at": r["created_at"]
            }
            for r in recent_reviews
        ]
        
        rating_pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "is_approved": True
                }
            },
            {
                "$group": {
                    "_id": "$rating",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        rating_dist = await self.reviews.aggregate(rating_pipeline).to_list(length=None)
        
        rating_data = {
            "average": 0,
            "total": 0,
            "distribution": {str(i): 0 for i in range(1, 6)}
        }
        
        total_rating = 0
        total_count = 0
        for item in rating_dist:
            rating = item["_id"]
            count = item["count"]
            rating_data["distribution"][str(rating)] = count
            total_rating += rating * count
            total_count += count
        
        if total_count > 0:
            rating_data["average"] = round(total_rating / total_count, 1)
            rating_data["total"] = total_count
        
        return {
            "id": str(tenant["_id"]),
            "salon_name": tenant["salon_name"],
            "subdomain": tenant["subdomain"],
            "owner_name": tenant["owner_name"],
            "phone": tenant["phone"],
            "email": tenant["email"],
            "address": tenant.get("address"),
            "logo_url": tenant.get("logo_url"),
            "brand_color": tenant.get("brand_color", "#6366f1"),
            "qr_code_url": tenant.get("qr_code_url"),
            "services": services_list,
            "recent_reviews": reviews_list,
            "rating_data": rating_data
        }
    
    async def track_referral_source(
        self,
        tenant_id: str,
        source: str,
        referrer_id: Optional[str] = None
    ):
        """Track referral source"""
        referral_data = {
            "tenant_id": tenant_id,
            "source": source,
            "referrer_id": referrer_id,
            "timestamp": datetime.utcnow()
        }
        
        await self.db.referral_tracking.insert_one(referral_data)
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance in km"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return round(distance, 2)
