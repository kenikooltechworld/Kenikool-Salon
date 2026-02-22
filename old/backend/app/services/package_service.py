"""
Package service - Business logic for service package management
"""
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class PackageService:
    """Service layer for package management"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_packages(
        self,
        tenant_id: str,
        is_active: Optional[bool] = None
    ) -> Dict:
        """Get list of packages"""
        try:
            # Build query
            query = {"tenant_id": tenant_id}
            
            if is_active is not None:
                query["is_active"] = is_active
            
            # Get total count
            total = self.db.packages.count_documents(query)
            
            # Get packages
            cursor = self.db.packages.find(query).sort("created_at", -1)
            packages = list(cursor)
            
            # Convert ObjectId to string
            for package in packages:
                package["_id"] = str(package["_id"])
            
            return {
                "packages": packages,
                "total": total
            }
        
        except Exception as e:
            logger.error(f"Error getting packages: {e}")
            raise Exception(f"Failed to get packages: {str(e)}")
    
    async def create_package(
        self,
        tenant_id: str,
        name: str,
        description: Optional[str],
        services: List[Dict],
        original_price: float,
        package_price: float,
        discount_percentage: float,
        validity_days: Optional[int],
        is_active: bool,
        is_transferable: bool,
        is_giftable: bool,
        restrictions: Optional[Dict],
        valid_from: Optional[datetime],
        valid_until: Optional[datetime],
        max_redemptions: Optional[int]
    ) -> Dict:
        """Create a new service package"""
        try:
            # Validate services exist and quantities are positive
            service_ids = []
            for service_item in services:
                service_id = service_item.get("service_id")
                quantity = service_item.get("quantity", 1)
                
                if quantity <= 0:
                    raise ValueError(f"Service quantity must be positive, got {quantity}")
                
                service = self.db.services.find_one({
                    "_id": ObjectId(service_id),
                    "tenant_id": tenant_id
                })
                if not service:
                    raise ValueError(f"Service {service_id} not found")
                
                service_ids.append(service_id)
            
            # Validate pricing
            if package_price >= original_price:
                raise ValueError("Package price must be less than original price")
            
            # Create package
            package_data = {
                "tenant_id": tenant_id,
                "name": name,
                "description": description,
                "services": services,
                "original_price": original_price,
                "package_price": package_price,
                "discount_percentage": discount_percentage,
                "validity_days": validity_days,
                "is_active": is_active,
                "is_transferable": is_transferable,
                "is_giftable": is_giftable,
                "restrictions": restrictions,
                "valid_from": valid_from,
                "valid_until": valid_until,
                "max_redemptions": max_redemptions,
                "current_redemptions": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.packages.insert_one(package_data)
            package_data["_id"] = str(result.inserted_id)
            
            return package_data
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error creating package: {e}")
            raise Exception(f"Failed to create package: {str(e)}")
    
    async def update_package(
        self,
        package_id: str,
        tenant_id: str,
        update_data: Dict
    ) -> Dict:
        """Update a package"""
        try:
            # Find package
            package = self.db.packages.find_one({
                "_id": ObjectId(package_id),
                "tenant_id": tenant_id
            })
            
            if not package:
                raise ValueError("Package not found")
            
            # Validate services if provided
            if "services" in update_data:
                for service_item in update_data["services"]:
                    service_id = service_item.get("service_id")
                    quantity = service_item.get("quantity", 1)
                    
                    if quantity <= 0:
                        raise ValueError(f"Service quantity must be positive, got {quantity}")
                    
                    service = self.db.services.find_one({
                        "_id": ObjectId(service_id),
                        "tenant_id": tenant_id
                    })
                    if not service:
                        raise ValueError(f"Service {service_id} not found")
            
            # Validate pricing if provided
            original_price = update_data.get("original_price", package.get("original_price"))
            package_price = update_data.get("package_price", package.get("package_price"))
            
            if package_price >= original_price:
                raise ValueError("Package price must be less than original price")
            
            # Update package
            update_data["updated_at"] = datetime.utcnow()
            
            self.db.packages.update_one(
                {"_id": ObjectId(package_id)},
                {"$set": update_data}
            )
            
            # Get updated package
            updated_package = self.db.packages.find_one({"_id": ObjectId(package_id)})
            updated_package["_id"] = str(updated_package["_id"])
            
            return updated_package
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error updating package: {e}")
            raise Exception(f"Failed to update package: {str(e)}")
    
    async def delete_package(
        self,
        package_id: str,
        tenant_id: str
    ) -> bool:
        """Delete a package"""
        try:
            # Find package
            package = self.db.packages.find_one({
                "_id": ObjectId(package_id),
                "tenant_id": tenant_id
            })
            
            if not package:
                raise ValueError("Package not found")
            
            # Soft delete by marking as inactive
            self.db.packages.update_one(
                {"_id": ObjectId(package_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return True
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error deleting package: {e}")
            raise Exception(f"Failed to delete package: {str(e)}")
    
    async def create_package_booking(
        self,
        package_id: str,
        tenant_id: str,
        client_id: str,
        stylist_id: str,
        booking_dates: List[Dict]
    ) -> Dict:
        """Create booking for package services"""
        try:
            # Find package
            package = self.db.packages.find_one({
                "_id": ObjectId(package_id),
                "tenant_id": tenant_id,
                "is_active": True
            })
            
            if not package:
                raise ValueError("Package not found")
            
            # Check validity period
            now = datetime.utcnow()
            if package.get("valid_from") and now < package["valid_from"]:
                raise ValueError("Package not yet valid")
            
            if package.get("valid_until") and now > package["valid_until"]:
                raise ValueError("Package has expired")
            
            # Check max redemptions
            if package.get("max_redemptions") and package["current_redemptions"] >= package["max_redemptions"]:
                raise ValueError("Package has reached maximum redemptions")
            
            # Create bookings for each service in package
            bookings = []
            total_price = 0
            booking_idx = 0
            
            for service_item in package.get("services", []):
                service_id = service_item.get("service_id")
                quantity = service_item.get("quantity", 1)
                
                # Create booking for each quantity
                for _ in range(quantity):
                    if booking_idx < len(booking_dates):
                        booking_date = booking_dates[booking_idx]
                    else:
                        raise ValueError("Not enough booking dates provided")
                    
                    service = self.db.services.find_one({"_id": ObjectId(service_id)})
                    if not service:
                        continue
                    
                    booking = {
                        "package_id": ObjectId(package_id),
                        "client_id": ObjectId(client_id),
                        "service_id": ObjectId(service_id),
                        "stylist_id": ObjectId(stylist_id),
                        "booking_date": booking_date.get("date"),
                        "booking_time": booking_date.get("time"),
                        "status": "confirmed",
                        "price": service.get("price", 0),
                        "tenant_id": tenant_id,
                        "created_at": datetime.utcnow()
                    }
                    
                    result = self.db.bookings.insert_one(booking)
                    booking["_id"] = str(result.inserted_id)
                    bookings.append(booking)
                    total_price += booking["price"]
                    booking_idx += 1
            
            # Update package redemptions
            self.db.packages.update_one(
                {"_id": ObjectId(package_id)},
                {"$inc": {"current_redemptions": 1}}
            )
            
            return {
                "package_id": package_id,
                "bookings": bookings,
                "total_price": package["package_price"],
                "original_price": package["original_price"],
                "savings": package["original_price"] - package["package_price"]
            }
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error creating package booking: {e}")
            raise Exception(f"Failed to create package booking: {str(e)}")
