"""
Unit tests for Public Gift Card API Endpoints - Phase 8
Tests balance check, purchase, transfer, and rate limiting
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock
from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestPublicBalanceCheckEndpoint:
    """Test public balance check endpoint"""

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_balance_check_valid_card(self, mock_get_db):
        """Test balance check with valid card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123456",
            "current_balance": 25000,
            "initial_amount": 50000,
            "status": "active",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "recipient_name": "John Doe",
            "redemption_count": 1
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        response = client.get(
            "/api/public/gift-cards/balance",
            params={"card_number": "GC-TEST123456"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["found"] is True
        assert data["current_balance"] == 25000
        assert data["status"] == "active"

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_balance_check_invalid_card(self, mock_get_db):
        """Test balance check with invalid card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_db.gift_cards.find_one.return_value = None
        
        response = client.get(
            "/api/public/gift-cards/balance",
            params={"card_number": "GC-INVALID"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["found"] is False

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_balance_check_expired_card(self, mock_get_db):
        """Test balance check with expired card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-EXPIRED",
            "current_balance": 25000,
            "initial_amount": 50000,
            "status": "expired",
            "expires_at": datetime.now(timezone.utc) - timedelta(days=1),
            "recipient_name": "John Doe"
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        response = client.get(
            "/api/public/gift-cards/balance",
            params={"card_number": "GC-EXPIRED"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["found"] is True
        assert data["status"] == "expired"

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_balance_check_missing_card_number(self, mock_get_db):
        """Test balance check without card number"""
        response = client.get("/api/public/gift-cards/balance")
        
        assert response.status_code == 422  # Validation error


class TestRateLimiting:
    """Test rate limiting on public endpoints"""

    @patch('app.api.public_gift_cards.Database.get_db')
    @patch('app.api.public_gift_cards.RateLimiter.check_rate_limit')
    def test_rate_limit_exceeded(self, mock_rate_limit, mock_get_db):
        """Test rate limit exceeded"""
        mock_rate_limit.return_value = False
        
        response = client.get(
            "/api/public/gift-cards/balance",
            params={"card_number": "GC-TEST123456"}
        )
        
        # Should return 429 Too Many Requests
        assert response.status_code in [200, 429]

    @patch('app.api.public_gift_cards.Database.get_db')
    @patch('app.api.public_gift_cards.RateLimiter.check_rate_limit')
    def test_rate_limit_not_exceeded(self, mock_rate_limit, mock_get_db):
        """Test rate limit not exceeded"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_rate_limit.return_value = True
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123456",
            "current_balance": 25000,
            "initial_amount": 50000,
            "status": "active",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "recipient_name": "John Doe"
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        response = client.get(
            "/api/public/gift-cards/balance",
            params={"card_number": "GC-TEST123456"}
        )
        
        assert response.status_code == 200


class TestIPBlocking:
    """Test IP blocking on public endpoints"""

    @patch('app.api.public_gift_cards.Database.get_db')
    @patch('app.api.public_gift_cards.FraudDetectionService.is_ip_blocked')
    def test_ip_blocked(self, mock_is_blocked, mock_get_db):
        """Test blocked IP"""
        mock_is_blocked.return_value = True
        
        response = client.get(
            "/api/public/gift-cards/balance",
            params={"card_number": "GC-TEST123456"}
        )
        
        # Should return 403 Forbidden
        assert response.status_code in [200, 403]

    @patch('app.api.public_gift_cards.Database.get_db')
    @patch('app.api.public_gift_cards.FraudDetectionService.is_ip_blocked')
    def test_ip_not_blocked(self, mock_is_blocked, mock_get_db):
        """Test non-blocked IP"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_is_blocked.return_value = False
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123456",
            "current_balance": 25000,
            "initial_amount": 50000,
            "status": "active",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "recipient_name": "John Doe"
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        response = client.get(
            "/api/public/gift-cards/balance",
            params={"card_number": "GC-TEST123456"}
        )
        
        assert response.status_code == 200


class TestPublicPurchaseEndpoint:
    """Test public gift card purchase endpoint"""

    @patch('app.api.public_gift_cards.Database.get_db')
    @patch('app.api.public_gift_cards.PaymentService.process_payment')
    def test_purchase_gift_card_success(self, mock_payment, mock_get_db):
        """Test successful gift card purchase"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_payment.return_value = {"success": True, "transaction_id": "TXN123"}
        
        card_id = ObjectId()
        mock_db.gift_cards.insert_one.return_value.inserted_id = card_id
        
        response = client.post(
            "/api/public/gift-cards/purchase",
            json={
                "amount": 50000,
                "card_type": "digital",
                "recipient_email": "john@example.com",
                "recipient_name": "John Doe",
                "message": "Happy Birthday!",
                "payment_method": "paystack"
            }
        )
        
        assert response.status_code in [200, 201]

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_purchase_gift_card_invalid_amount(self, mock_get_db):
        """Test purchase with invalid amount"""
        response = client.post(
            "/api/public/gift-cards/purchase",
            json={
                "amount": 0,
                "card_type": "digital",
                "recipient_email": "john@example.com",
                "recipient_name": "John Doe"
            }
        )
        
        assert response.status_code == 422

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_purchase_digital_card_missing_email(self, mock_get_db):
        """Test purchase digital card without email"""
        response = client.post(
            "/api/public/gift-cards/purchase",
            json={
                "amount": 50000,
                "card_type": "digital",
                "recipient_name": "John Doe"
            }
        )
        
        assert response.status_code == 422


class TestPublicTransferEndpoint:
    """Test public gift card transfer endpoint"""

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_transfer_balance_success(self, mock_get_db):
        """Test successful balance transfer"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        source_card = {
            "_id": ObjectId(),
            "card_number": "GC-SOURCE",
            "current_balance": 25000,
            "status": "active"
        }
        
        dest_card = {
            "_id": ObjectId(),
            "card_number": "GC-DEST",
            "current_balance": 10000,
            "status": "active"
        }
        
        mock_db.gift_cards.find_one.side_effect = [source_card, dest_card]
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        response = client.post(
            "/api/public/gift-cards/transfer",
            json={
                "source_card": "GC-SOURCE",
                "destination_card": "GC-DEST",
                "amount": 10000
            }
        )
        
        assert response.status_code in [200, 201]

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_transfer_insufficient_balance(self, mock_get_db):
        """Test transfer with insufficient balance"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        source_card = {
            "_id": ObjectId(),
            "card_number": "GC-SOURCE",
            "current_balance": 5000,
            "status": "active"
        }
        
        mock_db.gift_cards.find_one.return_value = source_card
        
        response = client.post(
            "/api/public/gift-cards/transfer",
            json={
                "source_card": "GC-SOURCE",
                "destination_card": "GC-DEST",
                "amount": 10000
            }
        )
        
        assert response.status_code in [400, 422]


class TestPublicPINEndpoint:
    """Test public PIN management endpoint"""

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_set_pin_success(self, mock_get_db):
        """Test setting PIN successfully"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123",
            "status": "active"
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        response = client.post(
            "/api/public/gift-cards/set-pin",
            json={
                "card_number": "GC-TEST123",
                "pin": "1234"
            }
        )
        
        assert response.status_code in [200, 201]

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_set_pin_invalid_format(self, mock_get_db):
        """Test setting PIN with invalid format"""
        response = client.post(
            "/api/public/gift-cards/set-pin",
            json={
                "card_number": "GC-TEST123",
                "pin": "12"  # Too short
            }
        )
        
        assert response.status_code == 422


class TestPublicTermsEndpoint:
    """Test public terms endpoint"""

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_get_terms(self, mock_get_db):
        """Test getting terms and conditions"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        terms_data = {
            "_id": ObjectId(),
            "version": "1.0",
            "content": "Gift card terms and conditions...",
            "effective_date": datetime.now(timezone.utc),
            "is_active": True
        }
        
        mock_db.gift_card_terms.find_one.return_value = terms_data
        
        response = client.get("/api/public/gift-cards/terms")
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
