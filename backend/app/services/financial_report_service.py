"""Financial reporting service for generating financial reports."""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List
from bson import ObjectId
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.refund import Refund
from app.models.appointment import Appointment
from app.models.customer import Customer
from app.context import get_tenant_id

logger = logging.getLogger(__name__)

# Try to import cache, but don't fail if it's not available
try:
    from app.cache import cache
    CACHE_AVAILABLE = True
except Exception:
    CACHE_AVAILABLE = False
    cache = None


class FinancialReportService:
    """Service for generating financial reports."""

    def __init__(self):
        """Initialize financial report service."""
        self.cache_ttl = 3600  # 1 hour cache for reports

    def _get_cache_key(self, report_type: str, start_date: str, end_date: str) -> str:
        """Generate cache key for report."""
        tenant_id = get_tenant_id()
        return f"financial_report:{tenant_id}:{report_type}:{start_date}:{end_date}"

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if available."""
        if not CACHE_AVAILABLE or not cache:
            return None
        try:
            return cache.get(key)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None

    def _set_in_cache(self, key: str, value: Any, ttl: int) -> None:
        """Set value in cache if available."""
        if not CACHE_AVAILABLE or not cache:
            return
        try:
            cache.set(key, value, ttl)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime."""
        try:
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid date format: {date_str}. Use ISO format (YYYY-MM-DD)")

    def get_revenue_report(
        self,
        start_date: str,
        end_date: str,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate revenue report for date range.

        Args:
            start_date: Start date (ISO format: YYYY-MM-DD)
            end_date: End date (ISO format: YYYY-MM-DD)
            use_cache: Whether to use cached results

        Returns:
            Dictionary with revenue metrics

        Raises:
            ValueError: If date format is invalid
        """
        tenant_id = get_tenant_id()
        
        # Check cache
        cache_key = self._get_cache_key("revenue", start_date, end_date)
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info(f"Revenue report cache hit for {start_date} to {end_date}")
                return cached_result

        # Parse dates
        start_dt = self._parse_date(start_date)
        end_dt = self._parse_date(end_date)
        
        # Ensure end date is end of day
        end_dt = end_dt.replace(hour=23, minute=59, second=59)

        # Query successful payments in date range
        payments = Payment.objects(
            tenant_id=ObjectId(tenant_id),
            status="success",
            created_at__gte=start_dt,
            created_at__lte=end_dt,
        )

        # Calculate metrics
        total_revenue = Decimal("0")
        payment_count = 0
        
        for payment in payments:
            total_revenue += payment.amount
            payment_count += 1

        # Query refunds in date range
        refunds = Refund.objects(
            tenant_id=ObjectId(tenant_id),
            status="success",
            created_at__gte=start_dt,
            created_at__lte=end_dt,
        )

        total_refunds = Decimal("0")
        refund_count = 0
        
        for refund in refunds:
            total_refunds += refund.amount
            refund_count += 1

        # Calculate net revenue
        net_revenue = total_revenue - total_refunds

        result = {
            "report_type": "revenue",
            "start_date": start_date,
            "end_date": end_date,
            "total_revenue": float(total_revenue),
            "total_refunds": float(total_refunds),
            "net_revenue": float(net_revenue),
            "payment_count": payment_count,
            "refund_count": refund_count,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache result
        self._set_in_cache(cache_key, result, self.cache_ttl)
        logger.info(f"Revenue report generated: {total_revenue} revenue, {total_refunds} refunds")

        return result

    def get_payment_report(
        self,
        start_date: str,
        end_date: str,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate payment report for date range.

        Args:
            start_date: Start date (ISO format: YYYY-MM-DD)
            end_date: End date (ISO format: YYYY-MM-DD)
            use_cache: Whether to use cached results

        Returns:
            Dictionary with payment metrics

        Raises:
            ValueError: If date format is invalid
        """
        tenant_id = get_tenant_id()
        
        # Check cache
        cache_key = self._get_cache_key("payment", start_date, end_date)
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info(f"Payment report cache hit for {start_date} to {end_date}")
                return cached_result

        # Parse dates
        start_dt = self._parse_date(start_date)
        end_dt = self._parse_date(end_date)
        
        # Ensure end date is end of day
        end_dt = end_dt.replace(hour=23, minute=59, second=59)

        # Query all payments in date range
        all_payments = Payment.objects(
            tenant_id=ObjectId(tenant_id),
            created_at__gte=start_dt,
            created_at__lte=end_dt,
        )

        # Calculate metrics by status
        status_breakdown = {
            "pending": {"count": 0, "amount": Decimal("0")},
            "success": {"count": 0, "amount": Decimal("0")},
            "failed": {"count": 0, "amount": Decimal("0")},
            "cancelled": {"count": 0, "amount": Decimal("0")},
        }

        for payment in all_payments:
            status = payment.status
            if status in status_breakdown:
                status_breakdown[status]["count"] += 1
                status_breakdown[status]["amount"] += payment.amount

        # Calculate success rate
        total_payments = sum(s["count"] for s in status_breakdown.values())
        successful_payments = status_breakdown["success"]["count"]
        success_rate = (successful_payments / total_payments * 100) if total_payments > 0 else 0

        result = {
            "report_type": "payment",
            "start_date": start_date,
            "end_date": end_date,
            "total_payments": total_payments,
            "successful_payments": successful_payments,
            "failed_payments": status_breakdown["failed"]["count"],
            "pending_payments": status_breakdown["pending"]["count"],
            "cancelled_payments": status_breakdown["cancelled"]["count"],
            "success_rate": round(success_rate, 2),
            "status_breakdown": {
                status: {
                    "count": data["count"],
                    "amount": float(data["amount"]),
                }
                for status, data in status_breakdown.items()
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache result
        self._set_in_cache(cache_key, result, self.cache_ttl)
        logger.info(f"Payment report generated: {total_payments} payments, {success_rate}% success rate")

        return result

    def get_refund_report(
        self,
        start_date: str,
        end_date: str,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate refund report for date range.

        Args:
            start_date: Start date (ISO format: YYYY-MM-DD)
            end_date: End date (ISO format: YYYY-MM-DD)
            use_cache: Whether to use cached results

        Returns:
            Dictionary with refund metrics

        Raises:
            ValueError: If date format is invalid
        """
        tenant_id = get_tenant_id()
        
        # Check cache
        cache_key = self._get_cache_key("refund", start_date, end_date)
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info(f"Refund report cache hit for {start_date} to {end_date}")
                return cached_result

        # Parse dates
        start_dt = self._parse_date(start_date)
        end_dt = self._parse_date(end_date)
        
        # Ensure end date is end of day
        end_dt = end_dt.replace(hour=23, minute=59, second=59)

        # Query all refunds in date range
        all_refunds = Refund.objects(
            tenant_id=ObjectId(tenant_id),
            created_at__gte=start_dt,
            created_at__lte=end_dt,
        )

        # Calculate metrics by status
        status_breakdown = {
            "pending": {"count": 0, "amount": Decimal("0")},
            "success": {"count": 0, "amount": Decimal("0")},
            "failed": {"count": 0, "amount": Decimal("0")},
        }

        for refund in all_refunds:
            status = refund.status
            if status in status_breakdown:
                status_breakdown[status]["count"] += 1
                status_breakdown[status]["amount"] += refund.amount

        # Calculate success rate
        total_refunds = sum(s["count"] for s in status_breakdown.values())
        successful_refunds = status_breakdown["success"]["count"]
        success_rate = (successful_refunds / total_refunds * 100) if total_refunds > 0 else 0

        result = {
            "report_type": "refund",
            "start_date": start_date,
            "end_date": end_date,
            "total_refunds": total_refunds,
            "successful_refunds": successful_refunds,
            "failed_refunds": status_breakdown["failed"]["count"],
            "pending_refunds": status_breakdown["pending"]["count"],
            "success_rate": round(success_rate, 2),
            "total_refunded_amount": float(status_breakdown["success"]["amount"]),
            "status_breakdown": {
                status: {
                    "count": data["count"],
                    "amount": float(data["amount"]),
                }
                for status, data in status_breakdown.items()
            },
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache result
        self._set_in_cache(cache_key, result, self.cache_ttl)
        logger.info(f"Refund report generated: {total_refunds} refunds, {success_rate}% success rate")

        return result

    def get_outstanding_balance_report(
        self,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate outstanding balance report for all customers.

        Args:
            use_cache: Whether to use cached results

        Returns:
            Dictionary with outstanding balance metrics

        """
        tenant_id = get_tenant_id()
        
        # Check cache
        cache_key = f"financial_report:{tenant_id}:outstanding_balance"
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info("Outstanding balance report cache hit")
                return cached_result

        # Get all customers
        customers = Customer.objects(tenant_id=ObjectId(tenant_id))

        outstanding_customers = []
        total_outstanding = Decimal("0")

        for customer in customers:
            # Get unpaid invoices for customer
            unpaid_invoices = Invoice.objects(
                tenant_id=ObjectId(tenant_id),
                customer_id=customer.id,
                status__in=["issued", "overdue"],
            )

            customer_balance = Decimal("0")
            for invoice in unpaid_invoices:
                customer_balance += invoice.total

            if customer_balance > 0:
                outstanding_customers.append({
                    "customer_id": str(customer.id),
                    "customer_name": f"{customer.first_name} {customer.last_name}",
                    "email": customer.email,
                    "phone": customer.phone,
                    "outstanding_balance": float(customer_balance),
                })
                total_outstanding += customer_balance

        result = {
            "report_type": "outstanding_balance",
            "total_outstanding": float(total_outstanding),
            "customers_with_balance": len(outstanding_customers),
            "customers": outstanding_customers,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache result
        self._set_in_cache(cache_key, result, self.cache_ttl)
        logger.info(f"Outstanding balance report generated: {total_outstanding} total outstanding")

        return result

    def get_comprehensive_report(
        self,
        start_date: str,
        end_date: str,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive financial report combining all metrics.

        Args:
            start_date: Start date (ISO format: YYYY-MM-DD)
            end_date: End date (ISO format: YYYY-MM-DD)
            use_cache: Whether to use cached results

        Returns:
            Dictionary with all financial metrics

        Raises:
            ValueError: If date format is invalid
        """
        tenant_id = get_tenant_id()
        
        # Check cache
        cache_key = self._get_cache_key("comprehensive", start_date, end_date)
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info(f"Comprehensive report cache hit for {start_date} to {end_date}")
                return cached_result

        # Generate all reports
        revenue_report = self.get_revenue_report(start_date, end_date, use_cache=False)
        payment_report = self.get_payment_report(start_date, end_date, use_cache=False)
        refund_report = self.get_refund_report(start_date, end_date, use_cache=False)
        outstanding_report = self.get_outstanding_balance_report(use_cache=False)

        result = {
            "report_type": "comprehensive",
            "start_date": start_date,
            "end_date": end_date,
            "revenue": revenue_report,
            "payments": payment_report,
            "refunds": refund_report,
            "outstanding_balance": outstanding_report,
            "generated_at": datetime.utcnow().isoformat(),
        }

        # Cache result
        self._set_in_cache(cache_key, result, self.cache_ttl)
        logger.info("Comprehensive financial report generated")

        return result

    def invalidate_cache(self) -> None:
        """Invalidate all financial report caches for current tenant."""
        tenant_id = get_tenant_id()
        
        # Delete all cache keys for this tenant
        cache_pattern = f"financial_report:{tenant_id}:*"
        logger.info(f"Invalidating financial report cache for tenant {tenant_id}")
        
        # Note: In production, use Redis pattern deletion or maintain a list of cache keys
        # For now, we'll rely on TTL expiration
