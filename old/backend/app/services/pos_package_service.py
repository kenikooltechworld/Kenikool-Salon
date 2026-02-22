"""
POS Package Service - Integration of package credits with POS system
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.services.service_credit_service import ServiceCreditService
from app.services.redemption_validation_service import RedemptionValidationService

logger = logging.getLogger(__name__)


class POSPackageService:
    """Service for managing package credit redemptions at POS"""
    
    def __init__(self, db):
        self.db = db
        self.credit_service = ServiceCreditService(db)
        self.validation_service = RedemptionValidationService(db)
    
    async def get_client_packages(
        self,
        client_id: str,
        include_expired: bool = False
    ) -> List[Dict]:
        """Get all active packages for a client at POS"""
        try:
            query = {
                "client_id": client_id,
                "status": {"$in": ["active", "fully_redeemed"]}
            }
            
            if not include_expired:
                query["$or"] = [
                    {"expiration_date": None},
                    {"expiration_date": {"$gte": datetime.utcnow()}}
                ]
            
            purchases = list(self.db.package_purchases.find(query))
            
            # Enrich with credit information
            for purchase in purchases:
                purchase["_id"] = str(purchase["_id"])
                
                # Get credit balance
                credits = list(self.db.service_credits.find({
                    "purchase_id": str(purchase["_id"])
                }))
                
                credit_balance = {}
                total_remaining = 0
                
                for credit in credits:
                    service_id = credit.get("service_id")
                    remaining = credit.get("remaining_quantity", 0)
                    
                    credit_balance[service_id] = {
                        "service_name": credit.get("service_name", ""),
                        "remaining": remaining,
                        "initial": credit.get("initial_quantity", 0)
                    }
                    
                    total_remaining += remaining
                
                purchase["credit_balance"] = credit_balance
                purchase["total_remaining_credits"] = total_remaining
            
            return purchases
        
        except Exception as e:
            logger.error(f"Error getting client packages: {e}")
            raise Exception(f"Failed to get client packages: {str(e)}")
    
    async def check_package_credits_for_service(
        self,
        client_id: str,
        service_id: str
    ) -> List[Dict]:
        """Check which packages have available credits for a specific service"""
        try:
            # Get all active packages for client
            packages = await self.get_client_packages(client_id)
            
            # Filter packages that have credits for this service
            packages_with_credits = []
            
            for package in packages:
                if service_id in package.get("credit_balance", {}):
                    credit_info = package["credit_balance"][service_id]
                    if credit_info["remaining"] > 0:
                        packages_with_credits.append({
                            "purchase_id": package["_id"],
                            "package_definition_id": package.get("package_definition_id"),
                            "service_id": service_id,
                            "remaining_credits": credit_info["remaining"],
                            "expiration_date": package.get("expiration_date"),
                            "days_remaining": self._calculate_days_remaining(package.get("expiration_date"))
                        })
            
            return packages_with_credits
        
        except Exception as e:
            logger.error(f"Error checking package credits: {e}")
            raise Exception(f"Failed to check package credits: {str(e)}")
    
    async def validate_pos_redemption(
        self,
        purchase_id: str,
        service_id: str,
        client_id: str,
        stylist_id: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> Dict:
        """Validate if a package credit can be redeemed at POS"""
        try:
            # Use redemption validation service
            validation_result = await self.validation_service.validate_redemption(
                purchase_id=purchase_id,
                service_id=service_id,
                client_id=client_id,
                stylist_id=stylist_id,
                location_id=location_id,
                redemption_date=datetime.utcnow()
            )
            
            return validation_result
        
        except Exception as e:
            logger.error(f"Error validating POS redemption: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}",
                "error_code": "VALIDATION_ERROR"
            }
    
    async def redeem_package_credit_at_pos(
        self,
        purchase_id: str,
        service_id: str,
        client_id: str,
        staff_id: str,
        pos_transaction_id: str,
        quantity: int = 1,
        stylist_id: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> Dict:
        """Redeem a package credit at POS"""
        try:
            # Validate redemption first
            validation_result = await self.validate_pos_redemption(
                purchase_id=purchase_id,
                service_id=service_id,
                client_id=client_id,
                stylist_id=stylist_id,
                location_id=location_id
            )
            
            if not validation_result["valid"]:
                raise ValueError(validation_result.get("error", "Redemption validation failed"))
            
            # Get credit
            credit = self.db.service_credits.find_one({
                "purchase_id": purchase_id,
                "service_id": service_id,
                "remaining_quantity": {"$gte": quantity}
            })
            
            if not credit:
                raise ValueError("Credit not found or insufficient quantity")
            
            # Redeem credit
            redemption_result = await self.credit_service.redeem_credit(
                credit_id=str(credit["_id"]),
                redeemed_by_staff_id=staff_id,
                transaction_id=pos_transaction_id,
                quantity=quantity,
                pos_transaction_id=pos_transaction_id
            )
            
            return {
                "success": True,
                "redemption_id": redemption_result.get("_id"),
                "service_value": redemption_result.get("service_value"),
                "message": f"Successfully redeemed {quantity} credit(s) for service"
            }
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error redeeming package credit at POS: {e}")
            raise Exception(f"Failed to redeem package credit: {str(e)}")
    
    async def get_package_redemption_summary(
        self,
        purchase_id: str
    ) -> Dict:
        """Get summary of package redemptions for display at POS"""
        try:
            purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(purchase_id)
            })
            
            if not purchase:
                raise ValueError("Package purchase not found")
            
            # Get credit balance
            balance = await self.credit_service.get_credit_balance(purchase_id)
            
            # Get package definition for display info
            package_def = self.db.packages.find_one({
                "_id": ObjectId(purchase["package_definition_id"])
            })
            
            return {
                "purchase_id": purchase_id,
                "package_name": package_def.get("name", "") if package_def else "",
                "status": purchase.get("status"),
                "expiration_date": purchase.get("expiration_date"),
                "days_remaining": self._calculate_days_remaining(purchase.get("expiration_date")),
                "credit_balance": balance.get("credits", {}),
                "total_remaining": balance.get("total_remaining", 0),
                "total_reserved": balance.get("total_reserved", 0)
            }
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error getting package redemption summary: {e}")
            raise Exception(f"Failed to get package summary: {str(e)}")
    
    # Private helper methods
    
    def _calculate_days_remaining(self, expiration_date: Optional[datetime]) -> Optional[int]:
        """Calculate days remaining until expiration"""
        if not expiration_date:
            return None
        
        try:
            days_remaining = (expiration_date - datetime.utcnow()).days
            return max(0, days_remaining)
        except Exception:
            return None
