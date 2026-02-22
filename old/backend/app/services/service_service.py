"""
Service management service - Business logic layer
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, ForbiddenException

logger = logging.getLogger(__name__)


class ServiceManagementService:
    """Service management service for handling service business logic"""
    
    @staticmethod
    async def get_services(
        tenant_id: str,
        is_active: Optional[bool] = None,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Get list of services for tenant with optional filtering
        
        Returns:
            List of service dicts
        """
        db = Database.get_db()
        
        # Build query
        query = {"tenant_id": tenant_id}
        if is_active is not None:
            query["is_active"] = is_active
        if category is not None:
            query["category"] = category
        
        logger.info(f"🔍 Querying services with: {query}")
        services = list(db.services.find(query))
        logger.info(f"📊 Found {len(services)} services for tenant {tenant_id}")
        
        return [ServiceManagementService._format_service_response(s) for s in services]
    
    @staticmethod
    async def get_service(service_id: str, tenant_id: str) -> Dict:
        """
        Get single service by ID
        
        Returns:
            Dict with service data
        """
        db = Database.get_db()
        
        service_doc = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if service_doc is None:
            raise NotFoundException("Service not found")
        
        return ServiceManagementService._format_service_response(service_doc)
    
    @staticmethod
    async def create_service(
        tenant_id: str,
        name: str,
        price: float,
        duration_minutes: int,
        description: Optional[str] = None,
        category: Optional[str] = None,
        assigned_stylists: List[str] = [],
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        tiered_pricing: Optional[List[Dict]] = None,
        booking_rules: Optional[Dict] = None,
        availability: Optional[Dict] = None,
        max_concurrent_bookings: int = 0,
        commission_structure: Optional[Dict] = None,
        required_resources: Optional[List[Dict]] = None,
        marketing_settings: Optional[Dict] = None
    ) -> Dict:
        """
        Create a new service
        
        Returns:
            Dict with created service data
            
        Requirements: 13.1, 13.2
        """
        db = Database.get_db()
        
        service_data = {
            "tenant_id": tenant_id,
            "name": name,
            "description": description,
            "price": price,
            "duration_minutes": duration_minutes,
            "category": category,
            "is_active": True,
            "assigned_stylists": assigned_stylists,
            "tiered_pricing": tiered_pricing or [],
            "booking_rules": booking_rules or {},
            "availability": availability or {},
            "max_concurrent_bookings": max_concurrent_bookings,
            "commission_structure": commission_structure,
            "required_resources": required_resources or [],
            "marketing_settings": marketing_settings or {},
            "prerequisite_services": [],
            "mandatory_addons": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.services.insert_one(service_data)
        service_id = str(result.inserted_id)
        
        logger.info(f"Service created: {service_id} for tenant: {tenant_id}")
        
        # Log audit trail
        if user_id and user_email:
            from app.services.audit_service import get_audit_service
            audit_service = get_audit_service(db)
            audit_service.log_service_creation(
                service_id=service_id,
                tenant_id=tenant_id,
                user_id=user_id,
                user_email=user_email,
                service_data=service_data
            )
        
        # Fetch created service
        service_doc = db.services.find_one({"_id": ObjectId(service_id)})
        return ServiceManagementService._format_service_response(service_doc)
    
    @staticmethod
    async def update_service(
        service_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        duration_minutes: Optional[int] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        assigned_stylists: Optional[List[str]] = None,
        available_at_locations: Optional[List[str]] = None,
        location_pricing: Optional[List[Dict]] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        tiered_pricing: Optional[List[Dict]] = None,
        booking_rules: Optional[Dict] = None,
        availability: Optional[Dict] = None,
        max_concurrent_bookings: Optional[int] = None,
        commission_structure: Optional[Dict] = None,
        required_resources: Optional[List[Dict]] = None,
        marketing_settings: Optional[Dict] = None
    ) -> Dict:
        """
        Update a service
        
        Returns:
            Dict with updated service data
            
        Requirements: 13.1, 13.3, 13.4
        """
        db = Database.get_db()
        
        # Check service exists and belongs to tenant
        service_doc = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if service_doc is None:
            raise NotFoundException("Service not found")
        
        # Store old values for audit
        old_values = {
            "name": service_doc.get("name"),
            "description": service_doc.get("description"),
            "price": service_doc.get("price"),
            "duration_minutes": service_doc.get("duration_minutes"),
            "category": service_doc.get("category"),
            "is_active": service_doc.get("is_active"),
            "assigned_stylists": service_doc.get("assigned_stylists", [])
        }
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        new_values = {}
        
        if name is not None:
            update_data["name"] = name
            new_values["name"] = name
        if description is not None:
            update_data["description"] = description
            new_values["description"] = description
        if price is not None:
            update_data["price"] = price
            new_values["price"] = price
        if duration_minutes is not None:
            update_data["duration_minutes"] = duration_minutes
            new_values["duration_minutes"] = duration_minutes
        if category is not None:
            update_data["category"] = category
            new_values["category"] = category
        if is_active is not None:
            update_data["is_active"] = is_active
            new_values["is_active"] = is_active
        if assigned_stylists is not None:
            update_data["assigned_stylists"] = assigned_stylists
            new_values["assigned_stylists"] = assigned_stylists
        if available_at_locations is not None:
            update_data["available_at_locations"] = available_at_locations
            new_values["available_at_locations"] = available_at_locations
        if location_pricing is not None:
            # Convert LocationPricing objects to dicts if needed
            if location_pricing and hasattr(location_pricing[0], 'dict'):
                location_pricing = [lp.dict() for lp in location_pricing]
            update_data["location_pricing"] = location_pricing
            new_values["location_pricing"] = location_pricing
        if tiered_pricing is not None:
            update_data["tiered_pricing"] = tiered_pricing
            new_values["tiered_pricing"] = tiered_pricing
        if booking_rules is not None:
            update_data["booking_rules"] = booking_rules
            new_values["booking_rules"] = booking_rules
        if availability is not None:
            update_data["availability"] = availability
            new_values["availability"] = availability
        if max_concurrent_bookings is not None:
            update_data["max_concurrent_bookings"] = max_concurrent_bookings
            new_values["max_concurrent_bookings"] = max_concurrent_bookings
        if commission_structure is not None:
            update_data["commission_structure"] = commission_structure
            new_values["commission_structure"] = commission_structure
        if required_resources is not None:
            update_data["required_resources"] = required_resources
            new_values["required_resources"] = required_resources
        if marketing_settings is not None:
            update_data["marketing_settings"] = marketing_settings
            new_values["marketing_settings"] = marketing_settings
        
        # Update service
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Service updated: {service_id}")
        
        # Send price change notification if price changed
        if price is not None and price != old_values.get("price"):
            try:
                from app.services.service_notification_service import get_service_notification_service
                notification_service = get_service_notification_service(db)
                notification_service.send_price_change_notification(
                    tenant_id=tenant_id,
                    service_id=service_id,
                    service_name=service_doc.get("name"),
                    old_price=old_values.get("price", 0),
                    new_price=price,
                    user_email=user_email or ""
                )
            except Exception as e:
                logger.error(f"Failed to send price change notification: {e}")
        
        # Send deactivation notification if service was deactivated
        if is_active is False and old_values.get("is_active") is True:
            try:
                from app.services.service_notification_service import get_service_notification_service
                notification_service = get_service_notification_service(db)
                notification_service.send_deactivation_notification(
                    tenant_id=tenant_id,
                    service_id=service_id,
                    service_name=service_doc.get("name")
                )
            except Exception as e:
                logger.error(f"Failed to send deactivation notification: {e}")
        
        # Log audit trail
        if user_id and user_email and new_values:
            from app.services.audit_service import get_audit_service
            audit_service = get_audit_service(db)
            audit_service.log_service_update(
                service_id=service_id,
                tenant_id=tenant_id,
                user_id=user_id,
                user_email=user_email,
                old_values=old_values,
                new_values=new_values
            )
        
        # Fetch updated service
        service_doc = db.services.find_one({"_id": ObjectId(service_id)})
        return ServiceManagementService._format_service_response(service_doc)
    
    @staticmethod
    async def delete_service(
        service_id: str,
        tenant_id: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None
    ) -> bool:
        """
        Delete a service (soft delete by setting is_active=False)
        
        Returns:
            True if successful
            
        Requirements: 13.1, 13.2
        """
        db = Database.get_db()
        
        # Check service exists and belongs to tenant
        service_doc = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if service_doc is None:
            raise NotFoundException("Service not found")
        
        # Soft delete
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        logger.info(f"Service deleted (soft): {service_id}")
        
        # Log audit trail
        if user_id and user_email:
            from app.services.audit_service import get_audit_service
            audit_service = get_audit_service(db)
            audit_service.log_service_deletion(
                service_id=service_id,
                tenant_id=tenant_id,
                user_id=user_id,
                user_email=user_email,
                service_data=ServiceManagementService._format_service_response(service_doc)
            )
        
        return True
    
    @staticmethod
    async def upload_service_photo(service_id: str, tenant_id: str, file_bytes: bytes) -> Dict:
        """
        Upload service photo to Cloudinary
        
        Returns:
            Dict with updated service data
        """
        from app.services.cloudinary_service import upload_image
        
        db = Database.get_db()
        
        # Check service exists and belongs to tenant
        service_doc = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if service_doc is None:
            raise NotFoundException("Service not found")
        
        # Upload to Cloudinary
        photo_url = await upload_image(
            file_bytes,
            folder=f"salons/{tenant_id}/services",
            public_id=f"service_{service_id}"
        )
        
        # Update service
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": {"photo_url": photo_url, "updated_at": datetime.utcnow()}}
        )
        
        logger.info(f"Photo uploaded for service: {service_id}")
        
        # Fetch updated service
        service_doc = db.services.find_one({"_id": ObjectId(service_id)})
        return ServiceManagementService._format_service_response(service_doc)
    
    @staticmethod
    def _format_service_response(service_doc: Dict) -> Dict:
        """Format service document for response"""
        return {
            "id": str(service_doc["_id"]),
            "tenant_id": service_doc["tenant_id"],
            "name": service_doc["name"],
            "description": service_doc.get("description"),
            "price": service_doc.get("price", 0.0),
            "duration_minutes": service_doc.get("duration_minutes", 30),
            "category": service_doc.get("category"),
            "photo_url": service_doc.get("photo_url"),
            "is_active": service_doc.get("is_active", True),
            "assigned_stylists": service_doc.get("assigned_stylists", []),
            "tiered_pricing": service_doc.get("tiered_pricing", []),
            "booking_rules": service_doc.get("booking_rules", {}),
            "availability": service_doc.get("availability", {}),
            "max_concurrent_bookings": service_doc.get("max_concurrent_bookings", 0),
            "commission_structure": service_doc.get("commission_structure"),
            "required_resources": service_doc.get("required_resources", []),
            "marketing_settings": service_doc.get("marketing_settings", {}),
            "prerequisite_services": service_doc.get("prerequisite_services", []),
            "mandatory_addons": service_doc.get("mandatory_addons", []),
            "available_at_locations": service_doc.get("available_at_locations", []),
            "location_pricing": service_doc.get("location_pricing", []),
            "created_at": service_doc.get("created_at", datetime.utcnow()),
            "updated_at": service_doc.get("updated_at", datetime.utcnow())
        }
    
    @staticmethod
    async def get_by_location(tenant_id: str, location_id: str) -> List[Dict]:
        """
        Get all services available at a specific location.
        
        Args:
            tenant_id: Tenant ID
            location_id: Location ID
            
        Returns:
            List of services available at the location
        """
        db = Database.get_db()
        
        services = list(db.services.find({
            "tenant_id": tenant_id,
            "available_at_locations": location_id,
            "is_active": True
        }))
        
        return [ServiceManagementService._format_service_response(s) for s in services]
    
    @staticmethod
    async def assign_to_location(
        service_id: str,
        tenant_id: str,
        location_id: str,
        location_price: Optional[float] = None,
        location_duration: Optional[int] = None
    ) -> Dict:
        """
        Make a service available at a location.
        
        Args:
            service_id: Service ID
            tenant_id: Tenant ID
            location_id: Location ID
            location_price: Optional location-specific price
            location_duration: Optional location-specific duration
            
        Returns:
            Updated service document
        """
        db = Database.get_db()
        
        # Verify service exists
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise NotFoundException("Service not found")
        
        # Add location to available_at_locations if not already there
        available_at_locations = service.get("available_at_locations", [])
        if location_id not in available_at_locations:
            available_at_locations.append(location_id)
        
        # Add location pricing if provided
        location_pricing = service.get("location_pricing", [])
        
        # Check if location pricing already exists
        location_pricing_exists = any(lp.get("location_id") == location_id for lp in location_pricing)
        
        if not location_pricing_exists:
            pricing_entry = {"location_id": location_id}
            if location_price is not None:
                pricing_entry["price"] = location_price
            if location_duration is not None:
                pricing_entry["duration_minutes"] = location_duration
            location_pricing.append(pricing_entry)
        
        # Update service
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {
                "$set": {
                    "available_at_locations": available_at_locations,
                    "location_pricing": location_pricing,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Assigned service {service_id} to location {location_id}")
        
        # Fetch updated service
        service_doc = db.services.find_one({"_id": ObjectId(service_id)})
        return ServiceManagementService._format_service_response(service_doc)
    
    @staticmethod
    async def remove_from_location(
        service_id: str,
        tenant_id: str,
        location_id: str
    ) -> Dict:
        """
        Remove a service from a location.
        
        Args:
            service_id: Service ID
            tenant_id: Tenant ID
            location_id: Location ID to remove from
            
        Returns:
            Updated service document
        """
        db = Database.get_db()
        
        # Verify service exists
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise NotFoundException("Service not found")
        
        # Remove location from available_at_locations
        available_at_locations = service.get("available_at_locations", [])
        if location_id in available_at_locations:
            available_at_locations.remove(location_id)
        
        # Remove location pricing
        location_pricing = service.get("location_pricing", [])
        location_pricing = [lp for lp in location_pricing if lp.get("location_id") != location_id]
        
        # Update service
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {
                "$set": {
                    "available_at_locations": available_at_locations,
                    "location_pricing": location_pricing,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Removed service {service_id} from location {location_id}")
        
        # Fetch updated service
        service_doc = db.services.find_one({"_id": ObjectId(service_id)})
        return ServiceManagementService._format_service_response(service_doc)
    
    @staticmethod
    async def get_location_pricing(
        service_id: str,
        tenant_id: str,
        location_id: str
    ) -> Dict:
        """
        Get location-specific pricing for a service.
        
        Args:
            service_id: Service ID
            tenant_id: Tenant ID
            location_id: Location ID
            
        Returns:
            Location-specific pricing or default pricing
        """
        db = Database.get_db()
        
        # Verify service exists
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise NotFoundException("Service not found")
        
        # Look for location-specific pricing
        location_pricing = service.get("location_pricing", [])
        for lp in location_pricing:
            if lp.get("location_id") == location_id:
                return {
                    "price": lp.get("price", service.get("price", 0.0)),
                    "duration_minutes": lp.get("duration_minutes", service.get("duration_minutes", 30))
                }
        
        # Return default pricing if no location-specific pricing found
        return {
            "price": service.get("price", 0.0),
            "duration_minutes": service.get("duration_minutes", 30)
        }


# Singleton instance
service_management_service = ServiceManagementService()
