"""Public waitlist service for customer-facing waitlist features."""

from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from app.models.waiting_room import QueueEntry, WaitingRoom
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.staff import Staff
from app.services.waiting_room_service import WaitingRoomService


class PublicWaitlistService:
    """Service for managing public-facing waitlist."""

    @staticmethod
    def join_waitlist(
        tenant_id: ObjectId,
        service_id: str,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        staff_id: Optional[str] = None,
        preferred_date: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> QueueEntry:
        """
        Add customer to public waitlist.
        
        Creates a pending appointment and adds customer to queue.
        """
        # Get service details
        service = Service.objects(id=ObjectId(service_id), tenant_id=tenant_id).first()
        if not service:
            raise ValueError("Service not found")

        # Get staff details if provided
        staff_name = None
        if staff_id:
            staff = Staff.objects(id=ObjectId(staff_id), tenant_id=tenant_id).first()
            if staff:
                staff_name = staff.name

        # Create a pending appointment for the waitlist entry
        appointment = Appointment(
            tenant_id=tenant_id,
            service_id=ObjectId(service_id),
            staff_id=ObjectId(staff_id) if staff_id else None,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            is_guest=True,
            status="waitlist",  # Special status for waitlist
            notes=notes or "",
            # No specific date/time yet - will be assigned when slot becomes available
            date=None,
            start_time=None,
            end_time=None,
        )
        appointment.save()

        # Calculate estimated wait time based on current queue
        estimated_wait = PublicWaitlistService._calculate_estimated_wait(
            tenant_id, service_id
        )

        # Add to queue
        queue_entry = WaitingRoomService.check_in_customer(
            appointment_id=str(appointment.id),
            customer_id=customer_email,  # Use email as customer ID for guests
            customer_name=customer_name,
            customer_phone=customer_phone,
            service_id=service_id,
            service_name=service.name,
            staff_id=staff_id,
            staff_name=staff_name,
            estimated_wait_time=estimated_wait,
        )

        return queue_entry

    @staticmethod
    def get_waitlist_status(tenant_id: ObjectId) -> Dict[str, Any]:
        """Get current waitlist status for public display."""
        # Get waiting room
        waiting_room = WaitingRoom.objects(tenant_id=tenant_id).first()

        if not waiting_room:
            return {
                "queue_length": 0,
                "average_wait_time_minutes": 0,
                "is_accepting": True,
                "message": "Waitlist is available",
            }

        # Check if accepting new entries
        is_accepting = waiting_room.is_accepting_checkins
        if waiting_room.max_queue_length:
            is_accepting = (
                is_accepting
                and waiting_room.current_queue_count < waiting_room.max_queue_length
            )

        message = None
        if not is_accepting:
            if waiting_room.max_queue_length and waiting_room.current_queue_count >= waiting_room.max_queue_length:
                message = "Waitlist is currently full. Please try again later."
            else:
                message = "Waitlist is temporarily closed."

        return {
            "queue_length": waiting_room.current_queue_count,
            "average_wait_time_minutes": waiting_room.average_wait_time_minutes,
            "is_accepting": is_accepting,
            "message": message,
        }

    @staticmethod
    def get_customer_position(
        tenant_id: ObjectId, customer_email: str
    ) -> Optional[Dict[str, Any]]:
        """Get customer's position in waitlist."""
        # Find queue entry by customer email (used as customer_id for guests)
        queue_entry = QueueEntry.objects(
            tenant_id=tenant_id,
            customer_id=customer_email,
            status__in=["waiting", "called"],
        ).first()

        if not queue_entry:
            return None

        # Get estimated wait time
        estimated_wait = WaitingRoomService.get_estimated_wait_time(customer_email)

        return {
            "position": queue_entry.position,
            "estimated_wait_time_minutes": estimated_wait or queue_entry.estimated_wait_time_minutes or 0,
            "status": queue_entry.status,
            "check_in_time": queue_entry.check_in_time,
            "service_name": queue_entry.service_name,
            "staff_name": queue_entry.staff_name,
        }

    @staticmethod
    def cancel_waitlist_entry(
        tenant_id: ObjectId, customer_email: str
    ) -> bool:
        """Cancel customer's waitlist entry."""
        # Find queue entry
        queue_entry = QueueEntry.objects(
            tenant_id=tenant_id,
            customer_id=customer_email,
            status__in=["waiting", "called"],
        ).first()

        if not queue_entry:
            return False

        # Cancel the queue entry
        WaitingRoomService.cancel_queue_entry(str(queue_entry.id))

        # Cancel the associated appointment
        appointment = Appointment.objects(
            id=ObjectId(queue_entry.appointment_id)
        ).first()
        if appointment:
            appointment.status = "cancelled"
            appointment.save()

        return True

    @staticmethod
    def _calculate_estimated_wait(tenant_id: ObjectId, service_id: str) -> int:
        """Calculate estimated wait time for a service."""
        # Get current queue count for this service
        queue_count = QueueEntry.objects(
            tenant_id=tenant_id,
            service_id=ObjectId(service_id),
            status__in=["waiting", "called", "in_service"],
        ).count()

        # Get service duration
        service = Service.objects(id=ObjectId(service_id), tenant_id=tenant_id).first()
        if not service:
            return 30  # Default 30 minutes

        service_duration = service.duration_minutes or 30

        # Get average wait time from recent completions
        recent_completed = QueueEntry.objects(
            tenant_id=tenant_id,
            service_id=ObjectId(service_id),
            status="completed",
            wait_duration_minutes__ne=None,
        ).order_by("-service_end_time")[:10]

        if recent_completed:
            avg_wait = sum(e.wait_duration_minutes for e in recent_completed) / len(
                recent_completed
            )
            # Estimate: average wait + (queue count * service duration)
            return int(avg_wait + (queue_count * service_duration))

        # Fallback: queue count * service duration
        return queue_count * service_duration
