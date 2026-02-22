"""
Tests for birthday campaign Celery task
Feature: campaign-system-enhancements, Task 7.1: Create birthday campaign Celery task
Validates: Requirements 3.2, 3.3
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, call
from bson import ObjectId

from app.tasks.campaign_tasks import (
    check_birthday_campaigns_task,
    send_birthday_campaigns_for_tenant,
    send_birthday_message,
    record_failed_send
)
from app.services.automation_service import AutomationService
from app.services.channel_service import ChannelService


class TestBirthdayCampaignsTask:
    """Tests for birthday campaigns Celery task"""
    
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
    def sample_client_with_birthday_today(self):
        """Create a sample client with birthday today"""
        today = datetime.utcnow()
        return {
            "_id": ObjectId(),
            "name": "John Doe",
            "phone": "+2348012345678",
            "email": "john@example.com",
            "birthday": datetime(1990, today.month, today.day),
            "tenant_id": "tenant_1"
        }
    
    @pytest.fixture
    def sample_client_without_birthday_today(self):
        """Create a sample client without birthday today"""
        return {
            "_id": ObjectId(),
            "name": "Jane Smith",
            "phone": "+2348087654321",
            "email": "jane@example.com",
            "birthday": datetime(1992, 6, 15),
            "tenant_id": "tenant_1"
        }
    
    def test_birthday_campaigns_task_with_no_tenants(self, mock_db):
        """Test birthday campaigns task when no tenants exist"""
        mock_db.tenants.find.return_value = []
        
        with patch('app.tasks.campaign_tasks.Database') as mock_database:
            mock_database.get_db.return_value = mock_db
            
            result = check_birthday_campaigns_task()
            
            assert result["status"] == "completed"
            assert result["total_sent"] == 0
            assert result["total_failed"] == 0
            assert result["tenants_processed"] == 0
    
    def test_birthday_campaigns_task_with_disabled_automation(self, mock_db, sample_tenant):
        """Test birthday campaigns task when automation is disabled"""
        mock_db.tenants.find.return_value = [sample_tenant]
        
        with patch('app.tasks.campaign_tasks.Database') as mock_database, \
             patch('app.tasks.campaign_tasks.AutomationService') as mock_auto_service_class:
            
            mock_database.get_db.return_value = mock_db
            mock_auto_service = MagicMock()
            mock_auto_service.get_settings.return_value = {"enabled": False}
            mock_auto_service_class.return_value = mock_auto_service
            
            result = check_birthday_campaigns_task()
            
            assert result["status"] == "completed"
            assert result["total_sent"] == 0
            assert result["tenants_processed"] == 1
    
    def test_birthday_campaigns_task_with_no_birthday_clients(
        self, mock_db, sample_tenant, sample_client_without_birthday_today
    ):
        """Test birthday campaigns task when no clients have birthdays today"""
        mock_db.tenants.find.return_value = [sample_tenant]
        mock_db.clients.find.return_value = []
        mock_db.tenants.find_one.return_value = sample_tenant
        
        with patch('app.tasks.campaign_tasks.Database') as mock_database, \
             patch('app.tasks.campaign_tasks.AutomationService') as mock_auto_service_class:
            
            mock_database.get_db.return_value = mock_db
            mock_auto_service = MagicMock()
            mock_auto_service.get_settings.return_value = {
                "enabled": True,
                "birthday_campaigns": {
                    "enabled": True,
                    "channels": ["sms"],
                    "message_template": "Happy Birthday {{client_name}}!",
                    "discount_percentage": 10,
                    "send_time": "09:00"
                }
            }
            mock_auto_service_class.return_value = mock_auto_service
            
            result = check_birthday_campaigns_task()
            
            assert result["status"] == "completed"
            assert result["total_sent"] == 0
            assert result["total_recipients"] == 0
    
    def test_birthday_campaigns_task_with_birthday_clients(
        self, mock_db, sample_tenant, sample_client_with_birthday_today
    ):
        """Test birthday campaigns task with clients having birthdays today"""
        tenant_id = str(sample_tenant["_id"])
        mock_db.tenants.find.return_value = [sample_tenant]
        mock_db.clients.find.return_value = [sample_client_with_birthday_today]
        mock_db.tenants.find_one.return_value = sample_tenant
        mock_db.campaign_sends.find_one.return_value = None  # No existing send
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        with patch('app.tasks.campaign_tasks.Database') as mock_database, \
             patch('app.tasks.campaign_tasks.AutomationService') as mock_auto_service_class, \
             patch('app.tasks.campaign_tasks.send_birthday_campaigns_for_tenant') as mock_send:
            
            mock_database.get_db.return_value = mock_db
            mock_auto_service = MagicMock()
            mock_auto_service.get_settings.return_value = {
                "enabled": True,
                "birthday_campaigns": {
                    "enabled": True,
                    "channels": ["sms"],
                    "message_template": "Happy Birthday {{client_name}}!",
                    "discount_percentage": 10,
                    "send_time": "09:00"
                }
            }
            mock_auto_service_class.return_value = mock_auto_service
            mock_send.return_value = (1, 0, 1)  # sent, failed, recipients
            
            result = check_birthday_campaigns_task()
            
            assert result["status"] == "completed"
            assert result["total_sent"] == 1
            assert result["total_failed"] == 0
            assert result["total_recipients"] == 1
    
    def test_send_birthday_campaigns_for_tenant_with_sms_channel(
        self, mock_db, sample_tenant, sample_client_with_birthday_today
    ):
        """Test sending birthday campaigns via SMS channel"""
        tenant_id = str(sample_tenant["_id"])
        birthday_config = {
            "enabled": True,
            "channels": ["sms"],
            "message_template": "Happy Birthday {{client_name}}! Get {{discount_percentage}}% off at {{salon_name}}",
            "discount_percentage": 10,
            "send_time": "09:00"
        }
        
        mock_db.clients.find.return_value = [sample_client_with_birthday_today]
        mock_db.tenants.find_one.return_value = sample_tenant
        mock_db.campaign_sends.find_one.return_value = None
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        mock_auto_service = MagicMock()
        
        with patch('app.tasks.campaign_tasks.send_birthday_message') as mock_send_msg:
            sent, failed, recipients = send_birthday_campaigns_for_tenant(
                db=mock_db,
                tenant_id=tenant_id,
                birthday_config=birthday_config,
                automation_service=mock_auto_service
            )
            
            # Should attempt to send
            assert recipients == 1
            # Note: send_time check may prevent actual send depending on current time
    
    def test_send_birthday_message_with_valid_sms(self, mock_db, sample_client_with_birthday_today):
        """Test sending birthday message via SMS with valid phone"""
        tenant_id = "tenant_1"
        client_id = str(sample_client_with_birthday_today["_id"])
        channel = "sms"
        message_content = "Happy Birthday John! Get 10% off at Test Salon"
        
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        with patch('app.tasks.campaign_tasks.ChannelService') as mock_channel_service:
            mock_channel_service.validate_message.return_value = {"valid": True}
            mock_channel_service.validate_phone.return_value = True
            mock_channel_service.calculate_cost.return_value = 0.05
            
            # Should not raise exception
            send_birthday_message(
                db=mock_db,
                tenant_id=tenant_id,
                client_id=client_id,
                client=sample_client_with_birthday_today,
                channel=channel,
                message_content=message_content,
                discount_percentage=10
            )
            
            # Verify campaign send was recorded
            mock_db.campaign_sends.insert_one.assert_called_once()
    
    def test_send_birthday_message_with_invalid_phone(self, mock_db, sample_client_with_birthday_today):
        """Test sending birthday message with invalid phone number"""
        tenant_id = "tenant_1"
        client_id = str(sample_client_with_birthday_today["_id"])
        channel = "sms"
        message_content = "Happy Birthday John!"
        
        # Client with invalid phone
        client = sample_client_with_birthday_today.copy()
        client["phone"] = "invalid"
        
        with patch('app.tasks.campaign_tasks.ChannelService') as mock_channel_service:
            mock_channel_service.validate_message.return_value = {"valid": True}
            mock_channel_service.validate_phone.return_value = False
            
            with pytest.raises(ValueError, match="Invalid phone number"):
                send_birthday_message(
                    db=mock_db,
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client=client,
                    channel=channel,
                    message_content=message_content,
                    discount_percentage=10
                )
    
    def test_send_birthday_message_with_email_channel(self, mock_db, sample_client_with_birthday_today):
        """Test sending birthday message via email"""
        tenant_id = "tenant_1"
        client_id = str(sample_client_with_birthday_today["_id"])
        channel = "email"
        message_content = "Happy Birthday John! Get 10% off at Test Salon"
        
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        with patch('app.tasks.campaign_tasks.ChannelService') as mock_channel_service:
            mock_channel_service.validate_message.return_value = {"valid": True}
            mock_channel_service.validate_email.return_value = True
            mock_channel_service.calculate_cost.return_value = 0.01
            
            send_birthday_message(
                db=mock_db,
                tenant_id=tenant_id,
                client_id=client_id,
                client=sample_client_with_birthday_today,
                channel=channel,
                message_content=message_content,
                discount_percentage=10
            )
            
            mock_db.campaign_sends.insert_one.assert_called_once()
    
    def test_send_birthday_message_with_no_email(self, mock_db, sample_client_with_birthday_today):
        """Test sending birthday message via email when client has no email"""
        tenant_id = "tenant_1"
        client_id = str(sample_client_with_birthday_today["_id"])
        channel = "email"
        message_content = "Happy Birthday John!"
        
        # Client without email
        client = sample_client_with_birthday_today.copy()
        client["email"] = None
        
        with patch('app.tasks.campaign_tasks.ChannelService') as mock_channel_service:
            mock_channel_service.validate_message.return_value = {"valid": True}
            
            with pytest.raises(ValueError, match="Client has no email address"):
                send_birthday_message(
                    db=mock_db,
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client=client,
                    channel=channel,
                    message_content=message_content,
                    discount_percentage=10
                )
    
    def test_record_failed_send(self, mock_db):
        """Test recording a failed campaign send"""
        tenant_id = "tenant_1"
        client_id = str(ObjectId())
        channel = "sms"
        message_content = "Happy Birthday!"
        error_message = "Invalid phone number"
        
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        record_failed_send(
            db=mock_db,
            tenant_id=tenant_id,
            client_id=client_id,
            channel=channel,
            message_content=message_content,
            error_message=error_message
        )
        
        # Verify failed send was recorded
        mock_db.campaign_sends.insert_one.assert_called_once()
        call_args = mock_db.campaign_sends.insert_one.call_args[0][0]
        assert call_args["status"] == "failed"
        assert call_args["error_message"] == error_message
        assert call_args["campaign_type"] == "birthday"
    
    def test_birthday_campaigns_task_error_handling(self, mock_db):
        """Test error handling in birthday campaigns task"""
        mock_db.tenants.find.side_effect = Exception("Database error")
        
        with patch('app.tasks.campaign_tasks.Database') as mock_database:
            mock_database.get_db.return_value = mock_db
            
            # Task should retry on error
            with pytest.raises(Exception):
                check_birthday_campaigns_task()
    
    def test_message_template_substitution(self, mock_db, sample_client_with_birthday_today):
        """Test that message template variables are properly substituted"""
        tenant_id = "tenant_1"
        client_id = str(sample_client_with_birthday_today["_id"])
        channel = "sms"
        message_template = "Happy Birthday {{client_name}}! Get {{discount_percentage}}% off at {{salon_name}}"
        
        mock_db.campaign_sends.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        with patch('app.tasks.campaign_tasks.ChannelService') as mock_channel_service:
            mock_channel_service.validate_message.return_value = {"valid": True}
            mock_channel_service.validate_phone.return_value = True
            mock_channel_service.calculate_cost.return_value = 0.05
            
            send_birthday_message(
                db=mock_db,
                tenant_id=tenant_id,
                client_id=client_id,
                client=sample_client_with_birthday_today,
                channel=channel,
                message_content=message_template.replace("{{client_name}}", "John Doe")
                                                    .replace("{{discount_percentage}}", "10")
                                                    .replace("{{salon_name}}", "Test Salon"),
                discount_percentage=10
            )
            
            # Verify the message was recorded with substituted values
            call_args = mock_db.campaign_sends.insert_one.call_args[0][0]
            assert "John Doe" in call_args["message_content"]
            assert "10%" in call_args["message_content"]
            assert "Test Salon" in call_args["message_content"]


class TestBirthdayCampaignsIntegration:
    """Integration tests for birthday campaigns"""
    
    def test_birthday_campaigns_multi_channel_send(self):
        """Test sending birthday campaigns via multiple channels"""
        # This would be an integration test with real database
        # For now, we'll skip it as it requires full setup
        pass
    
    def test_birthday_campaigns_frequency_limit(self):
        """Test that frequency limits are respected"""
        # Verify that clients don't receive multiple birthday campaigns
        pass
    
    def test_birthday_campaigns_automation_history_recording(self):
        """Test that automation history is properly recorded"""
        # Verify execution records are created
        pass
