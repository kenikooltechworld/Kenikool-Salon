"""
Unit tests for Payment Analytics Service
Tests payment analytics calculations and reporting
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock

from app.services.payment_analytics_service import PaymentAnalyticsService
from app.api.exceptions import BadRequestException


class TestDateRangeParsing:
    """Tests for date range parsing"""
    
    def test_parse_date_range_success(self):
        """Test successful date range parsing"""
        # Setup
        date_from = "2024-01-01T00:00:00Z"
        date_to = "2024-01-31T23:59:59Z"
        
        # Execute
        start_date, end_date = PaymentAnalyticsService.parse_date_range(date_from, date_to)
        
        # Assert
        assert start_date is not None
        assert end_date is not None
        assert start_date < end_date
    
    def test_parse_date_range_defaults(self):
        """Test date range parsing with defaults"""
        # Execute
        start_date, end_date = PaymentAnalyticsService.parse_date_range()
        
        # Assert
        assert start_date is not None
        assert end_date is not None
        assert start_date < end_date
        # Should default to last 30 days
        assert (end_date - start_date).days >= 29
    
    def test_parse_date_range_invalid_format(self):
        """Test date range parsing with invalid format"""
        # Setup
        date_from = "invalid-date"
        
        # Execute & Assert
        with pytest.raises(BadRequestException):
            PaymentAnalyticsService.parse_date_range(date_from)
    
    def test_parse_date_range_start_after_end(self):
        """Test date range parsing with start date after end date"""
        # Setup
        date_from = "2024-01-31T00:00:00Z"
        date_to = "2024-01-01T00:00:00Z"
        
        # Execute & Assert
        with pytest.raises(BadRequestException):
            PaymentAnalyticsService.parse_date_range(date_from, date_to)


class TestRevenueTrends:
    """Tests for revenue trend calculation"""
    
    @patch('app.services.payment_analytics_service.Database')
    def test_calculate_revenue_trends_daily(self, mock_db):
        """Test daily revenue trend calculation"""
        # Setup
        tenant_id = "test_tenant"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 3)
        
        mock_payments = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 50000.0,
                "status": "completed",
                "created_at": datetime(2024, 1, 1, 10, 0, 0)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 30000.0,
                "status": "completed",
                "created_at": datetime(2024, 1, 1, 14, 0, 0)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 40000.0,
                "status": "completed",
                "created_at": datetime(2024, 1, 2, 10, 0, 0)
            }
        ]
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find.return_value = mock_payments
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentAnalyticsService.calculate_revenue_trends(
            tenant_id, start_date, end_date, "daily"
        )
        
        # Assert
        assert len(result) == 2  # 2 days with payments
        assert result[0]["amount"] == 80000.0  # Jan 1
        assert result[0]["count"] == 2
        assert result[1]["amount"] == 40000.0  # Jan 2
        assert result[1]["count"] == 1
    
    @patch('app.services.payment_analytics_service.Database')
    def test_calculate_revenue_trends_no_payments(self, mock_db):
        """Test revenue trend calculation with no payments"""
        # Setup
        tenant_id = "test_tenant"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 3)
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find.return_value = []
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentAnalyticsService.calculate_revenue_trends(
            tenant_id, start_date, end_date, "daily"
        )
        
        # Assert
        assert len(result) == 0


class TestPaymentMethodAnalysis:
    """Tests for payment method analysis"""
    
    @patch('app.services.payment_analytics_service.Database')
    def test_analyze_payment_methods_success(self, mock_db):
        """Test successful payment method analysis"""
        # Setup
        tenant_id = "test_tenant"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        mock_payments = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 50000.0,
                "status": "completed",
                "payment_method": "card",
                "created_at": datetime(2024, 1, 1)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 30000.0,
                "status": "completed",
                "payment_method": "card",
                "created_at": datetime(2024, 1, 2)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 20000.0,
                "status": "completed",
                "payment_method": "cash",
                "created_at": datetime(2024, 1, 3)
            }
        ]
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find.return_value = mock_payments
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentAnalyticsService.analyze_payment_methods(
            tenant_id, start_date, end_date
        )
        
        # Assert
        assert len(result) == 2
        # Card should be first (higher amount)
        assert result[0]["method"] == "card"
        assert result[0]["amount"] == 80000.0
        assert result[0]["count"] == 2
        assert result[0]["percentage"] == pytest.approx(80.0)
        
        assert result[1]["method"] == "cash"
        assert result[1]["amount"] == 20000.0
        assert result[1]["percentage"] == pytest.approx(20.0)


class TestGatewayPerformance:
    """Tests for gateway performance analysis"""
    
    @patch('app.services.payment_analytics_service.Database')
    def test_analyze_gateway_performance_success(self, mock_db):
        """Test successful gateway performance analysis"""
        # Setup
        tenant_id = "test_tenant"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        mock_payments = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 50000.0,
                "status": "completed",
                "gateway": "paystack",
                "created_at": datetime(2024, 1, 1)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 30000.0,
                "status": "completed",
                "gateway": "paystack",
                "created_at": datetime(2024, 1, 2)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 20000.0,
                "status": "failed",
                "gateway": "paystack",
                "created_at": datetime(2024, 1, 3)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 40000.0,
                "status": "completed",
                "gateway": "flutterwave",
                "created_at": datetime(2024, 1, 4)
            }
        ]
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find.return_value = mock_payments
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentAnalyticsService.analyze_gateway_performance(
            tenant_id, start_date, end_date
        )
        
        # Assert
        assert len(result) == 2
        
        # Find paystack result
        paystack = next(r for r in result if r["gateway"] == "paystack")
        assert paystack["total_transactions"] == 3
        assert paystack["successful"] == 2
        assert paystack["failed"] == 1
        assert paystack["success_rate"] == pytest.approx(66.67, rel=0.01)
        
        # Find flutterwave result
        flutterwave = next(r for r in result if r["gateway"] == "flutterwave")
        assert flutterwave["total_transactions"] == 1
        assert flutterwave["successful"] == 1
        assert flutterwave["success_rate"] == 100.0


class TestFailedPaymentAnalysis:
    """Tests for failed payment analysis"""
    
    @patch('app.services.payment_analytics_service.Database')
    def test_analyze_failed_payments_success(self, mock_db):
        """Test successful failed payment analysis"""
        # Setup
        tenant_id = "test_tenant"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        mock_payments = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 50000.0,
                "status": "failed",
                "metadata": {"failure_reason": "Insufficient funds"},
                "created_at": datetime(2024, 1, 1)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 30000.0,
                "status": "failed",
                "metadata": {"failure_reason": "Insufficient funds"},
                "created_at": datetime(2024, 1, 2)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 20000.0,
                "status": "failed",
                "metadata": {"failure_reason": "Invalid card"},
                "created_at": datetime(2024, 1, 3)
            }
        ]
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find.return_value = mock_payments
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentAnalyticsService.analyze_failed_payments(
            tenant_id, start_date, end_date
        )
        
        # Assert
        assert result["total_failed"] == 3
        assert result["total_failed_amount"] == 100000.0
        assert len(result["common_failure_reasons"]) == 2
        assert result["common_failure_reasons"][0]["reason"] == "Insufficient funds"
        assert result["common_failure_reasons"][0]["count"] == 2


class TestComprehensiveAnalytics:
    """Tests for comprehensive analytics"""
    
    @patch('app.services.payment_analytics_service.Database')
    def test_get_payment_analytics_success(self, mock_db):
        """Test successful comprehensive analytics retrieval"""
        # Setup
        tenant_id = "test_tenant"
        
        mock_payments = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 50000.0,
                "status": "completed",
                "payment_method": "card",
                "gateway": "paystack",
                "payment_type": "full",
                "created_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 30000.0,
                "status": "completed",
                "payment_method": "cash",
                "gateway": "manual",
                "payment_type": "full",
                "created_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "amount": 20000.0,
                "status": "refunded",
                "refund_amount": 20000.0,
                "payment_method": "card",
                "gateway": "paystack",
                "payment_type": "full",
                "created_at": datetime.utcnow()
            }
        ]
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find.return_value = mock_payments
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentAnalyticsService.get_payment_analytics(tenant_id)
        
        # Assert
        assert result["total_revenue"] == 80000.0  # Only completed payments
        assert result["total_transactions"] == 2
        assert result["average_payment"] == 40000.0
        assert result["total_refunded"] == 20000.0
        assert result["refund_count"] == 1
        assert result["refund_rate"] == pytest.approx(50.0)
        assert "revenue_trends" in result
        assert "payment_method_breakdown" in result
        assert "gateway_breakdown" in result
        assert "status_breakdown" in result
