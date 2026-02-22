"""
Service Inquiry API endpoints - Handle custom service requests with image uploads
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from typing import Optional
from bson import ObjectId
from datetime import datetime
import logging

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/service-inquiries", tags=["service-inquiries"])


def get_db():
    """Get database instance"""
    return Database.get_db()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_service_inquiry(
    client_id: str = Query(...),
    service_name: str = Query(...),
    description: str = Query(...),
    estimated_price: Optional[float] = Query(None),
    file: Optional[UploadFile] = File(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Create a service inquiry with optional image upload"""
    db = get_db()
    
    try:
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Upload image to Cloudinary if provided
        photo_url = None
        if file:
            try:
                from app.services.cloudinary_service import upload_image
                
                file_bytes = await file.read()
                photo_url = await upload_image(
                    file_bytes,
                    folder=f"salon/service-inquiries/{tenant_id}",
                    public_id=None
                )
            except Exception as e:
                logger.error(f"Error uploading inquiry image: {e}")
                raise HTTPException(status_code=400, detail=f"Image upload failed: {str(e)}")
        
        # Create inquiry
        inquiry = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "service_name": service_name,
            "description": description,
            "estimated_price": estimated_price,
            "photo_url": photo_url,
            "status": "pending",
            "response": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.service_inquiries.insert_one(inquiry)
        inquiry["_id"] = str(result.inserted_id)
        
        logger.info(f"Created service inquiry {result.inserted_id} for client {client_id}")
        
        return inquiry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating service inquiry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=dict)
async def list_service_inquiries(
    status: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """List service inquiries"""
    db = get_db()
    
    try:
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status
        if client_id:
            query["client_id"] = client_id
        
        total = db.service_inquiries.count_documents(query)
        
        inquiries = list(
            db.service_inquiries.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Convert ObjectIds to strings
        for inquiry in inquiries:
            inquiry["_id"] = str(inquiry["_id"])
        
        return {
            "items": inquiries,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error listing service inquiries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{inquiry_id}", response_model=dict)
async def get_service_inquiry(
    inquiry_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get a single service inquiry"""
    db = get_db()
    
    try:
        inquiry = db.service_inquiries.find_one({
            "_id": ObjectId(inquiry_id),
            "tenant_id": tenant_id
        })
        
        if not inquiry:
            raise HTTPException(status_code=404, detail="Inquiry not found")
        
        inquiry["_id"] = str(inquiry["_id"])
        
        return inquiry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service inquiry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{inquiry_id}/respond", response_model=dict)
async def respond_to_inquiry(
    inquiry_id: str,
    response: str = Query(...),
    status_param: str = Query(..., alias="status"),
    custom_service_name: Optional[str] = Query(None),
    custom_service_price: Optional[float] = Query(None),
    custom_service_duration: Optional[int] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Respond to a service inquiry"""
    db = get_db()
    
    try:
        inquiry = db.service_inquiries.find_one({
            "_id": ObjectId(inquiry_id),
            "tenant_id": tenant_id
        })
        
        if not inquiry:
            raise HTTPException(status_code=404, detail="Inquiry not found")
        
        # Update inquiry
        update_data = {
            "status": status_param,
            "response": response,
            "updated_at": datetime.utcnow()
        }
        
        # If approved and custom service details provided, create service
        if status_param == "approved" and custom_service_name:
            service = {
                "tenant_id": tenant_id,
                "name": custom_service_name,
                "description": inquiry.get("description", ""),
                "price": custom_service_price or inquiry.get("estimated_price", 0),
                "duration_minutes": custom_service_duration or 60,
                "category": "custom",
                "photo_url": inquiry.get("photo_url"),
                "is_active": True,
                "locations": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            
            result = db.services.insert_one(service)
            update_data["custom_service_id"] = str(result.inserted_id)
        
        db.service_inquiries.update_one(
            {"_id": ObjectId(inquiry_id)},
            {"$set": update_data}
        )
        
        # Get updated inquiry
        updated_inquiry = db.service_inquiries.find_one({"_id": ObjectId(inquiry_id)})
        updated_inquiry["_id"] = str(updated_inquiry["_id"])
        
        logger.info(f"Responded to inquiry {inquiry_id} with status {status_param}")
        
        return updated_inquiry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error responding to inquiry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{inquiry_id}/convert", response_model=dict)
async def convert_inquiry_to_booking(
    inquiry_id: str,
    booking_date: str = Query(...),
    stylist_id: str = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Convert approved inquiry to booking"""
    db = get_db()
    
    try:
        inquiry = db.service_inquiries.find_one({
            "_id": ObjectId(inquiry_id),
            "tenant_id": tenant_id,
            "status": "approved"
        })
        
        if not inquiry:
            raise HTTPException(status_code=404, detail="Approved inquiry not found")
        
        # Get or create service
        service_id = inquiry.get("custom_service_id")
        if not service_id:
            raise HTTPException(status_code=400, detail="No service associated with this inquiry")
        
        # Create booking
        booking = {
            "tenant_id": tenant_id,
            "client_id": inquiry.get("client_id"),
            "service_id": service_id,
            "stylist_id": stylist_id,
            "booking_date": datetime.fromisoformat(booking_date),
            "status": "confirmed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.bookings.insert_one(booking)
        
        # Update inquiry
        db.service_inquiries.update_one(
            {"_id": ObjectId(inquiry_id)},
            {
                "$set": {
                    "status": "converted",
                    "booking_id": str(result.inserted_id),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Converted inquiry {inquiry_id} to booking {result.inserted_id}")
        
        return {
            "booking_id": str(result.inserted_id),
            "message": "Inquiry converted to booking successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting inquiry to booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))
