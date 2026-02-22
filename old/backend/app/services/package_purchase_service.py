"""
Package purchase service - Business logic for package purchases and redemptions
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class PackagePurchaseService:
    """Service layer for package purchase management"""
    
    def __init__(self, db, payment_service=None, credit_service=None):
        self.db = db
        self.payment_service = payment_service
        self.credit_service = credit_service
    
    async def create_purchase(
        self,
        tenant_id: str,
        client_id: str,
        package_definition_id: str,
        payment_method: str,
        purchased_by_staff_id: str,
        is_gift: bool = False,
        recipient_id: Optional[str] = None,
        gift_message: Optional[str] = None
    ) -> Dict:
        """Create a new package purchase with payment processing"""
        try:
            # Get package definition
            package_def = self.db.packages.find_one({
                "_id": ObjectId(package_definition_id),
                "tenant_id": tenant_id,
                "is_active": True
            })
            
            if not package_def:
                raise ValueError("Package definition not found or inactive")
            
            # Determine actual client (recipient if gift, otherwise purchaser)
            actual_client_id = recipient_id if is_gift else client_id
            
            # Validate recipient exists if gift
            if is_gift and recipient_id:
                recipient = self.db.clients.find_one({
                    "_id": ObjectId(recipient_id),
                    "tenant_id": tenant_id
                })
                if not recipient:
                    raise ValueError("Recipient client not found")
            
            # Calculate expiration date
            expiration_date = None
            if package_def.get("validity_days"):
                expiration_date = datetime.utcnow() + timedelta(days=package_def["validity_days"])
            
            # Create purchase record
            purchase_data = {
                "tenant_id": tenant_id,
                "package_definition_id": str(package_def["_id"]),
                "client_id": actual_client_id,
                "purchased_by_staff_id": purchased_by_staff_id,
                "purchase_date": datetime.utcnow(),
                "expiration_date": expiration_date,
                "status": "active",
                "original_price": package_def.get("original_price", 0),
                "amount_paid": package_def.get("package_price", 0),
                "payment_method": payment_method,
                "payment_transaction_id": "",
                "is_gift": is_gift,
                "gift_from_client_id": client_id if is_gift else None,
                "gift_message": gift_message,
                "is_transferable": package_def.get("is_transferable", True),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Process payment if payment service available
            if self.payment_service:
                try:
                    payment_result = await self.payment_service.process_payment(
                        tenant_id=tenant_id,
                        client_id=actual_client_id,
                        amount=purchase_data["amount_paid"],
                        payment_method=payment_method,
                        description=f"Package purchase: {package_def.get('name')}"
                    )
                    purchase_data["payment_transaction_id"] = payment_result.get("transaction_id", "")
                except Exception as e:
                    logger.error(f"Payment processing failed: {e}")
                    raise Exception(f"Payment processing failed: {str(e)}")
            
            # Insert purchase
            result = self.db.package_purchases.insert_one(purchase_data)
            purchase_data["_id"] = str(result.inserted_id)
            
            # Initialize service credits
            await self._initialize_service_credits(
                str(result.inserted_id),
                package_def.get("services", [])
            )
            
            # Create audit log
            await self._create_audit_log(
                tenant_id=tenant_id,
                action_type="purchase",
                entity_type="purchase",
                entity_id=str(result.inserted_id),
                performed_by_user_id=purchased_by_staff_id,
                client_id=actual_client_id,
                details={
                    "package_name": package_def.get("name"),
                    "amount": purchase_data["amount_paid"],
                    "is_gift": is_gift
                }
            )
            
            return purchase_data
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error creating package purchase: {e}")
            raise Exception(f"Failed to create package purchase: {str(e)}")
    
    async def get_client_packages(
        self,
        client_id: str,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get all packages for a client with optional status filtering"""
        try:
            query = {"client_id": client_id}
            
            if status:
                query["status"] = status
            
            cursor = self.db.package_purchases.find(query).sort("purchase_date", -1)
            purchases = list(cursor)
            
            # Convert ObjectId to string
            for purchase in purchases:
                purchase["_id"] = str(purchase["_id"])
            
            return purchases
        
        except Exception as e:
            logger.error(f"Error getting client packages: {e}")
            raise Exception(f"Failed to get client packages: {str(e)}")
    
    async def get_package_details(
        self,
        purchase_id: str
    ) -> Dict:
        """Get detailed information about a package purchase"""
        try:
            purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(purchase_id)
            })
            
            if not purchase:
                raise ValueError("Package purchase not found")
            
            purchase["_id"] = str(purchase["_id"])
            
            # Get service credits
            credits = list(self.db.service_credits.find({
                "purchase_id": purchase_id
            }))
            
            for credit in credits:
                credit["_id"] = str(credit["_id"])
            
            purchase["service_credits"] = credits
            
            # Get redemption history
            redemptions = list(self.db.redemption_transactions.find({
                "purchase_id": purchase_id
            }).sort("redemption_date", -1))
            
            for redemption in redemptions:
                redemption["_id"] = str(redemption["_id"])
            
            purchase["redemption_history"] = redemptions
            
            return purchase
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error getting package details: {e}")
            raise Exception(f"Failed to get package details: {str(e)}")
    
    async def transfer_package(
        self,
        purchase_id: str,
        from_client_id: str,
        to_client_id: str,
        staff_id: str
    ) -> Dict:
        """Transfer a package from one client to another"""
        try:
            # Get purchase
            purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(purchase_id),
                "client_id": from_client_id
            })
            
            if not purchase:
                raise ValueError("Package purchase not found or does not belong to client")
            
            # Check if transferable
            if not purchase.get("is_transferable", True):
                raise ValueError("Package is not transferable")
            
            # Check for remaining credits
            credits = list(self.db.service_credits.find({
                "purchase_id": purchase_id,
                "remaining_quantity": {"$gt": 0}
            }))
            
            if not credits:
                raise ValueError("Package has no remaining credits to transfer")
            
            # Verify recipient exists
            recipient = self.db.clients.find_one({
                "_id": ObjectId(to_client_id),
                "tenant_id": purchase["tenant_id"]
            })
            
            if not recipient:
                raise ValueError("Recipient client not found")
            
            # Update purchase ownership
            self.db.package_purchases.update_one(
                {"_id": ObjectId(purchase_id)},
                {
                    "$set": {
                        "client_id": to_client_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Create audit log
            await self._create_audit_log(
                tenant_id=purchase["tenant_id"],
                action_type="transfer",
                entity_type="purchase",
                entity_id=purchase_id,
                performed_by_user_id=staff_id,
                client_id=to_client_id,
                details={
                    "from_client_id": from_client_id,
                    "to_client_id": to_client_id
                }
            )
            
            # Get updated purchase
            updated_purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(purchase_id)
            })
            updated_purchase["_id"] = str(updated_purchase["_id"])
            
            return updated_purchase
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error transferring package: {e}")
            raise Exception(f"Failed to transfer package: {str(e)}")
    
    async def refund_package(
        self,
        purchase_id: str,
        reason: str,
        staff_id: str
    ) -> Dict:
        """Refund a package purchase"""
        try:
            # Get purchase
            purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(purchase_id)
            })
            
            if not purchase:
                raise ValueError("Package purchase not found")
            
            # Check if fully redeemed
            if purchase.get("status") == "fully_redeemed":
                raise ValueError("Cannot refund fully redeemed package")
            
            # Calculate refund amount based on unused credits
            credits = list(self.db.service_credits.find({
                "purchase_id": purchase_id
            }))
            
            total_credits = sum(c.get("initial_quantity", 0) for c in credits)
            remaining_credits = sum(c.get("remaining_quantity", 0) for c in credits)
            
            if total_credits == 0:
                refund_amount = 0
            else:
                refund_amount = (remaining_credits / total_credits) * purchase.get("amount_paid", 0)
            
            # Process refund if payment service available
            if self.payment_service and purchase.get("payment_transaction_id"):
                try:
                    await self.payment_service.process_refund(
                        transaction_id=purchase["payment_transaction_id"],
                        amount=refund_amount,
                        reason=reason
                    )
                except Exception as e:
                    logger.error(f"Refund processing failed: {e}")
                    raise Exception(f"Refund processing failed: {str(e)}")
            
            # Mark purchase as cancelled
            self.db.package_purchases.update_one(
                {"_id": ObjectId(purchase_id)},
                {
                    "$set": {
                        "status": "cancelled",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Create audit log
            await self._create_audit_log(
                tenant_id=purchase["tenant_id"],
                action_type="refund",
                entity_type="purchase",
                entity_id=purchase_id,
                performed_by_user_id=staff_id,
                client_id=purchase["client_id"],
                details={
                    "reason": reason,
                    "refund_amount": refund_amount
                }
            )
            
            # Get updated purchase
            updated_purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(purchase_id)
            })
            updated_purchase["_id"] = str(updated_purchase["_id"])
            
            return updated_purchase
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error refunding package: {e}")
            raise Exception(f"Failed to refund package: {str(e)}")
    
    async def extend_expiration(
        self,
        purchase_id: str,
        additional_days: int,
        staff_id: str
    ) -> Dict:
        """Extend the expiration date of a package"""
        try:
            # Get purchase
            purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(purchase_id)
            })
            
            if not purchase:
                raise ValueError("Package purchase not found")
            
            # Calculate new expiration date
            current_expiration = purchase.get("expiration_date")
            if current_expiration:
                new_expiration = current_expiration + timedelta(days=additional_days)
            else:
                new_expiration = datetime.utcnow() + timedelta(days=additional_days)
            
            # Update purchase
            self.db.package_purchases.update_one(
                {"_id": ObjectId(purchase_id)},
                {
                    "$set": {
                        "expiration_date": new_expiration,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Create audit log
            await self._create_audit_log(
                tenant_id=purchase["tenant_id"],
                action_type="extend",
                entity_type="purchase",
                entity_id=purchase_id,
                performed_by_user_id=staff_id,
                client_id=purchase["client_id"],
                details={
                    "additional_days": additional_days,
                    "new_expiration_date": new_expiration
                }
            )
            
            # Get updated purchase
            updated_purchase = self.db.package_purchases.find_one({
                "_id": ObjectId(purchase_id)
            })
            updated_purchase["_id"] = str(updated_purchase["_id"])
            
            return updated_purchase
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error extending package expiration: {e}")
            raise Exception(f"Failed to extend package expiration: {str(e)}")
    
    # Private helper methods
    
    async def _initialize_service_credits(
        self,
        purchase_id: str,
        services: List[Dict]
    ) -> None:
        """Initialize service credits for a package purchase"""
        try:
            # Convert services list to dict format for credit service
            service_quantities = {}
            for service_item in services:
                service_id = service_item.get("service_id")
                quantity = service_item.get("quantity", 1)
                service_quantities[service_id] = quantity
            
            # Use credit service if available, otherwise use direct DB access
            if self.credit_service:
                await self.credit_service.initialize_credits(
                    purchase_id=purchase_id,
                    service_quantities=service_quantities
                )
            else:
                # Fallback to direct DB access
                for service_id, quantity in service_quantities.items():
                    service = self.db.services.find_one({
                        "_id": ObjectId(service_id)
                    })
                    
                    if not service:
                        logger.warning(f"Service {service_id} not found during credit initialization")
                        continue
                    
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
                    
                    self.db.service_credits.insert_one(credit_data)
        
        except Exception as e:
            logger.error(f"Error initializing service credits: {e}")
            raise Exception(f"Failed to initialize service credits: {str(e)}")
    
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
