"""
API endpoints for service management with location-based filtering.
Handles service CRUD operations and location assignments.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database
from app.services.service_service import ServiceManagementService
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/services", tags=["services"])


def get_db():
    """Get database instance"""
    return Database.get_db()


# ============================================================================
# Service CRUD Endpoints
# ============================================================================

# Upload endpoint MUST come before /{service_id} routes
@router.post("/upload", response_model=dict)
async def upload_service_image(
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Upload an image for a service (returns URL only, no service update)"""
    try:
        from app.services.cloudinary_service import upload_image
        
        # Read file bytes
        file_bytes = await file.read()
        
        # Upload to Cloudinary
        url = await upload_image(
            file_bytes,
            folder=f"salon/services/{tenant_id}",
            public_id=None
        )
        
        return {"url": url}
    except Exception as e:
        logger.error(f"Error uploading service image: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{service_id}/photo", response_model=ServiceResponse)
async def upload_service_photo(
    service_id: str,
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Upload a photo for a service"""
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Upload to Cloudinary
        service = await ServiceManagementService.upload_service_photo(
            service_id, tenant_id, file_bytes
        )
        return service
    except Exception as e:
        logger.error(f"Error uploading service photo: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[ServiceResponse])
async def get_services(
    location_id: Optional[str] = Query(None, description="Filter by location ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get all services for a tenant with optional location filtering.
    
    If location_id is provided, returns only services available at that location.
    Otherwise, returns all services for the tenant.
    
    Requirements: 5.1, 5.3
    """
    try:
        logger.info(f"📋 GET /api/services - tenant_id: {tenant_id}, location_id: {location_id}, is_active: {is_active}")
        
        if location_id:
            # Get services by location
            services = await ServiceManagementService.get_by_location(tenant_id, location_id)
        else:
            # Get all services
            services = await ServiceManagementService.get_services(tenant_id, is_active=is_active)
        
        logger.info(f"✅ Returning {len(services)} services for tenant {tenant_id}")
        return services
    except Exception as e:
        logger.error(f"❌ Error getting services: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Service Templates Endpoints (MUST be before /{service_id})
# ============================================================================


@router.get("/templates", response_model=dict)
async def list_service_templates(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get all service templates for tenant or global templates"""
    try:
        # Try to get tenant-specific templates first, then fall back to global templates
        templates = list(db.service_templates.find({"$or": [{"tenant_id": tenant_id}, {"tenant_id": {"$exists": False}}]}))
        
        # Convert ObjectIds to strings and format response
        formatted_templates = []
        for template in templates:
            formatted_templates.append({
                "id": str(template["_id"]),
                "name": template.get("name"),
                "description": template.get("description", ""),
                "category": template.get("category"),
                "is_default": template.get("is_default", False),
                "template_data": {
                    "price": template.get("price", 0),
                    "duration_minutes": template.get("duration", 0),
                    "category": template.get("category"),
                    "description": template.get("description", ""),
                    "color": template.get("color"),
                    "icon": template.get("icon"),
                }
            })
        
        return {
            "templates": formatted_templates,
            "total": len(formatted_templates),
        }
    except Exception as e:
        logger.error(f"Error getting service templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_service_template(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Create a new service template"""
    try:
        # Validate required fields
        if not data.get("name"):
            raise HTTPException(status_code=400, detail="Template name is required")
        
        template_doc = {
            "tenant_id": tenant_id,
            "name": data.get("name"),
            "description": data.get("description", ""),
            "category": data.get("category"),
            "duration": data.get("duration"),
            "price": data.get("price"),
            "color": data.get("color"),
            "icon": data.get("icon"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.service_templates.insert_one(template_doc)
        template_doc["id"] = str(result.inserted_id)
        del template_doc["_id"]
        
        logger.info(f"Created service template {result.inserted_id} for tenant {tenant_id}")
        return template_doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating service template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/{template_id}/create-service", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_service_from_template(
    template_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Create a service from a template"""
    try:
        # Get the template
        template = db.service_templates.find_one({
            "_id": ObjectId(template_id),
            "$or": [{"tenant_id": tenant_id}, {"tenant_id": {"$exists": False}}]
        })
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Get customizations
        customizations = data.get("customizations", {})
        
        # Create service from template
        service_doc = {
            "tenant_id": tenant_id,
            "name": data.get("name", template.get("name")),
            "description": customizations.get("description") or template.get("description", ""),
            "category": customizations.get("category") or template.get("category"),
            "duration": customizations.get("duration_minutes") or template.get("duration"),
            "price": customizations.get("price") or template.get("price"),
            "color": template.get("color"),
            "icon": template.get("icon"),
            "photo_url": customizations.get("photo_url"),
            "is_active": True,
            "locations": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.services.insert_one(service_doc)
        service_doc["id"] = str(result.inserted_id)
        del service_doc["_id"]
        
        logger.info(f"Created service {result.inserted_id} from template {template_id} with photo_url: {customizations.get('photo_url')}")
        return service_doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating service from template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{service_id}/details", response_model=dict)
async def get_service_details(
    service_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get service details with statistics.
    
    Returns both the service information and statistics.
    """
    try:
        from datetime import datetime as dt, timedelta
        
        # Check if service_id is a valid ObjectId format
        if not service_id or not (len(service_id) == 24 and all(c in '0123456789abcdef' for c in service_id.lower())):
            # If it's a temporary ID (starts with 'temp_'), return a placeholder response
            if service_id.startswith('temp_'):
                return {
                    "service": {
                        "id": service_id,
                        "name": "New Service",
                        "description": "",
                        "price": 0,
                        "duration_minutes": 0,
                        "category": "",
                        "is_active": True,
                        "assigned_stylists": [],
                        "photo_url": None,
                        "tiered_pricing": [],
                        "booking_rules": None,
                        "availability": None,
                        "max_concurrent_bookings": 0,
                        "commission_structure": None,
                        "required_resources": [],
                        "marketing_settings": None,
                        "variants": [],
                        "recommendations": [],
                    },
                    "statistics": {
                        "total_bookings": 0,
                        "completed_bookings": 0,
                        "cancelled_bookings": 0,
                        "total_revenue": 0,
                        "average_booking_value": 0,
                        "revenue_trend": None,
                        "popularity_rank": 0,
                        "average_rating": 0,
                        "conversion_rate": 0,
                    },
                }
            raise HTTPException(status_code=400, detail="Invalid service ID format")
        
        service = await ServiceManagementService.get_service(service_id, tenant_id)
        
        # Get real statistics from bookings collection
        # Current period (last 90 days)
        end_date = dt.utcnow()
        start_date = end_date - timedelta(days=90)
        
        current_bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "service_id": service_id,
            "booking_date": {"$gte": start_date, "$lte": end_date}
        }))
        
        # Previous period (90 days before current)
        prev_end = start_date
        prev_start = start_date - timedelta(days=90)
        
        prev_bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "service_id": service_id,
            "booking_date": {"$gte": prev_start, "$lte": prev_end}
        }))
        
        # Calculate current period metrics
        total_bookings = len(current_bookings)
        completed_bookings = len([b for b in current_bookings if b.get("status") == "completed"])
        cancelled_bookings = len([b for b in current_bookings if b.get("status") == "cancelled"])
        
        total_revenue = sum(b.get("service_price", 0) for b in current_bookings)
        average_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0
        
        # Calculate previous period revenue for trend
        prev_revenue = sum(b.get("service_price", 0) for b in prev_bookings)
        revenue_trend = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        # Get average rating from reviews
        reviews = list(db.reviews.find({
            "tenant_id": tenant_id,
            "service_id": service_id,
            "status": "approved"
        }))
        
        average_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews) if reviews else 0
        
        # Calculate conversion rate (completed / total)
        conversion_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        # Get popularity rank (compare with other services)
        all_services_bookings = db.bookings.aggregate([
            {"$match": {"tenant_id": tenant_id, "booking_date": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {"_id": "$service_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ])
        
        popularity_rank = 0
        for idx, service_booking in enumerate(all_services_bookings, 1):
            if service_booking["_id"] == service_id:
                popularity_rank = idx
                break
        
        statistics = {
            "totalBookings": total_bookings,
            "completedBookings": completed_bookings,
            "cancelledBookings": cancelled_bookings,
            "totalRevenue": round(total_revenue, 2),
            "averageBookingValue": round(average_booking_value, 2),
            "revenueTrend": round(revenue_trend, 1),
            "popularityRank": popularity_rank,
            "averageRating": round(average_rating, 1),
            "conversionRate": round(conversion_rate, 1),
        }
        
        return {
            "service": service,
            "statistics": statistics,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service details: {e}")
        raise HTTPException(status_code=404, detail="Service not found")


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: str,
    location_id: Optional[str] = Query(None, description="Get location-specific pricing"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get a single service by ID.
    
    If location_id is provided, includes location-specific pricing in response.
    
    Requirements: 5.1, 5.3
    """
    try:
        service = await ServiceManagementService.get_service(service_id, tenant_id)
        
        # Add location-specific pricing if requested
        if location_id:
            pricing = await ServiceManagementService.get_location_pricing(
                service_id, tenant_id, location_id
            )
            service["location_pricing_override"] = pricing
        
        return service
    except Exception as e:
        logger.error(f"Error getting service: {e}")
        raise HTTPException(status_code=404, detail="Service not found")
    except Exception as e:
        logger.error(f"Error getting service details: {e}")
        raise HTTPException(status_code=404, detail="Service not found")


@router.post("", response_model=ServiceResponse)
async def create_service(
    request: ServiceCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Create a new service"""
    try:
        service = await ServiceManagementService.create_service(
            tenant_id=tenant_id,
            name=request.name,
            price=request.price,
            duration_minutes=request.duration_minutes,
            description=request.description,
            category=request.category,
            assigned_stylists=request.assigned_stylists,
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            tiered_pricing=request.tiered_pricing,
            booking_rules=request.booking_rules.dict() if request.booking_rules else None,
            availability=request.availability.dict() if request.availability else None,
            max_concurrent_bookings=request.max_concurrent_bookings,
            commission_structure=request.commission_structure.dict() if request.commission_structure else None,
            required_resources=request.required_resources,
            marketing_settings=request.marketing_settings.dict() if request.marketing_settings else None,
        )
        return service
    except Exception as e:
        logger.error(f"Error creating service: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: str,
    request: ServiceUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Update a service"""
    try:
        # Validate service ID format
        if not (len(service_id) == 24 and all(c in '0123456789abcdef' for c in service_id.lower())):
            raise HTTPException(status_code=400, detail="Invalid service ID format")
        
        # Convert location_pricing from Pydantic models to dicts if needed
        location_pricing = getattr(request, 'location_pricing', None)
        if location_pricing and isinstance(location_pricing, list) and len(location_pricing) > 0:
            if hasattr(location_pricing[0], 'dict'):
                location_pricing = [lp.dict() for lp in location_pricing]
        
        service = await ServiceManagementService.update_service(
            service_id=service_id,
            tenant_id=tenant_id,
            name=request.name,
            description=request.description,
            price=request.price,
            duration_minutes=request.duration_minutes,
            category=request.category,
            is_active=request.is_active,
            assigned_stylists=request.assigned_stylists,
            available_at_locations=getattr(request, 'available_at_locations', None),
            location_pricing=location_pricing,
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            tiered_pricing=request.tiered_pricing,
            booking_rules=request.booking_rules.dict() if request.booking_rules else None,
            availability=request.availability.dict() if request.availability else None,
            max_concurrent_bookings=request.max_concurrent_bookings,
            commission_structure=request.commission_structure.dict() if request.commission_structure else None,
            required_resources=request.required_resources,
            marketing_settings=request.marketing_settings.dict() if request.marketing_settings else None,
        )
        return service
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{service_id}", response_model=ServiceResponse)
async def patch_service(
    service_id: str,
    request: ServiceUpdate,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Partially update a service"""
    try:
        # Validate service ID format
        if not (len(service_id) == 24 and all(c in '0123456789abcdef' for c in service_id.lower())):
            raise HTTPException(status_code=400, detail="Invalid service ID format")
        
        # Convert location_pricing from Pydantic models to dicts if needed
        location_pricing = getattr(request, 'location_pricing', None)
        if location_pricing and isinstance(location_pricing, list) and len(location_pricing) > 0:
            if hasattr(location_pricing[0], 'dict'):
                location_pricing = [lp.dict() for lp in location_pricing]
        
        service = await ServiceManagementService.update_service(
            service_id=service_id,
            tenant_id=tenant_id,
            name=request.name,
            description=request.description,
            price=request.price,
            duration_minutes=request.duration_minutes,
            category=request.category,
            is_active=request.is_active,
            assigned_stylists=request.assigned_stylists,
            available_at_locations=getattr(request, 'available_at_locations', None),
            location_pricing=location_pricing,
            user_id=current_user.get("id"),
            user_email=current_user.get("email"),
            tiered_pricing=request.tiered_pricing,
            booking_rules=request.booking_rules.dict() if request.booking_rules else None,
            availability=request.availability.dict() if request.availability else None,
            max_concurrent_bookings=request.max_concurrent_bookings,
            commission_structure=request.commission_structure.dict() if request.commission_structure else None,
            required_resources=request.required_resources,
            marketing_settings=request.marketing_settings.dict() if request.marketing_settings else None,
        )
        return service
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error patching service: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Delete a service (soft delete)"""
    try:
        await ServiceManagementService.delete_service(
            service_id, tenant_id,
            user_id=current_user.get("id"),
            user_email=current_user.get("email")
        )
        return None
    except Exception as e:
        logger.error(f"Error deleting service: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{service_id}/availability", response_model=ServiceResponse)
async def update_service_availability(
    service_id: str,
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """Update service availability settings"""
    try:
        # Get existing service
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Update availability
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": {
                "availability": request,
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Fetch and return updated service
        updated_service = db.services.find_one({"_id": ObjectId(service_id)})
        return ServiceManagementService._format_service_response(updated_service)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service availability: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{service_id}/duplicate", response_model=ServiceResponse)
async def duplicate_service(
    service_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Duplicate a service with all its settings.
    
    Creates a copy of the service with a new name (original name + " (Copy)").
    """
    try:
        # Check if service_id is a valid ObjectId format
        if service_id.startswith('temp_'):
            raise HTTPException(status_code=400, detail="Cannot duplicate a service that hasn't been saved yet. Please save the service first.")
        
        if not (len(service_id) == 24 and all(c in '0123456789abcdef' for c in service_id.lower())):
            raise HTTPException(status_code=400, detail="Invalid service ID format")
        
        # Get the original service
        original_service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not original_service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Create a copy
        duplicate_doc = {
            "tenant_id": tenant_id,
            "name": f"{original_service.get('name')} (Copy)",
            "description": original_service.get("description"),
            "category": original_service.get("category"),
            "duration_minutes": original_service.get("duration_minutes"),
            "price": original_service.get("price"),
            "color": original_service.get("color"),
            "icon": original_service.get("icon"),
            "photo_url": original_service.get("photo_url"),
            "is_active": True,
            "assigned_stylists": original_service.get("assigned_stylists", []),
            "tiered_pricing": original_service.get("tiered_pricing", []),
            "booking_rules": original_service.get("booking_rules", {}),
            "availability": original_service.get("availability", {}),
            "max_concurrent_bookings": original_service.get("max_concurrent_bookings", 0),
            "commission_structure": original_service.get("commission_structure"),
            "required_resources": original_service.get("required_resources", []),
            "marketing_settings": original_service.get("marketing_settings", {}),
            "prerequisite_services": original_service.get("prerequisite_services", []),
            "mandatory_addons": original_service.get("mandatory_addons", []),
            "available_at_locations": original_service.get("available_at_locations", []),
            "location_pricing": original_service.get("location_pricing", []),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = db.services.insert_one(duplicate_doc)
        
        logger.info(f"Duplicated service {service_id} to {result.inserted_id}")
        
        # Fetch and return the duplicated service using the proper formatter
        duplicated_service = db.services.find_one({"_id": result.inserted_id})
        return ServiceManagementService._format_service_response(duplicated_service)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error duplicating service: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error duplicating service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Location Assignment Endpoints
# ============================================================================


@router.post("/{service_id}/locations/{location_id}", response_model=ServiceResponse)
async def assign_service_to_location(
    service_id: str,
    location_id: str,
    request: Optional[dict] = None,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Make a service available at a location.
    
    Optionally include location-specific pricing in the request body:
    {
        "location_price": 50.0,
        "location_duration": 30
    }
    
    Requirements: 5.1, 5.6
    """
    try:
        location_price = request.get("location_price") if request else None
        location_duration = request.get("location_duration") if request else None
        
        service = await ServiceManagementService.assign_to_location(
            service_id=service_id,
            tenant_id=tenant_id,
            location_id=location_id,
            location_price=location_price,
            location_duration=location_duration,
        )
        return service
    except Exception as e:
        logger.error(f"Error assigning service to location: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{service_id}/locations/{location_id}", response_model=ServiceResponse)
async def remove_service_from_location(
    service_id: str,
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Remove a service from a location.
    
    Requirements: 5.1
    """
    try:
        service = await ServiceManagementService.remove_from_location(
            service_id=service_id,
            tenant_id=tenant_id,
            location_id=location_id,
        )
        return service
    except Exception as e:
        logger.error(f"Error removing service from location: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{service_id}/locations/{location_id}/pricing", response_model=dict)
async def get_service_location_pricing(
    service_id: str,
    location_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get location-specific pricing for a service.
    
    Returns the location-specific price and duration, or default pricing if not set.
    
    Requirements: 5.1, 5.3
    """
    try:
        pricing = await ServiceManagementService.get_location_pricing(
            service_id, tenant_id, location_id
        )
        return pricing
    except Exception as e:
        logger.error(f"Error getting service location pricing: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Service Analytics Endpoints
# ============================================================================


@router.get("/{service_id}/bookings", response_model=dict)
async def get_service_bookings(
    service_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get recent bookings for a service with pagination.
    
    Returns paginated list of bookings for the service.
    """
    try:
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Get bookings for this service
        bookings_cursor = db.bookings.find({
            "tenant_id": tenant_id,
            "service_id": service_id
        }).sort("booking_date", -1).skip(skip).limit(limit)
        
        bookings = []
        for booking in bookings_cursor:
            bookings.append({
                "id": str(booking.get("_id")),
                "client_name": booking.get("client_name", "Unknown"),
                "client_id": str(booking.get("client_id", "")),
                "stylist_name": booking.get("stylist_name", "Unassigned"),
                "booking_date": booking.get("booking_date", ""),
                "status": booking.get("status", "pending"),
                "service_price": booking.get("service_price", 0),
                "variant_name": booking.get("variant_name"),
            })
        
        # Get total count
        total = db.bookings.count_documents({
            "tenant_id": tenant_id,
            "service_id": service_id
        })
        
        return {
            "bookings": bookings,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{service_id}/stylist-performance", response_model=dict)
async def get_service_stylist_performance(
    service_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get stylist performance metrics for a service.
    
    Returns performance data for each stylist assigned to this service.
    """
    try:
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Get all bookings for this service
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "service_id": service_id,
            "status": {"$in": ["completed", "confirmed"]}
        }))
        
        # Aggregate by stylist
        stylist_stats = {}
        total_revenue = 0
        
        for booking in bookings:
            stylist_id = str(booking.get("stylist_id", "unassigned"))
            stylist_name = booking.get("stylist_name", "Unassigned")
            revenue = booking.get("service_price", 0)
            
            if stylist_id not in stylist_stats:
                stylist_stats[stylist_id] = {
                    "stylist_id": stylist_id,
                    "stylist_name": stylist_name,
                    "total_bookings": 0,
                    "total_revenue": 0,
                }
            
            stylist_stats[stylist_id]["total_bookings"] += 1
            stylist_stats[stylist_id]["total_revenue"] += revenue
            total_revenue += revenue
        
        # Calculate percentages
        stylists = []
        for stylist_data in stylist_stats.values():
            percentage = (stylist_data["total_revenue"] / total_revenue * 100) if total_revenue > 0 else 0
            stylists.append({
                **stylist_data,
                "percentage_contribution": round(percentage, 1)
            })
        
        # Sort by revenue descending
        stylists.sort(key=lambda x: x["total_revenue"], reverse=True)
        
        return {
            "stylists": stylists,
            "total_revenue": total_revenue,
            "total_bookings": len(bookings),
            "total_stylists": len(stylists)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service stylist performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Service Recommendations Endpoints
# ============================================================================


@router.get("/{service_id}/capacity", response_model=dict)
async def get_service_capacity(
    service_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get service capacity information.
    
    Returns capacity settings and current utilization.
    """
    try:
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Get capacity information
        capacity_info = {
            "max_concurrent_bookings": service.get("max_concurrent_bookings", 0),
            "current_bookings": 0,
            "available_slots": service.get("max_concurrent_bookings", 0),
            "utilization_percentage": 0,
        }
        
        # Calculate current bookings if needed
        if capacity_info["max_concurrent_bookings"] > 0:
            current_bookings = db.bookings.count_documents({
                "tenant_id": tenant_id,
                "service_id": service_id,
                "status": {"$in": ["confirmed", "in_progress"]}
            })
            capacity_info["current_bookings"] = current_bookings
            capacity_info["available_slots"] = max(0, capacity_info["max_concurrent_bookings"] - current_bookings)
            capacity_info["utilization_percentage"] = round(
                (current_bookings / capacity_info["max_concurrent_bookings"] * 100) 
                if capacity_info["max_concurrent_bookings"] > 0 else 0
            )
        
        return capacity_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service capacity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{service_id}/capacity", response_model=ServiceResponse)
async def update_service_capacity(
    service_id: str,
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Update service capacity settings.
    
    Request body:
    {
        "max_concurrent_bookings": 5
    }
    """
    try:
        # Get existing service
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        max_concurrent = request.get("max_concurrent_bookings", 0)
        
        # Validate input
        if not isinstance(max_concurrent, int) or max_concurrent < 0:
            raise HTTPException(status_code=400, detail="max_concurrent_bookings must be a non-negative integer")
        
        # Update capacity
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": {
                "max_concurrent_bookings": max_concurrent,
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Fetch and return updated service
        updated_service = db.services.find_one({"_id": ObjectId(service_id)})
        return ServiceManagementService._format_service_response(updated_service)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service capacity: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{service_id}/variants", response_model=list)
async def get_service_variants(
    service_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get service variants (different versions/options of a service).
    
    Returns all variants associated with this service.
    """
    try:
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Get variants from the service document
        variants = service.get("variants", [])
        
        # Format variants response
        result = []
        for variant in variants:
            result.append({
                "id": variant.get("id", ""),
                "name": variant.get("name", ""),
                "description": variant.get("description", ""),
                "price": variant.get("price", 0),
                "duration_minutes": variant.get("duration_minutes", 0),
                "is_active": variant.get("is_active", True),
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service variants: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{service_id}/recommendations", response_model=list)
async def get_service_recommendations(
    service_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get recommended services for a service.
    
    Returns services that are frequently booked together or manually recommended.
    """
    try:
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Get recommendations from the service document
        recommendations = service.get("recommendations", [])
        
        # Fetch full service details for each recommendation
        result = []
        for rec_id in recommendations:
            try:
                rec_service = db.services.find_one({
                    "_id": ObjectId(rec_id),
                    "tenant_id": tenant_id
                })
                if rec_service:
                    result.append({
                        "id": str(rec_service["_id"]),
                        "name": rec_service.get("name"),
                        "price": rec_service.get("price", 0),
                        "duration_minutes": rec_service.get("duration", 0),
                        "category": rec_service.get("category"),
                        "photo_url": rec_service.get("photo_url"),
                        "is_manual": True,
                    })
            except:
                pass
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{service_id}/recommendations", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_service_recommendation(
    service_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Add a recommended service.
    
    Request body:
    {
        "recommended_service_id": "service_id_to_recommend"
    }
    """
    try:
        recommended_service_id = data.get("recommended_service_id")
        if not recommended_service_id:
            raise HTTPException(status_code=400, detail="recommended_service_id is required")
        
        # Verify both services exist and belong to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        recommended_service = db.services.find_one({
            "_id": ObjectId(recommended_service_id),
            "tenant_id": tenant_id
        })
        
        if not recommended_service:
            raise HTTPException(status_code=404, detail="Recommended service not found")
        
        # Add recommendation if not already present
        recommendations = service.get("recommendations", [])
        if recommended_service_id not in recommendations:
            recommendations.append(recommended_service_id)
            db.services.update_one(
                {"_id": ObjectId(service_id)},
                {"$set": {"recommendations": recommendations, "updated_at": datetime.utcnow()}}
            )
        
        logger.info(f"Added recommendation {recommended_service_id} to service {service_id}")
        return {"success": True, "message": "Recommendation added"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding service recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{service_id}/recommendations/{recommended_service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_service_recommendation(
    service_id: str,
    recommended_service_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Remove a recommended service.
    """
    try:
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Remove recommendation
        recommendations = service.get("recommendations", [])
        if recommended_service_id in recommendations:
            recommendations.remove(recommended_service_id)
            db.services.update_one(
                {"_id": ObjectId(service_id)},
                {"$set": {"recommendations": recommendations, "updated_at": datetime.utcnow()}}
            )
        
        logger.info(f"Removed recommendation {recommended_service_id} from service {service_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing service recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{service_id}/commission", response_model=dict)
async def get_service_commission(
    service_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get service commission settings.
    
    Returns commission structure for the service.
    """
    try:
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Get commission structure
        commission = service.get("commission_structure", {})
        
        # Return with defaults if not set
        return {
            "commission_type": commission.get("commission_type", "percentage"),
            "default_rate": commission.get("default_rate", 0),
            "stylist_overrides": commission.get("stylist_overrides", {}),
            "min_commission": commission.get("min_commission", 0),
            "max_commission": commission.get("max_commission", None),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service commission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{service_id}/commission", response_model=ServiceResponse)
async def update_service_commission(
    service_id: str,
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Update service commission settings.
    
    Request body:
    {
        "commission_type": "percentage",
        "default_rate": 20,
        "stylist_overrides": {
            "stylist_id": 25
        },
        "min_commission": 0,
        "max_commission": null
    }
    """
    try:
        # Get existing service
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Build commission structure
        commission_structure = {
            "commission_type": request.get("commission_type", "percentage"),
            "default_rate": request.get("default_rate", 0),
            "stylist_overrides": request.get("stylist_overrides", {}),
            "min_commission": request.get("min_commission", 0),
            "max_commission": request.get("max_commission"),
        }
        
        # Update commission
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": {
                "commission_structure": commission_structure,
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Fetch and return updated service
        updated_service = db.services.find_one({"_id": ObjectId(service_id)})
        return ServiceManagementService._format_service_response(updated_service)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service commission: {e}")
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/{service_id}/reports/performance", response_model=dict)
async def get_service_performance_report(
    service_id: str,
    start_date: Optional[str] = Query(None, description="Start date in ISO format"),
    end_date: Optional[str] = Query(None, description="End date in ISO format"),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get service performance report for a date range.
    
    Returns comprehensive metrics like bookings, revenue, ratings, etc.
    """
    try:
        from datetime import datetime as dt, timedelta
        
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Parse dates
        query_filter = {
            "tenant_id": tenant_id,
            "service_id": service_id
        }
        
        end = dt.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else dt.utcnow()
        start = dt.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else (end - timedelta(days=30))
        
        query_filter["booking_date"] = {"$gte": start, "$lte": end}
        
        # Get bookings for the period
        bookings = list(db.bookings.find(query_filter))
        
        # Calculate metrics
        total_bookings = len(bookings)
        completed_bookings = len([b for b in bookings if b.get("status") == "completed"])
        cancelled_bookings = len([b for b in bookings if b.get("status") == "cancelled"])
        
        total_revenue = sum(b.get("service_price", 0) for b in bookings)
        
        # Estimate costs (30% overhead)
        estimated_costs = total_revenue * 0.30
        profit = total_revenue - estimated_costs
        profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Get reviews for the period
        reviews_query = {
            "tenant_id": tenant_id,
            "service_id": service_id,
            "status": "approved",
            "created_at": {"$gte": start, "$lte": end}
        }
        
        reviews = list(db.reviews.find(reviews_query))
        average_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews) if reviews else 0
        
        # Calculate metrics
        cancellation_rate = (cancelled_bookings / total_bookings * 100) if total_bookings > 0 else 0
        profit_per_booking = profit / total_bookings if total_bookings > 0 else 0
        utilization_rate = (completed_bookings / total_bookings * 100) if total_bookings > 0 else 0
        
        # Get previous period for growth calculation
        prev_end = start
        prev_start = start - (end - start)
        
        prev_bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "service_id": service_id,
            "booking_date": {"$gte": prev_start, "$lte": prev_end}
        }))
        
        prev_revenue = sum(b.get("service_price", 0) for b in prev_bookings)
        revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        booking_growth = ((total_bookings - len(prev_bookings)) / len(prev_bookings) * 100) if prev_bookings else 0
        
        # Get stylist breakdown
        stylist_stats = {}
        for booking in bookings:
            stylist_id = str(booking.get("stylist_id", "unassigned"))
            
            if stylist_id not in stylist_stats:
                stylist_stats[stylist_id] = {
                    "stylist_id": stylist_id,
                    "bookings": 0,
                    "revenue": 0,
                }
            
            stylist_stats[stylist_id]["bookings"] += 1
            stylist_stats[stylist_id]["revenue"] += booking.get("service_price", 0)
        
        # Sort stylists by revenue
        top_stylists = sorted(
            stylist_stats.values(),
            key=lambda x: x["revenue"],
            reverse=True
        )[:5]
        
        # Calculate days in period
        days = (end - start).days + 1
        
        return {
            "service_id": service_id,
            "service_name": service.get("name", "Unknown Service"),
            "period": {
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "days": days,
            },
            "summary": {
                "total_bookings": total_bookings,
                "completed_bookings": completed_bookings,
                "cancelled_bookings": cancelled_bookings,
                "cancellation_rate": cancellation_rate,
                "total_revenue": total_revenue,
                "estimated_costs": estimated_costs,
                "profit": profit,
                "profit_margin": profit_margin,
            },
            "performance": {
                "utilization_rate": utilization_rate,
                "profit_per_booking": profit_per_booking,
                "average_rating": average_rating,
                "total_reviews": len(reviews),
            },
            "growth": {
                "revenue_growth": revenue_growth,
                "booking_growth": booking_growth,
            },
            "top_stylists": top_stylists,
            "revenue_trend": [],  # Can be enhanced with daily breakdown
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service performance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{service_id}/audit-log", response_model=dict)
async def get_service_audit_log(
    service_id: str,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Get audit log for a service.
    
    Returns paginated list of changes made to the service.
    """
    try:
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Get audit logs for this service
        audit_logs = list(db.audit_logs.find({
            "tenant_id": tenant_id,
            "entity_id": service_id,
            "entity_type": "service"
        }).sort("created_at", -1).skip(skip).limit(limit))
        
        # Format audit logs
        formatted_logs = []
        for log in audit_logs:
            formatted_logs.append({
                "id": str(log.get("_id")),
                "action": log.get("action", "unknown"),
                "user_id": log.get("user_id", "system"),
                "user_email": log.get("user_email", "system"),
                "changes": log.get("changes", {}),
                "timestamp": log.get("created_at"),
                "description": log.get("description", ""),
            })
        
        # Get total count
        total = db.audit_logs.count_documents({
            "tenant_id": tenant_id,
            "entity_id": service_id,
            "entity_type": "service"
        })
        
        return {
            "logs": formatted_logs,
            "total": total,
            "limit": limit,
            "skip": skip,
            "pages": (total + limit - 1) // limit if limit > 0 else 0,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service audit log: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Bulk Operations Endpoints
# ============================================================================

@router.post("/bulk/delete", status_code=status.HTTP_204_NO_CONTENT)
async def bulk_delete_services(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Delete multiple services at once.
    
    Request body:
    {
        "service_ids": ["id1", "id2", "id3"]
    }
    """
    try:
        service_ids = data.get("service_ids", [])
        if not service_ids:
            raise HTTPException(status_code=400, detail="service_ids is required")
        
        # Convert to ObjectIds
        object_ids = []
        for sid in service_ids:
            try:
                object_ids.append(ObjectId(sid))
            except:
                pass
        
        if not object_ids:
            raise HTTPException(status_code=400, detail="No valid service IDs provided")
        
        # Delete services
        result = db.services.delete_many({
            "_id": {"$in": object_ids},
            "tenant_id": tenant_id
        })
        
        logger.info(f"Bulk deleted {result.deleted_count} services for tenant {tenant_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk deleting services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/status", response_model=dict)
async def bulk_update_service_status(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Update status (active/inactive) for multiple services.
    
    Request body:
    {
        "service_ids": ["id1", "id2", "id3"],
        "is_active": true
    }
    """
    try:
        service_ids = data.get("service_ids", [])
        is_active = data.get("is_active", True)
        
        if not service_ids:
            raise HTTPException(status_code=400, detail="service_ids is required")
        
        # Convert to ObjectIds
        object_ids = []
        for sid in service_ids:
            try:
                object_ids.append(ObjectId(sid))
            except:
                pass
        
        if not object_ids:
            raise HTTPException(status_code=400, detail="No valid service IDs provided")
        
        # Update services
        result = db.services.update_many(
            {
                "_id": {"$in": object_ids},
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    "is_active": is_active,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Bulk updated status for {result.modified_count} services for tenant {tenant_id}")
        return {
            "updated_count": result.modified_count,
            "is_active": is_active
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk updating service status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/locations", response_model=dict)
async def bulk_assign_services_to_location(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Assign multiple services to a location.
    
    Request body:
    {
        "service_ids": ["id1", "id2", "id3"],
        "location_id": "location_id",
        "location_price": 50.0,
        "location_duration": 30
    }
    """
    try:
        service_ids = data.get("service_ids", [])
        location_id = data.get("location_id")
        location_price = data.get("location_price")
        location_duration = data.get("location_duration")
        
        if not service_ids:
            raise HTTPException(status_code=400, detail="service_ids is required")
        if not location_id:
            raise HTTPException(status_code=400, detail="location_id is required")
        
        # Convert to ObjectIds
        object_ids = []
        for sid in service_ids:
            try:
                object_ids.append(ObjectId(sid))
            except:
                pass
        
        if not object_ids:
            raise HTTPException(status_code=400, detail="No valid service IDs provided")
        
        # Build location pricing object
        location_pricing = {
            "location_id": location_id,
        }
        if location_price is not None:
            location_pricing["price"] = location_price
        if location_duration is not None:
            location_pricing["duration_minutes"] = location_duration
        
        # Update services - add location to available_at_locations and location_pricing
        result = db.services.update_many(
            {
                "_id": {"$in": object_ids},
                "tenant_id": tenant_id
            },
            {
                "$addToSet": {
                    "available_at_locations": location_id
                },
                "$push": {
                    "location_pricing": location_pricing
                },
                "$set": {
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Bulk assigned {result.modified_count} services to location {location_id} for tenant {tenant_id}")
        return {
            "updated_count": result.modified_count,
            "location_id": location_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk assigning services to location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/activate", response_model=dict)
async def bulk_activate_services(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Activate multiple services.
    
    Request body:
    {
        "service_ids": ["id1", "id2", "id3"]
    }
    """
    try:
        service_ids = data.get("service_ids", [])
        if not service_ids:
            raise HTTPException(status_code=400, detail="service_ids is required")
        
        # Convert to ObjectIds
        object_ids = []
        for sid in service_ids:
            try:
                object_ids.append(ObjectId(sid))
            except:
                pass
        
        if not object_ids:
            raise HTTPException(status_code=400, detail="No valid service IDs provided")
        
        # Update services
        result = db.services.update_many(
            {
                "_id": {"$in": object_ids},
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    "is_active": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Bulk activated {result.modified_count} services for tenant {tenant_id}")
        return {
            "success_count": result.modified_count,
            "failed_count": len(service_ids) - result.modified_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk activating services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/deactivate", response_model=dict)
async def bulk_deactivate_services(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Deactivate multiple services.
    
    Request body:
    {
        "service_ids": ["id1", "id2", "id3"]
    }
    """
    try:
        service_ids = data.get("service_ids", [])
        if not service_ids:
            raise HTTPException(status_code=400, detail="service_ids is required")
        
        # Convert to ObjectIds
        object_ids = []
        for sid in service_ids:
            try:
                object_ids.append(ObjectId(sid))
            except:
                pass
        
        if not object_ids:
            raise HTTPException(status_code=400, detail="No valid service IDs provided")
        
        # Update services
        result = db.services.update_many(
            {
                "_id": {"$in": object_ids},
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    "is_active": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Bulk deactivated {result.modified_count} services for tenant {tenant_id}")
        return {
            "success_count": result.modified_count,
            "failed_count": len(service_ids) - result.modified_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk deactivating services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/update-category", response_model=dict)
async def bulk_update_service_category(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Update category for multiple services.
    
    Request body:
    {
        "service_ids": ["id1", "id2", "id3"],
        "category": "Hair"
    }
    """
    try:
        service_ids = data.get("service_ids", [])
        category = data.get("category")
        
        if not service_ids:
            raise HTTPException(status_code=400, detail="service_ids is required")
        if not category:
            raise HTTPException(status_code=400, detail="category is required")
        
        # Convert to ObjectIds
        object_ids = []
        for sid in service_ids:
            try:
                object_ids.append(ObjectId(sid))
            except:
                pass
        
        if not object_ids:
            raise HTTPException(status_code=400, detail="No valid service IDs provided")
        
        # Update services
        result = db.services.update_many(
            {
                "_id": {"$in": object_ids},
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    "category": category,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Bulk updated category for {result.modified_count} services for tenant {tenant_id}")
        return {
            "success_count": result.modified_count,
            "failed_count": len(service_ids) - result.modified_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk updating service category: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/adjust-price", response_model=dict)
async def bulk_adjust_service_price(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Adjust price for multiple services.
    
    Request body:
    {
        "service_ids": ["id1", "id2", "id3"],
        "adjustment_type": "percentage" or "fixed",
        "adjustment_value": 10
    }
    """
    try:
        service_ids = data.get("service_ids", [])
        adjustment_type = data.get("adjustment_type", "percentage")
        adjustment_value = data.get("adjustment_value", 0)
        
        if not service_ids:
            raise HTTPException(status_code=400, detail="service_ids is required")
        
        # Convert to ObjectIds
        object_ids = []
        for sid in service_ids:
            try:
                object_ids.append(ObjectId(sid))
            except:
                pass
        
        if not object_ids:
            raise HTTPException(status_code=400, detail="No valid service IDs provided")
        
        # Get all services to update prices
        services = list(db.services.find({
            "_id": {"$in": object_ids},
            "tenant_id": tenant_id
        }))
        
        success_count = 0
        for service in services:
            current_price = service.get("price", 0)
            
            if adjustment_type == "percentage":
                new_price = current_price * (1 + adjustment_value / 100)
            else:  # fixed
                new_price = current_price + adjustment_value
            
            # Ensure price doesn't go negative
            new_price = max(0, new_price)
            
            db.services.update_one(
                {"_id": service["_id"]},
                {
                    "$set": {
                        "price": new_price,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            success_count += 1
        
        logger.info(f"Bulk adjusted price for {success_count} services for tenant {tenant_id}")
        return {
            "success_count": success_count,
            "failed_count": len(service_ids) - success_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk adjusting service price: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk/assign-stylist", response_model=dict)
async def bulk_assign_stylist_to_services(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Assign or remove stylist from multiple services.
    
    Request body:
    {
        "service_ids": ["id1", "id2", "id3"],
        "stylist_id": "stylist_id",
        "action": "add" or "remove"
    }
    """
    try:
        service_ids = data.get("service_ids", [])
        stylist_id = data.get("stylist_id")
        action = data.get("action", "add")
        
        if not service_ids:
            raise HTTPException(status_code=400, detail="service_ids is required")
        if not stylist_id:
            raise HTTPException(status_code=400, detail="stylist_id is required")
        
        # Convert to ObjectIds
        object_ids = []
        for sid in service_ids:
            try:
                object_ids.append(ObjectId(sid))
            except:
                pass
        
        if not object_ids:
            raise HTTPException(status_code=400, detail="No valid service IDs provided")
        
        success_count = 0
        
        if action == "add":
            # Add stylist to services
            result = db.services.update_many(
                {
                    "_id": {"$in": object_ids},
                    "tenant_id": tenant_id
                },
                {
                    "$addToSet": {
                        "assigned_stylists": stylist_id
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            success_count = result.modified_count
        else:  # remove
            # Remove stylist from services
            result = db.services.update_many(
                {
                    "_id": {"$in": object_ids},
                    "tenant_id": tenant_id
                },
                {
                    "$pull": {
                        "assigned_stylists": stylist_id
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            success_count = result.modified_count
        
        logger.info(f"Bulk {action}ed stylist {stylist_id} for {success_count} services for tenant {tenant_id}")
        return {
            "success_count": success_count,
            "failed_count": len(service_ids) - success_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error bulk assigning stylist to services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Service Variants Management Endpoints
# ============================================================================

@router.post("/{service_id}/variants", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_service_variant(
    service_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Create a new service variant.
    
    Request body:
    {
        "name": "Variant Name",
        "description": "Description",
        "price": 50.0,
        "duration_minutes": 30,
        "is_active": true
    }
    """
    try:
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Create variant with unique ID
        variant_id = str(ObjectId())
        variant = {
            "id": variant_id,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "price": data.get("price", 0),
            "duration_minutes": data.get("duration_minutes", 0),
            "is_active": data.get("is_active", True),
            "created_at": datetime.utcnow(),
        }
        
        # Add variant to service
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {
                "$push": {"variants": variant},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"Created variant {variant_id} for service {service_id}")
        return variant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating service variant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{service_id}/variants/{variant_id}", response_model=dict)
async def update_service_variant(
    service_id: str,
    variant_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Update a service variant.
    """
    try:
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Find and update variant
        variants = service.get("variants", [])
        variant_found = False
        
        for variant in variants:
            if variant.get("id") == variant_id:
                variant.update(data)
                variant["updated_at"] = datetime.utcnow()
                variant_found = True
                break
        
        if not variant_found:
            raise HTTPException(status_code=404, detail="Variant not found")
        
        # Update service with modified variants
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {
                "$set": {
                    "variants": variants,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Updated variant {variant_id} for service {service_id}")
        return variant
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service variant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{service_id}/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_variant(
    service_id: str,
    variant_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Delete a service variant.
    """
    try:
        # Verify service exists and belongs to tenant
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Remove variant from service
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {
                "$pull": {"variants": {"id": variant_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        logger.info(f"Deleted variant {variant_id} from service {service_id}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting service variant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Service Booking Rules Endpoints
# ============================================================================

@router.put("/{service_id}/booking-rules", response_model=ServiceResponse)
async def update_service_booking_rules(
    service_id: str,
    request: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db),
):
    """
    Update service booking rules.
    
    Request body:
    {
        "min_advance_booking_hours": 24,
        "max_advance_booking_days": 90,
        "cancellation_policy": "flexible",
        "requires_deposit": false,
        "deposit_percentage": 0
    }
    """
    try:
        # Get existing service
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Update booking rules
        db.services.update_one(
            {"_id": ObjectId(service_id)},
            {"$set": {
                "booking_rules": request,
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Fetch and return updated service
        updated_service = db.services.find_one({"_id": ObjectId(service_id)})
        return ServiceManagementService._format_service_response(updated_service)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service booking rules: {e}")
        raise HTTPException(status_code=400, detail=str(e))
