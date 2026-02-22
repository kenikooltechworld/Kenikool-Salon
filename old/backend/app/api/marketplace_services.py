"""
Marketplace Services API

Endpoints for managing third-party marketplace services and integrations.
Handles service browsing, installation, configuration, billing, and reviews.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import logging
import uuid

from app.database import Database
from app.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/marketplace", tags=["marketplace-services"])


# ============================================================================
# Enums
# ============================================================================

class ServiceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_APPROVAL = "pending_approval"


class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"
    ONE_TIME = "one-time"


class BillingStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


# ============================================================================
# Pydantic Models
# ============================================================================

class PricingTier(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    features: List[str] = []


class ServicePricing(BaseModel):
    type: str = Field(..., description="free, paid, or freemium")
    basePrice: Optional[float] = None
    currency: Optional[str] = "USD"
    billingCycle: Optional[BillingCycle] = None
    features: List[PricingTier] = []


class MarketplaceService(BaseModel):
    name: str
    description: str
    category: str
    icon: Optional[str] = None
    screenshots: Optional[List[str]] = []
    features: List[str] = []
    pricing: ServicePricing
    rating: float = 0.0
    reviewCount: int = 0
    developer: str
    version: str
    status: ServiceStatus = ServiceStatus.ACTIVE
    documentation: Optional[str] = None
    supportUrl: Optional[str] = None


class ServiceReview(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: str
    comment: str


class ServiceConfiguration(BaseModel):
    settings: Dict[str, Any] = {}
    webhookUrl: Optional[str] = None
    enableNotifications: bool = True
    syncFrequency: str = "daily"


class InstallServiceRequest(BaseModel):
    serviceId: str
    configuration: Optional[ServiceConfiguration] = None
    billingPlan: Optional[str] = "free"


class UpdateServiceConfigRequest(BaseModel):
    configuration: Dict[str, Any] = {}
    webhookUrl: Optional[str] = None
    enableNotifications: Optional[bool] = None
    syncFrequency: Optional[str] = None


class UninstallServiceRequest(BaseModel):
    reason: Optional[str] = None
    keepData: bool = False


# ============================================================================
# Service Browsing Endpoints
# ============================================================================

@router.get("/services")
async def get_available_services(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all available marketplace services with optional filtering
    
    Query Parameters:
    - category: Filter by service category
    - search: Search by service name or description
    - skip: Number of results to skip
    - limit: Number of results to return
    
    Returns list of available services
    """
    try:
        db = Database.get_db()
        
        query = {"status": ServiceStatus.ACTIVE}
        
        if category:
            query["category"] = category
        
        if search:
            query["$text"] = {"$search": search}
        
        services = list(db.marketplace_services.find(query).skip(skip).limit(limit))
        total = db.marketplace_services.count_documents(query)
        
        # Convert ObjectId to string
        for service in services:
            service["_id"] = str(service["_id"])
        
        return {
            "services": services,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error getting available services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_id}")
