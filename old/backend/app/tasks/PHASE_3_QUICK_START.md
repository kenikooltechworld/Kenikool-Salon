# Phase 3: Background Jobs - Quick Start Guide

## What's Implemented

Phase 3 adds Celery background tasks for gift card operations:

✅ **Email Delivery Tasks**
- `send_gift_card_email_task()` - Send emails with retry logic
- `send_scheduled_gift_card_email_task()` - Send at scheduled time

✅ **Expiration Management**
- `check_gift_card_expiration_task()` - Daily expiration checks and reminders
- Sends reminders at 30, 7, and 1 days before expiration
- Automatically marks expired cards

✅ **Bulk Operations**
- `bulk_create_gift_cards_task()` - Create multiple cards from CSV
- Individual error handling
- Automatic email sending for digital cards

✅ **Delivery Retry**
- `process_failed_deliveries_task()` - Retry failed emails every 4 hours
- Up to 3 retry attempts per card

✅ **Cleanup**
- `cleanup_old_gift_cards_task()` - Archive cards older than 1 year
- `generate_gift_card_certificates_task()` - Generate PDF certificates

## Starting Celery

### Development

```bash
# Terminal 1: Start Celery worker
cd backend
celery -A app.celery_app worker --loglevel=info

# Terminal 2: Start Celery Beat (scheduler)
celery -A app.celery_app beat --loglevel=info
```

### Production

```bash
# Start worker with multiple processes
celery -A app.celery_app worker --loglevel=info --concurrency=4

# Start beat scheduler
celery -A app.celery_app beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Task Scheduling

### Automatic Schedules (via Celery Beat)

- **Midnight (00:00)**: Check gift card expiration
- **Every 4 hours**: Retry failed deliveries
- **Sunday 3 AM**: Archive old gift cards

### Manual Task Queuing

```python
from app.tasks.gift_card_tasks import send_gift_card_email_task

# Send immediately
send_gift_card_email_task.delay(
    card_id="...",
    tenant_id="...",
    recipient_email="user@example.com"
)

# Send after 2 hours
send_gift_card_email_task.apply_async(
    args=["...", "...", "user@example.com"],
    countdown=7200
)
```

## Database Collections

### gift_cards
- `delivery_status`: pending, scheduled, delivered, failed, bounced
- `delivery_attempts`: Number of attempts
- `last_delivery_attempt`: Timestamp
- `reminder_30d`, `reminder_7d`, `reminder_1d`: Reminder flags

### gift_cards_archive
- Stores archived cards (older than 1 year)

### gift_card_bulk_operations
- Stores bulk operation results and statistics

## Monitoring

### Check Task Status

```bash
# Active tasks
celery -A app.celery_app inspect active

# Scheduled tasks
celery -A app.celery_app inspect scheduled

# Task stats
celery -A app.celery_app inspect stats
```

### View Logs

```bash
# Celery worker logs
tail -f celery_worker.log

# Filter gift card tasks
grep "gift_card" celery_worker.log
```

## Error Handling

### Retry Logic
- Automatic retry on failure
- Exponential backoff: 60s, 120s, 240s
- Max 3 retries per task

### Failed Deliveries
- Automatically retried every 4 hours
- Tracked in database
- Logged for debugging

## Integration Points

### Phase 2 Components Used
- `GiftCardEmailService`: Email sending
- `POSService`: Gift card creation
- `Database`: Data storage
- `Audit Logging`: Action tracking

### Phase 4 Dependencies
- Public API endpoints will use these tasks
- Frontend will trigger bulk operations
- Analytics will use task results

## Common Tasks

### Send Gift Card Email

```python
from app.tasks.gift_card_tasks import send_gift_card_email_task

send_gift_card_email_task.delay(
    card_id="507f1f77bcf86cd799439011",
    tenant_id="507f1f77bcf86cd799439012",
    recipient_email="customer@example.com",
    recipient_name="John Doe",
    message="Happy Birthday!"
)
```

### Bulk Create Cards

```python
from app.tasks.gift_card_tasks import bulk_create_gift_cards_task

cards = [
    {
        "amount": 50000,
        "card_type": "digital",
        "recipient_email": "user1@example.com",
        "recipient_name": "User 1"
    }
]

bulk_create_gift_cards_task.delay(
    tenant_id="507f1f77bcf86cd799439012",
    cards_data=cards,
    created_by="507f1f77bcf86cd799439013"
)
```

### Generate Certificate

```python
from app.tasks.gift_card_tasks import generate_gift_card_certificates_task

generate_gift_card_certificates_task.delay(
    card_id="507f1f77bcf86cd799439011",
    tenant_id="507f1f77bcf86cd799439012"
)
```

## Testing

### Test Email Task

```python
# In Django shell or test
from app.tasks.gift_card_tasks import send_gift_card_email_task

result = send_gift_card_email_task.delay(
    card_id="test_id",
    tenant_id="test_tenant",
    recipient_email="test@example.com"
)

# Check result
print(result.get())  # Blocks until complete
```

### Test Bulk Creation

```python
from app.tasks.gift_card_tasks import bulk_create_gift_cards_task

result = bulk_create_gift_cards_task.delay(
    tenant_id="test_tenant",
    cards_data=[{"amount": 50000}],
    created_by="test_user"
)

print(result.get())
```

## Troubleshooting

### Tasks Not Running

1. Check Celery worker is running: `celery -A app.celery_app inspect active`
2. Check Celery Beat is running: `celery -A app.celery_app inspect scheduled`
3. Check Redis connection: `redis-cli ping`
4. Check logs for errors

### Email Not Sending

1. Check `delivery_status` in database
2. Check `delivery_attempts` count
3. Check `last_delivery_attempt` timestamp
4. Review Celery logs for errors
5. Verify Resend API credentials

### High Task Queue

1. Increase worker concurrency: `--concurrency=8`
2. Add more workers
3. Check for stuck tasks: `celery -A app.celery_app inspect active`
4. Purge queue if needed: `celery -A app.celery_app purge`

## Performance Tips

1. **Batch Operations**: Use bulk_create for multiple cards
2. **Scheduled Delivery**: Use `apply_async` with countdown for delayed tasks
3. **Monitoring**: Check task stats regularly
4. **Logging**: Enable debug logging for troubleshooting
5. **Scaling**: Add more workers for high volume

## Next Phase

Phase 4 will add:
- Public API endpoints
- Customer portal frontend
- Analytics dashboard
- Advanced features

