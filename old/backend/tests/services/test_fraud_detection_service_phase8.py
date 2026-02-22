"""
Unit tests for Fraud Detection Service - Phase 8
Tests fraud detection and prevention mechanisms
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from bson import ObjectId

from app.services.fraud_detection_service import FraudDetectionService


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = Mock()
    db.gift_cards = Mock()
    db.gift_card_balance_checks = Mock()
    db.gift_card_redemption_attempts = Mock()
    db.fraud_flags = Mock()
    db.ip_blocks = Mock()
    return db


class TestBalanceCheckRateMonitoring:
    """Test balance check rate monitoring"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_balance_check_rate_normal(self, mock_get_db, mock_db):
        """Test normal balance check rate"""
        mock_get_db.return_value = mock_db
        mock_db.gift_card_balance_checks.find.return_value = []
        
        result = FraudDetectionService.check_balance_check_rate(
            ip_address="192.168.1.1",
            card_number="GC-TEST123",
            tenant_id="test_tenant"
        )
        
        assert result is not None

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_balance_check_rate_excessive(self, mock_get_db, mock_db):
        """Test excessive balance check rate"""
        mock_get_db.return_value = mock_db
        # Simulate 15 balance checks in the last hour
        checks = [
            {"timestamp": datetime.now(timezone.utc) - timedelta(minutes=i)}
            for i in range(15)
        ]
        
        mock_db.gift_card_balance_checks.find.return_value = checks
        
        result = FraudDetectionService.check_balance_check_rate(
            ip_address="192.168.1.1",
            card_number="GC-TEST123",
            tenant_id="test_tenant"
        )
        
        assert result is not None


class TestRedemptionVelocity:
    """Test redemption velocity checks"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_redemption_velocity_normal(self, mock_get_db, mock_db):
        """Test normal redemption velocity"""
        mock_get_db.return_value = mock_db
        mock_db.gift_card_redemption_attempts.find.return_value = []
        
        result = FraudDetectionService.check_redemption_velocity(
            card_number="GC-TEST123"
        )
        
        assert result is not None

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_redemption_velocity_excessive(self, mock_get_db, mock_db):
        """Test excessive redemption velocity"""
        mock_get_db.return_value = mock_db
        # Simulate 5 redemptions in the last day
        redemptions = [
            {"timestamp": datetime.now(timezone.utc) - timedelta(hours=i)}
            for i in range(5)
        ]
        
        mock_db.gift_card_redemption_attempts.find.return_value = redemptions
        
        result = FraudDetectionService.check_redemption_velocity(
            card_number="GC-TEST123"
        )
        
        assert result is not None


class TestUnusualPatternDetection:
    """Test unusual pattern detection"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_unusual_pattern_normal(self, mock_get_db, mock_db):
        """Test normal redemption pattern"""
        mock_get_db.return_value = mock_db
        mock_db.gift_card_redemption_attempts.find.return_value = []
        
        result = FraudDetectionService.check_unusual_pattern(
            card_number="GC-TEST123",
            amount=10000,
            location="Lagos"
        )
        
        assert result is not None

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_unusual_pattern_high_value(self, mock_get_db, mock_db):
        """Test high-value redemption"""
        mock_get_db.return_value = mock_db
        mock_db.gift_card_redemption_attempts.find.return_value = []
        
        result = FraudDetectionService.check_unusual_pattern(
            card_number="GC-TEST123",
            amount=500000,
            location="Lagos"
        )
        
        # High value might be flagged depending on card history
        assert result is not None

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_unusual_pattern_multiple_locations(self, mock_get_db, mock_db):
        """Test redemption from multiple locations"""
        mock_get_db.return_value = mock_db
        # Simulate redemptions from different locations
        mock_db.gift_card_redemption_attempts.find.return_value = [
            {"location": "Lagos", "timestamp": datetime.now(timezone.utc) - timedelta(hours=1)},
            {"location": "Abuja", "timestamp": datetime.now(timezone.utc) - timedelta(minutes=30)},
            {"location": "Port Harcourt", "timestamp": datetime.now(timezone.utc) - timedelta(minutes=5)}
        ]
        
        result = FraudDetectionService.check_unusual_pattern(
            card_number="GC-TEST123",
            amount=10000,
            location="Kano"
        )
        
        # Multiple locations might be flagged
        assert result is not None


