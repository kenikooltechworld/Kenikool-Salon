"""Public booking API routes for guest appointments via subdomain."""

from datetime import date, datetime
from typing import List
import logging

from fastapi import APIRouter, HTTPException, Request, Depends
from bson import ObjectId

from app.context import get_tenant_id
from app.models.public_booking import PublicBooking, PublicBookingStatus
from app.models.service import Service
from app.models.staff import Staff
from app.models.tenant import Tenant
from app.schemas.public_booking import (
    PublicBookingCreate,
    PublicBookingResponse,
    PublicServiceResponse,
    PublicStaffResponse,
    AvailabilityResponse,
    AvailabilitySlot,
)
from app.utils.availability_calculator import AvailabilityCalculator
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/public", tags=["public_booking"])


class SalonInfoResponse(BaseModel):
    """Salon information for public booking."""
    id: str
    name: str
    description: str
    email: str
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None


@router.get("/salon-info", response_model=SalonInfoResponse)
async def get_salon_info(request: Request):
    """
    Get salon information for public booking page.

    Returns:
        Salon details
    """
    tenant_id = request.scope.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid tenant ID")

    # Verify tenant is active and published
    tenant = Tenant.objects(id=tenant_id_obj).first()
    if not tenant or not tenant.is_published:
        raise HTTPException(status_code=404, detail="Salon not found")

    return SalonInfoResponse(
        id=str(tenant.id),
        name=tenant.name,
        description=tenant.description or "",
        email=tenant.email,
        logo_url=tenant.logo_url,
        primary_color=tenant.primary_color,
        secondary_color=tenant.secondary_color,
    )


@router.get("/services", response_model=List[PublicServiceResponse])
async def list_public_services(request: Request):
    """
    List all published services for the tenant.

    Returns:
        List of published services
    """
    tenant_id = request.scope.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid tenant ID")

    # Verify tenant is active and published
    tenant = Tenant.objects(id=tenant_id_obj).first()
    if not tenant or not tenant.is_published:
        raise HTTPException(status_code=404, detail="Salon not found")

    # Get published services
    services = Service.objects(
        tenant_id=tenant_id_obj, is_published=True, allow_public_booking=True
    ).order_by("name")

    return [
        PublicServiceResponse(
            id=str(service.id),
            name=service.name,
            description=service.description or "",
            duration_minutes=service.duration_minutes,
            price=float(service.price),
            is_published=service.is_published,
            public_description=service.public_description,
            public_image_url=service.public_image_url,
            allow_public_booking=service.allow_public_booking,
        )
        for service in services
    ]


@router.get("/staff", response_model=List[PublicStaffResponse])
async def list_public_staff(request: Request, service_id: str = None):
    """
    List available staff members for a service.

    Args:
        service_id: Optional service ID to filter staff

    Returns:
        List of available staff members
    """
    tenant_id = request.scope.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid tenant ID")

    # Verify tenant is active and published
    tenant = Tenant.objects(id=tenant_id_obj).first()
    if not tenant or not tenant.is_published:
        raise HTTPException(status_code=404, detail="Salon not found")

    # Get available staff
    staff_members = Staff.objects(
        tenant_id=tenant_id_obj,
        is_available_for_public_booking=True,
        status="active",
    ).order_by("user_id")

    return [
        PublicStaffResponse(
            id=str(staff.id),
            first_name=staff.user_id.first_name if staff.user_id else "Staff",
            last_name=staff.user_id.last_name if staff.user_id else "",
            is_available_for_public_booking=staff.is_available_for_public_booking,
            bio=staff.bio,
            profile_image_url=staff.profile_image_url,
        )
        for staff in staff_members
    ]


