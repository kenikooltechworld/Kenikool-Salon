"""Service for POS audit logging."""

from datetime import datetime
from typing import Optional, Any
from decimal import Decimal
from bson import ObjectId
from app.models.audit_log import AuditLog


class POSAuditService:
    """Service for POS audit logging and tracking."""

    @staticmethod
    def _convert_decimals(obj):
        """Convert Decimal values to float for MongoDB compatibility."""
        if isinstance(obj, dict):
            return {k: POSAuditService._convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [POSAuditService._convert_decimals(item) for item in obj]
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj

    @staticmethod
    def log_transaction_created(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
        user_id: ObjectId,
        transaction_data: dict,
    ) -> AuditLog:
        """
        Log transaction creation.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            user_id: User ID
            transaction_data: Transaction data

        Returns:
            Created AuditLog document
        """
        clean_data = POSAuditService._convert_decimals(transaction_data)
        
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=str(user_id),
            event_type="CREATE",
            resource=f"/transactions/{transaction_id}",
            ip_address="127.0.0.1",  # Will be set by middleware in production
            status_code=201,
            request_body=clean_data,
            tags=["pos", "transaction", "create"],
        )
        audit_log.save()
        return audit_log

    @staticmethod
    def log_transaction_modified(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
        old_value: dict,
        new_value: dict,
        user_id: ObjectId,
    ) -> AuditLog:
        """
        Log transaction modification.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            old_value: Old transaction data
            new_value: New transaction data
            user_id: User ID

        Returns:
            Created AuditLog document
        """
        clean_old = POSAuditService._convert_decimals(old_value)
        clean_new = POSAuditService._convert_decimals(new_value)
        
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=str(user_id),
            event_type="UPDATE",
            resource=f"/transactions/{transaction_id}",
            ip_address="127.0.0.1",
            status_code=200,
            request_body=clean_new,
            response_body={"old_value": clean_old, "new_value": clean_new},
            tags=["pos", "transaction", "update"],
        )
        audit_log.save()
        return audit_log

    @staticmethod
    def log_payment_processed(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
        payment_method: str,
        user_id: ObjectId,
        payment_data: Optional[dict] = None,
    ) -> AuditLog:
        """
        Log payment processing.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            payment_method: Payment method
            user_id: User ID
            payment_data: Optional payment data

        Returns:
            Created AuditLog document
        """
        clean_payment_data = POSAuditService._convert_decimals(payment_data or {})
        
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=str(user_id),
            event_type="PAYMENT",
            resource=f"/transactions/{transaction_id}/payment",
            ip_address="127.0.0.1",
            status_code=200,
            request_body={
                "payment_method": payment_method,
                **clean_payment_data
            },
            tags=["pos", "payment", "processed"],
        )
        audit_log.save()
        return audit_log

    @staticmethod
    def log_refund_processed(
        tenant_id: ObjectId,
        refund_id: ObjectId,
        user_id: ObjectId,
        refund_data: Optional[dict] = None,
    ) -> AuditLog:
        """
        Log refund processing.

        Args:
            tenant_id: Tenant ID
            refund_id: Refund ID
            user_id: User ID
            refund_data: Optional refund data

        Returns:
            Created AuditLog document
        """
        clean_refund_data = POSAuditService._convert_decimals(refund_data or {})
        
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=str(user_id),
            event_type="REFUND",
            resource=f"/refunds/{refund_id}",
            ip_address="127.0.0.1",
            status_code=200,
            request_body=clean_refund_data,
            tags=["pos", "refund", "processed"],
        )
        audit_log.save()
        return audit_log

    @staticmethod
    def log_discount_applied(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
        discount_id: ObjectId,
        user_id: ObjectId,
        discount_data: Optional[dict] = None,
    ) -> AuditLog:
        """
        Log discount application.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            discount_id: Discount ID
            user_id: User ID
            discount_data: Optional discount data

        Returns:
            Created AuditLog document
        """
        clean_discount_data = POSAuditService._convert_decimals(discount_data or {})
        
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=str(user_id),
            event_type="DISCOUNT",
            resource=f"/transactions/{transaction_id}/discount",
            ip_address="127.0.0.1",
            status_code=200,
            request_body={
                "discount_id": str(discount_id),
                **clean_discount_data
            },
            tags=["pos", "discount", "applied"],
        )
        audit_log.save()
        return audit_log

    @staticmethod
    def log_inventory_deducted(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
        items: list,
        user_id: ObjectId,
    ) -> AuditLog:
        """
        Log inventory deduction.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            items: List of items deducted
            user_id: User ID

        Returns:
            Created AuditLog document
        """
        clean_items = POSAuditService._convert_decimals(items)
        
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=str(user_id),
            event_type="INVENTORY",
            resource=f"/transactions/{transaction_id}/inventory",
            ip_address="127.0.0.1",
            status_code=200,
            request_body={"items": clean_items},
            tags=["pos", "inventory", "deducted"],
        )
        audit_log.save()
        return audit_log

    @staticmethod
    def get_audit_trail(
        tenant_id: ObjectId,
        resource_type: str,
        resource_id: str,
    ) -> list:
        """
        Get audit trail for a resource.

        Args:
            tenant_id: Tenant ID
            resource_type: Resource type (not used with new schema)
            resource_id: Resource ID

        Returns:
            List of AuditLog documents
        """
        # Search by resource path pattern
        audit_logs = AuditLog.objects(
            tenant_id=tenant_id,
            resource__contains=resource_id
        ).order_by("-created_at")

        return list(audit_logs)
