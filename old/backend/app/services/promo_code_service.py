"""
Promo code service - Business logic for promo code management
"""
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class PromoCodeService:
    """Service layer for promo code management"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_promo_codes(
        self,
        tenant_id: str,
        is_active: Optional[bool] = None
    ) -> Dict:
        """Get list of promo codes"""
        try:
            # Build query
            query = {"tenant_id": tenant_id}
            
            if is_active is not None:
                query["is_active"] = is_active
            
            # Get total count
            total = self.db.promo_codes.count_documents(query)
            
            # Get promo codes
            cursor = self.db.promo_codes.find(query).sort("created_at", -1)
            promo_codes = list(cursor)
            
            # Convert ObjectId to string
            for promo_code in promo_codes:
                promo_code["_id"] = str(promo_code["_id"])
            
            return {
                "promo_codes": promo_codes,
                "total": total
            }
        
        except Exception as e:
            logger.error(f"Error getting promo codes: {e}")
            raise Exception(f"Failed to get promo codes: {str(e)}")
    
    async def create_promo_code(
        self,
        tenant_id: str,
        code: str,
        description: Optional[str],
        discount_type: str,
        discount_value: float,
        min_purchase_amount: Optional[float],
        max_discount_amount: Optional[float],
        is_active: bool,
        valid_from: Optional[datetime],
        valid_until: Optional[datetime],
        max_uses: Optional[int],
        max_uses_per_client: Optional[int],
        applicable_services: List[str]
    ) -> Dict:
        """Create a new promo code"""
        try:
            # Uppercase the code
            code = code.upper()
            
            # Check if code already exists
            existing = self.db.promo_codes.find_one({
                "tenant_id": tenant_id,
                "code": code
            })
            
            if existing:
                raise ValueError("Promo code already exists")
            
            # Validate services if provided
            if applicable_services:
                for service_id in applicable_services:
                    service = self.db.services.find_one({
                        "_id": ObjectId(service_id),
                        "tenant_id": tenant_id
                    })
                    if not service:
                        raise ValueError(f"Service {service_id} not found")
            
            # Create promo code
            promo_code_data = {
                "tenant_id": tenant_id,
                "code": code,
                "description": description,
                "discount_type": discount_type,
                "discount_value": discount_value,
                "min_purchase_amount": min_purchase_amount,
                "max_discount_amount": max_discount_amount,
                "is_active": is_active,
                "valid_from": valid_from,
                "valid_until": valid_until,
                "max_uses": max_uses,
                "max_uses_per_client": max_uses_per_client,
                "applicable_services": applicable_services,
                "current_uses": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.promo_codes.insert_one(promo_code_data)
            promo_code_data["_id"] = str(result.inserted_id)
            
            return promo_code_data
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error creating promo code: {e}")
            raise Exception(f"Failed to create promo code: {str(e)}")
    
    async def validate_promo_code(
        self,
        tenant_id: str,
        code: str,
        client_id: str,
        service_ids: List[str],
        total_amount: float
    ) -> Dict:
        """Validate a promo code and calculate discount"""
        try:
            # Find promo code
            promo = self.db.promo_codes.find_one({
                "tenant_id": tenant_id,
                "code": code.upper(),
                "is_active": True
            })
            
            if not promo:
                return {
                    "valid": False,
                    "error": "Invalid promo code"
                }
            
            # Check validity period
            now = datetime.utcnow()
            if promo.get("valid_from") and now < promo["valid_from"]:
                return {
                    "valid": False,
                    "error": "Promo code not yet valid"
                }
            
            if promo.get("valid_until") and now > promo["valid_until"]:
                return {
                    "valid": False,
                    "error": "Promo code has expired"
                }
            
            # Check max uses
            if promo.get("max_uses") and promo["current_uses"] >= promo["max_uses"]:
                return {
                    "valid": False,
                    "error": "Promo code has reached maximum uses"
                }
            
            # Check per-client usage
            if promo.get("max_uses_per_client"):
                client_uses = self.db.promo_code_usage.count_documents({
                    "promo_code_id": str(promo["_id"]),
                    "client_id": client_id
                })
                
                if client_uses >= promo["max_uses_per_client"]:
                    return {
                        "valid": False,
                        "error": "You have already used this promo code"
                    }
            
            # Check minimum purchase amount
            if promo.get("min_purchase_amount") and total_amount < promo["min_purchase_amount"]:
                return {
                    "valid": False,
                    "error": f"Minimum purchase amount is ${promo['min_purchase_amount']:.2f}"
                }
            
            # Check applicable services
            if promo.get("applicable_services"):
                applicable = set(promo["applicable_services"])
                requested = set(service_ids)
                
                if not requested.intersection(applicable):
                    return {
                        "valid": False,
                        "error": "Promo code not applicable to selected services"
                    }
            
            # Calculate discount
            if promo["discount_type"] == "percentage":
                discount = total_amount * (promo["discount_value"] / 100)
            else:  # fixed
                discount = promo["discount_value"]
            
            # Apply max discount cap
            if promo.get("max_discount_amount"):
                discount = min(discount, promo["max_discount_amount"])
            
            # Ensure discount doesn't exceed total
            discount = min(discount, total_amount)
            
            return {
                "valid": True,
                "promo_code_id": str(promo["_id"]),
                "code": promo["code"],
                "discount_amount": round(discount, 2),
                "final_amount": round(total_amount - discount, 2)
            }
        
        except Exception as e:
            logger.error(f"Error validating promo code: {e}")
            return {
                "valid": False,
                "error": "Error validating promo code"
            }
    
    async def update_promo_code(
        self,
        promo_code_id: str,
        tenant_id: str,
        update_data: Dict
    ) -> Dict:
        """Update a promo code"""
        try:
            # Find promo code
            promo_code = self.db.promo_codes.find_one({
                "_id": ObjectId(promo_code_id),
                "tenant_id": tenant_id
            })
            
            if not promo_code:
                raise ValueError("Promo code not found")
            
            # Uppercase code if provided
            if "code" in update_data:
                update_data["code"] = update_data["code"].upper()
                
                # Check if new code already exists
                existing = self.db.promo_codes.find_one({
                    "tenant_id": tenant_id,
                    "code": update_data["code"],
                    "_id": {"$ne": ObjectId(promo_code_id)}
                })
                
                if existing:
                    raise ValueError("Promo code already exists")
            
            # Validate services if provided
            if "applicable_services" in update_data and update_data["applicable_services"]:
                for service_id in update_data["applicable_services"]:
                    service = self.db.services.find_one({
                        "_id": ObjectId(service_id),
                        "tenant_id": tenant_id
                    })
                    if not service:
                        raise ValueError(f"Service {service_id} not found")
            
            # Update promo code
            update_data["updated_at"] = datetime.utcnow()
            
            self.db.promo_codes.update_one(
                {"_id": ObjectId(promo_code_id)},
                {"$set": update_data}
            )
            
            # Get updated promo code
            updated_promo_code = self.db.promo_codes.find_one({"_id": ObjectId(promo_code_id)})
            updated_promo_code["_id"] = str(updated_promo_code["_id"])
            
            return updated_promo_code
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error updating promo code: {e}")
            raise Exception(f"Failed to update promo code: {str(e)}")
    
    async def delete_promo_code(
        self,
        promo_code_id: str,
        tenant_id: str
    ) -> bool:
        """Delete a promo code"""
        try:
            # Find promo code
            promo_code = self.db.promo_codes.find_one({
                "_id": ObjectId(promo_code_id),
                "tenant_id": tenant_id
            })
            
            if not promo_code:
                raise ValueError("Promo code not found")
            
            # Soft delete by marking as inactive
            self.db.promo_codes.update_one(
                {"_id": ObjectId(promo_code_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return True
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error deleting promo code: {e}")
            raise Exception(f"Failed to delete promo code: {str(e)}")
