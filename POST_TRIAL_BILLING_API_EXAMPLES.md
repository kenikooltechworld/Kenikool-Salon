# Post-Trial Billing Model - API Usage Examples

## 1. Get Current Subscription

### Request
```bash
curl -X GET http://localhost:8000/api/v1/billing/subscription \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Response (Trial Active)
```json
{
  "id": "507f1f77bcf86cd799439011",
  "tenant_id": "507f1f77bcf86cd799439012",
  "plan_name": "Free",
  "plan_tier": 0,
  "billing_cycle": "monthly",
  "status": "trial",
  "subscription_status": "trial",
  "current_period_start": "2024-02-22T00:00:00",
  "current_period_end": "2024-03-23T00:00:00",
  "next_billing_date": "2024-03-23T00:00:00",
  "is_trial": true,
  "trial_end": "2024-03-23T00:00:00",
  "days_until_expiry": 29,
  "last_payment_date": null,
  "last_payment_amount": null,
  "auto_renew": true,
  "trial_expiry_action_required": false,
  "transaction_fee_percentage": 0.0
}
```

### Response (Trial Expired - Action Required)
```json
{
  "id": "507f1f77bcf86cd799439011",
  "tenant_id": "507f1f77bcf86cd799439012",
  "plan_name": "Free",
  "plan_tier": 0,
  "billing_cycle": "monthly",
  "status": "expired",
  "subscription_status": "expired_trial",
  "current_period_start": "2024-02-22T00:00:00",
  "current_period_end": "2024-03-23T00:00:00",
  "next_billing_date": "2024-03-23T00:00:00",
  "is_trial": false,
  "trial_end": "2024-03-23T00:00:00",
  "days_until_expiry": 0,
  "last_payment_date": null,
  "last_payment_amount": null,
  "auto_renew": true,
  "trial_expiry_action_required": true,
  "transaction_fee_percentage": 0.0
}
```

### Response (Free with Fee)
```json
{
  "id": "507f1f77bcf86cd799439011",
  "tenant_id": "507f1f77bcf86cd799439012",
  "plan_name": "Free",
  "plan_tier": 0,
  "billing_cycle": "monthly",
  "status": "active",
  "subscription_status": "free_with_fee",
  "current_period_start": "2024-03-23T00:00:00",
  "current_period_end": "2024-04-22T00:00:00",
  "next_billing_date": "2024-04-22T00:00:00",
  "is_trial": false,
  "trial_end": null,
  "days_until_expiry": 30,
  "last_payment_date": null,
  "last_payment_amount": null,
  "auto_renew": true,
  "trial_expiry_action_required": false,
  "transaction_fee_percentage": 10.0
}
```

### Response (Paid Plan - Active)
```json
{
  "id": "507f1f77bcf86cd799439011",
  "tenant_id": "507f1f77bcf86cd799439012",
  "plan_name": "Professional",
  "plan_tier": 2,
  "billing_cycle": "monthly",
  "status": "active",
  "subscription_status": "active",
  "current_period_start": "2024-03-23T00:00:00",
  "current_period_end": "2024-04-23T00:00:00",
  "next_billing_date": "2024-04-23T00:00:00",
  "is_trial": false,
  "trial_end": null,
  "days_until_expiry": 31,
  "last_payment_date": "2024-03-23T10:30:00",
  "last_payment_amount": 50000.0,
  "auto_renew": true,
  "trial_expiry_action_required": false,
  "transaction_fee_percentage": 0.0
}
```

## 2. Continue Free with 10% Fee

### Request
```bash
curl -X POST http://localhost:8000/api/v1/billing/continue-free \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### Response
```json
{
  "id": "507f1f77bcf86cd799439011",
  "tenant_id": "507f1f77bcf86cd799439012",
  "plan_name": "Free",
  "plan_tier": 0,
  "billing_cycle": "monthly",
  "status": "active",
  "subscription_status": "free_with_fee",
  "current_period_start": "2024-03-23T12:00:00",
  "current_period_end": "2024-04-22T12:00:00",
  "next_billing_date": "2024-04-22T12:00:00",
  "is_trial": false,
  "trial_end": null,
  "days_until_expiry": 30,
  "last_payment_date": null,
  "last_payment_amount": null,
  "auto_renew": true,
  "trial_expiry_action_required": false,
  "transaction_fee_percentage": 10.0
}
```

## 3. Upgrade from Expired Trial

### Request
```bash
curl -X POST http://localhost:8000/api/v1/billing/upgrade-from-trial \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "507f1f77bcf86cd799439013",
    "billing_cycle": "monthly"
  }'
```

### Response
```json
{
  "id": "507f1f77bcf86cd799439011",
  "tenant_id": "507f1f77bcf86cd799439012",
  "plan_name": "Professional",
  "plan_tier": 2,
  "billing_cycle": "monthly",
  "status": "active",
  "subscription_status": "active",
  "current_period_start": "2024-03-23T12:00:00",
  "current_period_end": "2024-04-23T12:00:00",
  "next_billing_date": "2024-04-23T12:00:00",
  "is_trial": false,
  "trial_end": null,
  "days_until_expiry": 31,
  "last_payment_date": "2024-03-23T12:00:00",
  "last_payment_amount": 0.0,
  "auto_renew": true,
  "trial_expiry_action_required": false,
  "transaction_fee_percentage": 0.0
}
```

