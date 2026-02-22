"""Unit tests for Paystack service."""

import pytest
import json
import hmac
import hashlib
from decimal import Decimal
from unittest.mock import patch, MagicMock
from app.services.paystack_service import PaystackService


@pytest.fixture
def paystack_service():
    """Create a Paystack service instance for testing."""
    with patch.dict(
        "os.environ",
        {
            "PAYSTACK_LIVE_SECRET_KEY": "test_secret_key",
            "PAYSTACK_LIVE_PUBLIC_KEY": "test_public_key",
            "PAYSTACK_WEBHOOK_SECRET": "test_webhook_secret",
        },
    ):
        return PaystackService()


class TestPaystackServiceInitialization:
    """Test Paystack service initialization."""

    def test_service_initializes_with_env_keys(self, paystack_service):
        """Test that service initializes with environment keys."""
        assert paystack_service.secret_key == "test_secret_key"
        assert paystack_service.public_key == "test_public_key"
        assert paystack_service.webhook_secret == "test_webhook_secret"

    def test_service_initializes_without_keys(self):
        """Test that service initializes even without environment keys."""
        with patch.dict("os.environ", {}, clear=True):
            service = PaystackService()
            assert service.secret_key is None
            assert service.public_key is None


class TestInitializeTransaction:
    """Test transaction initialization."""

    @patch("requests.post")
    def test_initialize_transaction_success(self, mock_post, paystack_service):
        """Test successful transaction initialization."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "authorization_url": "https://checkout.paystack.com/test",
                "access_code": "test_access_code",
                "reference": "test_reference",
            },
        }
        mock_post.return_value = mock_response

        result = paystack_service.initialize_transaction(
            amount=Decimal("1000"),
            email="test@example.com",
            metadata={"order_id": "123"},
        )

        assert result["authorization_url"] == "https://checkout.paystack.com/test"
        assert result["reference"] == "test_reference"
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_initialize_transaction_with_metadata(self, mock_post, paystack_service):
        """Test transaction initialization with metadata."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "data": {"reference": "test_ref"},
        }
        mock_post.return_value = mock_response

        paystack_service.initialize_transaction(
            amount=Decimal("500"),
            email="test@example.com",
            metadata={"customer_id": "cust_123", "service": "haircut"},
        )

        call_args = mock_post.call_args
        assert call_args[1]["json"]["metadata"]["customer_id"] == "cust_123"

    def test_initialize_transaction_invalid_amount(self, paystack_service):
        """Test transaction initialization with invalid amount."""
        with pytest.raises(ValueError, match="Amount must be greater than 0"):
            paystack_service.initialize_transaction(
                amount=Decimal("0"),
                email="test@example.com",
            )

    def test_initialize_transaction_negative_amount(self, paystack_service):
        """Test transaction initialization with negative amount."""
        with pytest.raises(ValueError, match="Amount must be greater than 0"):
            paystack_service.initialize_transaction(
                amount=Decimal("-100"),
                email="test@example.com",
            )

    def test_initialize_transaction_missing_email(self, paystack_service):
        """Test transaction initialization without email."""
        with pytest.raises(ValueError, match="Email is required"):
            paystack_service.initialize_transaction(
                amount=Decimal("1000"),
                email="",
            )

    @patch("requests.post")
    def test_initialize_transaction_api_error(self, mock_post, paystack_service):
        """Test transaction initialization with API error."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": False,
            "message": "Invalid amount",
        }
        mock_post.return_value = mock_response

        with pytest.raises(ValueError, match="Paystack error"):
            paystack_service.initialize_transaction(
                amount=Decimal("1000"),
                email="test@example.com",
            )

    @patch("requests.post")
    def test_initialize_transaction_network_error(self, mock_post, paystack_service):
        """Test transaction initialization with network error."""
        mock_post.side_effect = Exception("Connection timeout")

        with pytest.raises(Exception):
            paystack_service.initialize_transaction(
                amount=Decimal("1000"),
                email="test@example.com",
            )


class TestVerifyTransaction:
    """Test transaction verification."""

    @patch("requests.get")
    def test_verify_transaction_success(self, mock_get, paystack_service):
        """Test successful transaction verification."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "message": "Authorization URL created",
            "data": {
                "reference": "test_reference",
                "amount": 100000,
                "status": "success",
                "customer": {"email": "test@example.com"},
            },
        }
        mock_get.return_value = mock_response

        result = paystack_service.verify_transaction("test_reference")

        assert result["reference"] == "test_reference"
        assert result["status"] == "success"
        mock_get.assert_called_once()

    def test_verify_transaction_missing_reference(self, paystack_service):
        """Test transaction verification without reference."""
        with pytest.raises(ValueError, match="Reference is required"):
            paystack_service.verify_transaction("")

    @patch("requests.get")
    def test_verify_transaction_api_error(self, mock_get, paystack_service):
        """Test transaction verification with API error."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": False,
            "message": "Reference not found",
        }
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Paystack error"):
            paystack_service.verify_transaction("invalid_ref")


class TestGetTransaction:
    """Test getting transaction details."""

    @patch("requests.get")
    def test_get_transaction_success(self, mock_get, paystack_service):
        """Test successful transaction retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "data": {
                "id": 123456,
                "reference": "test_ref",
                "amount": 100000,
                "status": "success",
            },
        }
        mock_get.return_value = mock_response

        result = paystack_service.get_transaction(123456)

        assert result["id"] == 123456
        assert result["reference"] == "test_ref"

    def test_get_transaction_invalid_id(self, paystack_service):
        """Test get transaction with invalid ID."""
        with pytest.raises(ValueError, match="Transaction ID must be a positive integer"):
            paystack_service.get_transaction(0)

    def test_get_transaction_negative_id(self, paystack_service):
        """Test get transaction with negative ID."""
        with pytest.raises(ValueError, match="Transaction ID must be a positive integer"):
            paystack_service.get_transaction(-1)


