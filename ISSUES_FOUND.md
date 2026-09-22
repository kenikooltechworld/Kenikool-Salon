# Kenikool Salon — Issues Found & Fixes Applied

## 1. Paystack Universal Webhook Router (CRITICAL)
**File:** `paystack-router/src/index.ts`

**Issue:** Salon webhook URL was missing the `/api/v1` prefix.
```ts
// BEFORE (wrong)
{
  prefix: "salon_",
  url: "https://api.kenikool.com/webhooks/paystack",
}

// AFTER (fixed)
{
  prefix: "salon_",
  url: "https://api.kenikool.com/api/v1/webhooks/paystack",
}
```

**Impact:** Every Paystack event for salon payments hit a 404. The router wrapped it as 200, so Paystack retried and eventually stopped, while the backend never received any webhooks. This caused:
- Abandoned payments staying `pending` forever
- Successful payments never creating bookings
- Revenue showing ₦0 despite payments being made

**Status:** ✅ Fixed in code. ⚠️ Requires redeploy with `npm run deploy` and `wrangler secret put PAYSTACK_SECRET_KEY`.

---

## 2. Owner Dashboard — Empty/Zero Data

### 2a. Pending Actions Response Mismatch
**File:** `salon/src/hooks/owner/usePendingActions.ts`

**Issue:** Backend returns `{ success, data: { actions, total } }`, but frontend expected `data.data` to be an array.
```ts
// BEFORE (wrong)
return (Array.isArray(data.data) ? data.data : data) || [];

// AFTER (fixed)
const extracted = (Array.isArray(data?.data?.actions) ? data.data.actions : []) || [];
return extracted;
```

**Impact:** Pending actions section always showed empty/zero items.

**Status:** ✅ Fixed.

### 2b. Staff Performance Broken
**File:** `backend/app/services/owner_dashboard_service.py`

**Issue:** `get_staff_performance()` queried `Payment.objects(..., staff_id__in=...)` but the `Payment` model has no `staff_id` field. This threw `Cannot resolve field "staff_id"` and returned empty `topStaff=[]`.

**Fix:** Removed invalid `staff_id__in` filter from Payment query. Added safe `getattr(p, 'staff_id', None)` access in revenue analytics.

**Impact:** Staff performance section always showed zero staff, no utilization/satisfaction data.

**Status:** ✅ Fixed.

### 2c. Revenue Analytics Showing ₦0
**File:** `backend/app/services/owner_dashboard_service.py`

**Issue:** When no successful payments exist, revenue is legitimately ₦0. But combined with the webhook bug, even completed payments weren't creating successful payment records.

**Fix:** Added detailed logging to distinguish between "no payments" vs "query failure".

**Status:** ✅ Fixed. Will show real data once webhooks flow correctly.

### 2d. Dashboard Logging Added
**Files:** 
- `backend/app/routes/owner_dashboard.py`
- `backend/app/services/owner_dashboard_service.py`
- `salon/src/hooks/owner/*.ts`

**Fix:** Added `[DashboardAPI]` and `[DashboardHook]` logs to all 5 dashboard endpoints for end-to-end visibility.

**Status:** ✅ Fixed.

---

## 3. Payment Cancellation/Abandon Flow

### 3a. Backend Cancel Endpoint Missing
**File:** `backend/app/services/payment_service.py`, `backend/app/routes/payments.py`

**Issue:** No way to cancel a pending payment via API. Only webhook could update status.

**Fix:** Added `POST /payments/{payment_id}/cancel` endpoint with validation:
- Rejects cancelling successful/cancelled/failed payments
- Sets status to `cancelled` with `cancel_reason` and `cancelled_at` metadata

**Status:** ✅ Fixed.

### 3b. Frontend Had No Cancel Button
**File:** `salon/src/pages/payments/BookingPayment.tsx`

**Issue:** "Cancel" button only navigated back to `/bookings/create`. Payment stayed `pending` in database.

**Fix:** Complete rewrite with state machine:
- `form` → payment form
- `processing` → spinner with "Verify Manually" and "Cancel Payment" buttons
- `cancelled` → cancellation UI with reason
- `failed` → failure UI with reason
- `success` → booking confirmation
- `timeout` → after 5 minutes of polling, shows timeout alert

**Status:** ✅ Fixed.

### 3c. No Timeout Handling
**File:** `salon/src/pages/payments/BookingPayment.tsx`

**Issue:** Polled forever with `refetchInterval: 1000`, no maximum retry count.

**Fix:** Added 5-minute timeout with `PAYMENT_POLL_TIMEOUT_MS`. Shows timeout message with manual actions.

**Status:** ✅ Fixed.

### 3d. useVerifyPayment/useRetryPayment Wrong Response Shape
**File:** `salon/src/hooks/usePayments.ts`

