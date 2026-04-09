"""Routes for appointment management."""

import logging
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from bson import ObjectId
from app.schemas.appointment import (
    AppointmentCreateRequest,
    AppointmentUpdateRequest,
    AppointmentCancelRequest,
    AppointmentConfirmRequest,
    AppointmentResponse,
    AppointmentListResponse,
    AvailableSlotsResponse,
    AvailableSlot,
    CalendarAvailabilityResponse,
    DayViewResponse,
    WeekViewResponse,
    MonthViewResponse,
)
from app.services.appointment_service import AppointmentService
from app.services.appointment_history_service import AppointmentHistoryService
from app.services.service_commission_service import ServiceCommissionService
from app.services.invoice_service import InvoiceService
from app.models.appointment import Appointment
from app.models.customer import Customer
from app.models.service import Service
from app.middleware.tenant_context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated
from app.routes.auth import get_current_user_dependency

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentResponse)
async def create_appointment(
    request: AppointmentCreateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Create a new appointment.
    
    - **customer_id**: Customer ID (optional if creating new customer)
    - **customer_name**: Customer name (for new customers)
    - **customer_email**: Customer email (for new customers)
    - **customer_phone**: Customer phone (for new customers)
    - **staff_id**: Staff member ID
    - **service_id**: Service ID
    - **start_time**: Appointment start time (local timezone, ISO format)
    - **end_time**: Appointment end time (local timezone, ISO format)
    """
    try:
        from app.models.customer import Customer
        
        logger.info(f"[CreateAppointment] Received request: start_time={request.start_time}, end_time={request.end_time}")
        logger.info(f"[CreateAppointment] Staff ID: {request.staff_id}, Customer ID: {request.customer_id}")
        
        # Handle customer creation if needed
        if request.customer_id:
            customer_id = ObjectId(request.customer_id)
        elif request.customer_name and request.customer_email and request.customer_phone:
            # Create new customer
            name_parts = request.customer_name.split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Check if customer with this email already exists
            existing_customer = Customer.objects(
                tenant_id=tenant_id, email=request.customer_email
            ).first()
            
            if existing_customer:
                customer_id = existing_customer.id
            else:
                # Create new customer
                customer = Customer(
                    tenant_id=tenant_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=request.customer_email,
                    phone=request.customer_phone,
                )
                customer.save()
                customer_id = customer.id
                logger.info(f"[CreateAppointment] Created new customer: {customer_id}")
        else:
            raise HTTPException(
                status_code=400,
                detail="Either customer_id or customer details (name, email, phone) must be provided"
            )
        
        staff_id = ObjectId(request.staff_id)
        service_id = ObjectId(request.service_id)
        location_id = ObjectId(request.location_id) if request.location_id else None
        
        # Parse local timezone strings to datetime
        # Format: "YYYY-MM-DDTHH:MM:SS"
        try:
            start_time = datetime.fromisoformat(request.start_time)
            end_time = datetime.fromisoformat(request.end_time)
        except ValueError as e:
            logger.error(f"[CreateAppointment] Invalid datetime format: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid datetime format: {str(e)}")
        
        appointment = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            location_id=location_id,
            notes=request.notes,
            payment_option=request.payment_option,
        )
        
        return AppointmentResponse(
            id=str(appointment.id),
            customer_id=str(appointment.customer_id),
            staff_id=str(appointment.staff_id),
            service_id=str(appointment.service_id),
            location_id=str(appointment.location_id) if appointment.location_id else None,
            start_time=appointment.start_time.isoformat(),
            end_time=appointment.end_time.isoformat(),
            status=appointment.status,
            notes=appointment.notes,
            price=appointment.price,
            cancellation_reason=appointment.cancellation_reason,
            cancelled_at=appointment.cancelled_at.isoformat() if appointment.cancelled_at else None,
            no_show_reason=appointment.no_show_reason,
            marked_no_show_at=appointment.marked_no_show_at.isoformat() if appointment.marked_no_show_at else None,
            confirmed_at=appointment.confirmed_at.isoformat() if appointment.confirmed_at else None,
            created_at=appointment.created_at.isoformat(),
            updated_at=appointment.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get an appointment by ID."""
    try:
        appt_id = ObjectId(appointment_id)
        appointment = AppointmentService.get_appointment(tenant_id, appt_id)
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return AppointmentResponse(
            id=str(appointment.id),
            customer_id=str(appointment.customer_id),
            staff_id=str(appointment.staff_id),
            service_id=str(appointment.service_id),
            location_id=str(appointment.location_id) if appointment.location_id else None,
            start_time=appointment.start_time.isoformat(),
            end_time=appointment.end_time.isoformat(),
            status=appointment.status,
            notes=appointment.notes,
            price=appointment.price,
            cancellation_reason=appointment.cancellation_reason,
            cancelled_at=appointment.cancelled_at.isoformat() if appointment.cancelled_at else None,
            no_show_reason=appointment.no_show_reason,
            marked_no_show_at=appointment.marked_no_show_at.isoformat() if appointment.marked_no_show_at else None,
            confirmed_at=appointment.confirmed_at.isoformat() if appointment.confirmed_at else None,
            created_at=appointment.created_at.isoformat(),
            updated_at=appointment.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Calendar view routes - must come BEFORE generic list route
@router.get("/day/{date}", response_model=DayViewResponse)
@tenant_isolated
async def get_day_view(
    date: str = Path(..., description="Date (ISO format YYYY-MM-DD)"),
    staff_id: Optional[str] = Query(None, description="Optional staff ID filter"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Get appointments for a specific day.
    
    - **date**: Date in ISO format (YYYY-MM-DD)
    - **staff_id**: Optional staff ID filter
    """
    try:
        date_obj = datetime.fromisoformat(date)
        staff_id_obj = ObjectId(staff_id) if staff_id else None
        
        appointments = AppointmentService.get_day_view(
            tenant_id=tenant_id,
            date=date_obj,
            staff_id=staff_id_obj,
        )
        
        return DayViewResponse(
            date=date,
            appointments=[
                AppointmentResponse(
                    id=str(appt.id),
                    customer_id=str(appt.customer_id),
                    staff_id=str(appt.staff_id),
                    service_id=str(appt.service_id),
                    location_id=str(appt.location_id) if appt.location_id else None,
                    start_time=appt.start_time.isoformat(),
                    end_time=appt.end_time.isoformat(),
                    status=appt.status,
                    notes=appt.notes,
                    price=appt.price,
                    cancellation_reason=appt.cancellation_reason,
                    cancelled_at=appt.cancelled_at.isoformat() if appt.cancelled_at else None,
                    no_show_reason=appt.no_show_reason,
                    marked_no_show_at=appt.marked_no_show_at.isoformat() if appt.marked_no_show_at else None,
                    confirmed_at=appt.confirmed_at.isoformat() if appt.confirmed_at else None,
                    created_at=appt.created_at.isoformat(),
                    updated_at=appt.updated_at.isoformat(),
                )
                for appt in appointments
            ],
            total=len(appointments),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/week/{date}", response_model=WeekViewResponse)
@tenant_isolated
async def get_week_view(
    date: str = Path(..., description="Any date in the week (ISO format YYYY-MM-DD)"),
    staff_id: Optional[str] = Query(None, description="Optional staff ID filter"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Get appointments for a specific week.
    
    - **date**: Any date in the week (ISO format YYYY-MM-DD)
    - **staff_id**: Optional staff ID filter
    """
    try:
        date_obj = datetime.fromisoformat(date)
        staff_id_obj = ObjectId(staff_id) if staff_id else None
        
        appointments = AppointmentService.get_week_view(
            tenant_id=tenant_id,
            date=date_obj,
            staff_id=staff_id_obj,
        )
        
        # Calculate week start and end
        week_start = date_obj - timedelta(days=date_obj.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)
        
        return WeekViewResponse(
            week_start=week_start.isoformat(),
            week_end=week_end.isoformat(),
            appointments=[
                AppointmentResponse(
                    id=str(appt.id),
                    customer_id=str(appt.customer_id),
                    staff_id=str(appt.staff_id),
                    service_id=str(appt.service_id),
                    location_id=str(appt.location_id) if appt.location_id else None,
                    start_time=appt.start_time.isoformat(),
                    end_time=appt.end_time.isoformat(),
                    status=appt.status,
                    notes=appt.notes,
                    price=appt.price,
                    cancellation_reason=appt.cancellation_reason,
                    cancelled_at=appt.cancelled_at.isoformat() if appt.cancelled_at else None,
                    no_show_reason=appt.no_show_reason,
                    marked_no_show_at=appt.marked_no_show_at.isoformat() if appt.marked_no_show_at else None,
                    confirmed_at=appt.confirmed_at.isoformat() if appt.confirmed_at else None,
                    created_at=appt.created_at.isoformat(),
                    updated_at=appt.updated_at.isoformat(),
                )
                for appt in appointments
            ],
            total=len(appointments),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/month/{date}", response_model=MonthViewResponse)
@tenant_isolated
async def get_month_view(
    date: str = Path(..., description="Any date in the month (ISO format YYYY-MM-DD)"),
    staff_id: Optional[str] = Query(None, description="Optional staff ID filter"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Get appointments for a specific month.
    
    - **date**: Any date in the month (ISO format YYYY-MM-DD)
    - **staff_id**: Optional staff ID filter
    """
    try:
        date_obj = datetime.fromisoformat(date)
        staff_id_obj = ObjectId(staff_id) if staff_id else None
        
        appointments = AppointmentService.get_month_view(
            tenant_id=tenant_id,
            date=date_obj,
            staff_id=staff_id_obj,
        )
        
        month_str = date_obj.strftime("%Y-%m")
        
        return MonthViewResponse(
            month=month_str,
            appointments=[
                AppointmentResponse(
                    id=str(appt.id),
                    customer_id=str(appt.customer_id),
                    staff_id=str(appt.staff_id),
                    service_id=str(appt.service_id),
                    location_id=str(appt.location_id) if appt.location_id else None,
                    start_time=appt.start_time.isoformat(),
                    end_time=appt.end_time.isoformat(),
                    status=appt.status,
                    notes=appt.notes,
                    price=appt.price,
                    cancellation_reason=appt.cancellation_reason,
                    cancelled_at=appt.cancelled_at.isoformat() if appt.cancelled_at else None,
                    no_show_reason=appt.no_show_reason,
                    marked_no_show_at=appt.marked_no_show_at.isoformat() if appt.marked_no_show_at else None,
                    confirmed_at=appt.confirmed_at.isoformat() if appt.confirmed_at else None,
                    created_at=appt.created_at.isoformat(),
                    updated_at=appt.updated_at.isoformat(),
                )
                for appt in appointments
            ],
            total=len(appointments),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Generic list route - must come AFTER specific routes
@router.get("", response_model=AppointmentListResponse)
@tenant_isolated
async def list_appointments(
    customer_id: Optional[str] = Query(None),
    staff_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    List appointments with filtering.
    
    - **customer_id**: Filter by customer ID
    - **staff_id**: Filter by staff ID
    - **status**: Filter by status (scheduled, confirmed, completed, cancelled, no_show)
    - **start_date**: Filter by start date (ISO format)
    - **end_date**: Filter by end date (ISO format)
    - **page**: Page number (1-indexed)
    - **page_size**: Number of results per page
    """
    try:
        customer_id_obj = ObjectId(customer_id) if customer_id else None
        staff_id_obj = ObjectId(staff_id) if staff_id else None
        start_date_obj = datetime.fromisoformat(start_date) if start_date else None
        end_date_obj = datetime.fromisoformat(end_date) if end_date else None
        
        appointments, total = AppointmentService.list_appointments(
            tenant_id=tenant_id,
            customer_id=customer_id_obj,
            staff_id=staff_id_obj,
            status=status,
            start_date=start_date_obj,
            end_date=end_date_obj,
            page=page,
            page_size=page_size,
        )
        
        return AppointmentListResponse(
            appointments=[
                AppointmentResponse(
                    id=str(appt.id),
                    customer_id=str(appt.customer_id),
                    staff_id=str(appt.staff_id),
                    service_id=str(appt.service_id),
                    location_id=str(appt.location_id) if appt.location_id else None,
                    start_time=appt.start_time.isoformat(),
                    end_time=appt.end_time.isoformat(),
                    status=appt.status,
                    notes=appt.notes,
                    price=appt.price,
                    cancellation_reason=appt.cancellation_reason,
                    cancelled_at=appt.cancelled_at.isoformat() if appt.cancelled_at else None,
                    no_show_reason=appt.no_show_reason,
                    marked_no_show_at=appt.marked_no_show_at.isoformat() if appt.marked_no_show_at else None,
                    confirmed_at=appt.confirmed_at.isoformat() if appt.confirmed_at else None,
                    created_at=appt.created_at.isoformat(),
                    updated_at=appt.updated_at.isoformat(),
                )
                for appt in appointments
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{appointment_id}/confirm", response_model=AppointmentResponse)
async def confirm_appointment(
    appointment_id: str,
    request: AppointmentConfirmRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Confirm an appointment."""
    try:
        from app.services.appointment_history_service import AppointmentHistoryService
        
        appt_id = ObjectId(appointment_id)
        time_slot_id = ObjectId(request.time_slot_id) if request.time_slot_id else None
        
        appointment = AppointmentService.confirm_appointment(
            tenant_id, appt_id, time_slot_id=time_slot_id
        )
        
        # Create appointment history entry
        try:
            AppointmentHistoryService.create_history_from_appointment(tenant_id, appt_id)
        except Exception as e:
            logger.warning(f"Failed to create appointment history: {str(e)}")
        
        return AppointmentResponse(
            id=str(appointment.id),
            customer_id=str(appointment.customer_id),
            staff_id=str(appointment.staff_id),
            service_id=str(appointment.service_id),
            location_id=str(appointment.location_id) if appointment.location_id else None,
            start_time=appointment.start_time.isoformat(),
            end_time=appointment.end_time.isoformat(),
            status=appointment.status,
            notes=appointment.notes,
            price=appointment.price,
            cancellation_reason=appointment.cancellation_reason,
            cancelled_at=appointment.cancelled_at.isoformat() if appointment.cancelled_at else None,
            no_show_reason=appointment.no_show_reason,
            marked_no_show_at=appointment.marked_no_show_at.isoformat() if appointment.marked_no_show_at else None,
            confirmed_at=appointment.confirmed_at.isoformat() if appointment.confirmed_at else None,
            created_at=appointment.created_at.isoformat(),
            updated_at=appointment.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: str,
    request: AppointmentCancelRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Cancel an appointment."""
    try:
        appt_id = ObjectId(appointment_id)
        appointment = AppointmentService.cancel_appointment(
            tenant_id, appt_id, reason=request.reason
        )
        
        # Create appointment history entry
        try:
            AppointmentHistoryService.create_history_from_appointment(tenant_id, appt_id)
        except Exception as e:
            logger.warning(f"Failed to create appointment history: {str(e)}")
        
        return AppointmentResponse(
            id=str(appointment.id),
            customer_id=str(appointment.customer_id),
            staff_id=str(appointment.staff_id),
            service_id=str(appointment.service_id),
            location_id=str(appointment.location_id) if appointment.location_id else None,
            start_time=appointment.start_time.isoformat(),
            end_time=appointment.end_time.isoformat(),
            status=appointment.status,
            notes=appointment.notes,
            price=appointment.price,
            cancellation_reason=appointment.cancellation_reason,
            cancelled_at=appointment.cancelled_at.isoformat() if appointment.cancelled_at else None,
            no_show_reason=appointment.no_show_reason,
            marked_no_show_at=appointment.marked_no_show_at.isoformat() if appointment.marked_no_show_at else None,
            confirmed_at=appointment.confirmed_at.isoformat() if appointment.confirmed_at else None,
            created_at=appointment.created_at.isoformat(),
            updated_at=appointment.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{appointment_id}/complete", response_model=AppointmentResponse)
async def complete_appointment(
    appointment_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Mark an appointment as completed and create history entry.
    Auto-creates invoice and initializes payment.

    - **appointment_id**: Appointment ID
    """
    try:
        appt_id = ObjectId(appointment_id)
        appointment = AppointmentService.get_appointment(tenant_id, appt_id)

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Mark appointment as completed
        appointment.status = "completed"
        appointment.save()

        # Create history entry
        try:
            AppointmentHistoryService.create_history_from_appointment(tenant_id, appt_id)
        except ValueError as e:
            # If history creation fails, still return the completed appointment
            pass

        # Calculate and record commission for the completed appointment
        try:
            ServiceCommissionService.calculate_commission_for_appointment(tenant_id, appt_id)
        except Exception as e:
            # Log commission calculation error but don't fail the appointment completion
            logger.error(f"Failed to calculate commission for appointment {appt_id}: {e}")

        # PHASE 1: Auto-create invoice on appointment completion
        invoice = None
        try:
            logger.info(f"[CompleteAppointment] Starting invoice creation for appointment {appt_id}")
            logger.info(f"[CompleteAppointment] Appointment price: {appointment.price}, Service ID: {appointment.service_id}")
            
            # Check if appointment has a price
            if not appointment.price:
                logger.warning(f"[CompleteAppointment] Appointment {appt_id} has no price, fetching from service")
                service = Service.objects(tenant_id=tenant_id, id=appointment.service_id).first()
                if service:
                    appointment.price = service.price
                    appointment.save()
                    logger.info(f"[CompleteAppointment] Updated appointment price to {appointment.price}")
                else:
                    logger.error(f"[CompleteAppointment] Service {appointment.service_id} not found")
            
            if appointment.price:
                invoice = InvoiceService.create_invoice_from_appointment(
                    tenant_id=tenant_id,
                    appointment_id=appt_id,
                    discount=Decimal("0"),
                    tax=Decimal("0"),
                )
                # Set invoice status to "issued" (ready for payment)
                invoice.status = "issued"
                invoice.save()
                logger.info(f"Auto-created invoice {invoice.id} for appointment {appt_id}")
            else:
                logger.warning(f"[CompleteAppointment] Cannot create invoice: appointment {appt_id} has no price")
        except Exception as e:
            logger.error(f"Failed to auto-create invoice for appointment {appt_id}: {e}", exc_info=True)

        # PHASE 2: Auto-initialize payment when invoice is issued
        if invoice:
            try:
                # Fetch customer email
                customer = Customer.objects(
                    tenant_id=tenant_id,
                    id=appointment.customer_id
                ).first()
                
                if customer and customer.email:
                    payment_response = InvoiceService.auto_initialize_payment_for_invoice(
                        tenant_id=tenant_id,
                        invoice=invoice,
                        customer_email=customer.email,
                    )
                    if payment_response:
                        logger.info(f"Auto-initialized payment for invoice {invoice.id}")
                    else:
                        logger.warning(f"Payment initialization returned None for invoice {invoice.id}")
                else:
                    logger.warning(f"Cannot initialize payment: customer email not found for customer {appointment.customer_id}")
            except Exception as e:
                logger.error(f"Failed to auto-initialize payment for invoice {invoice.id}: {e}")

        return AppointmentResponse(
            id=str(appointment.id),
            customer_id=str(appointment.customer_id),
            staff_id=str(appointment.staff_id),
            service_id=str(appointment.service_id),
            location_id=str(appointment.location_id) if appointment.location_id else None,
            start_time=appointment.start_time.isoformat(),
            end_time=appointment.end_time.isoformat(),
            status=appointment.status,
            notes=appointment.notes,
            price=appointment.price,
            cancellation_reason=appointment.cancellation_reason,
            cancelled_at=appointment.cancelled_at.isoformat() if appointment.cancelled_at else None,
            no_show_reason=appointment.no_show_reason,
            marked_no_show_at=appointment.marked_no_show_at.isoformat() if appointment.marked_no_show_at else None,
            confirmed_at=appointment.confirmed_at.isoformat() if appointment.confirmed_at else None,
            created_at=appointment.created_at.isoformat(),
            updated_at=appointment.updated_at.isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/available-slots/{staff_id}/{service_id}", response_model=AvailableSlotsResponse)
async def get_available_slots(
    staff_id: str,
    service_id: str,
    date: str = Query(..., description="Date in ISO format (YYYY-MM-DD)"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Get available time slots for a staff member on a given date.
    
    - **staff_id**: Staff member ID
    - **service_id**: Service ID
    - **date**: Date in ISO format (YYYY-MM-DD)
    """
    try:
        staff_id_obj = ObjectId(staff_id)
        service_id_obj = ObjectId(service_id)
        date_obj = datetime.fromisoformat(date)
        
        slots = AppointmentService.get_available_slots(
            tenant_id=tenant_id,
            staff_id=staff_id_obj,
            service_id=service_id_obj,
            date=date_obj,
        )
        
        return AvailableSlotsResponse(
            date=date,
            slots=[
                AvailableSlot(
                    start_time=start.isoformat(),
                    end_time=end.isoformat(),
                    staff_id=staff_id,
                    available=True,
                )
                for start, end in slots
            ],
            total_available=len(slots),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))






@router.post("/{appointment_id}/no-show", response_model=AppointmentResponse)
async def mark_no_show(
    appointment_id: str,
    request: AppointmentCancelRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Mark an appointment as no-show."""
    try:
        appt_id = ObjectId(appointment_id)
        appointment = AppointmentService.mark_no_show(
            tenant_id, appt_id, reason=request.reason
        )
        
        # Create appointment history entry
        try:
            AppointmentHistoryService.create_history_from_appointment(tenant_id, appt_id)
        except Exception as e:
            logger.warning(f"Failed to create appointment history: {str(e)}")
        
        return AppointmentResponse(
            id=str(appointment.id),
            customer_id=str(appointment.customer_id),
            staff_id=str(appointment.staff_id),
            service_id=str(appointment.service_id),
            location_id=str(appointment.location_id) if appointment.location_id else None,
            start_time=appointment.start_time.isoformat(),
            end_time=appointment.end_time.isoformat(),
            status=appointment.status,
            notes=appointment.notes,
            price=appointment.price,
            cancellation_reason=appointment.cancellation_reason,
            cancelled_at=appointment.cancelled_at.isoformat() if appointment.cancelled_at else None,
            no_show_reason=appointment.no_show_reason,
            marked_no_show_at=appointment.marked_no_show_at.isoformat() if appointment.marked_no_show_at else None,
            confirmed_at=appointment.confirmed_at.isoformat() if appointment.confirmed_at else None,
            created_at=appointment.created_at.isoformat(),
            updated_at=appointment.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    request: AppointmentUpdateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Update an appointment (notes, status, etc).
    
    - **appointment_id**: Appointment ID
    - **notes**: Appointment notes (optional)
    - **status**: Appointment status (optional)
    """
    try:
        appt_id = ObjectId(appointment_id)
        appointment = AppointmentService.get_appointment(tenant_id, appt_id)

        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        # Update notes if provided
        if request.notes is not None:
            appointment.notes = request.notes

        # Update status if provided
        if request.status is not None:
            appointment.status = request.status

        # Update cancellation reason if provided
        if request.cancellation_reason is not None:
            appointment.cancellation_reason = request.cancellation_reason

        appointment.save()

        return AppointmentResponse(
            id=str(appointment.id),
            customer_id=str(appointment.customer_id),
            staff_id=str(appointment.staff_id),
            service_id=str(appointment.service_id),
            location_id=str(appointment.location_id) if appointment.location_id else None,
            start_time=appointment.start_time.isoformat(),
            end_time=appointment.end_time.isoformat(),
            status=appointment.status,
            notes=appointment.notes,
            price=appointment.price,
            cancellation_reason=appointment.cancellation_reason,
            cancelled_at=appointment.cancelled_at.isoformat() if appointment.cancelled_at else None,
            no_show_reason=appointment.no_show_reason,
            marked_no_show_at=appointment.marked_no_show_at.isoformat() if appointment.marked_no_show_at else None,
            confirmed_at=appointment.confirmed_at.isoformat() if appointment.confirmed_at else None,
            created_at=appointment.created_at.isoformat(),
            updated_at=appointment.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
