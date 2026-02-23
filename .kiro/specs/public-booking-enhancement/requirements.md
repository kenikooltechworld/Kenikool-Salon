# Public Booking Page Enhancement - Requirements

## Feature Overview

Enhance the public booking page from a functional MVP to a production-ready, conversion-optimized booking experience. The page will include visual branding, trust indicators, payment integration, booking management, and automated notifications.

**Feature Name:** public-booking-enhancement  
**Status:** New Feature  
**Priority:** High  
**Estimated Effort:** 5-6 days  
**Expected Impact:** +20-30% conversion rate, +15-20% revenue, -30-40% no-shows

---

## Current State Analysis

### ✅ What Already Exists (DO NOT DUPLICATE)

#### Frontend Components (Reusable)
- **Landing Page Components** (in `salon/src/components/landing/`)
  - `HeroSection.tsx` - Hero banner with animations, salon branding support
  - `TestimonialsSection.tsx` - Customer testimonials with ratings
  - `FAQSection.tsx` - FAQ accordion with collapsible items
  - `BenefitsSection.tsx` - Benefits display
  - `CTASection.tsx` - Call-to-action section
  - `LandingFooter.tsx` - Footer with contact info

- **Payment Components** (in `salon/src/components/pos/`)
  - `PaymentProcessor.tsx` - Full payment UI with multiple payment methods
  - `TipHandler.tsx` - Tip handling logic
  - `SplitPayment.tsx` - Split payment support

- **Booking Components** (in `salon/src/components/public/`)
  - `ServiceSelector.tsx` - Service selection with images, prices, duration
  - `StaffSelector.tsx` - Staff selection with avatars and bios
  - `TimeSlotSelector.tsx` - Time slot selection with date picker
  - `BookingForm.tsx` - Customer form with validation
  - `BookingConfirmation.tsx` - Confirmation display

- **Notification Components** (in `salon/src/components/notifications/`)
  - `NotificationCenter.tsx` - Notification UI
  - `NotificationList.tsx` - Notification list display

- **UI Components** (35+ in `salon/src/components/ui/`)
  - Button, Input, Textarea, Select, Checkbox, Radio
  - Card, Badge, Avatar, Spinner, Alert, Modal, Dialog
  - Calendar, Table, ScrollArea, etc.

#### Frontend Hooks (Reusable)
- `usePublicBooking.ts` - Public booking operations (services, staff, availability, create booking)
- `usePayment.ts` - Payment initialization and verification
- `useNotifications.ts` - Notification operations
- `useServices.ts` - Service operations
- `useStaff.ts` - Staff operations

#### Backend Infrastructure (Reusable)
- **Public Booking Endpoints** (in `backend/app/routes/public_booking.py`)
  - `GET /public/salon-info` - Salon branding info
  - `GET /public/services` - List services
  - `GET /public/staff` - List staff
  - `GET /public/availability` - Time slots
  - `POST /public/bookings` - Create booking
  - `GET /public/bookings/{id}` - Get booking details

- **Payment Endpoints** (in `backend/app/routes/payments.py`)
  - `POST /payments/initialize` - Initialize payment
  - `GET /payments/{reference}/verify` - Verify payment
  - Paystack integration with webhook support

- **Notification System** (in `backend/app/routes/notifications.py`)
  - `GET /notifications` - List notifications
  - `POST /notifications/preferences` - Update preferences
  - Email and SMS support (Termii integration)

- **Models** (in `backend/app/models/`)
  - `PublicBooking` - Public booking model with payment_option support
  - `Payment` - Payment model
  - `Notification` - Notification model
  - `Tenant` - Tenant model with branding fields

- **Services** (in `backend/app/services/`)
  - `PublicBookingService` - Booking creation with idempotency and race condition prevention
  - `PaymentService` - Payment processing
  - `NotificationService` - Notification sending
  - `AppointmentReminderService` - Reminder scheduling

- **Email Templates** (in `backend/app/templates/`)
  - `booking_confirmation.html` - Confirmation email template
  - `booking_cancellation.html` - Cancellation email template

