"""Service for managing time slot reservations."""

from datetime import datetime, timedelta
from typing import Optional, List
from bson import ObjectId
from mongoengine import Q
from app.models.time_slot import TimeSlot
from app.models.appointment import Appointment


class TimeSlotService:
    """Service for time slot reservation management."""

    RESERVATION_WINDOW_MINUTES = 10

    @staticmethod
    def reserve_slot(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        service_id: ObjectId,
        start_time: datetime,
        end_time: datetime,
        customer_id: Optional[ObjectId] = None,
    ) -> TimeSlot:
        """
        Reserve a time slot for a customer.
        
        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            service_id: Service ID
            start_time: Slot start time (UTC)
            end_time: Slot end time (UTC)
            customer_id: Optional customer ID
            
        Returns:
            Created TimeSlot document
            
        Raises:
            ValueError: If slot is already reserved or booked
        """
        # Check if slot is already reserved or booked
        existing = TimeSlot.objects(
            Q(tenant_id=tenant_id) &
            Q(staff_id=staff_id) &
            Q(status__in=["reserved", "confirmed"]) &
            Q(start_time__lt=end_time) &
            Q(end_time__gt=start_time)
        ).first()
        
        if existing:
            raise ValueError(
                f"Time slot is already reserved for staff {staff_id} "
                f"between {start_time} and {end_time}"
            )
        
        # Check if slot is already booked (confirmed appointment)
        booked = Appointment.objects(
            Q(tenant_id=tenant_id) &
            Q(staff_id=staff_id) &
            Q(status__ne="cancelled") &
            Q(start_time__lt=end_time) &
            Q(end_time__gt=start_time)
        ).first()
        
        if booked:
            raise ValueError(
                f"Time slot is already booked for staff {staff_id} "
                f"between {start_time} and {end_time}"
            )
        
        # Create reservation
        expires_at = datetime.utcnow() + timedelta(minutes=TimeSlotService.RESERVATION_WINDOW_MINUTES)
        
        time_slot = TimeSlot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            customer_id=customer_id,
            start_time=start_time,
            end_time=end_time,
            status="reserved",
            reserved_at=datetime.utcnow(),
            expires_at=expires_at,
        )
        time_slot.save()
        return time_slot

    @staticmethod
    def confirm_reservation(
        tenant_id: ObjectId,
        time_slot_id: ObjectId,
        appointment_id: ObjectId,
    ) -> TimeSlot:
        """
        Confirm a time slot reservation by linking to appointment.
        
        Args:
            tenant_id: Tenant ID
            time_slot_id: TimeSlot ID
            appointment_id: Appointment ID
            
        Returns:
            Updated TimeSlot document
            
        Raises:
            ValueError: If time slot not found or expired
        """
        time_slot = TimeSlot.objects(
            tenant_id=tenant_id, id=time_slot_id
        ).first()
        
        if not time_slot:
            raise ValueError(f"Time slot {time_slot_id} not found")
        
        if time_slot.is_expired():
            time_slot.status = "expired"
            time_slot.save()
            raise ValueError(f"Time slot {time_slot_id} has expired")
        
        time_slot.status = "confirmed"
        time_slot.appointment_id = appointment_id
        time_slot.save()
        return time_slot

    @staticmethod
    def release_reservation(
        tenant_id: ObjectId,
        time_slot_id: ObjectId,
    ) -> TimeSlot:
        """
        Release a time slot reservation.
        
        Args:
            tenant_id: Tenant ID
            time_slot_id: TimeSlot ID
            
        Returns:
            Updated TimeSlot document
            
        Raises:
            ValueError: If time slot not found
        """
        time_slot = TimeSlot.objects(
            tenant_id=tenant_id, id=time_slot_id
        ).first()
        
        if not time_slot:
            raise ValueError(f"Time slot {time_slot_id} not found")
        
        time_slot.status = "released"
        time_slot.save()
        return time_slot

    @staticmethod
    def cleanup_expired_reservations(tenant_id: ObjectId) -> int:
        """
        Clean up expired reservations.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Number of expired reservations cleaned up
        """
        now = datetime.utcnow()
        
        # Find expired reservations
        expired = TimeSlot.objects(
            Q(tenant_id=tenant_id) &
            Q(status="reserved") &
            Q(expires_at__lt=now)
        )
        
        count = expired.count()
        
        # Mark as expired
        for slot in expired:
            slot.status = "expired"
            slot.save()
        
        return count

    @staticmethod
    def get_time_slot(
        tenant_id: ObjectId,
        time_slot_id: ObjectId,
    ) -> Optional[TimeSlot]:
        """
        Get a time slot by ID.
        
        Args:
            tenant_id: Tenant ID
            time_slot_id: TimeSlot ID
            
        Returns:
            TimeSlot document or None if not found
        """
        return TimeSlot.objects(tenant_id=tenant_id, id=time_slot_id).first()

    @staticmethod
    def list_active_reservations(
        tenant_id: ObjectId,
        staff_id: Optional[ObjectId] = None,
    ) -> List[TimeSlot]:
        """
        List active (non-expired) reservations.
        
        Args:
            tenant_id: Tenant ID
            staff_id: Optional staff ID filter
            
        Returns:
            List of active TimeSlot documents
        """
        query = Q(tenant_id=tenant_id) & Q(status="reserved")
        
        if staff_id:
            query &= Q(staff_id=staff_id)
        
        return list(TimeSlot.objects(query).order_by("expires_at"))
