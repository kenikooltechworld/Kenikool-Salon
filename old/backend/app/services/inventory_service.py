"""
Inventory service - Business logic layer
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class InventoryService:
    """Inventory service for handling inventory business logic"""
    
    @staticmethod
    async def get_inventory_products(
        tenant_id: str,
        category: Optional[str] = None,
        low_stock: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Dict]:
        """
        Get list of inventory products with filtering
        
        Returns:
            List of inventory product dicts
        """
        db = Database.get_db()
        
        # Build query
        query = {"tenant_id": tenant_id}
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"sku": {"$regex": search, "$options": "i"}}
            ]
        
        products = list(db.inventory.find(query).sort("name", 1))
        
        # Filter by low stock if requested
        if low_stock:
            products = [p for p in products if p["quantity"] <= p["reorder_level"]]
        
        return [InventoryService._format_product_response(p) for p in products]
    
    @staticmethod
    async def get_inventory_product(product_id: str, tenant_id: str) -> Dict:
        """
        Get single inventory product by ID
        
        Returns:
            Dict with product data
        """
        db = Database.get_db()
        
        product_doc = db.inventory.find_one({
            "_id": ObjectId(product_id),
            "tenant_id": tenant_id
        })
        
        if product_doc is None:
            raise NotFoundException("Inventory product not found")
        
        return InventoryService._format_product_response(product_doc)
    
    @staticmethod
    async def create_inventory_product(
        tenant_id: str,
        name: str,
        quantity: int,
        unit: str,
        cost_price: float,
        category: Optional[str] = None,
        sku: Optional[str] = None,
        selling_price: Optional[float] = None,
        reorder_level: int = 10,
        supplier: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Create a new inventory product
        
        Returns:
            Dict with created product data
        """
        db = Database.get_db()
        
        # Check if SKU already exists for this tenant
        if sku:
            existing_product = db.inventory.find_one({
                "tenant_id": tenant_id,
                "sku": sku
            })
            
            if existing_product is not None:
                raise BadRequestException("A product with this SKU already exists")
        
        product_data = {
            "tenant_id": tenant_id,
            "name": name,
            "category": category,
            "sku": sku,
            "quantity": quantity,
            "unit": unit,
            "cost_price": cost_price,
            "selling_price": selling_price,
            "reorder_level": reorder_level,
            "supplier": supplier,
            "notes": notes,
            "transactions": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Add initial transaction
        initial_transaction = {
            "transaction_type": "initial_stock",
            "quantity": quantity,
            "reason": "Initial stock",
            "notes": "Product created",
            "created_at": datetime.utcnow()
        }
        product_data["transactions"].append(initial_transaction)
        
        result = db.inventory.insert_one(product_data)
        product_id = str(result.inserted_id)
        
        logger.info(f"Inventory product created: {product_id} for tenant: {tenant_id}")
        
        # Fetch created product
        product_doc = db.inventory.find_one({"_id": ObjectId(product_id)})
        return InventoryService._format_product_response(product_doc)
    
    @staticmethod
    async def update_inventory_product(
        product_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
        sku: Optional[str] = None,
        unit: Optional[str] = None,
        cost_price: Optional[float] = None,
        selling_price: Optional[float] = None,
        reorder_level: Optional[int] = None,
        supplier: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Update an inventory product
        
        Returns:
            Dict with updated product data
        """
        db = Database.get_db()
        
        # Check product exists and belongs to tenant
        product_doc = db.inventory.find_one({
            "_id": ObjectId(product_id),
            "tenant_id": tenant_id
        })
        
        if product_doc is None:
            raise NotFoundException("Inventory product not found")
        
        # If SKU is being updated, check uniqueness
        if sku and sku != product_doc.get("sku"):
            existing_product = db.inventory.find_one({
                "tenant_id": tenant_id,
                "sku": sku,
                "_id": {"$ne": ObjectId(product_id)}
            })
            
            if existing_product is not None:
                raise BadRequestException("A product with this SKU already exists")
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if name is not None:
            update_data["name"] = name
        if category is not None:
            update_data["category"] = category
        if sku is not None:
            update_data["sku"] = sku
        if unit is not None:
            update_data["unit"] = unit
        if cost_price is not None:
            update_data["cost_price"] = cost_price
        if selling_price is not None:
            update_data["selling_price"] = selling_price
        if reorder_level is not None:
            update_data["reorder_level"] = reorder_level
        if supplier is not None:
            update_data["supplier"] = supplier
        if notes is not None:
            update_data["notes"] = notes
        
        # Update product
        db.inventory.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Inventory product updated: {product_id}")
        
        # Fetch updated product
        product_doc = db.inventory.find_one({"_id": ObjectId(product_id)})
        return InventoryService._format_product_response(product_doc)
    
    @staticmethod
    async def adjust_inventory(
        product_id: str,
        tenant_id: str,
        adjustment_type: str,
        quantity: int,
        reason: str,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Adjust inventory quantity
        
        Returns:
            Dict with updated product data
        """
        db = Database.get_db()
        
        # Validate adjustment type
        valid_types = ["add", "remove", "set"]
        if adjustment_type not in valid_types:
            raise BadRequestException(f"Invalid adjustment type. Must be one of: {', '.join(valid_types)}")
        
        # Check product exists and belongs to tenant
        product_doc = db.inventory.find_one({
            "_id": ObjectId(product_id),
            "tenant_id": tenant_id
        })
        
        if product_doc is None:
            raise NotFoundException("Inventory product not found")
        
        current_quantity = product_doc["quantity"]
        
        # Calculate new quantity
        if adjustment_type == "add":
            new_quantity = current_quantity + quantity
        elif adjustment_type == "remove":
            new_quantity = current_quantity - quantity
            if new_quantity < 0:
                raise BadRequestException("Cannot remove more than available quantity")
        else:  # set
            new_quantity = quantity
        
        # Create transaction record
        transaction = {
            "transaction_type": adjustment_type,
            "quantity": quantity,
            "reason": reason,
            "notes": notes,
            "previous_quantity": current_quantity,
            "new_quantity": new_quantity,
            "created_at": datetime.utcnow()
        }
        
        # Update product
        db.inventory.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$set": {
                    "quantity": new_quantity,
                    "updated_at": datetime.utcnow()
                },
                "$push": {"transactions": transaction}
            }
        )
        
        # Check if now low stock and send notification
        if new_quantity <= product_doc["reorder_level"]:
            try:
                from app.services.notification_service import NotificationService
                await NotificationService.create_low_stock_notification(
                    db=db,
                    tenant_id=tenant_id,
                    product_name=product_doc["name"],
                    current_quantity=new_quantity,
                    reorder_level=product_doc["reorder_level"]
                )
            except Exception as e:
                logger.warning(f"Failed to create low stock notification: {e}")
        
        logger.info(f"Inventory adjusted: {product_id} - {adjustment_type} {quantity}")
        
        # Fetch updated product
        product_doc = db.inventory.find_one({"_id": ObjectId(product_id)})
        return InventoryService._format_product_response(product_doc)
    
    @staticmethod
    async def get_low_stock_products(tenant_id: str) -> Dict:
        """
        Get products below reorder level
        
        Returns:
            Dict with low stock products and count
        """
        db = Database.get_db()
        
        # Find products where quantity <= reorder_level
        products = list(db.inventory.find({
            "tenant_id": tenant_id,
            "$expr": {"$lte": ["$quantity", "$reorder_level"]}
        }).sort("quantity", 1))
        
        return {
            "products": [InventoryService._format_product_response(p) for p in products],
            "total_count": len(products)
        }
    
    @staticmethod
    def _format_product_response(product_doc: Dict) -> Dict:
        """Format product document for response"""
        is_low_stock = product_doc["quantity"] <= product_doc["reorder_level"]
        
        return {
            "id": str(product_doc["_id"]),
            "tenant_id": product_doc["tenant_id"],
            "name": product_doc["name"],
            "category": product_doc.get("category"),
            "sku": product_doc.get("sku"),
            "quantity": product_doc["quantity"],
            "unit": product_doc["unit"],
            "cost_price": product_doc["cost_price"],
            "selling_price": product_doc.get("selling_price"),
            "reorder_level": product_doc["reorder_level"],
            "supplier": product_doc.get("supplier"),
            "notes": product_doc.get("notes"),
            "is_low_stock": is_low_stock,
            "created_at": product_doc["created_at"],
            "updated_at": product_doc["updated_at"]
        }


# Singleton instance
inventory_service = InventoryService()
