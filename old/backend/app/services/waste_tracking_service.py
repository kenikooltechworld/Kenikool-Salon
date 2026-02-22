from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from pymongo.collection import Collection
from pydantic import BaseModel, Field
from enum import Enum


class WasteReason(str, Enum):
    EXPIRED = "expired"
    DAMAGED = "damaged"
    SPILLED = "spilled"
    THEFT = "theft"
    OTHER = "other"


class WasteRecord(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    product_id: str
    quantity: float
    reason: WasteReason
    notes: Optional[str] = None
    cost_impact: float
    recorded_by: str
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    batch_id: Optional[str] = None

    class Config:
        populate_by_name = True


class WasteTrackingService:
    def __init__(self, db):
        self.db = db
        self.waste_collection: Collection = db.inventory_waste
        self.products_collection: Collection = db.inventory
        self.transactions_collection: Collection = db.inventory_transactions

    def record_waste(
        self,
        product_id: str,
        quantity: float,
        reason: WasteReason,
        recorded_by: str,
        notes: Optional[str] = None,
        batch_id: Optional[str] = None,
    ) -> Dict:
        """Record waste and deduct from inventory"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        if product.get("quantity", 0) < quantity:
            raise ValueError(f"Insufficient quantity. Available: {product['quantity']}")

        cost_impact = (product.get("cost_price", 0) or 0) * quantity

        waste_record = {
            "product_id": product_id,
            "quantity": quantity,
            "reason": reason.value,
            "notes": notes,
            "cost_impact": cost_impact,
            "recorded_by": recorded_by,
            "recorded_at": datetime.utcnow(),
            "batch_id": batch_id,
        }

        result = self.waste_collection.insert_one(waste_record)

        # Deduct from inventory
        self.products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"quantity": -quantity}},
        )

        # Create transaction record
        self.transactions_collection.insert_one(
            {
                "product_id": product_id,
                "type": "waste",
                "quantity_change": -quantity,
                "before_quantity": product.get("quantity", 0),
                "after_quantity": product.get("quantity", 0) - quantity,
                "reason": f"Waste: {reason.value}",
                "user_id": recorded_by,
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "waste_reason": reason.value,
                    "waste_notes": notes,
                    "batch_id": batch_id,
                },
            }
        )

        return {"id": str(result.inserted_id), **waste_record}

    def get_waste_report(
        self,
        product_id: Optional[str] = None,
        reason: Optional[WasteReason] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """Get waste report with optional filters"""
        query = {}

        if product_id:
            query["product_id"] = product_id
        if reason:
            query["reason"] = reason.value
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["recorded_at"] = date_query

        records = list(self.waste_collection.find(query).sort("recorded_at", -1))
        return [
            {**record, "_id": str(record["_id"]), "id": str(record["_id"])}
            for record in records
        ]

    def get_waste_by_product(self, product_id: str) -> Dict:
        """Get waste statistics for a product"""
        pipeline = [
            {"$match": {"product_id": product_id}},
            {
                "$group": {
                    "_id": "$reason",
                    "total_quantity": {"$sum": "$quantity"},
                    "total_cost": {"$sum": "$cost_impact"},
                    "count": {"$sum": 1},
                }
            },
        ]

        results = list(self.waste_collection.aggregate(pipeline))
        return {
            "product_id": product_id,
            "by_reason": {r["_id"]: {"quantity": r["total_quantity"], "cost": r["total_cost"], "count": r["count"]} for r in results},
            "total_quantity": sum(r["total_quantity"] for r in results),
            "total_cost": sum(r["total_cost"] for r in results),
        }

    def get_high_waste_products(self, threshold_percentage: float = 5.0) -> List[Dict]:
        """Identify products with waste exceeding threshold"""
        pipeline = [
            {
                "$group": {
                    "_id": "$product_id",
                    "total_waste_quantity": {"$sum": "$quantity"},
                    "total_waste_cost": {"$sum": "$cost_impact"},
                }
            },
            {"$sort": {"total_waste_cost": -1}},
        ]

        waste_by_product = list(self.waste_collection.aggregate(pipeline))

        high_waste = []
        for waste in waste_by_product:
            product = self.products_collection.find_one({"_id": ObjectId(waste["_id"])})
            if product:
                waste_percentage = (waste["total_waste_quantity"] / (product.get("quantity", 0) + waste["total_waste_quantity"])) * 100 if (product.get("quantity", 0) + waste["total_waste_quantity"]) > 0 else 0

                if waste_percentage >= threshold_percentage:
                    high_waste.append(
                        {
                            "product_id": waste["_id"],
                            "product_name": product.get("name"),
                            "waste_quantity": waste["total_waste_quantity"],
                            "waste_cost": waste["total_waste_cost"],
                            "waste_percentage": waste_percentage,
                        }
                    )

        return high_waste

    def calculate_shrinkage(self, product_id: str) -> Dict:
        """Calculate shrinkage (expected vs actual)"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        waste_stats = self.get_waste_by_product(product_id)
        total_waste = waste_stats["total_quantity"]

        return {
            "product_id": product_id,
            "current_quantity": product.get("quantity", 0),
            "total_waste": total_waste,
            "shrinkage_percentage": (total_waste / (product.get("quantity", 0) + total_waste)) * 100 if (product.get("quantity", 0) + total_waste) > 0 else 0,
            "waste_cost": waste_stats["total_cost"],
        }

    def get_waste_trends(self, days: int = 30) -> Dict:
        """Get waste trends over time"""
        from datetime import timedelta

        start_date = datetime.utcnow() - timedelta(days=days)

        pipeline = [
            {"$match": {"recorded_at": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$recorded_at"}
                    },
                    "daily_quantity": {"$sum": "$quantity"},
                    "daily_cost": {"$sum": "$cost_impact"},
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        trends = list(self.waste_collection.aggregate(pipeline))
        return {
            "period_days": days,
            "daily_trends": trends,
            "total_quantity": sum(t["daily_quantity"] for t in trends),
            "total_cost": sum(t["daily_cost"] for t in trends),
        }
