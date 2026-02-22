"""
Integration tests for security service
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, patch, AsyncMock

from app.services.security_service import security_service
from app.services.audit_log_service import audit_log_service
from app.utils.security import hash_password


@pytest.mark.asyncio
async def test_password_change_flow():
    """Test complete password change flow"""
    user_id = str(ObjectId())
    tenant_id = str(ObjectId())
    current_password = "OldPassword123!"
    new_password = "NewPassword456!"
    
    with patch('app.services.security_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        
        # Mock user
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "email": "test@example.com",
            "full_name": "Test User",
            "password_hash": hash_password(current_password)
        }
        
        mock_db.users.find_one.return_value = user
        mock_db.sessions.delete_many.return_value = Mock(deleted_count=2)
        
        request_info = {
            "ip_address": "192.168.1.1",
            "device": "Chrome",
            "browser": "Chrome 120",
            "session_id": str(ObjectId())
        }
        
        with patch('app.services.security_service.email_service') as mock_email:
            mock_email.send_password_change_confirmation = AsyncMock()
            
            result = await security_service.change_password(
                user_id, tenant_id, current_password, new_password, request_info
            )
        
        assert result is True
        mock_db.users.update_one.assert_called_once()
        mock_db.sessions.delete_many.assert_called_once()


@pytest.mark.asyncio
async def test_2fa_setup_and_verification_flow():
    """Test complete 2FA setup and verification flow"""
    user_id = str(ObjectId())
    tenant_id = str(ObjectId())
    
    with patch('app.services.security_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "email": "test@example.com"
        }
        
        mock_db.users.find_one.return_value = user
        
        # Step 1: Setup 2FA
        with patch('app.services.security_service.RedisCache') as mock_cache:
            setup_result = await security_service.setup_2fa(user_id, tenant_id)
        
        assert "secret" in setup_result
        assert "qr_code_url" in setup_result
        assert "backup_codes" in setup_result
        assert len(setup_result["backup_codes"]) == 10
        
        # Step 2: Verify and enable 2FA
        import pyotp
        secret = setup_result["secret"]
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        request_info = {"ip_address": "192.168.1.1"}
        
        with patch('app.services.security_service.RedisCache') as mock_cache:
            mock_cache.get.return_value = {
                "secret": secret,
                "backup_codes_hashed": ["hashed_code1", "hashed_code2"]
            }
            
            verify_result = await security_service.verify_and_enable_2fa(
                user_id, tenant_id, code, request_info
            )
        
        assert verify_result is True
        mock_db.users.update_one.assert_called()


@pytest.mark.asyncio
async def test_session_management_flow():
    """Test complete session management flow"""
    user_id = str(ObjectId())
    tenant_id = str(ObjectId())
    token = "test_token_123"
    
    with patch('app.services.security_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        
        # Create session
        session_id = ObjectId()
        mock_db.sessions.insert_one.return_value = Mock(inserted_id=session_id)
        
        request_info = {
            "ip_address": "192.168.1.1",
            "device": "Chrome on Windows",
            "browser": "Chrome 120",
            "user_agent": "Mozilla/5.0...",
            "location": "Lagos, Nigeria"
        }
        
        session_result = await security_service.create_session(
            user_id, tenant_id, token, request_info
        )
        
        assert session_result == str(session_id)
        
        # Get active sessions
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
        
        mock_db.sessions.find.return_value.sort.return_value = sessions
        
        get_result = await security_service.get_active_sessions(user_id, tenant_id)
        
        assert len(get_result) == 1
        assert get_result[0]["device"] == "Chrome"
        
        # Revoke session
        mock_db.sessions.delete_one.return_value = Mock(deleted_count=1)
        
        revoke_result = await security_service.revoke_session(
            user_id, tenant_id, str(ObjectId())
        )
        
        assert revoke_result is True


@pytest.mark.asyncio
async def test_security_score_calculation():
    """Test security score calculation"""
    user_id = str(ObjectId())
    tenant_id = str(ObjectId())
    
    with patch('app.services.security_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "password_hash": hash_password("StrongPassword123!"),
            "totp_enabled": True,
            "email_verified": True,
            "phone_verified": True,
            "password_changed_at": datetime.utcnow() - timedelta(days=30)
        }
        
        mock_db.users.find_one.return_value = user
        mock_db.security_logs.find.return_value = []
        
        with patch('app.services.security_service.RedisCache') as mock_cache:
            mock_cache.get.return_value = None
            
            score = await security_service.calculate_security_score(user_id, tenant_id)
        
        assert score >= 75  # Should be high score with all security measures


@pytest.mark.asyncio
async def test_audit_log_event_logging():
    """Test audit log event logging"""
    user_id = str(ObjectId())
    tenant_id = str(ObjectId())
    
    with patch('app.services.audit_log_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        
        log_id = ObjectId()
        mock_db.security_logs.insert_one.return_value = Mock(inserted_id=log_id)
        mock_db.security_logs.find_one.return_value = None
        
        request_info = {
            "ip_address": "192.168.1.1",
            "device": "Chrome",
            "browser": "Chrome 120"
        }
        
        result = await audit_log_service.log_event(
            user_id, tenant_id, "login", request_info, True
        )
        
        assert result == str(log_id)
        mock_db.security_logs.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_login_activity_monitoring():
    """Test login activity monitoring"""
    user_id = str(ObjectId())
    tenant_id = str(ObjectId())
    
    with patch('app.services.security_service.Database') as mock_db_class:
        mock_db = Mock()
        mock_db_class.get_db.return_value = mock_db
        
        # Test get login activity
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
        
        mock_db.security_logs.find.return_value.sort.return_value.limit.return_value = logs
        
        result = await security_service.get_login_activity(user_id, tenant_id)
        
        assert len(result) == 1
        assert result[0]["event_type"] == "login"
        
        # Test detect new device
        mock_db.security_logs.find_one.return_value = None
        
        request_info = {"ip_address": "192.168.1.1"}
        
        is_new = await security_service.detect_new_device(
            user_id, tenant_id, "New Device", request_info
        )
        
        assert is_new is True
        
        # Test account lockout check
        user = {
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "account_locked_until": datetime.utcnow() + timedelta(minutes=10)
        }
        
        mock_db.users.find_one.return_value = user
        
        is_locked = await security_service.check_account_lockout(user_id, tenant_id)
        
        assert is_locked is True
