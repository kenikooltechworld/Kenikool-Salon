"""
Group Booking API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database
from bson import ObjectId

router = APIRouter(prefix="/api/group-bookings", tags=["group-bookings"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.get("", response_model=dict)
async def get_group_bookings(
    group_subtype: Optional[str] = Query(None, description="Filter by group subtype"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get all group bookings for tenant"""
    try:
        filters = {"tenant_id": tenant_id, "booking_type": "group"}
        
        if group_subtype:
            filters["group_subtype"] = group_subtype
        
        if status_filter:
            filters["status"] = status_filter
        
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.strptime(date_from, "%Y-%m-%d")
            if date_to:
                date_filter["$lte"] = datetime.strptime(date_to, "%Y-%m-%d")
            if date_filter:
                filters["booking_date"] = date_filter
        
        total = db.bookings.count_documents(filters)
        
        bookings = list(
            db.bookings.find(filters)
            .skip(skip)
            .limit(limit)
            .sort("booking_date", -1)
        )
        
        for booking in bookings:
            booking["id"] = str(booking["_id"])
            del booking["_id"]
        
        return {
            "items": bookings,
            "page_info": {
                "total_count": total,
                "offset": skip,
                "limit": limit,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{booking_id}", response_model=dict)
async def get_group_booking(
    booking_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get a single group booking"""
    try:
        booking = db.bookings.find_one({
            "_id": ObjectId(booking_id),
            "tenant_id": tenant_id,
            "booking_type": "group"
        })
        
        if not booking:
            raise HTTPException(status_code=404, detail="Group booking not found")
        
        booking["id"] = str(booking["_id"])
        del booking["_id"]
        return booking
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_group_booking(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Create a new group booking"""
    try:
        group_booking_doc = {
            "tenant_id": tenant_id,
            "booking_type": "group",
            "group_subtype": data.get("group_subtype"),
            "client_name": data.get("client_name"),
            "client_phone": data.get("client_phone"),
            "client_email": data.get("client_email"),
            "service_id": data.get("service_id"),
            "stylist_id": data.get("stylist_id"),
            "booking_date": datetime.fromisoformat(data.get("booking_date")) if data.get("booking_date") else None,
            "status": "pending",
            "participants": data.get("participants", []),
            "notes": data.get("notes"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.bookings.insert_one(group_booking_doc)
        group_booking_doc["id"] = str(result.inserted_id)
        del group_booking_doc["_id"]
        
        return group_booking_doc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{booking_id}", response_model=dict)
async def update_group_booking(
    booking_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Update a group booking"""
    try:
        update_doc = {}
        for field in ["client_name", "client_phone", "client_email", "notes", "participants", "status"]:
            if field in data:
                update_doc[field] = data[field]
        
        if not update_doc:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_doc["updated_at"] = datetime.utcnow()
        
        result = db.bookings.find_one_and_update(
            {"_id": ObjectId(booking_id), "tenant_id": tenant_id, "booking_type": "group"},
            {"$set": update_doc},
            return_document=True,
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Group booking not found")
        
        result["id"] = str(result["_id"])
        del result["_id"]
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_booking(
    booking_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Delete a group booking"""
    try:
        result = db.bookings.delete_one({
            "_id": ObjectId(booking_id),
            "tenant_id": tenant_id,
            "booking_type": "group"
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Group booking not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
