"""Balance service for managing customer outstanding balances."""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from bson import ObjectId
from app.models.customer import Customer
from app.models.invoice import Invoice

logger = logging.getLogger(__name__)


class BalanceService:
    """Service for managing customer outstanding balances."""

    @staticmethod
    def calculate_customer_balance(tenant_id: ObjectId, customer_id: str) -> Decimal:
        """
        Calculate outstanding balance for a customer.

        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID

        Returns:
            Outstanding balance amount

        Raises:
            ValueError: If customer not found
        """
        
        # Get customer
        customer = Customer.objects(
            tenant_id=tenant_id,
            id=ObjectId(customer_id)
        ).first()

        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Get all unpaid invoices for customer
        unpaid_invoices = Invoice.objects(
            tenant_id=tenant_id,
            customer_id=ObjectId(customer_id),
            status__in=["issued", "overdue"],
        )

        # Calculate total outstanding
        total_outstanding = Decimal("0")
        for invoice in unpaid_invoices:
            total_outstanding += invoice.total

        return total_outstanding

    @staticmethod
    def update_customer_balance(tenant_id: ObjectId, customer_id: str) -> Decimal:
        """
        Update customer's outstanding balance in database.

        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID

        Returns:
            Updated outstanding balance

        Raises:
            ValueError: If customer not found
        """
        
        # Calculate current balance
        balance = BalanceService.calculate_customer_balance(tenant_id, customer_id)

        # Update customer record
        customer = Customer.objects(
            tenant_id=tenant_id,
            id=ObjectId(customer_id)
        ).first()

        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        customer.outstanding_balance = balance
        customer.save()

        logger.info(f"Customer {customer_id} balance updated to {balance}")

        return balance

    @staticmethod
    def check_booking_eligibility(tenant_id: ObjectId, customer_id: str) -> Dict[str, Any]:
        """
        Check if customer is eligible to book (no outstanding balance).

        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID

        Returns:
            Dictionary with eligibility status and balance info

        Raises:
            ValueError: If customer not found
        """
        
        # Get customer
        customer = Customer.objects(
            tenant_id=tenant_id,
            id=ObjectId(customer_id)
        ).first()

        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Calculate current balance
        balance = BalanceService.calculate_customer_balance(tenant_id, customer_id)

        # Check eligibility
        is_eligible = balance == 0

        return {
            "customer_id": str(customer.id),
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "outstanding_balance": float(balance),
            "is_eligible_to_book": is_eligible,
            "reason": "No outstanding balance" if is_eligible else f"Outstanding balance of {balance} must be paid before booking",
        }

    @staticmethod
    def get_customer_balance(tenant_id: ObjectId, customer_id: str) -> Dict[str, Any]:
        """
        Get customer's current outstanding balance.

        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID

        Returns:
            Dictionary with balance information

        Raises:
            ValueError: If customer not found
        """
        
        # Get customer
        customer = Customer.objects(
            tenant_id=tenant_id,
            id=ObjectId(customer_id)
        ).first()

        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Calculate current balance
        balance = BalanceService.calculate_customer_balance(tenant_id, customer_id)

        # Get unpaid invoices
        unpaid_invoices = Invoice.objects(
            tenant_id=tenant_id,
            customer_id=ObjectId(customer_id),
            status__in=["issued", "overdue"],
        )

        invoices_list = []
        for invoice in unpaid_invoices:
            invoices_list.append({
                "invoice_id": str(invoice.id),
                "amount": float(invoice.total),
                "status": invoice.status,
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "created_at": invoice.created_at.isoformat(),
            })

        return {
            "customer_id": str(customer.id),
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "outstanding_balance": float(balance),
            "unpaid_invoice_count": len(invoices_list),
            "unpaid_invoices": invoices_list,
        }
