"""
Tests for Package Notification Service
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock

from app.services.package_notification_service import PackageNotificationService


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = Mock()
    db.clients = Mock()
    return db


class TestSendPurchaseConfirmation:
    """Tests for send_purchase_confirmation method"""
    
    def test_send_purchase_confirmation_success(self, mock_db):
        """Should send purchase confirmation notification"""
        client_id = ObjectId()
        
        mock_db.clients.find_one.return_value = {
            "_id": client_id,
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        with patch('app.services.package_notification_service.Database.get_db', return_value=mock_db):
            with patch('app.services.package_notification_service.NotificationService') as mock_notification:
                result = PackageNotificationService.send_purchase_confirmation(
                    tenant_id="tenant123",
                    client_id=str(client_id),
                    purchase_id="purchase123",
                    package_name="3 Haircuts",
                    amount_paid=150.0,
                    expiration_date=datetime.utcnow() + timedelta(days=30)
                )
        
        assert result is True
        mock_db.clients.find_one.assert_called_once()
    
    def test_send_purchase_confirmation_client_not_found(self, mock_db):
        """Should return False when client not found"""
        mock_db.clients.find_one.return_value = None
        
        with patch('app.services.package_notification_service.Database.get_db', return_value=mock_db):
            result = PackageNotificationService.send_purchase_confirmation(
                tenant_id="tenant123",
                client_id="client123",
                purchase_id="purchase123",
                package_name="3 Haircuts",
                amount_paid=150.0,
                expiration_date=datetime.utcnow() + timedelta(days=30)
            )
        
        assert result is False


class TestSendExpirationWarning:
    """Tests for send_expiration_warning method"""
    
    def test_send_expiration_warning_success(self, mock_db):
        """Should send expiration warning notification"""
        client_id = ObjectId()
        
        mock_db.clients.find_one.return_value = {
            "_id": client_id,
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        with patch('app.services.package_notification_service.Database.get_db', return_value=mock_db):
            with patch('app.services.package_notification_service.NotificationService'):
                result = PackageNotificationService.send_expiration_warning(
                    tenant_id="tenant123",
                    client_id=str(client_id),
                    purchase_id="purchase123",
                    package_name="3 Haircuts",
                    expiration_date=datetime.utcnow() + timedelta(days=7),
                    remaining_credits={"Haircut": 2, "Massage": 1}
                )
        
        assert result is True


class TestSendExpirationNotice:
    """Tests for send_expiration_notice method"""
    
    def test_send_expiration_notice_success(self, mock_db):
        """Should send expiration notice notification"""
        client_id = ObjectId()
        
        mock_db.clients.find_one.return_value = {
            "_id": client_id,
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        with patch('app.services.package_notification_service.Database.get_db', return_value=mock_db):
            with patch('app.services.package_notification_service.NotificationService'):
                result = PackageNotificationService.send_expiration_notice(
                    tenant_id="tenant123",
                    client_id=str(client_id),
                    purchase_id="purchase123",
                    package_name="3 Haircuts",
                    expiration_date=datetime.utcnow(),
                    unused_value=50.0
                )
        
        assert result is True


class TestSendCompletionNotice:
    """Tests for send_completion_notice method"""
    
    def test_send_completion_notice_success(self, mock_db):
        """Should send completion notice notification"""
        client_id = ObjectId()
        
        mock_db.clients.find_one.return_value = {
            "_id": client_id,
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        with patch('app.services.package_notification_service.Database.get_db', return_value=mock_db):
            with patch('app.services.package_notification_service.NotificationService'):
                result = PackageNotificationService.send_completion_notice(
                    tenant_id="tenant123",
                    client_id=str(client_id),
                    purchase_id="purchase123",
                    package_name="3 Haircuts"
                )
        
        assert result is True


class TestSendGiftNotification:
    """Tests for send_gift_notification method"""
    
    def test_send_gift_notification_success(self, mock_db):
        """Should send gift notification"""
        recipient_id = ObjectId()
        
        mock_db.clients.find_one.return_value = {
            "_id": recipient_id,
            "name": "Jane Doe",
            "email": "jane@example.com"
        }
        
        with patch('app.services.package_notification_service.Database.get_db', return_value=mock_db):
            with patch('app.services.package_notification_service.NotificationService'):
                result = PackageNotificationService.send_gift_notification(
                    tenant_id="tenant123",
                    recipient_client_id=str(recipient_id),
                    purchase_id="purchase123",
                    package_name="3 Haircuts",
                    gift_from_name="John Doe",
                    gift_message="Enjoy!"
                )
        
        assert result is True
    
    def test_send_gift_notification_without_message(self, mock_db):
        """Should send gift notification without message"""
        recipient_id = ObjectId()
        
        mock_db.clients.find_one.return_value = {
            "_id": recipient_id,
            "name": "Jane Doe",
            "email": "jane@example.com"
        }
        
        with patch('app.services.package_notification_service.Database.get_db', return_value=mock_db):
            with patch('app.services.package_notification_service.NotificationService'):
                result = PackageNotificationService.send_gift_notification(
                    tenant_id="tenant123",
                    recipient_client_id=str(recipient_id),
                    purchase_id="purchase123",
                    package_name="3 Haircuts",
                    gift_from_name="John Doe"
                )
        
        assert result is True


class TestSendTransferNotification:
    """Tests for send_transfer_notification method"""
    
    def test_send_transfer_notification_success(self, mock_db):
        """Should send transfer notifications to both clients"""
        from_client_id = ObjectId()
        to_client_id = ObjectId()
        
        mock_db.clients.find_one.side_effect = [
            {
                "_id": from_client_id,
                "name": "John Doe",
                "email": "john@example.com"
            },
            {
                "_id": to_client_id,
                "name": "Jane Doe",
                "email": "jane@example.com"
            }
        ]
        
        with patch('app.services.package_notification_service.Database.get_db', return_value=mock_db):
            with patch('app.services.package_notification_service.NotificationService'):
                result = PackageNotificationService.send_transfer_notification(
                    tenant_id="tenant123",
                    from_client_id=str(from_client_id),
                    to_client_id=str(to_client_id),
                    purchase_id="purchase123",
                    package_name="3 Haircuts"
                )
        
        assert result is True
        assert mock_db.clients.find_one.call_count == 2
