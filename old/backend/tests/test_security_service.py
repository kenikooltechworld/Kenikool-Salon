"""
Tests for security service - password, 2FA, sessions, and security monitoring
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from bson import ObjectId

from app.services.security_service import (
    security_service, UnauthorizedException, BadRequestException, NotFoundException
)
from app.utils.security import hash_password, verify_password


class TestPasswordChange:
    """Tests for password change functionality"""

    @pytest.mark.asyncio
    async def test_change_password_success(self, db_mock):
        """Test successful password change"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        current_password = "OldPassword123!"
        new_password = "NewPassword456!"
        
        # Mock user
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "email": "test@example.com",
            "full_name": "Test User",
            "password_hash": hash_password(current_password)
        }
        
        db_mock.users.find_one.return_value = user
        db_mock.sessions.delete_many.return_value = Mock(deleted_count=2)
        
        request_info = {
            "ip_address": "192.168.1.1",
            "device": "Chrome",
            "browser": "Chrome 120",
            "session_id": str(ObjectId())
        }
        
        # Mock email service
        with patch('app.services.security_service.email_service') as mock_email:
            mock_email.send_password_change_confirmation = AsyncMock()
            
            # Mock audit log service
            with patch('app.services.security_service.audit_log_service') as mock_audit:
                mock_audit.log_event = AsyncMock()
                
                result = await security_service.change_password(
                    user_id, tenant_id, current_password, new_password, request_info
                )
        
        assert result is True
        db_mock.users.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_incorrect_current(self, db_mock):
        """Test password change with incorrect current password"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "password_hash": hash_password("CorrectPassword123!")
        }
        
        db_mock.users.find_one.return_value = user
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.security_service.audit_log_service') as mock_audit:
            mock_audit.log_event = AsyncMock()
            
            with pytest.raises(UnauthorizedException):
                await security_service.change_password(
                    user_id, tenant_id, "WrongPassword", "NewPassword456!", request_info
                )

    @pytest.mark.asyncio
    async def test_change_password_too_short(self, db_mock):
        """Test password change with password too short"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        current_password = "OldPassword123!"
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "password_hash": hash_password(current_password)
        }
        
        db_mock.users.find_one.return_value = user
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with pytest.raises(BadRequestException):
            await security_service.change_password(
                user_id, tenant_id, current_password, "Short1!", request_info
            )

    @pytest.mark.asyncio
    async def test_change_password_same_as_current(self, db_mock):
        """Test password change with same password as current"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        password = "SamePassword123!"
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "password_hash": hash_password(password)
        }
        
        db_mock.users.find_one.return_value = user
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with pytest.raises(BadRequestException):
            await security_service.change_password(
                user_id, tenant_id, password, password, request_info
            )


class TestTwoFactorAuth:
    """Tests for 2FA setup and verification"""

    @pytest.mark.asyncio
    async def test_setup_2fa_success(self, db_mock):
        """Test successful 2FA setup"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "email": "test@example.com"
        }
        
        db_mock.users.find_one.return_value = user
        
        with patch('app.services.security_service.redis_cache') as mock_cache:
            result = await security_service.setup_2fa(user_id, tenant_id)
        
        assert "secret" in result
        assert "qr_code_url" in result
        assert "backup_codes" in result
        assert len(result["backup_codes"]) == 10
        assert result["qr_code_url"].startswith("data:image/png;base64,")

    @pytest.mark.asyncio
    async def test_verify_and_enable_2fa_success(self, db_mock):
        """Test successful 2FA verification and enabling"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        # Generate valid TOTP secret
        import pyotp
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.security_service.redis_cache') as mock_cache:
            # Mock setup data in cache
            mock_cache.get.return_value = {
                "secret": secret,
                "backup_codes_hashed": ["hashed_code1", "hashed_code2"]
            }
            
            with patch('app.services.security_service.audit_log_service') as mock_audit:
                mock_audit.log_event = AsyncMock()
                
                result = await security_service.verify_and_enable_2fa(
                    user_id, tenant_id, code, request_info
                )
        
        assert result is True
        db_mock.users.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_disable_2fa_success(self, db_mock):
        """Test successful 2FA disabling"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        password = "Password123!"
        
        import pyotp
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "password_hash": hash_password(password),
            "totp_enabled": True,
            "totp_secret": secret
        }
        
        db_mock.users.find_one.return_value = user
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.security_service.audit_log_service') as mock_audit:
            mock_audit.log_event = AsyncMock()
            
            result = await security_service.disable_2fa(
                user_id, tenant_id, password, code, request_info
            )
        
        assert result is True
        db_mock.users.update_one.assert_called_once()


