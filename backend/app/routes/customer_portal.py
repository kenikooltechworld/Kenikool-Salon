"""Customer Portal Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.middleware.customer_auth import get_current_customer
from app.models.customer import Customer
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.staff import Staff
from app.schemas.customer_auth import BookingHistory

router = APIRouter(prefix="/public/customer-portal", tags=["Customer Portal"])


@router.get("/bookings", response_model=List[BookingHistory])
async def get_booking_history(
    current_customer: Customer = Depends(get_current_customer),
    status_filter: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
):
    """Get customer booking history"""
    query = {
        "tenant_id": current_customer.tenant_id,
        "$or": [
            {"customer_id": current_customer.id},
            {"guest_email": current_customer.email}
        ]
    }
    
    if status_filter:
        query["status"] = status_filter
    
    appointments = Appointment.objects(__raw__=query).order_by("-booking_date").skip(skip).limit(limit)
    
    bookings = []
    for appointment in appointments:
        # Get service and staff names
        service = Service.objects(id=appointment.service_id).first()
        staff = Staff.objects(id=appointment.staff_id).first()
        
        bookings.append(BookingHistory(
            id=str(appointment.id),
            service_name=service.name if service else "Unknown Service",
            staff_name=f"{staff.first_name} {staff.last_name}" if staff else "Unknown Staff",
            booking_date=str(appointment.booking_date),
            booking_time=appointment.booking_time,
            status=appointment.status,
            payment_status=appointment.payment_status if hasattr(appointment, 'payment_status') else None,
            total_price=float(appointment.total_price) if hasattr(appointment, 'total_price') else 0.0,
            notes=appointment.notes if hasattr(appointment, 'notes') else None,
            created_at=appointment.created_at
        ))
    
    return bookings


@router.get("/bookings/{booking_id}", response_model=BookingHistory)
async def get_booking_details(
    booking_id: str,
    current_customer: Customer = Depends(get_current_customer)
):
    """Get specific booking details"""
    try:
        appointment = Appointment.objects(id=ObjectId(booking_id)).first()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booking ID"
        )
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Verify customer owns this booking
    is_owner = (
        (hasattr(appointment, 'customer_id') and appointment.customer_id == current_customer.id) or
        (hasattr(appointment, 'guest_email') and appointment.guest_email == current_customer.email)
    )
    
    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this booking"
        )
    
    # Get service and staff names
    service = Service.objects(id=appointment.service_id).first()
    staff = Staff.objects(id=appointment.staff_id).first()
    
    return BookingHistory(
        id=str(appointment.id),
        service_name=service.name if service else "Unknown Service",
        staff_name=f"{staff.first_name} {staff.last_name}" if staff else "Unknown Staff",
        booking_date=str(appointment.booking_date),
        booking_time=appointment.booking_time,
        status=appointment.status,
        payment_status=appointment.payment_status if hasattr(appointment, 'payment_status') else None,
        total_price=float(appointment.total_price) if hasattr(appointment, 'total_price') else 0.0,
        notes=appointment.notes if hasattr(appointment, 'notes') else None,
        created_at=appointment.created_at
    )


@router.post("/bookings/{booking_id}/rebook")
async def rebook_appointment(
    booking_id: str,
    current_customer: Customer = Depends(get_current_customer)
):
    """Rebook a previous appointment with same details"""
    try:
        original_appointment = Appointment.objects(id=ObjectId(booking_id)).first()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booking ID"
        )
    
    if not original_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Verify customer owns this booking
    is_owner = (
        (hasattr(original_appointment, 'customer_id') and original_appointment.customer_id == current_customer.id) or
        (hasattr(original_appointment, 'guest_email') and original_appointment.guest_email == current_customer.email)
    )
    
    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to rebook this appointment"
        )
    
    # Return booking data for rebooking
    return {
        "message": "Redirecting to booking page",
        "booking_data": {
            "service_id": str(original_appointment.service_id),
            "staff_id": str(original_appointment.staff_id),
            "customer_name": f"{current_customer.first_name} {current_customer.last_name}",
            "customer_email": current_customer.email,
            "customer_phone": current_customer.phone,
        }
    }