class TestRefundTransaction:
    """Test transaction refunds."""

    @patch("requests.post")
    def test_refund_transaction_full(self, mock_post, paystack_service):
        """Test full transaction refund."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "data": {
                "reference": "test_ref",
                "amount": 100000,
                "status": "pending",
            },
        }
        mock_post.return_value = mock_response

        result = paystack_service.refund_transaction("test_ref")

        assert result["reference"] == "test_ref"
        call_args = mock_post.call_args
        assert "amount" not in call_args[1]["json"]

    @patch("requests.post")
    def test_refund_transaction_partial(self, mock_post, paystack_service):
        """Test partial transaction refund."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "data": {"reference": "test_ref"},
        }
        mock_post.return_value = mock_response

        paystack_service.refund_transaction("test_ref", amount=Decimal("500"))

        call_args = mock_post.call_args
        assert call_args[1]["json"]["amount"] == 50000  # 500 * 100

    def test_refund_transaction_missing_reference(self, paystack_service):
        """Test refund without reference."""
        with pytest.raises(ValueError, match="Reference is required"):
            paystack_service.refund_transaction("")

    def test_refund_transaction_invalid_amount(self, paystack_service):
        """Test refund with invalid amount."""
        with pytest.raises(ValueError, match="Refund amount must be greater than 0"):
            paystack_service.refund_transaction("test_ref", amount=Decimal("0"))


class TestWebhookSignatureVerification:
    """Test webhook signature verification."""

    def test_verify_webhook_signature_valid(self, paystack_service):
        """Test valid webhook signature verification."""
        request_body = '{"event":"charge.success","data":{"reference":"test"}}'
        signature = hmac.new(
            "test_webhook_secret".encode(),
            request_body.encode(),
            hashlib.sha512,
        ).hexdigest()

        result = paystack_service.verify_webhook_signature(request_body, signature)
        assert result is True

    def test_verify_webhook_signature_invalid(self, paystack_service):
        """Test invalid webhook signature verification."""
        request_body = '{"event":"charge.success"}'
        invalid_signature = "invalid_signature"

        result = paystack_service.verify_webhook_signature(request_body, invalid_signature)
        assert result is False

    def test_verify_webhook_signature_no_secret(self):
        """Test webhook verification without secret configured."""
        with patch.dict("os.environ", {}, clear=True):
            service = PaystackService()
            result = service.verify_webhook_signature("body", "signature")
            assert result is False


class TestExtractWebhookData:
    """Test webhook data extraction."""

    def test_extract_charge_success_webhook(self, paystack_service):
        """Test extracting charge.success webhook data."""
        webhook_body = {
            "event": "charge.success",
            "data": {
                "reference": "test_ref",
                "amount": 100000,
                "id": 123456,
                "customer": {"email": "test@example.com"},
                "authorization": {"auth_code": "auth_123"},
                "gateway_response": "Approved",
            },
        }

        result = paystack_service.extract_webhook_data(webhook_body)

        assert result["event"] == "charge.success"
        assert result["status"] == "success"
        assert result["reference"] == "test_ref"
        assert result["customer_email"] == "test@example.com"

    def test_extract_charge_failed_webhook(self, paystack_service):
        """Test extracting charge.failed webhook data."""
        webhook_body = {
            "event": "charge.failed",
            "data": {
                "reference": "test_ref",
                "amount": 100000,
                "id": 123456,
                "customer": {"email": "test@example.com"},
                "gateway_response": "Insufficient funds",
            },
        }

        result = paystack_service.extract_webhook_data(webhook_body)

        assert result["event"] == "charge.failed"
        assert result["status"] == "failed"
        assert result["failure_reason"] == "Insufficient funds"

    def test_extract_webhook_missing_event(self, paystack_service):
        """Test extracting webhook without event."""
        webhook_body = {"data": {}}

        with pytest.raises(ValueError, match="Webhook event not found"):
            paystack_service.extract_webhook_data(webhook_body)

    def test_extract_unhandled_webhook_event(self, paystack_service):
        """Test extracting unhandled webhook event."""
        webhook_body = {
            "event": "transfer.success",
            "data": {"reference": "test"},
        }

        result = paystack_service.extract_webhook_data(webhook_body)

        assert result["event"] == "transfer.success"
        assert "data" in result


class TestAmountConversion:
    """Test amount conversion to kobo."""

    @patch("requests.post")
    def test_amount_converted_to_kobo(self, mock_post, paystack_service):
        """Test that amounts are correctly converted to kobo."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "data": {"reference": "test"},
        }
        mock_post.return_value = mock_response

        paystack_service.initialize_transaction(
            amount=Decimal("1000.50"),
            email="test@example.com",
        )

        call_args = mock_post.call_args
        assert call_args[1]["json"]["amount"] == 100050  # 1000.50 * 100

    @patch("requests.post")
    def test_refund_amount_converted_to_kobo(self, mock_post, paystack_service):
        """Test that refund amounts are correctly converted to kobo."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": True,
            "data": {"reference": "test"},
        }
        mock_post.return_value = mock_response

        paystack_service.refund_transaction("test_ref", amount=Decimal("500.75"))

        call_args = mock_post.call_args
        assert call_args[1]["json"]["amount"] == 50075  # 500.75 * 100
