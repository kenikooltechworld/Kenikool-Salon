"""Pytest configuration and fixtures."""

import pytest
import os
from mongoengine import connect, disconnect


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Set up test database connection."""
    try:
        disconnect()
        # Use MongoDB Atlas connection from environment
        import os
        from app.config import Settings
        settings = Settings()
        
        # Connect to MongoDB Atlas
        connect(
            db=settings.database_name,
            host=settings.database_url,
            connect=False,
            serverSelectionTimeoutMS=5000,
        )
    except Exception as e:
        # If MongoDB is not available, skip database tests
        print(f"MongoDB connection error: {e}")
        pytest.skip(f"MongoDB not available: {e}")
    yield
    try:
        disconnect()
    except:
        pass


@pytest.fixture(autouse=True)
def clear_db():
    """Clear database before each test."""
    try:
        from mongoengine import get_db
        db = get_db()
        for collection_name in db.list_collection_names():
            if not collection_name.startswith("system."):
                db[collection_name].delete_many({})
    except:
        pass
    yield


@pytest.fixture
def test_settings():
    """Provide test settings."""
    from app.config import Settings
    return Settings(
        environment="testing",
        debug=True,
        database_url="mongodb://localhost:27017/salon_test",
        database_name="salon_test",
        redis_url="redis://localhost:6379/15",
        jwt_secret_key="test-secret-key",
    )


@pytest.fixture
def app_settings(test_settings):
    """Provide app settings for testing."""
    return test_settings
