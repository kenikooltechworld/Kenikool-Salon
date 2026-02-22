# Gift Card Background Tasks Documentation

## Overview

Phase 3 implements Celery background tasks for the gift card system, enabling asynchronous processing of email delivery, expiration management, and bulk operations.

## Tasks Implemented

### 1. Email Delivery Tasks

#### `send_gift_card_email_task(card_id, tenant_id, recipient_email, recipient_name, message)`
- **Purpose**: Send gift card delivery email with QR code
- **Retry Logic**: Up to 3 retries with exponential backoff (60s, 120s, 240s)
- **Features**:
  - Async email sending via GiftCardEmailService
  - Automatic retry on failure
  - Delivery status tracking
  - Audit logging

#### `send_scheduled_gift_card_email_task(card_id, tenant_id)`
- **Purpose**: Send gift cards at scheduled delivery time
- **Features**:
  - Checks if scheduled time has arrived
  - Validates card status
  - Automatic retry on failure
  - Logs delivery attempts

### 2. Expiration Management Tasks

#### `check_gift_card_expiration_task()`
- **Purpose**: Daily task to manage gift card expiration
- **Schedule**: Daily at midnight (00:00 UTC)
- **Features**:
  - Sends expiration reminders at 30, 7, and 1 days before expiration
  - Marks expired cards automatically
  - Prevents duplicate reminders
  - Tracks reminder delivery status
  - Audit logging for all actions

**Reminder Schedule**:
- 30 days before expiration: First reminder
- 7 days before expiration: Second reminder
- 1 day before expiration: Final reminder
- On expiration date: Card marked as expired

### 3. Bulk Operations Tasks

#### `bulk_create_gift_cards_task(tenant_id, cards_data, created_by)`
- **Purpose**: Bulk create gift cards from CSV data
- **Features**:
  - Batch processing of multiple cards
  - Individual error handling per card
  - Automatic email sending for digital cards
  - Stores bulk operation results
  - Tracks success/failure statistics

**Input Format**:
```python
cards_data = [
    {
        "amount": 50000,
        "card_type": "digital",
        "recipient_name": "John Doe",
        "recipient_email": "john@example.com",
        "message": "Happy Birthday!",
        "expiration_months": 12,
        "design_theme": "birthday",
        "activation_required": False,
        "pin": "1234"
    },
    # ... more cards
]
```

### 4. Delivery Retry Tasks

#### `process_failed_deliveries_task()`
- **Purpose**: Retry failed email deliveries
- **Schedule**: Every 4 hours
- **Features**:
  - Finds cards with failed deliveries
  - Retries up to 3 times
  - Queues retry tasks
  - Logs retry attempts

### 5. Cleanup Tasks

#### `cleanup_old_gift_cards_task()`
- **Purpose**: Archive old/expired gift cards
- **Schedule**: Weekly on Sunday at 3 AM
- **Features**:
  - Archives cards older than 1 year
  - Moves to gift_cards_archive collection
  - Deletes from active collection
  - Tracks archived count

#### `generate_gift_card_certificates_task(card_id, tenant_id)`
- **Purpose**: Generate PDF certificate for gift card
- **Features**:
  - Creates branded PDF certificate
  - Embeds QR code
  - Stores certificate URL
  - Updates gift card record
  - Audit logging

## Celery Beat Schedule

The following tasks are scheduled in `celery_app.py`:

```python
"check-gift-card-expiration": {
    "task": "app.tasks.gift_card_tasks.check_gift_card_expiration_task",
    "schedule": crontab(minute="0", hour="0"),  # Daily at midnight
},
"process-failed-gift-card-deliveries": {
    "task": "app.tasks.gift_card_tasks.process_failed_deliveries_task",
    "schedule": crontab(minute="0", hour="*/4"),  # Every 4 hours
},
"cleanup-old-gift-cards": {
    "task": "app.tasks.gift_card_tasks.cleanup_old_gift_cards_task",
    "schedule": crontab(minute="0", hour="3", day_of_week="0"),  # Weekly Sunday 3 AM
},
```

