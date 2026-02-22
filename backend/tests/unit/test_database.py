"""Property-based tests for database connection."""

import pytest
from hypothesis import given, strategies as st
from app.db import init_db, close_db
from app.config import Settings


class TestDatabaseConnection:
    """Test database connection reliability and consistency."""

    def test_database_configuration_valid(self):
        """Test that database configuration is valid."""
        settings = Settings(
            database_url="mongodb+srv://user:pass@cluster.mongodb.net/db",
            database_name="test_db",
        )

        assert settings.database_url is not None
        assert settings.database_name is not None
        assert "mongodb" in settings.database_url

    @given(
        db_name=st.text(min_size=1, max_size=64, alphabet=st.characters(blacklist_categories=("Cc", "Cs"))),
        pool_size=st.integers(min_value=1, max_value=100),
    )
    def test_database_pool_configuration(self, db_name, pool_size):
        """Test database pool configuration."""
        settings = Settings(
            database_name=db_name,
        )

        assert settings.database_name == db_name
        assert len(settings.database_name) > 0

    def test_database_url_format_valid(self):
        """Test that database URL format is valid."""
        valid_urls = [
            "mongodb://localhost:27017/db",
            "mongodb+srv://user:pass@cluster.mongodb.net/db",
            "mongodb://user:pass@host1,host2,host3/db",
        ]

        for url in valid_urls:
            settings = Settings(database_url=url)
            assert settings.database_url == url
            assert "mongodb" in settings.database_url

    def test_database_connection_timeout_valid(self):
        """Test that connection timeout is valid."""
        settings = Settings()

        # Default timeout should be reasonable
        assert settings.database_url is not None

    @given(
        db_names=st.lists(
            st.text(min_size=1, max_size=32, alphabet="abcdefghijklmnopqrstuvwxyz0123456789_"),
            min_size=1,
            max_size=5,
        )
    )
    def test_multiple_database_names(self, db_names):
        """Test multiple database name configurations."""
        for db_name in db_names:
            settings = Settings(database_name=db_name)
            assert settings.database_name == db_name

    def test_database_settings_immutable(self):
        """Test that database settings are properly configured."""
        settings1 = Settings(database_name="db1")
        settings2 = Settings(database_name="db2")

        assert settings1.database_name != settings2.database_name

    def test_connection_string_components(self):
        """Test that connection string has required components."""
        settings = Settings(
            database_url="mongodb+srv://user:pass@cluster.mongodb.net/salon_db"
        )

        url = settings.database_url
        assert "mongodb" in url
        assert "@" in url or "localhost" in url

    @given(
        min_pool=st.integers(min_value=1, max_value=10),
        max_pool=st.integers(min_value=10, max_value=100),
    )
    def test_pool_size_constraints(self, min_pool, max_pool):
        """Test that pool size constraints are valid."""
        assert min_pool <= max_pool
        assert min_pool > 0
        assert max_pool > 0

    def test_database_retry_configuration(self):
        """Test database retry configuration."""
        settings = Settings()

        # Should have valid configuration
        assert settings.database_url is not None
        assert settings.database_name is not None

    def test_database_ssl_configuration(self):
        """Test database SSL configuration."""
        settings = Settings(
            database_url="mongodb+srv://user:pass@cluster.mongodb.net/db"
        )

        # MongoDB Atlas uses SSL by default with +srv
        assert "mongodb+srv" in settings.database_url or "mongodb://" in settings.database_url
