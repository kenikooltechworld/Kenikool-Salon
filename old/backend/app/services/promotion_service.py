"""
Promotion and Special Offers Service - Task 15
"""
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class PromotionService:
    """Service for managing promotions and special offers"""
    
    @staticmethod
    async def create_promotion(
        promotion_data: Dict,
        salon_id: str
    ) -> Dict:
        """Create a new promotion - Requirements: 12"""
        db = Database.get_db()
        
        promotion = {
            "tenant_id": salon_id,
            "name": promotion_data.get("name"),
            "description": promotion_data.get("description"),
            "discount_type": promotion_data.get("discount_type"),  # percentage or fixed
            "discount_value": promotion_data.get("discount_value"),
            "eligible_services": promotion_data.get("eligible_services", []),
            "eligible_stylists": promotion_data.get("eligible_stylists", []),
            "start_date": promotion_data.get("start_date"),
            "end_date": promotion_data.get("end_date"),
            "max_uses": promotion_data.get("max_uses"),
            "current_uses": 0,
            "min_booking_amount": promotion_data.get("min_booking_amount", 0),
            "terms_conditions": promotion_data.get("terms_conditions"),
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.promotions.insert_one(promotion)
        promotion["_id"] = result.inserted_id
        
        logger.info(f"Created promotion: {result.inserted_id}")
        return promotion
    
    @staticmethod
    async def get_active_promotions(salon_id: str) -> List[Dict]:
        """Get all active promotions - Requirements: 12"""
        db = Database.get_db()
        
        now = datetime.utcnow()
        promotions = list(db.promotions.find({
            "tenant_id": salon_id,
            "status": "active",
            "start_date": {"$lte": now},
            "end_date": {"$gte": now}
        }))
        
        return promotions
    
    @staticmethod
    async def get_promotion_by_code(
        promo_code: str,
        salon_id: str
    ) -> Optional[Dict]:
        """Get promotion by code - Requirements: 12"""
        db = Database.get_db()
        
        promotion = db.promo_codes.find_one({
            "code": promo_code,
            "tenant_id": salon_id,
            "status": "active"
        })
        
        return promotion
    
    @staticmethod
    async def validate_promo_code(
        promo_code: str,
        salon_id: str,
        booking_amount: float
    ) -> Dict:
        """Validate promo code and calculate discount - Requirements: 12"""
        db = Database.get_db()
        
        promo = db.promo_codes.find_one({
            "code": promo_code,
            "tenant_id": salon_id,
            "status": "active"
        })
        
        if not promo:
            raise NotFoundException("Promo code not found or expired")
        
        # Check if max uses reached
        if promo.get("max_uses") and promo.get("current_uses", 0) >= promo.get("max_uses"):
            raise BadRequestException("Promo code has reached maximum uses")
        
        # Check minimum booking amount
        if booking_amount < promo.get("min_booking_amount", 0):
            raise BadRequestException(f"Minimum booking amount of {promo.get('min_booking_amount')} required")
        
        # Calculate discount
        discount_type = promo.get("discount_type")
        discount_value = promo.get("discount_value")
        
        if discount_type == "percentage":
            discount_amount = booking_amount * (discount_value / 100)
        else:
            discount_amount = discount_value
        
        return {
            "promo_code": promo_code,
            "discount_type": discount_type,
            "discount_value": discount_value,
            "discount_amount": discount_amount,
            "original_amount": booking_amount,
            "final_amount": booking_amount - discount_amount,
            "valid": True
        }
    
    @staticmethod
    async def apply_promo_code(
        promo_code: str,
        booking_id: str,
        salon_id: str
    ) -> bool:
        """Apply promo code to booking - Requirements: 12"""
        db = Database.get_db()
        
        result = db.promo_codes.update_one(
            {
                "code": promo_code,
                "tenant_id": salon_id
            },
            {
                "$inc": {"current_uses": 1},
                "$push": {"used_bookings": ObjectId(booking_id)}
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def get_promotions_for_service(
        service_id: str,
        salon_id: str
    ) -> List[Dict]:
        """Get promotions applicable to a service - Requirements: 12"""
        db = Database.get_db()
        
        now = datetime.utcnow()
        promotions = list(db.promotions.find({
            "tenant_id": salon_id,
            "status": "active",
            "start_date": {"$lte": now},
            "end_date": {"$gte": now},
            "eligible_services": ObjectId(service_id)
        }))
        
        return promotions
    
    @staticmethod
    async def create_promo_code(
        code_data: Dict,
        salon_id: str
    ) -> Dict:
        """Create a promo code - Requirements: 12"""
        db = Database.get_db()
        
        promo_code = {
            "tenant_id": salon_id,
            "code": code_data.get("code").upper(),
            "promotion_id": ObjectId(code_data.get("promotion_id")),
            "discount_type": code_data.get("discount_type"),
            "discount_value": code_data.get("discount_value"),
            "max_uses": code_data.get("max_uses"),
            "current_uses": 0,
            "min_booking_amount": code_data.get("min_booking_amount", 0),
            "start_date": code_data.get("start_date"),
            "end_date": code_data.get("end_date"),
            "status": "active",
            "used_bookings": [],
            "created_at": datetime.utcnow()
        }
        
        result = db.promo_codes.insert_one(promo_code)
        promo_code["_id"] = result.inserted_id
        
        logger.info(f"Created promo code: {code_data.get('code')}")
        return promo_code


promotion_service = PromotionService()
