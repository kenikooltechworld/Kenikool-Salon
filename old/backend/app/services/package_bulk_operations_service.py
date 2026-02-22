"""
Package bulk operations service - Business logic for bulk package operations
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class PackageBulkOperationsService:
    """Service layer for bulk package operations with transaction support"""
    
    def __init__(self, db):
        self.db = db
    
    async def bulk_activate_packages(
        self,
        tenant_id: str,
        package_ids: List[str],
        performed_by_staff_id: str
    ) -> Dict:
        """
        Bulk activate multiple package definitions
        
        Requirements: 17.1, 17.5
        Property 26: Bulk Operation Atomicity
        
        Args:
            tenant_id: Tenant identifier
            package_ids: List of package definition IDs to activate
            performed_by_staff_id: Staff member performing the operation
        
        Returns:
            Dict with operation summary (successful, failed, total)
        """
        try:
            successful = []
            failed = []
            
            # Start a session for transaction support
            session = self.db.client.start_session()
            
            try:
                session.start_transaction()
                
                for package_id in package_ids:
                    try:
                        # Validate package exists and belongs to tenant
                        package = self.db.packages.find_one({
                            "_id": ObjectId(package_id),
                            "tenant_id": tenant_id
                        }, session=session)
                        
                        if not package:
                            failed.append({
                                "package_id": package_id,
                                "error": "Package not found"
                            })
                            continue
                        
                        # Update package status
                        result = self.db.packages.update_one(
                            {"_id": ObjectId(package_id)},
                            {
                                "$set": {
                                    "is_active": True,
                                    "updated_at": datetime.utcnow()
                                }
                            },
                            session=session
                        )
                        
                        if result.modified_count > 0:
                            successful.append(package_id)
                            
                            # Create audit log
                            self.db.package_audit_logs.insert_one({
                                "tenant_id": tenant_id,
                                "action_type": "activate",
                                "entity_type": "definition",
                                "entity_id": package_id,
                                "performed_by_user_id": performed_by_staff_id,
                                "performed_by_role": "staff",
                                "details": {
                                    "operation": "bulk_activate",
                                    "package_name": package.get("name")
                                },
                                "timestamp": datetime.utcnow()
                            }, session=session)
                        else:
                            failed.append({
                                "package_id": package_id,
                                "error": "Failed to update package"
                            })
                    
                    except Exception as e:
                        failed.append({
                            "package_id": package_id,
                            "error": str(e)
                        })
                
                # Commit transaction
                session.commit_transaction()
            
            except Exception as e:
                session.abort_transaction()
                logger.error(f"Bulk activate transaction failed: {e}")
                raise Exception(f"Bulk activation failed: {str(e)}")
            
            finally:
                session.end_session()
            
            return {
                "operation": "bulk_activate",
                "total_requested": len(package_ids),
                "successful": len(successful),
                "failed": len(failed),
                "successful_ids": successful,
                "failed_details": failed,
                "timestamp": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Error in bulk_activate_packages: {e}")
            raise Exception(f"Bulk activation failed: {str(e)}")
    
    async def bulk_deactivate_packages(
        self,
        tenant_id: str,
        package_ids: List[str],
        performed_by_staff_id: str
    ) -> Dict:
        """
        Bulk deactivate multiple package definitions
        
        Requirements: 17.2, 17.5
        Property 26: Bulk Operation Atomicity
        
        Args:
            tenant_id: Tenant identifier
            package_ids: List of package definition IDs to deactivate
            performed_by_staff_id: Staff member performing the operation
        
        Returns:
            Dict with operation summary (successful, failed, total)
        """
        try:
            successful = []
            failed = []
            
            # Start a session for transaction support
            session = self.db.client.start_session()
            
            try:
                session.start_transaction()
                
                for package_id in package_ids:
                    try:
                        # Validate package exists and belongs to tenant
                        package = self.db.packages.find_one({
                            "_id": ObjectId(package_id),
                            "tenant_id": tenant_id
                        }, session=session)
                        
                        if not package:
                            failed.append({
                                "package_id": package_id,
                                "error": "Package not found"
                            })
                            continue
                        
                        # Update package status
                        result = self.db.packages.update_one(
                            {"_id": ObjectId(package_id)},
                            {
                                "$set": {
                                    "is_active": False,
                                    "updated_at": datetime.utcnow()
                                }
                            },
                            session=session
                        )
                        
                        if result.modified_count > 0:
                            successful.append(package_id)
                            
                            # Create audit log
                            self.db.package_audit_logs.insert_one({
                                "tenant_id": tenant_id,
                                "action_type": "deactivate",
                                "entity_type": "definition",
                                "entity_id": package_id,
                                "performed_by_user_id": performed_by_staff_id,
                                "performed_by_role": "staff",
                                "details": {
                                    "operation": "bulk_deactivate",
                                    "package_name": package.get("name")
                                },
                                "timestamp": datetime.utcnow()
                            }, session=session)
                        else:
                            failed.append({
                                "package_id": package_id,
                                "error": "Failed to update package"
                            })
                    
                    except Exception as e:
                        failed.append({
                            "package_id": package_id,
                            "error": str(e)
                        })
                
                # Commit transaction
                session.commit_transaction()
            
            except Exception as e:
                session.abort_transaction()
                logger.error(f"Bulk deactivate transaction failed: {e}")
                raise Exception(f"Bulk deactivation failed: {str(e)}")
            
            finally:
                session.end_session()
            
            return {
                "operation": "bulk_deactivate",
                "total_requested": len(package_ids),
                "successful": len(successful),
                "failed": len(failed),
                "successful_ids": successful,
                "failed_details": failed,
                "timestamp": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Error in bulk_deactivate_packages: {e}")
            raise Exception(f"Bulk deactivation failed: {str(e)}")
    
    async def bulk_update_prices(
        self,
        tenant_id: str,
        package_updates: List[Dict],
        performed_by_staff_id: str
    ) -> Dict:
        """
        Bulk update prices for multiple packages
        
        Requirements: 17.3, 17.5
        Property 26: Bulk Operation Atomicity
        
        Args:
            tenant_id: Tenant identifier
            package_updates: List of dicts with package_id and new_price
            performed_by_staff_id: Staff member performing the operation
        
        Returns:
            Dict with operation summary (successful, failed, total)
        """
        try:
            successful = []
            failed = []
            
            # Start a session for transaction support
            session = self.db.client.start_session()
            
            try:
                session.start_transaction()
                
                for update_item in package_updates:
                    package_id = update_item.get("package_id")
                    new_price = update_item.get("new_price")
                    
                    try:
                        # Validate inputs
                        if not package_id or new_price is None:
                            failed.append({
                                "package_id": package_id,
                                "error": "Missing package_id or new_price"
                            })
                            continue
                        
                        if new_price < 0:
                            failed.append({
                                "package_id": package_id,
                                "error": "Price cannot be negative"
                            })
                            continue
                        
                        # Validate package exists and belongs to tenant
                        package = self.db.packages.find_one({
                            "_id": ObjectId(package_id),
                            "tenant_id": tenant_id
                        }, session=session)
                        
                        if not package:
                            failed.append({
                                "package_id": package_id,
                                "error": "Package not found"
                            })
                            continue
                        
                        old_price = package.get("package_price", 0)
                        
                        # Update package price
                        result = self.db.packages.update_one(
                            {"_id": ObjectId(package_id)},
                            {
                                "$set": {
                                    "package_price": new_price,
                                    "updated_at": datetime.utcnow()
                                }
                            },
                            session=session
                        )
                        
                        if result.modified_count > 0:
                            successful.append(package_id)
                            
                            # Create audit log
                            self.db.package_audit_logs.insert_one({
                                "tenant_id": tenant_id,
                                "action_type": "update",
                                "entity_type": "definition",
                                "entity_id": package_id,
                                "performed_by_user_id": performed_by_staff_id,
                                "performed_by_role": "staff",
                                "details": {
                                    "operation": "bulk_update_prices",
                                    "package_name": package.get("name"),
                                    "old_price": old_price,
                                    "new_price": new_price
                                },
                                "timestamp": datetime.utcnow()
                            }, session=session)
                        else:
                            failed.append({
                                "package_id": package_id,
                                "error": "Failed to update package"
                            })
                    
                    except Exception as e:
                        failed.append({
                            "package_id": package_id,
                            "error": str(e)
                        })
                
                # Commit transaction
                session.commit_transaction()
            
            except Exception as e:
                session.abort_transaction()
                logger.error(f"Bulk update prices transaction failed: {e}")
                raise Exception(f"Bulk price update failed: {str(e)}")
            
            finally:
                session.end_session()
            
            return {
                "operation": "bulk_update_prices",
                "total_requested": len(package_updates),
                "successful": len(successful),
                "failed": len(failed),
                "successful_ids": successful,
                "failed_details": failed,
                "timestamp": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Error in bulk_update_prices: {e}")
            raise Exception(f"Bulk price update failed: {str(e)}")
    
    async def bulk_extend_expiration(
        self,
        tenant_id: str,
        purchase_updates: List[Dict],
        performed_by_staff_id: str
    ) -> Dict:
        """
        Bulk extend expiration dates for multiple purchased packages
        
        Requirements: 17.4, 17.5
        Property 26: Bulk Operation Atomicity
        
        Args:
            tenant_id: Tenant identifier
            purchase_updates: List of dicts with purchase_id and additional_days
            performed_by_staff_id: Staff member performing the operation
        
        Returns:
            Dict with operation summary (successful, failed, total)
        """
        try:
            successful = []
            failed = []
            
            # Start a session for transaction support
            session = self.db.client.start_session()
            
            try:
                session.start_transaction()
                
                for update_item in purchase_updates:
                    purchase_id = update_item.get("purchase_id")
                    additional_days = update_item.get("additional_days")
                    
                    try:
                        # Validate inputs
                        if not purchase_id or additional_days is None:
                            failed.append({
                                "purchase_id": purchase_id,
                                "error": "Missing purchase_id or additional_days"
                            })
                            continue
                        
                        if additional_days <= 0:
                            failed.append({
                                "purchase_id": purchase_id,
                                "error": "Additional days must be positive"
                            })
                            continue
                        
                        # Validate purchase exists and belongs to tenant
                        purchase = self.db.package_purchases.find_one({
                            "_id": ObjectId(purchase_id),
                            "tenant_id": tenant_id
                        }, session=session)
                        
                        if not purchase:
                            failed.append({
                                "purchase_id": purchase_id,
                                "error": "Package purchase not found"
                            })
                            continue
                        
                        # Calculate new expiration date
                        current_expiration = purchase.get("expiration_date")
                        if not current_expiration:
                            failed.append({
                                "purchase_id": purchase_id,
                                "error": "Package has no expiration date"
                            })
                            continue
                        
                        new_expiration = current_expiration + timedelta(days=additional_days)
                        
                        # Update purchase expiration
                        result = self.db.package_purchases.update_one(
                            {"_id": ObjectId(purchase_id)},
                            {
                                "$set": {
                                    "expiration_date": new_expiration,
                                    "updated_at": datetime.utcnow()
                                }
                            },
                            session=session
                        )
                        
                        if result.modified_count > 0:
                            successful.append(purchase_id)
                            
                            # Create audit log
                            self.db.package_audit_logs.insert_one({
                                "tenant_id": tenant_id,
                                "action_type": "extend",
                                "entity_type": "purchase",
                                "entity_id": purchase_id,
                                "performed_by_user_id": performed_by_staff_id,
                                "performed_by_role": "staff",
                                "details": {
                                    "operation": "bulk_extend_expiration",
                                    "old_expiration": current_expiration,
                                    "new_expiration": new_expiration,
                                    "additional_days": additional_days,
                                    "client_id": purchase.get("client_id")
                                },
                                "timestamp": datetime.utcnow()
                            }, session=session)
                        else:
                            failed.append({
                                "purchase_id": purchase_id,
                                "error": "Failed to update purchase"
                            })
                    
                    except Exception as e:
                        failed.append({
                            "purchase_id": purchase_id,
                            "error": str(e)
                        })
                
                # Commit transaction
                session.commit_transaction()
            
            except Exception as e:
                session.abort_transaction()
                logger.error(f"Bulk extend expiration transaction failed: {e}")
                raise Exception(f"Bulk expiration extension failed: {str(e)}")
            
            finally:
                session.end_session()
            
            return {
                "operation": "bulk_extend_expiration",
                "total_requested": len(purchase_updates),
                "successful": len(successful),
                "failed": len(failed),
                "successful_ids": successful,
                "failed_details": failed,
                "timestamp": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Error in bulk_extend_expiration: {e}")
            raise Exception(f"Bulk expiration extension failed: {str(e)}")
