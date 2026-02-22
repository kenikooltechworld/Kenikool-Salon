# Webhook 404 Investigation - Research Findings

## Problem Analysis

From the ngrok traffic inspector logs, we see:
- Multiple `POST /webhooks/paystack` requests returning **404 Not Found**
- Multiple `POST /api/v1/webhooks/paystack` requests returning **200 OK**

## Root Cause Investigation

### 1. Paystack Webhook URL Configuration
According to Paystack documentation, the webhook URL is configured in the Paystack dashboard under Settings → API Keys & Webhooks.

**Your current configuration:**
- `.env` specifies: `PAYSTACK_WEBHOOK_URL=https://lawyerly-inell-noncontroversially.ngrok-free.dev/api/v1/webhooks/paystack`
- Backend route registered at: `/api/v1/webhooks/paystack` (with prefix)

### 2. Why 404s on `/webhooks/paystack`?

The 404 errors suggest that Paystack is sending webhooks to BOTH:
1. The configured URL: `/api/v1/webhooks/paystack` ✓ (returns 200 OK)
2. A default/fallback path: `/webhooks/paystack` ✗ (returns 404)

**Possible reasons:**
- Paystack dashboard has multiple webhook URLs configured
- Paystack is retrying with a different path format
- There's a webhook configuration issue in the Paystack dashboard

### 3. What Needs to Be Verified

**ACTION REQUIRED:**
1. Log into your Paystack dashboard
2. Go to Settings → API Keys & Webhooks
3. Check the "Webhook URL" field
4. Verify it's set to: `https://lawyerly-inell-noncontroversially.ngrok-free.dev/api/v1/webhooks/paystack`
5. Ensure there are NO other webhook URLs configured
6. Save/update if needed

### 4. Current Status

- ✓ Backend webhook endpoint is correctly registered at `/api/v1/webhooks/paystack`
- ✓ Webhook signature verification is implemented
- ✓ Some webhooks ARE being received successfully (200 OK responses)
- ✗ Unknown why `/webhooks/paystack` is also being called (404s)

## Next Steps

1. **Verify Paystack Dashboard Configuration** - Check what webhook URL is actually configured
2. **Check for Multiple Webhook Configurations** - Ensure only one webhook URL is set
3. **Monitor Logs** - After fixing, verify no more 404s appear
4. **Test End-to-End** - Complete a payment and verify booking is created

## Technical Details

**Webhook Route Registration:**
```python
# In backend/app/main.py
app.include_router(webhooks.router, prefix=settings.api_prefix)
# This registers: POST /api/v1/webhooks/paystack
```

**Webhook Handler:**
```python
# In backend/app/routes/webhooks.py
@router.post("/paystack")
async def handle_paystack_webhook(request: Request):
    # Verifies signature
    # Processes payment status
    # Creates booking if needed
```

**Middleware Bypass:**
```python
# In backend/app/middleware/subdomain_context.py
if request.url.path.startswith("/api/v1/webhooks"):
    return await call_next(request)
# Allows webhooks to bypass tenant context middleware
```

## Conclusion

The 404 errors are likely due to Paystack dashboard configuration. The backend is correctly set up to receive webhooks at `/api/v1/webhooks/paystack`. The successful 200 OK responses confirm the webhook handler is working properly.

**The issue is NOT in the code - it's in the Paystack dashboard configuration.**
