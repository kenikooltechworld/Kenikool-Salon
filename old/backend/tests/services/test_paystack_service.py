"""
Tests for Paystack service.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.paystack_service import PaystackService


@pytest.fixture
def paystack_service():
    """Create a Paystack service instance for testing"""
    return PaystackService()


class TestPaystackService:
    """Test cases for PaystackService"""

    @patch("app.services.paystack_service.requests.post")
    async def test_initialize_transaction_success(self, mock_post, paystack_service):
        """Test successful transaction initialization"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "authorization_url": "https://checkout.paystack.com/...",
                "access_code": "access_code_123",
                "reference": "ref_123",
            },
        }
        mock_post.return_value = mock_response

        result = await paystack_service.initialize_transaction(
            email="test@example.com",
            amount=100.00,
            reference="ref_123",
        )

        assert result["authorization_url"] is not None
        assert result["access_code"] == "access_code_123"
        mock_post.assert_called_once()

    @patch("app.services.paystack_service.requests.post")
    async def test_initialize_transaction_failure(self, mock_post, paystack_service):
        """Test transaction initialization failure"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": False,
            "message": "Invalid email",
        }
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            await paystack_service.initialize_transaction(
                email="invalid",
                amount=100.00,
                reference="ref_123",
            )

        assert "Paystack error" in str(exc_info.value)

    @patch("app.services.paystack_service.requests.post")
    async def test_charge_authorization_success(self, mock_post, paystack_service):
        """Test successful authorization charge"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Charge successful",
            "data": {
                "reference": "ref_456",
                "amount": 10000,  # 100.00 in kobo
                "status": "success",
                "customer": {"email": "test@example.com"},
            },
        }
        mock_post.return_value = mock_response

        result = await paystack_service.charge_authorization(
            authorization_code="auth_code_123",
            email="test@example.com",
            amount=100.00,
            reference="ref_456",
        )

        assert result["status"] == "success"
        assert result["amount"] == 10000
        mock_post.assert_called_once()

    @patch("app.services.paystack_service.requests.post")
    async def test_charge_authorization_failure(self, mock_post, paystack_service):
        """Test authorization charge failure"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": False,
            "message": "Invalid authorization code",
        }
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            await paystack_service.charge_authorization(
                authorization_code="invalid_auth",
                email="test@example.com",
                amount=100.00,
                reference="ref_456",
            )

        assert "Paystack error" in str(exc_info.value)

    @patch("app.services.paystack_service.requests.get")
    async def test_verify_transaction_success(self, mock_get, paystack_service):
        """Test successful transaction verification"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Verification successful",
            "data": {
                "reference": "ref_123",
                "amount": 10000,
                "status": "success",
                "customer": {"email": "test@example.com"},
            },
        }
        mock_get.return_value = mock_response

        result = await paystack_service.verify_transaction(reference="ref_123")

        assert result["status"] == "success"
        assert result["reference"] == "ref_123"
        mock_get.assert_called_once()

    @patch("app.services.paystack_service.requests.get")
    async def test_verify_transaction_failure(self, mock_get, paystack_service):
        """Test transaction verification failure"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": False,
            "message": "Reference not found",
        }
        mock_get.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            await paystack_service.verify_transaction(reference="invalid_ref")

        assert "Paystack error" in str(exc_info.value)

    @patch("app.services.paystack_service.requests.get")
    async def test_get_customer_success(self, mock_get, paystack_service):
        """Test successful customer retrieval"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Customer retrieved",
            "data": {
                "id": 123,
                "customer_code": "CUS_123",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
        }
        mock_get.return_value = mock_response

        result = await paystack_service.get_customer(customer_code="CUS_123")

        assert result["email"] == "test@example.com"
        assert result["customer_code"] == "CUS_123"
        mock_get.assert_called_once()

    @patch("app.services.paystack_service.requests.post")
    async def test_create_customer_success(self, mock_post, paystack_service):
        """Test successful customer creation"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Customer created",
            "data": {
                "id": 123,
                "customer_code": "CUS_123",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
        }
        mock_post.return_value = mock_response

        result = await paystack_service.create_customer(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )

        assert result["email"] == "test@example.com"
        assert result["customer_code"] == "CUS_123"
        mock_post.assert_called_once()

    @patch("app.services.paystack_service.requests.post")
    async def test_deactivate_authorization_success(self, mock_post, paystack_service):
        """Test successful authorization deactivation"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Authorization deactivated",
            "data": {
                "authorization_code": "auth_code_123",
                "status": "deactivated",
            },
        }
        mock_post.return_value = mock_response

        result = await paystack_service.deactivate_authorization(
            authorization_code="auth_code_123",
            email="test@example.com",
        )

        assert result["status"] == "deactivated"
        mock_post.assert_called_once()

    def test_verify_webhook_signature_valid(self, paystack_service):
        """Test valid webhook signature verification"""
        import hmac
        import hashlib

        payload = b'{"event":"charge.success"}'
        hash_object = hmac.new(
            paystack_service.webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha512,
        )
        signature = hash_object.hexdigest()

        result = paystack_service.verify_webhook_signature(payload, signature)
        assert result is True

    def test_verify_webhook_signature_invalid(self, paystack_service):
        """Test invalid webhook signature verification"""
        payload = b'{"event":"charge.success"}'
        invalid_signature = "invalid_signature_123"

        result = paystack_service.verify_webhook_signature(payload, invalid_signature)
        assert result is False

    @patch("app.services.paystack_service.requests.get")
    async def test_list_authorizations_success(self, mock_get, paystack_service):
        """Test successful authorization listing"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Authorizations retrieved",
            "data": [
                {
                    "authorization_code": "auth_code_1",
                    "bin": "412345",
                    "last4": "1234",
                    "exp_month": "12",
                    "exp_year": "2025",
                    "channel": "card",
                    "card_type": "visa",
                    "bank": None,
                    "country_code": None,
                    "brand": "Visa",
                    "reusable": True,
                    "signature": "sig_123",
                    "account_number": None,
                },
            ],
        }
        mock_get.return_value = mock_response

        result = await paystack_service.list_authorizations(customer_code="CUS_123")

        assert len(result) == 1
        assert result[0]["authorization_code"] == "auth_code_1"
        mock_get.assert_called_once()

    @patch("app.services.paystack_service.requests.post")
    async def test_create_plan_success(self, mock_post, paystack_service):
        """Test successful plan creation"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Plan created",
            "data": {
                "id": 1,
                "name": "Gold Membership",
                "description": "Premium benefits",
                "amount": 99900,  # 999.00 in kobo
                "interval": "monthly",
                "plan_code": "PLN_123",
            },
        }
        mock_post.return_value = mock_response

        result = await paystack_service.create_plan(
            name="Gold Membership",
            description="Premium benefits",
            amount=999.00,
            interval="monthly",
        )

        assert result["name"] == "Gold Membership"
        assert result["plan_code"] == "PLN_123"
        mock_post.assert_called_once()

    @patch("app.services.paystack_service.requests.post")
    async def test_create_subscription_success(self, mock_post, paystack_service):
        """Test successful subscription creation"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Subscription created",
            "data": {
                "id": 1,
                "subscription_code": "SUB_123",
                "customer_code": "CUS_123",
                "plan_code": "PLN_123",
                "status": "active",
            },
        }
        mock_post.return_value = mock_response

        result = await paystack_service.create_subscription(
            customer_code="CUS_123",
            plan_code="PLN_123",
            authorization_code="auth_code_123",
        )

        assert result["subscription_code"] == "SUB_123"
        assert result["status"] == "active"
        mock_post.assert_called_once()

    @patch("app.services.paystack_service.requests.get")
    async def test_get_transaction_timeline_success(self, mock_get, paystack_service):
        """Test successful transaction timeline retrieval"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Timeline retrieved",
            "data": [
                {
                    "type": "charge",
                    "message": "Charge initiated",
                    "time": 1234567890,
                },
                {
                    "type": "success",
                    "message": "Charge successful",
                    "time": 1234567900,
                },
            ],
        }
        mock_get.return_value = mock_response

        result = await paystack_service.get_transaction_timeline(reference="ref_123")

        assert len(result) == 2
        assert result[0]["type"] == "charge"
        mock_get.assert_called_once()
