from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
from app.database import Database


class InventoryManagementService:
    
    @staticmethod
    def add_inventory_item(
        tenant_id: str,
        name: str,
        category: str,
        quantity: int,
        unit_cost: float,
        reorder_level: int,
        supplier_id: Optional[str] = None
    ) -> Dict:
        """Add inventory item"""
        db = Database.get_db()
        
        item = {
            "tenant_id": tenant_id,
            "name": name,
            "category": category,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "reorder_level": reorder_level,
            "supplier_id": ObjectId(supplier_id) if supplier_id else None,
            "status": "in_stock" if quantity > reorder_level else "low_stock",
            "created_at": datetime.utcnow()
        }
        
        result = db.inventory.insert_one(item)
        item["_id"] = str(result.inserted_id)
        
        return item
    
    @staticmethod
    def update_inventory(
        tenant_id: str,
        item_id: str,
        quantity_change: int,
        reason: str
    ) -> Dict:
        """Update inventory quantity"""
        db = Database.get_db()
        
        item = db.inventory.find_one({
            "_id": ObjectId(item_id),
            "tenant_id": tenant_id
        })
        
        if not item:
            raise ValueError("Item not found")
        
        new_quantity = item["quantity"] + quantity_change
        
        if new_quantity < 0:
            raise ValueError("Insufficient inventory")
        
        status = "in_stock" if new_quantity > item["reorder_level"] else "low_stock"
        
        db.inventory.update_one(
            {"_id": ObjectId(item_id)},
            {
                "$set": {
                    "quantity": new_quantity,
                    "status": status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Log transaction
        db.inventory_transactions.insert_one({
            "tenant_id": tenant_id,
            "item_id": ObjectId(item_id),
            "quantity_change": quantity_change,
            "reason": reason,
            "created_at": datetime.utcnow()
        })
        
        return {
            "item_id": item_id,
            "new_quantity": new_quantity,
            "status": status
        }
    
    @staticmethod
    def get_low_stock_items(tenant_id: str) -> List[Dict]:
        """Get items with low stock"""
        db = Database.get_db()
        
        items = list(db.inventory.find({
            "tenant_id": tenant_id,
            "status": "low_stock"
        }))
        
        return items
    
    @staticmethod
    def get_inventory_value(tenant_id: str) -> Dict:
        """Get total inventory value"""
        db = Database.get_db()
        
        items = list(db.inventory.find({"tenant_id": tenant_id}))
        
        total_value = sum(item["quantity"] * item["unit_cost"] for item in items)
        total_items = len(items)
        
        return {
            "total_items": total_items,
            "total_value": total_value,
            "average_item_value": total_value / total_items if total_items > 0 else 0
        }
    
    @staticmethod
    def get_inventory_by_category(tenant_id: str) -> Dict:
        """Get inventory grouped by category"""
        db = Database.get_db()
        
        pipeline = [
            {"$match": {"tenant_id": tenant_id}},
            {
                "$group": {
                    "_id": "$category",
                    "items": {"$sum": 1},
                    "total_quantity": {"$sum": "$quantity"},
                    "total_value": {"$sum": {"$multiply": ["$quantity", "$unit_cost"]}}
                }
            }
        ]
        
        return list(db.inventory.aggregate(pipeline))
