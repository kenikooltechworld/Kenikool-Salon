"""Integration tests for Paystack webhook handling."""

import json
import hmac
import hashlib
import pytest
from datetime import datetime
from decimal import Decimal
from bson import ObjectId
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.tenant import Tenant
from app.models.user import User
from app.services.paystack_service import PaystackService

client = TestClient(app)


@pytest.fixture
def test_tenant():
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Salon",
        subscription_tier="professional",
        status="active",
    )
    tenant.save()
    return tenant


@pytest.fixture
def test_user(test_tenant):
    """Create a test user."""
    user = User(
        tenant_id=test_tenant.id,
        email="owner@test.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="Owner",
        role_id=ObjectId(),
        status="active",
    )
    user.save()
    return user


@pytest.fixture
def test_customer(test_tenant):
    """Create a test customer."""
    customer = Customer(
        tenant_id=test_tenant.id,
        first_name="John",
        last_name="Doe",
        email="customer@test.com",
        phone="+234123456789",
    )
    customer.save()
    return customer


@pytest.fixture
def test_invoice(test_tenant, test_customer):
    """Create a test invoice."""
    invoice = Invoice(
        tenant_id=test_tenant.id,
        customer_id=test_customer.id,
        subtotal=Decimal("10000"),
        discount=Decimal("0"),
        tax=Decimal("0"),
        total=Decimal("10000"),
        status="issued",
    )
    invoice.save()
    return invoice


@pytest.fixture
def test_payment(test_tenant, test_customer, test_invoice):
    """Create a test payment."""
    payment = Payment(
        tenant_id=test_tenant.id,
        customer_id=test_customer.id,
        invoice_id=test_invoice.id,
        amount=Decimal("10000"),
        reference="test_reference_12345",
        gateway="paystack",
        status="pending",
    )
    payment.save()
    return payment


@pytest.fixture
def webhook_secret():
    """Get webhook secret from environment."""
    import os
    return os.getenv("PAYSTACK_WEBHOOK_SECRET", "test_webhook_secret")


def create_webhook_signature(body: str, secret: str) -> str:
    """Create a valid webhook signature."""
    return hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha512,
    ).hexdigest()


class TestPaystackWebhookSignatureVerification:
    """Test webhook signature verification."""

    def test_verify_valid_signature(self, webhook_secret):
        """Test verification of valid signature."""
        paystack_service = PaystackService()
        body = '{"event": "charge.success", "data": {}}'
        signature = create_webhook_signature(body, webhook_secret)
        
        # Mock the webhook secret
        with patch.object(paystack_service, 'webhook_secret', webhook_secret):
            result = paystack_service.verify_webhook_signature(body, signature)
            assert result is True

    def test_verify_invalid_signature(self, webhook_secret):
        """Test rejection of invalid signature."""
        paystack_service = PaystackService()
        body = '{"event": "charge.success", "data": {}}'
        invalid_signature = "invalid_signature_12345"
        
        # Mock the webhook secret
        with patch.object(paystack_service, 'webhook_secret', webhook_secret):
            result = paystack_service.verify_webhook_signature(body, invalid_signature)
            assert result is False

    def test_verify_signature_with_modified_body(self, webhook_secret):
        """Test rejection when body is modified."""
        paystack_service = PaystackService()
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


