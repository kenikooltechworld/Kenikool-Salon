"""
Tests for POS Gift Card Integration (Phase 7, Task 7.1)

Tests cover:
- Gift card as payment method
- Split payments (gift card + cash/card)
- Insufficient balance handling
- Receipt showing gift card details
- Remaining balance display
"""

import pytest
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from app.services.pos_service import POSService
from app.api.exceptions import NotFoundException, BadRequestException


class TestPOSGiftCardIntegration:
    """Test POS checkout integration with gift cards"""
    
    @pytest.fixture
    def tenant_id(self):
        """Test tenant ID"""
        return "test_tenant_123"
    
    @pytest.fixture
    def user_id(self):
        """Test user ID"""
        return "test_user_123"
    
    @pytest.fixture
    def active_gift_card(self, db, tenant_id):
        """Create an active gift card for testing"""
        card_data = {
            "tenant_id": tenant_id,
            "card_number": "GC-TEST12345678",
            "amount": 10000.0,
            "balance": 10000.0,
            "card_type": "digital",
            "status": "active",
            "recipient_email": "test@example.com",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "transactions": [],
            "audit_log": [],
            "security_flags": [],
            "suspicious_activity_count": 0,
            "balance_check_count_today": 0
        }
        result = db.gift_cards.insert_one(card_data)
        card_data["_id"] = result.inserted_id
        return card_data
    
    @pytest.fixture
    def low_balance_gift_card(self, db, tenant_id):
        """Create a gift card with low balance"""
        card_data = {
            "tenant_id": tenant_id,
            "card_number": "GC-LOWBALANCE123",
            "amount": 5000.0,
            "balance": 2000.0,
            "card_type": "digital",
            "status": "active",
            "recipient_email": "test@example.com",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "transactions": [],
            "audit_log": [],
            "security_flags": [],
            "suspicious_activity_count": 0,
            "balance_check_count_today": 0
        }
        result = db.gift_cards.insert_one(card_data)
        card_data["_id"] = result.inserted_id
        return card_data
    
    def test_gift_card_only_payment(self, db, tenant_id, user_id, active_gift_card):
        """Test paying with gift card only"""
        # Create transaction
        items = [
            {
                "type": "service",
                "item_id": "service_123",
                "item_name": "Haircut",
                "quantity": 1,
                "price": 5000.0
            }
        ]
        
        transaction = POSService.create_transaction(
            tenant_id=tenant_id,
            user_id=user_id,
            items=items
        )
        
        # Process payment with gift card
        payments = [
            {
                "method": "gift_card",
                "amount": 5000.0,
                "reference": active_gift_card["card_number"]
            }
        ]
        
        result = POSService.process_payment(
            transaction_id=transaction["id"],
            tenant_id=tenant_id,
            payments=payments
        )
        
        # Verify transaction completed
        assert result["status"] == "completed"
        assert result["payments"][0]["method"] == "gift_card"
        assert result["payments"][0]["amount"] == 5000.0
        
        # Verify gift card redemptions recorded
        assert "gift_card_redemptions" in result
        assert len(result["gift_card_redemptions"]) == 1
        assert result["gift_card_redemptions"][0]["card_number"] == active_gift_card["card_number"]
        assert result["gift_card_redemptions"][0]["amount"] == 5000.0
        assert result["gift_card_redemptions"][0]["remaining_balance"] == 5000.0
        
        # Verify gift card balance updated
        updated_card = db.gift_cards.find_one({"_id": active_gift_card["_id"]})
        assert updated_card["balance"] == 5000.0
        assert len(updated_card["transactions"]) == 1
        assert updated_card["transactions"][0]["type"] == "redeem"
        assert updated_card["transactions"][0]["amount"] == 5000.0
    
    def test_split_payment_gift_card_and_cash(self, db, tenant_id, user_id, active_gift_card):
        """Test split payment with gift card and cash"""
        # Create transaction for 12000
        items = [
            {
                "type": "service",
                "item_id": "service_123",
                "item_name": "Haircut + Color",
                "quantity": 1,
                "price": 12000.0
            }
        ]
        
        transaction = POSService.create_transaction(
            tenant_id=tenant_id,
            user_id=user_id,
            items=items
        )
        
        # Process payment: 10000 gift card + 2000 cash
        payments = [
            {
                "method": "gift_card",
                "amount": 10000.0,
                "reference": active_gift_card["card_number"]
            },
            {
                "method": "cash",
                "amount": 2000.0
            }
        ]
        
        result = POSService.process_payment(
            transaction_id=transaction["id"],
            tenant_id=tenant_id,
            payments=payments
        )
        
        # Verify transaction completed
        assert result["status"] == "completed"
        assert len(result["payments"]) == 2
        
        # Verify gift card fully redeemed
        assert result["gift_card_redemptions"][0]["remaining_balance"] == 0.0
        
        # Verify gift card status changed to redeemed
        updated_card = db.gift_cards.find_one({"_id": active_gift_card["_id"]})
        assert updated_card["balance"] == 0.0
        assert updated_card["status"] == "redeemed"
    
    def test_split_payment_multiple_gift_cards(self, db, tenant_id, user_id, active_gift_card, low_balance_gift_card):
        """Test split payment with multiple gift cards"""
        # Create transaction for 15000
        items = [
            {
                "type": "service",
                "item_id": "service_123",
                "item_name": "Premium Service",
                "quantity": 1,
                "price": 15000.0
            }
        ]
        
        transaction = POSService.create_transaction(
            tenant_id=tenant_id,
            user_id=user_id,
            items=items
        )
        
        # Process payment: 10000 + 2000 gift cards + 3000 cash
        payments = [
            {
                "method": "gift_card",
                "amount": 10000.0,
                "reference": active_gift_card["card_number"]
            },
            {
                "method": "gift_card",
                "amount": 2000.0,
                "reference": low_balance_gift_card["card_number"]
            },
            {
                "method": "cash",
                "amount": 3000.0
            }
        ]
        
        result = POSService.process_payment(
            transaction_id=transaction["id"],
            tenant_id=tenant_id,
            payments=payments
        )
        
        # Verify transaction completed
        assert result["status"] == "completed"
        assert len(result["gift_card_redemptions"]) == 2
        
        # Verify both gift cards redeemed
        assert result["gift_card_redemptions"][0]["remaining_balance"] == 0.0
        assert result["gift_card_redemptions"][1]["remaining_balance"] == 0.0
    
    def test_insufficient_gift_card_balance(self, db, tenant_id, user_id, low_balance_gift_card):
        """Test handling insufficient gift card balance"""
        # Create transaction for 5000
        items = [
            {
                "type": "service",
                "item_id": "service_123",
                "item_name": "Haircut",
                "quantity": 1,
                "price": 5000.0
            }
        ]
        
        transaction = POSService.create_transaction(
            tenant_id=tenant_id,
            user_id=user_id,
            items=items
        )
        
        # Try to pay 5000 with card that has only 2000
        payments = [
            {
                "method": "gift_card",
                "amount": 5000.0,
                "reference": low_balance_gift_card["card_number"]
            }
        ]
        
        # Should raise BadRequestException
        with pytest.raises(BadRequestException) as exc_info:
            POSService.process_payment(
                transaction_id=transaction["id"],
                tenant_id=tenant_id,
                payments=payments
            )
        
        assert "Insufficient balance" in str(exc_info.value)
        
        # Verify gift card balance unchanged
        card = db.gift_cards.find_one({"_id": low_balance_gift_card["_id"]})
        assert card["balance"] == 2000.0
    
    def test_invalid_gift_card_number(self, db, tenant_id, user_id):
        """Test handling invalid gift card number"""
        # Create transaction
        items = [
            {
                "type": "service",
                "item_id": "service_123",
                "item_name": "Haircut",
                "quantity": 1,
                "price": 5000.0
            }
        ]
        
        transaction = POSService.create_transaction(
            tenant_id=tenant_id,
            user_id=user_id,
            items=items
        )
        
        # Try to pay with invalid card
        payments = [
            {
                "method": "gift_card",
                "amount": 5000.0,
                "reference": "GC-INVALID12345"
            }
        ]
        
        # Should raise NotFoundException
        with pytest.raises(NotFoundException) as exc_info:
            POSService.process_payment(
                transaction_id=transaction["id"],
                tenant_id=tenant_id,
                payments=payments
            )
        
        assert "Gift card not found" in str(exc_info.value)
    
    def test_expired_gift_card(self, db, tenant_id, user_id):
        """Test handling expired gift card"""
        # Create expired gift card
        expired_card = {
            "tenant_id": tenant_id,
            "card_number": "GC-EXPIRED12345",
            "amount": 10000.0,
            "balance": 10000.0,
            "card_type": "digital",
            "status": "active",
            "recipient_email": "test@example.com",
            "created_at": datetime.now(timezone.utc) - timedelta(days=400),
            "expires_at": datetime.now(timezone.utc) - timedelta(days=30),
            "transactions": [],
            "audit_log": [],
            "security_flags": [],
            "suspicious_activity_count": 0,
            "balance_check_count_today": 0
        }
        result = db.gift_cards.insert_one(expired_card)
        expired_card["_id"] = result.inserted_id
        
        # Create transaction
        items = [
            {
                "type": "service",
                "item_id": "service_123",
                "item_name": "Haircut",
                "quantity": 1,
                "price": 5000.0
            }
        ]
        
        transaction = POSService.create_transaction(
            tenant_id=tenant_id,
            user_id=user_id,
            items=items
        )
        
        # Try to pay with expired card
        payments = [
            {
                "method": "gift_card",
                "amount": 5000.0,
                "reference": expired_card["card_number"]
            }
        ]
        
        # Should raise BadRequestException
        with pytest.raises(BadRequestException) as exc_info:
            POSService.process_payment(
                transaction_id=transaction["id"],
                tenant_id=tenant_id,
                payments=payments
            )
        
        assert "expired" in str(exc_info.value).lower()
        
        # Verify card status updated to expired
        card = db.gift_cards.find_one({"_id": expired_card["_id"]})
        assert card["status"] == "expired"
    
    def test_suspended_gift_card(self, db, tenant_id, user_id):
        """Test handling suspended gift card"""
        # Create suspended gift card
        suspended_card = {
            "tenant_id": tenant_id,
            "card_number": "GC-SUSPENDED123",
            "amount": 10000.0,
            "balance": 10000.0,
            "card_type": "digital",
            "status": "suspended",
            "recipient_email": "test@example.com",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "transactions": [],
            "audit_log": [],
            "security_flags": ["fraud_suspected"],
            "suspicious_activity_count": 5,
            "balance_check_count_today": 0
        }
        result = db.gift_cards.insert_one(suspended_card)
        suspended_card["_id"] = result.inserted_id
        
        # Create transaction
        items = [
            {
                "type": "service",
                "item_id": "service_123",
                "item_name": "Haircut",
                "quantity": 1,
                "price": 5000.0
            }
        ]
        
        transaction = POSService.create_transaction(
            tenant_id=tenant_id,
            user_id=user_id,
            items=items
        )
        
        # Try to pay with suspended card
        payments = [
            {
                "method": "gift_card",
                "amount": 5000.0,
                "reference": suspended_card["card_number"]
            }
        ]
        
        # Should raise BadRequestException
        with pytest.raises(BadRequestException) as exc_info:
            POSService.process_payment(
                transaction_id=transaction["id"],
                tenant_id=tenant_id,
                payments=payments
            )
        
        assert "suspended" in str(exc_info.value).lower()
    
    def test_gift_card_audit_trail(self, db, tenant_id, user_id, active_gift_card):
        """Test that gift card redemption creates proper audit trail"""
        # Create and process transaction
        items = [
            {
                "type": "service",
                "item_id": "service_123",
                "item_name": "Haircut",
                "quantity": 1,
                "price": 5000.0
            }
        ]
        
        transaction = POSService.create_transaction(
            tenant_id=tenant_id,
            user_id=user_id,
            items=items
        )
        
        payments = [
            {
                "method": "gift_card",
                "amount": 5000.0,
                "reference": active_gift_card["card_number"]
            }
        ]
        
        POSService.process_payment(
            transaction_id=transaction["id"],
            tenant_id=tenant_id,
            payments=payments
        )
        
        # Verify audit log created
        updated_card = db.gift_cards.find_one({"_id": active_gift_card["_id"]})
        assert len(updated_card["audit_log"]) > 0
        
        # Find redemption audit entry
        redemption_audit = next(
            (log for log in updated_card["audit_log"] if log["action"] == "redeemed"),
            None
        )
        assert redemption_audit is not None
        assert redemption_audit["details"]["amount"] == 5000.0
        assert redemption_audit["details"]["transaction_id"] == transaction["id"]
    
    def test_receipt_shows_gift_card_details(self, db, tenant_id, user_id, active_gift_card):
        """Test that receipt includes gift card details and remaining balance"""
        # Create and process transaction
        items = [
            {
                "type": "service",
                "item_id": "service_123",
                "item_name": "Haircut",
                "quantity": 1,
                "price": 5000.0
            }
        ]
        
        transaction = POSService.create_transaction(
            tenant_id=tenant_id,
            user_id=user_id,
            items=items
        )
        
        payments = [
            {
                "method": "gift_card",
                "amount": 5000.0,
                "reference": active_gift_card["card_number"]
            }
        ]
        
        result = POSService.process_payment(
            transaction_id=transaction["id"],
            tenant_id=tenant_id,
            payments=payments
        )
        
        # Verify receipt data includes gift card info
        assert "gift_card_redemptions" in result
        redemption = result["gift_card_redemptions"][0]
        
        # Verify all required fields for receipt
        assert "card_number" in redemption
        assert "amount" in redemption
        assert "remaining_balance" in redemption
        
        # Verify values
        assert redemption["card_number"] == active_gift_card["card_number"]
        assert redemption["amount"] == 5000.0
        assert redemption["remaining_balance"] == 5000.0
    
    def test_rollback_on_payment_failure(self, db, tenant_id, user_id, active_gift_card):
        """Test that gift card redemption is rolled back if payment fails"""
        # Create transaction
        items = [
            {
                "type": "service",
                "item_id": "service_123",
                "item_name": "Haircut",
                "quantity": 1,
                "price": 5000.0
            }
        ]
        
        transaction = POSService.create_transaction(
            tenant_id=tenant_id,
            user_id=user_id,
            items=items
        )
        
        # Try to pay with valid gift card but insufficient total payment
        payments = [
            {
                "method": "gift_card",
                "amount": 3000.0,
                "reference": active_gift_card["card_number"]
            }
            # Missing 2000 - should fail
        ]
        
        # Should raise BadRequestException
        with pytest.raises(BadRequestException):
            POSService.process_payment(
                transaction_id=transaction["id"],
                tenant_id=tenant_id,
                payments=payments
            )
        
        # Verify gift card balance unchanged (rollback successful)
        card = db.gift_cards.find_one({"_id": active_gift_card["_id"]})
        assert card["balance"] == 10000.0
        assert len(card["transactions"]) == 0  # No redemption recorded
