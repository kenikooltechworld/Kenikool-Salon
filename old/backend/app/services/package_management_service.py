"""
Service Package Management - Task 16
"""
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class PackageManagementService:
    """Service for managing service packages"""
    
    @staticmethod
    async def create_package(
        package_data: Dict,
        salon_id: str
    ) -> Dict:
        """Create a service package - Requirements: 13"""
        db = Database.get_db()
        
        # Calculate total price and savings
        services = package_data.get("services", [])
        total_individual_price = 0
        service_ids = []
        
        for service_id in services:
            service = db.services.find_one({"_id": ObjectId(service_id)})
            if service:
                total_individual_price += service.get("price", 0)
                service_ids.append(ObjectId(service_id))
        
        package_price = package_data.get("price", total_individual_price)
        savings = total_individual_price - package_price
        
        package = {
            "tenant_id": salon_id,
            "name": package_data.get("name"),
            "description": package_data.get("description"),
            "services": service_ids,
            "individual_price": total_individual_price,
            "package_price": package_price,
            "savings": savings,
            "duration_minutes": package_data.get("duration_minutes"),
            "max_uses": package_data.get("max_uses"),
            "current_uses": 0,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.packages.insert_one(package)
        package["_id"] = result.inserted_id
        
        logger.info(f"Created package: {result.inserted_id}")
        return package
    
    @staticmethod
    async def get_packages(
        salon_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict]:
        """Get all packages - Requirements: 13"""
        db = Database.get_db()
        
        packages = list(db.packages.find({
            "tenant_id": salon_id,
            "status": "active"
        }).skip(skip).limit(limit))
        
        return packages
    
    @staticmethod
    async def get_package(
        package_id: str,
        salon_id: str
    ) -> Optional[Dict]:
        """Get a specific package - Requirements: 13"""
        db = Database.get_db()
        
        package = db.packages.find_one({
            "_id": ObjectId(package_id),
            "tenant_id": salon_id
        })
        
        return package
    
    @staticmethod
    async def create_package_booking(
        package_id: str,
        booking_data: Dict,
        salon_id: str
    ) -> Dict:
        """Create booking for service package - Requirements: 13"""
        db = Database.get_db()
        
        package = db.packages.find_one({
            "_id": ObjectId(package_id),
            "tenant_id": salon_id
        })
        
        if not package:
            raise NotFoundException("Package not found")
        
        # Create individual bookings for each service in package
        bookings = []
        service_bookings = booking_data.get("service_bookings", [])
        
        for service_booking in service_bookings:
            booking = {
                "package_id": ObjectId(package_id),
                "service_id": ObjectId(service_booking.get("service_id")),
                "stylist_id": ObjectId(service_booking.get("stylist_id")),
                "booking_date": service_booking.get("booking_date"),
                "guest_email": booking_data.get("guest_email"),
                "guest_name": booking_data.get("guest_name"),
                "guest_phone": booking_data.get("guest_phone"),
                "status": "pending",
                "payment_status": "pending",
                "price": 0,  # Price covered by package
                "tenant_id": salon_id,
                "created_at": datetime.utcnow()
            }
            
            result = db.bookings.insert_one(booking)
            booking["_id"] = result.inserted_id
            bookings.append(booking)
        
        # Update package usage
        db.packages.update_one(
            {"_id": ObjectId(package_id)},
            {"$inc": {"current_uses": 1}}
        )
        
        logger.info(f"Created package booking with {len(bookings)} services")
        
        return {
            "package_id": package_id,
            "booking_count": len(bookings),
            "total_price": package.get("package_price"),
            "savings": package.get("savings"),
            "bookings": bookings
        }
    
    @staticmethod
    async def modify_package_booking(
        package_booking_id: str,
        modifications: Dict,
        salon_id: str
    ) -> Dict:
        """Modify package booking (add/remove services) - Requirements: 13"""
        db = Database.get_db()
        
        # Get original package booking
        original_booking = db.bookings.find_one({
            "_id": ObjectId(package_booking_id),
            "tenant_id": salon_id
        })
        
        if not original_booking:
            raise NotFoundException("Package booking not found")
        
        # Handle service additions/removals
        services_to_add = modifications.get("add_services", [])
        services_to_remove = modifications.get("remove_services", [])
        
        new_bookings = []
        
        for service_id in services_to_add:
            booking = {
                "package_id": original_booking.get("package_id"),
                "service_id": ObjectId(service_id),
                "stylist_id": ObjectId(modifications.get("stylist_id")),
                "booking_date": modifications.get("booking_date"),
                "guest_email": original_booking.get("guest_email"),
                "status": "pending",
                "payment_status": "pending",
                "tenant_id": salon_id,
                "created_at": datetime.utcnow()
            }
            
            result = db.bookings.insert_one(booking)
            new_bookings.append(result.inserted_id)
        
        # Remove services
        for service_id in services_to_remove:
            db.bookings.delete_one({
                "package_id": original_booking.get("package_id"),
                "service_id": ObjectId(service_id)
            })
        
        return {
            "package_booking_id": package_booking_id,
            "added_services": len(services_to_add),
            "removed_services": len(services_to_remove),
            "new_bookings": [str(b) for b in new_bookings]
        }


package_management_service = PackageManagementService()
