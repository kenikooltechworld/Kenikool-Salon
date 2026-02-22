"""
Batch Tracking Service - Handles batch/lot tracking for products
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bson import ObjectId


class BatchTrackingService:
    """Service for batch and lot tracking"""

    def __init__(self, db):
        self.db = db
        self.products_collection = db["inventory_products"]
        self.batches_collection = db["inventory_batches"]
        self.batches_collection.create_index([("product_id", 1), ("tenant_id", 1)])
        self.batches_collection.create_index("expiration_date")

    async def add_batch(
        self,
        tenant_id: str,
        product_id: str,
        batch_id: str,
        quantity: int,
        expiration_date: Optional[datetime] = None,
        cost_price: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a new batch to a product"""
        batch_data = {
            "tenant_id": tenant_id,
            "product_id": product_id,
            "batch_id": batch_id,
            "quantity": quantity,
            "quantity_used": 0,
            "expiration_date": expiration_date,
            "cost_price": cost_price,
            "notes": notes,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await self.batches_collection.insert_one(batch_data)
        batch_data["_id"] = str(result.inserted_id)

        return batch_data

    async def get_product_batches(
        self,
        tenant_id: str,
        product_id: str,
        include_expired: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get all batches for a product"""
        query = {
            "tenant_id": tenant_id,
            "product_id": product_id,
        }

        if not include_expired:
            query["status"] = "active"

        batches = await self.batches_collection.find(query).sort(
            "expiration_date", 1
        ).to_list(length=None)

        return [
            {**b, "_id": str(b["_id"])}
            for b in batches
        ]

    async def get_expiring_batches(
        self,
        tenant_id: str,
        days_until_expiry: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get batches expiring within N days"""
        now = datetime.utcnow()
        expiry_threshold = now + timedelta(days=days_until_expiry)

        batches = await self.batches_collection.find({
            "tenant_id": tenant_id,
            "status": "active",
            "expiration_date": {
                "$gte": now,
                "$lte": expiry_threshold,
            },
        }).sort("expiration_date", 1).to_list(length=None)

        return [
            {**b, "_id": str(b["_id"])}
            for b in batches
        ]

    async def get_expired_batches(
        self,
        tenant_id: str,
    ) -> List[Dict[str, Any]]:
        """Get expired batches"""
        now = datetime.utcnow()

        batches = await self.batches_collection.find({
            "tenant_id": tenant_id,
            "expiration_date": {"$lt": now},
            "status": "active",
        }).to_list(length=None)

        return [
            {**b, "_id": str(b["_id"])}
            for b in batches
        ]

    async def use_batch_fifo(
        self,
        tenant_id: str,
        product_id: str,
        quantity_to_use: int,
    ) -> Dict[str, Any]:
        """Use batch stock using FIFO (First In, First Out)"""
        batches = await self.get_product_batches(
            tenant_id=tenant_id,
            product_id=product_id,
            include_expired=False,
        )

        if not batches:
            return {"error": "No active batches available"}

        remaining_quantity = quantity_to_use
        used_batches = []

        for batch in batches:
            if remaining_quantity <= 0:
                break

            available_quantity = batch["quantity"] - batch["quantity_used"]

            if available_quantity > 0:
                quantity_to_use_from_batch = min(remaining_quantity, available_quantity)

                await self.batches_collection.update_one(
                    {"_id": ObjectId(batch["_id"])},
                    {
                        "$inc": {"quantity_used": quantity_to_use_from_batch},
                        "$set": {"updated_at": datetime.utcnow()},
                    },
                )

                used_batches.append({
                    "batch_id": batch["batch_id"],
                    "quantity_used": quantity_to_use_from_batch,
                })

                remaining_quantity -= quantity_to_use_from_batch

        return {
            "total_used": quantity_to_use - remaining_quantity,
            "remaining": remaining_quantity,
            "used_batches": used_batches,
        }

    async def mark_batch_expired(
        self,
        tenant_id: str,
        batch_id: str,
    ) -> bool:
        """Mark a batch as expired"""
        result = await self.batches_collection.update_one(
            {
                "_id": ObjectId(batch_id),
                "tenant_id": tenant_id,
            },
            {
                "$set": {
                    "status": "expired",
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        return result.modified_count > 0

    async def get_batch_history(
        self,
        tenant_id: str,
        product_id: str,
    ) -> List[Dict[str, Any]]:
        """Get complete batch history for a product"""
        batches = await self.batches_collection.find({
            "tenant_id": tenant_id,
            "product_id": product_id,
        }).sort("created_at", -1).to_list(length=None)

        return [
            {**b, "_id": str(b["_id"])}
            for b in batches
        ]
