"""
Tests for Gift Card Transfer Functionality
Tests transfer logic, daily limits, confirmation emails, and audit logging
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId

from app.services.pos_service import POSService
from app.api.exceptions import BadRequestException, NotFoundException


class TestGiftCardTransfer:
    """Test gift card transfer functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        db = Mock()
        db.gift_cards = Mock()
        return db
    
    @pytest.fixture
    def source_card_data(self):
        """Sample source gift card data"""
        return {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "card_number": "GC-SOURCE123",
            "amount": 10000,
            "balance": 10000,
            "status": "active",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "recipient_name": "John Doe",
            "recipient_email": "john@example.com",
            "transactions": [],
            "audit_log": []
        }
    
    @pytest.fixture
    def dest_card_data(self):
        """Sample destination gift card data"""
        return {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "card_number": "GC-DEST456",
            "amount": 5000,
            "balance": 5000,
            "status": "active",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "recipient_name": "Jane Smith",
            "recipient_email": "jane@example.com",
            "transactions": [],
            "audit_log": []
        }
    
    @patch('app.services.pos_service.Database.get_db')
    @patch('app.tasks.gift_card_tasks.send_transfer_confirmation_emails.delay')
    def test_transfer_full_balance_to_existing_card(self, mock_email_task, mock_get_db, mock_db, source_card_data, dest_card_data):
        """Test transferring full balance to an existing card"""
        mock_get_db.return_value = mock_db
        
        # Setup mock responses
        mock_db.gift_cards.find_one.side_effect = [
            source_card_data,  # First call for source card
            dest_card_data,    # Second call for destination card
            dest_card_data     # Third call after update
        ]
        
        # Execute transfer
        result = POSService.transfer_gift_card_balance(
            tenant_id="test_tenant",
            source_card="GC-SOURCE123",
            destination_card="GC-DEST456",
            amount=10000,
            transferred_by="user123"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["source_card"] == "GC-SOURCE123"
        assert result["destination_card"] == "GC-DEST456"
        assert result["amount"] == 10000
        assert result["source_balance"] == 0
        assert result["destination_balance"] == 15000
        assert result["created_new_card"] is False
        
        # Verify database updates
        assert mock_db.gift_cards.update_one.call_count == 2
        
        # Verify email task was called
        mock_email_task.assert_called_once()
    
    @patch('app.services.pos_service.Database.get_db')
    @patch('app.services.pos_service.POSService.create_gift_card')
    @patch('app.tasks.gift_card_tasks.send_transfer_confirmation_emails.delay')
    def test_transfer_to_new_card(self, mock_email_task, mock_create_card, mock_get_db, mock_db, source_card_data):
        """Test transferring balance to a new card (no destination provided)"""
        mock_get_db.return_value = mock_db
        
        new_card_data = {
            "_id": ObjectId(),
            "card_number": "GC-NEW789",
            "balance": 0,
            "status": "active"
        }
        
        mock_create_card.return_value = new_card_data
        mock_db.gift_cards.find_one.side_effect = [
            source_card_data,  # Source card
            new_card_data      # New card after creation
        ]
        
        # Execute transfer without destination
        result = POSService.transfer_gift_card_balance(
            tenant_id="test_tenant",
            source_card="GC-SOURCE123",
            destination_card=None,
            amount=5000,
            transferred_by="user123"
        )
        
        # Verify new card was created
        mock_create_card.assert_called_once()
        assert result["created_new_card"] is True
        assert result["destination_card"] == "GC-NEW789"
        assert result["amount"] == 5000
    
    @patch('app.services.pos_service.Database.get_db')
    def test_transfer_partial_balance(self, mock_get_db, mock_db, source_card_data, dest_card_data):
        """Test transferring partial balance"""
        mock_get_db.return_value = mock_db
        
        mock_db.gift_cards.find_one.side_effect = [
            source_card_data,
            dest_card_data,
            dest_card_data
        ]
        
        # Transfer partial amount
        result = POSService.transfer_gift_card_balance(
            tenant_id="test_tenant",
            source_card="GC-SOURCE123",
            destination_card="GC-DEST456",
            amount=3000,
            transferred_by="user123"
        )
        
        # Verify balances
        assert result["source_balance"] == 7000
        assert result["destination_balance"] == 8000
        assert result["amount"] == 3000
    
    @patch('app.services.pos_service.Database.get_db')
    def test_transfer_insufficient_balance(self, mock_get_db, mock_db, source_card_data):
        """Test transfer fails with insufficient balance"""
        mock_get_db.return_value = mock_db
        mock_db.gift_cards.find_one.return_value = source_card_data
        
        # Try to transfer more than available
        with pytest.raises(BadRequestException) as exc_info:
            POSService.transfer_gift_card_balance(
                tenant_id="test_tenant",
                source_card="GC-SOURCE123",
                destination_card="GC-DEST456",
                amount=15000,  # More than balance
                transferred_by="user123"
            )
        
        assert "Insufficient balance" in str(exc_info.value)
    
    @patch('app.services.pos_service.Database.get_db')
    def test_transfer_source_card_not_found(self, mock_get_db, mock_db):
        """Test transfer fails when source card not found"""
        mock_get_db.return_value = mock_db
        mock_db.gift_cards.find_one.return_value = None
        
        with pytest.raises(NotFoundException) as exc_info:
            POSService.transfer_gift_card_balance(
                tenant_id="test_tenant",
                source_card="GC-INVALID",
                destination_card="GC-DEST456",
                amount=1000,
                transferred_by="user123"
            )
        
        assert "Source gift card not found" in str(exc_info.value)
    
    @patch('app.services.pos_service.Database.get_db')
    def test_transfer_destination_card_not_found(self, mock_get_db, mock_db, source_card_data):
        """Test transfer fails when destination card not found"""
        mock_get_db.return_value = mock_db
        mock_db.gift_cards.find_one.side_effect = [
            source_card_data,  # Source found
            None               # Destination not found
        ]
        
        with pytest.raises(NotFoundException) as exc_info:
            POSService.transfer_gift_card_balance(
                tenant_id="test_tenant",
                source_card="GC-SOURCE123",
                destination_card="GC-INVALID",
                amount=1000,
                transferred_by="user123"
            )
        
        assert "Destination gift card not found" in str(exc_info.value)
    
    @patch('app.services.pos_service.Database.get_db')
    def test_transfer_daily_limit_enforced(self, mock_get_db, mock_db, source_card_data):
        """Test daily transfer limit (1 per card per day)"""
        mock_get_db.return_value = mock_db
        
        # Add a transfer from today to source card
        today = datetime.now(timezone.utc)
        source_card_data["transactions"] = [
            {
                "type": "transfer_out",
                "amount": 1000,
                "timestamp": today,
                "balance_after": 9000
            }
        ]
        
        mock_db.gift_cards.find_one.return_value = source_card_data
        
        # Try to transfer again today
        with pytest.raises(BadRequestException) as exc_info:
            POSService.transfer_gift_card_balance(
                tenant_id="test_tenant",
                source_card="GC-SOURCE123",
                destination_card="GC-DEST456",
                amount=1000,
                transferred_by="user123"
            )
        
        assert "Daily transfer limit reached" in str(exc_info.value)
    
    @patch('app.services.pos_service.Database.get_db')
    def test_transfer_expired_card(self, mock_get_db, mock_db, source_card_data):
        """Test transfer fails with expired source card"""
        mock_get_db.return_value = mock_db
        
        # Set card as expired
        source_card_data["expires_at"] = datetime.now(timezone.utc) - timedelta(days=1)
        mock_db.gift_cards.find_one.return_value = source_card_data
        
        with pytest.raises(BadRequestException) as exc_info:
            POSService.transfer_gift_card_balance(
                tenant_id="test_tenant",
                source_card="GC-SOURCE123",
                destination_card="GC-DEST456",
                amount=1000,
                transferred_by="user123"
            )
        
        assert "expired" in str(exc_info.value).lower()
    
    @patch('app.services.pos_service.Database.get_db')
    def test_transfer_inactive_source_card(self, mock_get_db, mock_db, source_card_data):
        """Test transfer fails with inactive source card"""
        mock_get_db.return_value = mock_db
        
        source_card_data["status"] = "inactive"
        mock_db.gift_cards.find_one.return_value = source_card_data
        
        with pytest.raises(BadRequestException) as exc_info:
            POSService.transfer_gift_card_balance(
                tenant_id="test_tenant",
                source_card="GC-SOURCE123",
                destination_card="GC-DEST456",
                amount=1000,
                transferred_by="user123"
            )
        
        assert "inactive" in str(exc_info.value).lower()
    
    @patch('app.services.pos_service.Database.get_db')
    def test_transfer_zero_amount(self, mock_get_db, mock_db, source_card_data):
        """Test transfer fails with zero amount"""
        mock_get_db.return_value = mock_db
        mock_db.gift_cards.find_one.return_value = source_card_data
        
        with pytest.raises(BadRequestException) as exc_info:
            POSService.transfer_gift_card_balance(
                tenant_id="test_tenant",
                source_card="GC-SOURCE123",
                destination_card="GC-DEST456",
                amount=0,
                transferred_by="user123"
            )
        
        assert "must be greater than 0" in str(exc_info.value)
    
    @patch('app.services.pos_service.Database.get_db')
    def test_transfer_negative_amount(self, mock_get_db, mock_db, source_card_data):
        """Test transfer fails with negative amount"""
        mock_get_db.return_value = mock_db
        mock_db.gift_cards.find_one.return_value = source_card_data
        
        with pytest.raises(BadRequestException) as exc_info:
            POSService.transfer_gift_card_balance(
                tenant_id="test_tenant",
                source_card="GC-SOURCE123",
                destination_card="GC-DEST456",
                amount=-1000,
                transferred_by="user123"
            )
        
        assert "must be greater than 0" in str(exc_info.value)
    
    @patch('app.services.pos_service.Database.get_db')
    @patch('app.tasks.gift_card_tasks.send_transfer_confirmation_emails.delay')
    def test_transfer_audit_log_created(self, mock_email_task, mock_get_db, mock_db, source_card_data, dest_card_data):
        """Test that audit log entries are created for transfer"""
        mock_get_db.return_value = mock_db
        
        mock_db.gift_cards.find_one.side_effect = [
            source_card_data,
            dest_card_data,
            dest_card_data
        ]
        
        # Execute transfer
        POSService.transfer_gift_card_balance(
            tenant_id="test_tenant",
            source_card="GC-SOURCE123",
            destination_card="GC-DEST456",
            amount=5000,
            transferred_by="user123"
        )
        
        # Verify audit log was added to both cards
        update_calls = mock_db.gift_cards.update_one.call_args_list
        
        # Check source card update
        source_update = update_calls[0][0][1]
        assert "$push" in source_update
        assert "audit_log" in source_update["$push"]
        assert source_update["$push"]["audit_log"]["action"] == "transfer_out"
        
        # Check destination card update
        dest_update = update_calls[1][0][1]
        assert "$push" in dest_update
        assert "audit_log" in dest_update["$push"]
        assert dest_update["$push"]["audit_log"]["action"] == "transfer_in"
    
    @patch('app.services.pos_service.Database.get_db')
    @patch('app.tasks.gift_card_tasks.send_transfer_confirmation_emails.delay')
    def test_transfer_transactions_recorded(self, mock_email_task, mock_get_db, mock_db, source_card_data, dest_card_data):
        """Test that transactions are recorded for both cards"""
        mock_get_db.return_value = mock_db
        
        mock_db.gift_cards.find_one.side_effect = [
            source_card_data,
            dest_card_data,
            dest_card_data
        ]
        
        # Execute transfer
        POSService.transfer_gift_card_balance(
            tenant_id="test_tenant",
            source_card="GC-SOURCE123",
            destination_card="GC-DEST456",
            amount=3000,
            transferred_by="user123"
        )
        
        # Verify transactions were added
        update_calls = mock_db.gift_cards.update_one.call_args_list
        
        # Check source card transaction
        source_update = update_calls[0][0][1]
        assert "transactions" in source_update["$push"]
        source_txn = source_update["$push"]["transactions"]
        assert source_txn["type"] == "transfer_out"
        assert source_txn["amount"] == 3000
        assert source_txn["balance_after"] == 7000
        
        # Check destination card transaction
        dest_update = update_calls[1][0][1]
        assert "transactions" in dest_update["$push"]
        dest_txn = dest_update["$push"]["transactions"]
        assert dest_txn["type"] == "transfer_in"
        assert dest_txn["amount"] == 3000
        assert dest_txn["balance_after"] == 8000
    
    @patch('app.services.pos_service.Database.get_db')
    @patch('app.tasks.gift_card_tasks.send_transfer_confirmation_emails.delay')
    def test_transfer_source_card_status_updated_when_zero_balance(self, mock_email_task, mock_get_db, mock_db, source_card_data, dest_card_data):
        """Test source card status changes to 'redeemed' when balance reaches zero"""
        mock_get_db.return_value = mock_db
        
        mock_db.gift_cards.find_one.side_effect = [
            source_card_data,
            dest_card_data,
            dest_card_data
        ]
        
        # Transfer full balance
        POSService.transfer_gift_card_balance(
            tenant_id="test_tenant",
            source_card="GC-SOURCE123",
            destination_card="GC-DEST456",
            amount=10000,  # Full balance
            transferred_by="user123"
        )
        
        # Verify source card status updated to 'redeemed'
        source_update = mock_db.gift_cards.update_one.call_args_list[0][0][1]
        assert source_update["$set"]["status"] == "redeemed"
    
    @patch('app.services.pos_service.Database.get_db')
    @patch('app.tasks.gift_card_tasks.send_transfer_confirmation_emails.delay')
    def test_transfer_destination_card_activated(self, mock_email_task, mock_get_db, mock_db, source_card_data, dest_card_data):
        """Test destination card is activated if it was inactive"""
        mock_get_db.return_value = mock_db
        
        # Set destination card as inactive
        dest_card_data["status"] = "inactive"
        
        mock_db.gift_cards.find_one.side_effect = [
            source_card_data,
            dest_card_data,
            dest_card_data
        ]
        
        # Execute transfer
        POSService.transfer_gift_card_balance(
            tenant_id="test_tenant",
            source_card="GC-SOURCE123",
            destination_card="GC-DEST456",
            amount=1000,
            transferred_by="user123"
        )
        
        # Verify destination card status updated to 'active'
        dest_update = mock_db.gift_cards.update_one.call_args_list[1][0][1]
        assert dest_update["$set"]["status"] == "active"


class TestTransferConfirmationEmails:
    """Test transfer confirmation email functionality"""
    
    @pytest.mark.asyncio
    @patch('app.services.gift_card_email_service.email_service.send_email')
    @patch('app.services.gift_card_email_service.Database.get_db')
    async def test_send_transfer_confirmation_to_sender(self, mock_get_db, mock_send_email):
        """Test sending transfer confirmation email to sender"""
        from app.services.gift_card_email_service import GiftCardEmailService
        
        mock_send_email.return_value = True
        
        result = await GiftCardEmailService.send_transfer_confirmation_email(
            card_id="card123",
            card_number="GC-SOURCE123",
            recipient_email="sender@example.com",
            recipient_name="John Doe",
            transfer_type="sent",
            amount=5000,
            new_balance=5000,
            other_card_number="GC-DEST456"
        )
        
        assert result["success"] is True
        mock_send_email.assert_called_once()
        
        # Verify email content
        call_args = mock_send_email.call_args
        assert call_args[1]["to"] == "sender@example.com"
        assert "Transfer Confirmation" in call_args[1]["subject"]
        assert "Sent" in call_args[1]["subject"]
    
    @pytest.mark.asyncio
    @patch('app.services.gift_card_email_service.email_service.send_email')
    async def test_send_transfer_confirmation_to_receiver(self, mock_send_email):
        """Test sending transfer confirmation email to receiver"""
        from app.services.gift_card_email_service import GiftCardEmailService
        
        mock_send_email.return_value = True
        
        result = await GiftCardEmailService.send_transfer_confirmation_email(
            card_id="card456",
            card_number="GC-DEST456",
            recipient_email="receiver@example.com",
            recipient_name="Jane Smith",
            transfer_type="received",
            amount=5000,
            new_balance=10000,
            other_card_number="GC-SOURCE123"
        )
        
        assert result["success"] is True
        mock_send_email.assert_called_once()
        
        # Verify email content
        call_args = mock_send_email.call_args
        assert call_args[1]["to"] == "receiver@example.com"
        assert "Transfer Confirmation" in call_args[1]["subject"]
        assert "Received" in call_args[1]["subject"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
