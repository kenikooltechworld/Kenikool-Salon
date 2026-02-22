"""
Comprehensive unit tests for Gift Card Service - Phase 8
Tests all service methods with 80%+ code coverage
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from bson import ObjectId

from app.services.gift_card_service import GiftCardService


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = Mock()
    db.gift_cards = AsyncMock()
    db.gift_card_transactions = AsyncMock()
    db.clients = AsyncMock()
    return db


@pytest.fixture
def gift_card_service(mock_db):
    """Create a gift card service instance"""
    return GiftCardService(mock_db)


class TestGiftCardValidation:
    """Test gift card validation"""

    @pytest.mark.asyncio
    async def test_validate_gift_card_valid(self, gift_card_service, mock_db):
        """Test validating a valid gift card"""
        card_id = ObjectId()
        card_data = {
            "_id": card_id,
            "tenant_id": "test_tenant",
            "code": "GC-TEST123456",
            "status": "active",
            "current_balance": 25000,
            "initial_amount": 50000,
            "expiry_date": datetime.utcnow() + timedelta(days=365),
            "recipient_name": "John Doe"
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = await gift_card_service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-TEST123456",
            amount_to_use=10000
        )
        
        assert result["valid"] is True
        assert result["current_balance"] == 25000
        assert result["gift_card_id"] == str(card_id)

    @pytest.mark.asyncio
    async def test_validate_gift_card_not_found(self, gift_card_service, mock_db):
        """Test validating a non-existent gift card"""
        mock_db.gift_cards.find_one.return_value = None
        
        result = await gift_card_service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-INVALID"
        )
        
        assert result["valid"] is False
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_validate_gift_card_expired(self, gift_card_service, mock_db):
        """Test validating an expired gift card"""
        card_data = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "code": "GC-EXPIRED",
            "status": "active",
            "current_balance": 25000,
            "expiry_date": datetime.utcnow() - timedelta(days=1)
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = await gift_card_service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-EXPIRED"
        )
        
        assert result["valid"] is False
        assert "expired" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_validate_gift_card_insufficient_balance(self, gift_card_service, mock_db):
        """Test validating with insufficient balance"""
        card_data = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "code": "GC-LOW",
            "status": "active",
            "current_balance": 5000,
            "expiry_date": datetime.utcnow() + timedelta(days=365)
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = await gift_card_service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-LOW",
            amount_to_use=10000
        )
        
        assert result["valid"] is False
        assert "insufficient" in result["error"].lower()


class TestGiftCardRedemption:
    """Test gift card redemption"""

    @pytest.mark.asyncio
    async def test_redeem_gift_card_success(self, gift_card_service, mock_db):
        """Test successful gift card redemption"""
        card_id = ObjectId()
        card_data = {
            "_id": card_id,
            "tenant_id": "test_tenant",
            "code": "GC-TEST123",
            "status": "active",
            "current_balance": 25000,
            "initial_amount": 50000,
            "expiry_date": datetime.utcnow() + timedelta(days=365),
            "recipient_name": "John Doe",
            "redemption_count": 0
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_card_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = await gift_card_service.redeem_gift_card(
            tenant_id="test_tenant",
            code="GC-TEST123",
            amount_to_use=10000,
            booking_id="booking123"
        )
        
        assert result["success"] is True
        assert result["amount_used"] == 10000
        assert result["remaining_balance"] == 15000

    @pytest.mark.asyncio
    async def test_redeem_gift_card_invalid(self, gift_card_service, mock_db):
        """Test redeeming an invalid gift card"""
        mock_db.gift_cards.find_one.return_value = None
        
        result = await gift_card_service.redeem_gift_card(
            tenant_id="test_tenant",
            code="GC-INVALID",
            amount_to_use=10000
        )
        
        assert result["success"] is False
        assert "error" in result


class TestGiftCardBalance:
    """Test gift card balance checking"""

    @pytest.mark.asyncio
    async def test_get_gift_card_balance(self, gift_card_service, mock_db):
        """Test getting gift card balance"""
        card_data = {
            "_id": ObjectId(),
            "code": "GC-TEST123",
            "current_balance": 25000,
            "initial_amount": 50000,
            "status": "active",
            "recipient_name": "John Doe",
            "expiry_date": datetime.utcnow() + timedelta(days=365),
            "redemption_count": 1
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = await gift_card_service.get_gift_card_balance(
            tenant_id="test_tenant",
            code="GC-TEST123"
        )
        
        assert result["found"] is True
        assert result["current_balance"] == 25000
        assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_gift_card_balance_not_found(self, gift_card_service, mock_db):
        """Test getting balance for non-existent card"""
        mock_db.gift_cards.find_one.return_value = None
        
        result = await gift_card_service.get_gift_card_balance(
            tenant_id="test_tenant",
            code="GC-INVALID"
        )
        
        assert result["found"] is False


class TestGiftCardTransactions:
    """Test gift card transaction history"""

    @pytest.mark.asyncio
    async def test_get_gift_card_transactions(self, gift_card_service, mock_db):
        """Test getting transaction history"""
        transactions = [
            {
                "_id": ObjectId(),
                "type": "redeem",
                "amount": 10000,
                "transaction_date": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "type": "redeem",
                "amount": 5000,
                "transaction_date": datetime.utcnow() - timedelta(days=1)
            }
        ]
        
        # Create a proper async mock for the cursor
        mock_cursor = AsyncMock()
        mock_cursor.sort = Mock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=transactions)
        mock_db.gift_card_transactions.find = Mock(return_value=mock_cursor)
        
        result = await gift_card_service.get_gift_card_transactions(
            tenant_id="test_tenant",
            gift_card_id=str(ObjectId())
        )
        
        assert len(result) == 2
        assert result[0]["amount"] == 10000


class TestGiftCardCancellation:
    """Test gift card cancellation"""

    @pytest.mark.asyncio
    async def test_cancel_gift_card_with_refund(self, gift_card_service, mock_db):
        """Test canceling a gift card with refund"""
        card_id = ObjectId()
        card_data = {
            "_id": card_id,
            "status": "active",
            "current_balance": 25000
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = await gift_card_service.cancel_gift_card(
            tenant_id="test_tenant",
            gift_card_id=str(card_id),
            refund=True
        )
        
        assert result["success"] is True
        assert result["refunded"] is True

    @pytest.mark.asyncio
    async def test_cancel_gift_card_without_refund(self, gift_card_service, mock_db):
        """Test canceling a gift card without refund"""
        card_id = ObjectId()
        card_data = {
            "_id": card_id,
            "status": "active",
            "current_balance": 25000
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = await gift_card_service.cancel_gift_card(
            tenant_id="test_tenant",
            gift_card_id=str(card_id),
            refund=False
        )
        
        assert result["success"] is True
        assert result["refunded"] is False

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_card(self, gift_card_service, mock_db):
        """Test canceling a non-existent card"""
        mock_db.gift_cards.find_one.return_value = None
        
        result = await gift_card_service.cancel_gift_card(
            tenant_id="test_tenant",
            gift_card_id=str(ObjectId())
        )
        
        assert result["success"] is False


class TestGiftCardAnalytics:
    """Test gift card analytics"""

    @pytest.mark.asyncio
    async def test_get_gift_card_analytics(self, gift_card_service, mock_db):
        """Test getting analytics"""
        analytics_data = [
            {
                "_id": "active",
                "count": 10,
                "total_initial_amount": 500000,
                "total_current_balance": 250000
            },
            {
                "_id": "redeemed",
                "count": 5,
                "total_initial_amount": 250000,
                "total_current_balance": 0
            }
        ]
        
        # Create a proper async mock for the cursor
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=analytics_data)
        mock_db.gift_cards.aggregate = Mock(return_value=mock_cursor)
        
        result = await gift_card_service.get_gift_card_analytics(
            tenant_id="test_tenant"
        )
        
        assert result["total_gift_cards"] == 15
        assert result["total_sold"] == 750000
        assert result["total_outstanding_balance"] == 250000
        assert result["total_redeemed_value"] == 500000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
