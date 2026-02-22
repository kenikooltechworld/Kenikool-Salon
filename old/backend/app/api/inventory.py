"""
Inventory API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from bson import ObjectId
import logging

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.get("", response_model=dict)
async def list_inventory(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    location_id: Optional[str] = Query(None, description="Filter by location"),
    search: Optional[str] = Query(None, description="Search by product name"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List inventory items for tenant"""
    db = get_db()
    
    try:
        filters = {"tenant_id": tenant_id}
        
        if location_id:
            filters["location_id"] = location_id
        
        if search:
            filters["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"sku": {"$regex": search, "$options": "i"}},
            ]
        
        # Get total count
        total = db.inventory.count_documents(filters)
        
        # Get paginated results
        items = list(
            db.inventory.find(filters)
            .skip(offset)
            .limit(limit)
            .sort("created_at", -1)
        )
        
        # Convert ObjectIds to strings
        for item in items:
            item["id"] = str(item["_id"])
            del item["_id"]
        
        return {
            "items": items,
            "page_info": {
                "total_count": total,
                "offset": offset,
                "limit": limit,
            }
        }
    except Exception as e:
        logger.error(f"Error listing inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{item_id}", response_model=dict)
async def get_inventory_item(
    item_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get a single inventory item by ID"""
    db = get_db()
    
    try:
        item = db.inventory.find_one({
            "_id": ObjectId(item_id),
            "tenant_id": tenant_id,
        })
        
        if not item:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        item["id"] = str(item["_id"])
        del item["_id"]
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inventory item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a new inventory item"""
    db = get_db()
    
    try:
        # Validate required fields
        if not data.get("name") or not data.get("sku"):
            raise HTTPException(status_code=400, detail="Name and SKU are required")
        
        # Create inventory item document
        item_doc = {
            "tenant_id": tenant_id,
            "name": data.get("name"),
            "sku": data.get("sku"),
            "quantity": data.get("quantity", 0),
            "location_id": data.get("location_id"),
            "unit_cost": data.get("unit_cost", 0),
            "reorder_level": data.get("reorder_level", 0),
            "category": data.get("category"),
            "notes": data.get("notes"),
            "created_at": __import__("datetime").datetime.utcnow(),
            "updated_at": __import__("datetime").datetime.utcnow(),
        }
        
        result = db.inventory.insert_one(item_doc)
        item_doc["id"] = str(result.inserted_id)
        del item_doc["_id"]
        
        logger.info(f"Created inventory item {result.inserted_id} for tenant {tenant_id}")
        return item_doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating inventory item: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{item_id}", response_model=dict)
async def update_inventory_item(
    item_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update an inventory item"""
    db = get_db()
    
    try:
        # Build update document
        update_doc = {}
        for field in ["name", "sku", "quantity", "location_id", "unit_cost", "reorder_level", "category", "notes"]:
            if field in data:
                update_doc[field] = data[field]
        
        if not update_doc:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_doc["updated_at"] = __import__("datetime").datetime.utcnow()
        
        result = db.inventory.find_one_and_update(
            {"_id": ObjectId(item_id), "tenant_id": tenant_id},
            {"$set": update_doc},
            return_document=True,
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        result["id"] = str(result["_id"])
        del result["_id"]
        
        logger.info(f"Updated inventory item {item_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating inventory item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Delete an inventory item"""
    db = get_db()
    
    try:
        result = db.inventory.delete_one({
            "_id": ObjectId(item_id),
            "tenant_id": tenant_id,
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Inventory item not found")
        
        logger.info(f"Deleted inventory item {item_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting inventory item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
