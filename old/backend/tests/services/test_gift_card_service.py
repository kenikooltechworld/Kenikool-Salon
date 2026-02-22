"""
Comprehensive unit tests for Gift Card Service
Tests all service methods with 80%+ code coverage
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from bson import ObjectId
import bcrypt

from app.services.gift_card_service import GiftCardService
from app.api.exceptions import BadRequestException, NotFoundException


class TestGiftCardServiceCreation:
    """Test gift card creation functionality"""

    @patch('app.services.gift_card_service.Database.get_db')
    @patch('app.services.gift_card_service.GiftCardService.generate_card_number')
    @patch('app.services.gift_card_service.GiftCardService.send_digital_card')
    def test_create_digital_gift_card(self, mock_send, mock_gen_number, mock_get_db):
        """Test creating a digital gift card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_gen_number.return_value = "GC-TEST123456"
        mock_send.return_value = True
        
        card_id = ObjectId()
        mock_db.gift_cards.insert_one.return_value.inserted_id = card_id
        
        result = GiftCardService.create_gift_card(
            tenant_id="test_tenant",
            amount=50000,
            card_type="digital",
            recipient_email="john@example.com",
            recipient_name="John Doe",
            message="Happy Birthday!",
            design_theme="default",
            activation_required=False
        )
        
        assert result["card_number"] == "GC-TEST123456"
        assert result["amount"] == 50000
        assert result["status"] == "active"
        assert result["card_type"] == "digital"
        mock_db.gift_cards.insert_one.assert_called_once()
        mock_send.assert_called_once()

    @patch('app.services.gift_card_service.Database.get_db')
    @patch('app.services.gift_card_service.GiftCardService.generate_card_number')
    def test_create_physical_gift_card(self, mock_gen_number, mock_get_db):
        """Test creating a physical gift card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_gen_number.return_value = "GC-PHYS123456"
        
        card_id = ObjectId()
        mock_db.gift_cards.insert_one.return_value.inserted_id = card_id
        
        result = GiftCardService.create_gift_card(
            tenant_id="test_tenant",
            amount=100000,
            card_type="physical",
            activation_required=True
        )
        
        assert result["card_number"] == "GC-PHYS123456"
        assert result["status"] == "inactive"
        assert result["card_type"] == "physical"
        assert result["activation_required"] is True

    @patch('app.services.gift_card_service.Database.get_db')
    def test_create_gift_card_with_scheduled_delivery(self, mock_get_db):
        """Test creating gift card with scheduled delivery"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        scheduled_date = datetime.now(timezone.utc) + timedelta(days=7)
        
        with patch.object(GiftCardService, 'generate_card_number', return_value="GC-SCHED123"):
            card_id = ObjectId()
            mock_db.gift_cards.insert_one.return_value.inserted_id = card_id
            
            result = GiftCardService.create_gift_card(
                tenant_id="test_tenant",
                amount=50000,
                card_type="digital",
                recipient_email="john@example.com",
                recipient_name="John Doe",
                scheduled_delivery=scheduled_date
            )
            
            assert result["scheduled_delivery"] == scheduled_date
            assert result["delivery_status"] == "pending"

    @patch('app.services.gift_card_service.Database.get_db')
    def test_create_gift_card_with_pin(self, mock_get_db):
        """Test creating gift card with PIN protection"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        with patch.object(GiftCardService, 'generate_card_number', return_value="GC-PIN123"):
            card_id = ObjectId()
            mock_db.gift_cards.insert_one.return_value.inserted_id = card_id
            
            result = GiftCardService.create_gift_card(
                tenant_id="test_tenant",
                amount=50000,
                card_type="digital",
                recipient_email="john@example.com",
                recipient_name="John Doe",
                pin_enabled=True
            )
            
            assert result["pin_enabled"] is True

    @patch('app.services.gift_card_service.Database.get_db')
    def test_create_gift_card_invalid_amount(self, mock_get_db):
        """Test creating gift card with invalid amount"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        with pytest.raises(BadRequestException):
            GiftCardService.create_gift_card(
                tenant_id="test_tenant",
                amount=0,
                card_type="digital",
                recipient_email="john@example.com"
            )

    @patch('app.services.gift_card_service.Database.get_db')
    def test_create_gift_card_invalid_card_type(self, mock_get_db):
        """Test creating gift card with invalid card type"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        with pytest.raises(BadRequestException):
            GiftCardService.create_gift_card(
                tenant_id="test_tenant",
                amount=50000,
                card_type="invalid_type",
                recipient_email="john@example.com"
            )

    @patch('app.services.gift_card_service.Database.get_db')
    def test_create_digital_card_missing_email(self, mock_get_db):
        """Test creating digital card without email"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        with pytest.raises(BadRequestException):
            GiftCardService.create_gift_card(
                tenant_id="test_tenant",
                amount=50000,
                card_type="digital"
            )


