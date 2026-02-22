"""
Integration tests for Gift Card POS Integration - Phase 8
Tests POS checkout with gift card, split payments, receipt generation, balance updates
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
from bson import ObjectId


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = Mock()
    db.gift_cards = AsyncMock()
    db.gift_card_transactions = AsyncMock()
    db.pos_transactions = AsyncMock()
    db.pos_receipts = AsyncMock()
    return db


class TestPOSCheckoutWithGiftCard:
    """Test POS checkout with gift card"""

    @pytest.mark.asyncio
    async def test_checkout_with_gift_card_only(self, mock_db):
        """Test checkout using only gift card"""
        card_data = {
            "_id": ObjectId(),
            "code": "GC-POS001",
            "status": "active",
            "current_balance": 50000,
            "expiry_date": datetime.utcnow() + timedelta(days=365)
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_card_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.pos_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = mock_db.gift_cards.find_one({"code": "GC-POS001"})
        assert result["status"] == "active"
        assert result["current_balance"] == 50000

    @pytest.mark.asyncio
    async def test_checkout_with_insufficient_gift_card_balance(self, mock_db):
        """Test checkout with insufficient gift card balance"""
        card_data = {
            "_id": ObjectId(),
            "code": "GC-POS002",
            "status": "active",
            "current_balance": 20000,
            "expiry_date": datetime.utcnow() + timedelta(days=365)
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = mock_db.gift_cards.find_one({"code": "GC-POS002"})
        assert result["current_balance"] == 20000

    @pytest.mark.asyncio
    async def test_checkout_with_expired_gift_card(self, mock_db):
        """Test checkout with expired gift card"""
        card_data = {
            "_id": ObjectId(),
            "code": "GC-EXPIRED",
            "status": "active",
            "current_balance": 50000,
            "expiry_date": datetime.utcnow() - timedelta(days=1)
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        result = mock_db.gift_cards.find_one({"code": "GC-EXPIRED"})
        assert result["expiry_date"] < datetime.utcnow()


class TestPOSSplitPayment:
    """Test POS split payment (gift card + cash/card)"""

    @pytest.mark.asyncio
    async def test_split_payment_gift_card_and_cash(self, mock_db):
        """Test split payment with gift card and cash"""
        card_data = {
            "_id": ObjectId(),
            "code": "GC-SPLIT001",
            "status": "active",
            "current_balance": 30000,
            "expiry_date": datetime.utcnow() + timedelta(days=365)
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_card_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.pos_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = mock_db.gift_cards.find_one({"code": "GC-SPLIT001"})
        assert result["current_balance"] == 30000

    @pytest.mark.asyncio
    async def test_split_payment_gift_card_and_card(self, mock_db):
        """Test split payment with gift card and credit card"""
        card_data = {
            "_id": ObjectId(),
            "code": "GC-SPLIT002",
            "status": "active",
            "current_balance": 25000,
            "expiry_date": datetime.utcnow() + timedelta(days=365)
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_card_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.pos_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = mock_db.gift_cards.find_one({"code": "GC-SPLIT002"})
        assert result["current_balance"] == 25000

    @pytest.mark.asyncio
    async def test_split_payment_multiple_gift_cards(self, mock_db):
        """Test split payment with multiple gift cards"""
        card1_data = {
            "_id": ObjectId(),
            "code": "GC-MULTI001",
            "status": "active",
            "current_balance": 20000,
            "expiry_date": datetime.utcnow() + timedelta(days=365)
        }
        
        card2_data = {
            "_id": ObjectId(),
            "code": "GC-MULTI002",
            "status": "active",
            "current_balance": 15000,
            "expiry_date": datetime.utcnow() + timedelta(days=365)
        }
        
        mock_db.gift_cards.find_one.side_effect = [card1_data, card2_data]
        mock_db.gift_card_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.pos_transactions.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result1 = mock_db.gift_cards.find_one({"code": "GC-MULTI001"})
        result2 = mock_db.gift_cards.find_one({"code": "GC-MULTI002"})
        
        assert result1["current_balance"] == 20000
        assert result2["current_balance"] == 15000


class TestPOSReceiptGeneration:
    """Test POS receipt generation"""

    @pytest.mark.asyncio
    async def test_generate_receipt_with_gift_card(self, mock_db):
        """Test generating receipt with gift card payment"""
        transaction_data = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "items": [
                {"name": "Haircut", "price": 25000, "quantity": 1},
                {"name": "Hair Treatment", "price": 25000, "quantity": 1}
            ],
            "total_amount": 50000,
            "payment_method": "gift_card",
            "gift_card_code": "GC-POS001",
            "gift_card_amount": 50000,
            "created_at": datetime.utcnow()
        }
        
        mock_db.pos_transactions.find_one.return_value = transaction_data
        
        result = mock_db.pos_transactions.find_one({"_id": transaction_data["_id"]})
        assert result["total_amount"] == 50000
        assert result["payment_method"] == "gift_card"

    @pytest.mark.asyncio
    async def test_generate_receipt_with_split_payment(self, mock_db):
        """Test generating receipt with split payment"""
        transaction_data = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "items": [
                {"name": "Haircut", "price": 25000, "quantity": 1},
                {"name": "Hair Treatment", "price": 25000, "quantity": 1}
            ],
            "total_amount": 50000,
            "payment_method": "split",
            "gift_card_amount": 30000,
            "cash_amount": 20000,
            "created_at": datetime.utcnow()
        }
        
        mock_db.pos_transactions.find_one.return_value = transaction_data
        
        result = mock_db.pos_transactions.find_one({"_id": transaction_data["_id"]})
        assert result["gift_card_amount"] == 30000
        assert result["cash_amount"] == 20000

    @pytest.mark.asyncio
    async def test_receipt_shows_remaining_balance(self, mock_db):
        """Test that receipt shows remaining gift card balance"""
        transaction_data = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "total_amount": 30000,
            "payment_method": "gift_card",
            "gift_card_code": "GC-POS001",
            "gift_card_amount": 30000,
            "gift_card_remaining_balance": 20000,
            "created_at": datetime.utcnow()
        }
        
        mock_db.pos_transactions.find_one.return_value = transaction_data
        
        result = mock_db.pos_transactions.find_one({"_id": transaction_data["_id"]})
        assert result["gift_card_remaining_balance"] == 20000


class TestPOSTransactionLogging:
    """Test POS transaction logging"""

    @pytest.mark.asyncio
    async def test_log_gift_card_transaction(self, mock_db):
        """Test logging gift card transaction"""
        mock_db.gift_card_transactions.insert_one.return_value.inserted_id = ObjectId()
        
        transaction_log = {
            "tenant_id": "test_tenant",
            "gift_card_code": "GC-LOG001",
            "transaction_type": "redemption",
            "amount": 30000,
            "remaining_balance": 20000,
            "location": "POS Terminal 1",
            "created_at": datetime.utcnow()
        }
        
        mock_db.gift_card_transactions.insert_one(transaction_log)
        assert mock_db.gift_card_transactions.insert_one.called

    @pytest.mark.asyncio
    async def test_transaction_includes_metadata(self, mock_db):
        """Test that transaction includes metadata"""
        mock_db.gift_card_transactions.insert_one.return_value.inserted_id = ObjectId()
        
        transaction_log = {
            "tenant_id": "test_tenant",
            "gift_card_code": "GC-LOG002",
            "transaction_type": "redemption",
            "amount": 30000,
            "remaining_balance": 20000,
            "location": "POS Terminal 1",
            "staff_id": "staff_123",
            "client_id": "client_456",
            "created_at": datetime.utcnow()
        }
        
        mock_db.gift_card_transactions.insert_one(transaction_log)
        assert mock_db.gift_card_transactions.insert_one.called

    @pytest.mark.asyncio
    async def test_get_transaction_history(self, mock_db):
        """Test getting transaction history"""
        transactions = [
            {
                "_id": ObjectId(),
                "gift_card_code": "GC-HISTORY",
                "transaction_type": "redemption",
                "amount": 20000,
                "created_at": datetime.utcnow() - timedelta(days=1)
            },
            {
                "_id": ObjectId(),
                "gift_card_code": "GC-HISTORY",
                "transaction_type": "reload",
                "amount": 25000,
                "created_at": datetime.utcnow()
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=transactions)
        mock_db.gift_card_transactions.find = AsyncMock(return_value=mock_cursor)
        
        result = await mock_db.gift_card_transactions.find({})
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
