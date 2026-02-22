"""
Tests for booking checkout with gift card integration
"""
import pytest
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from unittest.mock import patch, MagicMock

from app.database import Database
from app.services.pos_service import POSService
from app.api.exceptions import NotFoundException, BadRequestException


@pytest.fixture
def db():
    """Get database instance"""
    return Database.get_db()


class TestBookingGiftCardIntegration:
    """Test suite for booking checkout with gift cards"""
    
    @pytest.fixture
    def tenant_id(self):
        """Fixture for tenant ID"""
        return str(ObjectId())
    
    @pytest.fixture
    def user_id(self):
        """Fixture for user ID"""
        return str(ObjectId())
    
    @pytest.fixture
    def client_id(self):
        """Fixture for client ID"""
        return str(ObjectId())
    
    @pytest.fixture
    def service_id(self):
        """Fixture for service ID"""
        return str(ObjectId())
    
    @pytest.fixture
    def stylist_id(self):
        """Fixture for stylist ID"""
        return str(ObjectId())
    
    @pytest.fixture
    def booking(self, db, tenant_id, client_id, service_id, stylist_id):
        """Fixture for test booking"""
        booking_data = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "service": {
                "id": service_id,
                "name": "Haircut",
                "price": 10000
            },
            "stylist_id": stylist_id,
            "booking_date": datetime.now(timezone.utc) + timedelta(days=1),
            "status": "confirmed",
            "payment_status": "pending",
            "deposit_amount": 0,
            "created_at": datetime.now(timezone.utc)
        }
        result = db.bookings.insert_one(booking_data)
        booking_data["_id"] = result.inserted_id
        booking_data["id"] = str(result.inserted_id)
        return booking_data
    
    @pytest.fixture
    def active_gift_card(self, db, tenant_id):
        """Fixture for active gift card with sufficient balance"""
        card_data = {
            "tenant_id": tenant_id,
            "card_number": "GC-TEST123456",
            "amount": 15000,
            "balance": 15000,
            "status": "active",
            "card_type": "digital",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "created_at": datetime.now(timezone.utc),
            "transactions": []
        }
        result = db.gift_cards.insert_one(card_data)
        card_data["_id"] = result.inserted_id
        return card_data
    
    @pytest.fixture
    def low_balance_gift_card(self, db, tenant_id):
        """Fixture for gift card with low balance"""
        card_data = {
            "tenant_id": tenant_id,
            "card_number": "GC-LOWBAL123",
            "amount": 5000,
            "balance": 3000,
            "status": "active",
            "card_type": "digital",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "created_at": datetime.now(timezone.utc),
            "transactions": []
        }
        result = db.gift_cards.insert_one(card_data)
        card_data["_id"] = result.inserted_id
        return card_data
    
    def test_checkout_with_single_gift_card(self, db, tenant_id, booking, active_gift_card):
        """Test booking checkout with single gift card payment"""
        # Arrange
        booking_id = str(booking["_id"])
        payment_methods = [
            {
                "method": "gift_card",
                "amount": 10000,
                "gift_card_code": active_gift_card["card_number"]
            }
        ]
        
        # Act
        from app.api.payments import process_booking_checkout
        result = process_booking_checkout(
            request={
                "booking_id": booking_id,
                "payment_methods": payment_methods
            },
            tenant_id=tenant_id,
            user={"id": "test_user"}
        )
        
        # Assert
        assert result["status"] == "success"
        assert result["total_paid"] == 10000
        assert len(result["gift_card_redemptions"]) == 1
        assert result["gift_card_redemptions"][0]["card_number"] == active_gift_card["card_number"]
        assert result["gift_card_redemptions"][0]["amount"] == 10000
        assert result["gift_card_redemptions"][0]["remaining_balance"] == 5000
        
        # Verify booking updated
        updated_booking = db.bookings.find_one({"_id": booking["_id"]})
        assert updated_booking["payment_status"] == "paid"
        assert "gift_card_redemptions" in updated_booking
        
        # Verify gift card balance updated
        updated_card = db.gift_cards.find_one({"_id": active_gift_card["_id"]})
        assert updated_card["balance"] == 5000
    
    def test_checkout_with_multiple_gift_cards(self, db, tenant_id, booking):
        """Test booking checkout with multiple gift cards"""
        # Arrange
        card1 = {
            "tenant_id": tenant_id,
            "card_number": "GC-CARD1",
            "amount": 5000,
            "balance": 5000,
            "status": "active",
            "card_type": "digital",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "created_at": datetime.now(timezone.utc),
            "transactions": []
        }
        card2 = {
            "tenant_id": tenant_id,
            "card_number": "GC-CARD2",
            "amount": 6000,
            "balance": 6000,
            "status": "active",
            "card_type": "digital",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "created_at": datetime.now(timezone.utc),
            "transactions": []
        }
        db.gift_cards.insert_one(card1)
        db.gift_cards.insert_one(card2)
        
        booking_id = str(booking["_id"])
        payment_methods = [
            {
                "method": "gift_card",
                "amount": 5000,
                "gift_card_code": "GC-CARD1"
            },
            {
                "method": "gift_card",
                "amount": 5000,
                "gift_card_code": "GC-CARD2"
            }
        ]
        
        # Act
        from app.api.payments import process_booking_checkout
        result = process_booking_checkout(
            request={
                "booking_id": booking_id,
                "payment_methods": payment_methods
            },
            tenant_id=tenant_id,
            user={"id": "test_user"}
        )
        
        # Assert
        assert result["status"] == "success"
        assert result["total_paid"] == 10000
        assert len(result["gift_card_redemptions"]) == 2
        
        # Verify both cards updated
        updated_card1 = db.gift_cards.find_one({"card_number": "GC-CARD1"})
        assert updated_card1["balance"] == 0
        
        updated_card2 = db.gift_cards.find_one({"card_number": "GC-CARD2"})
        assert updated_card2["balance"] == 1000
    
    def test_checkout_with_gift_card_and_cash(self, db, tenant_id, booking, low_balance_gift_card):
        """Test booking checkout with gift card + cash split payment"""
        # Arrange
        booking_id = str(booking["_id"])
        payment_methods = [
            {
                "method": "gift_card",
                "amount": 3000,
                "gift_card_code": low_balance_gift_card["card_number"]
            },
            {
                "method": "cash",
                "amount": 7000
            }
        ]
        
        # Act
        from app.api.payments import process_booking_checkout
        result = process_booking_checkout(
            request={
                "booking_id": booking_id,
                "payment_methods": payment_methods
            },
            tenant_id=tenant_id,
            user={"id": "test_user"}
        )
        
        # Assert
        assert result["status"] == "success"
        assert result["total_paid"] == 10000
        assert len(result["gift_card_redemptions"]) == 1
        
        # Verify gift card fully redeemed
        updated_card = db.gift_cards.find_one({"_id": low_balance_gift_card["_id"]})
        assert updated_card["balance"] == 0
    
    def test_checkout_with_invalid_gift_card(self, db, tenant_id, booking):
        """Test booking checkout with invalid gift card number"""
        # Arrange
        booking_id = str(booking["_id"])
        payment_methods = [
            {
                "method": "gift_card",
                "amount": 10000,
                "gift_card_code": "GC-INVALID"
            }
        ]
        
        # Act & Assert
        from app.api.payments import process_booking_checkout
        with pytest.raises(BadRequestException) as exc_info:
            process_booking_checkout(
                request={
                    "booking_id": booking_id,
                    "payment_methods": payment_methods
                },
                tenant_id=tenant_id,
                user={"id": "test_user"}
            )
        
        assert "Gift card payment failed" in str(exc_info.value)
    
    def test_checkout_with_insufficient_gift_card_balance(self, db, tenant_id, booking, low_balance_gift_card):
        """Test booking checkout with insufficient gift card balance"""
        # Arrange
        booking_id = str(booking["_id"])
        payment_methods = [
            {
                "method": "gift_card",
                "amount": 5000,  # More than available balance (3000)
                "gift_card_code": low_balance_gift_card["card_number"]
            }
        ]
        
        # Act & Assert
        from app.api.payments import process_booking_checkout
        with pytest.raises(BadRequestException) as exc_info:
            process_booking_checkout(
                request={
                    "booking_id": booking_id,
                    "payment_methods": payment_methods
                },
                tenant_id=tenant_id,
                user={"id": "test_user"}
            )
        
        assert "Gift card payment failed" in str(exc_info.value)
        
        # Verify gift card balance unchanged
        card = db.gift_cards.find_one({"_id": low_balance_gift_card["_id"]})
        assert card["balance"] == 3000
    
    def test_checkout_with_expired_gift_card(self, db, tenant_id, booking):
        """Test booking checkout with expired gift card"""
        # Arrange
        expired_card = {
            "tenant_id": tenant_id,
            "card_number": "GC-EXPIRED",
            "amount": 10000,
            "balance": 10000,
            "status": "active",
            "card_type": "digital",
            "expires_at": datetime.now(timezone.utc) - timedelta(days=1),  # Expired
            "created_at": datetime.now(timezone.utc) - timedelta(days=365),
            "transactions": []
        }
        db.gift_cards.insert_one(expired_card)
        
        booking_id = str(booking["_id"])
        payment_methods = [
            {
                "method": "gift_card",
                "amount": 10000,
                "gift_card_code": "GC-EXPIRED"
            }
        ]
        
        # Act & Assert
        from app.api.payments import process_booking_checkout
        with pytest.raises(BadRequestException) as exc_info:
            process_booking_checkout(
                request={
                    "booking_id": booking_id,
                    "payment_methods": payment_methods
                },
                tenant_id=tenant_id,
                user={"id": "test_user"}
            )
        
        assert "Gift card payment failed" in str(exc_info.value)
    
    def test_checkout_with_insufficient_total_payment(self, db, tenant_id, booking, active_gift_card):
        """Test booking checkout with insufficient total payment amount"""
        # Arrange
        booking_id = str(booking["_id"])
        payment_methods = [
            {
                "method": "gift_card",
                "amount": 5000,  # Less than required 10000
                "gift_card_code": active_gift_card["card_number"]
            }
        ]
        
        # Act & Assert
        from app.api.payments import process_booking_checkout
        with pytest.raises(BadRequestException) as exc_info:
            process_booking_checkout(
                request={
                    "booking_id": booking_id,
                    "payment_methods": payment_methods
                },
                tenant_id=tenant_id,
                user={"id": "test_user"}
            )
        
        assert "Insufficient payment" in str(exc_info.value)
        
        # Verify gift card balance unchanged (rollback)
        card = db.gift_cards.find_one({"_id": active_gift_card["_id"]})
        assert card["balance"] == 15000
    
    def test_checkout_with_booking_not_found(self, db, tenant_id):
        """Test booking checkout with non-existent booking"""
        # Arrange
        fake_booking_id = str(ObjectId())
        payment_methods = [
            {
                "method": "cash",
                "amount": 10000
            }
        ]
        
        # Act & Assert
        from app.api.payments import process_booking_checkout
        with pytest.raises(NotFoundException) as exc_info:
            process_booking_checkout(
                request={
                    "booking_id": fake_booking_id,
                    "payment_methods": payment_methods
                },
                tenant_id=tenant_id,
                user={"id": "test_user"}
            )
        
        assert "Booking not found" in str(exc_info.value)
    
    def test_checkout_without_payment_methods(self, db, tenant_id, booking):
        """Test booking checkout without payment methods"""
        # Arrange
        booking_id = str(booking["_id"])
        
        # Act & Assert
        from app.api.payments import process_booking_checkout
        with pytest.raises(BadRequestException) as exc_info:
            process_booking_checkout(
                request={
                    "booking_id": booking_id,
                    "payment_methods": []
                },
                tenant_id=tenant_id,
                user={"id": "test_user"}
            )
        
        assert "At least one payment method is required" in str(exc_info.value)
    
    def test_checkout_gift_card_rollback_on_failure(self, db, tenant_id, booking):
        """Test that gift card redemptions are rolled back if checkout fails"""
        # Arrange
        card1 = {
            "tenant_id": tenant_id,
            "card_number": "GC-ROLLBACK1",
            "amount": 5000,
            "balance": 5000,
            "status": "active",
            "card_type": "digital",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "created_at": datetime.now(timezone.utc),
            "transactions": []
        }
        result1 = db.gift_cards.insert_one(card1)
        card1["_id"] = result1.inserted_id
        
        booking_id = str(booking["_id"])
        payment_methods = [
            {
                "method": "gift_card",
                "amount": 5000,
                "gift_card_code": "GC-ROLLBACK1"
            },
            {
                "method": "gift_card",
                "amount": 5000,
                "gift_card_code": "GC-INVALID"  # This will fail
            }
        ]
        
        # Act & Assert
        from app.api.payments import process_booking_checkout
        with pytest.raises(BadRequestException):
            process_booking_checkout(
                request={
                    "booking_id": booking_id,
                    "payment_methods": payment_methods
                },
                tenant_id=tenant_id,
                user={"id": "test_user"}
            )
        
        # Verify first card was rolled back
        card = db.gift_cards.find_one({"_id": card1["_id"]})
        assert card["balance"] == 5000  # Balance restored
        
        # Verify refund transaction recorded
        assert len(card["transactions"]) == 1
        assert card["transactions"][0]["type"] == "refund"
        assert card["transactions"][0]["reason"] == "payment_failed"
    
    def test_checkout_creates_payment_record(self, db, tenant_id, booking, active_gift_card):
        """Test that checkout creates a payment record"""
        # Arrange
        booking_id = str(booking["_id"])
        payment_methods = [
            {
                "method": "gift_card",
                "amount": 10000,
                "gift_card_code": active_gift_card["card_number"]
            }
        ]
        
        # Act
        from app.api.payments import process_booking_checkout
        result = process_booking_checkout(
            request={
                "booking_id": booking_id,
                "payment_methods": payment_methods
            },
            tenant_id=tenant_id,
            user={"id": "test_user"}
        )
        
        # Assert
        payment_id = result["payment_id"]
        payment = db.payments.find_one({"_id": ObjectId(payment_id)})
        
        assert payment is not None
        assert payment["booking_id"] == booking_id
        assert payment["amount"] == 10000
        assert payment["status"] == "completed"
        assert len(payment["gift_card_redemptions"]) == 1
    
    def test_checkout_with_deposit_already_paid(self, db, tenant_id, booking, active_gift_card):
        """Test booking checkout when deposit was already paid"""
        # Arrange
        # Update booking with deposit
        db.bookings.update_one(
            {"_id": booking["_id"]},
            {"$set": {"deposit_amount": 3000}}
        )
        
        booking_id = str(booking["_id"])
        # Only need to pay remaining balance (10000 - 3000 = 7000)
        payment_methods = [
            {
                "method": "gift_card",
                "amount": 7000,
                "gift_card_code": active_gift_card["card_number"]
            }
        ]
        
        # Act
        from app.api.payments import process_booking_checkout
        result = process_booking_checkout(
            request={
                "booking_id": booking_id,
                "payment_methods": payment_methods
            },
            tenant_id=tenant_id,
            user={"id": "test_user"}
        )
        
        # Assert
        assert result["status"] == "success"
        assert result["total_paid"] == 7000
        
        # Verify gift card balance
        updated_card = db.gift_cards.find_one({"_id": active_gift_card["_id"]})
        assert updated_card["balance"] == 8000  # 15000 - 7000
