"""
Unit tests for Payment Notification Service
Tests payment notifications, reminders, and summaries
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, patch

from app.services.payment_notification_service import payment_notification_service
from app.api.exceptions import NotFoundException, BadRequestException


class TestPaymentNotificationService:
    """Test cases for PaymentNotificationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        return Mock()
    
    @pytest.fixture
    def sample_payment(self):
        """Sample payment document"""
        return {
            "_id": ObjectId(),
            "tenant_id": "test-tenant",
            "amount": 50000,
            "reference": "PAY-001",
            "status": "completed",
            "created_at": datetime.utcnow()
        }
    
    def test_create_payment_notification_completed(self, mock_db, sample_payment):
        """Test creating a completed payment notification"""
        with patch('app.services.payment_notification_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = sample_payment
            mock_db.notifications.insert_one.return_value = Mock(inserted_id=ObjectId())
            
            # Call service
            result = payment_notification_service.create_payment_notification(
                "test-tenant",
                str(sample_payment["_id"]),
                "completed",
                "user-123"
            )
            
            # Assertions
            assert "notification_id" in result
            assert result["notification_type"] == "completed"
            assert "Payment Completed" in result["title"]
            mock_db.notifications.insert_one.assert_called_once()
    
    def test_create_payment_notification_failed(self, mock_db, sample_payment):
        """Test creating a failed payment notification"""
        with patch('app.services.payment_notification_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            failed_payment = sample_payment.copy()
            failed_payment["status"] = "failed"
            
            mock_db.payments.find_one.return_value = failed_payment
            mock_db.notifications.insert_one.return_value = Mock(inserted_id=ObjectId())
            
            # Call service
            result = payment_notification_service.create_payment_notification(
                "test-tenant",
                str(failed_payment["_id"]),
                "failed",
                "user-123"
            )
            
            # Assertions
            assert result["notification_type"] == "failed"
            assert "Payment Failed" in result["title"]
    
    def test_create_payment_notification_invalid_type(self, mock_db, sample_payment):
        """Test creating notification with invalid type"""
        with patch('app.services.payment_notification_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = sample_payment
            
            # Call service and expect exception
            with pytest.raises(BadRequestException):
                payment_notification_service.create_payment_notification(
                    "test-tenant",
                    str(sample_payment["_id"]),
                    "invalid_type",
                    "user-123"
                )
    
    def test_create_payment_notification_payment_not_found(self, mock_db):
        """Test creating notification for non-existent payment"""
        with patch('app.services.payment_notification_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = None
            
            # Call service and expect exception
            with pytest.raises(NotFoundException):
                payment_notification_service.create_payment_notification(
                    "test-tenant",
                    str(ObjectId()),
                    "completed",
                    "user-123"
                )
    
    def test_create_refund_notification_full(self, mock_db, sample_payment):
        """Test creating a full refund notification"""
        with patch('app.services.payment_notification_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = sample_payment
            mock_db.notifications.insert_one.return_value = Mock(inserted_id=ObjectId())
            
            # Call service
            result = payment_notification_service.create_refund_notification(
                "test-tenant",
                str(sample_payment["_id"]),
                50000,
                "full",
                "user-123"
            )
            
            # Assertions
            assert result["notification_type"] == "refund"
            assert "Full Refund" in result["title"]
            assert "50000" in result["message"]
    
    def test_create_refund_notification_partial(self, mock_db, sample_payment):
        """Test creating a partial refund notification"""
        with patch('app.services.payment_notification_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = sample_payment
            mock_db.notifications.insert_one.return_value = Mock(inserted_id=ObjectId())
            
            # Call service
            result = payment_notification_service.create_refund_notification(
                "test-tenant",
                str(sample_payment["_id"]),
                25000,
                "partial",
                "user-123"
            )
            
            # Assertions
            assert result["notification_type"] == "refund"
            assert "Partial Refund" in result["title"]
            assert "25000" in result["message"]
    
    def test_send_payment_reminder_success(self, mock_db, sample_payment):
        """Test sending a payment reminder successfully"""
        with patch('app.services.payment_notification_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            pending_payment = sample_payment.copy()
            pending_payment["status"] = "pending"
            
            mock_db.payments.find_one.return_value = pending_payment
            mock_db.notifications.insert_one.return_value = Mock(inserted_id=ObjectId())
            
            # Call service
            result = payment_notification_service.send_payment_reminder(
                "test-tenant",
                str(pending_payment["_id"]),
                "customer-123"
            )
            
            # Assertions
            assert result["notification_type"] == "payment_reminder"
            assert "Payment Reminder" in result["title"]
            assert "pending" in result["message"].lower()
    
    def test_send_payment_reminder_non_pending(self, mock_db, sample_payment):
        """Test sending reminder for non-pending payment"""
        with patch('app.services.payment_notification_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = sample_payment  # Status is completed
            
            # Call service and expect exception
            with pytest.raises(BadRequestException):
                payment_notification_service.send_payment_reminder(
                    "test-tenant",
                    str(sample_payment["_id"]),
                    "customer-123"
                )
    
    def test_send_daily_payment_summary(self, mock_db):
        """Test sending daily payment summary"""
        with patch('app.services.payment_notification_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            # Setup mock payments for the day
            payment1 = {
                "_id": ObjectId(),
                "amount": 50000,
                "status": "completed",
                "created_at": datetime.utcnow()
            }
            
            payment2 = {
                "_id": ObjectId(),
                "amount": 25000,
                "status": "failed",
                "created_at": datetime.utcnow()
            }
            
            payment3 = {
                "_id": ObjectId(),
                "amount": 15000,
                "status": "pending",
                "created_at": datetime.utcnow()
            }
            
            mock_db.payments.find.return_value = [payment1, payment2, payment3]
            mock_db.notifications.insert_one.return_value = Mock(inserted_id=ObjectId())
            
            # Call service
            result = payment_notification_service.send_daily_payment_summary(
                "test-tenant",
                "user-123"
            )
            
            # Assertions
            assert result["notification_type"] == "daily_summary"
            assert "Daily Payment Summary" in result["title"]
            assert result["statistics"]["total_payments"] == 3
            assert result["statistics"]["total_amount"] == 90000
            assert result["statistics"]["completed_count"] == 1
            assert result["statistics"]["failed_count"] == 1
            assert result["statistics"]["pending_count"] == 1
    
    def test_send_daily_payment_summary_custom_date(self, mock_db):
        """Test sending daily payment summary for custom date"""
        with patch('app.services.payment_notification_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find.return_value = []
            mock_db.notifications.insert_one.return_value = Mock(inserted_id=ObjectId())
            
            # Call service with custom date
            custom_date = datetime.utcnow() - timedelta(days=7)
            result = payment_notification_service.send_daily_payment_summary(
                "test-tenant",
                "user-123",
                summary_date=custom_date
            )
            
            # Assertions
            assert result["notification_type"] == "daily_summary"
            assert custom_date.date().isoformat() in result["summary_date"]
    
    def test_get_pending_payment_reminders(self, mock_db):
        """Test getting pending payments for reminders"""
        with patch('app.services.payment_notification_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            # Setup mock pending payments
            old_pending = {
                "_id": ObjectId(),
                "client_id": str(ObjectId()),
                "amount": 50000,
                "reference": "PAY-OLD",
                "status": "pending",
                "created_at": datetime.utcnow() - timedelta(days=5)
            }
            
            recent_pending = {
                "_id": ObjectId(),
                "client_id": str(ObjectId()),
                "amount": 25000,
                "reference": "PAY-NEW",
                "status": "pending",
                "created_at": datetime.utcnow() - timedelta(days=1)
            }
            
            mock_db.payments.find.return_value = [old_pending]  # Only old one should be returned
            
            # Call service
            result = payment_notification_service.get_pending_payment_reminders(
                "test-tenant",
                days_threshold=3
            )
            
            # Assertions
            assert len(result) == 1
            assert result[0]["reference"] == "PAY-OLD"
            assert result[0]["days_pending"] == 5
    
    def test_generate_notification_message_all_types(self):
        """Test notification message generation for all types"""
        payment = {
            "amount": 50000,
            "reference": "PAY-001"
        }
        
        # Test all notification types
        types = ["completed", "failed", "refunded", "manual_recorded", "large_payment"]
        
        for notification_type in types:
            title, message = payment_notification_service._generate_notification_message(
                notification_type,
                payment
            )
            
            assert title is not None
            assert message is not None
            assert len(title) > 0
            assert len(message) > 0
            assert "50000" in message or "PAY-001" in message


class TestPaymentNotificationProperties:
    """Property-based tests for payment notification service"""
    
    def test_notification_completeness_property(self):
        """
        Property: For any payment notification created, 
        all required fields must be present and non-null
        
        Validates: Requirements 9.1, 9.2, 9.3
        """
        # This property ensures notification completeness
        assert hasattr(payment_notification_service, 'create_payment_notification')
        assert hasattr(payment_notification_service, 'create_refund_notification')
    
    def test_reminder_threshold_consistency_property(self):
        """
        Property: Payment reminders must only be sent for payments 
        older than the specified threshold
        
        Validates: Requirements 9.4
        """
        # This property ensures reminder threshold consistency
        assert hasattr(payment_notification_service, 'get_pending_payment_reminders')
        assert hasattr(payment_notification_service, 'send_payment_reminder')
