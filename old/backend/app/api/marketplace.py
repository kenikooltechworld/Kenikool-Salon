"""
Marketplace API

Endpoints for marketplace functionality including salon listings,
search, and filtering.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
import logging
from math import radians, cos, sin, asin, sqrt

from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


# ============================================================================
# Pydantic Models
# ============================================================================

class SalonLocation(BaseModel):
    """Salon location info"""
    latitude: float
    longitude: float
    address: str
    city: str
    state: str


class SalonService(BaseModel):
    """Salon service info"""
    _id: str
    name: str
    price: float
    duration_minutes: int


class SalonStaff(BaseModel):
    """Salon staff info"""
    _id: str
    name: str
    specialties: List[str]


class SalonResponse(BaseModel):
    """Salon response"""
    _id: str
    name: str
    description: Optional[str]
    location: SalonLocation
    phone: str
    email: str
    rating: float
    review_count: int
    image_url: Optional[str]
    services_count: int
    staff_count: int
    is_verified: bool


class SalonDetailResponse(SalonResponse):
    """Detailed salon response"""
    services: List[SalonService]
    staff: List[SalonStaff]
    amenities: List[str]
    operating_hours: dict
    booking_url: Optional[str]


# ============================================================================
# Helper Functions
# ============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def format_salon_response(salon: dict) -> dict:
    """Format salon document for API response"""
    location = salon.get("location", {})
    
    return {
        "_id": str(salon.get("_id", "")),
        "name": salon.get("name", ""),
        "description": salon.get("description"),
        "location": {
            "latitude": location.get("latitude", 0),
            "longitude": location.get("longitude", 0),
            "address": location.get("address", ""),
            "city": location.get("city", ""),
            "state": location.get("state", "")
        },
        "phone": salon.get("phone", ""),
        "email": salon.get("email", ""),
        "rating": salon.get("rating", 0),
        "review_count": salon.get("review_count", 0),
        "image_url": salon.get("image_url"),
        "starting_price": salon.get("starting_price"),
        "services_count": salon.get("services_count", 0),
        "staff_count": salon.get("staff_count", 0),
        "is_verified": salon.get("is_verified", False)
    }


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/salons", response_model=dict)
async def list_salons(
    limit: int = Query(12, ge=1, le=100),
    skip: int = Query(0, ge=0),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(50, ge=1, le=500),
    max_distance: Optional[float] = Query(None, ge=1, le=500, description="Maximum distance in kilometers (alias for radius_km)"),
    search: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    sort_by: str = Query("rating", pattern="^(rating|distance|name)$")
):
    """
    List salons with optional filtering and location-based search
    
    Query Parameters:
    - limit: Number of results (default: 12, max: 100)
    - skip: Number of results to skip for pagination
    - latitude: User latitude for distance calculation
    - longitude: User longitude for distance calculation
    - radius_km: Search radius in kilometers (default: 50)
    - max_distance: Maximum distance in kilometers (alias for radius_km)
    - search: Search by salon name
    - city: Filter by city
    - state: Filter by state
    - min_rating: Filter by minimum rating
    - sort_by: Sort by 'rating', 'distance', or 'name'
    
    Returns:
    - salons: List of salon objects with distance_km if location provided
    - total: Total number of salons matching criteria
    - limit: Limit used
    - skip: Skip used
    
    Requirement 10.2: Distance filtering in marketplace
    Requirement 4.4: Distance calculation error handling
    Requirement 4.5: Include distance_km in response
    """
    try:
        db = Database.get_db()
        
        # Use max_distance if provided, otherwise use radius_km
        search_radius = max_distance if max_distance is not None else radius_km
        
        # Build query filter
        # Include salons that are published (is_published: True)
        # Also include salons that don't have is_published field for backward compatibility
        query = {"$or": [{"is_published": True}, {"is_published": {"$exists": False}}]}
        
        # Text search
        if search:
            query["$text"] = {"$search": search}
        
        # City filter
        if city:
            query["location.city"] = {"$regex": city, "$options": "i"}
        
        # State filter
        if state:
            query["location.state"] = {"$regex": state, "$options": "i"}
        
        # Rating filter
        if min_rating is not None:
            query["rating"] = {"$gte": min_rating}
        
        # Get all matching salons (we'll filter by distance in Python)
        salons_cursor = db.salons.find(query).skip(skip).limit(limit * 2)  # Get extra for distance filtering
        salons = list(salons_cursor)
        
        # Filter by distance if location provided
        if latitude is not None and longitude is not None:
            filtered_salons = []
            for salon in salons:
                try:
                    location = salon.get("location", {})
                    salon_lat = location.get("latitude")
                    salon_lon = location.get("longitude")
                    
                    if salon_lat is not None and salon_lon is not None:
                        distance = haversine_distance(latitude, longitude, salon_lat, salon_lon)
                        
                        if distance <= search_radius:
                            salon["distance_km"] = round(distance, 2)
                            filtered_salons.append(salon)
                except Exception as e:
                    # Log error but continue processing other salons
                    logger.error(f"Error calculating distance for salon {salon.get('_id')}: {e}")
                    # Still include salon without distance info
                    filtered_salons.append(salon)
            
            salons = filtered_salons
        
        # Sort results
        try:
            if sort_by == "distance" and latitude is not None and longitude is not None:
                # Sort by distance, then by rating as secondary criteria
                salons.sort(key=lambda x: (
                    x.get("distance_km", float("inf")),
                    -x.get("rating", 0),  # Negative for descending order
                    -x.get("review_count", 0)  # Negative for descending order
                ))
            elif sort_by == "rating":
                # Sort by rating, then by review count as secondary criteria
                salons.sort(key=lambda x: (
                    -x.get("rating", 0),  # Negative for descending order
                    -x.get("review_count", 0)  # Negative for descending order
                ))
            elif sort_by == "name":
                salons.sort(key=lambda x: x.get("name", ""))
        except Exception as e:
            logger.error(f"Error sorting salons: {e}")
            # Continue without sorting
        
        # Apply limit after sorting
        salons = salons[:limit]
        
        # Format responses
        formatted_salons = [format_salon_response(salon) for salon in salons]
        
        # Get total count
        total = db.salons.count_documents(query)
        
        return {
            "salons": formatted_salons,
            "total": total,
            "limit": limit,
            "skip": skip
        }
    
    except Exception as e:
        logger.error(f"Error listing salons: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/salons/{salon_id}", response_model=SalonDetailResponse)
async def get_salon_detail(salon_id: str):
    """
    Get detailed information about a specific salon
    
    Includes services, staff, amenities, and operating hours
    """
    try:
        from bson import ObjectId
        
        db = Database.get_db()
        
        # Get salon - return if published or doesn't have is_published field
        salon = db.salons.find_one({"_id": ObjectId(salon_id), "$or": [{"is_published": True}, {"is_published": {"$exists": False}}]})
        
        if not salon:
            raise HTTPException(status_code=404, detail="Salon not found")
        
        # Get services
        services = list(db.services.find(
            {"salon_id": salon_id},
            {"_id": 1, "name": 1, "price": 1, "duration_minutes": 1}
        ).limit(50))
        
        # Get staff
        staff = list(db.stylists.find(
            {"salon_id": salon_id},
            {"_id": 1, "name": 1, "specialties": 1}
        ).limit(50))
        
        # Format response
        response = format_salon_response(salon)
        response["services"] = [
            {
                "_id": str(s.get("_id", "")),
                "name": s.get("name", ""),
                "price": s.get("price", 0),
                "duration_minutes": s.get("duration_minutes", 0)
            }
            for s in services
        ]
        response["staff"] = [
            {
                "_id": str(s.get("_id", "")),
                "name": s.get("name", ""),
                "specialties": s.get("specialties", [])
            }
            for s in staff
        ]
        response["amenities"] = salon.get("amenities", [])
        response["operating_hours"] = salon.get("operating_hours", {})
        response["booking_url"] = f"/marketplace/salons/{salon_id}/book"
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting salon detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/salons/{salon_id}/services")
async def get_salon_services(salon_id: str):
    """
    Get all services offered by a salon
    """
    try:
        db = Database.get_db()
        
        services = list(db.services.find(
            {"salon_id": salon_id},
            {"_id": 1, "name": 1, "price": 1, "duration_minutes": 1, "description": 1}
        ))
        
        # Convert ObjectId to string
        for service in services:
            service["_id"] = str(service["_id"])
        
        return {
            "services": services,
            "total": len(services)
        }
    
    except Exception as e:
        logger.error(f"Error getting salon services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/salons/{salon_id}/stylists")
async def get_salon_stylists(salon_id: str):
    """
    Get all stylists/staff at a salon
    """
    try:
        db = Database.get_db()
        
        stylists = list(db.stylists.find(
            {"salon_id": salon_id},
            {"_id": 1, "name": 1, "specialties": 1, "rating": 1, "image_url": 1}
        ))
        
        # Convert ObjectId to string
        for stylist in stylists:
            stylist["_id"] = str(stylist["_id"])
        
        return {
            "stylists": stylists,
            "total": len(stylists)
        }
    
    except Exception as e:
        logger.error(f"Error getting salon stylists: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/salons/{salon_id}/availability")
async def get_salon_availability(
    salon_id: str,
    date: str,
    service_id: Optional[str] = Query(None)
):
    """
    Get available time slots for a salon on a specific date
    
    Query Parameters:
    - date: Date in YYYY-MM-DD format
    - service_id: Optional service ID to filter by service duration
    """
    try:
        db = Database.get_db()
        
        # Get salon
        salon = db.salons.find_one({"_id": salon_id})
        if not salon:
            raise HTTPException(status_code=404, detail="Salon not found")
        
        # Get service duration if specified
        service_duration = 60  # Default 1 hour
        if service_id:
            service = db.services.find_one({"_id": service_id})
            if service:
                service_duration = service.get("duration_minutes", 60)
        
        # Get bookings for the date
        bookings = list(db.marketplace_bookings.find({
            "tenant_id": salon_id,
            "booking_date": date,
            "booking_status": {"$in": ["confirmed", "completed"]}
        }))
        
        # Get salon business hours from location
        location_id = salon.get("location_id")
        location = db.locations.find_one({"_id": location_id}) if location_id else None
        
        # Extract business hours (default 9 AM - 6 PM if not specified)
        business_hours = location.get("business_hours", {}) if location else {}
        opening_time = business_hours.get("opening_time", "09:00")
        closing_time = business_hours.get("closing_time", "18:00")
        
        # Parse hours and minutes
        opening_hour, opening_minute = map(int, opening_time.split(":"))
        closing_hour, closing_minute = map(int, closing_time.split(":"))
        
        # Generate available slots based on actual business hours (30-minute intervals)
        available_slots = []
        current_hour = opening_hour
        current_minute = opening_minute
        
        while (current_hour < closing_hour) or (current_hour == closing_hour and current_minute < closing_minute):
            time_str = f"{current_hour:02d}:{current_minute:02d}"
            
            # Check if slot is booked
            is_booked = any(
                booking["booking_time"] == time_str
                for booking in bookings
            )
            
            if not is_booked:
                available_slots.append(time_str)
            
            # Move to next 30-minute slot
            current_minute += 30
            if current_minute >= 60:
                current_minute = 0
                current_hour += 1
        
        return {
            "date": date,
            "available_slots": available_slots,
            "total_available": len(available_slots),
            "business_hours": {
                "opening": opening_time,
                "closing": closing_time
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting salon availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/salons/search/nearby", response_model=dict)
async def search_nearby_salons(
    latitude: float = Query(..., description="User latitude"),
    longitude: float = Query(..., description="User longitude"),
    max_distance: float = Query(50, ge=1, le=500, description="Maximum distance in kilometers"),
    limit: int = Query(12, ge=1, le=100),
    skip: int = Query(0, ge=0),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    search: Optional[str] = Query(None),
):
    """
    Search for nearby salons with secondary sorting by rating/reviews.
    
    When multiple salons are at similar distances (within 0.5km),
    they are sorted by rating and review count as secondary criteria.
    
    Query Parameters:
    - latitude: User latitude (required)
    - longitude: User longitude (required)
    - max_distance: Maximum distance in kilometers (default: 50)
    - limit: Number of results (default: 12, max: 100)
    - skip: Number of results to skip for pagination
    - min_rating: Filter by minimum rating
    - search: Search by salon name
    
    Returns:
    - salons: List of salon objects sorted by distance, then rating
    - total: Total number of salons matching criteria
    - limit: Limit used
    - skip: Skip used
    
    Requirement 10.5: Secondary sorting by rating/reviews when distances are similar
    """
    try:
        db = Database.get_db()
        
        # Build query filter
        query = {"$or": [{"is_published": True}, {"is_published": {"$exists": False}}]}
        
        # Text search
        if search:
            query["$text"] = {"$search": search}
        
        # Rating filter
        if min_rating is not None:
            query["rating"] = {"$gte": min_rating}
        
        # Get all matching salons
        salons_cursor = db.salons.find(query).skip(skip).limit(limit * 2)
        salons = list(salons_cursor)
        
        # Filter by distance and calculate distance_km
        filtered_salons = []
        for salon in salons:
            try:
                location = salon.get("location", {})
                salon_lat = location.get("latitude")
                salon_lon = location.get("longitude")
                
                if salon_lat is not None and salon_lon is not None:
                    distance = haversine_distance(latitude, longitude, salon_lat, salon_lon)
                    
                    if distance <= max_distance:
                        salon["distance_km"] = round(distance, 2)
                        filtered_salons.append(salon)
            except Exception as e:
                logger.error(f"Error calculating distance for salon {salon.get('_id')}: {e}")
                # Still include salon without distance info
                filtered_salons.append(salon)
        
        # Sort by distance, then by rating and review count as secondary criteria
        # This ensures salons at similar distances are grouped and sorted by quality
        try:
            filtered_salons.sort(key=lambda x: (
                x.get("distance_km", float("inf")),  # Primary: distance
                -x.get("rating", 0),                  # Secondary: rating (descending)
                -x.get("review_count", 0)            # Tertiary: review count (descending)
            ))
        except Exception as e:
            logger.error(f"Error sorting salons: {e}")
        
        # Apply limit after sorting
        filtered_salons = filtered_salons[:limit]
        
        # Format responses
        formatted_salons = [format_salon_response(salon) for salon in filtered_salons]
        
        # Get total count
        total = db.salons.count_documents(query)
        
        return {
            "salons": formatted_salons,
            "total": total,
            "limit": limit,
            "skip": skip
        }
    
    except Exception as e:
        logger.error(f"Error searching nearby salons: {e}")
        raise HTTPException(status_code=500, detail=str(e))