@router.get("/availability", response_model=AvailabilityResponse)
async def get_availability(
    request: Request,
    service_id: str,
    staff_id: str,
    booking_date: date,
):
    """
    Get available time slots for a service and staff member on a given date.

    Args:
        service_id: Service ID
        staff_id: Staff member ID
        booking_date: Date to check availability

    Returns:
        Available time slots for the date
    """
    tenant_id = request.scope.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
        service_id_obj = ObjectId(service_id)
        staff_id_obj = ObjectId(staff_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Verify tenant is active and published
    tenant = Tenant.objects(id=tenant_id_obj).first()
    if not tenant or not tenant.is_published:
        raise HTTPException(status_code=404, detail="Salon not found")

    # Verify service exists and is published
    service = Service.objects(
        tenant_id=tenant_id_obj, id=service_id_obj, is_published=True
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Verify staff exists and is available for public booking
    staff = Staff.objects(
        tenant_id=tenant_id_obj,
        id=staff_id_obj,
        is_available_for_public_booking=True,
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    # Get available slots
    slots = AvailabilityCalculator.get_available_slots(
        tenant_id_obj, staff_id_obj, service_id_obj, booking_date
    )

    return AvailabilityResponse(
        date=booking_date,
        slots=[
            AvailabilitySlot(time=slot.time.strftime("%H:%M"), available=slot.available) for slot in slots
        ],
    )


@router.post("/bookings", response_model=PublicBookingResponse)
async def create_public_booking(
    request: Request,
    booking_data: PublicBookingCreate,
):
    """
    Create a public booking (guest appointment).

    Args:
        booking_data: Booking details

    Returns:
        Created booking details
    """
    from app.services.public_booking_service import PublicBookingService
    
    tenant_id = request.scope.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
        service_id_obj = ObjectId(booking_data.service_id)
        staff_id_obj = ObjectId(booking_data.staff_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Verify tenant is active and published
    tenant = Tenant.objects(id=tenant_id_obj).first()
    if not tenant or not tenant.is_published:
        raise HTTPException(status_code=404, detail="Salon not found")

    # Verify service exists and is published
    service = Service.objects(
        tenant_id=tenant_id_obj, id=service_id_obj, is_published=True
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Verify staff exists and is available for public booking
    staff = Staff.objects(
        tenant_id=tenant_id_obj,
        id=staff_id_obj,
        is_available_for_public_booking=True,
    ).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    # Check if slot is available
    slots = AvailabilityCalculator.get_available_slots(
        tenant_id_obj, staff_id_obj, service_id_obj, booking_data.booking_date
    )

    slot_available = any(
        slot.time == booking_data.booking_time and slot.available for slot in slots
    )

    if not slot_available:
        raise HTTPException(status_code=409, detail="Selected time slot is not available")

    # Generate idempotency key from request headers if provided
    idempotency_key = request.headers.get("idempotency-key")

    try:
        # Create public booking using service with idempotency support
        public_booking = PublicBookingService.create_public_booking(
            tenant_id=tenant_id_obj,
            service_id=service_id_obj,
            staff_id=staff_id_obj,
            customer_name=booking_data.customer_name,
            customer_email=booking_data.customer_email,
            customer_phone=booking_data.customer_phone,
            booking_date=booking_data.booking_date,
            booking_time=booking_data.booking_time,
            duration_minutes=booking_data.duration_minutes,
            notes=booking_data.notes,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            idempotency_key=idempotency_key,
            payment_option=booking_data.payment_option or "later",
        )
        
        # If payment is required now, initialize payment
        if booking_data.payment_option == "now":
            try:
                from app.services.payment_service import PaymentService
                from app.models.service import Service as ServiceModel
                
                service = ServiceModel.objects(
                    tenant_id=tenant_id_obj, id=service_id_obj
                ).first()
                
                if service:
                    payment_service = PaymentService()
                    payment_result = payment_service.initialize_payment(
                        tenant_id=tenant_id_obj,
                        customer_id=booking.customer_id,
                        amount=float(service.price),
                        description=f"Booking for {service.name}",
                        metadata={
                            "booking_id": str(public_booking.id),
                            "booking_type": "public",
                        },
                    )
                    
                    # Update booking with payment info
                    public_booking.payment_id = payment_result.get("payment_id")
                    public_booking.payment_status = "pending"
                    public_booking.save()
                    
                    logger.info(f"Payment initialized for booking {public_booking.id}")
            except Exception as e:
                logger.error(f"Error initializing payment for booking: {str(e)}")
        
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return PublicBookingResponse(
        id=str(public_booking.id),
        tenant_id=str(public_booking.tenant_id),
        service_id=str(public_booking.service_id),
        staff_id=str(public_booking.staff_id),
        appointment_id=str(public_booking.appointment_id) if public_booking.appointment_id else None,
        customer_name=public_booking.customer_name,
        customer_email=public_booking.customer_email,
        customer_phone=public_booking.customer_phone,
        booking_date=public_booking.booking_date,
        booking_time=public_booking.booking_time,
        duration_minutes=public_booking.duration_minutes,
        status=public_booking.status,
        notes=public_booking.notes,
        created_at=public_booking.created_at.isoformat(),
        updated_at=public_booking.updated_at.isoformat(),
    )


@router.get("/bookings/{booking_id}", response_model=PublicBookingResponse)
async def get_public_booking(request: Request, booking_id: str):
    """
    Get public booking details.

    Args:
        booking_id: Public booking ID

    Returns:
        Booking details
    """
    tenant_id = request.scope.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
        booking_id_obj = ObjectId(booking_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Get booking
    booking = PublicBooking.objects(
        tenant_id=tenant_id_obj, id=booking_id_obj
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return PublicBookingResponse(
        id=str(booking.id),
        tenant_id=str(booking.tenant_id),
        service_id=str(booking.service_id),
        staff_id=str(booking.staff_id),
        appointment_id=str(booking.appointment_id) if booking.appointment_id else None,
        customer_name=booking.customer_name,
        customer_email=booking.customer_email,
        customer_phone=booking.customer_phone,
        booking_date=booking.booking_date,
        booking_time=booking.booking_time,
        duration_minutes=booking.duration_minutes,
        status=booking.status,
        notes=booking.notes,
        created_at=booking.created_at.isoformat(),
        updated_at=booking.updated_at.isoformat(),
    )
