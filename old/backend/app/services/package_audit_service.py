"""
Package audit service - Audit logging for all package operations
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class PackageAuditService:
    """Service for package audit logging"""
    
    def __init__(self, db):
        self.db = db
    
    async def log_action(
        self,
        tenant_id: str,
        action_type: str,
        entity_type: str,
        entity_id: str,
        performed_by_user_id: str,
        performed_by_role: str,
        client_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a package operation
        
        Requirements: 18.1, 18.2, 18.3, 18.4, 18.5
        
        Args:
            tenant_id: Tenant ID
            action_type: Type of action (create, purchase, redeem, transfer, refund, extend)
            entity_type: Type of entity (definition, purchase, credit)
            entity_id: ID of the entity being audited
            performed_by_user_id: User ID who performed the action
            performed_by_role: Role of the user
            client_id: Client ID if applicable
            details: Additional action details
            
        Returns:
            Audit log entry ID
        """
        try:
            log_entry = {
                "tenant_id": tenant_id,
                "action_type": action_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "performed_by_user_id": performed_by_user_id,
                "performed_by_role": performed_by_role,
                "client_id": client_id,
                "details": details or {},
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            result = self.db.package_audit_logs.insert_one(log_entry)
            log_id = str(result.inserted_id)
            
            logger.info(
                f"Package audit log created: {action_type} on {entity_type} {entity_id} "
                f"by user {performed_by_user_id}"
            )
            
            return log_id
        
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            raise Exception(f"Failed to create audit log: {str(e)}")
    
    async def log_package_creation(
        self,
        tenant_id: str,
        package_id: str,
        performed_by_user_id: str,
        performed_by_role: str,
        package_name: str,
        package_price: float
    ) -> str:
        """Log package definition creation"""
        return await self.log_action(
            tenant_id=tenant_id,
            action_type="create",
            entity_type="definition",
            entity_id=package_id,
            performed_by_user_id=performed_by_user_id,
            performed_by_role=performed_by_role,
            details={
                "package_name": package_name,
                "package_price": package_price
            }
        )
    
    async def log_package_purchase(
        self,
        tenant_id: str,
        purchase_id: str,
        performed_by_user_id: str,
        performed_by_role: str,
        client_id: str,
        package_name: str,
        amount: float,
        is_gift: bool = False
    ) -> str:
        """Log package purchase"""
        return await self.log_action(
            tenant_id=tenant_id,
            action_type="purchase",
            entity_type="purchase",
            entity_id=purchase_id,
            performed_by_user_id=performed_by_user_id,
            performed_by_role=performed_by_role,
            client_id=client_id,
            details={
                "package_name": package_name,
                "amount": amount,
                "is_gift": is_gift
            }
        )
    
    async def log_package_redemption(
        self,
        tenant_id: str,
        purchase_id: str,
        performed_by_user_id: str,
        performed_by_role: str,
        client_id: str,
        service_name: str,
        service_value: float
    ) -> str:
        """Log package redemption"""
        return await self.log_action(
            tenant_id=tenant_id,
            action_type="redeem",
            entity_type="credit",
            entity_id=purchase_id,
            performed_by_user_id=performed_by_user_id,
            performed_by_role=performed_by_role,
            client_id=client_id,
            details={
                "service_name": service_name,
                "service_value": service_value
            }
        )
    
    async def log_package_transfer(
        self,
        tenant_id: str,
        purchase_id: str,
        performed_by_user_id: str,
        performed_by_role: str,
        from_client_id: str,
        to_client_id: str
    ) -> str:
        """Log package transfer"""
        return await self.log_action(
            tenant_id=tenant_id,
            action_type="transfer",
            entity_type="purchase",
            entity_id=purchase_id,
            performed_by_user_id=performed_by_user_id,
            performed_by_role=performed_by_role,
            client_id=to_client_id,
            details={
                "from_client_id": from_client_id,
                "to_client_id": to_client_id
            }
        )
    
    async def log_package_refund(
        self,
        tenant_id: str,
        purchase_id: str,
        performed_by_user_id: str,
        performed_by_role: str,
        client_id: str,
        reason: str,
        refund_amount: float
    ) -> str:
        """Log package refund"""
        return await self.log_action(
            tenant_id=tenant_id,
            action_type="refund",
            entity_type="purchase",
            entity_id=purchase_id,
            performed_by_user_id=performed_by_user_id,
            performed_by_role=performed_by_role,
            client_id=client_id,
            details={
                "reason": reason,
                "refund_amount": refund_amount
            }
        )
    
    async def log_expiration_extension(
        self,
        tenant_id: str,
        purchase_id: str,
        performed_by_user_id: str,
        performed_by_role: str,
        client_id: str,
        additional_days: int,
        new_expiration_date: datetime
    ) -> str:
        """Log package expiration extension"""
        return await self.log_action(
            tenant_id=tenant_id,
            action_type="extend",
            entity_type="purchase",
            entity_id=purchase_id,
            performed_by_user_id=performed_by_user_id,
            performed_by_role=performed_by_role,
            client_id=client_id,
            details={
                "additional_days": additional_days,
                "new_expiration_date": new_expiration_date.isoformat()
            }
        )
    
    async def get_audit_logs(
        self,
        tenant_id: str,
        action_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        client_id: Optional[str] = None,
        performed_by_user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Get audit logs with optional filtering
        
        Requirements: 18.6
        """
        try:
            query = {"tenant_id": tenant_id}
            
            if action_type:
                query["action_type"] = action_type
            if entity_type:
                query["entity_type"] = entity_type
            if entity_id:
                query["entity_id"] = entity_id
            if client_id:
                query["client_id"] = client_id
            if performed_by_user_id:
                query["performed_by_user_id"] = performed_by_user_id
            
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                if date_query:
                    query["timestamp"] = date_query
            
            # Get total count
            total = self.db.package_audit_logs.count_documents(query)
            
            # Get paginated results
            skip = (page - 1) * page_size
            logs = list(
                self.db.package_audit_logs.find(query)
                .sort("timestamp", -1)
                .skip(skip)
                .limit(page_size)
            )
            
            # Convert ObjectId to string
            for log in logs:
                log["id"] = str(log.pop("_id"))
            
            return {
                "logs": logs,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            raise Exception(f"Failed to get audit logs: {str(e)}")
    
    async def get_entity_audit_history(
        self,
        tenant_id: str,
        entity_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """Get complete audit history for a specific entity"""
        try:
            logs = list(
                self.db.package_audit_logs.find({
                    "tenant_id": tenant_id,
                    "entity_id": entity_id
                })
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for log in logs:
                log["id"] = str(log.pop("_id"))
            
            return logs
        
        except Exception as e:
            logger.error(f"Error getting entity audit history: {e}")
            raise Exception(f"Failed to get entity audit history: {str(e)}")
    
    async def get_user_audit_activity(
        self,
        tenant_id: str,
        performed_by_user_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """Get audit activity for a specific user"""
        try:
            logs = list(
                self.db.package_audit_logs.find({
                    "tenant_id": tenant_id,
                    "performed_by_user_id": performed_by_user_id
                })
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for log in logs:
                log["id"] = str(log.pop("_id"))
            
            return logs
        
        except Exception as e:
            logger.error(f"Error getting user audit activity: {e}")
            raise Exception(f"Failed to get user audit activity: {str(e)}")
    
    async def get_client_audit_history(
        self,
        tenant_id: str,
        client_id: str,
        limit: int = 100
    ) -> List[Dict]:
        """Get audit history for a specific client"""
        try:
            logs = list(
                self.db.package_audit_logs.find({
                    "tenant_id": tenant_id,
                    "client_id": client_id
                })
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for log in logs:
                log["id"] = str(log.pop("_id"))
            
            return logs
        
        except Exception as e:
            logger.error(f"Error getting client audit history: {e}")
            raise Exception(f"Failed to get client audit history: {str(e)}")
