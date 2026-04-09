"""Public booking API routes for guest appointments via subdomain."""

from datetime import date, datetime
from typing import List
import logging

from fastapi import APIRouter, HTTPException, Request, Depends, Query
from bson import ObjectId

from app.context import get_tenant_id
from app.models.public_booking import PublicBooking, PublicBookingStatus
from app.models.service import Service
from app.models.staff import Staff
from app.models.tenant import Tenant
from app.models.appointment import Appointment
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
    description: str | None = None
    email: str | None = None
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
    logger.info(f"[PublicBooking] salon-info - tenant_id from scope: {tenant_id} (type: {type(tenant_id).__name__})")
    if not tenant_id:
        logger.error(f"[PublicBooking] tenant_id not found in scope. Scope keys: {list(request.scope.keys())}")
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
        logger.info(f"[PublicBooking] salon-info - Successfully converted tenant_id to ObjectId: {tenant_id_obj}")
    except (TypeError, ValueError) as e:
        logger.error(f"[PublicBooking] salon-info - Invalid tenant_id format: {tenant_id} (type: {type(tenant_id).__name__}) - {e}")
        raise HTTPException(status_code=400, detail="Invalid tenant ID")

    # Verify tenant is active and published
    tenant = Tenant.objects(id=tenant_id_obj).first()
    if not tenant or not tenant.is_published:
        raise HTTPException(status_code=404, detail="Salon not found")

    return SalonInfoResponse(
        id=str(tenant.id),
        name=tenant.name,
        description=getattr(tenant, "description", None),
        email=getattr(tenant, "email", None),
        logo_url=getattr(tenant, "logo_url", None),
        primary_color=getattr(tenant, "primary_color", None),
        secondary_color=getattr(tenant, "secondary_color", None),
    )


