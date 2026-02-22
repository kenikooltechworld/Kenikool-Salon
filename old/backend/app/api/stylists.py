"""
API endpoints for stylist management with location-based filtering.
Handles stylist CRUD operations and location assignments.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Body
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.api.dependencies import get_current_user, get_tenant_id, require_owner_or_admin
from app.database import Database
from app.services.stylist_service import StylistService
from app.schemas.stylist import StylistCreate, StylistUpdate, StylistResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stylists", tags=["stylists"])


def get_db():
    """Get database instance"""
    return Database.get_db()


# ============================================================================
# Stylist Photo Upload Endpoint
# ============================================================================

@router.post("/{stylist_id}/photo", response_model=StylistResponse)
async def upload_stylist_photo(
    stylist_id: str,
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Upload a photo for a stylist"""
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Upload to Cloudinary
        stylist = await StylistService.upload_stylist_photo(
            stylist_id, tenant_id, file_bytes
        )
        return stylist
    except Exception as e:
        logger.error(f"Error uploading stylist photo: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Stylist CRUD Endpoints
# ============================================================================


@router.get("", response_model=List[StylistResponse])
async def get_stylists(
    location_id: Optional[str] = Query(None, description="Filter by location ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get all stylists for a tenant with optional location filtering.
    
    If location_id is provided, returns only stylists assigned to that location.
    Otherwise, returns all stylists for the tenant.
    
    Requirements: 4.1, 4.3
    """
    try:
        if location_id:
            # Get stylists by location
            stylists = await StylistService.get_by_location(tenant_id, location_id)
        else:
            # Get all stylists
            stylists = await StylistService.get_stylists(tenant_id, is_active=is_active)
        
        return stylists
    except Exception as e:
        logger.error(f"Error getting stylists: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{stylist_id}", response_model=StylistResponse)
async def get_stylist(
    stylist_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get a single stylist by ID"""
    try:
        stylist = await StylistService.get_stylist(stylist_id, tenant_id)
        return stylist
    except Exception as e:
        logger.error(f"Error getting stylist: {e}")
        raise HTTPException(status_code=404, detail="Stylist not found")


@router.post("", response_model=StylistResponse)
async def create_stylist(
    request: StylistCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Create a new stylist"""
    try:
        stylist = await StylistService.create_stylist(
            tenant_id=tenant_id,
            name=request.name,
            phone=request.phone,
            email=request.email,
            bio=request.bio,
            photo=request.photo,
            specialties=request.specialties,
            commission_type=request.commission_type,
            commission_value=request.commission_value,
            schedule=request.schedule.dict() if request.schedule else None,
            assigned_locations=request.assigned_locations,
            location_availability=request.location_availability,
        )
        return stylist
    except Exception as e:
        logger.error(f"Error creating stylist: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{stylist_id}", response_model=StylistResponse)
async def update_stylist(
    stylist_id: str,
    request: StylistUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Update a stylist"""
    try:
        stylist = await StylistService.update_stylist(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
            name=request.name,
            email=request.email,
            phone=request.phone,
            bio=request.bio,
            photo=request.photo,
            is_active=request.is_active,
            specialties=request.specialties,
            commission_type=request.commission_type,
            commission_value=request.commission_value,
            schedule=request.schedule.dict() if request.schedule else None,
            assigned_locations=request.assigned_locations,
            location_availability=request.location_availability,
        )
        return stylist
    except Exception as e:
        logger.error(f"Error updating stylist: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{stylist_id}", response_model=StylistResponse)
async def patch_stylist(
    stylist_id: str,
    request: StylistUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Partially update a stylist"""
    try:
        stylist = await StylistService.update_stylist(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
            name=request.name,
            email=request.email,
            phone=request.phone,
            bio=request.bio,
            photo=request.photo,
            is_active=request.is_active,
            specialties=request.specialties,
            commission_type=request.commission_type,
            commission_value=request.commission_value,
            schedule=request.schedule.dict() if request.schedule else None,
            assigned_locations=request.assigned_locations,
            location_availability=request.location_availability,
        )
        return stylist
    except Exception as e:
        logger.error(f"Error updating stylist: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{stylist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stylist(
    stylist_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Delete a stylist (hard delete - completely removes from database)"""
    try:
        await StylistService.delete_stylist(stylist_id, tenant_id)
        return None
    except Exception as e:
        logger.error(f"Error deleting stylist: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Stylist Schedule Endpoint
# ============================================================================

@router.patch("/{stylist_id}/schedule", response_model=StylistResponse)
async def update_stylist_schedule(
    stylist_id: str,
    request: dict = Body(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Update a stylist's schedule"""
    try:
        schedule = request.get("schedule", {})
        stylist = await StylistService.update_stylist(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
            schedule=schedule,
        )
        return stylist
    except Exception as e:
        logger.error(f"Error updating stylist schedule: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Location Assignment Endpoints
# ============================================================================


@router.post("/{stylist_id}/locations/{location_id}", response_model=StylistResponse)
async def assign_stylist_to_location(
    stylist_id: str,
    location_id: str,
    request: Optional[dict] = Body(None),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Assign a stylist to a location.
    
    Optionally include availability data in the request body.
    
    Requirements: 4.2, 4.7
    """
    try:
        availability = request.get("availability") if request else None
        stylist = await StylistService.assign_to_location(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
            location_id=location_id,
            availability=availability,
        )
        return stylist
    except Exception as e:
        logger.error(f"Error assigning stylist to location: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{stylist_id}/locations/{location_id}", response_model=StylistResponse)
async def remove_stylist_from_location(
    stylist_id: str,
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Remove a stylist from a location.
    
    Requirements: 4.2
    """
    try:
        stylist = await StylistService.remove_from_location(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
            location_id=location_id,
        )
        return stylist
    except Exception as e:
        logger.error(f"Error removing stylist from location: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{stylist_id}/locations/{location_id}/availability", response_model=StylistResponse)
async def update_stylist_location_availability(
    stylist_id: str,
    location_id: str,
    request: dict = Body(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Update a stylist's availability at a specific location.
    
    Requirements: 4.7
    """
    try:
        availability = request.get("availability", {})
        stylist = await StylistService.update_location_availability(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
            location_id=location_id,
            availability=availability,
        )
        return stylist
    except Exception as e:
        logger.error(f"Error updating stylist location availability: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Stylist Performance, Commission, and Attendance Endpoints
# ============================================================================


@router.get("/{stylist_id}/performance")
async def get_stylist_performance(
    stylist_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get stylist performance metrics"""
    try:
        performance = await StylistService.get_stylist_performance(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
        )
        return performance
    except Exception as e:
        logger.error(f"Error getting stylist performance: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{stylist_id}/commissions")
async def get_stylist_commissions(
    stylist_id: str,
    start_date: str = Query(..., description="Start date (ISO format)"),
    end_date: str = Query(..., description="End date (ISO format)"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get stylist commission records for a date range"""
    try:
        commissions = await StylistService.get_stylist_commissions(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
        )
        return commissions
    except Exception as e:
        logger.error(f"Error getting stylist commissions: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{stylist_id}/attendance")
async def get_stylist_attendance(
    stylist_id: str,
    month: str = Query(..., description="Month (YYYY-MM format)"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get stylist attendance records for a month"""
    try:
        attendance = await StylistService.get_stylist_attendance(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
            month=month,
        )
        return attendance
    except Exception as e:
        logger.error(f"Error getting stylist attendance: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{stylist_id}/current-hours")
async def get_current_hours_worked(
    stylist_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get current hours worked for today (if clocked in)"""
    try:
        hours = await StylistService.get_current_hours_worked(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
        )
        return {"hours_worked": hours}
    except Exception as e:
        logger.error(f"Error getting current hours: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{stylist_id}/clock-in")
async def clock_in_stylist(
    stylist_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Clock in a stylist"""
    try:
        result = await StylistService.clock_in(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
        )
        return result
    except Exception as e:
        logger.error(f"Error clocking in stylist: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{stylist_id}/clock-out")
async def clock_out_stylist(
    stylist_id: str,
    request: dict = Body(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Clock out a stylist"""
    try:
        attendance_id = request.get("attendance_id")
        if not attendance_id:
            raise HTTPException(status_code=400, detail="attendance_id is required")
        
        result = await StylistService.clock_out(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
            attendance_id=attendance_id,
        )
        return result
    except Exception as e:
        logger.error(f"Error clocking out stylist: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{stylist_id}/assign-services")
async def assign_services_to_stylist(
    stylist_id: str,
    request: dict = Body(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Assign services to a stylist"""
    try:
        service_ids = request.get("service_ids", [])
        stylist = await StylistService.assign_services(
            stylist_id=stylist_id,
            tenant_id=tenant_id,
            service_ids=service_ids,
        )
        return stylist
    except Exception as e:
        logger.error(f"Error assigning services to stylist: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Emergency Contacts Endpoints
# ============================================================================

@router.get("/{stylist_id}/emergency-contacts")
async def get_emergency_contacts(
    stylist_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get emergency contacts for a stylist"""
    try:
        db_instance = Database.get_db()
        stylist = db_instance.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if not stylist:
            raise HTTPException(status_code=404, detail="Stylist not found")
        
        emergency_contacts = stylist.get("emergency_contacts", [])
        return {"emergency_contacts": emergency_contacts}
    except Exception as e:
        logger.error(f"Error getting emergency contacts: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{stylist_id}/emergency-contacts")
async def add_emergency_contact(
    stylist_id: str,
    request: dict = Body(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Add an emergency contact for a stylist"""
    try:
        db_instance = Database.get_db()
        
        contact = {
            "name": request.get("name"),
            "relationship": request.get("relationship"),
            "phone": request.get("phone"),
            "email": request.get("email"),
        }
        
        db_instance.stylists.update_one(
            {"_id": ObjectId(stylist_id), "tenant_id": tenant_id},
            {"$push": {"emergency_contacts": contact}}
        )
        
        return {"message": "Emergency contact added", "contact": contact}
    except Exception as e:
        logger.error(f"Error adding emergency contact: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{stylist_id}/medical-info")
async def get_medical_info(
    stylist_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get medical information for a stylist"""
    try:
        db_instance = Database.get_db()
        stylist = db_instance.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if not stylist:
            raise HTTPException(status_code=404, detail="Stylist not found")
        
        medical_info = stylist.get("medical_info", {})
        return medical_info
    except Exception as e:
        logger.error(f"Error getting medical info: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{stylist_id}/medical-info")
async def update_medical_info(
    stylist_id: str,
    request: dict = Body(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Update medical information for a stylist"""
    try:
        db_instance = Database.get_db()
        
        medical_info = {
            "allergies": request.get("allergies", []),
            "blood_type": request.get("blood_type"),
            "medications": request.get("medications", []),
            "conditions": request.get("conditions", []),
        }
        
        db_instance.stylists.update_one(
            {"_id": ObjectId(stylist_id), "tenant_id": tenant_id},
            {"$set": {"medical_info": medical_info, "updated_at": datetime.utcnow()}}
        )
        
        return {"message": "Medical info updated", "medical_info": medical_info}
    except Exception as e:
        logger.error(f"Error updating medical info: {e}")
        raise HTTPException(status_code=400, detail=str(e))
