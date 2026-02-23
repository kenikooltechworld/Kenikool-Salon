# Public Booking Page Enhancement - Design

## Architecture Overview

The enhanced public booking page follows a layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │  PublicBookingApp (Main Container)               │   │
│  │  ├─ HeroSection (Salon Branding)                 │   │
│  │  ├─ TestimonialsSection (Social Proof)           │   │
│  │  ├─ BookingFlow (Multi-step form)                │   │
│  │  │  ├─ ServiceSelector                           │   │
│  │  │  ├─ StaffSelector                             │   │
│  │  │  ├─ TimeSlotSelector                          │   │
│  │  │  ├─ BookingForm (with Payment Option)         │   │
│  │  │  └─ PaymentProcessor (if Pay Now)             │   │
│  │  ├─ BookingConfirmation                          │   │
│  │  ├─ FAQSection (Trust Building)                  │   │
│  │  └─ Footer                                       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         ↓ (API Calls via React Query)
┌─────────────────────────────────────────────────────────┐
│                    Backend Layer                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Public Booking Routes                           │   │
│  │  ├─ GET /public/salon-info                       │   │
│  │  ├─ GET /public/services                         │   │
│  │  ├─ GET /public/staff                            │   │
│  │  ├─ GET /public/availability                     │   │
│  │  ├─ POST /public/bookings                        │   │
│  │  ├─ GET /public/bookings/{id}                    │   │
│  │  ├─ POST /public/bookings/{id}/cancel            │   │
│  │  ├─ POST /public/bookings/{id}/reschedule        │   │
│  │  ├─ GET /public/bookings/testimonials            │   │
│  │  ├─ GET /public/bookings/statistics              │   │
│  │  └─ POST /public/bookings/{id}/notification-pref │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Services                                        │   │
│  │  ├─ PublicBookingService                         │   │
│  │  ├─ PaymentService                               │   │
│  │  ├─ NotificationService                          │   │
│  │  └─ AppointmentReminderService                   │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Celery Tasks                                    │   │
│  │  ├─ send_booking_confirmation_email              │   │
│  │  ├─ send_booking_reminders (24h, 1h)             │   │
│  │  └─ send_cancellation_email                      │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         ↓ (Database & External Services)
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
│  ├─ MongoDB (PublicBooking, Notification, etc.)         │
│  ├─ Paystack (Payment Processing)                       │
│  ├─ Termii (SMS Notifications)                          │
│  └─ Email Service (SMTP)                                │
└─────────────────────────────────────────────────────────┘
```

---

## Component Structure

### Frontend Components

#### 1. PublicBookingApp (Main Container)
**Location:** `salon/src/pages/public/PublicBookingApp.tsx`  
**Status:** Exists (will be enhanced)

**Responsibilities:**
- Fetch salon info from `/public/salon-info`
- Manage booking flow state (current step, booking data)
- Render all sections in correct order
- Handle navigation between steps
- Apply salon branding (colors, logo)

**Props:** None (uses URL subdomain for tenant context)

**State:**
```typescript
interface BookingState {
  currentStep: "hero" | "service" | "staff" | "time" | "form" | "payment" | "confirmation";
  bookingData: Partial<BookingData>;
  confirmationData: any;
  salonInfo: SalonInfo;
}
```

**New Sections to Add:**
- HeroSection (at top)
- TestimonialsSection (after hero)
- BookingFlow (existing, enhanced)
- FAQSection (after booking)
- Footer (at bottom)

---

#### 2. PublicHeroSection (New Component)
**Location:** `salon/src/components/public/PublicHeroSection.tsx`  
**Reuses:** `HeroSection.tsx` from landing page

**Responsibilities:**
- Display salon logo, name, description
- Apply salon primary/secondary colors
- Show "Book Now" CTA button
- Smooth scroll to booking form

**Props:**
```typescript
interface PublicHeroSectionProps {
  salonInfo: SalonInfo;
  onBookNowClick: () => void;
}
```

**Implementation:**
- Adapt `HeroSection.tsx` to accept salon info
- Use salon colors for background and button
- Add smooth scroll behavior
- Support light/dark modes

---

#### 3. PublicTestimonialsSection (New Component)
**Location:** `salon/src/components/public/PublicTestimonialsSection.tsx`  
**Reuses:** `TestimonialsSection.tsx` from landing page

**Responsibilities:**
- Fetch testimonials from backend
- Display testimonials with ratings
- Show customer names and review text
- Handle carousel on mobile

**Props:**
```typescript
interface PublicTestimonialsSectionProps {
  testimonials: Testimonial[];
  isLoading: boolean;
}
```

**Implementation:**
- Fetch from new endpoint: `GET /public/bookings/testimonials`
- Display 3-5 testimonials
- Show star ratings
- Carousel on mobile, grid on desktop

---

#### 4. PublicFAQSection (New Component)
**Location:** `salon/src/components/public/PublicFAQSection.tsx`  
**Reuses:** `FAQSection.tsx` from landing page

**Responsibilities:**
- Display FAQ items with expand/collapse
- Show booking-specific questions
- Support keyboard navigation
- Smooth animations

**Props:**
```typescript
interface PublicFAQSectionProps {
  faqs: FAQ[];
}
```

**Implementation:**
- Use accordion pattern
- Include 5-8 booking-related FAQs
- Support keyboard navigation
- Smooth expand/collapse animations

---

#### 5. PublicBookingStatistics (New Component)
**Location:** `salon/src/components/public/PublicBookingStatistics.tsx`

**Responsibilities:**
- Display booking count, rating, response time
- Animate numbers on load
- Show social proof

**Props:**
```typescript
interface PublicBookingStatisticsProps {
  statistics: {
    totalBookings: number;
    averageRating: number;
    averageResponseTime: number;
  };
}
```

**Implementation:**
- Fetch from new endpoint: `GET /public/bookings/statistics`
- Animate numbers from 0 to final value
- Display in 3-column grid (desktop) or single column (mobile)

---

#### 6. Enhanced BookingForm (Modified)
**Location:** `salon/src/components/public/BookingForm.tsx`  
**Status:** Exists (will be enhanced)

**New Features:**
- Add payment option selector (Pay Now vs Pay Later)
- Show payment methods if "Pay Now" selected
- Integrate PaymentProcessor component

**Props:**
```typescript
interface BookingFormProps {
  onSubmit: (data: BookingFormData) => Promise<void>;
  onPaymentOptionChange?: (option: "now" | "later") => void;
}