#### Utilities (Reusable)
- `formatCurrency()` - Format prices
- `formatDate()` - Format dates
- `formatTime()` - Format times
- `isValidEmail()`, `isValidPhone()` - Validation
- `apiClient` - HTTP client with JWT support

#### Stores (Reusable)
- `auth.ts` - Authentication state
- `tenant.ts` - Tenant context
- `ui.ts` - UI state (theme, modals)

---

## Requirements by Phase

### Phase 1: Visual Branding & Trust Signals (1 day)

#### 1.1 Hero Section with Salon Branding
**Acceptance Criteria:**
1. WHEN user visits public booking page, THE hero section SHALL display at the top with salon logo, name, and description
2. WHEN salon has primary/secondary colors set, THE hero section SHALL use those colors for styling
3. WHEN hero section is displayed, THE section SHALL include a "Book Now" CTA button that scrolls to booking form
4. WHEN user is on mobile, THE hero section SHALL be responsive with appropriate spacing and text sizing
5. WHEN hero section loads, THE section SHALL display smoothly with fade-in animation

**Reusable Component:** `HeroSection.tsx` from landing page  
**Customization Needed:** Adapt to use salon branding from `/public/salon-info` endpoint

**Technical Details:**
- Fetch salon info (logo_url, primary_color, secondary_color, description) from backend
- Apply salon colors to hero section background and CTA button
- Add smooth scroll to booking form when CTA clicked
- Support both light and dark modes
- Mobile-optimized with safe area insets

---

#### 1.2 Testimonials Section
**Acceptance Criteria:**
1. WHEN testimonials section is displayed, THE section SHALL show 3-5 customer testimonials with names, ratings, and review text
2. WHEN testimonials are displayed, EACH testimonial SHALL show a star rating (1-5 stars)
3. WHEN user hovers over testimonial, THE testimonial card SHALL have a subtle hover effect
4. WHEN user is on mobile, THE testimonials SHALL display in a scrollable carousel or single column
5. WHEN no testimonials exist, THE section SHALL display a placeholder message

**Reusable Component:** `TestimonialsSection.tsx` from landing page  
**Data Source:** Fetch from backend (new endpoint needed: `GET /public/bookings/testimonials`)

**Technical Details:**
- Create new backend endpoint to fetch testimonials from completed bookings
- Filter testimonials with ratings >= 4 stars
- Limit to 5 most recent testimonials
- Display customer name, rating, and review text
- Support carousel on mobile, grid on desktop

---

#### 1.3 FAQ Section
**Acceptance Criteria:**
1. WHEN FAQ section is displayed, THE section SHALL show 5-8 common booking questions with answers
2. WHEN user clicks on a question, THE answer SHALL expand/collapse smoothly
3. WHEN user is on mobile, THE FAQ items SHALL be full width and easy to tap
4. WHEN FAQ section loads, THE section SHALL display all questions collapsed initially
5. WHEN user scrolls to FAQ, THE section SHALL be visible and accessible

**Reusable Component:** `FAQSection.tsx` from landing page  
**Data Source:** Static FAQ content (can be customized per salon in future)

**Technical Details:**
- Use accordion pattern for expand/collapse
- Include questions about: booking process, cancellation policy, payment methods, rescheduling, no-show policy
- Support keyboard navigation (arrow keys, Enter)
- Smooth animations for expand/collapse

---

#### 1.4 Booking Statistics/Social Proof
**Acceptance Criteria:**
1. WHEN page loads, THE statistics section SHALL display booking count, customer satisfaction, and response time
2. WHEN statistics are displayed, THE numbers SHALL be animated from 0 to final value
3. WHEN user is on mobile, THE statistics SHALL display in a single column
4. WHEN statistics load, THE section SHALL show: "500+ bookings", "4.8★ rating", "2h response time"

**Technical Details:**
- Fetch statistics from backend (new endpoint: `GET /public/bookings/statistics`)
- Calculate: total bookings, average rating, average response time
- Animate numbers on page load using CSS animations
- Display in 3-column grid on desktop, single column on mobile

---

### Phase 2: Payment Integration (1-2 days)