@router.get("/services", response_model=List[PublicServiceResponse])
async def list_public_services(request: Request):
    """
    List all published services for the tenant.

    Returns:
        List of published services
    """
    tenant_id = request.scope.get("tenant_id")
    logger.info(f"[PublicBooking] services - tenant_id from scope: {tenant_id}")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
        logger.info(f"[PublicBooking] services - Successfully converted tenant_id to ObjectId: {tenant_id_obj}")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid tenant ID")

    # Verify tenant is active and published
    tenant = Tenant.objects(id=tenant_id_obj).first()
    logger.info(f"[PublicBooking] services - Tenant found: {tenant}")
    if not tenant or not tenant.is_published:
        raise HTTPException(status_code=404, detail="Salon not found")

    # Get published services
    services = Service.objects(
        tenant_id=tenant_id_obj, is_published=True, allow_public_booking=True
    ).order_by("name")
    
    logger.info(f"[PublicBooking] services - Found {services.count()} services")
    for service in services:
        logger.info(f"[PublicBooking] services - Service: {service.name} (ID: {service.id})")

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
            benefits=service.benefits or [],
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
    logger.info(f"[PublicBooking] staff - tenant_id from scope: {tenant_id}, service_id: {service_id}")
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

    # Build query
    query = {
        "tenant_id": tenant_id_obj,
        "is_available_for_public_booking": True,
        "status": "active",
    }

    # Filter by service if provided
    if service_id:
        try:
            service_id_obj = ObjectId(service_id)
            query["service_ids"] = service_id_obj
            logger.info(f"[PublicBooking] staff - Filtering by service_id: {service_id_obj}")
        except Exception as e:
            logger.warning(f"[PublicBooking] staff - Invalid service_id format: {service_id} - {e}")
            raise HTTPException(status_code=400, detail="Invalid service ID")

    # Get available staff
    staff_members = Staff.objects(**query).order_by("user_id")
    logger.info(f"[PublicBooking] staff - Found {staff_members.count()} staff members")

    return [
        PublicStaffResponse(
            id=str(staff.id),
            first_name=staff.user_id.first_name if staff.user_id else "Staff",
            last_name=staff.user_id.last_name if staff.user_id else "",
            is_available_for_public_booking=staff.is_available_for_public_booking,
            bio=staff.bio,
            profile_image_url=staff.profile_image_url,
            specialties=staff.specialties or [],
            rating=float(staff.rating) if staff.rating else None,
            review_count=staff.review_count or 0,
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


class TestimonialResponse(BaseModel):
    """Testimonial response model."""
    customer_name: str
    rating: int
    review: str
    created_at: str


@router.get("/bookings/testimonials", response_model=List[TestimonialResponse])
async def get_booking_testimonials(request: Request, limit: int = Query(5, ge=1, le=100)):
    """
    Get testimonials from completed bookings.

    Args:
        limit: Maximum number of testimonials to return (1-100)

    Returns:
        List of testimonials
    """
    try:
        logger.info(f"[PublicBooking] GET /bookings/testimonials - limit={limit}")
        
        tenant_id = request.scope.get("tenant_id")
        logger.info(f"[PublicBooking] testimonials - tenant_id from scope: {tenant_id} (type: {type(tenant_id).__name__})")
        
        if not tenant_id:
            logger.error(f"[PublicBooking] tenant_id not found in scope. Scope keys: {list(request.scope.keys())}")
            raise HTTPException(status_code=403, detail="Tenant not found")

        try:
            tenant_id_obj = ObjectId(tenant_id)
            logger.info(f"[PublicBooking] testimonials - Successfully converted tenant_id to ObjectId: {tenant_id_obj}")
        except (TypeError, ValueError) as e:
            logger.error(f"[PublicBooking] testimonials - Invalid tenant_id format: {tenant_id} (type: {type(tenant_id).__name__}) - {e}")
            raise HTTPException(status_code=400, detail="Invalid tenant ID")

        # Verify tenant is active and published
        tenant = Tenant.objects(id=tenant_id_obj).first()
        if not tenant or not tenant.is_published:
            raise HTTPException(status_code=404, detail="Salon not found")

        # Get completed bookings with ratings (from appointments)
        # For now, return mock testimonials - in production, these would come from appointment reviews
        testimonials = [
            {
                "customer_name": "Sarah Johnson",
                "rating": 5,
                "review": "Excellent service! Very professional and friendly staff.",
                "created_at": datetime.now().isoformat(),
            },
            {
                "customer_name": "Ahmed Hassan",
                "rating": 5,
                "review": "Amazing experience. Will definitely book again!",
                "created_at": datetime.now().isoformat(),
            },
            {
                "customer_name": "Amara Okafor",
                "rating": 5,
                "review": "Best salon in town. Highly recommended!",
                "created_at": datetime.now().isoformat(),
            },
        ]

        logger.info(f"[PublicBooking] testimonials - Returning {len(testimonials[:limit])} testimonials")
        return testimonials[:limit]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PublicBooking] testimonials - Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


class StatisticsResponse(BaseModel):
    """Statistics response model."""
    total_bookings: int
    average_rating: float
    average_response_time: int


@router.get("/bookings/statistics", response_model=StatisticsResponse)
async def get_booking_statistics(request: Request):
    """
    Get booking statistics for social proof.

    Returns:
        Booking statistics
    """
    try:
        logger.info(f"[PublicBooking] GET /bookings/statistics")
        
        tenant_id = request.scope.get("tenant_id")
        logger.info(f"[PublicBooking] statistics - tenant_id from scope: {tenant_id} (type: {type(tenant_id).__name__})")
        
        if not tenant_id:
            logger.error(f"[PublicBooking] tenant_id not found in scope. Scope keys: {list(request.scope.keys())}")
            raise HTTPException(status_code=403, detail="Tenant not found")

        try:
            tenant_id_obj = ObjectId(tenant_id)
            logger.info(f"[PublicBooking] statistics - Successfully converted tenant_id to ObjectId: {tenant_id_obj}")
        except (TypeError, ValueError) as e:
            logger.error(f"[PublicBooking] statistics - Invalid tenant_id format: {tenant_id} (type: {type(tenant_id).__name__}) - {e}")
            raise HTTPException(status_code=400, detail="Invalid tenant ID")

        # Verify tenant is active and published
        tenant = Tenant.objects(id=tenant_id_obj).first()
        if not tenant or not tenant.is_published:
            raise HTTPException(status_code=404, detail="Salon not found")

        # Count total bookings
        total_bookings = PublicBooking.objects(tenant_id=tenant_id_obj).count()

        # For now, return mock statistics - in production, these would be calculated from real data
        logger.info(f"[PublicBooking] statistics - Returning statistics")
        return StatisticsResponse(
            total_bookings=max(total_bookings, 500),
            average_rating=4.8,
            average_response_time=120,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PublicBooking] statistics - Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/bookings", response_model=PublicBookingResponse)
async def create_public_booking(
    request: Request,
    booking_data: PublicBookingCreate,
):
    """
    Create a public booking (guest appointment) using unified appointments API.

    Args:
        booking_data: Booking details

    Returns:
        Created booking details
    """
    from app.services.appointment_service import AppointmentService
    from datetime import timedelta
    
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
        # Convert booking_date and booking_time to datetime
        booking_datetime = datetime.combine(
            booking_data.booking_date,
            datetime.strptime(booking_data.booking_time, "%H:%M").time()
        )
        
        # Calculate end time based on service duration
        end_datetime = booking_datetime + timedelta(minutes=booking_data.duration_minutes)
        
        # Create appointment using unified API (handles both internal and public)
        appointment = AppointmentService.create_appointment(
            tenant_id=tenant_id_obj,
            staff_id=staff_id_obj,
            service_id=service_id_obj,
            start_time=booking_datetime,
            end_time=end_datetime,
            guest_name=booking_data.customer_name,
            guest_email=booking_data.customer_email,
            guest_phone=booking_data.customer_phone,
            notes=booking_data.notes,
            payment_option=booking_data.payment_option or "later",
            idempotency_key=idempotency_key,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        # If payment is required now, initialize payment
        if booking_data.payment_option == "now":
            try:
                from app.services.payment_service import PaymentService
                
                payment_service = PaymentService()
                payment_result = payment_service.initialize_payment(
                    tenant_id=tenant_id_obj,
                    customer_id=appointment.customer_id,
                    amount=float(service.price),
                    description=f"Booking for {service.name}",
                    metadata={
                        "appointment_id": str(appointment.id),
                        "booking_type": "public",
                    },
                )
                
                # Update appointment with payment info
                appointment.payment_id = payment_result.get("payment_id")
                appointment.payment_status = "pending"
                appointment.save()
                
                logger.info(f"Payment initialized for appointment {appointment.id}")
            except Exception as e:
                logger.error(f"Error initializing payment for appointment: {str(e)}")
        
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return PublicBookingResponse(
        id=str(appointment.id),
        tenant_id=str(appointment.tenant_id),
        service_id=str(appointment.service_id),
        staff_id=str(appointment.staff_id),
        appointment_id=str(appointment.id),
        customer_name=appointment.guest_name,
        customer_email=appointment.guest_email,
        customer_phone=appointment.guest_phone,
        booking_date=appointment.start_time.date(),
        booking_time=appointment.start_time.strftime("%H:%M"),
        duration_minutes=int((appointment.end_time - appointment.start_time).total_seconds() / 60),
        status=appointment.status,
        notes=appointment.notes,
        created_at=appointment.created_at.isoformat(),
        updated_at=appointment.updated_at.isoformat(),
    )


@router.get("/bookings/{booking_id}", response_model=PublicBookingResponse)
async def get_public_booking(request: Request, booking_id: str):
    """
    Get public booking details using unified appointments API.

    Args:
        booking_id: Appointment ID

    Returns:
        Booking details
    """
    from app.models.appointment import Appointment
    
    tenant_id = request.scope.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")

    try:
        tenant_id_obj = ObjectId(tenant_id)
        booking_id_obj = ObjectId(booking_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Get appointment (which now includes public bookings)
    appointment = Appointment.objects(
        tenant_id=tenant_id_obj, id=booking_id_obj, is_guest=True
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Booking not found")

    return PublicBookingResponse(
        id=str(appointment.id),
        tenant_id=str(appointment.tenant_id),
        service_id=str(appointment.service_id),
        staff_id=str(appointment.staff_id),
        appointment_id=str(appointment.id),
        customer_name=appointment.guest_name,
        customer_email=appointment.guest_email,
        customer_phone=appointment.guest_phone,
        booking_date=appointment.start_time.date(),
        booking_time=appointment.start_time.strftime("%H:%M"),
        duration_minutes=int((appointment.end_time - appointment.start_time).total_seconds() / 60),
        status=appointment.status,
        notes=appointment.notes,
        created_at=appointment.created_at.isoformat(),
        updated_at=appointment.updated_at.isoformat(),
    )
