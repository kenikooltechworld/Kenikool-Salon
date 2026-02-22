"""Resource service for managing physical resources."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from app.models.resource import (
    Resource,
    ResourceAvailability,
    ResourceAssignment,
    ResourceUtilization,
    ResourceMaintenance,
)
from app.context import get_tenant_id


class ResourceService:
    """Service for managing resources."""

    @staticmethod
    def create_resource(
        name: str,
        type: str,
        quantity: int = 1,
        location_id: str = None,
        description: str = None,
        purchase_date: datetime = None,
        purchase_price: Decimal = None,
        tags: List[str] = None,
    ) -> Resource:
        """Create a new resource."""
        tenant_id = get_tenant_id()

        resource = Resource(
            tenant_id=tenant_id,
            name=name,
            type=type,
            quantity=quantity,
            available_quantity=quantity,
            location_id=location_id,
            description=description,
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            tags=tags or [],
        )
        resource.save()
        return resource

    @staticmethod
    def get_resource(resource_id: str) -> Optional[Resource]:
        """Get resource by ID."""
        tenant_id = get_tenant_id()
        return Resource.objects(id=resource_id, tenant_id=tenant_id).first()

    @staticmethod
    def get_resources(
        type: str = None,
        status: str = None,
        location_id: str = None,
        is_active: bool = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[Resource]:
        """Get resources with optional filtering."""
        tenant_id = get_tenant_id()
        query = Resource.objects(tenant_id=tenant_id)

        if type:
            query = query(type=type)
        if status:
            query = query(status=status)
        if location_id:
            query = query(location_id=location_id)
        if is_active is not None:
            query = query(is_active=is_active)

        return query.order_by("-created_at")[skip : skip + limit]

    @staticmethod
    def update_resource(
        resource_id: str,
        name: str = None,
        description: str = None,
        quantity: int = None,
        tags: List[str] = None,
    ) -> Optional[Resource]:
        """Update a resource."""
        tenant_id = get_tenant_id()
        resource = Resource.objects(id=resource_id, tenant_id=tenant_id).first()

        if resource:
            if name:
                resource.name = name
            if description:
                resource.description = description
            if quantity:
                resource.quantity = quantity
            if tags:
                resource.tags = tags
            resource.save()

        return resource

    @staticmethod
    def delete_resource(resource_id: str) -> bool:
        """Delete a resource (soft delete by marking inactive)."""
        tenant_id = get_tenant_id()
        resource = Resource.objects(id=resource_id, tenant_id=tenant_id).first()

        if resource:
            resource.is_active = False
            resource.status = "inactive"
            resource.save()
            return True
        return False

    @staticmethod
    def reserve_resource(resource_id: str, quantity: int = 1) -> bool:
        """Reserve resource quantity."""
        resource = ResourceService.get_resource(resource_id)
        if resource:
            return resource.reserve(quantity)
        return False

    @staticmethod
    def release_resource(resource_id: str, quantity: int = 1):
        """Release reserved resource quantity."""
        resource = ResourceService.get_resource(resource_id)
        if resource:
            resource.release(quantity)

    @staticmethod
    def check_resource_availability(
        resource_id: str, quantity: int = 1, date: datetime = None
    ) -> bool:
        """Check if resource is available for booking."""
        resource = ResourceService.get_resource(resource_id)
        if not resource:
            return False

        # Check if resource is active and has available quantity
        if not resource.is_available():
            return False

        if resource.available_quantity < quantity:
            return False

        # Check if resource is under maintenance on the given date
        if date:
            maintenance = ResourceMaintenance.objects(
                tenant_id=get_tenant_id(),
                resource_id=resource_id,
                scheduled_date__lte=date,
                status__in=["scheduled", "in_progress"],
            ).first()
            if maintenance:
                return False

        return True

    @staticmethod
    def get_available_resources(
        type: str = None, quantity: int = 1, date: datetime = None
    ) -> List[Resource]:
        """Get available resources of a specific type."""
        tenant_id = get_tenant_id()
        query = Resource.objects(
            tenant_id=tenant_id, status="active", is_active=True, available_quantity__gte=quantity
        )

        if type:
            query = query(type=type)

        resources = query.order_by("-available_quantity")

        # Filter out resources under maintenance
        if date:
            available = []
            for resource in resources:
                if ResourceService.check_resource_availability(str(resource.id), quantity, date):
                    available.append(resource)
            return available

        return resources

    # Resource Availability Management
    @staticmethod
    def set_availability(
        resource_id: str,
        start_time: str,
        end_time: str,
        day_of_week: str = None,
        is_recurring: bool = True,
        effective_from: datetime = None,
        effective_to: datetime = None,
    ) -> ResourceAvailability:
        """Set resource availability."""
        tenant_id = get_tenant_id()

        availability = ResourceAvailability(
            tenant_id=tenant_id,
            resource_id=resource_id,
            start_time=start_time,
            end_time=end_time,
            day_of_week=day_of_week,
            is_recurring=is_recurring,
            effective_from=effective_from,
            effective_to=effective_to,
        )
        availability.save()
        return availability

    @staticmethod
    def get_availability(resource_id: str) -> List[ResourceAvailability]:
        """Get resource availability."""
        tenant_id = get_tenant_id()
        return ResourceAvailability.objects(
            tenant_id=tenant_id, resource_id=resource_id, is_active=True
        )

    # Resource Assignment Management
    @staticmethod
    def assign_resource_to_appointment(
        appointment_id: str, resource_id: str, quantity: int = 1
    ) -> Optional[ResourceAssignment]:
        """Assign resource to appointment."""
        tenant_id = get_tenant_id()

        # Check if resource is available
        if not ResourceService.check_resource_availability(resource_id, quantity):
            return None

        # Reserve the resource
        if not ResourceService.reserve_resource(resource_id, quantity):
            return None

        assignment = ResourceAssignment(
            tenant_id=tenant_id,
            appointment_id=appointment_id,
            resource_id=resource_id,
            quantity_used=quantity,
        )
        assignment.save()
        return assignment

    @staticmethod
    def get_appointment_resources(appointment_id: str) -> List[ResourceAssignment]:
        """Get resources assigned to appointment."""
        tenant_id = get_tenant_id()
        return ResourceAssignment.objects(
            tenant_id=tenant_id, appointment_id=appointment_id, status__ne="cancelled"
        )

    @staticmethod
    def release_appointment_resources(appointment_id: str):
        """Release all resources assigned to appointment."""
        tenant_id = get_tenant_id()
        assignments = ResourceAssignment.objects(
            tenant_id=tenant_id, appointment_id=appointment_id, status__ne="released"
        )

        for assignment in assignments:
            ResourceService.release_resource(str(assignment.resource_id), assignment.quantity_used)
            assignment.release()

    # Resource Maintenance Management
    @staticmethod
    def schedule_maintenance(
        resource_id: str,
        maintenance_type: str,
        scheduled_date: datetime,
        estimated_duration_hours: int = None,
        description: str = None,
        cost: Decimal = None,
    ) -> ResourceMaintenance:
        """Schedule resource maintenance."""
        tenant_id = get_tenant_id()

        maintenance = ResourceMaintenance(
            tenant_id=tenant_id,
            resource_id=resource_id,
            maintenance_type=maintenance_type,
            scheduled_date=scheduled_date,
            estimated_duration_hours=estimated_duration_hours,
            description=description,
            cost=cost,
        )
        maintenance.save()

        # Mark resource as under maintenance
        resource = ResourceService.get_resource(resource_id)
        if resource:
            resource.mark_maintenance()

        return maintenance

    @staticmethod
    def get_maintenance_schedule(
        resource_id: str = None, status: str = None
    ) -> List[ResourceMaintenance]:
        """Get maintenance schedule."""
        tenant_id = get_tenant_id()
        query = ResourceMaintenance.objects(tenant_id=tenant_id)

        if resource_id:
            query = query(resource_id=resource_id)
        if status:
            query = query(status=status)

        return query.order_by("scheduled_date")

    @staticmethod
    def complete_maintenance(maintenance_id: str) -> Optional[ResourceMaintenance]:
        """Mark maintenance as completed."""
        tenant_id = get_tenant_id()
        maintenance = ResourceMaintenance.objects(
            id=maintenance_id, tenant_id=tenant_id
        ).first()

        if maintenance:
            maintenance.mark_completed()

            # Mark resource as active again
            resource = ResourceService.get_resource(str(maintenance.resource_id))
            if resource:
                resource.mark_active()

        return maintenance

    # Resource Utilization Tracking
    @staticmethod
    def track_utilization(
        resource_id: str, usage_hours: Decimal, date: datetime = None
    ) -> ResourceUtilization:
        """Track resource utilization."""
        tenant_id = get_tenant_id()

        if not date:
            date = datetime.utcnow()

        # Calculate utilization percentage
        utilization_percent = (usage_hours / Decimal(24)) * 100

        utilization = ResourceUtilization(
            tenant_id=tenant_id,
            resource_id=resource_id,
            date=date,
            usage_hours=usage_hours,
            utilization_percent=utilization_percent,
        )
        utilization.save()
        return utilization

    @staticmethod
    def get_utilization_stats(
        resource_id: str = None, start_date: datetime = None, end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get resource utilization statistics."""
        tenant_id = get_tenant_id()
        query = ResourceUtilization.objects(tenant_id=tenant_id)

        if resource_id:
            query = query(resource_id=resource_id)
        if start_date:
            query = query(date__gte=start_date)
        if end_date:
            query = query(date__lte=end_date)

        utilizations = query.order_by("-date")

        if not utilizations:
            return {
                "total_records": 0,
                "average_utilization": 0,
                "peak_utilization": 0,
                "min_utilization": 0,
            }

        utilization_percents = [u.utilization_percent for u in utilizations]
        average = sum(utilization_percents) / len(utilization_percents)

        return {
            "total_records": len(utilizations),
            "average_utilization": float(average),
            "peak_utilization": float(max(utilization_percents)),
            "min_utilization": float(min(utilization_percents)),
        }

    @staticmethod
    def get_resource_conflicts(
        resource_id: str, start_date: datetime, end_date: datetime
    ) -> List[ResourceAssignment]:
        """Get resource conflicts (overlapping assignments)."""
        tenant_id = get_tenant_id()
        return ResourceAssignment.objects(
            tenant_id=tenant_id,
            resource_id=resource_id,
            status__in=["assigned", "in_use"],
            assigned_at__gte=start_date,
            assigned_at__lte=end_date,
        )
