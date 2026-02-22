"""
Salon Location Management Service

Handles all business logic for multi-location salon management including:
- Location CRUD operations
- Primary location management
- Dependency checking
- Location analytics
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError
import logging

logger = logging.getLogger(__name__)


class SalonLocationService:
    """Service for managing salon locations"""

    def __init__(self, db):
        """Initialize with database connection"""
        self.db = db
        self.locations_collection: Collection = db.locations
        self.stylists_collection: Collection = db.stylists
        self.services_collection: Collection = db.services
        self.bookings_collection: Collection = db.bookings

    async def create_location(self, tenant_id: str, data: Dict) -> Dict:
        """
        Create a new location for a tenant
        
        Args:
            tenant_id: Tenant ID
            data: Location data from LocationCreate schema
            
        Returns:
            Created location document
            
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        required_fields = ['name', 'address', 'city', 'state', 'phone']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")

        # If setting as primary, unset other primary locations
        if data.get('is_primary', False):
            await self.locations_collection.update_many(
                {'tenant_id': tenant_id, 'is_primary': True},
                {'$set': {'is_primary': False}}
            )

        # Create location document
        location_doc = {
            'tenant_id': tenant_id,
            'name': data['name'],
            'address': data['address'],
            'city': data['city'],
            'state': data['state'],
            'country': data.get('country', ''),
            'postal_code': data.get('postal_code', ''),
            'phone': data['phone'],
            'email': data.get('email'),
            'timezone': data.get('timezone'),
            'status': data.get('status', 'active'),
            'is_primary': data.get('is_primary', False),
            'capacity': data.get('capacity'),
            'manager_id': data.get('manager_id'),
            'amenities': data.get('amenities', []),
            'business_hours': data.get('business_hours'),
            'reopening_date': data.get('reopening_date'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'formatted_address': data.get('formatted_address'),
            'images': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        result = await self.locations_collection.insert_one(location_doc)
        location_doc['_id'] = result.inserted_id
        return self._format_location(location_doc)

    async def get_locations(self, tenant_id: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Get all locations for a tenant
        
        Args:
            tenant_id: Tenant ID
            filters: Optional filters (status, amenities, etc.)
            
        Returns:
            List of location documents
        """
        query = {'tenant_id': tenant_id}
        
        if filters:
            if 'status' in filters:
                query['status'] = filters['status']
            if 'amenities' in filters:
                query['amenities'] = {'$in': filters['amenities']}

        locations = await self.locations_collection.find(query).sort('is_primary', -1).to_list(None)
        return [self._format_location(loc) for loc in locations]

    async def get_location(self, location_id: str, tenant_id: str) -> Dict:
        """
        Get a single location by ID
        
        Args:
            location_id: Location ID
            tenant_id: Tenant ID (for verification)
            
        Returns:
            Location document
            
        Raises:
            ValueError: If location not found
        """
        location = await self.locations_collection.find_one({
            '_id': ObjectId(location_id),
            'tenant_id': tenant_id
        })
        
        if not location:
            raise ValueError(f"Location {location_id} not found")
        
        return self._format_location(location)

    async def update_location(self, location_id: str, tenant_id: str, data: Dict) -> Dict:
        """
        Update a location
        
        Args:
            location_id: Location ID
            tenant_id: Tenant ID (for verification)
            data: Update data from LocationUpdate schema
            
        Returns:
            Updated location document
            
        Raises:
            ValueError: If location not found
        """
        # Verify location exists and belongs to tenant
        location = await self.locations_collection.find_one({
            '_id': ObjectId(location_id),
            'tenant_id': tenant_id
        })
        
        if not location:
            raise ValueError(f"Location {location_id} not found")

        # If setting as primary, unset other primary locations
        if data.get('is_primary', False) and not location.get('is_primary', False):
            await self.locations_collection.update_many(
                {'tenant_id': tenant_id, 'is_primary': True},
                {'$set': {'is_primary': False}}
            )

        # Build update document (only include provided fields)
        update_doc = {}
        for key, value in data.items():
            if value is not None:
                update_doc[key] = value

        update_doc['updated_at'] = datetime.utcnow()

        # Update location
        result = await self.locations_collection.find_one_and_update(
            {'_id': ObjectId(location_id)},
            {'$set': update_doc},
            return_document=True
        )

        return self._format_location(result)

    async def delete_location(self, location_id: str, tenant_id: str) -> Dict:
        """
        Delete a location after checking dependencies
        
        Args:
            location_id: Location ID
            tenant_id: Tenant ID (for verification)
            
        Returns:
            Success message
            
        Raises:
            ValueError: If location has dependencies or not found
        """
        # Verify location exists
        location = await self.locations_collection.find_one({
            '_id': ObjectId(location_id),
            'tenant_id': tenant_id
        })
        
        if not location:
            raise ValueError(f"Location {location_id} not found")

        # Check dependencies
        dependencies = await self.check_dependencies(location_id)
        
        if not dependencies['can_delete']:
            raise ValueError(
                f"Cannot delete location with dependencies: "
                f"{dependencies['staff_count']} staff, "
                f"{dependencies['service_count']} services, "
                f"{dependencies['booking_count']} bookings"
            )

        # Delete location
        await self.locations_collection.delete_one({'_id': ObjectId(location_id)})
        
        return {'success': True, 'message': 'Location deleted successfully'}

    async def set_primary_location(self, tenant_id: str, location_id: str) -> Dict:
        """
        Set a location as the primary location for a tenant
        
        Args:
            tenant_id: Tenant ID
            location_id: Location ID to set as primary
            
        Returns:
            Updated location document
            
        Raises:
            ValueError: If location not found
        """
        # Verify location exists
        location = await self.locations_collection.find_one({
            '_id': ObjectId(location_id),
            'tenant_id': tenant_id
        })
        
        if not location:
            raise ValueError(f"Location {location_id} not found")

        # Unset other primary locations
        await self.locations_collection.update_many(
            {'tenant_id': tenant_id, 'is_primary': True},
            {'$set': {'is_primary': False}}
        )

        # Set this location as primary
        result = await self.locations_collection.find_one_and_update(
            {'_id': ObjectId(location_id)},
            {'$set': {'is_primary': True, 'updated_at': datetime.utcnow()}},
            return_document=True
        )

        return self._format_location(result)

    async def check_dependencies(self, location_id: str) -> Dict:
        """
        Check if a location has dependencies (staff, services, bookings)
        
        Args:
            location_id: Location ID
            
        Returns:
            Dictionary with dependency information
        """
        # Count staff assigned to location
        staff_count = await self.stylists_collection.count_documents({
            'assigned_locations': ObjectId(location_id)
        })

        # Count services available at location
        service_count = await self.services_collection.count_documents({
            'available_at_locations': ObjectId(location_id)
        })

        # Count active bookings at location
        booking_count = await self.bookings_collection.count_documents({
            'location_id': ObjectId(location_id),
            'status': {'$in': ['pending', 'confirmed']}
        })

        can_delete = staff_count == 0 and service_count == 0 and booking_count == 0

        message = None
        if not can_delete:
            reasons = []
            if staff_count > 0:
                reasons.append(f"{staff_count} staff member(s)")
            if service_count > 0:
                reasons.append(f"{service_count} service(s)")
            if booking_count > 0:
                reasons.append(f"{booking_count} active booking(s)")
            message = f"Location has {', '.join(reasons)}"

        return {
            'can_delete': can_delete,
            'staff_count': staff_count,
            'service_count': service_count,
            'booking_count': booking_count,
            'message': message
        }

    async def get_location_analytics(
        self,
        location_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Calculate analytics for a location
        
        Args:
            location_id: Location ID
            start_date: Start date for analytics period
            end_date: End date for analytics period
            
        Returns:
            Analytics data
        """
        # Get location to verify it exists
        location = await self.locations_collection.find_one({
            '_id': ObjectId(location_id)
        })
        
        if not location:
            raise ValueError(f"Location {location_id} not found")

        # Query bookings for this location in the date range
        bookings = await self.bookings_collection.find({
            'location_id': ObjectId(location_id),
            'created_at': {'$gte': start_date, '$lte': end_date}
        }).to_list(None)

        # Calculate metrics
        total_bookings = len(bookings)
        completed_bookings = len([b for b in bookings if b.get('status') == 'completed'])
        
        # Calculate revenue (sum of booking prices)
        total_revenue = sum(float(b.get('price', 0)) for b in bookings)
        average_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0

        # Calculate occupancy rate
        capacity = location.get('capacity', 1)
        days_in_period = (end_date - start_date).days or 1
        occupancy_rate = (completed_bookings / (capacity * days_in_period)) * 100 if capacity > 0 else 0

        # Get top services
        service_counts = {}
        for booking in bookings:
            service_id = str(booking.get('service_id', 'unknown'))
            service_counts[service_id] = service_counts.get(service_id, 0) + 1
        
        top_services = sorted(
            [{'service_id': k, 'count': v} for k, v in service_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:5]

        # Get staff performance
        staff_performance = {}
        for booking in bookings:
            staff_id = str(booking.get('stylist_id', 'unknown'))
            if staff_id not in staff_performance:
                staff_performance[staff_id] = {'bookings': 0, 'revenue': 0}
            staff_performance[staff_id]['bookings'] += 1
            staff_performance[staff_id]['revenue'] += float(booking.get('price', 0))

        staff_perf_list = [
            {'staff_id': k, **v} for k, v in staff_performance.items()
        ]

        return {
            'location_id': location_id,
            'total_revenue': total_revenue,
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'occupancy_rate': round(occupancy_rate, 2),
            'average_booking_value': round(average_booking_value, 2),
            'top_services': top_services,
            'staff_performance': staff_perf_list,
            'period_start': start_date,
            'period_end': end_date
        }

    async def upload_location_image(
        self,
        location_id: str,
        tenant_id: str,
        image_url: str,
        is_primary: bool = False
    ) -> Dict:
        """
        Add an image to a location
        
        Args:
            location_id: Location ID
            tenant_id: Tenant ID (for verification)
            image_url: URL of the uploaded image
            is_primary: Whether to set as primary image
            
        Returns:
            Updated location document
            
        Raises:
            ValueError: If location not found or max images reached
        """
        # Verify location exists
        location = await self.locations_collection.find_one({
            '_id': ObjectId(location_id),
            'tenant_id': tenant_id
        })
        
        if not location:
            raise ValueError(f"Location {location_id} not found")

        # Check max images limit
        images = location.get('images', [])
        if len(images) >= 10:
            raise ValueError("Maximum 10 images per location")

        # If setting as primary, unset other primary images
        if is_primary:
            images = [{'id': img['id'], 'url': img['url'], 'is_primary': False, 'uploaded_at': img['uploaded_at']} 
                     for img in images]

        # Add new image
        image_id = str(ObjectId())
        new_image = {
            'id': image_id,
            'url': image_url,
            'is_primary': is_primary,
            'uploaded_at': datetime.utcnow()
        }
        images.append(new_image)

        # Update location
        result = await self.locations_collection.find_one_and_update(
            {'_id': ObjectId(location_id)},
            {'$set': {'images': images, 'updated_at': datetime.utcnow()}},
            return_document=True
        )

        return self._format_location(result)

    async def delete_location_image(
        self,
        location_id: str,
        tenant_id: str,
        image_id: str
    ) -> Dict:
        """
        Delete an image from a location
        
        Args:
            location_id: Location ID
            tenant_id: Tenant ID (for verification)
            image_id: Image ID to delete
            
        Returns:
            Updated location document
            
        Raises:
            ValueError: If location or image not found
        """
        # Verify location exists
        location = await self.locations_collection.find_one({
            '_id': ObjectId(location_id),
            'tenant_id': tenant_id
        })
        
        if not location:
            raise ValueError(f"Location {location_id} not found")

        # Find and remove image
        images = location.get('images', [])
        image_to_delete = None
        for img in images:
            if img['id'] == image_id:
                image_to_delete = img
                break

        if not image_to_delete:
            raise ValueError(f"Image {image_id} not found")

        # Remove image
        images = [img for img in images if img['id'] != image_id]

        # Update location
        result = await self.locations_collection.find_one_and_update(
            {'_id': ObjectId(location_id)},
            {'$set': {'images': images, 'updated_at': datetime.utcnow()}},
            return_document=True
        )

        return self._format_location(result)

    def _format_location(self, location: Dict) -> Dict:
        """
        Format a location document for API response
        
        Args:
            location: Raw location document from database
            
        Returns:
            Formatted location document
        """
        return {
            'id': str(location['_id']),
            'tenant_id': location['tenant_id'],
            'name': location['name'],
            'address': location['address'],
            'city': location['city'],
            'state': location['state'],
            'country': location.get('country', ''),
            'postal_code': location.get('postal_code', ''),
            'phone': location['phone'],
            'email': location.get('email'),
            'timezone': location.get('timezone'),
            'status': location.get('status', 'active'),
            'is_primary': location.get('is_primary', False),
            'capacity': location.get('capacity'),
            'manager_id': location.get('manager_id'),
            'amenities': location.get('amenities', []),
            'business_hours': location.get('business_hours'),
            'reopening_date': location.get('reopening_date'),
            'latitude': location.get('latitude'),
            'longitude': location.get('longitude'),
            'formatted_address': location.get('formatted_address'),
            'images': location.get('images', []),
            'created_at': location['created_at'],
            'updated_at': location['updated_at']
        }
