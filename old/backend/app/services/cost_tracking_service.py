from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from pymongo.collection import Collection


class CostTrackingService:
    def __init__(self, db):
        self.db = db
        self.products_collection: Collection = db.inventory
        self.cost_history_collection: Collection = db.product_cost_history
        self.transactions_collection: Collection = db.inventory_transactions

    def update_product_cost(
        self,
        product_id: str,
        new_cost_price: float,
        reason: str = "price_update",
        updated_by: str = "system",
    ) -> Dict:
        """Update product cost and maintain history"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        old_cost = product.get("cost_price", 0)

        # Record cost history
        cost_record = {
            "product_id": product_id,
            "old_cost": old_cost,
            "new_cost": new_cost_price,
            "reason": reason,
            "updated_by": updated_by,
            "updated_at": datetime.utcnow(),
        }

        self.cost_history_collection.insert_one(cost_record)

        # Update product
        self.products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"cost_price": new_cost_price}},
        )

        return {
            "product_id": product_id,
            "old_cost": old_cost,
            "new_cost": new_cost_price,
            "change_percentage": (
                ((new_cost_price - old_cost) / old_cost * 100) if old_cost > 0 else 0
            ),
        }

    def get_cost_history(self, product_id: str) -> List[Dict]:
        """Get cost history for a product"""
        records = list(
            self.cost_history_collection.find({"product_id": product_id}).sort(
                "updated_at", -1
            )
        )
        return [
            {**r, "_id": str(r["_id"]), "id": str(r["_id"])} for r in records
        ]

    def calculate_average_cost(self, product_id: str) -> float:
        """Calculate average cost for inventory valuation"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # For simplicity, use current cost price
        # In real scenario, would calculate weighted average based on purchase history
        return product.get("cost_price", 0)

    def calculate_product_margin(self, product_id: str) -> Dict:
        """Calculate margin for a product"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        selling_price = product.get("price", 0)
        cost_price = product.get("cost_price", 0)

        if cost_price == 0:
            margin_percentage = 0
        else:
            margin_percentage = ((selling_price - cost_price) / cost_price) * 100

        gross_profit = selling_price - cost_price

        return {
            "product_id": product_id,
            "product_name": product.get("name"),
            "selling_price": selling_price,
            "cost_price": cost_price,
            "gross_profit": gross_profit,
            "margin_percentage": margin_percentage,
            "is_negative_margin": margin_percentage < 0,
        }

    def get_all_product_margins(self) -> List[Dict]:
        """Get margins for all products"""
        products = list(self.products_collection.find({}))
        margins = []

        for product in products:
            margin = self.calculate_product_margin(str(product["_id"]))
            margins.append(margin)

        return sorted(margins, key=lambda x: x["margin_percentage"])

    def get_negative_margin_products(self) -> List[Dict]:
        """Get products with negative margins"""
        all_margins = self.get_all_product_margins()
        return [m for m in all_margins if m["is_negative_margin"]]

    def calculate_gross_profit_per_product(
        self,
        product_id: str,
        quantity_sold: float,
    ) -> Dict:
        """Calculate gross profit for sold quantity"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        selling_price = product.get("price", 0)
        cost_price = product.get("cost_price", 0)

        total_revenue = selling_price * quantity_sold
        total_cost = cost_price * quantity_sold
        gross_profit = total_revenue - total_cost

        return {
            "product_id": product_id,
            "product_name": product.get("name"),
            "quantity_sold": quantity_sold,
            "unit_selling_price": selling_price,
            "unit_cost_price": cost_price,
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "gross_profit": gross_profit,
            "profit_margin_percentage": (
                (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            ),
        }

    def calculate_service_profitability(
        self,
        service_id: str,
        quantity_used: float,
        service_price: float,
    ) -> Dict:
        """Calculate profitability including product costs"""
        # This would need service-product mapping data
        # For now, return basic structure
        return {
            "service_id": service_id,
            "service_price": service_price,
            "product_cost": 0,  # Would be calculated from mapped products
            "gross_profit": service_price,
            "profit_margin_percentage": 100,
        }

    def get_cost_trends(
        self,
        product_id: str,
        days: int = 90,
    ) -> Dict:
        """Get cost trends over time"""
        from datetime import timedelta

        start_date = datetime.utcnow() - timedelta(days=days)

        records = list(
            self.cost_history_collection.find(
                {
                    "product_id": product_id,
                    "updated_at": {"$gte": start_date},
                }
            ).sort("updated_at", 1)
        )

        return {
            "product_id": product_id,
            "period_days": days,
            "cost_changes": [
                {
                    "date": r["updated_at"].isoformat(),
                    "old_cost": r["old_cost"],
                    "new_cost": r["new_cost"],
                    "change": r["new_cost"] - r["old_cost"],
                    "change_percentage": (
                        ((r["new_cost"] - r["old_cost"]) / r["old_cost"] * 100)
                        if r["old_cost"] > 0
                        else 0
                    ),
                    "reason": r["reason"],
                }
                for r in records
            ],
            "current_cost": records[-1]["new_cost"] if records else 0,
            "starting_cost": records[0]["old_cost"] if records else 0,
        }

    def calculate_inventory_valuation(self) -> Dict:
        """Calculate total inventory value"""
        products = list(self.products_collection.find({}))

        total_value = 0
        by_category = {}

        for product in products:
            quantity = product.get("quantity", 0)
            cost_price = product.get("cost_price", 0)
            product_value = quantity * cost_price

            total_value += product_value

            category = product.get("category", "uncategorized")
            if category not in by_category:
                by_category[category] = {"value": 0, "quantity": 0, "products": 0}

            by_category[category]["value"] += product_value
            by_category[category]["quantity"] += quantity
            by_category[category]["products"] += 1

        return {
            "total_inventory_value": total_value,
            "total_products": len(products),
            "by_category": by_category,
        }
