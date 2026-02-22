"""Unit tests for webhook signature verification."""

import hmac
import hashlib
import pytest
from unittest.mock import patch
from app.services.paystack_service import PaystackService


def create_webhook_signature(body: str, secret: str) -> str:
    """Create a valid webhook signature."""
    return hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha512,
    ).hexdigest()


class TestWebhookSignatureVerification:
    """Test webhook signature verification."""

    def test_verify_valid_signature(self):
        """Test verification of valid signature."""
        paystack_service = PaystackService()
        webhook_secret = "test_webhook_secret"
        body = '{"event": "charge.success", "data": {}}'
        signature = create_webhook_signature(body, webhook_secret)
        
        # Mock the webhook secret
        with patch.object(paystack_service, 'webhook_secret', webhook_secret):
            result = paystack_service.verify_webhook_signature(body, signature)
            assert result is True

    def test_verify_invalid_signature(self):
        """Test rejection of invalid signature."""
        paystack_service = PaystackService()
        webhook_secret = "test_webhook_secret"
        body = '{"event": "charge.success", "data": {}}'
        invalid_signature = "invalid_signature_12345"
        
        # Mock the webhook secret
        with patch.object(paystack_service, 'webhook_secret', webhook_secret):
            result = paystack_service.verify_webhook_signature(body, invalid_signature)
            assert result is False

    def test_verify_signature_with_modified_body(self):
        """Test rejection when body is modified."""
        paystack_service = PaystackService()
        webhook_secret = "test_webhook_secret"
        body = '{"event": "charge.success", "data": {}}'
        signature = create_webhook_signature(body, webhook_secret)
        
        # Modify body
        modified_body = '{"event": "charge.success", "data": {"amount": 1000}}'
        
        # Mock the webhook secret
        with patch.object(paystack_service, 'webhook_secret', webhook_secret):
            result = paystack_service.verify_webhook_signature(modified_body, signature)
            assert result is False

    def test_verify_signature_missing_secret(self):
        """Test verification fails when secret is not configured."""
        paystack_service = PaystackService()
        body = '{"event": "charge.success", "data": {}}'
        signature = "any_signature"
        
        # Mock missing webhook secret
        with patch.object(paystack_service, 'webhook_secret', None):
            result = paystack_service.verify_webhook_signature(body, signature)
            assert result is False

    def test_extract_webhook_data_charge_success(self):
        """Test extracting data from charge.success event."""
        paystack_service = PaystackService()
        webhook_body = {
            "event": "charge.success",
            "data": {
                "reference": "test_ref_123",
                "amount": 1000000,
                "id": 123456,
                "paid_at": "2024-01-15T10:30:00.000Z",
                "customer": {"email": "test@example.com"},
                "authorization": {"auth_code": "auth_123"},
            }
        }
        
        extracted = paystack_service.extract_webhook_data(webhook_body)
        
        assert extracted["event"] == "charge.success"
        assert extracted["status"] == "success"
        assert extracted["reference"] == "test_ref_123"
        assert extracted["amount"] == 1000000
        assert extracted["transaction_id"] == 123456
        assert extracted["customer_email"] == "test@example.com"

    def test_extract_webhook_data_charge_failed(self):
        """Test extracting data from charge.failed event."""
        paystack_service = PaystackService()
        webhook_body = {
            "event": "charge.failed",
            "data": {
                "reference": "test_ref_123",
                "amount": 1000000,
                "id": 123456,
                "paid_at": "2024-01-15T10:30:00.000Z",
                "customer": {"email": "test@example.com"},
                "gateway_response": "Insufficient funds",
            }
        }
        
        extracted = paystack_service.extract_webhook_data(webhook_body)
        
        assert extracted["event"] == "charge.failed"
        assert extracted["status"] == "failed"
        assert extracted["reference"] == "test_ref_123"
        assert extracted["failure_reason"] == "Insufficient funds"

    def test_extract_webhook_data_missing_event(self):
        """Test extraction fails when event is missing."""
        paystack_service = PaystackService()
        webhook_body = {
            "data": {
                "reference": "test_ref_123",
            }
        }
        
        with pytest.raises(ValueError, match="Webhook event not found"):
            paystack_service.extract_webhook_data(webhook_body)

    def test_extract_webhook_data_unhandled_event(self):
        """Test extraction of unhandled event type."""
        paystack_service = PaystackService()
        webhook_body = {
            "event": "charge.dispute.created",
            "data": {
                "reference": "test_ref_123",
            }
        }
        
        extracted = paystack_service.extract_webhook_data(webhook_body)
        
        assert extracted["event"] == "charge.dispute.created"
        assert "data" in extracted
