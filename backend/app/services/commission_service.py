"""Service for managing staff commissions in POS system."""

from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from bson import ObjectId
from mongoengine import Q
from app.models.staff_commission import StaffCommission
from app.models.transaction import Transaction


class CommissionService:
    """Service for commission calculation and management."""

    @staticmethod
    def calculate_commission(
        tenant_id: ObjectId,
        transaction_id: ObjectId,
        staff_id: ObjectId,
        commission_rate: Decimal = Decimal("0"),
        commission_type: str = "percentage",
    ) -> Optional[StaffCommission]:
        """
        Calculate and record commission for a transaction.

        Args:
            tenant_id: Tenant ID
            transaction_id: Transaction ID
            staff_id: Staff ID
            commission_rate: Commission rate (percentage or fixed amount)
            commission_type: Commission type (percentage, fixed, tiered)

        Returns:
            Created StaffCommission document or None if transaction not found
        """
        transaction = Transaction.objects(
            tenant_id=tenant_id,
            id=transaction_id
        ).first()

        if not transaction:
            return None

        # Calculate commission amount
        if commission_type == "percentage":
            commission_amount = (transaction.total * commission_rate) / Decimal("100")
        elif commission_type == "fixed":
            commission_amount = commission_rate
        else:
            # For tiered, use fixed amount
            commission_amount = commission_rate

        # Create commission record
        commission = StaffCommission(
            tenant_id=tenant_id,
            staff_id=staff_id,
            transaction_id=transaction_id,
            commission_amount=commission_amount,
            commission_rate=commission_rate,
            commission_type=commission_type,
            calculated_at=datetime.utcnow(),
        )
        commission.save()
        return commission

    @staticmethod
    def get_staff_commission(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        commission_id: ObjectId,
    ) -> Optional[StaffCommission]:
        """
        Get a staff commission record.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff ID
            commission_id: Commission ID

        Returns:
            StaffCommission document or None if not found
        """
        return StaffCommission.objects(
            tenant_id=tenant_id,
            staff_id=staff_id,
            id=commission_id
        ).first()

    @staticmethod
    def list_staff_commissions(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[StaffCommission], int]:
        """
        List commissions for a staff member.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff ID
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (commissions list, total count)
        """
        query = Q(tenant_id=tenant_id) & Q(staff_id=staff_id)

        total = StaffCommission.objects(query).count()

        skip = (page - 1) * page_size
        commissions = StaffCommission.objects(query).skip(skip).limit(page_size).order_by("-calculated_at")

        return list(commissions), total

    @staticmethod
    def calculate_total_commission(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Decimal:
        """
        Calculate total commission for a staff member in a period.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff ID
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Total commission amount
        """
        query = Q(tenant_id=tenant_id) & Q(staff_id=staff_id)

        if start_date:
            query &= Q(calculated_at__gte=start_date)

        if end_date:
            query &= Q(calculated_at__lte=end_date)

        commissions = StaffCommission.objects(query)

        total_commission = Decimal("0")
        for commission in commissions:
            total_commission += commission.commission_amount

        return total_commission

    @staticmethod
    def get_commission_structure(
        tenant_id: ObjectId,
        staff_id: ObjectId,
    ) -> dict:
        """
        Get commission structure for a staff member.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff ID

        Returns:
            Dictionary with commission structure details
        """
        from app.models.staff import Staff

        staff = Staff.objects(
            tenant_id=tenant_id,
            id=staff_id
        ).first()

        if not staff:
            return {
                "commission_type": "percentage",
                "commission_rate": Decimal("0"),
            }

        # Return staff commission details if available
        return {
            "commission_type": getattr(staff, "commission_type", "percentage"),
            "commission_rate": getattr(staff, "commission_rate", Decimal("0")),
        }

    @staticmethod
    def calculate_payout(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        period: str = "monthly",
    ) -> Decimal:
        """
        Calculate commission payout for a staff member.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff ID
            period: Period (daily, weekly, monthly)

        Returns:
            Total payout amount
        """
        from datetime import timedelta

        now = datetime.utcnow()

        if period == "daily":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
        elif period == "weekly":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
        else:  # monthly
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end_date = start_date.replace(year=now.year + 1, month=1)
            else:
                end_date = start_date.replace(month=now.month + 1)

        return CommissionService.calculate_total_commission(
            tenant_id, staff_id, start_date, end_date
        )

    @staticmethod
    def process_commission_payout(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        payout_amount: Decimal,
    ) -> dict:
        """
        Process commission payout for a staff member.

        Args:
            tenant_id: Tenant ID
            staff_id: Staff ID
            payout_amount: Payout amount

        Returns:
            Dictionary with payout details
        """
        return {
            "tenant_id": str(tenant_id),
            "staff_id": str(staff_id),
            "payout_amount": payout_amount,
            "payout_date": datetime.utcnow(),
            "status": "completed",
        }
