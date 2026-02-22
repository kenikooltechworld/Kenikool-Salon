# Booking Display Issue - Root Cause & Fix

## Problem
Bookings created through the authenticated booking page were not appearing in the Bookings list, even though they existed in the database's Appointment collection.

## Root Cause
**Field Name Mismatch Between Backend and Frontend**

The backend API returns appointment data with snake_case field names:
- `start_time`, `end_time`, `customer_id`, `staff_id`, `service_id`, etc.

But the frontend Booking type expects camelCase field names:
- `startTime`, `endTime`, `customerId`, `staffId`, `serviceId`, etc.

When the frontend received the API response, it couldn't find the expected fields (e.g., `booking.startTime` was undefined because the data had `booking.start_time`). This caused:
1. The BookingList component to fail when trying to access `booking.startTime`
2. Bookings to not render properly in the UI
3. The "No bookings found" message to display even though data was fetched

## Solution
Added response transformation in all appointment-related hooks in `salon/src/hooks/useBookings.ts`:

### Hooks Updated:
1. **useBookings()** - Transforms list of appointments
2. **useBooking()** - Transforms single appointment
3. **useCreateBooking()** - Transforms created appointment response
4. **useConfirmBooking()** - Transforms confirmed appointment
5. **useCancelBooking()** - Transforms cancelled appointment
6. **useCompleteBooking()** - Transforms completed appointment
7. **useMarkNoShow()** - Transforms no-show appointment
8. **useCalendarView()** - Transforms calendar appointments

### Transformation Pattern:
```typescript
// Transform snake_case from backend to camelCase for frontend
return (data.data || []).map((appt: any) => ({
  id: appt.id,
  customerId: appt.customer_id,
  staffId: appt.staff_id,
  serviceId: appt.service_id,
  locationId: appt.location_id,
  startTime: appt.start_time,
  endTime: appt.end_time,
  status: appt.status,
  notes: appt.notes,
  price: appt.price,
  cancellationReason: appt.cancellation_reason,
  cancelledAt: appt.cancelled_at,
  cancelledBy: appt.cancelled_by,
  noShowReason: appt.no_show_reason,
  markedNoShowAt: appt.marked_no_show_at,
  confirmedAt: appt.confirmed_at,
  createdAt: appt.created_at,
  updatedAt: appt.updated_at,
}));
```

## Impact
- Bookings now display correctly in the Bookings page after creation
- All booking operations (confirm, cancel, complete, mark no-show) work properly
- Calendar views display appointments correctly
- No database changes required - purely a frontend data transformation fix

## Files Modified
- `salon/src/hooks/useBookings.ts` - Added snake_case to camelCase transformation to all hooks