## Usage Examples

### Sending a Gift Card Email

```python
from app.tasks.gift_card_tasks import send_gift_card_email_task

# Queue email sending task
send_gift_card_email_task.delay(
    card_id="507f1f77bcf86cd799439011",
    tenant_id="507f1f77bcf86cd799439012",
    recipient_email="customer@example.com",
    recipient_name="John Doe",
    message="Enjoy your gift!"
)
```

### Bulk Creating Gift Cards

```python
from app.tasks.gift_card_tasks import bulk_create_gift_cards_task

cards_data = [
    {
        "amount": 50000,
        "card_type": "digital",
        "recipient_email": "user1@example.com",
        "recipient_name": "User 1"
    },
    {
        "amount": 100000,
        "card_type": "physical",
        "recipient_name": "User 2"
    }
]

# Queue bulk creation task
bulk_create_gift_cards_task.delay(
    tenant_id="507f1f77bcf86cd799439012",
    cards_data=cards_data,
    created_by="507f1f77bcf86cd799439013"
)
```

### Scheduling Delayed Email

```python
from app.tasks.gift_card_tasks import send_scheduled_gift_card_email_task
from datetime import datetime, timedelta

# Schedule email for 2 hours from now
send_scheduled_gift_card_email_task.apply_async(
    args=["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"],
    countdown=7200  # 2 hours in seconds
)
```

## Error Handling

### Retry Logic

All email tasks implement exponential backoff retry:
- **Attempt 1**: Immediate
- **Attempt 2**: After 60 seconds
- **Attempt 3**: After 120 seconds
- **Attempt 4**: After 240 seconds

### Failed Delivery Processing

Failed deliveries are automatically retried every 4 hours:
1. Task finds cards with `delivery_status = "failed"`
2. Checks `delivery_attempts < 3`
3. Queues retry task
4. Updates attempt counter

### Error Logging

All errors are logged with:
- Task name
- Card ID
- Error message
- Stack trace
- Timestamp

## Database Collections

### gift_cards
Main collection for active gift cards with delivery tracking fields:
- `delivery_status`: pending, scheduled, delivered, failed, bounced
- `delivery_attempts`: Number of delivery attempts
- `last_delivery_attempt`: Timestamp of last attempt
- `scheduled_delivery`: Scheduled delivery time
- `reminder_30d`, `reminder_7d`, `reminder_1d`: Reminder sent flags

### gift_cards_archive
Archive collection for old/expired cards (older than 1 year)

### gift_card_bulk_operations
Stores bulk operation results:
- `total_requested`: Total cards requested
- `total_created`: Successfully created
- `total_failed`: Failed creations
- `created_cards`: List of created card details
- `failed_cards`: List of failures with reasons

## Monitoring

### Task Status

Monitor task execution:
```bash
# View active tasks
celery -A app.celery_app inspect active

# View scheduled tasks
celery -A app.celery_app inspect scheduled

# View task stats
celery -A app.celery_app inspect stats
```

### Logs

Check task logs:
```bash
# View Celery worker logs
tail -f celery_worker.log

# Filter gift card tasks
grep "gift_card" celery_worker.log
```

## Performance Considerations

### Task Concurrency
- Default worker prefetch: 4 tasks
- Max tasks per child: 1000
- Time limits: 30 minutes hard, 25 minutes soft

### Bulk Operations
- Processes cards sequentially
- Individual error handling prevents batch failure
- Stores results for audit trail

### Email Delivery
- Async processing prevents blocking
- Retry logic ensures delivery
- Rate limiting via Resend API

## Integration with Phase 2

Phase 3 tasks work with Phase 2 components:

1. **GiftCardEmailService**: Sends emails with templates
2. **POSService**: Creates gift cards
3. **Database**: Stores and tracks operations
4. **Audit Logging**: Records all actions

## Next Steps (Phase 4)

Phase 4 will add:
- Public API endpoints for customer portal
- Frontend components for gift card management
- Analytics dashboard
- Advanced features (transfer, fraud detection)

