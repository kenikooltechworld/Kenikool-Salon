"""
Inventory Transaction Service - Handles transaction recording and retrieval
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from ..models.inventory_transaction import (
    InventoryTransaction,
    TransactionType,
    WasteReason,
)


class InventoryTransactionService:
    """Service for managing inventory transactions"""

    def __init__(self, db):
        self.db = db
        self.collection = db["inventory_transactions"]
        # Create indexes for performance
        self.collection.create_index("tenant_id")
        self.collection.create_index("product_id")
        self.collection.create_index("created_at")
        self.collection.create_index([("tenant_id", 1), ("product_id", 1)])
        self.collection.create_index([("tenant_id", 1), ("created_at", -1)])

    async def create_transaction(
        self,
        tenant_id: str,
        product_id: str,
        transaction_type: TransactionType,
        quantity_before: int,
        quantity_after: int,
        user_id: str,
        reason: Optional[str] = None,
        waste_reason: Optional[WasteReason] = None,
        reference_id: Optional[str] = None,
        notes: Optional[str] = None,
        batch_id: Optional[str] = None,
        location_id: Optional[str] = None,
    ) -> InventoryTransaction:
        """Create a new inventory transaction (immutable)"""
        transaction_data = {
            "tenant_id": tenant_id,
            "product_id": product_id,
            "transaction_type": transaction_type.value,
            "quantity_before": quantity_before,
            "quantity_after": quantity_after,
            "quantity_changed": quantity_after - quantity_before,
            "user_id": user_id,
            "reason": reason,
            "waste_reason": waste_reason.value if waste_reason else None,
            "reference_id": reference_id,
            "notes": notes,
            "batch_id": batch_id,
            "location_id": location_id,
            "created_at": datetime.utcnow(),
        }

        result = await self.collection.insert_one(transaction_data)
        transaction_data["_id"] = result.inserted_id

        return InventoryTransaction(**transaction_data)

    async def get_transactions(
        self,
        tenant_id: str,
        product_id: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[InventoryTransaction], int]:
        """Get transactions with optional filtering"""
        query: Dict[str, Any] = {"tenant_id": tenant_id}

        if product_id:
            query["product_id"] = product_id
        if transaction_type:
            query["transaction_type"] = transaction_type.value
        if user_id:
            query["user_id"] = user_id

        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["created_at"] = date_query

        total_count = await self.collection.count_documents(query)

        transactions = await self.collection.find(query).sort(
            "created_at", -1
        ).skip(skip).limit(limit).to_list(length=limit)

        return (
            [InventoryTransaction(**t) for t in transactions],
            total_count,
        )

    async def get_product_transactions(
        self,
        tenant_id: str,
        product_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[InventoryTransaction], int]:
        """Get all transactions for a specific product"""
        return await self.get_transactions(
            tenant_id=tenant_id,
            product_id=product_id,
            skip=skip,
            limit=limit,
        )

    async def get_transaction_summary(
        self,
        tenant_id: str,
        product_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get transaction summary for a product in the last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)

        transactions, _ = await self.get_transactions(
            tenant_id=tenant_id,
            product_id=product_id,
            start_date=start_date,
            limit=1000,
        )

        summary = {
            "total_transactions": len(transactions),
            "by_type": {},
            "total_added": 0,
            "total_removed": 0,
            "net_change": 0,
        }

        for transaction in transactions:
            tx_type = transaction.transaction_type
            if tx_type not in summary["by_type"]:
                summary["by_type"][tx_type] = 0
            summary["by_type"][tx_type] += 1

            if transaction.quantity_changed > 0:
                summary["total_added"] += transaction.quantity_changed
            else:
                summary["total_removed"] += abs(transaction.quantity_changed)

            summary["net_change"] += transaction.quantity_changed

        return summary

    async def export_transactions_csv(
        self,
        tenant_id: str,
        product_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> str:
        """Export transactions to CSV format"""
        transactions, _ = await self.get_transactions(
            tenant_id=tenant_id,
            product_id=product_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000,
        )

        csv_lines = [
            "Date,Product ID,Type,Before,After,Changed,User,Reason,Reference"
        ]

        for tx in transactions:
            csv_lines.append(
                f"{tx.created_at.isoformat()},{tx.product_id},"
                f"{tx.transaction_type},{tx.quantity_before},"
                f"{tx.quantity_after},{tx.quantity_changed},"
                f"{tx.user_id},{tx.reason or ''},{tx.reference_id or ''}"
            )

        return "\n".join(csv_lines)
