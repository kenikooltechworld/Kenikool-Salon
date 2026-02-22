"""Tests for FastAPI application initialization."""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestApplicationInitialization:
    """Test FastAPI application initialization."""

    def test_app_creation(self):
        """Test that app is created successfully."""
        app = create_app()
        assert app is not None
        assert app.title == "Salon/Spa/Gym SaaS Platform"

    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data

    def test_swagger_documentation_available(self, client):
        """Test that Swagger documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema_available(self, client):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in response."""
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        assert "access-control-allow-origin" in response.headers

    def test_request_id_header_present(self, client):
        """Test that request ID header is present in response."""
        response = client.get("/health")
        assert "x-request-id" in response.headers
        assert response.headers["x-request-id"] != ""

    def test_multiple_requests_have_different_ids(self, client):
        """Test that multiple requests have different request IDs."""
        response1 = client.get("/health")
        response2 = client.get("/health")

        id1 = response1.headers.get("x-request-id")
        id2 = response2.headers.get("x-request-id")

        assert id1 != id2

    def test_404_not_found(self, client):
        """Test 404 not found response."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_app_has_middleware(self):
        """Test that app has middleware configured."""
        app = create_app()
        # Check that middleware is registered
        assert len(app.user_middleware) > 0
