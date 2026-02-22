"""
Unit tests for Fraud Detection Service
Tests rate monitoring, velocity checks, pattern detection, and card flagging
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId

from app.services.fraud_detection_service import FraudDetectionService
from app.api.exceptions import BadRequestException


class TestFraudDetectionRateMonitoring:
    """Test rate monitoring functionality"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_balance_check_rate_normal(self, mock_get_db):
        """Test normal balance check rate"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock Redis for rate limiting
        with patch('app.services.fraud_detection_service.redis_client') as mock_redis:
            mock_redis.get.return_value = None  # No previous checks
            
            result = FraudDetectionService.check_balance_check_rate(
                ip_address="192.168.1.1",
                card_number="GC-TEST123"
            )
            
            assert result is True  # Not suspicious

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_balance_check_rate_excessive(self, mock_get_db):
        """Test excessive balance check rate"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        with patch('app.services.fraud_detection_service.redis_client') as mock_redis:
            # Simulate 15 checks in 1 minute (limit is 10)
            mock_redis.get.return_value = b"15"
            
            result = FraudDetectionService.check_balance_check_rate(
                ip_address="192.168.1.1",
                card_number="GC-TEST123"
            )
            
            assert result is False  # Suspicious

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_balance_check_rate_at_limit(self, mock_get_db):
        """Test balance check rate at limit"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        with patch('app.services.fraud_detection_service.redis_client') as mock_redis:
            # Exactly at limit
            mock_redis.get.return_value = b"10"
            
            result = FraudDetectionService.check_balance_check_rate(
                ip_address="192.168.1.1",
                card_number="GC-TEST123"
            )
            
            assert result is True  # Not suspicious yet

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_balance_check_rate_multiple_ips(self, mock_get_db):
        """Test rate checking for different IPs"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        with patch('app.services.fraud_detection_service.redis_client') as mock_redis:
            mock_redis.get.side_effect = [None, None, None]
            
            result1 = FraudDetectionService.check_balance_check_rate(
                ip_address="192.168.1.1",
                card_number="GC-TEST123"
            )
            result2 = FraudDetectionService.check_balance_check_rate(
                ip_address="192.168.1.2",
                card_number="GC-TEST123"
            )
            result3 = FraudDetectionService.check_balance_check_rate(
                ip_address="192.168.1.3",
                card_number="GC-TEST123"
            )
            
            assert result1 is True
            assert result2 is True
            assert result3 is True


class TestFraudDetectionVelocityChecks:
    """Test velocity check functionality"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_redemption_velocity_normal(self, mock_get_db):
        """Test normal redemption velocity"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "transactions": [
                {
                    "type": "redeem",
                    "amount": 5000,
                    "timestamp": datetime.now(timezone.utc) - timedelta(hours=2)
                }
            ]
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = FraudDetectionService.check_redemption_velocity(
            card_number="GC-TEST123"
        )
        
        assert result is True  # Not suspicious

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_redemption_velocity_excessive(self, mock_get_db):
        """Test excessive redemption velocity"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        now = datetime.now(timezone.utc)
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "transactions": [
                {"type": "redeem", "amount": 5000, "timestamp": now},
                {"type": "redeem", "amount": 5000, "timestamp": now - timedelta(minutes=5)},
                {"type": "redeem", "amount": 5000, "timestamp": now - timedelta(minutes=10)},
                {"type": "redeem", "amount": 5000, "timestamp": now - timedelta(minutes=15)}
            ]
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = FraudDetectionService.check_redemption_velocity(
            card_number="GC-TEST123"
        )
        
        assert result is False  # Suspicious

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_redemption_velocity_daily_limit(self, mock_get_db):
        """Test daily redemption limit (max 3 per day)"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        now = datetime.now(timezone.utc)
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "transactions": [
                {"type": "redeem", "amount": 5000, "timestamp": now},
                {"type": "redeem", "amount": 5000, "timestamp": now - timedelta(hours=1)},
                {"type": "redeem", "amount": 5000, "timestamp": now - timedelta(hours=2)},
                {"type": "redeem", "amount": 5000, "timestamp": now - timedelta(hours=3)}
            ]
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = FraudDetectionService.check_redemption_velocity(
            card_number="GC-TEST123"
        )
        
        assert result is False  # Exceeded daily limit


