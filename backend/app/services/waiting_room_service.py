"""Waiting room service for managing queue and check-in."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.models.waiting_room import QueueEntry, WaitingRoom, QueueHistory
from app.context import get_tenant_id


class WaitingRoomService:
    """Service for managing waiting room queue."""

    @staticmethod
    def check_in_customer(
        appointment_id: str,
        customer_id: str,
        customer_name: str,
        customer_phone: str = None,
        service_id: str = None,
        service_name: str = None,
        staff_id: str = None,
        staff_name: str = None,
        estimated_wait_time: int = None,
    ) -> Optional[QueueEntry]:
        """Check in a customer to the waiting room."""
        tenant_id = get_tenant_id()

        # Check if customer is already in queue
        existing = QueueEntry.objects(
            tenant_id=tenant_id,
            appointment_id=appointment_id,
            status__in=["waiting", "called"],
        ).first()

        if existing:
            return existing

        # Get current queue count to determine position
        queue_count = QueueEntry.objects(
            tenant_id=tenant_id, status__in=["waiting", "called"]
        ).count()

        queue_entry = QueueEntry(
            tenant_id=tenant_id,
            appointment_id=appointment_id,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            check_in_time=datetime.utcnow(),
            position=queue_count + 1,
            service_id=service_id,
            service_name=service_name,
            staff_id=staff_id,
            staff_name=staff_name,
            estimated_wait_time_minutes=estimated_wait_time,
        )
        queue_entry.save()

        # Update waiting room status
        WaitingRoomService._update_waiting_room_status()

        return queue_entry

    @staticmethod
    def get_queue_entry(entry_id: str) -> Optional[QueueEntry]:
        """Get queue entry by ID."""
        tenant_id = get_tenant_id()
        return QueueEntry.objects(id=entry_id, tenant_id=tenant_id).first()

    @staticmethod
    def get_current_queue(
        status: str = None, limit: int = 50, skip: int = 0
    ) -> List[QueueEntry]:
        """Get current queue entries."""
        tenant_id = get_tenant_id()
        query = QueueEntry.objects(tenant_id=tenant_id)

        if status:
            query = query(status=status)
        else:
            # Default: get waiting and called customers
            query = query(status__in=["waiting", "called"])

        return query.order_by("position")[skip : skip + limit]

    @staticmethod
    def get_next_customer() -> Optional[QueueEntry]:
        """Get next customer in queue."""
        tenant_id = get_tenant_id()
        return QueueEntry.objects(
            tenant_id=tenant_id, status="waiting"
        ).order_by("position").first()

    @staticmethod
    def call_customer(entry_id: str) -> Optional[QueueEntry]:
        """Call next customer in queue."""
        entry = WaitingRoomService.get_queue_entry(entry_id)
        if entry:
            entry.mark_called()
            WaitingRoomService._update_waiting_room_status()
        return entry

    @staticmethod
    def start_service(entry_id: str) -> Optional[QueueEntry]:
        """Mark customer as in service."""
        entry = WaitingRoomService.get_queue_entry(entry_id)
        if entry:
            entry.mark_in_service()
            WaitingRoomService._update_waiting_room_status()
        return entry

    @staticmethod
    def complete_service(entry_id: str) -> Optional[QueueEntry]:
        """Mark service as completed."""
        entry = WaitingRoomService.get_queue_entry(entry_id)
        if entry:
            entry.mark_completed()

            # Archive to history
            WaitingRoomService._archive_to_history(entry)

            # Update queue positions
            WaitingRoomService._update_queue_positions()

            # Update waiting room status
            WaitingRoomService._update_waiting_room_status()

        return entry

    @staticmethod
    def mark_no_show(entry_id: str, reason: str = None) -> Optional[QueueEntry]:
        """Mark customer as no-show."""
        entry = WaitingRoomService.get_queue_entry(entry_id)
        if entry:
            entry.mark_no_show(reason)

            # Archive to history
            WaitingRoomService._archive_to_history(entry)

            # Update queue positions
            WaitingRoomService._update_queue_positions()

            # Update waiting room status
            WaitingRoomService._update_waiting_room_status()

        return entry

    @staticmethod
    def cancel_queue_entry(entry_id: str) -> Optional[QueueEntry]:
        """Cancel queue entry."""
        entry = WaitingRoomService.get_queue_entry(entry_id)
        if entry:
            entry.mark_cancelled()

            # Archive to history
            WaitingRoomService._archive_to_history(entry)

            # Update queue positions
            WaitingRoomService._update_queue_positions()

            # Update waiting room status
            WaitingRoomService._update_waiting_room_status()

        return entry

    @staticmethod
    def get_customer_position(customer_id: str) -> Optional[int]:
        """Get customer's position in queue."""
        tenant_id = get_tenant_id()
        entry = QueueEntry.objects(
            tenant_id=tenant_id, customer_id=customer_id, status__in=["waiting", "called"]
        ).first()

        return entry.position if entry else None

    @staticmethod
    def get_estimated_wait_time(customer_id: str) -> Optional[int]:
        """Get estimated wait time for customer."""
        tenant_id = get_tenant_id()
        entry = QueueEntry.objects(
            tenant_id=tenant_id, customer_id=customer_id, status__in=["waiting", "called"]
        ).first()

        if not entry:
            return None

        # Get average service time from completed services
        completed = QueueEntry.objects(
            tenant_id=tenant_id, status="completed", service_duration_minutes__ne=None
        ).order_by("-service_end_time")[:10]

        if not completed:
            return entry.estimated_wait_time_minutes

        avg_service_time = sum(
            [e.service_duration_minutes for e in completed if e.service_duration_minutes]
        ) / len(completed)

        # Calculate wait time based on position and average service time
        customers_ahead = QueueEntry.objects(
            tenant_id=tenant_id, status__in=["in_service"], position__lt=entry.position
        ).count()

        estimated_wait = int(customers_ahead * avg_service_time)
        return estimated_wait

    @staticmethod
    def get_queue_stats() -> Dict[str, Any]:
        """Get queue statistics."""
        tenant_id = get_tenant_id()

        # Current queue
        waiting = QueueEntry.objects(tenant_id=tenant_id, status="waiting").count()
        called = QueueEntry.objects(tenant_id=tenant_id, status="called").count()
        in_service = QueueEntry.objects(tenant_id=tenant_id, status="in_service").count()

        # Completed today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        completed_today = QueueEntry.objects(
            tenant_id=tenant_id, status="completed", service_end_time__gte=today_start
        ).count()

        no_show_today = QueueEntry.objects(
            tenant_id=tenant_id, status="no_show", check_in_time__gte=today_start
        ).count()

        # Average wait time
        completed_entries = QueueEntry.objects(
            tenant_id=tenant_id, status="completed", wait_duration_minutes__ne=None
        ).order_by("-service_end_time")[:50]

        avg_wait_time = 0
        if completed_entries:
            avg_wait_time = int(
                sum([e.wait_duration_minutes for e in completed_entries])
                / len(completed_entries)
            )

        return {
            "current_queue": {
                "waiting": waiting,
                "called": called,
                "in_service": in_service,
                "total": waiting + called + in_service,
            },
            "today": {
                "completed": completed_today,
                "no_show": no_show_today,
            },
            "average_wait_time_minutes": avg_wait_time,
        }

    @staticmethod
    def get_queue_history(
        start_date: datetime = None,
        end_date: datetime = None,
        status: str = None,
        limit: int = 100,
        skip: int = 0,
    ) -> List[QueueHistory]:
        """Get queue history."""
        tenant_id = get_tenant_id()
        query = QueueHistory.objects(tenant_id=tenant_id)

        if start_date:
            query = query(check_in_time__gte=start_date)
        if end_date:
            query = query(check_in_time__lte=end_date)
        if status:
            query = query(status=status)

        return query.order_by("-check_in_time")[skip : skip + limit]

    @staticmethod
    def get_waiting_room(location_id: str = None) -> Optional[WaitingRoom]:
        """Get waiting room."""
        tenant_id = get_tenant_id()
        query = WaitingRoom.objects(tenant_id=tenant_id)

        if location_id:
            query = query(location_id=location_id)

        return query.first()

    @staticmethod
    def create_waiting_room(
        name: str, location_id: str = None, max_queue_length: int = None
    ) -> WaitingRoom:
        """Create a waiting room."""
        tenant_id = get_tenant_id()

        waiting_room = WaitingRoom(
            tenant_id=tenant_id,
            name=name,
            location_id=location_id,
            max_queue_length=max_queue_length,
        )
        waiting_room.save()
        return waiting_room

    # Private helper methods
    @staticmethod
    def _update_queue_positions():
        """Update queue positions after changes."""
        tenant_id = get_tenant_id()
        queue_entries = QueueEntry.objects(
            tenant_id=tenant_id, status__in=["waiting", "called"]
        ).order_by("check_in_time")

        for position, entry in enumerate(queue_entries, 1):
            entry.position = position
            entry.save()

    @staticmethod
    def _update_waiting_room_status():
        """Update waiting room status."""
        tenant_id = get_tenant_id()

        # Get current queue count
        queue_count = QueueEntry.objects(
            tenant_id=tenant_id, status__in=["waiting", "called"]
        ).count()

        # Get average wait time
        completed = QueueEntry.objects(
            tenant_id=tenant_id, status="completed", wait_duration_minutes__ne=None
        ).order_by("-service_end_time")[:20]

        avg_wait_time = 0
        if completed:
            avg_wait_time = int(
                sum([e.wait_duration_minutes for e in completed]) / len(completed)
            )

        # Update waiting room
        waiting_room = WaitingRoom.objects(tenant_id=tenant_id).first()
        if waiting_room:
            waiting_room.update_queue_status(queue_count, avg_wait_time)

    @staticmethod
    def _archive_to_history(entry: QueueEntry):
        """Archive queue entry to history."""
        tenant_id = get_tenant_id()

        # Calculate total duration
        total_duration = None
        if entry.check_in_time and entry.service_end_time:
            total_duration = int(
                (entry.service_end_time - entry.check_in_time).total_seconds() / 60
            )

        history = QueueHistory(
            tenant_id=tenant_id,
            appointment_id=entry.appointment_id,
            customer_id=entry.customer_id,
            customer_name=entry.customer_name,
            check_in_time=entry.check_in_time,
            called_time=entry.called_time,
            service_start_time=entry.service_start_time,
            service_end_time=entry.service_end_time,
            wait_duration_minutes=entry.wait_duration_minutes,
            service_duration_minutes=entry.service_duration_minutes,
            total_duration_minutes=total_duration,
            status=entry.status,
            no_show_reason=entry.no_show_reason,
            service_id=entry.service_id,
            service_name=entry.service_name,
            staff_id=entry.staff_id,
            staff_name=entry.staff_name,
        )
        history.save()

        # Remove from active queue
        entry.delete()
