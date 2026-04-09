"""Service for managing availability events and real-time updates."""

from datetime import datetime, timedelta
from typing import Optional, List
from bson import ObjectId
from app.models.availability_event import AvailabilityEvent


class AvailabilityEventService:
    """Service for managing availability events."""
    
    @staticmethod
    def create_event(
        tenant_id: ObjectId,
        service_id: ObjectId,
        date: datetime,
        time_slot: str,
        event_type: str,
        staff_id: Optional[ObjectId] = None,
    ) -> AvailabilityEvent:
        """Create a new availability event."""
        event = AvailabilityEvent(
            tenant_id=tenant_id,
            service_id=service_id,
            staff_id=staff_id,
            date=date,
            time_slot=time_slot,
            event_type=event_type,
        )
        event.save()
        return event
    
    @staticmethod
    def get_recent_events(
        tenant_id: ObjectId,
        service_id: ObjectId,
        date: datetime,
        minutes: int = 30,
    ) -> List[AvailabilityEvent]:
        """Get recent availability events for a service on a specific date."""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        events = AvailabilityEvent.objects(
            tenant_id=tenant_id,
            service_id=service_id,
            date=date,
            created_at__gte=cutoff_time,
        ).order_by('-created_at')
        
        return list(events)
    
    @staticmethod
    def increment_viewer_count(
        tenant_id: ObjectId,
        service_id: ObjectId,
        date: datetime,
        time_slot: str,
        staff_id: Optional[ObjectId] = None,
    ) -> int:
        """Increment viewer count for a specific slot."""
        # Find or create event for this slot
        query = {
            "tenant_id": tenant_id,
            "service_id": service_id,
            "date": date,
            "time_slot": time_slot,
        }
        
        if staff_id:
            query["staff_id"] = staff_id
        
        event = AvailabilityEvent.objects(**query).first()
        
        if not event:
            # Create new event with viewer count
            event = AvailabilityEvent(
                tenant_id=tenant_id,
                service_id=service_id,
                staff_id=staff_id,
                date=date,
                time_slot=time_slot,
                event_type="viewing",
                viewer_count=1,
            )
            event.save()
            return 1
        else:
            # Increment existing viewer count
            event.viewer_count += 1
            event.save()
            return event.viewer_count
    
    @staticmethod
    def decrement_viewer_count(
        tenant_id: ObjectId,
        service_id: ObjectId,
        date: datetime,
        time_slot: str,
        staff_id: Optional[ObjectId] = None,
    ) -> int:
        """Decrement viewer count for a specific slot."""
        query = {
            "tenant_id": tenant_id,
            "service_id": service_id,
            "date": date,
            "time_slot": time_slot,
        }
        
        if staff_id:
            query["staff_id"] = staff_id
        
        event = AvailabilityEvent.objects(**query).first()
        
        if event and event.viewer_count > 0:
            event.viewer_count -= 1
            event.save()
            return event.viewer_count
        
        return 0
    
    @staticmethod
    def get_viewer_count(
        tenant_id: ObjectId,
        service_id: ObjectId,
        date: datetime,
        time_slot: str,
        staff_id: Optional[ObjectId] = None,
    ) -> int:
        """Get current viewer count for a specific slot."""
        query = {
            "tenant_id": tenant_id,
            "service_id": service_id,
            "date": date,
            "time_slot": time_slot,
        }
        
        if staff_id:
            query["staff_id"] = staff_id
        
        event = AvailabilityEvent.objects(**query).first()
        
        return event.viewer_count if event else 0
    
    @staticmethod
    def cleanup_old_events(days: int = 7):
        """Clean up availability events older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = AvailabilityEvent.objects(created_at__lt=cutoff_date).delete()
        
        return result
