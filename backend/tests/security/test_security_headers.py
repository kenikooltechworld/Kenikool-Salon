"""Tests for security headers middleware."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middleware.security_headers import SecurityHeadersMiddleware


@pytest.fixture
def app():
    """Create test app with security headers middleware."""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}

    app.add_middleware(SecurityHeadersMiddleware)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


def test_x_frame_options_header(client):
    """Test X-Frame-Options header is set."""
    response = client.get("/test")
    assert response.headers["X-Frame-Options"] == "DENY"


def test_x_content_type_options_header(client):
    """Test X-Content-Type-Options header is set."""
    response = client.get("/test")
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_x_xss_protection_header(client):
    """Test X-XSS-Protection header is set."""
    response = client.get("/test")
    assert response.headers["X-XSS-Protection"] == "1; mode=block"


def test_strict_transport_security_header(client):
    """Test Strict-Transport-Security header is set."""
    response = client.get("/test")
    assert "max-age=31536000" in response.headers["Strict-Transport-Security"]


def test_content_security_policy_header(client):
    """Test Content-Security-Policy header is set."""
    response = client.get("/test")
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_referrer_policy_header(client):
    """Test Referrer-Policy header is set."""
    response = client.get("/test")
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_permissions_policy_header(client):
    """Test Permissions-Policy header is set."""
    response = client.get("/test")
    assert "geolocation=()" in response.headers["Permissions-Policy"]
    assert "microphone=()" in response.headers["Permissions-Policy"]
    assert "camera=()" in response.headers["Permissions-Policy"]
