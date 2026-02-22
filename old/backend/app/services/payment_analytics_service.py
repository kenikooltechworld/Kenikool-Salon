"""
Payment Analytics Service - Payment analytics and reporting
Handles payment trend analysis, method breakdown, gateway performance, and failed payment analysis
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from collections import defaultdict

from app.database import Database
from app.api.exceptions import BadRequestException

logger = logging.getLogger(__name__)


class PaymentAnalyticsService:
    """Service for payment analytics and reporting"""
    
    @staticmethod
    def parse_date_range(
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> tuple:
        """
        Parse and validate date range
        
        Args:
            date_from: Start date (ISO format)
            date_to: End date (ISO format)
            
        Returns:
            Tuple of (start_datetime, end_datetime)
            
        Raises:
            BadRequestException: If date format is invalid
        """
        try:
            if date_from:
                start_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            else:
                start_date = datetime.utcnow() - timedelta(days=30)
            
            if date_to:
                end_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            else:
                end_date = datetime.utcnow()
            
            if start_date > end_date:
                raise BadRequestException("Start date must be before end date")
            
            return start_date, end_date
        
        except ValueError as e:
            raise BadRequestException(f"Invalid date format: {str(e)}")
    
    @staticmethod
    def calculate_revenue_trends(
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        period: str = "daily"
    ) -> List[Dict]:
        """
        Calculate revenue trends over time
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date
            end_date: End date
            period: "daily", "weekly", or "monthly"
            
        Returns:
            List of revenue trend data points
        """
        db = Database.get_db()
        
        # Fetch payments in date range
        payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "status": {"$in": ["completed", "refunded", "partially_refunded"]},
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        # Group by period
        trends = defaultdict(lambda: {"amount": 0, "count": 0})
        
        for payment in payments:
            created_at = payment.get("created_at", datetime.utcnow())
            
            if period == "daily":
                key = created_at.strftime("%Y-%m-%d")
            elif period == "weekly":
                week_start = created_at - timedelta(days=created_at.weekday())
                key = week_start.strftime("%Y-W%U")
            else:  # monthly
                key = created_at.strftime("%Y-%m")
            
            amount = payment.get("amount", 0)
            trends[key]["amount"] += amount
            trends[key]["count"] += 1
        
        # Format result
        result = [
            {
                "period": key,
                "amount": data["amount"],
                "count": data["count"],
                "average": data["amount"] / data["count"] if data["count"] > 0 else 0
            }
            for key, data in sorted(trends.items())
        ]
        
        return result
    
    @staticmethod
    def analyze_payment_methods(
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Analyze payment method breakdown
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of payment method analysis
        """
        db = Database.get_db()
        
        # Fetch payments in date range
        payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "status": {"$in": ["completed", "refunded", "partially_refunded"]},
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        # Group by payment method
        methods = defaultdict(lambda: {"amount": 0, "count": 0})
        total_amount = 0
        
        for payment in payments:
            method = payment.get("payment_method") or payment.get("gateway", "unknown")
            amount = payment.get("amount", 0)
            
            methods[method]["amount"] += amount
            methods[method]["count"] += 1
            total_amount += amount
        
        # Format result with percentages
        result = [
            {
                "method": method,
                "amount": data["amount"],
                "count": data["count"],
                "percentage": (data["amount"] / total_amount * 100) if total_amount > 0 else 0
            }
            for method, data in sorted(methods.items(), key=lambda x: x[1]["amount"], reverse=True)
        ]
        
        return result
    
    @staticmethod
    def analyze_gateway_performance(
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Analyze payment gateway performance
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of gateway performance data
        """
        db = Database.get_db()
        
        # Fetch all payments in date range
        all_payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        # Group by gateway
        gateways = defaultdict(lambda: {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "pending": 0,
            "amount": 0
        })
        
        for payment in all_payments:
            gateway = payment.get("gateway", "unknown")
            status = payment.get("status", "unknown")
            amount = payment.get("amount", 0)
            
            gateways[gateway]["total"] += 1
            gateways[gateway]["amount"] += amount
            
            if status == "completed":
                gateways[gateway]["completed"] += 1
            elif status == "failed":
                gateways[gateway]["failed"] += 1
            elif status == "pending":
                gateways[gateway]["pending"] += 1
        
        # Format result with success rates
        result = [
            {
                "gateway": gateway,
                "total_transactions": data["total"],
                "successful": data["completed"],
                "failed": data["failed"],
                "pending": data["pending"],
                "total_amount": data["amount"],
                "success_rate": (data["completed"] / data["total"] * 100) if data["total"] > 0 else 0,
                "average_amount": data["amount"] / data["total"] if data["total"] > 0 else 0
            }
            for gateway, data in sorted(gateways.items())
        ]
        
        return result
    
    @staticmethod
    def analyze_failed_payments(
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Analyze failed payments
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Dict with failed payment analysis
        """
        db = Database.get_db()
        
        # Fetch failed payments
        failed_payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "status": "failed",
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        # Analyze failure reasons
        failure_reasons = defaultdict(int)
        total_failed_amount = 0
        
        for payment in failed_payments:
            reason = payment.get("metadata", {}).get("failure_reason", "Unknown")
            amount = payment.get("amount", 0)
            
            failure_reasons[reason] += 1
            total_failed_amount += amount
        
        # Format result
        common_reasons = [
            {
                "reason": reason,
                "count": count
            }
            for reason, count in sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return {
            "total_failed": len(failed_payments),
            "total_failed_amount": total_failed_amount,
            "common_failure_reasons": common_reasons[:5]  # Top 5 reasons
        }
    
    @staticmethod
    def get_payment_analytics(
        tenant_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict:
        """
        Get comprehensive payment analytics
        
        Args:
            tenant_id: Tenant ID
            date_from: Start date (ISO format)
            date_to: End date (ISO format)
            
        Returns:
            Dict with complete analytics data
        """
        db = Database.get_db()
        
        # Parse date range
        start_date, end_date = PaymentAnalyticsService.parse_date_range(date_from, date_to)
        
        # Fetch all payments in date range
        payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        # Calculate basic metrics
        completed_payments = [p for p in payments if p.get("status") == "completed"]
        total_revenue = sum(p.get("amount", 0) for p in completed_payments)
        total_transactions = len(completed_payments)
        average_payment = total_revenue / total_transactions if total_transactions > 0 else 0
        
        # Calculate refund metrics
        refunded_payments = [p for p in payments if p.get("status") in ["refunded", "partially_refunded"]]
        total_refunded = sum(p.get("refund_amount", 0) for p in refunded_payments)
        refund_count = len(refunded_payments)
        refund_rate = (refund_count / total_transactions * 100) if total_transactions > 0 else 0
        
        # Calculate status breakdown
        status_breakdown = defaultdict(int)
        for payment in payments:
            status = payment.get("status", "unknown")
            status_breakdown[status] += 1
        
        # Get analytics data
        revenue_trends = PaymentAnalyticsService.calculate_revenue_trends(
            tenant_id, start_date, end_date, "daily"
        )
        
        payment_methods = PaymentAnalyticsService.analyze_payment_methods(
            tenant_id, start_date, end_date
        )
        
        gateway_performance = PaymentAnalyticsService.analyze_gateway_performance(
            tenant_id, start_date, end_date
        )
        
        failed_analysis = PaymentAnalyticsService.analyze_failed_payments(
            tenant_id, start_date, end_date
        )
        
        # Calculate payment type breakdown
        payment_types = defaultdict(lambda: {"amount": 0, "count": 0})
        for payment in completed_payments:
            ptype = payment.get("payment_type", "unknown")
            amount = payment.get("amount", 0)
            payment_types[ptype]["amount"] += amount
            payment_types[ptype]["count"] += 1
        
        payment_type_breakdown = [
            {
                "type": ptype,
                "amount": data["amount"],
                "count": data["count"]
            }
            for ptype, data in payment_types.items()
        ]
        
        return {
            "date_range": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "total_revenue": total_revenue,
            "total_transactions": total_transactions,
            "average_payment": average_payment,
            "revenue_trends": revenue_trends,
            "payment_method_breakdown": payment_methods,
            "gateway_breakdown": gateway_performance,
            "payment_type_breakdown": payment_type_breakdown,
            "status_breakdown": dict(status_breakdown),
            "total_refunded": total_refunded,
            "refund_count": refund_count,
            "refund_rate": refund_rate,
            "failed_payment_count": failed_analysis["total_failed"],
            "failed_payment_amount": failed_analysis["total_failed_amount"],
            "common_failure_reasons": failed_analysis["common_failure_reasons"]
        }


# Singleton instance
payment_analytics_service = PaymentAnalyticsService()