class TestFraudDetectionPatternDetection:
    """Test pattern detection functionality"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_unusual_pattern_high_value(self, mock_get_db):
        """Test detection of unusual high-value redemption"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "amount": 50000,
            "balance": 50000,
            "transactions": []
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        # Try to redeem full amount immediately
        result = FraudDetectionService.check_unusual_pattern(
            card_number="GC-TEST123",
            amount=50000,
            location="Unknown Location"
        )
        
        assert result is False  # Suspicious

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_unusual_pattern_multiple_locations(self, mock_get_db):
        """Test detection of multiple locations in short time"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        now = datetime.now(timezone.utc)
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "amount": 50000,
            "balance": 40000,
            "transactions": [
                {"type": "redeem", "amount": 5000, "timestamp": now, "location": "Location A"},
                {"type": "redeem", "amount": 5000, "timestamp": now - timedelta(minutes=5), "location": "Location B"}
            ]
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = FraudDetectionService.check_unusual_pattern(
            card_number="GC-TEST123",
            amount=5000,
            location="Location C"
        )
        
        assert result is False  # Suspicious - multiple locations

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_unusual_pattern_normal(self, mock_get_db):
        """Test normal usage pattern"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "amount": 50000,
            "balance": 40000,
            "transactions": [
                {"type": "redeem", "amount": 5000, "timestamp": datetime.now(timezone.utc) - timedelta(days=1), "location": "Salon A"}
            ]
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = FraudDetectionService.check_unusual_pattern(
            card_number="GC-TEST123",
            amount=5000,
            location="Salon A"
        )
        
        assert result is True  # Not suspicious


class TestFraudDetectionCardFlagging:
    """Test card flagging functionality"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_flag_card(self, mock_get_db):
        """Test flagging a card for review"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "security_flags": []
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = FraudDetectionService.flag_card(
            card_id="card123",
            reason="Excessive balance checks",
            severity="medium"
        )
        
        assert result["success"] is True
        mock_db.gift_cards.update_one.assert_called_once()

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_flag_card_multiple_flags(self, mock_get_db):
        """Test card with multiple flags"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "security_flags": ["excessive_checks", "unusual_pattern"]
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = FraudDetectionService.flag_card(
            card_id="card123",
            reason="High velocity redemption",
            severity="high"
        )
        
        assert result["success"] is True

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_suspend_card(self, mock_get_db):
        """Test suspending a card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "active"
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = FraudDetectionService.suspend_card(
            card_id="card123",
            reason="Suspected fraud"
        )
        
        assert result["success"] is True
        
        # Verify status was updated to suspended
        update_call = mock_db.gift_cards.update_one.call_args
        assert update_call[0][1]["$set"]["status"] == "suspended"

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_unsuspend_card(self, mock_get_db):
        """Test unsuspending a card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "suspended"
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = FraudDetectionService.unsuspend_card(
            card_id="card123",
            reason="False positive - verified legitimate use"
        )
        
        assert result["success"] is True


class TestFraudDetectionStaffNotification:
    """Test staff notification functionality"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    @patch('app.tasks.gift_card_tasks.notify_staff_of_fraud_flag.delay')
    def test_notify_staff_of_flag(self, mock_notify_task, mock_get_db):
        """Test staff notification when card is flagged"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "security_flags": ["excessive_checks"]
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        FraudDetectionService.flag_card(
            card_id="card123",
            reason="Excessive balance checks",
            severity="medium"
        )
        
        # Verify notification task was called
        mock_notify_task.assert_called_once()

    @patch('app.services.fraud_detection_service.Database.get_db')
    @patch('app.tasks.gift_card_tasks.notify_staff_of_fraud_flag.delay')
    def test_notify_staff_high_severity(self, mock_notify_task, mock_get_db):
        """Test staff notification for high severity flags"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "security_flags": []
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        FraudDetectionService.flag_card(
            card_id="card123",
            reason="Suspected fraud",
            severity="high"
        )
        
        # Verify notification was sent
        mock_notify_task.assert_called_once()


class TestFraudDetectionAuditLogging:
    """Test audit logging of fraud detection events"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_audit_log_flag_event(self, mock_get_db):
        """Test audit log entry for flag event"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "security_flags": [],
            "audit_log": []
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        FraudDetectionService.flag_card(
            card_id="card123",
            reason="Excessive balance checks",
            severity="medium"
        )
        
        # Verify audit log was updated
        update_call = mock_db.gift_cards.update_one.call_args
        assert "$push" in update_call[0][1]
        assert "audit_log" in update_call[0][1]["$push"]

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_audit_log_suspend_event(self, mock_get_db):
        """Test audit log entry for suspend event"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "active",
            "audit_log": []
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        FraudDetectionService.suspend_card(
            card_id="card123",
            reason="Suspected fraud"
        )
        
        # Verify audit log was updated
        update_call = mock_db.gift_cards.update_one.call_args
        assert "$push" in update_call[0][1]
        assert "audit_log" in update_call[0][1]["$push"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
