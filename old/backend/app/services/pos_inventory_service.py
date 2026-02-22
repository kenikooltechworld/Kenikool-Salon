from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from pymongo.collection import Collection


class POSInventoryService:
    def __init__(self, db):
        self.db = db
        self.products_collection: Collection = db.inventory
        self.transactions_collection: Collection = db.inventory_transactions
        self.pos_sales_collection: Collection = db.pos_sales

    def deduct_for_pos_sale(
        self,
        product_id: str,
        quantity: float,
        sale_id: str,
        user_id: str,
        unit_price: float,
    ) -> Dict:
        """Deduct inventory for POS sale"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        current_quantity = product.get("quantity", 0)
        if current_quantity < quantity:
            raise ValueError(
                f"Insufficient stock. Available: {current_quantity}, Requested: {quantity}"
            )

        # Deduct from inventory
        self.products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"quantity": -quantity}},
        )

        # Create transaction record
        transaction = {
            "product_id": product_id,
            "type": "pos_sale",
            "quantity_change": -quantity,
            "before_quantity": current_quantity,
            "after_quantity": current_quantity - quantity,
            "reason": f"POS Sale: {sale_id}",
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "metadata": {
                "sale_id": sale_id,
                "unit_price": unit_price,
                "total_amount": quantity * unit_price,
            },
        }

        self.transactions_collection.insert_one(transaction)

        # Record POS sale
        pos_sale = {
            "product_id": product_id,
            "sale_id": sale_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": quantity * unit_price,
            "user_id": user_id,
            "recorded_at": datetime.utcnow(),
            "status": "completed",
        }

        self.pos_sales_collection.insert_one(pos_sale)

        return {
            "success": True,
            "product_id": product_id,
            "quantity_deducted": quantity,
            "remaining_quantity": current_quantity - quantity,
        }

    def restore_for_voided_sale(
        self,
        product_id: str,
        quantity: float,
        sale_id: str,
        user_id: str,
    ) -> Dict:
        """Restore inventory for voided POS sale"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        current_quantity = product.get("quantity", 0)

        # Restore to inventory
        self.products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"quantity": quantity}},
        )

        # Create reversal transaction
        transaction = {
            "product_id": product_id,
            "type": "pos_void",
            "quantity_change": quantity,
            "before_quantity": current_quantity,
            "after_quantity": current_quantity + quantity,
            "reason": f"POS Void: {sale_id}",
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "metadata": {
                "sale_id": sale_id,
                "reversal": True,
            },
        }

        self.transactions_collection.insert_one(transaction)

        # Update POS sale status
        self.pos_sales_collection.update_one(
            {"sale_id": sale_id, "product_id": product_id},
            {"$set": {"status": "voided", "voided_at": datetime.utcnow()}},
        )

        return {
            "success": True,
            "product_id": product_id,
            "quantity_restored": quantity,
            "new_quantity": current_quantity + quantity,
        }

    def restore_for_refund(
        self,
        product_id: str,
        quantity: float,
        sale_id: str,
        user_id: str,
        refund_reason: str = "customer_return",
    ) -> Dict:
        """Restore inventory for refunded POS sale"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        current_quantity = product.get("quantity", 0)

        # Restore to inventory
        self.products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"quantity": quantity}},
        )

        # Create refund transaction
        transaction = {
            "product_id": product_id,
            "type": "pos_refund",
            "quantity_change": quantity,
            "before_quantity": current_quantity,
            "after_quantity": current_quantity + quantity,
            "reason": f"POS Refund: {refund_reason}",
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "metadata": {
                "sale_id": sale_id,
                "refund_reason": refund_reason,
            },
        }

        self.transactions_collection.insert_one(transaction)

        # Update POS sale status
        self.pos_sales_collection.update_one(
            {"sale_id": sale_id, "product_id": product_id},
            {"$set": {"status": "refunded", "refunded_at": datetime.utcnow()}},
        )

        return {
            "success": True,
            "product_id": product_id,
            "quantity_restored": quantity,
            "new_quantity": current_quantity + quantity,
        }

    def get_pos_sales_history(
        self,
        product_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """Get POS sales history"""
        query = {}

        if product_id:
            query["product_id"] = product_id
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["recorded_at"] = date_query

        sales = list(
            self.pos_sales_collection.find(query).sort("recorded_at", -1)
        )
        return [
            {**s, "_id": str(s["_id"]), "id": str(s["_id"])} for s in sales
        ]

    def get_pos_sales_analytics(
        self,
        product_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """Get POS sales analytics"""
        query = {"status": "completed"}

        if product_id:
            query["product_id"] = product_id
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["recorded_at"] = date_query

        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$product_id",
                    "total_quantity": {"$sum": "$quantity"},
                    "total_revenue": {"$sum": "$total_amount"},
                    "transaction_count": {"$sum": 1},
                    "avg_unit_price": {"$avg": "$unit_price"},
                }
            },
            {"$sort": {"total_revenue": -1}},
        ]

        results = list(self.pos_sales_collection.aggregate(pipeline))

        return {
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            "total_quantity_sold": sum(r["total_quantity"] for r in results),
            "total_revenue": sum(r["total_revenue"] for r in results),
            "total_transactions": sum(r["transaction_count"] for r in results),
            "by_product": results,
        }

    def separate_service_vs_retail(
        self,
        product_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict:
        """Separate service usage from retail sales"""
        query = {"product_id": product_id}

        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["timestamp"] = date_query

        service_usage = list(
            self.transactions_collection.find(
                {**query, "type": "service_usage"}
            )
        )
        retail_sales = list(
            self.transactions_collection.find(
                {**query, "type": "pos_sale"}
            )
        )

        service_quantity = sum(abs(t["quantity_change"]) for t in service_usage)
        retail_quantity = sum(abs(t["quantity_change"]) for t in retail_sales)

        return {
            "product_id": product_id,
            "service_usage": {
                "quantity": service_quantity,
                "transaction_count": len(service_usage),
            },
            "retail_sales": {
                "quantity": retail_quantity,
                "transaction_count": len(retail_sales),
            },
            "total_consumption": service_quantity + retail_quantity,
            "service_percentage": (
                (service_quantity / (service_quantity + retail_quantity) * 100)
                if (service_quantity + retail_quantity) > 0
                else 0
            ),
            "retail_percentage": (
                (retail_quantity / (service_quantity + retail_quantity) * 100)
                if (service_quantity + retail_quantity) > 0
                else 0
            ),
        }
