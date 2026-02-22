# Refund Handling Implementation - Complete

## Overview
Implemented automatic refund processing when appointments are cancelled or marked as no-show. The system now:
1. Links appointments to payments via `payment_id` field
2. Automatically triggers refunds when cancellations occur
3. Handles refunds gracefully without blocking appointment status changes

## Changes Made

### 1. Backend Model Changes

#### `backend/app/models/appointment.py`
- Added `payment_id` field to link appointments to payments
- This allows tracking which payment corresponds to each appointment

```python
payment_id = ObjectIdField(null=True)
```

### 2. Backend Service Changes

#### `backend/app/services/appointment_service.py`

**Imports:**
- Added `from app.models.payment import Payment` to support refund lookups

**`create_appointment` method:**
- Added `payment_id: Optional[ObjectId] = None` parameter
- Stores payment_id when creating appointments from booking payments
- Enables linking appointments to their corresponding payments

**`cancel_appointment` method:**
- Added refund processing logic:
  - Checks if appointment has associated payment
  - Retrieves payment from database
  - If payment status is "success", creates refund via RefundService
  - Refund reason includes cancellation reason
  - Errors are logged but don't block cancellation

**`mark_no_show` method:**
- Added refund processing logic:
  - Same flow as cancel_appointment
  - Refund reason indicates "no-show" status
  - Graceful error handling

### 3. Backend Webhook Changes

#### `backend/app/routes/webhooks.py`

**`_create_booking_from_payment` function:**
- Updated to pass `payment_id=payment.id` when creating appointments
- Ensures new appointments are linked to their payment records

### 4. Frontend Components

**No changes needed** - The existing frontend components already:
- Handle cancel/no-show mutations properly
- Invalidate queries on success
- Display updated booking status
- Show success/error feedback through React Query

## Refund Flow

### When Appointment is Cancelled:
1. User clicks "Cancel" button in BookingCard or BookingDetail
2. Frontend calls `useCancelBooking` mutation
3. Backend `cancel_appointment` endpoint is called
4. AppointmentService.cancel_appointment:
   - Updates appointment status to "cancelled"
   - Releases time slots
   - **Checks if appointment.payment_id exists**
   - **Retrieves payment record**
   - **If payment.status == "success", creates refund**
   - Queues cancellation notification
5. Frontend receives updated appointment
6. React Query invalidates bookings queries
7. UI updates to show "cancelled" status

### When Appointment is Marked No-Show:
1. User clicks "No-Show" button in BookingCard or BookingDetail
2. Frontend calls `useMarkNoShow` mutation
3. Backend `mark_no_show` endpoint is called
4. AppointmentService.mark_no_show:
   - Updates appointment status to "no_show"
   - **Checks if appointment.payment_id exists**
   - **Retrieves payment record**
   - **If payment.status == "success", creates refund**
5. Frontend receives updated appointment
6. React Query invalidates bookings queries
7. UI updates to show "no_show" status

## Error Handling

- Refund processing errors are logged but don't block appointment status changes
- If Paystack refund fails, the appointment is still marked as cancelled/no-show
- Customer can contact support if refund doesn't process
- Audit logs capture all refund attempts

## Testing Considerations

The implementation:
- Maintains backward compatibility (payment_id is optional)
- Handles appointments without payments gracefully
- Doesn't break existing appointment workflows
- Follows existing error handling patterns

## Next Steps (Optional)

1. Add refund status display in BookingDetail modal
2. Create refund history view for customers
3. Add refund retry mechanism for failed refunds
4. Send refund confirmation emails to customers