class TestSessionManagement:
    """Tests for session management"""

    @pytest.mark.asyncio
    async def test_create_session_success(self, db_mock):
        """Test successful session creation"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        token = "test_token_123"
        
        session_id = ObjectId()
        db_mock.sessions.insert_one.return_value = Mock(inserted_id=session_id)
        
        request_info = {
            "ip_address": "192.168.1.1",
            "device": "Chrome on Windows",
            "browser": "Chrome 120",
            "user_agent": "Mozilla/5.0...",
            "location": "Lagos, Nigeria"
        }
        
        result = await security_service.create_session(
            user_id, tenant_id, token, request_info
        )
        
        assert result == str(session_id)
        db_mock.sessions.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_sessions(self, db_mock):
        """Test getting active sessions"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        sessions = [
            {
                "_id": ObjectId(),
                "user_id": user_id,
                "device": "Chrome",
                "browser": "Chrome 120",
                "ip_address": "192.168.1.1",
                "location": "Lagos",
                "last_active": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=30)
            }
        ]
        
        db_mock.sessions.find.return_value.sort.return_value = sessions
        
        result = await security_service.get_active_sessions(user_id, tenant_id)
        
        assert len(result) == 1
        assert result[0]["device"] == "Chrome"

    @pytest.mark.asyncio
    async def test_revoke_session_success(self, db_mock):
        """Test successful session revocation"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        session_id = str(ObjectId())
        
        db_mock.sessions.delete_one.return_value = Mock(deleted_count=1)
        
        result = await security_service.revoke_session(user_id, tenant_id, session_id)
        
        assert result is True
        db_mock.sessions.delete_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_revoke_all_other_sessions(self, db_mock):
        """Test revoking all other sessions"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        current_session_id = str(ObjectId())
        
        db_mock.sessions.delete_many.return_value = Mock(deleted_count=3)
        
        result = await security_service.revoke_all_other_sessions(
            user_id, tenant_id, current_session_id
        )
        
        assert result == 3
        db_mock.sessions.delete_many.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self, db_mock):
        """Test cleanup of expired sessions"""
        db_mock.sessions.delete_many.return_value = Mock(deleted_count=5)
        
        result = await security_service.cleanup_expired_sessions()
        
        assert result == 5
        db_mock.sessions.delete_many.assert_called_once()


class TestSecurityScore:
    """Tests for security score calculation"""

    @pytest.mark.asyncio
    async def test_calculate_security_score_high(self, db_mock):
        """Test security score calculation with high security"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "password_hash": hash_password("StrongPassword123!"),
            "totp_enabled": True,
            "email_verified": True,
            "phone_verified": True,
            "password_changed_at": datetime.utcnow() - timedelta(days=30)
        }
        
        db_mock.users.find_one.return_value = user
        db_mock.security_logs.find.return_value = []
        
        with patch('app.services.security_service.redis_cache') as mock_cache:
            mock_cache.get.return_value = None
            
            result = await security_service.calculate_security_score(user_id, tenant_id)
        
        assert result >= 75  # Should be high score

    @pytest.mark.asyncio
    async def test_calculate_security_score_cached(self, db_mock):
        """Test security score calculation with cached result"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        with patch('app.services.security_service.redis_cache') as mock_cache:
            mock_cache.get.return_value = 85
            
            result = await security_service.calculate_security_score(user_id, tenant_id)
        
        assert result == 85
        db_mock.users.find_one.assert_not_called()