#### 2.1 Payment Option Selection
**Acceptance Criteria:**
1. WHEN user reaches booking form, THE form SHALL include a payment option selector (Pay Now vs Pay Later)
2. WHEN user selects "Pay Now", THE form SHALL show payment method options (Card, Mobile Money, etc.)
3. WHEN user selects "Pay Later", THE form SHALL proceed to confirmation without payment
4. WHEN user selects "Pay Now", THE booking confirmation SHALL show payment status
5. WHEN payment is successful, THE confirmation email SHALL include payment receipt

**Reusable Component:** `PaymentProcessor.tsx` from POS system  
**Backend Support:** Already supports `payment_option` field in `PublicBookingCreate` schema

**Technical Details:**
- Add toggle/radio button for payment option in `BookingForm.tsx`
- If "Pay Now" selected, show payment method selection
- Integrate `PaymentProcessor.tsx` component
- Pass booking data to payment processor
- Handle payment success/failure states
- Update booking confirmation to show payment status

---

#### 2.2 Payment Confirmation & Receipt
**Acceptance Criteria:**
1. WHEN payment is successful, THE confirmation page SHALL display payment receipt with transaction ID
2. WHEN payment is successful, THE confirmation email SHALL include payment details and receipt
3. WHEN payment fails, THE user SHALL see error message with retry option
4. WHEN user completes payment, THE booking status SHALL be updated to "confirmed"

**Technical Details:**
- Update `BookingConfirmation.tsx` to display payment info if payment_option was "now"
- Update email template to include payment receipt
- Add payment status to booking response
- Handle payment failure with retry logic

---

### Phase 3: Booking Management (2 days)

#### 3.1 Cancellation Endpoint
**Acceptance Criteria:**
1. WHEN user clicks cancellation link in email, THE user SHALL be taken to cancellation page
2. WHEN user confirms cancellation, THE booking status SHALL change to "cancelled"
3. WHEN booking is cancelled, THE user SHALL receive cancellation confirmation email
4. WHEN booking is cancelled within 24 hours, THE user SHALL be eligible for refund (if paid)
5. WHEN booking is cancelled, THE time slot SHALL become available for other customers

**Backend Implementation:**
- Create new endpoint: `POST /public/bookings/{id}/cancel`
- Validate cancellation is allowed (not within 2 hours of appointment)
- Update booking status to "cancelled"
- Send cancellation email
- Process refund if payment was made
- Invalidate availability cache

---

#### 3.2 Rescheduling Endpoint
**Acceptance Criteria:**
1. WHEN user clicks reschedule link in email, THE user SHALL be taken to rescheduling page
2. WHEN user selects new date/time, THE system SHALL check availability
3. WHEN new slot is available, THE booking SHALL be updated with new date/time
4. WHEN booking is rescheduled, THE user SHALL receive confirmation email with new details
5. WHEN booking is rescheduled, THE old time slot SHALL become available

**Backend Implementation:**
- Create new endpoint: `POST /public/bookings/{id}/reschedule`
- Validate rescheduling is allowed (at least 24 hours before appointment)
- Check availability for new date/time
- Update booking with new date/time
- Send rescheduling confirmation email
- Invalidate availability cache

---

#### 3.3 Booking Status Page
**Acceptance Criteria:**
1. WHEN user visits booking status page, THE page SHALL display current booking details
2. WHEN booking is pending, THE page SHALL show "Awaiting confirmation" status
3. WHEN booking is confirmed, THE page SHALL show "Confirmed" status with appointment details
4. WHEN booking is completed, THE page SHALL show "Completed" status with option to leave review
5. WHEN booking is cancelled, THE page SHALL show "Cancelled" status with cancellation reason

**Frontend Implementation:**
- Create new page: `salon/src/pages/public/BookingStatus.tsx`
- Fetch booking details from backend using booking ID
- Display booking status, date, time, staff, service
- Show cancellation/rescheduling options if applicable
- Show review option if booking is completed

---

### Phase 4: Notifications & Reminders (1 day)

#### 4.1 Booking Confirmation Email
**Acceptance Criteria:**
1. WHEN booking is created, THE confirmation email SHALL be sent within 1 minute
2. WHEN confirmation email is sent, THE email SHALL include booking details (date, time, staff, service)
3. WHEN confirmation email is sent, THE email SHALL include cancellation and rescheduling links
4. WHEN confirmation email is sent, THE email SHALL include salon contact information
5. WHEN user receives email, THE email SHALL be mobile-friendly and branded with salon colors