interface BookingFormData {
  customerName: string;
  customerEmail: string;
  customerPhone: string;
  notes?: string;
  paymentOption: "now" | "later";
}
```

**Implementation:**
- Add radio buttons for payment option
- Show PaymentProcessor if "Pay Now" selected
- Pass payment_option to backend

---

#### 7. Enhanced BookingConfirmation (Modified)
**Location:** `salon/src/components/public/BookingConfirmation.tsx`  
**Status:** Exists (will be enhanced)

**New Features:**
- Display payment status if payment was made
- Show payment receipt/transaction ID
- Add links to cancellation and rescheduling pages
- Show notification preferences link

**Props:**
```typescript
interface BookingConfirmationProps {
  booking: PublicBookingResponse;
  paymentInfo?: PaymentInfo;
}
```

**Implementation:**
- Display payment status and receipt if applicable
- Add cancellation/rescheduling links
- Add notification preferences link
- Show booking management options

---

#### 8. BookingStatusPage (New Page)
**Location:** `salon/src/pages/public/BookingStatus.tsx`

**Responsibilities:**
- Display booking details
- Show booking status
- Provide cancellation/rescheduling options
- Allow leaving review if completed

**Props:** None (uses URL params for booking ID)

**Implementation:**
- Fetch booking from `/public/bookings/{id}`
- Display booking details
- Show status-specific actions
- Handle cancellation/rescheduling

---

#### 9. NotificationPreferencesPage (New Page)
**Location:** `salon/src/pages/public/NotificationPreferences.tsx`

**Responsibilities:**
- Display notification preference toggles
- Save preferences to backend
- Show success message

**Props:** None (uses URL params for booking ID)

**Implementation:**
- Fetch current preferences
- Display toggles for each notification type
- Save to backend on change
- Show success/error messages

---

### Backend Components

#### 1. Enhanced PublicBookingService
**Location:** `backend/app/services/public_booking_service.py`  
**Status:** Exists (will be enhanced)

**New Methods:**
```python
@staticmethod
def cancel_public_booking(
    tenant_id: ObjectId,
    booking_id: ObjectId,
    cancellation_reason: str
) -> PublicBooking:
    """Cancel a public booking and process refund if applicable."""
    # Validate cancellation is allowed
    # Update booking status to cancelled
    # Process refund if payment was made
    # Send cancellation email
    # Invalidate availability cache
    pass

