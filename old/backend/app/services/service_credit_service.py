"""
Service credit service - Business logic for managing service credits within packages
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class ServiceCreditService:
    """Service layer for service credit management"""
    
    def __init__(self, db):
        self.db = db
    
    async def initialize_credits(
        self,
        purchase_id: str,
        service_quantities: Dict[str, int]
    ) -> List[Dict]:
        """Initialize service credits for a package purchase"""
        try:
            created_credits = []
            
            for service_id, quantity in service_quantities.items():
                # Get service details
                service = self.db.services.find_one({
                    "_id": ObjectId(service_id)
                })
                
                if not service:
                    logger.warning(f"Service {service_id} not found during credit initialization")
                    continue
                
                # Create credit record
                credit_data = {
                    "purchase_id": purchase_id,
                    "service_id": service_id,
                    "service_name": service.get("name", ""),
                    "service_price": service.get("price", 0),
                    "initial_quantity": quantity,
                    "remaining_quantity": quantity,
                    "reserved_quantity": 0,
                    "status": "available",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                result = self.db.service_credits.insert_one(credit_data)
                credit_data["_id"] = str(result.inserted_id)
                created_credits.append(credit_data)
            
            return created_credits
        
        except Exception as e:
            logger.error(f"Error initializing service credits: {e}")
            raise Exception(f"Failed to initialize service credits: {str(e)}")
    
    async def get_available_credits(
        self,
        purchase_id: str,
        service_id: Optional[str] = None
    ) -> List[Dict]:
        """Get available service credits for a package purchase"""
        try:
            query = {
                "purchase_id": purchase_id,
                "status": {"$in": ["available", "reserved"]},
                "remaining_quantity": {"$gt": 0}
            }
            
            if service_id:
                query["service_id"] = service_id
            
            cursor = self.db.service_credits.find(query)
            credits = list(cursor)
            
            # Convert ObjectId to string
            for credit in credits:
                credit["_id"] = str(credit["_id"])
            
            return credits
        
        except Exception as e:
            logger.error(f"Error getting available credits: {e}")
            raise Exception(f"Failed to get available credits: {str(e)}")
    
    async def reserve_credit(
        self,
        purchase_id: str,
        service_id: str,
        booking_id: str,
        quantity: int = 1
    ) -> Dict:
        """Reserve a service credit for a booking"""
        try:
            # Get available credit
            credit = self.db.service_credits.find_one({
                "purchase_id": purchase_id,
                "service_id": service_id,
                "remaining_quantity": {"$gte": quantity},
                "status": {"$in": ["available", "reserved"]}
            })
            
            if not credit:
                raise ValueError(f"Insufficient credits available for service {service_id}")
            
            # Create reservation
            reservation_data = {
                "credit_id": str(credit["_id"]),
                "booking_id": booking_id,
                "reserved_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24),
                "status": "active"
            }
            
            result = self.db.credit_reservations.insert_one(reservation_data)
            reservation_data["_id"] = str(result.inserted_id)
            
            # Update credit reserved quantity
            self.db.service_credits.update_one(
                {"_id": credit["_id"]},
                {
                    "$inc": {"reserved_quantity": quantity},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            return reservation_data
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error reserving credit: {e}")
            raise Exception(f"Failed to reserve credit: {str(e)}")
    
    async def release_credit(
        self,
        reservation_id: str,
        quantity: int = 1
    ) -> Dict:
        """Release a reserved service credit"""
        try:
            # Get reservation
            reservation = self.db.credit_reservations.find_one({
                "_id": ObjectId(reservation_id),
                "status": "active"
            })
            
            if not reservation:
                raise ValueError("Reservation not found or already released")
            
            # Get credit
            credit = self.db.service_credits.find_one({
                "_id": ObjectId(reservation["credit_id"])
            })
            
            if not credit:
                raise ValueError("Credit not found")
            
            # Update credit reserved quantity
            self.db.service_credits.update_one(
                {"_id": credit["_id"]},
                {
                    "$inc": {"reserved_quantity": -quantity},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Update reservation status
            self.db.credit_reservations.update_one(
                {"_id": ObjectId(reservation_id)},
                {
                    "$set": {"status": "released"}
                }
            )
            
            # Get updated reservation
            updated_reservation = self.db.credit_reservations.find_one({
                "_id": ObjectId(reservation_id)
            })
            updated_reservation["_id"] = str(updated_reservation["_id"])
            
            return updated_reservation
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error releasing credit: {e}")
            raise Exception(f"Failed to release credit: {str(e)}")
    
    async def redeem_credit(
        self,
        credit_id: str,
        redeemed_by_staff_id: str,
        transaction_id: str,
        quantity: int = 1,
        pos_transaction_id: Optional[str] = None,
        booking_id: Optional[str] = None
    ) -> Dict:
        """Redeem a service credit"""
        try:
            # Get credit
            credit = self.db.service_credits.find_one({
                "_id": ObjectId(credit_id)
            })
            
            if not credit:
                raise ValueError("Credit not found")
            
            # Check if credit is available
            if credit.get("remaining_quantity", 0) < quantity:
                raise ValueError(f"Insufficient credits available. Remaining: {credit.get('remaining_quantity', 0)}")
            
            # Check if package is expired
            purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(credit["purchase_id"])
            })
            
            if not purchase:
                raise ValueError("Package purchase not found")
            
            if purchase.get("status") == "expired":
                raise ValueError("Package has expired")
            
            if purchase.get("status") == "cancelled":
                raise ValueError("Package has been cancelled")
            
            # Check expiration date
            if purchase.get("expiration_date"):
                if datetime.utcnow() > purchase["expiration_date"]:
                    raise ValueError("Package has expired")
            
            # Create redemption transaction
            redemption_data = {
                "purchase_id": credit["purchase_id"],
                "credit_id": credit_id,
                "service_id": credit["service_id"],
                "client_id": purchase["client_id"],
                "redeemed_by_staff_id": redeemed_by_staff_id,
                "redemption_date": datetime.utcnow(),
                "service_value": credit.get("service_price", 0) * quantity,
                "pos_transaction_id": pos_transaction_id,
                "booking_id": booking_id,
                "created_at": datetime.utcnow()
            }
            
            result = self.db.redemption_transactions.insert_one(redemption_data)
            redemption_data["_id"] = str(result.inserted_id)
            
            # Update credit remaining quantity
            new_remaining = credit.get("remaining_quantity", 0) - quantity
            new_status = "redeemed" if new_remaining == 0 else credit.get("status", "available")
            
            self.db.service_credits.update_one(
                {"_id": ObjectId(credit_id)},
                {
                    "$inc": {"remaining_quantity": -quantity},
                    "$set": {
                        "status": new_status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Check if all credits in package are redeemed
            remaining_credits = self.db.service_credits.find_one({
                "purchase_id": credit["purchase_id"],
                "remaining_quantity": {"$gt": 0}
            })
            
            if not remaining_credits:
                # Mark package as fully redeemed
                self.db.package_purchases.update_one(
                    {"_id": ObjectId(credit["purchase_id"])},
                    {
                        "$set": {
                            "status": "fully_redeemed",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            
            # Create audit log
            await self._create_audit_log(
                tenant_id=purchase["tenant_id"],
                action_type="redeem",
                entity_type="credit",
                entity_id=credit_id,
                performed_by_user_id=redeemed_by_staff_id,
                client_id=purchase["client_id"],
                details={
                    "service_id": credit["service_id"],
                    "quantity": quantity,
                    "service_value": redemption_data["service_value"]
                }
            )
            
            return redemption_data
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error redeeming credit: {e}")
            raise Exception(f"Failed to redeem credit: {str(e)}")
    
    async def get_credit_balance(
        self,
        purchase_id: str
    ) -> Dict:
        """Get credit balance for a package purchase"""
        try:
            credits = list(self.db.service_credits.find({
                "purchase_id": purchase_id
            }))
            
            balance = {}
            total_remaining = 0
            total_reserved = 0
            
            for credit in credits:
                service_id = credit.get("service_id")
                remaining = credit.get("remaining_quantity", 0)
                reserved = credit.get("reserved_quantity", 0)
                
                balance[service_id] = {
                    "service_name": credit.get("service_name", ""),
                    "remaining": remaining,
                    "reserved": reserved,
                    "initial": credit.get("initial_quantity", 0)
                }
                
                total_remaining += remaining
                total_reserved += reserved
            
            return {
                "purchase_id": purchase_id,
                "credits": balance,
                "total_remaining": total_remaining,
                "total_reserved": total_reserved
            }
        
        except Exception as e:
            logger.error(f"Error getting credit balance: {e}")
            raise Exception(f"Failed to get credit balance: {str(e)}")
    
    # Private helper methods
    
    async def _create_audit_log(
        self,
        tenant_id: str,
        action_type: str,
        entity_type: str,
        entity_id: str,
        performed_by_user_id: str,
        client_id: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> None:
        """Create an audit log entry"""
        try:
            audit_data = {
                "tenant_id": tenant_id,
                "action_type": action_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "performed_by_user_id": performed_by_user_id,
                "performed_by_role": "staff",
                "client_id": client_id,
                "details": details or {},
                "timestamp": datetime.utcnow()
            }
            
            self.db.package_audit_logs.insert_one(audit_data)
        
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            # Don't raise - audit logging failure shouldn't block operations
