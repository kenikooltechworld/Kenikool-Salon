"""Service for managing service-based staff commissions."""

from datetime import datetime
from typing import List, Optional, Tuple
from decimal import Decimal
from bson import ObjectId
from mongoengine import Q
from app.models.service_commission import ServiceCommission
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.staff import Staff


class ServiceCommissionService:
    """Service for service-based commission calculation and management."""

    @staticmethod
    def calculate_commission_for_appointment(
        tenant_id: ObjectId,
        appointment_id: ObjectId,
    ) -> Optional[ServiceCommission]:
        """
        Calculate and record commission for a completed appointment.
        
        Uses Option A (simple): staff payment_rate as commission percentage
        Supports Option B (complex): per-service commission_percentage override

        Args:
            tenant_id: Tenant ID
            appointment_id: Appointment ID

        Returns:
            Created ServiceCommission document or None if appointment/staff/service not found
        """
        appointment = Appointment.objects(
            tenant_id=tenant_id,
            id=appointment_id
        ).first()

        if not appointment or appointment.status != "completed":
            return None

        # Get staff and service details
        staff = Staff.objects(
            tenant_id=tenant_id,
            id=appointment.staff_id
        ).first()

        service = Service.objects(
            tenant_id=tenant_id,
            id=appointment.service_id
        ).first()

        if not staff or not service:
            return None

        # Get service price (use appointment price if captured, otherwise service price)
        service_price = appointment.price or service.price

        # Determine commission percentage
        # Option B: Check if service has override commission_percentage
        if service.commission_percentage is not None:
            commission_percentage = service.commission_percentage
        else:
            # Option A: Use staff payment_rate as commission percentage
            commission_percentage = staff.payment_rate or Decimal("0")

        # Calculate commission amount
        commission_amount = (service_price * commission_percentage) / Decimal("100")

        # Check if commission already exists for this appointment
        existing = ServiceCommission.objects(
            tenant_id=tenant_id,
            appointment_id=appointment_id
        ).first()

        if existing:
            return existing

        # Create commission record
        commission = ServiceCommission(
            tenant_id=tenant_id,
            staff_id=appointment.staff_id,
            appointment_id=appointment_id,
            service_id=appointment.service_id,
            service_price=service_price,
            commission_percentage=commission_percentage,
            commission_amount=commission_amount,
            status="pending",
            earned_date=datetime.utcnow(),
        )
        commission.save()
        return commission

    @staticmethod
    def get_service_commission(
        tenant_id: ObjectId,
        commission_id: ObjectId,
    ) -> Optional[ServiceCommission]:
        """
        Get a service commission record.

        Args:
            tenant_id: Tenant ID
            commission_id: Commission ID

        Returns:
            ServiceCommission document or None if not found
        """
        return ServiceCommission.objects(
            tenant_id=tenant_id,
            id=commission_id
        ).first()

    @staticmethod
    def list_staff_commissions(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ServiceCommission], int]:
        """
        List commissions for a staff member with filtering.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff ID
            status: Filter by status (pending/paid)
            start_date: Filter by earned_date >= start_date
            end_date: Filter by earned_date <= end_date
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (commissions list, total count)
        """
        query = Q(tenant_id=tenant_id) & Q(staff_id=staff_id)

        if status:
            query &= Q(status=status)

        if start_date:
            query &= Q(earned_date__gte=start_date)

        if end_date:
            query &= Q(earned_date__lte=end_date)

        total = ServiceCommission.objects(query).count()

        skip = (page - 1) * page_size
        commissions = ServiceCommission.objects(query).skip(skip).limit(page_size).order_by("-earned_date")

        return list(commissions), total

    @staticmethod
    def get_commission_summary(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """
        Get commission summary for a staff member.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff ID
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Dictionary with commission summary
        """
        query = Q(tenant_id=tenant_id) & Q(staff_id=staff_id)

        if start_date:
            query &= Q(earned_date__gte=start_date)

        if end_date:
            query &= Q(earned_date__lte=end_date)

        commissions = ServiceCommission.objects(query)

        total_earned = Decimal("0")
        total_pending = Decimal("0")
        total_paid = Decimal("0")
        total_services = 0

        for commission in commissions:
            total_earned += commission.commission_amount
            total_services += 1

            if commission.status == "pending":
                total_pending += commission.commission_amount
            elif commission.status == "paid":
                total_paid += commission.commission_amount

        return {
            "total_earned": total_earned,
            "total_pending": total_pending,
            "total_paid": total_paid,
            "total_services": total_services,
            "average_commission": total_earned / total_services if total_services > 0 else Decimal("0"),
        }

    @staticmethod
    def get_commission_by_service(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[dict]:
        """
        Get commission breakdown by service.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff ID
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            List of dictionaries with service commission breakdown
        """
        query = Q(tenant_id=tenant_id) & Q(staff_id=staff_id)

        if start_date:
            query &= Q(earned_date__gte=start_date)

        if end_date:
            query &= Q(earned_date__lte=end_date)

        commissions = ServiceCommission.objects(query)

        # Group by service
        service_breakdown = {}
        for commission in commissions:
            service_id = str(commission.service_id)
            if service_id not in service_breakdown:
                service_breakdown[service_id] = {
                    "service_id": service_id,
                    "total_commission": Decimal("0"),
                    "count": 0,
                    "service_name": None,
                }

            service_breakdown[service_id]["total_commission"] += commission.commission_amount
            service_breakdown[service_id]["count"] += 1

        # Fetch service names
        for service_id_str, data in service_breakdown.items():
            service = Service.objects(
                tenant_id=tenant_id,
                id=ObjectId(service_id_str)
            ).first()
            if service:
                data["service_name"] = service.name

        return list(service_breakdown.values())

    @staticmethod
    def mark_commission_as_paid(
        tenant_id: ObjectId,
        commission_id: ObjectId,
    ) -> Optional[ServiceCommission]:
        """
        Mark a commission as paid.

        Args:
            tenant_id: Tenant ID
            commission_id: Commission ID

        Returns:
            Updated ServiceCommission document or None if not found
        """
        commission = ServiceCommission.objects(
            tenant_id=tenant_id,
            id=commission_id
        ).first()

        if not commission:
            return None

        commission.status = "paid"
        commission.paid_date = datetime.utcnow()
        commission.save()
        return commission

    @staticmethod
    def mark_commissions_as_paid(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        commission_ids: List[ObjectId],
    ) -> int:
        """
        Mark multiple commissions as paid.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff ID
            commission_ids: List of commission IDs

        Returns:
            Number of commissions updated
        """
        result = ServiceCommission.objects(
            tenant_id=tenant_id,
            staff_id=staff_id,
            id__in=commission_ids,
            status="pending"
        ).update(
            status="paid",
            paid_date=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return result

    @staticmethod
    def get_pending_commissions(
        tenant_id: ObjectId,
        staff_id: ObjectId,
    ) -> Tuple[List[ServiceCommission], Decimal]:
        """
        Get all pending commissions for a staff member.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff ID

        Returns:
            Tuple of (pending commissions list, total pending amount)
        """
        commissions = ServiceCommission.objects(
            tenant_id=tenant_id,
            staff_id=staff_id,
            status="pending"
        ).order_by("-earned_date")

        total_pending = sum(
            (c.commission_amount for c in commissions),
            Decimal("0")
        )

        return list(commissions), total_pending
