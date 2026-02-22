"""
Service Package Service
Handles service package management
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class ServicePackageService:
    """Service for managing service packages"""

    def __init__(self, db):
        self.db = db
        self.collection = db.service_packages
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create indexes for efficient querying"""
        try:
            # Index for querying by tenant
            self.collection.create_index("tenant_id")
            # Index for active packages
            self.collection.create_index([("tenant_id", 1), ("is_active", 1)])
            # Index for validity dates
            self.collection.create_index([("tenant_id", 1), ("valid_until", 1)])
            logger.info("Service package indexes created")
        except Exception as e:
            logger.error(f"Failed to create service package indexes: {e}")

    def create_package(
        self,
        tenant_id: str,
        name: str,
        description: Optional[str],
        service_ids: List[str],
        package_price: float,
        valid_from: Optional[datetime],
        valid_until: Optional[datetime],
        is_active: bool,
    ) -> Dict:
        """
        Create a service package
        
        Requirements: 5.1, 5.2, 5.7
        """
        # Validate at least 2 services
        if len(service_ids) < 2:
            raise BadRequestException("Package must contain at least 2 services")
        
        # Validate services exist and belong to tenant
        services = []
        total_service_price = 0.0
        
        for service_id in service_ids:
            service = self.db.services.find_one({
                "_id": ObjectId(service_id),
                "tenant_id": tenant_id
            })
            
            if not service:
                raise NotFoundException(f"Service {service_id} not found")
            
            services.append(service)
            total_service_price += service.get("price", 0.0)
        
        # Validate package price is less than sum of services
        if package_price >= total_service_price:
            raise BadRequestException(
                f"Package price (₦{package_price}) must be less than total service price (₦{total_service_price})"
            )
        
        # Validate date range
        if valid_from and valid_until and valid_from >= valid_until:
            raise BadRequestException("valid_from must be before valid_until")
        
        # Calculate savings
        savings = total_service_price - package_price
        savings_percentage = (savings / total_service_price) * 100 if total_service_price > 0 else 0
        
        package_data = {
            "tenant_id": tenant_id,
            "name": name,
            "description": description,
            "service_ids": service_ids,
            "package_price": package_price,
            "total_service_price": total_service_price,
            "savings": savings,
            "savings_percentage": savings_percentage,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "is_active": is_active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = self.collection.insert_one(package_data)
        package_id = str(result.inserted_id)

        logger.info(f"Service package created: {package_id} for tenant: {tenant_id}")

        return self._format_package_response(
            self.collection.find_one({"_id": ObjectId(package_id)})
        )

    def get_packages(
        self,
        tenant_id: str,
        is_active: Optional[bool] = None,
        include_expired: bool = False
    ) -> List[Dict]:
        """
        Get all packages for a tenant
        
        Requirements: 5.3
        """
        query = {"tenant_id": tenant_id}
        
        if is_active is not None:
            query["is_active"] = is_active
        
        # Filter out expired packages unless explicitly requested
        if not include_expired:
            now = datetime.utcnow()
            query["$or"] = [
                {"valid_until": None},
                {"valid_until": {"$gte": now}}
            ]
        
        packages = list(self.collection.find(query).sort("created_at", -1))

        return [self._format_package_response(p) for p in packages]

    def get_package(self, package_id: str, tenant_id: str) -> Dict:
        """
        Get a single package by ID
        
        Requirements: 5.4
        """
        package = self.collection.find_one(
            {"_id": ObjectId(package_id), "tenant_id": tenant_id}
        )

        if not package:
            raise NotFoundException("Package not found")

        return self._format_package_response(package)

    def update_package(
        self,
        package_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        service_ids: Optional[List[str]] = None,
        package_price: Optional[float] = None,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        is_active: Optional[bool] = None,
    ) -> Dict:
        """
        Update a service package
        
        Requirements: 5.5, 5.7
        """
        package = self.collection.find_one(
            {"_id": ObjectId(package_id), "tenant_id": tenant_id}
        )

        if not package:
            raise NotFoundException("Package not found")

        update_data = {"updated_at": datetime.utcnow()}

        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if is_active is not None:
            update_data["is_active"] = is_active
        if valid_from is not None:
            update_data["valid_from"] = valid_from
        if valid_until is not None:
            update_data["valid_until"] = valid_until

        # Handle service_ids and package_price updates
        current_service_ids = package.get("service_ids", [])
        current_package_price = package.get("package_price", 0)

        if service_ids is not None:
            current_service_ids = service_ids
            update_data["service_ids"] = service_ids

        if package_price is not None:
            current_package_price = package_price
            update_data["package_price"] = package_price

        # Recalculate total service price and savings if services or price changed
        if service_ids is not None or package_price is not None:
            total_service_price = 0.0
            
            for service_id in current_service_ids:
                service = self.db.services.find_one({
                    "_id": ObjectId(service_id),
                    "tenant_id": tenant_id
                })
                
                if not service:
                    raise NotFoundException(f"Service {service_id} not found")
                
                total_service_price += service.get("price", 0.0)
            
            # Validate package price
            if current_package_price >= total_service_price:
                raise BadRequestException(
                    f"Package price (₦{current_package_price}) must be less than total service price (₦{total_service_price})"
                )
            
            savings = total_service_price - current_package_price
            savings_percentage = (savings / total_service_price) * 100 if total_service_price > 0 else 0
            
            update_data["total_service_price"] = total_service_price
            update_data["savings"] = savings
            update_data["savings_percentage"] = savings_percentage

        # Validate date range
        final_valid_from = valid_from if valid_from is not None else package.get("valid_from")
        final_valid_until = valid_until if valid_until is not None else package.get("valid_until")
        
        if final_valid_from and final_valid_until and final_valid_from >= final_valid_until:
            raise BadRequestException("valid_from must be before valid_until")

        self.collection.update_one(
            {"_id": ObjectId(package_id)}, {"$set": update_data}
        )

        logger.info(f"Service package updated: {package_id}")

        return self._format_package_response(
            self.collection.find_one({"_id": ObjectId(package_id)})
        )

    def delete_package(self, package_id: str, tenant_id: str) -> bool:
        """
        Delete a service package
        
        Requirements: 5.6
        """
        result = self.collection.delete_one(
            {"_id": ObjectId(package_id), "tenant_id": tenant_id}
        )

        if result.deleted_count == 0:
            raise NotFoundException("Package not found")

        logger.info(f"Service package deleted: {package_id}")
        return True

    def is_package_valid(self, package_id: str, tenant_id: str) -> bool:
        """
        Check if a package is currently valid
        
        Requirements: 5.7
        """
        package = self.collection.find_one(
            {"_id": ObjectId(package_id), "tenant_id": tenant_id}
        )

        if not package:
            return False

        if not package.get("is_active", False):
            return False

        now = datetime.utcnow()
        
        valid_from = package.get("valid_from")
        if valid_from and now < valid_from:
            return False
        
        valid_until = package.get("valid_until")
        if valid_until and now > valid_until:
            return False

        return True

    def _format_package_response(self, package: Dict) -> Dict:
        """Format package document for response"""
        return {
            "id": str(package["_id"]),
            "tenant_id": package["tenant_id"],
            "name": package["name"],
            "description": package.get("description"),
            "service_ids": package.get("service_ids", []),
            "package_price": package.get("package_price", 0),
            "total_service_price": package.get("total_service_price", 0),
            "savings": package.get("savings", 0),
            "savings_percentage": package.get("savings_percentage", 0),
            "valid_from": package.get("valid_from"),
            "valid_until": package.get("valid_until"),
            "is_active": package.get("is_active", True),
            "created_at": package.get("created_at", datetime.utcnow()),
            "updated_at": package.get("updated_at", datetime.utcnow()),
        }


# Singleton instance
service_package_service = None


def get_service_package_service(db):
    """Get or create service package service instance"""
    global service_package_service
    if service_package_service is None:
        service_package_service = ServicePackageService(db)
    return service_package_service
