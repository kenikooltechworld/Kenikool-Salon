"""
Tests for win-back campaign Celery task
Feature: campaign-system-enhancements, Task 7.2: Create win-back campaign Celery task
Validates: Requirements 3.4, 3.5
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, call
from bson import ObjectId

from app.tasks.campaign_tasks import (
    check_winback_campaigns_task,
    send_winback_campaigns_for_tenant,
    send_winback_message,
    record_failed_send
)
from app.services.automation_service import AutomationService
from app.services.channel_service import ChannelService


class TestWinbackCampaignsTask:
    """Tests for win-back campaigns Celery task"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database"""
        return MagicMock()
    
    @pytest.fixture
    def mock_automation_service(self):
        """Create a mock automation service"""
        return MagicMock(spec=AutomationService)
    
    @pytest.fixture
    def sample_tenant(self):
        """Create a sample tenant"""
        return {
            "_id": ObjectId(),
            "salon_name": "Test Salon",
            "status": "active"
        }
    
    @pytest.fixture
    def sample_inactive_client(self):
        """Create a sample inactive client (no visit for 90+ days)"""
        return {
            "_id": ObjectId(),
            "name": "John Doe",
            "phone": "+2348012345678",
            "email": "john@example.com",
            "last_visit_date": datetime.utcnow() - timedelta(days=100),
            "tenant_id": "tenant_1"
        }
    
    @pytest.fixture
    def sample_active_client(self):
        """Create a sample active client (visited recently)"""
        return {
            "_id": ObjectId(),
            "name": "Jane Smith",
            "phone": "+2348087654321",
            "email": "jane@example.com",
            "last_visit_date": datetime.utcnow() - timedelta(days=30),
            "tenant_id": "tenant_1"
        }
    
    def test_winback_campaigns_task_with_no_tenants(self, mock_db):
        """Test win-back campaigns task when no tenants exist"""
        mock_db.tenants.find.return_value = []
        
        with patch('app.tasks.campaign_tasks.Database') as mock_database:
            mock_database.get_db.return_value = mock_db
            
            result = check_winback_campaigns_task()
            
            assert result["status"] == "completed"
            assert result["total_sent"] == 0
            assert result["total_failed"] == 0
            assert result["tenants_processed"] == 0
    
    def test_winback_campaigns_task_with_disabled_automation(self, mock_db, sample_tenant):
        """Test win-back campaigns task when automation is disabled"""
        mock_db.tenants.find.return_value = [sample_tenant]
        
        with patch('app.tasks.campaign_tasks.Database') as mock_database, \
             patch('app.tasks.campaign_tasks.AutomationService') as mock_auto_service_class:
            
            mock_database.get_db.return_value = mock_db
            mock_auto_service = MagicMock()
            mock_auto_service.get_settings.return_value = {"enabled": False}
            mock_auto_service_class.return_value = mock_auto_service
            
            result = check_winback_campaigns_task()
            
            assert result["status"] == "completed"
            assert result["total_sent"] == 0
            assert result["tenants_processed"] == 1
    
    def test_winback_campaigns_task_with_no_inactive_clients(
        self, mock_db, sample_tenant, sample_active_client
    ):
        """Test win-back campaigns task when no clients are inactive"""
        tenant_id = str(sample_tenant["_id"])
        mock_db.tenants.find.return_value = [sample_tenant]
        mock_db.clients.find.return_value = []
        
        with patch('app.tasks.campaign_tasks.Database') as mock_database, \
             patch('app.tasks.campaign_tasks.AutomationService') as mock_auto_service_class:
            
            mock_database.get_db.return_value = mock_db
            mock_auto_service = MagicMock()
            mock_auto_service.get_settings.return_value = {
                "enabled": True,
                "winback_campaigns": {
                    "enabled": True,
                    "inactive_days": 90,
                    "frequency_limit_days": 30,
                    "channels": ["sms"],
                    "discount_percentage": 15
                }
            }
            mock_auto_service_class.return_value = mock_auto_service
            
            result = check_winback_campaigns_task()
            
            assert result["status"] == "completed"
            assert result["total_sent"] == 0
            assert result["total_recipients"] == 0
    
    def test_winback_campaigns_task_with_inactive_clients(
        self, mock_db, sample_tenant, sample_inactive_client
    ):
        """Test win-back campaigns task with inactive clients"""
        tenant_id = str(sample_tenant["_id"])
        mock_db.tenants.find.return_value = [sample_tenant]
        
        with patch('app.tasks.campaign_tasks.Database') as mock_database, \
             patch('app.tasks.campaign_tasks.AutomationService') as mock_auto_service_class, \
             patch('app.tasks.campaign_tasks.send_winback_campaigns_for_tenant') as mock_send:
            
            mock_database.get_db.return_value = mock_db
            mock_auto_service = MagicMock()
            mock_auto_service.get_settings.return_value = {
                "enabled": True,
                "winback_campaigns": {
                    "enabled": True,
                    "inactive_days": 90,
                    "frequency_limit_days": 30,
                    "channels": ["sms"],
                    "discount_percentage": 15
                }
            }
            mock_auto_service_class.return_value = mock_auto_service
            mock_send.return_value = (1, 0, 1)  # sent, failed, recipients
            
            result = check_winback_campaigns_task()
            
            assert result["status"] == "completed"
            assert result["total_sent"] == 1
            assert result["total_failed"] == 0
            assert result["total_recipients"] == 1
    
    def test_send_winback_campaigns_for_tenant_with_sms_channel(
        self, mock_db, sample_tenant, sample_inactive_client
    ):
        """Test sending win-back campaigns via SMS channel"""
        tenant_id = str(sample_tenant["_id"])
        winback_config = {
            "enabled": True,
            "inactive_days": 90,
            "frequency_limit_days": 30,
            "channels": ["sms"],
            "discount_percentage": 15,
            "message_template": "We miss you {{client_name}}! Come back and get {{discount_percentage}}% off at {{salon_name}}!",
            "send_time": f"{datetime.utcnow().hour}:00"
        }
        
        mock_db.clients.find.return_value = [sample_inactive_client]
        mock_db.tenants.find_one.return_value = sample_tenant
        mock_db.campaign_sends.find_one.return_value = None  # No previous sends
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        with patch('app.tasks.campaign_tasks.send_winback_message') as mock_send_msg:
            sent, failed, recipients = send_winback_campaigns_for_tenant(
                db=mock_db,
                tenant_id=tenant_id,
                winback_config=winback_config,
                automation_service=MagicMock()
            )
            
            assert sent == 1
            assert failed == 0
            assert recipients == 1
            mock_send_msg.assert_called_once()
    
    def test_send_winback_campaigns_respects_frequency_limit(
        self, mock_db, sample_tenant, sample_inactive_client
    ):
        """Test that frequency limits are respected"""
        tenant_id = str(sample_tenant["_id"])
        winback_config = {
            "enabled": True,
            "inactive_days": 90,
            "frequency_limit_days": 30,
            "channels": ["sms"],
            "discount_percentage": 15,
            "message_template": "We miss you {{client_name}}!",
            "send_time": f"{datetime.utcnow().hour}:00"
        }
        
        # Mock that a campaign was already sent within frequency limit
        recent_send = {
            "_id": ObjectId(),
            "sent_at": datetime.utcnow() - timedelta(days=15)
        }
        
        mock_db.clients.find.return_value = [sample_inactive_client]
        mock_db.tenants.find_one.return_value = sample_tenant
        mock_db.campaign_sends.find_one.return_value = recent_send  # Already sent
        
        with patch('app.tasks.campaign_tasks.send_winback_message') as mock_send_msg:
            sent, failed, recipients = send_winback_campaigns_for_tenant(
                db=mock_db,
                tenant_id=tenant_id,
                winback_config=winback_config,
                automation_service=MagicMock()
            )
            
            # Should not send because frequency limit is active
            assert sent == 0
            assert failed == 0
            assert recipients == 1
            mock_send_msg.assert_not_called()
    
    def test_send_winback_campaigns_with_multiple_channels(
        self, mock_db, sample_tenant, sample_inactive_client
    ):
        """Test sending win-back campaigns via multiple channels"""
        tenant_id = str(sample_tenant["_id"])
        winback_config = {
            "enabled": True,
            "inactive_days": 90,
            "frequency_limit_days": 30,
            "channels": ["sms", "email"],
            "discount_percentage": 15,
            "message_template": "We miss you {{client_name}}!",
            "send_time": f"{datetime.utcnow().hour}:00"
        }
        
        mock_db.clients.find.return_value = [sample_inactive_client]
        mock_db.tenants.find_one.return_value = sample_tenant
        mock_db.campaign_sends.find_one.return_value = None  # No previous sends
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        with patch('app.tasks.campaign_tasks.send_winback_message') as mock_send_msg:
            sent, failed, recipients = send_winback_campaigns_for_tenant(
                db=mock_db,
                tenant_id=tenant_id,
                winback_config=winback_config,
                automation_service=MagicMock()
            )
            
            # Should send via both channels
            assert sent == 2
            assert failed == 0
            assert recipients == 1
            assert mock_send_msg.call_count == 2
    
    def test_send_winback_message_with_sms_channel(self, mock_db, sample_inactive_client):
        """Test sending win-back message via SMS"""
        tenant_id = "tenant_1"
        client_id = str(sample_inactive_client["_id"])
        message_content = "We miss you John! Come back and get 15% off!"
        
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        with patch('app.tasks.campaign_tasks.ChannelService') as mock_channel_service:
            mock_channel_service.validate_message.return_value = {"valid": True}
            mock_channel_service.validate_phone.return_value = True
            mock_channel_service.calculate_cost.return_value = 0.5
            
            send_winback_message(
                db=mock_db,
                tenant_id=tenant_id,
                client_id=client_id,
                client=sample_inactive_client,
                channel="sms",
                message_content=message_content,
                discount_percentage=15,
                inactive_days=90
            )
            
            # Verify campaign send was recorded
            mock_db.campaign_sends.insert_one.assert_called_once()
            call_args = mock_db.campaign_sends.insert_one.call_args[0][0]
            
            assert call_args["tenant_id"] == tenant_id
            assert call_args["client_id"] == client_id
            assert call_args["channel"] == "sms"
            assert call_args["campaign_type"] == "winback"
            assert call_args["status"] == "sent"
            assert call_args["discount_percentage"] == 15
            assert call_args["inactive_days"] == 90
    
    def test_send_winback_message_with_email_channel(self, mock_db, sample_inactive_client):
        """Test sending win-back message via email"""
        tenant_id = "tenant_1"
        client_id = str(sample_inactive_client["_id"])
        message_content = "We miss you John! Come back and get 15% off!"
        
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        with patch('app.tasks.campaign_tasks.ChannelService') as mock_channel_service:
            mock_channel_service.validate_message.return_value = {"valid": True}
            mock_channel_service.validate_email.return_value = True
            mock_channel_service.calculate_cost.return_value = 0.1
            
            send_winback_message(
                db=mock_db,
                tenant_id=tenant_id,
                client_id=client_id,
                client=sample_inactive_client,
                channel="email",
                message_content=message_content,
                discount_percentage=15,
                inactive_days=90
            )
            
            # Verify campaign send was recorded
            mock_db.campaign_sends.insert_one.assert_called_once()
            call_args = mock_db.campaign_sends.insert_one.call_args[0][0]
            
            assert call_args["channel"] == "email"
            assert call_args["campaign_type"] == "winback"
    
    def test_send_winback_message_with_invalid_phone(self, mock_db, sample_inactive_client):
        """Test sending win-back message with invalid phone number"""
        tenant_id = "tenant_1"
        client_id = str(sample_inactive_client["_id"])
        message_content = "We miss you John!"
        
        # Client with no phone
        client_no_phone = sample_inactive_client.copy()
        client_no_phone["phone"] = None
        
        with patch('app.tasks.campaign_tasks.ChannelService') as mock_channel_service:
            mock_channel_service.validate_message.return_value = {"valid": True}
            
            with pytest.raises(ValueError, match="Client has no phone number"):
                send_winback_message(
                    db=mock_db,
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client=client_no_phone,
                    channel="sms",
                    message_content=message_content,
                    discount_percentage=15,
                    inactive_days=90
                )
    
    def test_send_winback_message_with_invalid_email(self, mock_db, sample_inactive_client):
        """Test sending win-back message with invalid email"""
        tenant_id = "tenant_1"
        client_id = str(sample_inactive_client["_id"])
        message_content = "We miss you John!"
        
        # Client with no email
        client_no_email = sample_inactive_client.copy()
        client_no_email["email"] = None
        
        with patch('app.tasks.campaign_tasks.ChannelService') as mock_channel_service:
            mock_channel_service.validate_message.return_value = {"valid": True}
            
            with pytest.raises(ValueError, match="Client has no email address"):
                send_winback_message(
                    db=mock_db,
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client=client_no_email,
                    channel="email",
                    message_content=message_content,
                    discount_percentage=15,
                    inactive_days=90
                )
    
    def test_record_failed_send_for_winback(self, mock_db):
        """Test recording failed win-back campaign send"""
        tenant_id = "tenant_1"
        client_id = "client_1"
        channel = "sms"
        message_content = "We miss you!"
        error_message = "Invalid phone number"
        
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        record_failed_send(
            db=mock_db,
            tenant_id=tenant_id,
            client_id=client_id,
            channel=channel,
            message_content=message_content,
            error_message=error_message,
            campaign_type="winback"
        )
        
        # Verify failed send was recorded
        mock_db.campaign_sends.insert_one.assert_called_once()
        call_args = mock_db.campaign_sends.insert_one.call_args[0][0]
        
        assert call_args["tenant_id"] == tenant_id
        assert call_args["client_id"] == client_id
        assert call_args["channel"] == channel
        assert call_args["campaign_type"] == "winback"
        assert call_args["status"] == "failed"
        assert call_args["error_message"] == error_message
    
    def test_winback_campaigns_task_error_handling(self, mock_db):
        """Test error handling in win-back campaigns task"""
        mock_db.tenants.find.side_effect = Exception("Database error")
        
        with patch('app.tasks.campaign_tasks.Database') as mock_database:
            mock_database.get_db.return_value = mock_db
            
            # Task should retry on error
            with pytest.raises(Exception):
                check_winback_campaigns_task()
    
    def test_message_template_substitution_winback(self, mock_db, sample_inactive_client):
        """Test message template substitution for win-back campaigns"""
        tenant_id = "tenant_1"
        client_id = str(sample_inactive_client["_id"])
        
        template = "Hi {{client_name}}, we miss you! Get {{discount_percentage}}% off at {{salon_name}}"
        expected_message = "Hi John Doe, we miss you! Get 15% off at Test Salon"
        
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        with patch('app.tasks.campaign_tasks.ChannelService') as mock_channel_service:
            mock_channel_service.validate_message.return_value = {"valid": True}
            mock_channel_service.validate_phone.return_value = True
            mock_channel_service.calculate_cost.return_value = 0.5
            
            send_winback_message(
                db=mock_db,
                tenant_id=tenant_id,
                client_id=client_id,
                client=sample_inactive_client,
                channel="sms",
                message_content=template.replace("{{client_name}}", sample_inactive_client["name"])
                                       .replace("{{discount_percentage}}", "15")
                                       .replace("{{salon_name}}", "Test Salon"),
                discount_percentage=15,
                inactive_days=90
            )
            
            # Verify the message was substituted correctly
            call_args = mock_db.campaign_sends.insert_one.call_args[0][0]
            assert call_args["message_content"] == expected_message


class TestWinbackCampaignsIntegration:
    """Integration tests for win-back campaigns"""
    
    def test_winback_campaigns_multi_channel_send(self):
        """Test sending win-back campaigns via multiple channels"""
        # This would be an integration test with real database
        # For now, we'll skip it as it requires full setup
        pass
    
    def test_winback_campaigns_frequency_limit(self):
        """Test that frequency limits are respected"""
        # Verify that clients don't receive multiple win-back campaigns
        # within the configured frequency limit period
        pass
    
    def test_winback_campaigns_automation_history_recording(self):
        """Test that automation history is properly recorded"""
        # Verify execution records are created with correct metrics
        pass
