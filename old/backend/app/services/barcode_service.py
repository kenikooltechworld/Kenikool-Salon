"""
Barcode Service - Handles barcode scanning and lookup
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId


class BarcodeService:
    """Service for barcode scanning and product lookup"""

    def __init__(self, db):
        self.db = db
        self.products_collection = db["inventory_products"]
        # Create index for barcode/SKU lookup
        self.products_collection.create_index("sku")
        self.products_collection.create_index("barcode")

    async def find_by_barcode(
        self,
        tenant_id: str,
        barcode: str,
    ) -> Optional[Dict[str, Any]]:
        """Find product by barcode or SKU"""
        product = await self.products_collection.find_one({
            "tenant_id": tenant_id,
            "$or": [
                {"barcode": barcode},
                {"sku": barcode},
            ],
            "is_active": True,
        })

        if product:
            product["_id"] = str(product["_id"])
            return product

        return None

    async def batch_lookup(
        self,
        tenant_id: str,
        barcodes: List[str],
    ) -> Dict[str, Any]:
        """Look up multiple barcodes at once"""
        results = {
            "found": [],
            "not_found": [],
        }

        for barcode in barcodes:
            product = await self.find_by_barcode(tenant_id, barcode)
            if product:
                results["found"].append({
                    "barcode": barcode,
                    "product": product,
                })
            else:
                results["not_found"].append(barcode)

        return results

    async def get_product_details(
        self,
        tenant_id: str,
        product_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get full product details for display"""
        try:
            product = await self.products_collection.find_one({
                "_id": ObjectId(product_id),
                "tenant_id": tenant_id,
            })

            if product:
                product["_id"] = str(product["_id"])
                return product

            return None
        except Exception:
            return None

    async def update_stock_from_scan(
        self,
        tenant_id: str,
        product_id: str,
        quantity_change: int,
        user_id: str,
        reason: str = "Barcode scan adjustment",
    ) -> bool:
        """Update stock quantity from barcode scan"""
        try:
            product = await self.products_collection.find_one({
                "_id": ObjectId(product_id),
                "tenant_id": tenant_id,
            })

            if not product:
                return False

            current_quantity = product.get("quantity", 0)
            new_quantity = max(0, current_quantity + quantity_change)

            await self.products_collection.update_one(
                {
                    "_id": ObjectId(product_id),
                    "tenant_id": tenant_id,
                },
                {
                    "$set": {
                        "quantity": new_quantity,
                        "updated_at": __import__("datetime").datetime.utcnow(),
                    }
                },
            )

            return True
        except Exception:
            return False