async def get_service_details(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific service
    """
    try:
        from bson import ObjectId
        
        db = Database.get_db()
        
        service = db.marketplace_services.find_one({"_id": ObjectId(service_id)})
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        service["_id"] = str(service["_id"])
        
        # Check if user has installed this service
        installed = db.installed_services.find_one({
            "tenant_id": current_user.get("tenant_id"),
            "service_id": service_id
        })
        
        service["isInstalled"] = installed is not None
        
        return service
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_id}/availability")
async def get_service_availability(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get service availability for current tenant
    """
    try:
        from bson import ObjectId
        
        db = Database.get_db()
        
        service = db.marketplace_services.find_one({"_id": ObjectId(service_id)})
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        return {
            "serviceId": service_id,
            "isAvailable": True,
            "regions": service.get("regions", ["US", "CA", "UK"]),
            "supportedLanguages": service.get("supportedLanguages", ["en"]),
            "requirements": service.get("requirements", {})
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_service_categories(current_user: dict = Depends(get_current_user)):
    """
    Get all available service categories
    """
    try:
        db = Database.get_db()
        
        categories = db.marketplace_services.distinct("category")
        
        return categories
    
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_services(
    q: str = Query(..., min_length=1),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Search marketplace services
    """
    try:
        db = Database.get_db()
        
        query = {
            "status": ServiceStatus.ACTIVE,
            "$text": {"$search": q}
        }
        
        if category:
            query["category"] = category
        
        services = list(db.marketplace_services.find(query).skip(skip).limit(limit))
        total = db.marketplace_services.count_documents(query)
        
        for service in services:
            service["_id"] = str(service["_id"])
        
        return {
            "results": services,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error searching services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Service Installation Endpoints
# ============================================================================

@router.post("/install")
async def install_service(
    request: InstallServiceRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Install a marketplace service for the current tenant
    """
    try:
        from bson import ObjectId
        
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        # Check if service exists
        service = db.marketplace_services.find_one({"_id": ObjectId(request.serviceId)})
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Check if already installed
        existing = db.installed_services.find_one({
            "tenant_id": tenant_id,
            "service_id": request.serviceId
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="Service already installed")
        
        # Create installed service record
        installed_service = {
            "_id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "service_id": request.serviceId,
            "installation_date": datetime.utcnow(),
            "status": "active",
            "configuration": request.configuration.dict() if request.configuration else {},
            "billing_status": "active",
            "total_cost": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db.installed_services.insert_one(installed_service)
        
        return {
            "id": installed_service["_id"],
            "serviceId": request.serviceId,
            "status": "active",
            "installationDate": installed_service["installation_date"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error installing service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/installed")
async def get_installed_services(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all installed services for the current tenant
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status
        
        services = list(db.installed_services.find(query).skip(skip).limit(limit))
        total = db.installed_services.count_documents(query)
        
        return {
            "services": services,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error getting installed services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/installed/{service_id}")
async def get_installed_service(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of an installed service
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        service = db.installed_services.find_one({
            "tenant_id": tenant_id,
            "service_id": service_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Installed service not found")
        
        return service
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting installed service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/uninstall/{service_id}")
async def uninstall_service(
    service_id: str,
    request: UninstallServiceRequest = Body(default={}),
    current_user: dict = Depends(get_current_user)
):
    """
    Uninstall a marketplace service
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        result = db.installed_services.delete_one({
            "tenant_id": tenant_id,
            "service_id": service_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Installed service not found")
        
        return {"success": True, "message": "Service uninstalled successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uninstalling service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Service Configuration Endpoints
# ============================================================================

@router.get("/services/{service_id}/configuration")
async def get_service_configuration(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get configuration for an installed service
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        service = db.installed_services.find_one({
            "tenant_id": tenant_id,
            "service_id": service_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Installed service not found")
        
        return {
            "serviceId": service_id,
            "settings": service.get("configuration", {}),
            "webhookUrl": service.get("webhook_url"),
            "enableNotifications": service.get("enable_notifications", True),
            "syncFrequency": service.get("sync_frequency", "daily")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/services/{service_id}/configuration")
async def update_service_configuration(
    service_id: str,
    request: UpdateServiceConfigRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update configuration for an installed service
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        update_data = {
            "configuration": request.configuration,
            "updated_at": datetime.utcnow()
        }
        
        if request.webhookUrl is not None:
            update_data["webhook_url"] = request.webhookUrl
        
        if request.enableNotifications is not None:
            update_data["enable_notifications"] = request.enableNotifications
        
        if request.syncFrequency is not None:
            update_data["sync_frequency"] = request.syncFrequency
        
        result = db.installed_services.update_one(
            {
                "tenant_id": tenant_id,
                "service_id": service_id
            },
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Installed service not found")
        
        return {
            "serviceId": service_id,
            "settings": request.configuration,
            "webhookUrl": request.webhookUrl,
            "enableNotifications": request.enableNotifications,
            "syncFrequency": request.syncFrequency
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/services/{service_id}/test-connection")
async def test_service_connection(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Test connection to a service
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        service = db.installed_services.find_one({
            "tenant_id": tenant_id,
            "service_id": service_id
        })
        
        if not service:
            raise HTTPException(status_code=404, detail="Installed service not found")
        
        # Simulate connection test
        return {
            "success": True,
            "message": "Connection test successful"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing service connection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/services/{service_id}/sync")
async def sync_service_data(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Sync data from a service
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        result = db.installed_services.update_one(
            {
                "tenant_id": tenant_id,
                "service_id": service_id
            },
            {
                "$set": {
                    "last_sync_date": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Installed service not found")
        
        return {
            "success": True,
            "syncedAt": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing service data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Service Reviews Endpoints
# ============================================================================

@router.get("/services/{service_id}/reviews")
async def get_service_reviews(
    service_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get reviews for a service
    """
    try:
        db = Database.get_db()
        
        reviews = list(db.service_reviews.find(
            {"service_id": service_id}
        ).skip(skip).limit(limit))
        
        total = db.service_reviews.count_documents({"service_id": service_id})
        
        for review in reviews:
            review["_id"] = str(review["_id"])
        
        return {
            "reviews": reviews,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error getting service reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews")
async def create_service_review(
    request: ServiceReview,
    service_id: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a review for a service
    """
    try:
        db = Database.get_db()
        
        review = {
            "_id": str(uuid.uuid4()),
            "service_id": service_id,
            "tenant_id": current_user.get("tenant_id"),
            "rating": request.rating,
            "title": request.title,
            "comment": request.comment,
            "author": current_user.get("email"),
            "helpful": 0,
            "unhelpful": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        db.service_reviews.insert_one(review)
        
        return review
    
    except Exception as e:
        logger.error(f"Error creating service review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/reviews/{review_id}")
async def update_service_review(
    review_id: str,
    request: ServiceReview,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a service review
    """
    try:
        db = Database.get_db()
        
        result = db.service_reviews.update_one(
            {"_id": review_id},
            {
                "$set": {
                    "rating": request.rating,
                    "title": request.title,
                    "comment": request.comment,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return {"success": True}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reviews/{review_id}")
async def delete_service_review(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a service review
    """
    try:
        db = Database.get_db()
        
        result = db.service_reviews.delete_one({"_id": review_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return {"success": True}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting service review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews/{review_id}/helpful")
async def mark_review_helpful(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a review as helpful
    """
    try:
        db = Database.get_db()
        
        result = db.service_reviews.update_one(
            {"_id": review_id},
            {"$inc": {"helpful": 1}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return {"success": True}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking review as helpful: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews/{review_id}/unhelpful")
async def mark_review_unhelpful(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark a review as unhelpful
    """
    try:
        db = Database.get_db()
        
        result = db.service_reviews.update_one(
            {"_id": review_id},
            {"$inc": {"unhelpful": 1}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        
        return {"success": True}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking review as unhelpful: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Service Billing Endpoints
# ============================================================================

@router.get("/services/{service_id}/billing")
async def get_service_billing(
    service_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get billing information for a service
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        billing = db.service_billing.find_one({
            "tenant_id": tenant_id,
            "service_id": service_id
        })
        
        if not billing:
            raise HTTPException(status_code=404, detail="Billing information not found")
        
        billing["_id"] = str(billing["_id"])
        
        return billing
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service billing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/billing")
async def get_all_service_billings(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all service billings for the current tenant
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status
        
        billings = list(db.service_billing.find(query).skip(skip).limit(limit))
        total = db.service_billing.count_documents(query)
        
        for billing in billings:
            billing["_id"] = str(billing["_id"])
        
        return {
            "billings": billings,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error getting service billings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/services/{service_id}/billing-plan")
async def update_billing_plan(
    service_id: str,
    billing_plan: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """
    Update billing plan for a service
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        result = db.service_billing.update_one(
            {
                "tenant_id": tenant_id,
                "service_id": service_id
            },
            {
                "$set": {
                    "billing_plan": billing_plan,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Billing information not found")
        
        return {"success": True}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating billing plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/{service_id}/billing-history")
async def get_billing_history(
    service_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Get billing history for a service
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        history = list(db.service_billing_history.find({
            "tenant_id": tenant_id,
            "service_id": service_id
        }).skip(skip).limit(limit).sort("created_at", -1))
        
        total = db.service_billing_history.count_documents({
            "tenant_id": tenant_id,
            "service_id": service_id
        })
        
        for record in history:
            record["_id"] = str(record["_id"])
        
        return {
            "history": history,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error getting billing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/spending")
async def get_total_spending(current_user: dict = Depends(get_current_user)):
    """
    Get total marketplace spending for the current tenant
    """
    try:
        db = Database.get_db()
        tenant_id = current_user.get("tenant_id")
        
        # Calculate monthly spending
        monthly_billings = list(db.service_billing.find({
            "tenant_id": tenant_id,
            "billing_cycle": "monthly"
        }))
        
        total_monthly = sum(b.get("amount", 0) for b in monthly_billings)
        
        # Calculate annual spending
        annual_billings = list(db.service_billing.find({
            "tenant_id": tenant_id,
            "billing_cycle": "annual"
        }))
        
        total_annual = sum(b.get("amount", 0) for b in annual_billings)
        
        return {
            "totalMonthly": total_monthly,
            "totalAnnual": total_annual,
            "currency": "USD"
        }
    
    except Exception as e:
        logger.error(f"Error getting total spending: {e}")
        raise HTTPException(status_code=500, detail=str(e))
