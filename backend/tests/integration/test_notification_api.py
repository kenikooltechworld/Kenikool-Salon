"""Integration tests for notification API."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.notification import Notification, NotificationTemplate, NotificationPreference
from app.context import set_tenant_id
from mongoengine import connect, disconnect
from mongomock import MongoClient


@pytest.fixture(scope="function")
def setup_db():
    """Setup test database."""
    disconnect()
    connect("mongoenginetest", mongo_client_class=MongoClient)
    yield
    disconnect()


@pytest.fixture
def client(setup_db):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def tenant_id():
    """Set tenant context."""
    test_tenant_id = "test_tenant_123"
    set_tenant_id(test_tenant_id)
    return test_tenant_id


@pytest.fixture
def auth_headers(tenant_id):
    """Create auth headers with tenant context."""
    return {
        "Authorization": "Bearer test_token",
        "X-Tenant-ID": tenant_id,
    }


class TestNotificationAPI:
    """Test notification API endpoints."""

    def test_create_notification(self, client, auth_headers, tenant_id):
        """Test creating a notification via API."""
        payload = {
            "recipient_id": "customer_123",
            "recipient_type": "customer",
            "notification_type": "appointment_confirmation",
            "channel": "email",
            "content": "Your appointment is confirmed",
            "subject": "Appointment Confirmation",
            "recipient_email": "customer@example.com",
        }

        response = client.post(
            "/v1/notifications",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["recipient_id"] == "customer_123"
        assert data["notification_type"] == "appointment_confirmation"
        assert data["status"] == "pending"

    def test_get_notification(self, client, auth_headers, tenant_id):
        """Test retrieving a notification via API."""
        # Create notification
        payload = {
            "recipient_id": "customer_123",
            "recipient_type": "customer",
            "notification_type": "appointment_confirmation",
            "channel": "email",
            "content": "Your appointment is confirmed",
            "recipient_email": "customer@example.com",
        }

        create_response = client.post(
            "/v1/notifications",
            json=payload,
            headers=auth_headers,
        )
        notification_id = create_response.json()["id"]

        # Get notification
        response = client.get(
            f"/v1/notifications/{notification_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == notification_id
        assert data["recipient_id"] == "customer_123"

    def test_list_notifications(self, client, auth_headers, tenant_id):
        """Test listing notifications via API."""
        # Create multiple notifications
        for i in range(3):
            payload = {
                "recipient_id": f"customer_{i}",
                "recipient_type": "customer",
                "notification_type": "appointment_confirmation",
                "channel": "email",
                "content": f"Appointment {i} confirmed",
                "recipient_email": f"customer{i}@example.com",
            }
            client.post(
                "/v1/notifications",
                json=payload,
                headers=auth_headers,
            )

        # List notifications
        response = client.get(
            "/v1/notifications",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_notifications_with_filter(self, client, auth_headers, tenant_id):
        """Test listing notifications with filters."""
        # Create notifications with different types
        for notification_type in [
            "appointment_confirmation",
            "appointment_reminder_24h",
        ]:
            payload = {
                "recipient_id": "customer_123",
                "recipient_type": "customer",
                "notification_type": notification_type,
                "channel": "email",
                "content": f"{notification_type} notification",
                "recipient_email": "customer@example.com",
            }
            client.post(
                "/v1/notifications",
                json=payload,
                headers=auth_headers,
            )

        # Filter by type
        response = client.get(
            "/v1/notifications?notification_type=appointment_confirmation",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["notification_type"] == "appointment_confirmation"

    def test_mark_notification_read(self, client, auth_headers, tenant_id):
        """Test marking notification as read."""
        # Create notification
        payload = {
            "recipient_id": "customer_123",
            "recipient_type": "customer",
            "notification_type": "appointment_confirmation",
            "channel": "email",
            "content": "Your appointment is confirmed",
            "recipient_email": "customer@example.com",
        }

        create_response = client.post(
            "/v1/notifications",
            json=payload,
            headers=auth_headers,
        )
        notification_id = create_response.json()["id"]

        # Mark as read
        response = client.patch(
            f"/v1/notifications/{notification_id}/read",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_read"] is True
        assert data["read_at"] is not None

    def test_mark_notification_sent(self, client, auth_headers, tenant_id):
        """Test marking notification as sent."""
        # Create notification
        payload = {
            "recipient_id": "customer_123",
            "recipient_type": "customer",
            "notification_type": "appointment_confirmation",
            "channel": "email",
            "content": "Your appointment is confirmed",
            "recipient_email": "customer@example.com",
        }

        create_response = client.post(
            "/v1/notifications",
            json=payload,
            headers=auth_headers,
        )
        notification_id = create_response.json()["id"]

        # Mark as sent
        response = client.patch(
            f"/v1/notifications/{notification_id}/sent",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "sent"
        assert data["sent_at"] is not None

    def test_mark_notification_failed(self, client, auth_headers, tenant_id):
        """Test marking notification as failed."""
        # Create notification
        payload = {
            "recipient_id": "customer_123",
            "recipient_type": "customer",
            "notification_type": "appointment_confirmation",
            "channel": "email",
            "content": "Your appointment is confirmed",
            "recipient_email": "customer@example.com",
        }

        create_response = client.post(
            "/v1/notifications",
            json=payload,
            headers=auth_headers,
        )
        notification_id = create_response.json()["id"]

        # Mark as failed
        response = client.patch(
            f"/v1/notifications/{notification_id}/failed?reason=Email+service+unavailable",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["failure_reason"] == "Email service unavailable"


class TestNotificationPreferencesAPI:
    """Test notification preferences API."""

    def test_set_preference(self, client, auth_headers, tenant_id):
        """Test setting notification preference via API."""
        payload = {
            "customer_id": "customer_123",
            "notification_type": "appointment_reminder_24h",
            "channel": "email",
            "enabled": False,
        }

        response = client.post(
            "/v1/notifications/preferences",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "customer_123"
        assert data["enabled"] is False

    def test_get_customer_preferences(self, client, auth_headers, tenant_id):
        """Test getting customer preferences via API."""
        # Set multiple preferences
        for i in range(2):
            payload = {
                "customer_id": "customer_123",
                "notification_type": f"appointment_type_{i}",
                "channel": "email",
                "enabled": i % 2 == 0,
            }
            client.post(
                "/v1/notifications/preferences",
                json=payload,
                headers=auth_headers,
            )

        # Get preferences
        response = client.get(
            "/v1/notifications/preferences/customer_123",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestNotificationTemplatesAPI:
    """Test notification templates API."""

    def test_create_template(self, client, auth_headers, tenant_id):
        """Test creating a template via API."""
        payload = {
            "template_type": "appointment_confirmation",
            "channel": "email",
            "subject": "Appointment Confirmed",
            "body": "Your appointment with {{staff_name}} is confirmed",
            "variables": ["staff_name", "appointment_time"],
        }

        response = client.post(
            "/v1/notifications/templates",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["template_type"] == "appointment_confirmation"
        assert data["channel"] == "email"
        assert len(data["variables"]) == 2

    def test_list_templates(self, client, auth_headers, tenant_id):
        """Test listing templates via API."""
        # Create multiple templates
        for i in range(2):
            payload = {
                "template_type": f"template_type_{i}",
                "channel": "email",
                "subject": f"Subject {i}",
                "body": f"Body {i}",
            }
            client.post(
                "/v1/notifications/templates",
                json=payload,
                headers=auth_headers,
            )

        # List templates
        response = client.get(
            "/v1/notifications/templates",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_template(self, client, auth_headers, tenant_id):
        """Test getting a specific template via API."""
        # Create template
        payload = {
            "template_type": "appointment_confirmation",
            "channel": "email",
            "subject": "Appointment Confirmed",
            "body": "Your appointment is confirmed",
        }

        client.post(
            "/v1/notifications/templates",
            json=payload,
            headers=auth_headers,
        )

        # Get template
        response = client.get(
            "/v1/notifications/templates/appointment_confirmation/email",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["template_type"] == "appointment_confirmation"
        assert data["channel"] == "email"

    def test_update_template(self, client, auth_headers, tenant_id):
        """Test updating a template via API."""
        # Create template
        create_payload = {
            "template_type": "appointment_confirmation",
            "channel": "email",
            "subject": "Appointment Confirmed",
            "body": "Your appointment is confirmed",
        }

        create_response = client.post(
            "/v1/notifications/templates",
            json=create_payload,
            headers=auth_headers,
        )
        template_id = create_response.json()["id"]

        # Update template
        update_payload = {
            "template_type": "appointment_confirmation",
            "channel": "email",
            "subject": "Updated Subject",
            "body": "Updated body with {{variable}}",
            "variables": ["variable"],
        }

        response = client.put(
            f"/v1/notifications/templates/{template_id}",
            json=update_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["body"] == "Updated body with {{variable}}"