@staticmethod
def reschedule_public_booking(
    tenant_id: ObjectId,
    booking_id: ObjectId,
    new_date: date,
    new_time: time
) -> PublicBooking:
    """Reschedule a public booking to new date/time."""
    # Validate rescheduling is allowed
    # Check availability for new slot
    # Update booking with new date/time
    # Send rescheduling confirmation email
    # Invalidate availability cache
    pass

@staticmethod
def get_booking_testimonials(
    tenant_id: ObjectId,
    limit: int = 5
) -> List[Testimonial]:
    """Get testimonials from completed bookings."""
    # Find completed bookings with ratings
    # Filter ratings >= 4 stars
    # Return most recent testimonials
    pass

@staticmethod
def get_booking_statistics(
    tenant_id: ObjectId
) -> Dict:
    """Get booking statistics for social proof."""
    # Count total bookings
    # Calculate average rating
    # Calculate average response time
    # Return statistics
    pass
```

---

#### 2. New Routes
**Location:** `backend/app/routes/public_booking.py`  
**Status:** Exists (will be enhanced)

**New Endpoints:**
```python
@router.post("/public/bookings/{booking_id}/cancel")
async def cancel_public_booking(
    request: Request,
    booking_id: str,
    cancellation_data: PublicBookingCancellation
):
    """Cancel a public booking."""
    pass

@router.post("/public/bookings/{booking_id}/reschedule")
async def reschedule_public_booking(
    request: Request,
    booking_id: str,
    reschedule_data: PublicBookingReschedule
):
    """Reschedule a public booking."""
    pass

@router.get("/public/bookings/testimonials")
async def get_booking_testimonials(request: Request):
    """Get testimonials from completed bookings."""
    pass

@router.get("/public/bookings/statistics")
async def get_booking_statistics(request: Request):
    """Get booking statistics for social proof."""
    pass

@router.post("/public/bookings/{booking_id}/notification-preferences")
async def update_notification_preferences(
    request: Request,
    booking_id: str,
    preferences: NotificationPreferences
):
    """Update notification preferences for a booking."""
    pass
```

---

#### 3. Celery Tasks
**Location:** `backend/app/tasks/notifications.py`  
**Status:** Exists (will be enhanced)

**New Tasks:**
```python
@shared_task
def send_booking_reminders():
    """Send 24h and 1h reminder emails/SMS for upcoming bookings."""
    # Find bookings 24 hours away (not yet reminded)
    # Find bookings 1 hour away (not yet reminded)
    # Send email/SMS reminders
    # Update booking with reminder status
    pass

@shared_task
def send_cancellation_email(booking_id: str):
    """Send cancellation confirmation email."""
    # Fetch booking details
    # Send cancellation email
    # Log notification
    pass
```

---

#### 4. New Models
**Location:** `backend/app/models/`

**PublicBookingNotificationPreference:**
```python
class PublicBookingNotificationPreference(Document):
    booking_id: ObjectId
    customer_email: str
    customer_phone: str
    send_confirmation_email: bool = True
    send_24h_reminder_email: bool = True
    send_1h_reminder_email: bool = True
    send_sms_reminders: bool = False
    created_at: datetime
    updated_at: datetime
```

---

## Data Flow

### Booking Creation Flow
```
1. User selects service
   ↓
2. User selects staff
   ↓
3. User selects time slot
   ↓
4. User fills form + selects payment option
   ↓
5. If "Pay Later":
   - POST /public/bookings (payment_option: "later")
   - Backend creates booking
   - Backend sends confirmation email
   - Frontend shows confirmation
   ↓