## 4. Transaction with Fee Applied

### Create Transaction (Free with Fee)
```bash
curl -X POST http://localhost:8000/api/v1/pos/transactions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "507f1f77bcf86cd799439014",
    "staff_id": "507f1f77bcf86cd799439015",
    "items": [
      {
        "item_type": "service",
        "item_id": "507f1f77bcf86cd799439016",
        "item_name": "Haircut",
        "quantity": 1,
        "unit_price": 100.0,
        "tax_rate": 0,
        "discount_rate": 0
      }
    ],
    "payment_method": "cash"
  }'
```

### Response (Transaction with 10% Fee)
```json
{
  "id": "507f1f77bcf86cd799439017",
  "tenant_id": "507f1f77bcf86cd799439012",
  "customer_id": "507f1f77bcf86cd799439014",
  "staff_id": "507f1f77bcf86cd799439015",
  "transaction_type": "service",
  "items": [
    {
      "item_type": "service",
      "item_id": "507f1f77bcf86cd799439016",
      "item_name": "Haircut",
      "quantity": 1,
      "unit_price": 100.0,
      "line_total": 100.0,
      "tax_rate": 0,
      "tax_amount": 0,
      "discount_rate": 0,
      "discount_amount": 0
    }
  ],
  "subtotal": 100.0,
  "tax_amount": 0,
  "discount_amount": 0,
  "transaction_fee": 10.0,
  "total": 110.0,
  "payment_method": "cash",
  "payment_status": "pending",
  "reference_number": "TXN-20240323120000-000001",
  "created_at": "2024-03-23T12:00:00",
  "updated_at": "2024-03-23T12:00:00"
}
```

### Response (Transaction without Fee - Paid Plan)
```json
{
  "id": "507f1f77bcf86cd799439018",
  "tenant_id": "507f1f77bcf86cd799439012",
  "customer_id": "507f1f77bcf86cd799439014",
  "staff_id": "507f1f77bcf86cd799439015",
  "transaction_type": "service",
  "items": [
    {
      "item_type": "service",
      "item_id": "507f1f77bcf86cd799439016",
      "item_name": "Haircut",
      "quantity": 1,
      "unit_price": 100.0,
      "line_total": 100.0,
      "tax_rate": 0,
      "tax_amount": 0,
      "discount_rate": 0,
      "discount_amount": 0
    }
  ],
  "subtotal": 100.0,
  "tax_amount": 0,
  "discount_amount": 0,
  "transaction_fee": 0,
  "total": 100.0,
  "payment_method": "cash",
  "payment_status": "pending",
  "reference_number": "TXN-20240323120100-000002",
  "created_at": "2024-03-23T12:01:00",
  "updated_at": "2024-03-23T12:01:00"
}
```

## 5. Frontend Integration Example

### React Hook Usage
```typescript
import { useSubscription } from '@/hooks/useSubscription';

function BillingPage() {
  const { data: subscription } = useSubscription();

  if (subscription?.trial_expiry_action_required) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800 font-semibold mb-3">
          ⚠️ Your trial has expired. Choose an option below:
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => handleContinueFree()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg"
          >
            Continue Free (10% fee)
          </button>
          <button
            onClick={() => handleUpgrade()}
            className="px-4 py-2 bg-green-600 text-white rounded-lg"
          >
            Upgrade to Paid Plan
          </button>
        </div>
      </div>
    );
  }

  if (subscription?.subscription_status === 'free_with_fee') {
    return (
      <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
        <p className="text-orange-800">
          You're on the Free tier with a 10% transaction fee.
          <button onClick={() => handleUpgrade()} className="ml-2 underline">
            Upgrade to remove fees
          </button>
        </p>
      </div>
    );
  }

  return <div>Your subscription is active with no fees</div>;
}
```

## 6. Scheduled Task Execution

### Celery Beat Schedule
Tasks run automatically on this schedule:

```
check-trial-expiry: Daily at midnight UTC
send-trial-expiry-reminders: Daily at midnight UTC
check-subscription-expiry: Daily at midnight UTC
send-renewal-reminders: Daily at midnight UTC
```

### Manual Task Execution (for testing)
```bash
# Check trial expiry
celery -A app.tasks call app.tasks.subscriptions.check_trial_expiry

# Send trial expiry reminders
celery -A app.tasks call app.tasks.subscriptions.send_trial_expiry_reminders

# Check subscription expiry
celery -A app.tasks call app.tasks.subscriptions.check_subscription_expiry

# Send renewal reminders
celery -A app.tasks call app.tasks.subscriptions.send_renewal_reminders
```

## 7. Error Responses

### Invalid Plan ID
```json
{
  "detail": "Pricing plan not found"
}
```

### Subscription Not Found
```json
{
  "detail": "Subscription not found"
}
```

### Cannot Upgrade to Free Plan
```json
{
  "detail": "Cannot upgrade to free plan"
}
```

## Summary

The post-trial billing model provides:
1. **Automatic trial expiry detection** - Scheduled tasks check daily
2. **User choice** - Continue free with 10% fee or upgrade
3. **Automatic fee calculation** - 10% applied to all transactions for free tier
4. **Clean API** - Simple endpoints for all operations
5. **Frontend integration** - Ready-to-use React components

All endpoints are production-ready and fully tested.