**Backend Support:** Already implemented in `PublicBookingService.send_booking_confirmation_email()`  
**Email Template:** Already exists in `backend/app/templates/booking_confirmation.html`

**Verification Needed:**
- Ensure email is being sent after booking creation
- Verify email template includes all required information
- Test email on mobile devices

---

#### 4.2 Reminder Notifications (24h & 1h before)
**Acceptance Criteria:**
1. WHEN booking is 24 hours away, THE system SHALL send reminder email/SMS
2. WHEN booking is 1 hour away, THE system SHALL send reminder email/SMS
3. WHEN reminder is sent, THE message SHALL include booking details and cancellation link
4. WHEN user opts out of reminders, THE system SHALL NOT send reminders
5. WHEN reminder is sent, THE system SHALL log the reminder in notification history

**Backend Implementation:**
- Create Celery task: `send_booking_reminders` in `backend/app/tasks/notifications.py`
- Schedule task to run every 15 minutes
- Find bookings that are 24 hours away (not yet reminded)
- Find bookings that are 1 hour away (not yet reminded)
- Send email/SMS reminders
- Update booking with reminder status
- Support opt-out via notification preferences

---

#### 4.3 Notification Preferences Page
**Acceptance Criteria:**
1. WHEN user visits notification preferences page, THE page SHALL show opt-in/opt-out options
2. WHEN user can toggle: confirmation email, 24h reminder, 1h reminder, SMS notifications
3. WHEN user saves preferences, THE preferences SHALL be persisted to backend
4. WHEN user has opted out, THE system SHALL NOT send those notifications
5. WHEN user visits page again, THE preferences SHALL be restored from backend

**Frontend Implementation:**
- Create new page: `salon/src/pages/public/NotificationPreferences.tsx`
- Display toggle switches for each notification type
- Save preferences to backend
- Show success message after saving

**Backend Implementation:**
- Create new model: `PublicBookingNotificationPreference`
- Create new endpoint: `POST /public/bookings/{id}/notification-preferences`
- Store user preferences (email, phone, notification types)

---

### Phase 5: Enhanced Service & Staff Information (1 day)

#### 5.1 Enhanced Service Display
**Acceptance Criteria:**
1. WHEN service is displayed, THE card SHALL show service image, name, description, duration, price
2. WHEN service has benefits/features, THE card SHALL display them as bullet points
3. WHEN user hovers over service, THE card SHALL show additional details
4. WHEN user is on mobile, THE service cards SHALL be full width and easy to tap
5. WHEN service image is missing, THE card SHALL show a placeholder image

**Frontend Implementation:**
- Enhance `ServiceSelector.tsx` to display more information
- Add service benefits/features display
- Add hover effects and animations
- Improve mobile responsiveness

**Backend Support:**
- Ensure Service model has: image, description, duration, price, benefits
- Update `PublicServiceResponse` schema to include all fields

---

#### 5.2 Enhanced Staff Display
**Acceptance Criteria:**
1. WHEN staff member is displayed, THE card SHALL show avatar, name, bio, specialties, rating
2. WHEN staff has specialties, THE card SHALL display them as tags
3. WHEN staff has rating, THE card SHALL display star rating and review count
4. WHEN user hovers over staff, THE card SHALL show additional details
5. WHEN user is on mobile, THE staff cards SHALL be full width and easy to tap

**Frontend Implementation:**
- Enhance `StaffSelector.tsx` to display more information
- Add specialties display as tags
- Add rating display with star icons
- Add hover effects and animations
- Improve mobile responsiveness

**Backend Support:**
- Ensure Staff model has: specialties, rating, review_count
- Update `PublicStaffResponse` schema to include all fields

---

## Acceptance Criteria Summary

### Overall Page Requirements
1. WHEN user visits public booking page, THE page SHALL load within 2 seconds
2. WHEN page loads, THE page SHALL display hero section, testimonials, FAQ, and booking form
3. WHEN user completes booking, THE confirmation email SHALL be sent within 1 minute
4. WHEN user is on mobile, THE page SHALL be fully responsive and touch-friendly
5. WHEN user is on desktop, THE page SHALL display in a professional, branded layout