6. If "Pay Now":
   - POST /public/bookings (payment_option: "now")
   - Backend creates booking with payment_status: "pending"
   - Frontend shows PaymentProcessor
   - User completes payment
   - POST /payments/initialize
   - User redirected to Paystack
   - Paystack redirects back with reference
   - POST /payments/{reference}/verify
   - Backend updates booking with payment_status: "success"
   - Backend sends confirmation email with receipt
   - Frontend shows confirmation
```

### Reminder Flow
```
1. Booking created at 2024-01-15 10:00
   Appointment scheduled for 2024-01-20 14:00
   ↓
2. Celery task runs every 15 minutes
   ↓
3. 2024-01-19 14:00 (24 hours before):
   - Task finds booking
   - Sends 24h reminder email
   - Updates booking: reminder_24h_sent = True
   ↓
4. 2024-01-20 13:00 (1 hour before):
   - Task finds booking
   - Sends 1h reminder email/SMS
   - Updates booking: reminder_1h_sent = True
```

### Cancellation Flow
```
1. User clicks cancellation link in email
   ↓
2. Frontend navigates to BookingStatus page
   ↓
3. User confirms cancellation
   ↓
4. POST /public/bookings/{id}/cancel
   ↓
5. Backend:
   - Validates cancellation is allowed
   - Updates booking status to "cancelled"
   - Processes refund if payment was made
   - Sends cancellation email
   - Invalidates availability cache
   ↓
6. Frontend shows cancellation confirmation
```

---

## Database Schema Changes

### PublicBooking Model (Enhanced)
```python
class PublicBooking(Document):
    # Existing fields
    tenant_id: ObjectId
    customer_id: ObjectId
    service_id: ObjectId
    staff_id: ObjectId
    booking_date: date
    booking_time: str
    duration_minutes: int
    status: PublicBookingStatus
    
    # New fields
    payment_option: str  # "now" or "later"
    payment_status: Optional[str]  # "pending", "success", "failed"
    payment_id: Optional[str]
    cancellation_reason: Optional[str]
    cancelled_at: Optional[datetime]
    rescheduled_from: Optional[ObjectId]  # Reference to original booking if rescheduled
    reminder_24h_sent: bool = False
    reminder_1h_sent: bool = False
    
    # Existing fields
    created_at: datetime
    updated_at: datetime
```

### New Collections
```python
# PublicBookingNotificationPreference
class PublicBookingNotificationPreference(Document):
    booking_id: ObjectId
    customer_email: str
    customer_phone: str
    send_confirmation_email: bool = True
    send_24h_reminder_email: bool = True
    send_1h_reminder_email: bool = True
    send_sms_reminders: bool = False
    created_at: datetime
    updated_at: datetime
```

---

## API Contracts

### New Endpoints

#### 1. Cancel Booking
```
POST /public/bookings/{booking_id}/cancel

Request:
{
  "cancellation_reason": "string"
}

Response:
{
  "id": "string",
  "status": "cancelled",
  "cancelled_at": "2024-01-15T10:30:00Z",
  "message": "Booking cancelled successfully"
}
```

#### 2. Reschedule Booking
```
POST /public/bookings/{booking_id}/reschedule

Request:
{
  "new_date": "2024-01-20",
  "new_time": "15:00"
}

Response:
{
  "id": "string",
  "booking_date": "2024-01-20",
  "booking_time": "15:00",
  "message": "Booking rescheduled successfully"
}
```

#### 3. Get Testimonials
```
GET /public/bookings/testimonials?limit=5