class TestPaystackWebhookEndpoint:
    """Test webhook endpoint."""

    def test_webhook_missing_signature_header(self, test_payment, webhook_secret):
        """Test webhook rejected when signature header is missing."""
        body = {
            "event": "charge.success",
            "data": {
                "reference": test_payment.reference,
                "amount": 1000000,
                "status": "success",
            }
        }
        
        response = client.post(
            "/v1/webhooks/paystack",
            json=body,
        )
        
        assert response.status_code == 401
        assert "Missing X-Paystack-Signature header" in response.json()["detail"]

    def test_webhook_invalid_signature(self, test_payment, webhook_secret):
        """Test webhook rejected with invalid signature."""
        body = {
            "event": "charge.success",
            "data": {
                "reference": test_payment.reference,
                "amount": 1000000,
                "status": "success",
            }
        }
        
        response = client.post(
            "/v1/webhooks/paystack",
            json=body,
            headers={"X-Paystack-Signature": "invalid_signature"},
        )
        
        assert response.status_code == 401
        assert "Invalid webhook signature" in response.json()["detail"]

    def test_webhook_charge_success(self, test_payment, test_invoice, webhook_secret):
        """Test successful charge webhook."""
        body_dict = {
            "event": "charge.success",
            "data": {
                "reference": test_payment.reference,
                "amount": 1000000,
                "status": "success",
                "id": 123456,
                "paid_at": "2024-01-15T10:30:00.000Z",
                "customer": {"email": "customer@test.com"},
                "authorization": {"auth_code": "auth_123"},
                "gateway_response": "Approved",
            }
        }
        
        body_str = json.dumps(body_dict)
        signature = create_webhook_signature(body_str, webhook_secret)
        
        with patch.object(PaystackService, 'webhook_secret', webhook_secret):
            response = client.post(
                "/v1/webhooks/paystack",
                content=body_str,
                headers={
                    "X-Paystack-Signature": signature,
                    "Content-Type": "application/json",
                },
            )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify payment status updated
        updated_payment = Payment.objects(id=test_payment.id).first()
        assert updated_payment.status == "success"
        assert updated_payment.metadata.get("paystack_transaction_id") == 123456
        
        # Verify invoice marked as paid
        updated_invoice = Invoice.objects(id=test_invoice.id).first()
        assert updated_invoice.status == "paid"
        assert updated_invoice.paid_at is not None

    def test_webhook_charge_failed(self, test_payment, webhook_secret):
        """Test failed charge webhook."""
        body_dict = {
            "event": "charge.failed",
            "data": {
                "reference": test_payment.reference,
                "amount": 1000000,
                "status": "failed",
                "id": 123456,
                "paid_at": "2024-01-15T10:30:00.000Z",
                "customer": {"email": "customer@test.com"},
                "gateway_response": "Insufficient funds",
            }
        }
        
        body_str = json.dumps(body_dict)
        signature = create_webhook_signature(body_str, webhook_secret)
        
        with patch.object(PaystackService, 'webhook_secret', webhook_secret):
            response = client.post(
                "/v1/webhooks/paystack",
                content=body_str,
                headers={
                    "X-Paystack-Signature": signature,
                    "Content-Type": "application/json",
                },
            )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify payment status updated
        updated_payment = Payment.objects(id=test_payment.id).first()
        assert updated_payment.status == "failed"
        assert "Insufficient funds" in updated_payment.metadata.get("failure_reason", "")

    def test_webhook_payment_not_found(self, webhook_secret):
        """Test webhook when payment not found."""
        body_dict = {
            "event": "charge.success",
            "data": {
                "reference": "nonexistent_reference",
                "amount": 1000000,
                "status": "success",
                "id": 123456,
                "paid_at": "2024-01-15T10:30:00.000Z",
                "customer": {"email": "customer@test.com"},
                "authorization": {"auth_code": "auth_123"},
                "gateway_response": "Approved",
            }
        }
        
        body_str = json.dumps(body_dict)
        signature = create_webhook_signature(body_str, webhook_secret)
        
        with patch.object(PaystackService, 'webhook_secret', webhook_secret):
            response = client.post(
                "/v1/webhooks/paystack",
                content=body_str,
                headers={
                    "X-Paystack-Signature": signature,
                    "Content-Type": "application/json",
                },
            )
        
        assert response.status_code == 404
        assert "Payment not found" in response.json()["detail"]

    def test_webhook_unhandled_event(self, test_payment, webhook_secret):
        """Test webhook with unhandled event type."""
        body_dict = {
            "event": "charge.dispute.created",
            "data": {
                "reference": test_payment.reference,
                "amount": 1000000,
                "id": 123456,
            }
        }
        
        body_str = json.dumps(body_dict)
        signature = create_webhook_signature(body_str, webhook_secret)
        
        with patch.object(PaystackService, 'webhook_secret', webhook_secret):
            response = client.post(
                "/v1/webhooks/paystack",
                content=body_str,
                headers={
                    "X-Paystack-Signature": signature,
                    "Content-Type": "application/json",
                },
            )
        
        # Should still return success for unhandled events
        assert response.status_code == 200
        assert response.json()["success"] is True


class TestWebhookIdempotency:
    """Test webhook idempotency handling."""

    def test_duplicate_webhook_charge_success(self, test_payment, test_invoice, webhook_secret):
        """Test that duplicate webhooks don't cause issues."""
        body_dict = {
            "event": "charge.success",
            "data": {
                "reference": test_payment.reference,
                "amount": 1000000,
                "status": "success",
                "id": 123456,
                "paid_at": "2024-01-15T10:30:00.000Z",
                "customer": {"email": "customer@test.com"},
                "authorization": {"auth_code": "auth_123"},
                "gateway_response": "Approved",
            }
        }
        
        body_str = json.dumps(body_dict)
        signature = create_webhook_signature(body_str, webhook_secret)
        
        with patch.object(PaystackService, 'webhook_secret', webhook_secret):
            # Send webhook twice
            response1 = client.post(
                "/v1/webhooks/paystack",
                content=body_str,
                headers={
                    "X-Paystack-Signature": signature,
                    "Content-Type": "application/json",
                },
            )
            
            response2 = client.post(
                "/v1/webhooks/paystack",
                content=body_str,
                headers={
                    "X-Paystack-Signature": signature,
                    "Content-Type": "application/json",
                },
            )
        
        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Payment should still be marked as success
        updated_payment = Payment.objects(id=test_payment.id).first()
        assert updated_payment.status == "success"
        
        # Invoice should still be marked as paid
        updated_invoice = Invoice.objects(id=test_invoice.id).first()
        assert updated_invoice.status == "paid"


class TestWebhookAuditLogging:
    """Test webhook audit logging."""

    @patch('app.routes.webhooks.audit_service.log_event')
    def test_webhook_audit_logged(self, mock_log_event, test_payment, webhook_secret):
        """Test that webhook events are logged to audit trail."""
        body_dict = {
            "event": "charge.success",
            "data": {
                "reference": test_payment.reference,
                "amount": 1000000,
                "status": "success",
                "id": 123456,
                "paid_at": "2024-01-15T10:30:00.000Z",
                "customer": {"email": "customer@test.com"},
                "authorization": {"auth_code": "auth_123"},
                "gateway_response": "Approved",
            }
        }
        
        body_str = json.dumps(body_dict)
        signature = create_webhook_signature(body_str, webhook_secret)
        
        # Mock the async log_event to return a coroutine
        async def mock_async_log(*args, **kwargs):
            return None
        
        mock_log_event.return_value = mock_async_log()
        
        with patch.object(PaystackService, 'webhook_secret', webhook_secret):
            response = client.post(
                "/v1/webhooks/paystack",
                content=body_str,
                headers={
                    "X-Paystack-Signature": signature,
                    "Content-Type": "application/json",
                },
            )
        
        assert response.status_code == 200
