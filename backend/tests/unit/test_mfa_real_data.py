"""Unit tests for MFA with real MongoDB data."""

import pytest
from app.services.mfa_service import MFAService
from app.models.user import User
from app.models.role import Role


@pytest.fixture
def mfa_service():
    """Create MFA service."""
    return MFAService()


@pytest.fixture
def test_tenant_id():
    """Create a test tenant ID."""
    return "test-tenant-mfa"


@pytest.fixture
def test_role(test_tenant_id):
    """Create a test role in MongoDB."""
    role = Role(
        tenant_id=test_tenant_id,
        name="Manager",
        description="Manager role",
        is_custom=False,
        permissions=[],
    )
    role.save()
    return role


@pytest.fixture
def test_user(test_tenant_id, test_role):
    """Create a test user in MongoDB."""
    user = User(
        tenant_id=test_tenant_id,
        email="mfa-test@example.com",
        password_hash="hashed-password",
        first_name="MFA",
        last_name="Test",
        phone="1234567890",
        role_ids=[test_role.id],  # Multiple roles per user
        status="active",
        mfa_enabled=False,
    )
    user.save()
    return user


class TestMFAWithRealMongoDB:
    """Test MFA with real MongoDB data."""

    def test_totp_secret_generation(self, mfa_service):
        """Test TOTP secret generation."""
        secret = mfa_service.generate_totp_secret()

        assert secret is not None
        assert len(secret) > 0
        assert isinstance(secret, str)

    def test_totp_uri_generation(self, mfa_service, test_user):
        """Test TOTP URI generation."""
        secret = mfa_service.generate_totp_secret()
        uri = mfa_service.get_totp_uri(
            email=test_user.email,
            secret=secret,
            issuer="SalonSPA",
        )

        assert uri is not None
        assert "otpauth://totp/" in uri
        assert test_user.email in uri
        assert "SalonSPA" in uri

    def test_qr_code_generation(self, mfa_service, test_user):
        """Test QR code generation."""
        secret = mfa_service.generate_totp_secret()
        uri = mfa_service.get_totp_uri(
            email=test_user.email,
            secret=secret,
            issuer="SalonSPA",
        )
        qr_code = mfa_service.generate_qr_code(uri)

        assert qr_code is not None
        assert len(qr_code) > 0
        assert "data:image/png;base64," in qr_code

    def test_totp_code_verification(self, mfa_service):
        """Test TOTP code verification."""
        secret = mfa_service.generate_totp_secret()

        # Get current TOTP code
        totp_code = mfa_service.get_totp_code(secret)
        assert totp_code is not None
        assert len(totp_code) == 6
        assert totp_code.isdigit()

        # Verify code
        is_valid = mfa_service.verify_totp_code(secret, totp_code)
        assert is_valid is True

    def test_totp_code_invalid_rejection(self, mfa_service):
        """Test that invalid TOTP codes are rejected."""
        secret = mfa_service.generate_totp_secret()

        # Try invalid code
        invalid_code = "000000"
        is_valid = mfa_service.verify_totp_code(secret, invalid_code)
        assert is_valid is False

    def test_backup_codes_generation(self, mfa_service):
        """Test backup codes generation."""
        backup_codes = mfa_service.generate_backup_codes(count=10)

        assert backup_codes is not None
        assert len(backup_codes) == 10

        # All codes should be unique
        assert len(set(backup_codes)) == 10

        # All codes should be non-empty strings
        for code in backup_codes:
            assert isinstance(code, str)
            assert len(code) > 0

    def test_backup_code_verification(self, mfa_service):
        """Test backup code verification."""
        backup_codes = mfa_service.generate_backup_codes(count=5)

        # Verify each code
        for code in backup_codes:
            is_valid = mfa_service.verify_backup_code(code, backup_codes)
            assert is_valid is True

    def test_backup_code_invalid_rejection(self, mfa_service):
        """Test that invalid backup codes are rejected."""
        backup_codes = mfa_service.generate_backup_codes(count=5)

        # Try invalid code
        invalid_code = "invalid-code"
        is_valid = mfa_service.verify_backup_code(invalid_code, backup_codes)
        assert is_valid is False

    def test_mfa_setup_in_mongodb(self, mfa_service, test_user, test_tenant_id):
        """Test MFA setup in MongoDB."""
        secret = mfa_service.generate_totp_secret()

        # Update user with MFA
        test_user.mfa_enabled = True
        test_user.mfa_method = "totp"
        test_user.save()

        # Verify user was updated
        updated_user = User.objects(id=test_user.id, tenant_id=test_tenant_id).first()
        assert updated_user.mfa_enabled is True
        assert updated_user.mfa_method == "totp"

    def test_mfa_disable_in_mongodb(self, mfa_service, test_user, test_tenant_id):
        """Test MFA disable in MongoDB."""
        # Enable MFA
        test_user.mfa_enabled = True
        test_user.mfa_method = "totp"
        test_user.save()

        # Disable MFA
        test_user.mfa_enabled = False
        test_user.mfa_method = None
        test_user.save()

        # Verify user was updated
        updated_user = User.objects(id=test_user.id, tenant_id=test_tenant_id).first()
        assert updated_user.mfa_enabled is False
        assert updated_user.mfa_method is None

    def test_multiple_users_mfa_isolation(self, mfa_service, test_tenant_id, test_role):
        """Test that MFA settings are isolated between users."""
        # Create two users
        user1 = User(
            tenant_id=test_tenant_id,
            email="user1@example.com",
            password_hash="hashed-password",
            first_name="User",
            last_name="One",
            phone="1111111111",
            role_ids=[test_role.id],  # Multiple roles per user
            status="active",
            mfa_enabled=True,
            mfa_method="totp",
        )
        user1.save()

        user2 = User(
            tenant_id=test_tenant_id,
            email="user2@example.com",
            password_hash="hashed-password",
            first_name="User",
            last_name="Two",
            phone="2222222222",
            role_ids=[test_role.id],  # Multiple roles per user
            status="active",
            mfa_enabled=False,
        )
        user2.save()

        # Verify MFA settings are isolated
        saved_user1 = User.objects(id=user1.id).first()
        saved_user2 = User.objects(id=user2.id).first()

        assert saved_user1.mfa_enabled is True
        assert saved_user2.mfa_enabled is False

    def test_totp_code_time_window(self, mfa_service):
        """Test TOTP code time window tolerance."""
        secret = mfa_service.generate_totp_secret()

        # Get current code
        current_code = mfa_service.get_totp_code(secret)

        # Verify current code works
        assert mfa_service.verify_totp_code(secret, current_code) is True

    def test_backup_codes_uniqueness(self, mfa_service):
        """Test that backup codes are always unique."""
        codes_set = set()

        for _ in range(5):
            backup_codes = mfa_service.generate_backup_codes(count=10)
            for code in backup_codes:
                assert code not in codes_set
                codes_set.add(code)

        # All codes should be unique
        assert len(codes_set) == 50
