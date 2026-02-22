"""
Audit Service
Handles audit logging for service changes
"""
from datetime import datetime
from typing import Dict, Optional, Any, List
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Service for logging audit trails"""

    def __init__(self, db):
        self.db = db
        self.collection = db.audit_logs
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create indexes for efficient querying"""
        try:
            # Index for querying by entity
            self.collection.create_index([("entity_type", 1), ("entity_id", 1)])
            # Index for querying by tenant
            self.collection.create_index("tenant_id")
            # Index for querying by timestamp
            self.collection.create_index("timestamp")
            # Compound index for common queries
            self.collection.create_index(
                [("tenant_id", 1), ("entity_type", 1), ("timestamp", -1)]
            )
            logger.info("Audit log indexes created")
        except Exception as e:
            logger.error(f"Failed to create audit log indexes: {e}")

    def log_change(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        tenant_id: str,
        user_id: str,
        user_email: str,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log an audit entry
        
        Args:
            entity_type: Type of entity (e.g., "service", "booking")
            entity_id: ID of the entity
            action: Action performed (e.g., "create", "update", "delete")
            tenant_id: Tenant ID
            user_id: User who performed the action
            user_email: Email of the user
            changes: Dictionary of field changes {field: {"old": value, "new": value}}
            metadata: Additional metadata
            
        Returns:
            ID of the audit log entry
            
        Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
        """
        audit_entry = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "user_email": user_email,
            "changes": changes or {},
            "metadata": metadata or {},
            "timestamp": datetime.utcnow(),
        }

        result = self.collection.insert_one(audit_entry)
        logger.info(
            f"Audit log created: {action} on {entity_type} {entity_id} by {user_email}"
        )
        return str(result.inserted_id)

    def log_service_creation(
        self,
        service_id: str,
        tenant_id: str,
        user_id: str,
        user_email: str,
        service_data: Dict[str, Any],
    ) -> str:
        """
        Log service creation
        
        Requirements: 13.1, 13.2
        """
        return self.log_change(
            entity_type="service",
            entity_id=service_id,
            action="create",
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            metadata={"service_data": service_data},
        )

    def log_service_update(
        self,
        service_id: str,
        tenant_id: str,
        user_id: str,
        user_email: str,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
    ) -> str:
        """
        Log service update with field-level changes
        
        Requirements: 13.1, 13.3, 13.4
        """
        # Calculate field-level changes
        changes = {}
        for field, new_value in new_values.items():
            old_value = old_values.get(field)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}

        return self.log_change(
            entity_type="service",
            entity_id=service_id,
            action="update",
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            changes=changes,
        )

    def log_service_deletion(
        self,
        service_id: str,
        tenant_id: str,
        user_id: str,
        user_email: str,
        service_data: Dict[str, Any],
    ) -> str:
        """
        Log service deletion
        
        Requirements: 13.1, 13.2
        """
        return self.log_change(
            entity_type="service",
            entity_id=service_id,
            action="delete",
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            metadata={"service_data": service_data},
        )

    def get_entity_audit_log(
        self,
        entity_type: str,
        entity_id: str,
        tenant_id: str,
        limit: int = 50,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get audit log for a specific entity
        
        Requirements: 13.6
        """
        logs = list(
            self.collection.find(
                {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "tenant_id": tenant_id,
                }
            )
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

        # Convert ObjectId to string
        for log in logs:
            log["_id"] = str(log["_id"])

        return logs

    def get_audit_log_by_filters(
        self,
        tenant_id: str,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs with filters
        
        Requirements: 13.6
        """
        query = {"tenant_id": tenant_id}

        if entity_type:
            query["entity_type"] = entity_type

        if action:
            query["action"] = action

        if user_id:
            query["user_id"] = user_id

        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date

        logs = list(
            self.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        )

        # Convert ObjectId to string
        for log in logs:
            log["_id"] = str(log["_id"])

        return logs

    def count_audit_logs(
        self,
        tenant_id: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
    ) -> int:
        """Count audit logs matching criteria"""
        query = {"tenant_id": tenant_id}

        if entity_type:
            query["entity_type"] = entity_type

        if entity_id:
            query["entity_id"] = entity_id

        return self.collection.count_documents(query)


# Singleton instance
audit_service = None


def get_audit_service(db):
    """Get or create audit service instance"""
    global audit_service
    if audit_service is None:
        audit_service = AuditService(db)
    return audit_service