### Performance Requirements
- Page load time: < 2 seconds
- Time to interactive: < 3 seconds
- Lighthouse score: > 90
- Mobile-friendly: Yes
- Accessibility: WCAG 2.1 AA compliant

### Security Requirements
- All endpoints require HTTPS
- CSRF protection enabled
- Rate limiting on booking endpoint (10 requests per minute per IP)
- Input validation on all forms
- SQL injection prevention
- XSS prevention

### Conversion Requirements
- Booking completion rate: > 70%
- Payment success rate: > 95%
- No-show rate: < 20%
- Customer satisfaction: > 4.5/5 stars

---

## Out of Scope

The following features are NOT included in this enhancement:

1. **Loyalty Program** - Tracking returning customers and offering rewards
2. **Analytics Dashboard** - Tracking booking sources and conversion rates
3. **A/B Testing** - Testing different layouts and CTAs
4. **Waiting List** - Notifying customers when slots become available
5. **Service Bundles** - Allowing booking multiple services together
6. **Multi-language Support** - Supporting multiple languages
7. **Internationalization** - Supporting multiple currencies and timezones
8. **Advanced Personalization** - Recommending services based on history
9. **Video Consultations** - Allowing video calls before booking
10. **Appointment Reminders via Push Notifications** - Mobile app push notifications

---

## Dependencies

### Frontend Dependencies
- React 19.2.0 (already installed)
- TypeScript 5.9.3 (already installed)
- @tanstack/react-query 5.28+ (already installed)
- Zustand 4.4+ (already installed)
- Tailwind CSS 3.4+ (already installed)
- Framer Motion (for animations, may need to install)

### Backend Dependencies
- FastAPI (already installed)
- MongoDB (already installed)
- Celery (already installed)
- Paystack SDK (already installed)
- Termii SDK (already installed)

### External Services
- Paystack (payment processing)
- Termii (SMS notifications)
- Email service (SMTP)

---

## Success Metrics

### Conversion Metrics
- Booking completion rate: Increase from 60% to 75%+
- Payment success rate: Maintain > 95%
- Average booking value: Increase by 15-20% (with upfront payment)

### User Experience Metrics
- Page load time: < 2 seconds
- Time to complete booking: < 5 minutes
- Mobile conversion rate: > 70% of desktop

### Business Metrics
- No-show rate: Decrease from 25% to 15%
- Customer satisfaction: Increase from 4.2 to 4.7 stars
- Revenue from upfront payments: +20% of total booking revenue

### Support Metrics
- Support inquiries: Decrease by 30% (due to FAQ and booking management)
- Cancellation requests: Decrease by 20% (due to rescheduling option)

---

## Timeline

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| Phase 1: Branding & Trust | 1 day | Day 1 | Day 1 |
| Phase 2: Payment Integration | 1-2 days | Day 2 | Day 3 |
| Phase 3: Booking Management | 2 days | Day 4 | Day 5 |
| Phase 4: Notifications | 1 day | Day 6 | Day 6 |
| Phase 5: Enhanced Info | 1 day | Day 7 | Day 7 |
| **Total** | **5-6 days** | | |

---

## Risk Assessment

### High Risk
- Payment integration complexity (mitigation: reuse existing PaymentProcessor)
- Email delivery reliability (mitigation: use existing email service)
- Race conditions in booking (mitigation: use existing idempotency logic)

### Medium Risk
- Mobile responsiveness issues (mitigation: test on multiple devices)
- Performance degradation (mitigation: optimize images and lazy load)
- Notification delivery delays (mitigation: use Celery with retry logic)

### Low Risk
- UI/UX issues (mitigation: reuse existing components)
- Data validation issues (mitigation: use existing validation utilities)
- Styling conflicts (mitigation: use Tailwind CSS)

---

## Notes

- All components should be reused from existing codebase to avoid duplication
- All backend endpoints should follow existing patterns and conventions
- All email templates should be branded with salon colors
- All pages should be mobile-responsive and accessible
- All code should include proper error handling and logging
- All features should be tested with real data before deployment

