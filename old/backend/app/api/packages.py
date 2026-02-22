"""
Package management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.schemas.package import (
    PackageCreate,
    PackageUpdate,
    PackageResponse,
    PackageListResponse,
    ServiceQuantity,
    PackageRestrictions
)
from app.schemas.package_purchase import (
    PackagePurchaseCreate,
    PackagePurchaseResponse,
    PackagePurchaseListResponse
)
from app.schemas.service_credit import (
    ServiceCreditResponse,
    CreditBalanceResponse,
    CreditReservationResponse,
    RedemptionTransactionResponse
)
from app.services.package_service import PackageService
from app.services.package_purchase_service import PackagePurchaseService
from app.services.service_credit_service import ServiceCreditService
from app.api.dependencies import get_current_user, get_db

router = APIRouter(prefix="/api/packages", tags=["packages"])


@router.post("", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
async def create_package(
    package_data: PackageCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new service package"""
    try:
        service = PackageService(db)
        
        result = await service.create_package(
            tenant_id=current_user.get("tenant_id"),
            name=package_data.name,
            description=package_data.description,
            services=[s.dict() for s in package_data.services],
            original_price=package_data.original_price,
            package_price=package_data.package_price,
            discount_percentage=package_data.discount_percentage,
            validity_days=package_data.validity_days,
            is_active=package_data.is_active,
            is_transferable=package_data.is_transferable,
            is_giftable=package_data.is_giftable,
            restrictions=package_data.restrictions.dict() if package_data.restrictions else None,
            valid_from=package_data.valid_from,
            valid_until=package_data.valid_until,
            max_redemptions=package_data.max_redemptions
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=PackageListResponse)
async def list_packages(
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """List all packages for tenant"""
    try:
        service = PackageService(db)
        
        result = await service.get_packages(
            tenant_id=current_user.get("tenant_id"),
            is_active=is_active
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{package_id}", response_model=PackageResponse)
async def get_package(
    package_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get a specific package"""
    try:
        service = PackageService(db)
        
        result = await service.get_packages(
            tenant_id=current_user.get("tenant_id")
        )
        
        packages = result.get("packages", [])
        package = next((p for p in packages if p.get("_id") == package_id), None)
        
        if not package:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
        
        return package
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{package_id}", response_model=PackageResponse)
async def update_package(
    package_id: str,
    package_data: PackageUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update a package"""
    try:
        service = PackageService(db)
        
        update_dict = package_data.dict(exclude_unset=True)
        
        # Convert ServiceQuantity objects to dicts
        if "services" in update_dict and update_dict["services"]:
            update_dict["services"] = [s.dict() if hasattr(s, "dict") else s for s in update_dict["services"]]
        
        # Convert PackageRestrictions to dict
        if "restrictions" in update_dict and update_dict["restrictions"]:
            update_dict["restrictions"] = update_dict["restrictions"].dict() if hasattr(update_dict["restrictions"], "dict") else update_dict["restrictions"]
        
        result = await service.update_package(
            package_id=package_id,
            tenant_id=current_user.get("tenant_id"),
            update_data=update_dict
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_package(
    package_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete a package"""
    try:
        service = PackageService(db)
        
        await service.delete_package(
            package_id=package_id,
            tenant_id=current_user.get("tenant_id")
        )
        
        return None
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



# Package Purchase Endpoints

@router.post("/purchases", response_model=PackagePurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_package_purchase(
    purchase_data: PackagePurchaseCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new package purchase"""
    try:
        service = PackagePurchaseService(db)
        
        result = await service.create_purchase(
            tenant_id=current_user.get("tenant_id"),
            client_id=current_user.get("client_id"),
            package_definition_id=purchase_data.package_definition_id,
            payment_method=purchase_data.payment_method,
            purchased_by_staff_id=current_user.get("user_id"),
            is_gift=purchase_data.is_gift,
            recipient_id=purchase_data.recipient_id,
            gift_message=purchase_data.gift_message
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/purchases", response_model=PackagePurchaseListResponse)
async def list_client_purchases(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """List all package purchases for current client"""
    try:
        service = PackagePurchaseService(db)
        
        purchases = await service.get_client_packages(
            client_id=current_user.get("client_id"),
            status=status
        )
        
        return {
            "purchases": purchases,
            "total": len(purchases)
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/purchases/{purchase_id}", response_model=PackagePurchaseResponse)
async def get_purchase_details(
    purchase_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get detailed information about a package purchase"""
    try:
        service = PackagePurchaseService(db)
        
        result = await service.get_package_details(purchase_id)
        
        # Verify ownership
        if result.get("client_id") != current_user.get("client_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))




# Service Credit Endpoints

@router.get("/purchases/{purchase_id}/credits", response_model=CreditBalanceResponse)
async def get_credit_balance(
    purchase_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get credit balance for a package purchase"""
    try:
        # Verify ownership
        purchase = db.package_purchases.find_one({"_id": ObjectId(purchase_id)})
        if not purchase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")
        
        if purchase.get("client_id") != current_user.get("client_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        service = ServiceCreditService(db)
        result = await service.get_credit_balance(purchase_id)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/credits/{credit_id}/reserve", response_model=CreditReservationResponse, status_code=status.HTTP_201_CREATED)
async def reserve_credit(
    credit_id: str,
    booking_id: str,
    quantity: int = 1,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Reserve a service credit for a booking"""
    try:
        # Get credit and verify ownership
        credit = db.service_credits.find_one({"_id": ObjectId(credit_id)})
        if not credit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credit not found")
        
        purchase = db.package_purchases.find_one({"_id": ObjectId(credit["purchase_id"])})
        if not purchase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")
        
        if purchase.get("client_id") != current_user.get("client_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        service = ServiceCreditService(db)
        result = await service.reserve_credit(
            purchase_id=credit["purchase_id"],
            service_id=credit["service_id"],
            booking_id=booking_id,
            quantity=quantity
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/credits/reservations/{reservation_id}/release", response_model=CreditReservationResponse)
async def release_credit(
    reservation_id: str,
    quantity: int = 1,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Release a reserved service credit"""
    try:
        # Get reservation and verify ownership
        reservation = db.credit_reservations.find_one({"_id": ObjectId(reservation_id)})
        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
        
        credit = db.service_credits.find_one({"_id": ObjectId(reservation["credit_id"])})
        if not credit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credit not found")
        
        purchase = db.package_purchases.find_one({"_id": ObjectId(credit["purchase_id"])})
        if not purchase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")
        
        if purchase.get("client_id") != current_user.get("client_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        service = ServiceCreditService(db)
        result = await service.release_credit(
            reservation_id=reservation_id,
            quantity=quantity
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Import ObjectId for the endpoints
from bson import ObjectId



# Package Transfer and Refund Endpoints

@router.post("/purchases/{purchase_id}/transfer")
async def transfer_package(
    purchase_id: str,
    to_client_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Transfer a package to another client"""
    try:
        # Verify ownership
        purchase = db.package_purchases.find_one({"_id": ObjectId(purchase_id)})
        if not purchase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")
        
        if purchase.get("client_id") != current_user.get("client_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        service = PackagePurchaseService(db)
        result = await service.transfer_package(
            purchase_id=purchase_id,
            from_client_id=purchase.get("client_id"),
            to_client_id=to_client_id,
            staff_id=current_user.get("user_id")
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/purchases/{purchase_id}/refund")
async def refund_package(
    purchase_id: str,
    reason: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Refund a package purchase"""
    try:
        # Verify ownership
        purchase = db.package_purchases.find_one({"_id": ObjectId(purchase_id)})
        if not purchase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase not found")
        
        if purchase.get("client_id") != current_user.get("client_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        service = PackagePurchaseService(db)
        result = await service.refund_package(
            purchase_id=purchase_id,
            reason=reason,
            staff_id=current_user.get("user_id")
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Booking Integration Endpoints

@router.get("/bookings/{client_id}/available-credits")
async def get_available_package_credits_for_booking(
    client_id: str,
    service_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get available package credits for a client and service"""
    try:
        # Verify access
        if client_id != current_user.get("client_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        from app.services.booking_service import BookingService
        
        result = await BookingService.check_available_package_credits(
            client_id=client_id,
            service_id=service_id,
            tenant_id=current_user.get("tenant_id")
        )
        
        return {
            "available_credits": result,
            "total": len(result)
        }
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/bookings/{booking_id}/reserve-credit")
async def reserve_package_credit_for_booking(
    booking_id: str,
    credit_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Reserve a package credit for a booking"""
    try:
        # Get booking and verify access
        booking = db.bookings.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        
        if booking.get("client_id") != current_user.get("client_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        from app.services.booking_service import BookingService
        
        result = await BookingService.reserve_package_credit_for_booking(
            booking_id=booking_id,
            credit_id=credit_id,
            tenant_id=current_user.get("tenant_id")
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/bookings/{booking_id}/redeem-credit")
async def redeem_package_credit_for_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Redeem a reserved package credit when booking is completed"""
    try:
        # Get booking and verify access
        booking = db.bookings.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        
        if booking.get("client_id") != current_user.get("client_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        from app.services.booking_service import BookingService
        
        result = await BookingService.redeem_package_credit_for_booking(
            booking_id=booking_id,
            tenant_id=current_user.get("tenant_id"),
            staff_id=current_user.get("user_id")
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/bookings/{booking_id}/release-credit")
async def release_package_credit_for_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Release a reserved package credit when booking is cancelled"""
    try:
        # Get booking and verify access
        booking = db.bookings.find_one({"_id": ObjectId(booking_id)})
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
        
        if booking.get("client_id") != current_user.get("client_id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        from app.services.booking_service import BookingService
        
        result = await BookingService.release_package_credit_for_booking(
            booking_id=booking_id,
            tenant_id=current_user.get("tenant_id")
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Package Analytics Endpoints

@router.get("/analytics/sales")
async def get_sales_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get package sales metrics"""
    try:
        from app.services.package_analytics_service import PackageAnalyticsService
        
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        service = PackageAnalyticsService(db)
        result = await service.get_sales_metrics(
            tenant_id=current_user.get("tenant_id"),
            start_date=start_dt,
            end_date=end_dt
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/analytics/redemption")
async def get_redemption_metrics(
    package_definition_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get package redemption metrics"""
    try:
        from app.services.package_analytics_service import PackageAnalyticsService
        
        service = PackageAnalyticsService(db)
        result = await service.get_redemption_metrics(
            tenant_id=current_user.get("tenant_id"),
            package_definition_id=package_definition_id
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/analytics/performance")
async def get_performance_metrics(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get package performance metrics"""
    try:
        from app.services.package_analytics_service import PackageAnalyticsService
        
        service = PackageAnalyticsService(db)
        result = await service.get_performance_metrics(
            tenant_id=current_user.get("tenant_id")
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/analytics/expiration")
async def get_expiration_report(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get package expiration report"""
    try:
        from app.services.package_analytics_service import PackageAnalyticsService
        
        service = PackageAnalyticsService(db)
        result = await service.get_expiration_report(
            tenant_id=current_user.get("tenant_id")
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/analytics/roi/{package_definition_id}")
async def get_package_roi(
    package_definition_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get ROI metrics for a specific package"""
    try:
        from app.services.package_analytics_service import PackageAnalyticsService
        
        service = PackageAnalyticsService(db)
        result = await service.get_package_roi(
            tenant_id=current_user.get("tenant_id"),
            package_definition_id=package_definition_id
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Package Recommendation Endpoints

@router.get("/recommendations/{client_id}")
async def get_package_recommendations(
    client_id: str,
    limit: int = 5,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get recommended packages for a client based on their booking history
    
    Requirements: 19.1
    """
    try:
        from app.services.package_recommendation_service import PackageRecommendationService
        
        service = PackageRecommendationService(db)
        recommendations = await service.get_recommendations_for_client(
            client_id=client_id,
            tenant_id=current_user.get("tenant_id"),
            limit=limit
        )
        
        return {
            "client_id": client_id,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Package Audit Trail Endpoints

@router.get("/audit-trail")
async def get_package_audit_trail(
    action_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    client_id: Optional[str] = None,
    performed_by_user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get package audit trail with optional filtering
    
    Requirements: 18.6
    """
    try:
        from app.services.package_audit_service import PackageAuditService
        from bson import ObjectId
        
        service = PackageAuditService(db)
        
        # Parse dates if provided
        start_dt = None
        end_dt = None
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        result = await service.get_audit_logs(
            tenant_id=current_user.get("tenant_id"),
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            client_id=client_id,
            performed_by_user_id=performed_by_user_id,
            start_date=start_dt,
            end_date=end_dt,
            page=page,
            page_size=page_size
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/audit-trail/entity/{entity_id}")
async def get_entity_audit_history(
    entity_id: str,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get complete audit history for a specific entity
    
    Requirements: 18.6
    """
    try:
        from app.services.package_audit_service import PackageAuditService
        
        service = PackageAuditService(db)
        logs = await service.get_entity_audit_history(
            tenant_id=current_user.get("tenant_id"),
            entity_id=entity_id,
            limit=limit
        )
        
        return {
            "entity_id": entity_id,
            "logs": logs,
            "total": len(logs)
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/audit-trail/user/{user_id}")
async def get_user_audit_activity(
    user_id: str,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get audit activity for a specific user
    
    Requirements: 18.6
    """
    try:
        from app.services.package_audit_service import PackageAuditService
        
        service = PackageAuditService(db)
        logs = await service.get_user_audit_activity(
            tenant_id=current_user.get("tenant_id"),
            performed_by_user_id=user_id,
            limit=limit
        )
        
        return {
            "user_id": user_id,
            "logs": logs,
            "total": len(logs)
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/audit-trail/client/{client_id}")
async def get_client_audit_history(
    client_id: str,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get audit history for a specific client
    
    Requirements: 18.6
    """
    try:
        from app.services.package_audit_service import PackageAuditService
        
        service = PackageAuditService(db)
        logs = await service.get_client_audit_history(
            tenant_id=current_user.get("tenant_id"),
            client_id=client_id,
            limit=limit
        )
        
        return {
            "client_id": client_id,
            "logs": logs,
            "total": len(logs)
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Bulk Operations Endpoints

from app.schemas.package_bulk_operations import (
    BulkActivateRequest,
    BulkDeactivateRequest,
    BulkUpdatePricesRequest,
    BulkExtendExpirationRequest,
    BulkActivateResponse,
    BulkDeactivateResponse,
    BulkUpdatePricesResponse,
    BulkExtendExpirationResponse
)
from app.services.package_bulk_operations_service import PackageBulkOperationsService


@router.post("/bulk/activate", response_model=BulkActivateResponse)
async def bulk_activate_packages(
    request: BulkActivateRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Bulk activate multiple package definitions
    
    Requirements: 17.1, 17.5
    Property 26: Bulk Operation Atomicity
    """
    try:
        service = PackageBulkOperationsService(db)
        
        result = await service.bulk_activate_packages(
            tenant_id=current_user.get("tenant_id"),
            package_ids=request.package_ids,
            performed_by_staff_id=current_user.get("user_id")
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/bulk/deactivate", response_model=BulkDeactivateResponse)
async def bulk_deactivate_packages(
    request: BulkDeactivateRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Bulk deactivate multiple package definitions
    
    Requirements: 17.2, 17.5
    Property 26: Bulk Operation Atomicity
    """
    try:
        service = PackageBulkOperationsService(db)
        
        result = await service.bulk_deactivate_packages(
            tenant_id=current_user.get("tenant_id"),
            package_ids=request.package_ids,
            performed_by_staff_id=current_user.get("user_id")
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/bulk/update-prices", response_model=BulkUpdatePricesResponse)
async def bulk_update_prices(
    request: BulkUpdatePricesRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Bulk update prices for multiple packages
    
    Requirements: 17.3, 17.5
    Property 26: Bulk Operation Atomicity
    """
    try:
        service = PackageBulkOperationsService(db)
        
        result = await service.bulk_update_prices(
            tenant_id=current_user.get("tenant_id"),
            package_updates=request.package_updates,
            performed_by_staff_id=current_user.get("user_id")
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/purchases/bulk/extend", response_model=BulkExtendExpirationResponse)
async def bulk_extend_expiration(
    request: BulkExtendExpirationRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Bulk extend expiration dates for multiple purchased packages
    
    Requirements: 17.4, 17.5
    Property 26: Bulk Operation Atomicity
    """
    try:
        service = PackageBulkOperationsService(db)
        
        result = await service.bulk_extend_expiration(
            tenant_id=current_user.get("tenant_id"),
            purchase_updates=request.purchase_updates,
            performed_by_staff_id=current_user.get("user_id")
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