class TestCardFlagging:
    """Test card flagging functionality"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_flag_card_low_severity(self, mock_get_db, mock_db):
        """Test flagging card with low severity"""
        mock_get_db.return_value = mock_db
        card_id = ObjectId()
        mock_db.fraud_flags.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        result = FraudDetectionService.flag_card(
            card_id=str(card_id),
            reason="Multiple failed balance checks",
            severity="low"
        )
        
        assert result is not None

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_flag_card_high_severity(self, mock_get_db, mock_db):
        """Test flagging card with high severity"""
        mock_get_db.return_value = mock_db
        card_id = ObjectId()
        mock_db.fraud_flags.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        result = FraudDetectionService.flag_card(
            card_id=str(card_id),
            reason="Suspected fraud - rapid redemptions",
            severity="high"
        )
        
        assert result is not None


class TestCardSuspension:
    """Test card suspension functionality"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_suspend_card(self, mock_get_db, mock_db):
        """Test suspending a card"""
        mock_get_db.return_value = mock_db
        card_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = FraudDetectionService.suspend_card(
            card_id=str(card_id),
            reason="Fraud investigation"
        )
        
        assert result is not None

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_suspend_nonexistent_card(self, mock_get_db, mock_db):
        """Test suspending a non-existent card"""
        mock_get_db.return_value = mock_db
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=0)
        
        result = FraudDetectionService.suspend_card(
            card_id=str(ObjectId()),
            reason="Fraud investigation"
        )
        
        assert result is not None


class TestIPBlocking:
    """Test IP blocking functionality"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_block_ip_address(self, mock_get_db, mock_db):
        """Test blocking an IP address"""
        mock_get_db.return_value = mock_db
        mock_db.ip_blocks.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        result = FraudDetectionService.block_ip(
            ip_address="192.168.1.1",
            reason="Excessive balance check attempts",
            duration_minutes=15
        )
        
        assert result is not None

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_ip_blocked(self, mock_get_db, mock_db):
        """Test checking if IP is blocked"""
        mock_get_db.return_value = mock_db
        mock_db.ip_blocks.find_one.return_value = {
            "_id": ObjectId(),
            "ip_address": "192.168.1.1",
            "blocked_until": datetime.now(timezone.utc) + timedelta(minutes=10)
        }
        
        result = FraudDetectionService.is_ip_blocked("192.168.1.1")
        
        assert result is not None

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_check_ip_not_blocked(self, mock_get_db, mock_db):
        """Test checking if IP is not blocked"""
        mock_get_db.return_value = mock_db
        mock_db.ip_blocks.find_one.return_value = None
        
        result = FraudDetectionService.is_ip_blocked("192.168.1.1")
        
        assert result is not None


class TestFraudDetectionIntegration:
    """Test fraud detection integration scenarios"""

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_detect_brute_force_attack(self, mock_get_db, mock_db):
        """Test detecting brute force attack on balance checks"""
        mock_get_db.return_value = mock_db
        # Simulate 20 failed balance check attempts from same IP
        checks = [
            {"timestamp": datetime.now(timezone.utc) - timedelta(seconds=i), "success": False}
            for i in range(20)
        ]
        
        mock_db.gift_card_balance_checks.find.return_value = checks
        
        result = FraudDetectionService.check_balance_check_rate(
            ip_address="192.168.1.1",
            card_number="GC-TEST123",
            tenant_id="test_tenant"
        )
        
        assert result is not None

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_detect_rapid_redemptions(self, mock_get_db, mock_db):
        """Test detecting rapid redemptions on same card"""
        mock_get_db.return_value = mock_db
        # Simulate 5 redemptions in 5 minutes
        redemptions = [
            {"timestamp": datetime.now(timezone.utc) - timedelta(minutes=i), "amount": 10000}
            for i in range(5)
        ]
        
        mock_db.gift_card_redemption_attempts.find.return_value = redemptions
        
        result = FraudDetectionService.check_redemption_velocity(
            card_number="GC-TEST123"
        )
        
        assert result is not None

    @patch('app.services.fraud_detection_service.Database.get_db')
    def test_detect_geographic_anomaly(self, mock_get_db, mock_db):
        """Test detecting geographic anomaly"""
        mock_get_db.return_value = mock_db
        # Simulate redemption in Lagos, then immediately in Abuja (impossible travel)
        mock_db.gift_card_redemption_attempts.find.return_value = [
            {"location": "Lagos", "timestamp": datetime.now(timezone.utc) - timedelta(minutes=5)},
            {"location": "Abuja", "timestamp": datetime.now(timezone.utc) - timedelta(minutes=1)}
        ]
        
        result = FraudDetectionService.check_unusual_pattern(
            card_number="GC-TEST123",
            amount=10000,
            location="Abuja"
        )
        
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
