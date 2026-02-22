"""
Location service for managing salon locations.
Handles business logic for location management, geocoding, and analytics.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo.database import Database
import logging

from app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationStatus,
)

logger = logging.getLogger(__name__)


class LocationService:
    """Service for managing salon locations"""

    def __init__(self, db: Database):
        """Initialize service with database connection"""
        self.db = db
        self.locations_collection = db["locations"]
        self.stylists_collection = db["stylists"]
        self.services_collection = db["services"]
        self.bookings_collection = db["bookings"]

    # ========================================================================
    # Location CRUD Operations
    # ========================================================================

    def create_location(
        self, tenant_id: str, location_data: LocationCreate
    ) -> Dict[str, Any]:
        """
        Create a new location.

        Args:
            tenant_id: Tenant ID
            location_data: Location creation data

        Returns:
            Created location document

        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        if not location_data.name or not location_data.address:
            raise ValueError("Name and address are required")

        # If setting as primary, unset other primary locations
        if location_data.is_primary:
            self.locations_collection.update_many(
                {"tenant_id": tenant_id, "is_primary": True},
                {"$set": {"is_primary": False}}
            )

        # Create location document
        location_doc = {
            "tenant_id": tenant_id,
            "name": location_data.name,
            "address": location_data.address,
            "city": location_data.city,
            "state": location_data.state,
            "country": location_data.country,
            "postal_code": location_data.postal_code,
            "phone": location_data.phone,
            "email": location_data.email,
            "timezone": location_data.timezone,
            "status": location_data.status.value,
            "is_primary": location_data.is_primary,
            "amenities": location_data.amenities or [],
            "capacity": location_data.capacity,
            "manager_id": location_data.manager_id,
            "business_hours": location_data.business_hours,
            "latitude": location_data.latitude,
            "longitude": location_data.longitude,
            "formatted_address": location_data.formatted_address,
            "reopening_date": location_data.reopening_date,
            "images": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = self.locations_collection.insert_one(location_doc)
        location_doc["_id"] = result.inserted_id
        logger.info(f"Created location {result.inserted_id} for tenant {tenant_id}")
        return location_doc

    def get_locations(
        self,
        tenant_id: str,
        status: Optional[LocationStatus] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Get all locations for a tenant with optional filtering.

        Args:
            tenant_id: Tenant ID
            status: Filter by status
            search: Search by name, city, or address
            page: Page number
            limit: Items per page

        Returns:
            Paginated list of locations
        """
        filters = {"tenant_id": tenant_id}

        if status:
            filters["status"] = status.value

        if search:
            filters["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"city": {"$regex": search, "$options": "i"}},
                {"address": {"$regex": search, "$options": "i"}},
            ]

        total = self.locations_collection.count_documents(filters)
        skip = (page - 1) * limit

        locations = list(self.locations_collection.find(filters).skip(skip).limit(limit))

        pages = (total + limit - 1) // limit

        return {
            "items": locations,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
        }

    def get_location(self, location_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single location by ID.

        Args:
            location_id: Location ID
            tenant_id: Tenant ID (for verification)

        Returns:
            Location document or None

        Raises:
            ValueError: If location not found or doesn't belong to tenant
        """
        try:
            location = self.locations_collection.find_one({
                "_id": ObjectId(location_id),
                "tenant_id": tenant_id,
            })
            if not location:
                raise ValueError("Location not found")
            return location
        except Exception as e:
            logger.error(f"Error getting location {location_id}: {e}")
            raise

    def update_location(
        self, location_id: str, tenant_id: str, updates: LocationUpdate
    ) -> Dict[str, Any]:
        """
        Update a location.

        Args:
            location_id: Location ID
            tenant_id: Tenant ID
            updates: Update data

        Returns:
            Updated location document

        Raises:
            ValueError: If location not found
        
        Requirement 5.5: Invalidate caches on location update
        Requirement 8.2: Re-geocode on address change
        """
        # Verify location exists and belongs to tenant
        location = self.get_location(location_id, tenant_id)

        # If setting as primary, unset other primary locations
        if updates.is_primary:
            self.locations_collection.update_many(
                {"tenant_id": tenant_id, "_id": {"$ne": ObjectId(location_id)}, "is_primary": True},
                {"$set": {"is_primary": False}}
            )

        # Build update document
        update_doc = {}
        address_changed = False
        
        for field, value in updates.dict(exclude_unset=True).items():
            if value is not None:
                if isinstance(value, LocationStatus):
                    update_doc[field] = value.value
                else:
                    update_doc[field] = value
                
                # Track if address changed
                if field == "address" and value != location.get("address"):
                    address_changed = True

        update_doc["updated_at"] = datetime.utcnow()

        # Update location
        result = self.locations_collection.find_one_and_update(
            {"_id": ObjectId(location_id), "tenant_id": tenant_id},
            {"$set": update_doc},
            return_document=True,
        )

        # Invalidate caches if address changed
        if address_changed:
            try:
                from app.services.cache_service import CacheService
                cache_service = CacheService()
                cache_service.invalidate_location(location_id)
                logger.info(f"Invalidated caches for location {location_id} due to address change")
            except Exception as e:
                logger.error(f"Error invalidating cache for location {location_id}: {e}")

        logger.info(f"Updated location {location_id}")
        return result

    def delete_location(self, location_id: str, tenant_id: str) -> None:
        """
        Delete a location.

        Args:
            location_id: Location ID
            tenant_id: Tenant ID

        Raises:
            ValueError: If location has dependencies
        """
        # Validate location_id is a valid ObjectId
        try:
            location_oid = ObjectId(location_id)
        except Exception as e:
            raise ValueError(f"Invalid location ID: {location_id}")

        # Check dependencies
        dependencies = self.check_dependencies(location_id)
        if not dependencies["can_delete"]:
            raise ValueError(
                f"Cannot delete location with dependencies: "
                f"{dependencies['staff_count']} staff, "
                f"{dependencies['service_count']} services, "
                f"{dependencies['booking_count']} bookings"
            )

        result = self.locations_collection.delete_one({
            "_id": location_oid,
            "tenant_id": tenant_id,
        })

        if result.deleted_count == 0:
            raise ValueError("Location not found")

        logger.info(f"Deleted location {location_id}")

    # ========================================================================
    # Primary Location Management
    # ========================================================================

    async def set_primary_location(self, tenant_id: str, location_id: str) -> Dict[str, Any]:
        """
        Set a location as primary for the tenant.

        Args:
            tenant_id: Tenant ID
            location_id: Location ID to set as primary

        Returns:
            Updated location document
        """
        # Unset other primary locations
        await self.locations_collection.update_many(
            {"tenant_id": tenant_id, "is_primary": True},
            {"$set": {"is_primary": False}}
        )

        # Set this location as primary
        result = await self.locations_collection.find_one_and_update(
            {"_id": ObjectId(location_id), "tenant_id": tenant_id},
            {"$set": {"is_primary": True, "updated_at": datetime.utcnow()}},
            return_document=True,
        )

        if not result:
            raise ValueError("Location not found")

        logger.info(f"Set location {location_id} as primary for tenant {tenant_id}")
        return result

    async def get_primary_location(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the primary location for a tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            Primary location document or None
        """
        return await self.locations_collection.find_one({
            "tenant_id": tenant_id,
            "is_primary": True,
        })

    # ========================================================================
    # Dependency Checking
    # ========================================================================

    def check_dependencies(self, location_id: str) -> Dict[str, Any]:
        """
        Check if location has dependencies (staff, services, bookings).

        Args:
            location_id: Location ID

        Returns:
            Dictionary with dependency information
        """
        # Validate location_id is a valid ObjectId
        try:
            location_oid = ObjectId(location_id)
        except Exception as e:
            logger.error(f"Invalid location ID format: {location_id}")
            return {
                "can_delete": False,
                "staff_count": 0,
                "service_count": 0,
                "booking_count": 0,
                "messages": ["Invalid location ID"],
            }

        staff_count = self.stylists_collection.count_documents({
            "assigned_locations": location_oid
        })

        service_count = self.services_collection.count_documents({
            "available_at_locations": location_oid
        })

        booking_count = self.bookings_collection.count_documents({
            "location_id": location_oid,
            "status": {"$in": ["pending", "confirmed"]}
        })

        messages = []
        if staff_count > 0:
            messages.append(f"{staff_count} staff member(s) assigned")
        if service_count > 0:
            messages.append(f"{service_count} service(s) available")
        if booking_count > 0:
            messages.append(f"{booking_count} active booking(s)")

        return {
            "can_delete": staff_count == 0 and service_count == 0 and booking_count == 0,
            "staff_count": staff_count,
            "service_count": service_count,
            "booking_count": booking_count,
            "messages": messages,
        }

    # ========================================================================
    # Image Management
    # ========================================================================

    async def add_image(
        self, location_id: str, tenant_id: str, image_url: str, is_primary: bool = False
    ) -> Dict[str, Any]:
        """
        Add an image to a location.

        Args:
            location_id: Location ID
            tenant_id: Tenant ID
            image_url: Image URL
            is_primary: Whether to set as primary image

        Returns:
            Updated location document

        Raises:
            ValueError: If location not found or max images reached
        """
        location = await self.get_location(location_id, tenant_id)

        # Check max images limit
        if len(location.get("images", [])) >= 10:
            raise ValueError("Maximum 10 images per location")

        # If setting as primary, unset other primary images
        if is_primary:
            await self.locations_collection.update_one(
                {"_id": ObjectId(location_id)},
                {"$set": {"images.$[].is_primary": False}}
            )

        image_id = str(ObjectId())
        image_doc = {
            "id": image_id,
            "url": image_url,
            "is_primary": is_primary,
            "uploaded_at": datetime.utcnow(),
        }

        result = await self.locations_collection.find_one_and_update(
            {"_id": ObjectId(location_id), "tenant_id": tenant_id},
            {
                "$push": {"images": image_doc},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True,
        )

        logger.info(f"Added image to location {location_id}")
        return result

    def delete_image(self, location_id: str, tenant_id: str, image_id: str) -> Dict[str, Any]:
        """
        Delete an image from a location.

        Args:
            location_id: Location ID
            tenant_id: Tenant ID
            image_id: Image ID to delete

        Returns:
            Updated location document
        """
        result = self.locations_collection.find_one_and_update(
            {"_id": ObjectId(location_id), "tenant_id": tenant_id},
            {
                "$pull": {"images": {"id": image_id}},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True,
        )

        if not result:
            raise ValueError("Location not found")

        logger.info(f"Deleted image {image_id} from location {location_id}")
        return result

    async def set_primary_image(
        self, location_id: str, tenant_id: str, image_id: str
    ) -> Dict[str, Any]:
        """
        Set an image as primary for a location.

        Args:
            location_id: Location ID
            tenant_id: Tenant ID
            image_id: Image ID to set as primary

        Returns:
            Updated location document
        """
        # Unset all primary images
        await self.locations_collection.update_one(
            {"_id": ObjectId(location_id), "tenant_id": tenant_id},
            {"$set": {"images.$[].is_primary": False}}
        )

        # Set the specified image as primary
        result = await self.locations_collection.find_one_and_update(
            {"_id": ObjectId(location_id), "tenant_id": tenant_id},
            {
                "$set": {
                    "images.$[img].is_primary": True,
                    "updated_at": datetime.utcnow()
                }
            },
            array_filters=[{"img.id": image_id}],
            return_document=True,
        )

        if not result:
            raise ValueError("Location or image not found")

        logger.info(f"Set image {image_id} as primary for location {location_id}")
        return result

    # ========================================================================
    # Status Management
    # ========================================================================

    async def update_status(
        self, location_id: str, tenant_id: str, status: LocationStatus, reopening_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Update location status.

        Args:
            location_id: Location ID
            tenant_id: Tenant ID
            status: New status
            reopening_date: Reopening date for temporarily_closed status

        Returns:
            Updated location document
        """
        update_doc = {
            "status": status.value,
            "updated_at": datetime.utcnow(),
        }

        if status == LocationStatus.TEMPORARILY_CLOSED and reopening_date:
            update_doc["reopening_date"] = reopening_date

        result = await self.locations_collection.find_one_and_update(
            {"_id": ObjectId(location_id), "tenant_id": tenant_id},
            {"$set": update_doc},
            return_document=True,
        )

        if not result:
            raise ValueError("Location not found")

        logger.info(f"Updated status for location {location_id} to {status.value}")
        return result

    # ========================================================================
    # Analytics
    # ========================================================================

    async def get_location_analytics(
        self, location_id: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get analytics for a location.

        Args:
            location_id: Location ID
            start_date: Start date for analytics
            end_date: End date for analytics

        Returns:
            Analytics data
        """
        # Get location for capacity
        location = await self.locations_collection.find_one({"_id": ObjectId(location_id)})
        if not location:
            raise ValueError("Location not found")

        # Count total bookings
        total_bookings = await self.bookings_collection.count_documents({
            "location_id": ObjectId(location_id),
            "created_at": {"$gte": start_date, "$lte": end_date}
        })

        # Count completed bookings
        completed_bookings = await self.bookings_collection.count_documents({
            "location_id": ObjectId(location_id),
            "status": "completed",
            "created_at": {"$gte": start_date, "$lte": end_date}
        })

        # Calculate occupancy rate
        days = (end_date - start_date).days or 1
        capacity = location.get("capacity", 1)
        occupancy_rate = (completed_bookings / (capacity * days)) * 100 if capacity > 0 else 0

        # Calculate revenue from completed bookings
        revenue_pipeline = [
            {
                "$match": {
                    "location_id": ObjectId(location_id),
                    "status": "completed",
                    "created_at": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_revenue": {"$sum": {"$toDouble": "$total_price"}}
                }
            }
        ]
        revenue_result = list(await self.bookings_collection.aggregate(revenue_pipeline))
        total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0.0
        average_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0.0

        return {
            "total_revenue": total_revenue,
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "occupancy_rate": min(occupancy_rate, 100.0),
            "average_booking_value": average_booking_value,
            "top_services": [],
            "staff_performance": [],
        }

    # ========================================================================
    # Boundary Data Integration (2026 Feature)
    # ========================================================================

    async def validate_location_boundary(
        self,
        location_id: str,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """
        Validate location against boundary data

        Args:
            location_id: Location ID
            tenant_id: Tenant ID

        Returns:
            Validation result with boundary information

        Requirement 14.2: Validate salon locations against boundary data
        """
        try:
            location = await self.get_location(location_id, tenant_id)
            
            if not location.get("latitude") or not location.get("longitude"):
                return {
                    "valid": False,
                    "error": "Location missing coordinates",
                }

            from app.services.boundary_service import BoundaryService
            from app.services.cache_service import CacheService
            
            cache_service = CacheService()
            boundary_service = BoundaryService(cache_service)
            
            # Get boundary data
            boundary_data = await boundary_service.get_administrative_divisions(
                location["latitude"],
                location["longitude"],
                country=location.get("country"),
            )
            
            # Update location with boundary information
            update_doc = {
                "administrative_region": boundary_data.get("region"),
                "postal_code": boundary_data.get("postal_code"),
                "boundary_validated_at": datetime.utcnow(),
            }
            
            result = await self.locations_collection.find_one_and_update(
                {"_id": ObjectId(location_id), "tenant_id": tenant_id},
                {"$set": update_doc},
                return_document=True,
            )
            
            logger.info(f"Validated location {location_id} against boundary data")
            
            return {
                "valid": True,
                "boundary_data": boundary_data,
                "location": result,
            }
        
        except Exception as e:
            logger.error(f"Error validating location boundary: {e}")
            return {
                "valid": False,
                "error": str(e),
            }

    async def refresh_boundary_data_for_locations(
        self,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """
        Refresh boundary data for all locations in a tenant

        Args:
            tenant_id: Tenant ID

        Returns:
            Refresh statistics

        Requirement 14.4: Automatically refresh boundary data when updated
        """
        try:
            from app.services.boundary_service import BoundaryService
            from app.services.cache_service import CacheService
            
            cache_service = CacheService()
            boundary_service = BoundaryService(cache_service)
            
            # Get all locations for tenant
            locations = list(self.locations_collection.find({"tenant_id": tenant_id}))
            
            stats = {
                "total_locations": len(locations),
                "revalidated": 0,
                "errors": [],
                "refreshed_at": datetime.utcnow().isoformat(),
            }
            
            # Refresh boundary data for each location
            for location in locations:
                try:
                    if location.get("latitude") and location.get("longitude"):
                        boundary_data = await boundary_service.get_administrative_divisions(
                            location["latitude"],
                            location["longitude"],
                            country=location.get("country"),
                            use_cache=False,  # Force refresh
                        )
                        
                        # Update location with new boundary data
                        await self.locations_collection.update_one(
                            {"_id": location["_id"]},
                            {
                                "$set": {
                                    "administrative_region": boundary_data.get("region"),
                                    "postal_code": boundary_data.get("postal_code"),
                                    "boundary_validated_at": datetime.utcnow(),
                                }
                            }
                        )
                        
                        stats["revalidated"] += 1
                
                except Exception as e:
                    logger.error(f"Error refreshing boundary for location {location['_id']}: {e}")
                    stats["errors"].append({
                        "location_id": str(location["_id"]),
                        "error": str(e),
                    })
            
            logger.info(f"Refreshed boundary data for {stats['revalidated']} locations")
            return stats
        
        except Exception as e:
            logger.error(f"Error refreshing boundary data: {e}")
            raise

    async def get_locations_by_region(
        self,
        tenant_id: str,
        region: str,
    ) -> List[Dict[str, Any]]:
        """
        Get all locations in a specific administrative region

        Args:
            tenant_id: Tenant ID
            region: Administrative region name

        Returns:
            List of locations in the region

        Requirement 14.2: Use boundary data for regional filtering
        """
        try:
            locations = list(self.locations_collection.find({
                "tenant_id": tenant_id,
                "administrative_region": region,
            }))
            
            logger.info(f"Found {len(locations)} locations in region {region}")
            return locations
        
        except Exception as e:
            logger.error(f"Error getting locations by region: {e}")
            raise
