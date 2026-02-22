"""
Pytest configuration and fixtures
"""
import sys
import os
from pathlib import Path
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import Mock, MagicMock, patch

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Initialize database connection for all tests"""
    # Don't auto-connect - let tests decide
    yield


@pytest.fixture
def db_mock():
    """Mock database instance for unit tests"""
    mock_db = MagicMock()
    
    # Mock collections
    mock_db.users = MagicMock()
    mock_db.sessions = MagicMock()
    mock_db.api_keys = MagicMock()
    mock_db.user_preferences = MagicMock()
    mock_db.privacy_settings = MagicMock()
    mock_db.security_logs = MagicMock()
    mock_db.data_exports = MagicMock()
    mock_db.account_deletions = MagicMock()
    mock_db.notifications = MagicMock()
    mock_db.notification_queue = MagicMock()
    mock_db.notification_preferences = MagicMock()
    
    return mock_db


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "test-tenant-123"