class TestGiftCardServiceActivation:
    """Test gift card activation functionality"""

    @patch('app.services.gift_card_service.Database.get_db')
    def test_activate_card(self, mock_get_db):
        """Test activating an inactive card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "inactive",
            "activation_required": True
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = GiftCardService.activate_card(
            card_id=str(card_data["_id"]),
            activated_by="user123"
        )
        
        assert result["success"] is True
        assert result["status"] == "active"
        mock_db.gift_cards.update_one.assert_called_once()

    @patch('app.services.gift_card_service.Database.get_db')
    def test_activate_already_active_card(self, mock_get_db):
        """Test activating an already active card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "active"
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        with pytest.raises(BadRequestException):
            GiftCardService.activate_card(
                card_id=str(card_data["_id"]),
                activated_by="user123"
            )

    @patch('app.services.gift_card_service.Database.get_db')
    def test_activate_nonexistent_card(self, mock_get_db):
        """Test activating a nonexistent card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_db.gift_cards.find_one.return_value = None
        
        with pytest.raises(NotFoundException):
            GiftCardService.activate_card(
                card_id="invalid_id",
                activated_by="user123"
            )


class TestGiftCardServiceVoid:
    """Test gift card void functionality"""

    @patch('app.services.gift_card_service.Database.get_db')
    def test_void_card_with_refund(self, mock_get_db):
        """Test voiding a card with refund"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "active",
            "balance": 25000,
            "amount": 50000
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = GiftCardService.void_card(
            card_id=str(card_data["_id"]),
            reason="customer_request",
            voided_by="user123",
            refund=True
        )
        
        assert result["success"] is True
        assert result["status"] == "voided"
        assert result["refund_amount"] == 25000

    @patch('app.services.gift_card_service.Database.get_db')
    def test_void_card_without_refund(self, mock_get_db):
        """Test voiding a card without refund"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "active",
            "balance": 25000
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = GiftCardService.void_card(
            card_id=str(card_data["_id"]),
            reason="fraud",
            voided_by="user123",
            refund=False
        )
        
        assert result["success"] is True
        assert result["refund_amount"] == 0

    @patch('app.services.gift_card_service.Database.get_db')
    def test_void_already_voided_card(self, mock_get_db):
        """Test voiding an already voided card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "voided"
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        with pytest.raises(BadRequestException):
            GiftCardService.void_card(
                card_id=str(card_data["_id"]),
                reason="error",
                voided_by="user123"
            )


