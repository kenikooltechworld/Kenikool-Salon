"""Financial reporting routes."""

import logging
from fastapi import APIRouter, Query, HTTPException
from app.services.financial_report_service import FinancialReportService
from app.middleware.auth import require_auth
from app.context import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/financial-reports", tags=["financial-reports"])
report_service = FinancialReportService()


@router.get("/revenue")
@require_auth
def get_revenue_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    use_cache: bool = Query(True, description="Use cached results"),
):
    """
    Get revenue report for date range.

    Returns:
        - total_revenue: Total revenue from successful payments
        - total_refunds: Total refunded amount
        - net_revenue: Revenue minus refunds
        - payment_count: Number of successful payments
        - refund_count: Number of successful refunds
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        report = report_service.get_revenue_report(start_date, end_date, use_cache)
        return {
            "success": True,
            "data": report,
            "error": None,
        }
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating revenue report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate revenue report")


@router.get("/payments")
@require_auth
def get_payment_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    use_cache: bool = Query(True, description="Use cached results"),
):
    """
    Get payment report for date range.

    Returns:
        - total_payments: Total number of payment attempts
        - successful_payments: Number of successful payments
        - failed_payments: Number of failed payments
        - pending_payments: Number of pending payments
        - cancelled_payments: Number of cancelled payments
        - success_rate: Percentage of successful payments
        - status_breakdown: Detailed breakdown by status
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        report = report_service.get_payment_report(start_date, end_date, use_cache)
        return {
            "success": True,
            "data": report,
            "error": None,
        }
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating payment report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate payment report")


@router.get("/refunds")
@require_auth
def get_refund_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    use_cache: bool = Query(True, description="Use cached results"),
):
    """
    Get refund report for date range.

    Returns:
        - total_refunds: Total number of refund attempts
        - successful_refunds: Number of successful refunds
        - failed_refunds: Number of failed refunds
        - pending_refunds: Number of pending refunds
        - success_rate: Percentage of successful refunds
        - total_refunded_amount: Total amount refunded
        - status_breakdown: Detailed breakdown by status
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        report = report_service.get_refund_report(start_date, end_date, use_cache)
        return {
            "success": True,
            "data": report,
            "error": None,
        }
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating refund report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate refund report")


@router.get("/outstanding-balance")
@require_auth
def get_outstanding_balance_report(
    use_cache: bool = Query(True, description="Use cached results"),
):
    """
    Get outstanding balance report for all customers.

    Returns:
        - total_outstanding: Total outstanding balance across all customers
        - customers_with_balance: Number of customers with outstanding balance
        - customers: List of customers with outstanding balance details
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        report = report_service.get_outstanding_balance_report(use_cache)
        return {
            "success": True,
            "data": report,
            "error": None,
        }
    except Exception as e:
        logger.error(f"Error generating outstanding balance report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate outstanding balance report")


@router.get("/comprehensive")
@require_auth
def get_comprehensive_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    use_cache: bool = Query(True, description="Use cached results"),
):
    """
    Get comprehensive financial report combining all metrics.

    Returns:
        - revenue: Revenue report
        - payments: Payment report
        - refunds: Refund report
        - outstanding_balance: Outstanding balance report
    """
    try:
        tenant_id = get_tenant_id()
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Tenant context not found")

        report = report_service.get_comprehensive_report(start_date, end_date, use_cache)
        return {
            "success": True,
            "data": report,
            "error": None,
        }
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating comprehensive report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate comprehensive report")
