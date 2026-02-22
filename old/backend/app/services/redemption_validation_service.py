"""
Redemption validation service - Business logic for validating package redemptions
"""
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class RedemptionValidationService:
    """Service layer for redemption validation"""
    
    def __init__(self, db):
        self.db = db
    
    async def validate_redemption(
        self,
        purchase_id: str,
        service_id: str,
        client_id: str,
        stylist_id: Optional[str] = None,
        location_id: Optional[str] = None,
        redemption_date: Optional[datetime] = None
    ) -> Dict:
        """Validate if a redemption is allowed"""
        try:
            if redemption_date is None:
                redemption_date = datetime.utcnow()
            
            # Check expiration
            expiration_valid = await self.check_expiration(purchase_id)
            if not expiration_valid:
                return {
                    "valid": False,
                    "error": "Package has expired",
                    "error_code": "PACKAGE_EXPIRED"
                }
            
            # Check credit availability
            credit_available = await self.check_credit_availability(purchase_id, service_id)
            if not credit_available:
                return {
                    "valid": False,
                    "error": f"No available credits for service {service_id}",
                    "error_code": "INSUFFICIENT_CREDITS"
                }
            
            # Check ownership
            purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(purchase_id)
            })
            
            if not purchase:
                return {
                    "valid": False,
                    "error": "Package purchase not found",
                    "error_code": "PURCHASE_NOT_FOUND"
                }
            
            if purchase.get("client_id") != client_id:
                return {
                    "valid": False,
                    "error": "Package does not belong to client",
                    "error_code": "OWNERSHIP_MISMATCH"
                }
            
            # Check service inclusion
            service_included = await self._check_service_included(purchase_id, service_id)
            if not service_included:
                return {
                    "valid": False,
                    "error": f"Service {service_id} not included in package",
                    "error_code": "SERVICE_NOT_INCLUDED"
                }
            
            # Check package status
            if purchase.get("status") == "cancelled":
                return {
                    "valid": False,
                    "error": "Package has been cancelled",
                    "error_code": "PACKAGE_CANCELLED"
                }
            
            if purchase.get("status") == "fully_redeemed":
                return {
                    "valid": False,
                    "error": "Package has been fully redeemed",
                    "error_code": "PACKAGE_FULLY_REDEEMED"
                }
            
            # Check restrictions
            restrictions = await self.check_restrictions(
                purchase_id=purchase_id,
                stylist_id=stylist_id,
                location_id=location_id,
                redemption_date=redemption_date
            )
            
            if restrictions:
                return {
                    "valid": False,
                    "error": "Redemption violates package restrictions",
                    "error_code": "RESTRICTION_VIOLATION",
                    "violations": restrictions
                }
            
            return {
                "valid": True,
                "error": None,
                "error_code": None
            }
        
        except Exception as e:
            logger.error(f"Error validating redemption: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}",
                "error_code": "VALIDATION_ERROR"
            }
    
    async def check_expiration(
        self,
        purchase_id: str
    ) -> bool:
        """Check if package is expired"""
        try:
            purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(purchase_id)
            })
            
            if not purchase:
                return False
            
            # Check status
            if purchase.get("status") == "expired":
                return False
            
            # Check expiration date
            if purchase.get("expiration_date"):
                if datetime.utcnow() > purchase["expiration_date"]:
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking expiration: {e}")
            return False
    
    async def check_credit_availability(
        self,
        purchase_id: str,
        service_id: str
    ) -> bool:
        """Check if credits are available for a service"""
        try:
            credit = self.db.service_credits.find_one({
                "purchase_id": purchase_id,
                "service_id": service_id,
                "remaining_quantity": {"$gt": 0},
                "status": {"$in": ["available", "reserved"]}
            })
            
            return credit is not None
        
        except Exception as e:
            logger.error(f"Error checking credit availability: {e}")
            return False
    
    async def check_restrictions(
        self,
        purchase_id: str,
        stylist_id: Optional[str] = None,
        location_id: Optional[str] = None,
        redemption_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Check if redemption violates package restrictions"""
        try:
            if redemption_date is None:
                redemption_date = datetime.utcnow()
            
            violations = []
            
            # Get package definition
            purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(purchase_id)
            })
            
            if not purchase:
                return violations
            
            package_def = self.db.packages.find_one({
                "_id": ObjectId(purchase["package_definition_id"])
            })
            
            if not package_def:
                return violations
            
            restrictions = package_def.get("restrictions", {})
            
            # Check stylist restrictions
            if restrictions.get("stylist_ids"):
                allowed_stylists = restrictions["stylist_ids"]
                if stylist_id and stylist_id not in allowed_stylists:
                    violations.append({
                        "type": "stylist_restriction",
                        "message": f"Service can only be redeemed with stylists: {', '.join(allowed_stylists)}",
                        "allowed_values": allowed_stylists
                    })
            
            # Check location restrictions
            if restrictions.get("location_ids"):
                allowed_locations = restrictions["location_ids"]
                if location_id and location_id not in allowed_locations:
                    violations.append({
                        "type": "location_restriction",
                        "message": f"Service can only be redeemed at locations: {', '.join(allowed_locations)}",
                        "allowed_values": allowed_locations
                    })
            
            # Check time restrictions
            time_restrictions = restrictions.get("time_restrictions", {})
            if time_restrictions:
                time_violation = await self._check_time_restriction(
                    time_restrictions,
                    redemption_date
                )
                if time_violation:
                    violations.append(time_violation)
            
            # Check blackout dates
            blackout_dates = restrictions.get("blackout_dates", [])
            if blackout_dates:
                redemption_date_only = redemption_date.date()
                for blackout_date in blackout_dates:
                    if isinstance(blackout_date, datetime):
                        blackout_date_only = blackout_date.date()
                    else:
                        blackout_date_only = blackout_date
                    
                    if redemption_date_only == blackout_date_only:
                        violations.append({
                            "type": "blackout_date",
                            "message": f"Service cannot be redeemed on {redemption_date_only}",
                            "blackout_date": str(redemption_date_only)
                        })
                        break
            
            return violations
        
        except Exception as e:
            logger.error(f"Error checking restrictions: {e}")
            return []
    
    # Private helper methods
    
    async def _check_service_included(
        self,
        purchase_id: str,
        service_id: str
    ) -> bool:
        """Check if service is included in package"""
        try:
            credit = self.db.service_credits.find_one({
                "purchase_id": purchase_id,
                "service_id": service_id
            })
            
            return credit is not None
        
        except Exception as e:
            logger.error(f"Error checking service inclusion: {e}")
            return False
    
    async def _check_time_restriction(
        self,
        time_restrictions: Dict,
        redemption_date: datetime
    ) -> Optional[Dict]:
        """Check if redemption violates time restrictions"""
        try:
            # Check day of week
            days_of_week = time_restrictions.get("days_of_week")
            if days_of_week:
                # Monday = 0, Sunday = 6
                current_day = redemption_date.weekday()
                if current_day not in days_of_week:
                    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    allowed_days = [day_names[d] for d in days_of_week]
                    return {
                        "type": "time_restriction_day",
                        "message": f"Service can only be redeemed on: {', '.join(allowed_days)}",
                        "allowed_days": allowed_days
                    }
            
            # Check time of day
            start_time = time_restrictions.get("start_time")
            end_time = time_restrictions.get("end_time")
            
            if start_time or end_time:
                current_time = redemption_date.strftime("%H:%M")
                
                if start_time and current_time < start_time:
                    return {
                        "type": "time_restriction_before",
                        "message": f"Service can only be redeemed after {start_time}",
                        "start_time": start_time
                    }
                
                if end_time and current_time > end_time:
                    return {
                        "type": "time_restriction_after",
                        "message": f"Service can only be redeemed before {end_time}",
                        "end_time": end_time
                    }
            
            return None
        
        except Exception as e:
            logger.error(f"Error checking time restriction: {e}")
            return None
