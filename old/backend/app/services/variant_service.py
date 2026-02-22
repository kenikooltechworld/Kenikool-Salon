from datetime import datetime
from typing import List, Dict, Optional
from bson import ObjectId
from pymongo.collection import Collection


class VariantService:
    def __init__(self, db):
        self.db = db
        self.products_collection: Collection = db.inventory
        self.variants_collection: Collection = db.inventory_variants

    def add_variant(
        self,
        product_id: str,
        variant_type: str,
        variant_value: str,
        sku: str,
        quantity: int = 0,
        price: Optional[float] = None,
        cost_price: Optional[float] = None,
    ) -> Dict:
        """Add a variant to a product"""
        product = self.products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError(f"Product {product_id} not found")

        variant = {
            "product_id": product_id,
            "type": variant_type,
            "value": variant_value,
            "sku": sku,
            "quantity": quantity,
            "price": price or product.get("price"),
            "cost_price": cost_price or product.get("cost_price"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = self.variants_collection.insert_one(variant)

        # Update product to mark it has variants
        self.products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"has_variants": True}},
        )

        return {"id": str(result.inserted_id), **variant}

    def get_product_variants(self, product_id: str) -> List[Dict]:
        """Get all variants for a product"""
        variants = list(
            self.variants_collection.find({"product_id": product_id}).sort(
                "type", 1
            )
        )
        return [
            {**v, "_id": str(v["_id"]), "id": str(v["_id"])} for v in variants
        ]

    def get_variants_by_type(self, product_id: str, variant_type: str) -> List[Dict]:
        """Get variants of a specific type"""
        variants = list(
            self.variants_collection.find(
                {"product_id": product_id, "type": variant_type}
            )
        )
        return [
            {**v, "_id": str(v["_id"]), "id": str(v["_id"])} for v in variants
        ]

    def update_variant(
        self,
        variant_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
        cost_price: Optional[float] = None,
    ) -> Dict:
        """Update variant details"""
        update_data = {"updated_at": datetime.utcnow()}

        if quantity is not None:
            update_data["quantity"] = quantity
        if price is not None:
            update_data["price"] = price
        if cost_price is not None:
            update_data["cost_price"] = cost_price

        result = self.variants_collection.update_one(
            {"_id": ObjectId(variant_id)},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            raise ValueError(f"Variant {variant_id} not found")

        variant = self.variants_collection.find_one({"_id": ObjectId(variant_id)})
        return {**variant, "_id": str(variant["_id"]), "id": str(variant["_id"])}

    def delete_variant(self, variant_id: str) -> Dict:
        """Delete a variant"""
        variant = self.variants_collection.find_one({"_id": ObjectId(variant_id)})
        if not variant:
            raise ValueError(f"Variant {variant_id} not found")

        self.variants_collection.delete_one({"_id": ObjectId(variant_id)})

        # Check if product still has variants
        remaining = self.variants_collection.count_documents(
            {"product_id": variant["product_id"]}
        )
        if remaining == 0:
            self.products_collection.update_one(
                {"_id": ObjectId(variant["product_id"])},
                {"$set": {"has_variants": False}},
            )

        return {"success": True, "message": "Variant deleted"}

    def get_variant_by_sku(self, sku: str) -> Optional[Dict]:
        """Find variant by SKU"""
        variant = self.variants_collection.find_one({"sku": sku})
        if variant:
            return {**variant, "_id": str(variant["_id"]), "id": str(variant["_id"])}
        return None

    def adjust_variant_quantity(
        self,
        variant_id: str,
        quantity_change: int,
        reason: str = "adjustment",
    ) -> Dict:
        """Adjust variant quantity"""
        variant = self.variants_collection.find_one({"_id": ObjectId(variant_id)})
        if not variant:
            raise ValueError(f"Variant {variant_id} not found")

        new_quantity = variant["quantity"] + quantity_change
        if new_quantity < 0:
            raise ValueError("Insufficient quantity")

        self.variants_collection.update_one(
            {"_id": ObjectId(variant_id)},
            {
                "$set": {"quantity": new_quantity, "updated_at": datetime.utcnow()},
                "$push": {
                    "quantity_history": {
                        "change": quantity_change,
                        "before": variant["quantity"],
                        "after": new_quantity,
                        "reason": reason,
                        "timestamp": datetime.utcnow(),
                    }
                },
            },
        )

        updated = self.variants_collection.find_one({"_id": ObjectId(variant_id)})
        return {**updated, "_id": str(updated["_id"]), "id": str(updated["_id"])}

    def get_variant_stock_summary(self, product_id: str) -> Dict:
        """Get stock summary across all variants"""
        variants = self.get_product_variants(product_id)

        total_quantity = sum(v["quantity"] for v in variants)
        total_value = sum(v["quantity"] * (v.get("price", 0) or 0) for v in variants)

        return {
            "product_id": product_id,
            "total_variants": len(variants),
            "total_quantity": total_quantity,
            "total_value": total_value,
            "variants": variants,
        }