class TestGiftCardServiceReload:
    """Test gift card reload functionality"""

    @patch('app.services.gift_card_service.Database.get_db')
    def test_reload_card(self, mock_get_db):
        """Test reloading a gift card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "active",
            "balance": 10000,
            "amount": 50000,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=30)
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = GiftCardService.reload_card(
            card_id=str(card_data["_id"]),
            amount=20000,
            payment_method="cash"
        )
        
        assert result["success"] is True
        assert result["new_balance"] == 30000
        assert result["reload_amount"] == 20000

    @patch('app.services.gift_card_service.Database.get_db')
    def test_reload_expired_card(self, mock_get_db):
        """Test reloading an expired card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "expired",
            "balance": 10000,
            "expires_at": datetime.now(timezone.utc) - timedelta(days=1)
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        with pytest.raises(BadRequestException):
            GiftCardService.reload_card(
                card_id=str(card_data["_id"]),
                amount=20000,
                payment_method="cash"
            )

    @patch('app.services.gift_card_service.Database.get_db')
    def test_reload_invalid_amount(self, mock_get_db):
        """Test reloading with invalid amount"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "active"
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        with pytest.raises(BadRequestException):
            GiftCardService.reload_card(
                card_id=str(card_data["_id"]),
                amount=0,
                payment_method="cash"
            )


class TestGiftCardServicePIN:
    """Test gift card PIN functionality"""

    @patch('app.services.gift_card_service.Database.get_db')
    def test_set_pin(self, mock_get_db):
        """Test setting a PIN"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "active"
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = GiftCardService.set_pin(
            card_number="GC-TEST123",
            pin="1234"
        )
        
        assert result["success"] is True
        mock_db.gift_cards.update_one.assert_called_once()

    @patch('app.services.gift_card_service.Database.get_db')
    def test_validate_pin_correct(self, mock_get_db):
        """Test validating correct PIN"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Hash a PIN for testing
        hashed_pin = bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode()
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "pin": hashed_pin,
            "pin_enabled": True
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = GiftCardService.validate_pin(
            card_number="GC-TEST123",
            pin="1234"
        )
        
        assert result is True

    @patch('app.services.gift_card_service.Database.get_db')
    def test_validate_pin_incorrect(self, mock_get_db):
        """Test validating incorrect PIN"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        hashed_pin = bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode()
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "pin": hashed_pin,
            "pin_enabled": True
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = GiftCardService.validate_pin(
            card_number="GC-TEST123",
            pin="9999"
        )
        
        assert result is False

    @patch('app.services.gift_card_service.Database.get_db')
    def test_validate_pin_not_enabled(self, mock_get_db):
        """Test validating PIN when not enabled"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "pin_enabled": False
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = GiftCardService.validate_pin(
            card_number="GC-TEST123",
            pin="1234"
        )
        
        assert result is True  # No PIN required


class TestGiftCardServiceBulkCreate:
    """Test bulk gift card creation"""

    @patch('app.services.gift_card_service.Database.get_db')
    @patch('app.services.gift_card_service.GiftCardService.create_gift_card')
    def test_bulk_create_cards(self, mock_create, mock_get_db):
        """Test bulk creating gift cards"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        cards_data = [
            {
                "recipient_name": "John Doe",
                "recipient_email": "john@example.com",
                "message": "Happy Birthday!"
            },
            {
                "recipient_name": "Jane Smith",
                "recipient_email": "jane@example.com",
                "message": "Congratulations!"
            }
        ]
        
        mock_create.side_effect = [
            {"card_number": "GC-001", "success": True},
            {"card_number": "GC-002", "success": True}
        ]
        
        result = GiftCardService.bulk_create(
            tenant_id="test_tenant",
            cards_data=cards_data,
            amount=50000,
            card_type="digital",
            created_by="user123"
        )
        
        assert result["total_created"] == 2
        assert result["total_failed"] == 0
        assert len(result["created_cards"]) == 2

    @patch('app.services.gift_card_service.Database.get_db')
    def test_bulk_create_exceeds_limit(self, mock_get_db):
        """Test bulk create with too many cards"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        cards_data = [{"recipient_name": f"User {i}", "recipient_email": f"user{i}@example.com"} for i in range(101)]
        
        with pytest.raises(BadRequestException):
            GiftCardService.bulk_create(
                tenant_id="test_tenant",
                cards_data=cards_data,
                amount=50000,
                card_type="digital",
                created_by="user123"
            )


class TestGiftCardServiceAnalytics:
    """Test gift card analytics"""

    @patch('app.services.gift_card_service.Database.get_db')
    def test_get_analytics(self, mock_get_db):
        """Test getting analytics"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        mock_db.gift_cards.find.return_value = [
            {
                "amount": 50000,
                "balance": 25000,
                "status": "active",
                "card_type": "digital",
                "transactions": [{"type": "redeem", "amount": 25000}]
            },
            {
                "amount": 30000,
                "balance": 30000,
                "status": "active",
                "card_type": "physical",
                "transactions": []
            }
        ]
        
        analytics = GiftCardService.get_analytics(
            tenant_id="test_tenant"
        )
        
        assert analytics["total_sold"] == 80000
        assert analytics["total_redeemed"] == 25000
        assert analytics["outstanding_liability"] == 55000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