Response:
[
  {
    "customer_name": "John Doe",
    "rating": 5,
    "review": "Great service!",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

#### 4. Get Statistics
```
GET /public/bookings/statistics

Response:
{
  "total_bookings": 500,
  "average_rating": 4.8,
  "average_response_time": 120
}
```

#### 5. Update Notification Preferences
```
POST /public/bookings/{booking_id}/notification-preferences

Request:
{
  "send_confirmation_email": true,
  "send_24h_reminder_email": true,
  "send_1h_reminder_email": true,
  "send_sms_reminders": false
}

Response:
{
  "message": "Preferences updated successfully"
}
```

---

## Frontend State Management

### Zustand Store (if needed)
```typescript
interface PublicBookingStore {
  // State
  bookingData: Partial<BookingData>;
  currentStep: BookingStep;
  paymentOption: "now" | "later";
  
  // Actions
  setBookingData: (data: Partial<BookingData>) => void;
  setCurrentStep: (step: BookingStep) => void;
  setPaymentOption: (option: "now" | "later") => void;
  resetBooking: () => void;
}
```

### React Query Hooks
```typescript
// Existing hooks (will be enhanced)
usePublicServices()
usePublicStaff(serviceId)
usePublicAvailability(serviceId, staffId, date)
useCreatePublicBooking()
usePublicBooking(bookingId)

// New hooks
usePublicTestimonials()
usePublicBookingStatistics()
useCancelPublicBooking()
useReschedulePublicBooking()
useNotificationPreferences(bookingId)
useUpdateNotificationPreferences()
```

---

## Error Handling

### Frontend Error Handling
```typescript
// Booking creation errors
- "Service not found" → Show error alert
- "Staff not available" → Show error alert
- "Time slot not available" → Show error alert
- "Invalid email/phone" → Show field error
- "Network error" → Show retry button

// Payment errors
- "Payment initialization failed" → Show error alert with retry
- "Payment verification failed" → Show error alert with retry
- "Payment declined" → Show error alert with retry option

// Cancellation errors
- "Cancellation not allowed" → Show error message
- "Refund processing failed" → Show error alert
```

### Backend Error Handling
```python
# Booking creation errors
- 404: Service/Staff not found
- 409: Time slot conflict
- 400: Invalid input data
- 500: Internal server error

# Cancellation errors
- 404: Booking not found
- 400: Cancellation not allowed (too close to appointment)
- 500: Refund processing failed

# Rescheduling errors
- 404: Booking not found
- 400: Rescheduling not allowed
- 409: New time slot not available
- 500: Internal server error
```

---

## Performance Considerations

### Frontend Optimization
- Lazy load testimonials section (below fold)
- Lazy load FAQ section (below fold)
- Optimize service/staff images (WebP format, responsive sizes)
- Cache salon info in localStorage
- Debounce availability checks
- Memoize components to prevent unnecessary re-renders

### Backend Optimization
- Cache salon info (5 minute TTL)
- Cache services list (5 minute TTL)
- Cache staff list (5 minute TTL)
- Cache availability (1 minute TTL)
- Use database indexes on frequently queried fields
- Batch email sending for reminders

### Database Optimization
- Index on: tenant_id, booking_date, status
- Index on: booking_id, customer_email
- Index on: created_at (for testimonials)

---

## Security Considerations

### Frontend Security
- Sanitize user input (name, email, phone, notes)
- Validate email and phone format
- CSRF protection (use existing middleware)
- XSS prevention (React escapes by default)
- Rate limiting on booking submission

### Backend Security
- Validate all input data
- Check tenant isolation (ensure user can only access their tenant's data)
- Rate limit booking endpoint (10 requests per minute per IP)
- Validate payment reference before processing
- Log all cancellations and refunds
- Encrypt sensitive data (payment info, phone numbers)

---

## Testing Strategy

### Unit Tests
- Test booking creation with various inputs
- Test cancellation logic
- Test rescheduling logic
- Test notification preference updates
- Test testimonial filtering

### Integration Tests
- Test full booking flow (service → staff → time → form → confirmation)
- Test payment flow (booking → payment → confirmation)
- Test cancellation flow (booking → cancellation → refund)
- Test reminder sending (Celery task)

### E2E Tests
- Test complete booking journey on desktop
- Test complete booking journey on mobile
- Test payment flow with Paystack
- Test email delivery

### Performance Tests
- Test page load time (target: < 2 seconds)
- Test booking creation response time (target: < 1 second)
- Test with 1000 concurrent users

---

## Deployment Checklist

- [ ] All tests passing
- [ ] Code review completed
- [ ] Database migrations run
- [ ] Celery tasks configured
- [ ] Email templates tested
- [ ] Payment gateway configured
- [ ] SMS gateway configured
- [ ] Monitoring/logging configured
- [ ] Backup strategy in place
- [ ] Rollback plan documented

