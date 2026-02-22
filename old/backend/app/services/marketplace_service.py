"""
Marketplace Service
Business logic for public salon directory and marketplace
"""

from typing import List, Optional, Tuple
from bson import ObjectId
from datetime import datetime
import math

from app.database import get_database
from app.schemas.marketplace import (
    SalonProfile,
    SalonSearch,
    SalonFilter,
    SalonRegister,
    SalonCard
)


class MarketplaceService:
    """Service for marketplace operations"""

    def __init__(self):
        self._db = None
        self._tenants = None
        self._services_col = None
        self._staff_col = None
        self._reviews_col = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def tenants(self):
        if self._tenants is None:
            self._tenants = self.db.tenants
        return self._tenants
    
    @property
    def services_col(self):
        if self._services_col is None:
            self._services_col = self.db.services
        return self._services_col
    
    @property
    def staff_col(self):
        if self._staff_col is None:
            self._staff_col = self.db.staff
        return self._staff_col
    
    @property
    def reviews_col(self):
        if self._reviews_col is None:
            self._reviews_col = self.db.reviews
        return self._reviews_col

    def calculate_distance(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula
        Returns distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    async def search_salons(
        self, 
        search: SalonSearch
    ) -> Tuple[List[SalonCard], int]:
        """
        Search for salons with filters and location-based search
        Returns list of salon cards and total count
        """
        query = {"is_published": True}

        # Text search
        if search.query:
            query["$or"] = [
                {"name": {"$regex": search.query, "$options": "i"}},
                {"description": {"$regex": search.query, "$options": "i"}},
                {"specialties": {"$regex": search.query, "$options": "i"}}
            ]

        # Apply filters
        if search.filters:
            filters = search.filters

            # Rating filter
            if filters.min_rating:
                query["average_rating"] = {"$gte": filters.min_rating}

            # Price filter
            if filters.max_price:
                query["starting_price"] = {"$lte": filters.max_price}

            # Service filter
            if filters.services:
                # Get service IDs matching the service names
                service_docs = list(self.services_col.find({
                    "name": {"$in": filters.services}
                }))
                service_ids = [str(s["_id"]) for s in service_docs]
                query["service_ids"] = {"$in": service_ids}

            # Location-based search
            if filters.latitude and filters.longitude:
                radius_meters = filters.radius_km * 1000
                query["location"] = {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [filters.longitude, filters.latitude]
                        },
                        "$maxDistance": radius_meters
                    }
                }

        # Get total count
        total = self.tenants.count_documents(query)

        # Execute query with pagination
        cursor = self.tenants.find(query).skip(search.skip).limit(search.limit)

        # Build salon cards
        salons = []
        user_location = None
        if search.filters and search.filters.latitude and search.filters.longitude:
            user_location = (search.filters.latitude, search.filters.longitude)

        for tenant in cursor:
            # Calculate distance if user location provided
            distance_km = None
            if user_location and tenant.get("location"):
                coords = tenant["location"]["coordinates"]
                distance_km = self.calculate_distance(
                    user_location[0],
                    user_location[1],
                    coords[1],  # latitude
                    coords[0]   # longitude
                )

            salon_card = SalonCard(
                _id=str(tenant["_id"]),
                name=tenant.get("name", ""),
                logo_url=tenant.get("logo_url"),
                average_rating=tenant.get("average_rating", 0.0),
                total_reviews=tenant.get("total_reviews", 0),
                starting_price=tenant.get("starting_price"),
                distance_km=distance_km,
                city=tenant.get("city"),
                specialties=tenant.get("specialties", [])
            )
            salons.append(salon_card)

        # Sort results
        if search.filters and search.filters.sort_by:
            sort_by = search.filters.sort_by
            if sort_by == "distance" and user_location:
                salons.sort(key=lambda x: x.distance_km or float('inf'))
            elif sort_by == "rating":
                salons.sort(key=lambda x: x.average_rating, reverse=True)
            elif sort_by == "price":
                salons.sort(key=lambda x: x.starting_price or float('inf'))
            elif sort_by == "popularity":
                salons.sort(key=lambda x: x.total_reviews, reverse=True)

        return salons, total

    async def get_salon_profile(self, salon_id: str) -> Optional[SalonProfile]:
        """
        Get complete salon profile by ID or subdomain
        """
        # Try to find by ObjectId first
        query = {}
        try:
            query = {"_id": ObjectId(salon_id)}
        except:
            # If not valid ObjectId, try subdomain
            query = {"subdomain": salon_id}

        tenant = self.tenants.find_one(query)
        if not tenant or not tenant.get("is_published"):
            return None

        # Get services
        services = list(self.services_col.find({
            "tenant_id": tenant["_id"]
        }))

        # Get staff
        staff = list(self.staff_col.find({
            "tenant_id": tenant["_id"]
        }))

        # Build profile
        profile = SalonProfile(
            _id=str(tenant["_id"]),
            tenant_id=str(tenant["_id"]),
            name=tenant.get("name", ""),
            subdomain=tenant.get("subdomain", ""),
            description=tenant.get("description"),
            address=tenant.get("address", ""),
            city=tenant.get("city"),
            state=tenant.get("state"),
            phone=tenant.get("phone", ""),
            email=tenant.get("email"),
            website=tenant.get("website"),
            logo_url=tenant.get("logo_url"),
            cover_photo_url=tenant.get("cover_photo_url"),
            gallery_urls=tenant.get("gallery_urls", []),
            location=tenant.get("location"),
            services=[{
                "id": str(s["_id"]),
                "name": s.get("name", ""),
                "price": s.get("price", 0),
                "duration_minutes": s.get("duration_minutes", 0),
                "description": s.get("description")
            } for s in services],
            staff=[{
                "id": str(st["_id"]),
                "name": st.get("name", ""),
                "photo_url": st.get("photo_url"),
                "specialties": st.get("specialties", [])
            } for st in staff],
            average_rating=tenant.get("average_rating", 0.0),
            total_reviews=tenant.get("total_reviews", 0),
            starting_price=tenant.get("starting_price"),
            is_published=tenant.get("is_published", False),
            is_featured=tenant.get("is_featured", False),
            specialties=tenant.get("specialties", []),
            operating_hours=tenant.get("operating_hours"),
            created_at=tenant.get("created_at", datetime.utcnow())
        )

        return profile

    async def register_salon(self, registration: SalonRegister) -> str:
        """
        Register a new salon (creates tenant with trial subscription)
        Returns tenant_id
        """
        # Generate subdomain from salon name
        subdomain = registration.salon_name.lower().replace(" ", "-")
        subdomain = "".join(c for c in subdomain if c.isalnum() or c == "-")

        # Check if subdomain already exists
        existing = self.tenants.find_one({"subdomain": subdomain})
        if existing:
            # Append number to make unique
            counter = 1
            while self.tenants.find_one({"subdomain": f"{subdomain}-{counter}"}):
                counter += 1
            subdomain = f"{subdomain}-{counter}"

        # Create tenant document
        tenant_doc = {
            "name": registration.salon_name,
            "subdomain": subdomain,
            "description": registration.description,
            "address": registration.address,
            "city": registration.city,
            "state": registration.state,
            "phone": registration.phone,
            "email": registration.email,
            "website": registration.website,
            "owner_name": registration.owner_name,
            "owner_phone": registration.owner_phone,
            "owner_email": registration.owner_email,
            "subscription_plan": "trial",
            "is_published": False,  # Requires profile completion
            "is_featured": False,
            "average_rating": 0.0,
            "total_reviews": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = self.tenants.insert_one(tenant_doc)
        return str(result.inserted_id)

    async def update_salon_location(
        self, 
        tenant_id: str, 
        latitude: float, 
        longitude: float
    ):
        """
        Update salon geospatial location
        """
        self.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {
                "$set": {
                    "location": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "updated_at": datetime.utcnow()
                }
            }
        )

    async def publish_salon(self, tenant_id: str):
        """
        Publish salon to public directory
        """
        self.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {
                "$set": {
                    "is_published": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )

    async def unpublish_salon(self, tenant_id: str):
        """
        Remove salon from public directory
        """
        self.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {
                "$set": {
                    "is_published": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
