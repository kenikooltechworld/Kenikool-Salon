"""Integration tests for registration API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.models.temp_registration import TempRegistration
from app.models.tenant import Tenant
from app.models.user import User


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def cleanup():
    """Clean up test data."""
    yield
    # Clean up after test
    TempRegistration.drop_collection()
    Tenant.drop_collection()
    User.drop_collection()


class TestRegisterEndpoint:
    """Tests for POST /auth/register endpoint."""

    def test_register_with_valid_data(self, client, cleanup):
        """Test registration with valid data."""
        response = client.post(
            "/v1/auth/register",
            json={
                "salon_name": "Test Salon",
                "owner_name": "John Doe",
                "email": "john@example.com",
                "phone": "+234 123 456 7890",
                "password": "SecurePass123!",
                "address": "123 Main St, Lagos",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "temp_registration_id" in data["data"]
        assert data["data"]["email"] == "john@example.com"

    def test_register_with_invalid_email(self, client, cleanup):
        """Test registration with invalid email."""
        response = client.post(
            "/v1/auth/register",
            json={
                "salon_name": "Test Salon",
                "owner_name": "John Doe",
                "email": "invalid-email",
                "phone": "+234 123 456 7890",
                "password": "SecurePass123!",
                "address": "123 Main St, Lagos",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_register_with_duplicate_email(self, client, cleanup):
        """Test registration with duplicate email."""
        # First registration
        client.post(
            "/v1/auth/register",
            json={
                "salon_name": "Test Salon",
                "owner_name": "John Doe",
                "email": "john@example.com",
                "phone": "+234 123 456 7890",
                "password": "SecurePass123!",
                "address": "123 Main St, Lagos",
            },
        )

        # Second registration with same email
        response = client.post(
            "/v1/auth/register",
            json={
                "salon_name": "Another Salon",
                "owner_name": "Jane Doe",
                "email": "john@example.com",
                "phone": "+234 987 654 3210",
                "password": "SecurePass123!",
                "address": "456 Oak St, Lagos",
            },
        )
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "already registered" in data["error"]["message"]

    def test_register_with_weak_password(self, client, cleanup):
        """Test registration with weak password."""
        response = client.post(
            "/v1/auth/register",
            json={
                "salon_name": "Test Salon",
                "owner_name": "John Doe",
                "email": "john@example.com",
                "phone": "+234 123 456 7890",
                "password": "weak",
                "address": "123 Main St, Lagos",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_register_with_optional_fields(self, client, cleanup):
        """Test registration with optional fields."""
        response = client.post(
            "/v1/auth/register",
            json={
                "salon_name": "Test Salon",
                "owner_name": "John Doe",
                "email": "john@example.com",
                "phone": "+234 123 456 7890",
                "password": "SecurePass123!",
                "address": "123 Main St, Lagos",
                "bank_account": "1234567890",
                "referral_code": "REF123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestVerifyCodeEndpoint:
    """Tests for POST /auth/verify-code endpoint."""

    def test_verify_with_valid_code(self, client, cleanup):
        """Test verification with valid code."""
        # First register
        register_response = client.post(
            "/v1/auth/register",
            json={
                "salon_name": "Test Salon",
                "owner_name": "John Doe",
                "email": "john@example.com",
                "phone": "+234 123 456 7890",
                "password": "SecurePass123!",
                "address": "123 Main St, Lagos",
            },
        )
        register_data = register_response.json()
        verification_code = register_data["data"]["verification_code"]

        # Then verify
        response = client.post(
            "/v1/auth/verify-code",
            json={
                "email": "john@example.com",
                "code": verification_code,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "tenant_id" in data["data"]
        assert "subdomain" in data["data"]
        assert "access_token" in data["data"]

    def test_verify_with_invalid_code(self, client, cleanup):
        """Test verification with invalid code."""
        # First register
        client.post(
            "/v1/auth/register",
            json={
                "salon_name": "Test Salon",
                "owner_name": "John Doe",
                "email": "john@example.com",
                "phone": "+234 123 456 7890",
                "password": "SecurePass123!",
                "address": "123 Main St, Lagos",
            },
        )

        # Try to verify with wrong code
        response = client.post(
            "/v1/auth/verify-code",
            json={
                "email": "john@example.com",
                "code": "000000",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Invalid verification code" in data["error"]["message"]

    def test_verify_with_nonexistent_email(self, client, cleanup):
        """Test verification with nonexistent email."""
        response = client.post(
            "/v1/auth/verify-code",
            json={
                "email": "nonexistent@example.com",
                "code": "123456",
            },
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_verify_creates_tenant_and_user(self, client, cleanup):
        """Test that verification creates tenant and user."""
        # Register
        register_response = client.post(
            "/v1/auth/register",
            json={
                "salon_name": "Test Salon",
                "owner_name": "John Doe",
                "email": "john@example.com",
                "phone": "+234 123 456 7890",
                "password": "SecurePass123!",
                "address": "123 Main St, Lagos",
            },
        )
        register_data = register_response.json()
        verification_code = register_data["data"]["verification_code"]

        # Verify
        verify_response = client.post(
            "/v1/auth/verify-code",
            json={
                "email": "john@example.com",
                "code": verification_code,
            },
        )
        verify_data = verify_response.json()

        # Check tenant was created
        tenant = Tenant.objects(id=verify_data["data"]["tenant_id"]).first()
        assert tenant is not None
        assert tenant.name == "Test Salon"
        assert tenant.subdomain == verify_data["data"]["subdomain"]

        # Check user was created
        user = User.objects(id=verify_data["data"]["user_id"]).first()
        assert user is not None
        assert user.email == "john@example.com"


class TestResendCodeEndpoint:
    """Tests for POST /auth/resend-code endpoint."""

    def test_resend_code_with_valid_email(self, client, cleanup):
        """Test resending code with valid email."""
        # First register
        client.post(
            "/v1/auth/register",
            json={
                "salon_name": "Test Salon",
                "owner_name": "John Doe",
                "email": "john@example.com",
                "phone": "+234 123 456 7890",
                "password": "SecurePass123!",
                "address": "123 Main St, Lagos",
            },
        )

        # Resend code
        response = client.post(
            "/v1/auth/resend-code",
            json={"email": "john@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_resend_code_with_nonexistent_email(self, client, cleanup):
        """Test resending code with nonexistent email."""
        response = client.post(
            "/v1/auth/resend-code",
            json={"email": "nonexistent@example.com"},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_resend_code_resets_attempts(self, client, cleanup):
        """Test that resending code resets attempt count."""
        # Register
        register_response = client.post(
            "/v1/auth/register",
            json={
                "salon_name": "Test Salon",
                "owner_name": "John Doe",
                "email": "john@example.com",
                "phone": "+234 123 456 7890",
                "password": "SecurePass123!",
                "address": "123 Main St, Lagos",
            },
        )
        register_data = register_response.json()

        # Try wrong code multiple times
        for _ in range(3):
            client.post(
                "/v1/auth/verify-code",
                json={
                    "email": "john@example.com",
                    "code": "000000",
                },
            )

        # Resend code
        client.post(
            "/v1/auth/resend-code",
            json={"email": "john@example.com"},
        )

        # Check that attempts were reset
        temp_reg = TempRegistration.objects(email="john@example.com").first()
        assert temp_reg.attempt_count == 0