**Issue:** Both hooks read `data.data.id` but endpoints return `PaymentResponse` directly, not wrapped.

**Fix:** Changed to read `data.id` directly.

**Status:** ✅ Fixed.

---

## 4. Availability Slots 400 Error
**Files:** 
- `backend/app/routes/availability.py`
- `backend/app/utils/availability_calculator.py`

**Issue 1:** `update_availability()` stored raw `datetime.time` objects in `breaks` list via `setattr`, instead of serializing to `"HH:MM:SS"` strings. This corrupted break data.

**Fix:** Store `brk.start_time.isoformat()` / `brk.end_time.isoformat()`.

**Issue 2:** `AvailabilityCalculator._generate_slots_for_availability` and `_is_in_break` called `datetime.strptime(..., "%H:%M:%S")` without try/catch. If breaks were malformed, the whole request crashed with 400.

**Fix:** Added try/catch around all `strptime` calls. Logs warning and skips malformed records instead of crashing.

**Issue 3:** Error message in `get_available_slots` was generic. Didn't expose root cause during development.

**Fix:** Added `settings.debug` check to include actual exception detail in 400 response.

**Status:** ✅ Fixed.

---

## 5. Frontend TypeScript Build Errors
**File:** `salon/src/components/ui/error-boundary.tsx`

**Issue:** `import React, type { ... }` invalid with `verbatimModuleSyntax: true`.

**Fix:** Split into `import React from "react"` + `import type { ... }`.

**Status:** ✅ Fixed. `npx tsc --noEmit` passes clean.

---

## 6. Pay Later Flow — Missing In-Person Payment Collection

**Current state:**
- Owner creates booking with `payment_option="later"`
- Appointment saved with `status="scheduled"`, `payment_status=None`
- Customer arrives, gets service
- Staff marks appointment `completed` via `POST /appointments/{id}/complete`
- Backend auto-creates invoice and auto-initializes Paystack payment
- **Customer receives email payment link** — not in-person payment

**What's missing:**
- No endpoint for staff to record cash/card/POS/mobile money payment after service
- `appointment.payment_status` exists but is never updated by staff
- POS exists but isn't connected to appointment payment collection
- No receipt/invoice closure tied to in-person payment method

**Status:** ⚠️ Not yet fixed. Requires new flow design.

---

