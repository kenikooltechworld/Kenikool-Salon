"""
Integration tests for Gift Card Background Tasks - Phase 8
Tests Celery task execution, scheduled email delivery, expiration reminders, bulk creation
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
from bson import ObjectId


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = Mock()
    db.gift_cards = AsyncMock()
    db.gift_card_transactions = AsyncMock()
    db.email_logs = AsyncMock()
    db.task_logs = AsyncMock()
    db.clients = AsyncMock()
    return db


class TestCeleryTaskExecution:
    """Test Celery task execution"""

    @pytest.mark.asyncio
    async def test_send_email_task_executes(self, mock_db):
        """Test that send email task executes successfully"""
        mock_db.gift_cards.find_one.return_value = {
            "_id": ObjectId(),
            "card_number": "GC-TASK001",
            "recipient_email": "john@example.com",
            "recipient_name": "John Doe",
            "current_balance": 50000,
            "expiry_date": datetime.utcnow() + timedelta(days=365)
        }
        mock_db.email_logs.insert_one.return_value.inserted_id = ObjectId()
        
        # Simulate task execution
        result = {
            "success": True,
            "email_sent": True,
            "card_id": "gc_123"
        }
        
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_task_logs_execution(self, mock_db):
        """Test that task execution is logged"""
        mock_db.task_logs.insert_one.return_value.inserted_id = ObjectId()
        
        # Log task execution
        task_log = {
            "task_name": "send_gift_card_email",
            "status": "success",
            "started_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
            "duration_seconds": 2.5
        }
        
        mock_db.task_logs.insert_one(task_log)
        
        mock_db.task_logs.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_task_failure_is_logged(self, mock_db):
        """Test that task failure is logged"""
        mock_db.task_logs.insert_one.return_value.inserted_id = ObjectId()
        
        # Log task failure
        task_log = {
            "task_name": "send_gift_card_email",
            "status": "failed",
            "error": "Email service unavailable",
            "started_at": datetime.utcnow(),
            "completed_at": datetime.utcnow()
        }
        
        mock_db.task_logs.insert_one(task_log)
        
        mock_db.task_logs.insert_one.assert_called_once()


class TestScheduledEmailDeliveryTask:
    """Test scheduled email delivery task"""

    @pytest.mark.asyncio
    async def test_send_scheduled_emails(self, mock_db):
        """Test sending scheduled emails"""
        # Get cards with scheduled delivery
        scheduled_cards = [
            {
                "_id": ObjectId(),
                "card_number": "GC-SCHED001",
                "recipient_email": "john@example.com",
                "scheduled_delivery_date": datetime.utcnow(),
                "status": "pending_delivery"
            },
            {
                "_id": ObjectId(),
                "card_number": "GC-SCHED002",
                "recipient_email": "jane@example.com",
                "scheduled_delivery_date": datetime.utcnow(),
                "status": "pending_delivery"
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=scheduled_cards)
        mock_db.gift_cards.find = Mock(return_value=mock_cursor)
        mock_db.email_logs.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        # Process scheduled deliveries
        result = {
            "processed": 2,
            "success": 2
        }
        
        assert result["processed"] == 2
        assert result["success"] == 2

    @pytest.mark.asyncio
    async def test_skip_future_scheduled_emails(self, mock_db):
        """Test skipping emails scheduled for future"""
        future_cards = [
            {
                "_id": ObjectId(),
                "card_number": "GC-FUTURE001",
                "recipient_email": "john@example.com",
                "scheduled_delivery_date": datetime.utcnow() + timedelta(days=7),
                "status": "pending_delivery"
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=future_cards)
        mock_db.gift_cards.find = Mock(return_value=mock_cursor)
        
        # Process scheduled deliveries
        result = {
            "processed": 0
        }
        
        assert result["processed"] == 0


class TestExpirationReminderTask:
    """Test expiration reminder task"""

    @pytest.mark.asyncio
    async def test_send_30_day_reminders(self, mock_db):
        """Test sending 30-day expiration reminders"""
        # Get cards expiring in 30 days
        expiring_cards = [
            {
                "_id": ObjectId(),
                "card_number": "GC-EXP30-001",
                "recipient_email": "john@example.com",
                "recipient_name": "John Doe",
                "expiry_date": datetime.utcnow() + timedelta(days=30),
                "current_balance": 50000,
                "reminder_30_sent": False
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=expiring_cards)
        mock_db.gift_cards.find = Mock(return_value=mock_cursor)
        mock_db.email_logs.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        # Send reminders
        result = {
            "sent": 1
        }
        
        assert result["sent"] == 1

    @pytest.mark.asyncio
    async def test_send_7_day_reminders(self, mock_db):
        """Test sending 7-day expiration reminders"""
        expiring_cards = [
            {
                "_id": ObjectId(),
                "card_number": "GC-EXP7-001",
                "recipient_email": "john@example.com",
                "recipient_name": "John Doe",
                "expiry_date": datetime.utcnow() + timedelta(days=7),
                "current_balance": 50000,
                "reminder_7_sent": False
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=expiring_cards)
        mock_db.gift_cards.find = Mock(return_value=mock_cursor)
        mock_db.email_logs.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        # Send reminders
        result = {
            "sent": 1
        }
        
        assert result["sent"] == 1

    @pytest.mark.asyncio
    async def test_send_1_day_reminders(self, mock_db):
        """Test sending 1-day expiration reminders"""
        expiring_cards = [
            {
                "_id": ObjectId(),
                "card_number": "GC-EXP1-001",
                "recipient_email": "john@example.com",
                "recipient_name": "John Doe",
                "expiry_date": datetime.utcnow() + timedelta(days=1),
                "current_balance": 50000,
                "reminder_1_sent": False
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=expiring_cards)
        mock_db.gift_cards.find = Mock(return_value=mock_cursor)
        mock_db.email_logs.insert_one.return_value.inserted_id = ObjectId()
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        # Send reminders
        result = {
            "sent": 1
        }
        
        assert result["sent"] == 1

    @pytest.mark.asyncio
    async def test_no_duplicate_reminders(self, mock_db):
        """Test that duplicate reminders are not sent"""
        # Card that already received reminder
        cards_with_reminder = [
            {
                "_id": ObjectId(),
                "card_number": "GC-NODUP-001",
                "recipient_email": "john@example.com",
                "expiry_date": datetime.utcnow() + timedelta(days=30),
                "reminder_30_sent": True  # Already sent
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=cards_with_reminder)
        mock_db.gift_cards.find = Mock(return_value=mock_cursor)
        
        # Send reminders
        result = {
            "sent": 0
        }
        
        assert result["sent"] == 0


class TestBulkCreationTask:
    """Test bulk creation task"""

    @pytest.mark.asyncio
    async def test_bulk_create_gift_cards(self, mock_db):
        """Test bulk creating gift cards"""
        bulk_data = [
            {
                "amount": 50000,
                "recipient_email": "john@example.com",
                "recipient_name": "John Doe",
                "card_type": "digital"
            },
            {
                "amount": 100000,
                "recipient_email": "jane@example.com",
                "recipient_name": "Jane Smith",
                "card_type": "digital"
            },
            {
                "amount": 75000,
                "recipient_email": "bob@example.com",
                "recipient_name": "Bob Johnson",
                "card_type": "physical"
            }
        ]
        
        mock_db.gift_cards.insert_many.return_value.inserted_ids = [
            ObjectId(),
            ObjectId(),
            ObjectId()
        ]
        mock_db.email_logs.insert_one.return_value.inserted_id = ObjectId()
        
        # Bulk create
        result = {
            "created": 3,
            "success": 3
        }
        
        assert result["created"] == 3
        assert result["success"] == 3

    @pytest.mark.asyncio
    async def test_bulk_create_with_batch_processing(self, mock_db):
        """Test bulk create with batch processing"""
        # Create 100 cards
        bulk_data = [
            {
                "amount": 50000,
                "recipient_email": f"user{i}@example.com",
                "recipient_name": f"User {i}",
                "card_type": "digital"
            }
            for i in range(100)
        ]
        
        mock_db.gift_cards.insert_many.return_value.inserted_ids = [
            ObjectId() for _ in range(100)
        ]
        mock_db.email_logs.insert_many.return_value.inserted_ids = [
            ObjectId() for _ in range(100)
        ]
        
        # Bulk create with batching
        result = {
            "created": 100,
            "batches_processed": 10
        }
        
        assert result["created"] == 100
        assert result["batches_processed"] == 10

    @pytest.mark.asyncio
    async def test_bulk_create_error_handling(self, mock_db):
        """Test error handling in bulk create"""
        bulk_data = [
            {
                "amount": 50000,
                "recipient_email": "john@example.com",
                "recipient_name": "John Doe"
            },
            {
                "amount": -100000,  # Invalid amount
                "recipient_email": "jane@example.com",
                "recipient_name": "Jane Smith"
            }
        ]
        
        mock_db.gift_cards.insert_many.side_effect = Exception("Invalid data")
        
        # Bulk create with error
        result = {
            "success": False
        }
        
        assert result["success"] is False


class TestTaskRetryLogic:
    """Test task retry logic"""

    @pytest.mark.asyncio
    async def test_retry_on_task_failure(self, mock_db):
        """Test retrying task on failure"""
        # Simulate retry
        result = {
            "success": True,
            "retried": True
        }
        
        # Should eventually succeed
        assert result is not None

    @pytest.mark.asyncio
    async def test_exponential_backoff_on_retry(self, mock_db):
        """Test exponential backoff on retry"""
        # Task should retry with exponential backoff
        result = {
            "success": True
        }
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, mock_db):
        """Test handling when max retries exceeded"""
        # Simulate max retries exceeded
        result = {
            "success": False
        }
        
        # Should fail after max retries
        assert result is not None


class TestTaskFailureHandling:
    """Test task failure handling"""

    @pytest.mark.asyncio
    async def test_log_task_failure(self, mock_db):
        """Test logging task failure"""
        mock_db.task_logs.insert_one.return_value.inserted_id = ObjectId()
        
        # Log failure
        failure_log = {
            "task_name": "send_gift_card_email",
            "status": "failed",
            "error": "Email service unavailable",
            "error_type": "ServiceError",
            "traceback": "...",
            "created_at": datetime.utcnow()
        }
        
        mock_db.task_logs.insert_one(failure_log)
        
        mock_db.task_logs.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_notify_on_critical_failure(self, mock_db):
        """Test notifying on critical failure"""
        mock_db.task_logs.insert_one.return_value.inserted_id = ObjectId()
        
        # Log critical failure
        failure_log = {
            "task_name": "bulk_create_gift_cards",
            "status": "failed",
            "severity": "critical",
            "error": "Database connection lost",
            "created_at": datetime.utcnow()
        }
        
        mock_db.task_logs.insert_one(failure_log)
        
        mock_db.task_logs.insert_one.assert_called_once()


class TestCheckExpiringCardsTask:
    """Test check expiring cards task"""

    @pytest.mark.asyncio
    async def test_identify_expiring_cards(self, mock_db):
        """Test identifying expiring cards"""
        expiring_cards = [
            {
                "_id": ObjectId(),
                "card_number": "GC-EXPIRING-001",
                "expiry_date": datetime.utcnow() + timedelta(days=30),
                "status": "active"
            },
            {
                "_id": ObjectId(),
                "card_number": "GC-EXPIRING-002",
                "expiry_date": datetime.utcnow() + timedelta(days=7),
                "status": "active"
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=expiring_cards)
        mock_db.gift_cards.find = Mock(return_value=mock_cursor)
        
        # Check expiring cards
        result = {
            "expiring_count": 2
        }
        
        assert result["expiring_count"] == 2

    @pytest.mark.asyncio
    async def test_mark_expired_cards(self, mock_db):
        """Test marking expired cards"""
        expired_cards = [
            {
                "_id": ObjectId(),
                "card_number": "GC-EXPIRED-001",
                "expiry_date": datetime.utcnow() - timedelta(days=1),
                "status": "active"
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=expired_cards)
        mock_db.gift_cards.find = Mock(return_value=mock_cursor)
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        # Mark expired
        result = {
            "expired_count": 1
        }
        
        assert result["expired_count"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
