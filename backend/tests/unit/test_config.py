"""Property-based tests for configuration management."""

import pytest
from hypothesis import given, strategies as st
from app.config import Settings


class TestConfigurationConsistency:
    """Test configuration consistency across different environments."""

    @given(
        environment=st.sampled_from(["development", "staging", "production"]),
        debug=st.booleans(),
        port=st.integers(min_value=1024, max_value=65535),
    )
    def test_configuration_loads_correctly(self, environment, debug, port):
        """Test that configuration loads correctly with various values."""
        settings = Settings(
            environment=environment,
            debug=debug,
            port=port,
        )

        assert settings.environment == environment
        assert settings.debug == debug
        assert settings.port == port

    @given(
        jwt_expire_minutes=st.integers(min_value=1, max_value=10080),
        jwt_refresh_days=st.integers(min_value=1, max_value=365),
    )
    def test_token_expiration_values_valid(self, jwt_expire_minutes, jwt_refresh_days):
        """Test that token expiration values are valid."""
        settings = Settings(
            jwt_access_token_expire_minutes=jwt_expire_minutes,
            jwt_refresh_token_expire_days=jwt_refresh_days,
        )

        assert settings.jwt_access_token_expire_minutes == jwt_expire_minutes
        assert settings.jwt_refresh_token_expire_days == jwt_refresh_days
        assert jwt_expire_minutes > 0
        assert jwt_refresh_days > 0

    def test_default_values_applied(self):
        """Test that default values are applied when not provided."""
        settings = Settings()

        assert settings.environment == "development"
        assert settings.debug is True
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.api_prefix == "/api/v1"
        assert settings.jwt_algorithm == "HS256"

    @given(
        origins=st.lists(
            st.just("http://localhost:3000"),
            min_size=1,
            max_size=5,
        )
    )
    def test_cors_origins_configuration(self, origins):
        """Test CORS origins configuration."""
        settings = Settings(cors_origins=origins)

        assert settings.cors_origins == origins
        assert len(settings.cors_origins) > 0

    def test_configuration_consistency_multiple_instances(self):
        """Test that configuration is consistent across multiple instances."""
        settings1 = Settings(environment="development", port=8000)
        settings2 = Settings(environment="development", port=8000)

        assert settings1.environment == settings2.environment
        assert settings1.port == settings2.port
        assert settings1.jwt_secret_key == settings2.jwt_secret_key

    @given(
        log_level=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    )
    def test_log_level_configuration(self, log_level):
        """Test log level configuration."""
        settings = Settings(log_level=log_level)

        assert settings.log_level == log_level
        assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    def test_database_url_format(self):
        """Test that database URL is properly formatted."""
        db_url = "mongodb+srv://user:pass@cluster.mongodb.net/db"
        settings = Settings(database_url=db_url)

        assert settings.database_url == db_url
        assert "mongodb" in settings.database_url

    def test_redis_url_format(self):
        """Test that Redis URL is properly formatted."""
        redis_url = "redis://localhost:6379/0"
        settings = Settings(redis_url=redis_url)

        assert settings.redis_url == redis_url
        assert "redis://" in settings.redis_url

    def test_rabbitmq_url_format(self):
        """Test that RabbitMQ URL is properly formatted."""
        rabbitmq_url = "amqp://guest:guest@localhost:5672//"
        settings = Settings(rabbitmq_url=rabbitmq_url)

        assert settings.rabbitmq_url == rabbitmq_url
        assert "amqp://" in settings.rabbitmq_url

    @given(
        api_title=st.text(min_size=1, max_size=100),
        api_version=st.text(min_size=1, max_size=20),
    )
    def test_api_metadata_configuration(self, api_title, api_version):
        """Test API metadata configuration."""
        settings = Settings(
            api_title=api_title,
            api_version=api_version,
        )

        assert settings.api_title == api_title
        assert settings.api_version == api_version

    def test_frontend_url_configuration(self):
        """Test frontend URL configuration."""
        frontend_url = "http://localhost:3000"
        settings = Settings(frontend_url=frontend_url)

        assert settings.frontend_url == frontend_url
        assert "http" in settings.frontend_url