class TestLoginActivityMonitoring:
    """Tests for login activity monitoring"""

    @pytest.mark.asyncio
    async def test_get_login_activity(self, db_mock):
        """Test getting login activity"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        logs = [
            {
                "_id": ObjectId(),
                "user_id": user_id,
                "event_type": "login",
                "ip_address": "192.168.1.1",
                "device": "Chrome",
                "success": True,
                "timestamp": datetime.utcnow()
            }
        ]
        
        db_mock.security_logs.find.return_value.sort.return_value.limit.return_value = logs
        
        result = await security_service.get_login_activity(user_id, tenant_id)
        
        assert len(result) == 1
        assert result[0]["event_type"] == "login"

    @pytest.mark.asyncio
    async def test_detect_new_device(self, db_mock):
        """Test detecting new device"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        device = "New Device"
        
        db_mock.security_logs.find_one.return_value = None
        
        request_info = {"ip_address": "192.168.1.1"}
        
        result = await security_service.detect_new_device(
            user_id, tenant_id, device, request_info
        )
        
        assert result is True

    @pytest.mark.asyncio
    async def test_check_account_lockout_locked(self, db_mock):
        """Test checking account lockout when locked"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "account_locked_until": datetime.utcnow() + timedelta(minutes=10)
        }
        
        db_mock.users.find_one.return_value = user
        
        result = await security_service.check_account_lockout(user_id, tenant_id)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_increment_failed_login_attempts(self, db_mock):
        """Test incrementing failed login attempts"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "failed_login_attempts": 4
        }
        
        db_mock.users.find_one.return_value = user
        
        result = await security_service.increment_failed_login_attempts(user_id, tenant_id)
        
        assert result == 5
        db_mock.users.update_one.assert_called_once()


class TestAuditLogService:
    """Tests for audit log service"""

    @pytest.mark.asyncio
    async def test_log_event_success(self, db_mock):
        """Test logging security event"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        log_id = ObjectId()
        
        db_mock.security_logs.insert_one.return_value = Mock(inserted_id=log_id)
        db_mock.security_logs.find_one.return_value = None
        
        request_info = {
            "ip_address": "192.168.1.1",
            "device": "Chrome",
            "browser": "Chrome 120"
        }
        
        result = await audit_log_service.log_event(
            user_id, tenant_id, "login", request_info, True
        )
        
        assert result == str(log_id)
        db_mock.security_logs.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_audit_log(self, db_mock):
        """Test getting audit log"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        logs = [
            {
                "_id": ObjectId(),
                "user_id": user_id,
                "event_type": "login",
                "timestamp": datetime.utcnow()
            }
        ]
        
        db_mock.security_logs.find.return_value.sort.return_value.limit.return_value = logs
        
        result = await audit_log_service.get_audit_log(user_id, tenant_id)
        
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_export_audit_log(self, db_mock):
        """Test exporting audit log as CSV"""
        user_id = str(ObjectId())
        tenant_id = str(ObjectId())
        
        logs = [
            {
                "_id": ObjectId(),
                "user_id": user_id,
                "event_type": "login",
                "ip_address": "192.168.1.1",
                "device": "Chrome",
                "browser": "Chrome 120",
                "location": "Lagos",
                "success": True,
                "flagged": False,
                "details": {},
                "timestamp": datetime.utcnow()
            }
        ]
        
        db_mock.security_logs.find.return_value.sort.return_value = logs
        
        result = await audit_log_service.export_audit_log(user_id, tenant_id)
        
        assert "Timestamp,Event Type" in result
        assert "login" in result


@pytest.fixture
def db_mock():
    """Mock database for testing"""
    with patch('app.services.security_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        yield mock_db