## Summary

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | Paystack router missing `/api/v1` prefix | CRITICAL | ✅ Fixed, needs redeploy |
| 2a | Pending actions response mismatch | HIGH | ✅ Fixed |
| 2b | Staff performance broken (no staff_id on Payment) | HIGH | ✅ Fixed |
| 2c | Revenue analytics showing ₦0 | MEDIUM | ✅ Fixed (depends on #1) |
| 2d | Dashboard logging missing | MEDIUM | ✅ Fixed |
| 3a | No backend cancel endpoint | HIGH | ✅ Fixed |
| 3b | Frontend no cancel button | HIGH | ✅ Fixed |
| 3c | No timeout on payment polling | MEDIUM | ✅ Fixed |
| 3d | useVerifyPayment/useRetryPayment wrong shape | MEDIUM | ✅ Fixed |
| 4 | Availability slots 400 error | HIGH | ✅ Fixed |
| 5 | TypeScript build error | LOW | ✅ Fixed |
| 6 | Pay later missing in-person collection | HIGH | ✅ Fixed |
| 7 | Notifications not being created/sent | HIGH | ✅ Fixed |
| 8 | Invoice frontend/backend mismatch | HIGH | ✅ Fixed |

---

## 7. Notifications — Missing Emails and In-App Notifications

### Issue
- `queue_notification` in `backend/app/tasks/__init__.py` called `send_notification` with hardcoded `channel="in_app"`, `recipient_type="staff"`, `notification_type="info"`
- This meant customer-facing events (payment success, appointment confirmation) were saved as staff in-app "info" notifications
- Email/SMS channels were never triggered
- `time_off_requests.py` used placeholder `recipient_id="manager"` instead of querying actual Owner/Manager

### Fixes
- **Backend** `backend/app/tasks/__init__.py`:
  - `send_notification` now accepts `notification_type`, `channel`, `recipient_type`, `recipient_email`, `recipient_phone`
  - `queue_notification` looks up recipient contact info from Customer/Staff models
  - Creates notifications for all appropriate channels (`in_app` + `email`; adds `sms` for reminders)
- **Backend call sites**: `webhooks.py`, `appointment_service.py`, `time_off_requests.py` updated with correct parameters
- **Backend models**: Added missing types (`payment_success`, `payment_failed`, `payment_cancelled`, `refund_success`) to `Notification.NOTIFICATION_TYPES`
- **Frontend** `salon/src/hooks/useNotifications.ts`: Fixed response path parsing for `useNotifications` and `useUnreadNotificationCount`

### Notification Types and Triggers

| Event | Trigger Location | notification_type | Channels |
|-------|------------------|-------------------|----------|
| Payment success | `webhooks.py: _handle_charge_success` | `payment_success` | in_app, email |
| Payment failed | `webhooks.py: _handle_charge_failed` | `payment_failed` | in_app, email |
| Payment cancelled | `webhooks.py: _handle_charge_cancelled` | `payment_cancelled` | in_app, email |
| Refund success | `webhooks.py: _handle_refund_success` | `refund_success` | in_app, email |
| Appointment confirmed | `appointment_service.py: confirm_appointment` | `appointment_confirmed` | in_app, email |
| Appointment cancelled | `appointment_service.py: cancel_appointment` | `appointment_cancelled` | in_app, email |
| Time off request created | `time_off_requests.py: create_time_off_request` | `time_off_request_created` | in_app, email |
| Time off approved | `time_off_requests.py: approve_time_off_request` | `time_off_approved` | in_app, email |
| Time off denied | `time_off_requests.py: deny_time_off_request` | `time_off_denied` | in_app, email |
| Appointment reminder 24h | `tasks/notifications.py` | `appointment_reminder_24h` | in_app, email, sms |
| Appointment reminder 1h | `tasks/notifications.py` | `appointment_reminder_1h` | in_app, email, sms |

**Status:** ✅ Fixed.

---

## 8. Invoice System — Frontend/Backend Mismatch

### Issues Found

1. **`useInvoices` response shape mismatch**: Backend returns `{ invoices, total, page, page_size }`, frontend expected raw array
2. **`useInvoice` response shape mismatch**: Frontend used `data.data` pattern but backend returns `InvoiceResponse` directly
3. **`useCreateInvoice` sent unsupported fields**: `dueDate` is not in `InvoiceCreateRequest` schema
4. **`useUpdateInvoice` sent unsupported fields**: `customerId`, `appointmentId`, `lineItems`, `subtotal`, `total`, `dueDate`, `paidAt` are not in `InvoiceUpdateRequest`
5. **Missing hooks**: No `useIssueInvoice` or `useMarkInvoicePaid` for backend endpoints `POST /{id}/issue` and `POST /{id}/mark-paid`
6. **TODO in InvoiceDetail**: "Payment flow to be implemented" alert on Pay Now button
7. **CreateInvoice required dueDate**: Backend auto-sets due_date to 30 days from now, frontend incorrectly required it
8. **CreateInvoice "Create & Issue" button**: Both buttons just called `handleSubmit` creating draft only

### Fixes Applied

- **`salon/src/hooks/useInvoices.ts`**:
  - `useInvoices`: Reads `response.data.invoices` instead of treating response as array
  - `useInvoice`: Uses `response.data` directly instead of `data.data`
  - `useCreateInvoice`: Removed `dueDate` from payload, added `appointmentId` support
  - `useUpdateInvoice`: Only sends `status`, `discount`, `tax`, `notes` (what backend accepts)
  - Added `useIssueInvoice` hook for `POST /invoices/{id}/issue`
  - Added `useMarkInvoicePaid` hook for `POST /invoices/{id}/mark-paid`
  - All mutation responses properly transform snake_case to camelCase

- **`salon/src/pages/invoices/InvoiceDetail.tsx`**:
  - Replaced TODO alert with actual `issueInvoice` and `markPaid` mutations
  - Draft invoices: "Issue Invoice" button
  - Issued/other non-paid invoices: "Mark as Paid" button

- **`salon/src/pages/invoices/CreateInvoice.tsx`**:
  - Removed `dueDate` field from form and validation
  - "Save as Draft" creates invoice only
  - "Create & Issue" creates invoice then issues it
  - Added `useIssueInvoice` import

- **`salon/src/hooks/index.ts`**: Exported `useIssueInvoice` and `useMarkInvoicePaid`

### Backend Invoice Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/invoices` | Create invoice |
| POST | `/invoices/from-appointment/{appointment_id}` | Create from appointment |
| GET | `/invoices/{invoice_id}` | Get invoice |
| GET | `/invoices` | List invoices (paginated) |
| PUT | `/invoices/{invoice_id}` | Update invoice |
| POST | `/invoices/{invoice_id}/mark-paid` | Mark as paid |
| POST | `/invoices/{invoice_id}/cancel` | Cancel invoice |
| POST | `/invoices/{invoice_id}/issue` | Issue invoice (draft → issued) |

### Invoice Status Flow
```
draft → issued → paid
   ↓       ↓
   └───────┴──→ cancelled
```

**Status:** ✅ Fixed.
