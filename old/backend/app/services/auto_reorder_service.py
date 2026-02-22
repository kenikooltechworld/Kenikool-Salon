from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from pymongo.collection import Collection
import math


class AutoReorderService:
    def __init__(self, db):
        self.db = db
        self.products_collection: Collection = db.inventory
        self.purchase_orders_collection: Collection = db.purchase_orders
        self.suppliers_collection: Collection = db.suppliers

    def calculate_eoq(
        self,
        annual_demand: float,
        ordering_cost: float = 50,
        holding_cost: float = 5,
    ) -> float:
        """Calculate Economic Order Quantity (EOQ)"""
        if annual_demand <= 0 or holding_cost <= 0:
            return 0

        eoq = math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
        return max(eoq, 1)

    def should_reorder(
        self,
        product_id: str,
    ) -> bool:
        """Check if product should be reordered"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        if not product.get("auto_reorder_enabled"):
            return False

        current_quantity = product.get("quantity", 0)
        reorder_point = product.get("reorder_point", 10)

        return current_quantity <= reorder_point

    def create_auto_reorder_po(
        self,
        product_id: str,
        created_by: str = "system",
    ) -> Optional[Dict]:
        """Create a draft PO for auto-reorder"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        if not product.get("auto_reorder_enabled"):
            return None

        if not self.should_reorder(product_id):
            return None

        supplier_id = product.get("supplier_id")
        if not supplier_id:
            return None

        supplier = self.suppliers_collection.find_one({"_id": ObjectId(supplier_id)})
        if not supplier:
            return None

        # Calculate reorder quantity using EOQ
        annual_demand = product.get("annual_demand", 100)
        reorder_quantity = int(self.calculate_eoq(annual_demand))
        reorder_quantity = max(reorder_quantity, product.get("reorder_quantity", 50))

        # Create PO
        po = {
            "supplier_id": supplier_id,
            "status": "draft",
            "items": [
                {
                    "product_id": product_id,
                    "product_name": product.get("name"),
                    "quantity": reorder_quantity,
                    "unit_price": product.get("cost_price", 0),
                    "total": reorder_quantity * (product.get("cost_price", 0) or 0),
                }
            ],
            "subtotal": reorder_quantity * (product.get("cost_price", 0) or 0),
            "tax": 0,
            "shipping": 0,
            "total": reorder_quantity * (product.get("cost_price", 0) or 0),
            "notes": f"Auto-generated reorder for {product['name']}",
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "auto_generated": True,
        }

        result = self.purchase_orders_collection.insert_one(po)
        return {"id": str(result.inserted_id), **po}

    def combine_supplier_reorders(
        self,
        supplier_id: str,
        created_by: str = "system",
    ) -> Optional[Dict]:
        """Combine multiple products from same supplier into one PO"""
        supplier = self.suppliers_collection.find_one({"_id": ObjectId(supplier_id)})
        if not supplier:
            raise ValueError(f"Supplier {supplier_id} not found")

        # Find all products from this supplier that need reordering
        products_to_reorder = list(
            self.products_collection.find(
                {
                    "supplier_id": supplier_id,
                    "auto_reorder_enabled": True,
                    "quantity": {"$lte": "$reorder_point"},
                }
            )
        )

        if not products_to_reorder:
            return None

        items = []
        subtotal = 0

        for product in products_to_reorder:
            annual_demand = product.get("annual_demand", 100)
            reorder_quantity = int(self.calculate_eoq(annual_demand))
            reorder_quantity = max(reorder_quantity, product.get("reorder_quantity", 50))

            item_total = reorder_quantity * (product.get("cost_price", 0) or 0)

            items.append(
                {
                    "product_id": str(product["_id"]),
                    "product_name": product.get("name"),
                    "quantity": reorder_quantity,
                    "unit_price": product.get("cost_price", 0),
                    "total": item_total,
                }
            )

            subtotal += item_total

        po = {
            "supplier_id": supplier_id,
            "status": "draft",
            "items": items,
            "subtotal": subtotal,
            "tax": 0,
            "shipping": 0,
            "total": subtotal,
            "notes": f"Auto-generated combined reorder from {supplier['name']}",
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "auto_generated": True,
        }

        result = self.purchase_orders_collection.insert_one(po)
        return {"id": str(result.inserted_id), **po}

    def get_reorder_candidates(self) -> List[Dict]:
        """Get all products that need reordering"""
        candidates = list(
            self.products_collection.find(
                {
                    "auto_reorder_enabled": True,
                    "quantity": {"$lte": "$reorder_point"},
                    "supplier_id": {"$exists": True, "$ne": None},
                }
            )
        )

        return [
            {
                **p,
                "_id": str(p["_id"]),
                "id": str(p["_id"]),
            }
            for p in candidates
        ]

    def get_auto_generated_pos(self, status: Optional[str] = None) -> List[Dict]:
        """Get auto-generated purchase orders"""
        query = {"auto_generated": True}
        if status:
            query["status"] = status

        pos = list(self.purchase_orders_collection.find(query).sort("created_at", -1))
        return [
            {**p, "_id": str(p["_id"]), "id": str(p["_id"])} for p in pos
        ]

    def set_auto_reorder_config(
        self,
        product_id: str,
        auto_reorder_enabled: bool,
        reorder_point: Optional[int] = None,
        reorder_quantity: Optional[int] = None,
        annual_demand: Optional[float] = None,
    ) -> Dict:
        """Set auto-reorder configuration for a product"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        update_data = {
            "auto_reorder_enabled": auto_reorder_enabled,
        }

        if reorder_point is not None:
            update_data["reorder_point"] = reorder_point
        if reorder_quantity is not None:
            update_data["reorder_quantity"] = reorder_quantity
        if annual_demand is not None:
            update_data["annual_demand"] = annual_demand

        self.products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data},
        )

        updated = self.products_collection.find_one({"_id": ObjectId(product_id)})
        return {**updated, "_id": str(updated["_id"]), "id": str(updated["_id"])}

    def get_auto_reorder_config(self, product_id: str) -> Dict:
        """Get auto-reorder configuration for a product"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        return {
            "product_id": product_id,
            "auto_reorder_enabled": product.get("auto_reorder_enabled", False),
            "reorder_point": product.get("reorder_point", 10),
            "reorder_quantity": product.get("reorder_quantity", 50),
            "annual_demand": product.get("annual_demand", 100),
            "current_quantity": product.get("quantity", 0),
            "supplier_id": product.get("supplier_id"),
        }
