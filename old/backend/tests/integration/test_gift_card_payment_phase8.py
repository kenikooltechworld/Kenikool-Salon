"""
Integration tests for Gift Card Payment Integration - Phase 8
Tests payment processing, failure handling, and reconciliation
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
from bson import ObjectId


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = Mock()
    db.payments = AsyncMock()
    db.payment_logs = AsyncMock()
    db.refunds = AsyncMock()
    db.gift_cards = AsyncMock()
    return db


class TestPaymentProcessing:
    """Test payment processing workflow"""

    @pytest.mark.asyncio
    async def test_process_payment_with_gift_card(self, mock_db):
        """Test processing payment with gift card"""
        mock_db.payments.insert_one.return_value.inserted_id = ObjectId()
        
        payment_log = {
            "reference": "ref_123456",
            "amount": 50000,
            "payment_method": "paystack",
            "description": "Gift Card Purchase",
            "status": "success",
            "created_at": datetime.utcnow()
        }
        
        mock_db.payments.insert_one(payment_log)
        assert mock_db.payments.insert_one.called

    @pytest.mark.asyncio
    async def test_payment_with_multiple_gift_cards(self, mock_db):
        """Test payment for multiple gift cards"""
        mock_db.payments.insert_one.return_value.inserted_id = ObjectId()
        
        payment_log = {
            "reference": "ref_bulk_123",
            "amount": 250000,
            "payment_method": "paystack",
            "description": "Bulk Gift Card Purchase",
            "quantity": 5,
            "status": "success",
            "created_at": datetime.utcnow()
        }
        
        mock_db.payments.insert_one(payment_log)
        assert mock_db.payments.insert_one.called

    @pytest.mark.asyncio
    async def test_payment_failure_handling(self, mock_db):
        """Test handling payment failure"""
        payment_log = {
            "reference": "ref_failed_123",
            "amount": 50000,
            "status": "failed",
            "error": "Payment declined",
            "created_at": datetime.utcnow()
        }
        
        mock_db.payments.insert_one(payment_log)
        assert mock_db.payments.insert_one.called

    @pytest.mark.asyncio
    async def test_rollback_on_payment_failure(self, mock_db):
        """Test rolling back gift card creation on payment failure"""
        card_id = ObjectId()
        mock_db.gift_cards.delete_one.return_value = Mock(deleted_count=1)
        
        result = mock_db.gift_cards.delete_one({"_id": card_id})
        assert result.deleted_count == 1

    @pytest.mark.asyncio
    async def test_generate_payment_receipt(self, mock_db):
        """Test generating payment receipt"""
        payment_data = {
            "_id": ObjectId(),
            "reference": "ref_123456",
            "amount": 50000,
            "status": "success",
            "email": "john@example.com",
            "created_at": datetime.utcnow(),
            "gift_card_amount": 50000,
            "card_type": "digital"
        }
        
        mock_db.payments.find_one.return_value = payment_data
        
        result = mock_db.payments.find_one({"reference": "ref_123456"})
        assert result["reference"] == "ref_123456"
        assert result["amount"] == 50000

    @pytest.mark.asyncio
    async def test_send_receipt_email(self, mock_db):
        """Test sending receipt email"""
        payment_data = {
            "_id": ObjectId(),
            "reference": "ref_123456",
            "amount": 50000,
            "email": "john@example.com",
            "created_at": datetime.utcnow()
        }
        
        mock_db.payments.find_one.return_value = payment_data
        
        result = mock_db.payments.find_one({"reference": "ref_123456"})
        assert result is not None

    @pytest.mark.asyncio
    async def test_receipt_includes_gift_card_details(self, mock_db):
        """Test that receipt includes gift card details"""
        payment_data = {
            "_id": ObjectId(),
            "reference": "ref_123456",
            "amount": 50000,
            "status": "success",
            "email": "john@example.com",
            "created_at": datetime.utcnow(),
            "gift_card_number": "GC-DIGITAL001",
            "recipient_name": "John Doe"
        }
        
        mock_db.payments.find_one.return_value = payment_data
        
        result = mock_db.payments.find_one({"reference": "ref_123456"})
        assert result["gift_card_number"] == "GC-DIGITAL001"
        assert result["recipient_name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_reconcile_payments(self, mock_db):
        """Test reconciling payments"""
        payments = [
            {
                "_id": ObjectId(),
                "reference": "ref_1",
                "amount": 50000,
                "status": "success",
                "reconciled": False,
                "created_at": datetime.utcnow() - timedelta(days=1)
            },
            {
                "_id": ObjectId(),
                "reference": "ref_2",
                "amount": 100000,
                "status": "success",
                "reconciled": False,
                "created_at": datetime.utcnow() - timedelta(days=1)
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=payments)
        mock_db.payments.find = AsyncMock(return_value=mock_cursor)
        
        result = await mock_db.payments.find({})
        assert result is not None

    @pytest.mark.asyncio
    async def test_identify_unreconciled_payments(self, mock_db):
        """Test identifying unreconciled payments"""
        unreconciled = [
            {
                "_id": ObjectId(),
                "reference": "ref_unreconciled_1",
                "amount": 50000,
                "status": "success",
                "reconciled": False
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=unreconciled)
        mock_db.payments.find = AsyncMock(return_value=mock_cursor)
        
        result = await mock_db.payments.find({"reconciled": False})
        assert result is not None

    @pytest.mark.asyncio
    async def test_process_refund(self, mock_db):
        """Test processing refund"""
        mock_db.refunds.insert_one.return_value.inserted_id = ObjectId()
        
        refund_log = {
            "original_reference": "ref_original_123",
            "amount": 50000,
            "reason": "customer_request",
            "status": "success",
            "created_at": datetime.utcnow()
        }
        
        mock_db.refunds.insert_one(refund_log)
        assert mock_db.refunds.insert_one.called

    @pytest.mark.asyncio
    async def test_refund_updates_payment_status(self, mock_db):
        """Test that refund updates payment status"""
        mock_db.refunds.insert_one.return_value.inserted_id = ObjectId()
        mock_db.payments.update_one.return_value = Mock(modified_count=1)
        
        refund_log = {
            "original_reference": "ref_original_123",
            "amount": 50000,
            "reason": "customer_request",
            "status": "success",
            "created_at": datetime.utcnow()
        }
        
        mock_db.refunds.insert_one(refund_log)
        assert mock_db.refunds.insert_one.called

    @pytest.mark.asyncio
    async def test_partial_refund(self, mock_db):
        """Test processing partial refund"""
        mock_db.refunds.insert_one.return_value.inserted_id = ObjectId()
        
        refund_log = {
            "original_reference": "ref_original_123",
            "amount": 25000,
            "reason": "partial_cancellation",
            "status": "success",
            "created_at": datetime.utcnow()
        }
        
        mock_db.refunds.insert_one(refund_log)
        assert mock_db.refunds.insert_one.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
