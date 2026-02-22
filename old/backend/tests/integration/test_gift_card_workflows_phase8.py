"""
Integration tests for Gift Card Workflows - Phase 8
Tests end-to-end workflows including validation, redemption, balance checks, and cancellation
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
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


def create_mock_gift_card(code="GC-TEST001", balance=50000, status="active"):
    """Helper to create mock gift card data"""
    return {
        "_id": ObjectId(),
        "tenant_id": "test_tenant",
        "code": code,
        "status": status,
        "current_balance": balance,
        "initial_amount": balance,
        "recipient_name": "John Doe",
        "recipient_email": "john@example.com",
        "expiry_date": datetime.utcnow() + timedelta(days=365),
        "created_at": datetime.utcnow(),
        "redemption_count": 0
    }


class TestGiftCardValidationWorkflow:
    """Test gift card validation workflow"""

    @pytest.mark.asyncio
    async def test_validate_active_card(self, mock_db):
        """Test validating active gift card"""
        service = GiftCardService(mock_db)
        card_data = create_mock_gift_card(code="GC-VALID001", balance=50000, status="active")
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = await service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-VALID001"
        )
        
        assert result["valid"] is True
        assert result["current_balance"] == 50000

    @pytest.mark.asyncio
    async def test_validate_inactive_card(self, mock_db):
        """Test validating inactive gift card"""
        service = GiftCardService(mock_db)
        card_data = create_mock_gift_card(code="GC-INACTIVE", balance=50000, status="inactive")
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = await service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-INACTIVE"
        )
        
        assert result["valid"] is False
        assert "inactive" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_validate_nonexistent_card(self, mock_db):
        """Test validating nonexistent gift card"""
        service = GiftCardService(mock_db)
        mock_db.gift_cards.find_one.return_value = None
        
        result = await service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-NOTFOUND"
        )
        
        assert result["valid"] is False
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_validate_expired_card(self, mock_db):
        """Test validating expired gift card"""
        service = GiftCardService(mock_db)
        card_data = create_mock_gift_card(code="GC-EXPIRED", balance=50000, status="active")
        card_data["expiry_date"] = datetime.utcnow() - timedelta(days=1)
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = await service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-EXPIRED"
        )
        
        assert result["valid"] is False
        assert "expired" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_validate_with_amount_check(self, mock_db):
        """Test validating with amount check"""
        service = GiftCardService(mock_db)
        card_data = create_mock_gift_card(code="GC-AMOUNT", balance=30000, status="active")
        mock_db.gift_cards.find_one.return_value = card_data
        
        # Valid amount
        result = await service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-AMOUNT",
            amount_to_use=20000
        )
        assert result["valid"] is True
        
        # Invalid amount (exceeds balance)
        result = await service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-AMOUNT",
            amount_to_use=50000
        )
        assert result["valid"] is False
        assert "Insufficient balance" in result["error"]


class TestGiftCardRedemptionWorkflow:
    """Test complete redemption workflow"""

    @pytest.mark.asyncio
    async def test_full_redemption(self, mock_db):
        """Test full redemption workflow"""
        service = GiftCardService(mock_db)
        card_data = create_mock_gift_card(code="GC-REDEEM001", balance=50000, status="active")
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_card_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        mock_db.clients.find_one.return_value = None
        
        result = await service.redeem_gift_card(
            tenant_id="test_tenant",
            code="GC-REDEEM001",
            amount_to_use=50000,
            booking_id="booking123"
        )
        
        assert result["success"] is True
        assert result["amount_used"] == 50000
        assert result["remaining_balance"] == 0

    @pytest.mark.asyncio
    async def test_partial_redemption(self, mock_db):
        """Test partial redemption"""
        service = GiftCardService(mock_db)
        card_data = create_mock_gift_card(code="GC-PARTIAL", balance=50000, status="active")
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_card_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        mock_db.clients.find_one.return_value = None
        
        result = await service.redeem_gift_card(
            tenant_id="test_tenant",
            code="GC-PARTIAL",
            amount_to_use=30000
        )
        
        assert result["success"] is True
        assert result["amount_used"] == 30000
        assert result["remaining_balance"] == 20000

    @pytest.mark.asyncio
    async def test_redemption_insufficient_balance(self, mock_db):
        """Test redemption with insufficient balance"""
        service = GiftCardService(mock_db)
        card_data = create_mock_gift_card(code="GC-INSUFFICIENT", balance=10000, status="active")
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = await service.redeem_gift_card(
            tenant_id="test_tenant",
            code="GC-INSUFFICIENT",
            amount_to_use=50000
        )
        
        assert result["success"] is False
        assert "Insufficient balance" in result["error"]

    @pytest.mark.asyncio
    async def test_redemption_inactive_card(self, mock_db):
        """Test redemption with inactive card"""
        service = GiftCardService(mock_db)
        card_data = create_mock_gift_card(code="GC-INACTIVE", balance=50000, status="inactive")
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = await service.redeem_gift_card(
            tenant_id="test_tenant",
            code="GC-INACTIVE",
            amount_to_use=30000
        )
        
        assert result["success"] is False


class TestGiftCardBalanceCheck:
    """Test gift card balance check workflow"""

    @pytest.mark.asyncio
    async def test_get_balance_active_card(self, mock_db):
        """Test getting balance of active card"""
        service = GiftCardService(mock_db)
        card_data = create_mock_gift_card(code="GC-BALANCE001", balance=35000, status="active")
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = await service.get_gift_card_balance(
            tenant_id="test_tenant",
            code="GC-BALANCE001"
        )
        
        assert result["found"] is True
        assert result["current_balance"] == 35000
        assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_balance_nonexistent_card(self, mock_db):
        """Test getting balance of nonexistent card"""
        service = GiftCardService(mock_db)
        mock_db.gift_cards.find_one.return_value = None
        
        result = await service.get_gift_card_balance(
            tenant_id="test_tenant",
            code="GC-NOTFOUND"
        )
        
        assert result["found"] is False
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_get_balance_includes_metadata(self, mock_db):
        """Test that balance check includes metadata"""
        service = GiftCardService(mock_db)
        card_data = create_mock_gift_card(code="GC-META", balance=25000, status="active")
        card_data["redemption_count"] = 3
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = await service.get_gift_card_balance(
            tenant_id="test_tenant",
            code="GC-META"
        )
        
        assert result["found"] is True
        assert result["current_balance"] == 25000
        assert result["initial_amount"] == 25000
        assert result["redemption_count"] == 3


class TestGiftCardCancellation:
    """Test gift card cancellation workflow"""

    @pytest.mark.asyncio
    async def test_cancel_unused_card(self, mock_db):
        """Test canceling unused card"""
        service = GiftCardService(mock_db)
        card_id = ObjectId()
        card_data = create_mock_gift_card(code="GC-CANCEL001", balance=50000, status="active")
        card_data["_id"] = card_id
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = await service.cancel_gift_card(
            tenant_id="test_tenant",
            gift_card_id=str(card_id),
            refund=True
        )
        
        assert result["success"] is True
        assert result["refunded"] is True

    @pytest.mark.asyncio
    async def test_cancel_partially_used_card(self, mock_db):
        """Test canceling partially used card"""
        service = GiftCardService(mock_db)
        card_id = ObjectId()
        card_data = create_mock_gift_card(code="GC-CANCEL002", balance=20000, status="active")
        card_data["_id"] = card_id
        card_data["initial_amount"] = 50000
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = await service.cancel_gift_card(
            tenant_id="test_tenant",
            gift_card_id=str(card_id),
            refund=True
        )
        
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_card(self, mock_db):
        """Test canceling nonexistent card"""
        service = GiftCardService(mock_db)
        mock_db.gift_cards.find_one.return_value = None
        
        result = await service.cancel_gift_card(
            tenant_id="test_tenant",
            gift_card_id=str(ObjectId()),
            refund=True
        )
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()


class TestGiftCardAnalytics:
    """Test gift card analytics workflow"""

    @pytest.mark.asyncio
    async def test_get_analytics(self, mock_db):
        """Test getting gift card analytics"""
        service = GiftCardService(mock_db)
        
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
        
        # Create a proper mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=analytics_data)
        mock_db.gift_cards.aggregate = Mock(return_value=mock_cursor)
        
        result = await service.get_gift_card_analytics(
            tenant_id="test_tenant"
        )
        
        assert result is not None


class TestGiftCardTransactionHistory:
    """Test gift card transaction history"""

    @pytest.mark.asyncio
    async def test_get_transaction_history(self, mock_db):
        """Test getting transaction history"""
        service = GiftCardService(mock_db)
        
        transactions = [
            {
                "_id": ObjectId(),
                "gift_card_id": "gc_123",
                "amount_used": 20000,
                "balance_after": 30000,
                "transaction_date": datetime.utcnow() - timedelta(days=1)
            },
            {
                "_id": ObjectId(),
                "gift_card_id": "gc_123",
                "amount_used": 15000,
                "balance_after": 15000,
                "transaction_date": datetime.utcnow()
            }
        ]
        
        # Create a proper mock cursor with sort and to_list
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=transactions)
        mock_cursor.sort = Mock(return_value=mock_cursor)
        mock_db.gift_card_transactions.find = Mock(return_value=mock_cursor)
        
        result = await service.get_gift_card_transactions(
            tenant_id="test_tenant",
            gift_card_id="gc_123"
        )
        
        assert len(result) == 2
        assert result[0]["amount_used"] == 20000
        assert result[1]["amount_used"] == 15000


class TestCompleteGiftCardLifecycle:
    """Test complete gift card lifecycle"""

    @pytest.mark.asyncio
    async def test_digital_card_lifecycle(self, mock_db):
        """Test complete lifecycle of digital gift card"""
        service = GiftCardService(mock_db)
        
        card_data = create_mock_gift_card(code="GC-LIFECYCLE001", balance=50000, status="active")
        
        # Setup mocks for each call
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_card_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        mock_db.clients.find_one.return_value = None
        
        # Step 1: Validate card
        validation = await service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-LIFECYCLE001"
        )
        assert validation["valid"] is True
        
        # Step 2: Check balance
        balance = await service.get_gift_card_balance(
            tenant_id="test_tenant",
            code="GC-LIFECYCLE001"
        )
        assert balance["current_balance"] == 50000
        
        # Step 3: Redeem card
        redeem = await service.redeem_gift_card(
            tenant_id="test_tenant",
            code="GC-LIFECYCLE001",
            amount_to_use=20000
        )
        assert redeem["success"] is True
        assert redeem["remaining_balance"] == 30000

    @pytest.mark.asyncio
    async def test_physical_card_lifecycle(self, mock_db):
        """Test complete lifecycle of physical gift card"""
        service = GiftCardService(mock_db)
        
        card_data = create_mock_gift_card(code="GC-PHYS-LIFECYCLE", balance=100000, status="inactive")
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        mock_db.gift_card_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.clients.find_one.return_value = None
        
        # Step 1: Validate inactive card (should fail)
        validation = await service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-PHYS-LIFECYCLE"
        )
        assert validation["valid"] is False
        
        # Step 2: Activate card
        card_data["status"] = "active"
        
        # Step 3: Validate active card (should succeed)
        validation = await service.validate_gift_card(
            tenant_id="test_tenant",
            code="GC-PHYS-LIFECYCLE"
        )
        assert validation["valid"] is True
        
        # Step 4: Redeem card
        card_data["current_balance"] = 50000
        redeem = await service.redeem_gift_card(
            tenant_id="test_tenant",
            code="GC-PHYS-LIFECYCLE",
            amount_to_use=50000
        )
        assert redeem["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
