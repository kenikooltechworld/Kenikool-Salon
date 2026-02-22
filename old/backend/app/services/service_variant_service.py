"""
Service Variant Service
Handles service variant management
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class ServiceVariantService:
    """Service for managing service variants"""

    def __init__(self, db):
        self.db = db
        self.collection = db.service_variants
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create indexes for efficient querying"""
        try:
            # Index for querying by service
            self.collection.create_index([("service_id", 1), ("tenant_id", 1)])
            # Index for querying by tenant
            self.collection.create_index("tenant_id")
            logger.info("Service variant indexes created")
        except Exception as e:
            logger.error(f"Failed to create service variant indexes: {e}")

    def create_variant(
        self,
        service_id: str,
        tenant_id: str,
        name: str,
        description: Optional[str],
        price_adjustment: float,
        price_adjustment_type: str,
        duration_adjustment: int,
        is_active: bool,
        base_price: float,
        base_duration: int,
    ) -> Dict:
        """
        Create a service variant
        
        Requirements: 3.1, 3.2, 3.6
        """
        # Validate adjustment type
        if price_adjustment_type not in ["fixed", "percentage"]:
            raise BadRequestException("Invalid price_adjustment_type. Must be 'fixed' or 'percentage'")

        # Calculate final price
        if price_adjustment_type == "fixed":
            final_price = base_price + price_adjustment
        else:  # percentage
            final_price = base_price * (1 + price_adjustment / 100)

        # Ensure final price is not negative
        if final_price < 0:
            raise BadRequestException("Final price cannot be negative")

        # Calculate final duration
        final_duration = base_duration + duration_adjustment
        if final_duration <= 0:
            raise BadRequestException("Final duration must be positive")

        variant_data = {
            "service_id": service_id,
            "tenant_id": tenant_id,
            "name": name,
            "description": description,
            "price_adjustment": price_adjustment,
            "price_adjustment_type": price_adjustment_type,
            "duration_adjustment": duration_adjustment,
            "final_price": final_price,
            "final_duration": final_duration,
            "is_active": is_active,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = self.collection.insert_one(variant_data)
        variant_id = str(result.inserted_id)

        logger.info(f"Service variant created: {variant_id} for service: {service_id}")

        return self._format_variant_response(
            self.collection.find_one({"_id": ObjectId(variant_id)})
        )

    def get_variants(self, service_id: str, tenant_id: str) -> List[Dict]:
        """
        Get all variants for a service
        
        Requirements: 3.3
        """
        variants = list(
            self.collection.find({"service_id": service_id, "tenant_id": tenant_id})
        )

        return [self._format_variant_response(v) for v in variants]

    def get_variant(self, variant_id: str, tenant_id: str) -> Dict:
        """Get a single variant by ID"""
        variant = self.collection.find_one(
            {"_id": ObjectId(variant_id), "tenant_id": tenant_id}
        )

        if not variant:
            raise NotFoundException("Variant not found")

        return self._format_variant_response(variant)

    def update_variant(
        self,
        variant_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price_adjustment: Optional[float] = None,
        price_adjustment_type: Optional[str] = None,
        duration_adjustment: Optional[int] = None,
        is_active: Optional[bool] = None,
        base_price: Optional[float] = None,
        base_duration: Optional[int] = None,
    ) -> Dict:
        """
        Update a service variant
        
        Requirements: 3.4, 3.6
        """
        variant = self.collection.find_one(
            {"_id": ObjectId(variant_id), "tenant_id": tenant_id}
        )

        if not variant:
            raise NotFoundException("Variant not found")

        update_data = {"updated_at": datetime.utcnow()}

        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if is_active is not None:
            update_data["is_active"] = is_active

        # Handle price adjustment updates
        current_price_adjustment = variant.get("price_adjustment", 0)
        current_price_type = variant.get("price_adjustment_type", "fixed")
        current_duration_adjustment = variant.get("duration_adjustment", 0)

        if price_adjustment is not None:
            current_price_adjustment = price_adjustment
            update_data["price_adjustment"] = price_adjustment

        if price_adjustment_type is not None:
            if price_adjustment_type not in ["fixed", "percentage"]:
                raise BadRequestException("Invalid price_adjustment_type")
            current_price_type = price_adjustment_type
            update_data["price_adjustment_type"] = price_adjustment_type

        if duration_adjustment is not None:
            current_duration_adjustment = duration_adjustment
            update_data["duration_adjustment"] = duration_adjustment

        # Recalculate final price and duration if needed
        if any(
            x is not None
            for x in [price_adjustment, price_adjustment_type, base_price]
        ):
            if base_price is None:
                # Get service to get base price
                service = self.db.services.find_one(
                    {"_id": ObjectId(variant["service_id"])}
                )
                base_price = service.get("price", 0)

            if current_price_type == "fixed":
                final_price = base_price + current_price_adjustment
            else:
                final_price = base_price * (1 + current_price_adjustment / 100)

            if final_price < 0:
                raise BadRequestException("Final price cannot be negative")

            update_data["final_price"] = final_price

        if duration_adjustment is not None or base_duration is not None:
            if base_duration is None:
                # Get service to get base duration
                service = self.db.services.find_one(
                    {"_id": ObjectId(variant["service_id"])}
                )
                base_duration = service.get("duration_minutes", 30)

            final_duration = base_duration + current_duration_adjustment
            if final_duration <= 0:
                raise BadRequestException("Final duration must be positive")

            update_data["final_duration"] = final_duration

        self.collection.update_one(
            {"_id": ObjectId(variant_id)}, {"$set": update_data}
        )

        logger.info(f"Service variant updated: {variant_id}")

        return self._format_variant_response(
            self.collection.find_one({"_id": ObjectId(variant_id)})
        )

    def delete_variant(self, variant_id: str, tenant_id: str) -> bool:
        """
        Delete a service variant
        
        Requirements: 3.5
        """
        result = self.collection.delete_one(
            {"_id": ObjectId(variant_id), "tenant_id": tenant_id}
        )

        if result.deleted_count == 0:
            raise NotFoundException("Variant not found")

        logger.info(f"Service variant deleted: {variant_id}")
        return True

    def _format_variant_response(self, variant: Dict) -> Dict:
        """Format variant document for response"""
        return {
            "id": str(variant["_id"]),
            "service_id": variant["service_id"],
            "tenant_id": variant["tenant_id"],
            "name": variant["name"],
            "description": variant.get("description"),
            "price_adjustment": variant.get("price_adjustment", 0),
            "price_adjustment_type": variant.get("price_adjustment_type", "fixed"),
            "duration_adjustment": variant.get("duration_adjustment", 0),
            "final_price": variant.get("final_price", 0),
            "final_duration": variant.get("final_duration", 30),
            "is_active": variant.get("is_active", True),
            "created_at": variant.get("created_at", datetime.utcnow()),
            "updated_at": variant.get("updated_at", datetime.utcnow()),
        }


# Singleton instance
service_variant_service = None


def get_service_variant_service(db):
    """Get or create service variant service instance"""
    global service_variant_service
    if service_variant_service is None:
        service_variant_service = ServiceVariantService(db)
    return service_variant_service
