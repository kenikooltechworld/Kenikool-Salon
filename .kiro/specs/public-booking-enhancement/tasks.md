# Public Booking Page Enhancement - Implementation Tasks

## Phase 1: Visual Branding & Trust Signals (1 day)

### 1.1 Create PublicHeroSection Component
- [ ] Create `salon/src/components/public/PublicHeroSection.tsx`
- [ ] Adapt `HeroSection.tsx` from landing page to accept salon info
- [ ] Display salon logo, name, description
- [ ] Apply salon primary/secondary colors
- [ ] Add "Book Now" CTA button with smooth scroll
- [ ] Support light/dark modes
- [ ] Test on mobile and desktop
- [ ] Add TypeScript types and prop validation

**Acceptance Criteria:**
- Hero section displays at top of page
- Salon colors are applied correctly
- "Book Now" button scrolls to booking form
- Mobile responsive with proper spacing
- Smooth fade-in animation on load

**Reusable Component:** `HeroSection.tsx` from landing page  
**Files to Modify:** `salon/src/pages/public/PublicBookingApp.tsx`

---

### 1.2 Create PublicTestimonialsSection Component
- [ ] Create `salon/src/components/public/PublicTestimonialsSection.tsx`
- [ ] Adapt `TestimonialsSection.tsx` from landing page
- [ ] Create hook: `usePublicTestimonials()` to fetch testimonials
- [ ] Display 3-5 testimonials with ratings
- [ ] Show customer names and review text
- [ ] Implement carousel on mobile, grid on desktop
- [ ] Add loading and error states
- [ ] Test with real testimonial data

**Acceptance Criteria:**
- Testimonials display with ratings
- Carousel works on mobile
- Grid layout on desktop
- Loading state shows spinner
- Error state shows retry button

**Backend Endpoint Needed:** `GET /public/bookings/testimonials`  
**Files to Create:** `salon/src/hooks/usePublicTestimonials.ts`

---

### 1.3 Create PublicFAQSection Component
- [ ] Create `salon/src/components/public/PublicFAQSection.tsx`
- [ ] Adapt `FAQSection.tsx` from landing page
- [ ] Add 5-8 booking-specific FAQ items
- [ ] Implement expand/collapse with smooth animations
- [ ] Support keyboard navigation (arrow keys, Enter)
- [ ] Test accessibility with screen reader
- [ ] Mobile responsive

**Acceptance Criteria:**
- FAQ items expand/collapse smoothly
- Keyboard navigation works
- Mobile responsive
- All items collapsed initially
- Smooth animations

**FAQ Content:**
- How do I book an appointment?
- Can I cancel or reschedule?
- What payment methods do you accept?
- What is your cancellation policy?
- How will I receive reminders?
- What if I'm late?
- Do you offer group bookings?
- How do I leave a review?

---

### 1.4 Create PublicBookingStatistics Component
- [ ] Create `salon/src/components/public/PublicBookingStatistics.tsx`
- [ ] Create hook: `usePublicBookingStatistics()` to fetch statistics
- [ ] Display: total bookings, average rating, response time
- [ ] Animate numbers from 0 to final value on load
- [ ] 3-column grid on desktop, single column on mobile
- [ ] Add loading state

**Acceptance Criteria:**
- Statistics display with animated numbers
- Grid layout on desktop
- Single column on mobile
- Loading state shows skeleton
- Numbers animate smoothly

**Backend Endpoint Needed:** `GET /public/bookings/statistics`  
**Files to Create:** `salon/src/hooks/usePublicBookingStatistics.ts`

---

### 1.5 Update PublicBookingApp to Include New Sections
- [ ] Import all new components
- [ ] Add HeroSection at top
- [ ] Add TestimonialsSection after hero
- [ ] Add BookingFlow (existing)
- [ ] Add FAQSection after booking
- [ ] Add Footer at bottom
- [ ] Add PublicBookingStatistics in hero or after testimonials
- [ ] Test layout on mobile and desktop
- [ ] Verify scroll behavior

**Acceptance Criteria:**
- All sections display in correct order
- Sections are properly spaced
- Mobile responsive
- Smooth scrolling between sections
- No layout shifts

---

## Phase 2: Payment Integration (1-2 days)

### 2.1 Enhance BookingForm with Payment Option
- [ ] Modify `salon/src/components/public/BookingForm.tsx`
- [ ] Add payment option selector (Pay Now vs Pay Later)
- [ ] Show payment methods if "Pay Now" selected
- [ ] Integrate PaymentProcessor component
- [ ] Update form submission to include payment_option
- [ ] Handle payment success/failure states
- [ ] Add loading state during payment
- [ ] Test with real payment data

**Acceptance Criteria:**
- Payment option toggle displays
- Payment methods show when "Pay Now" selected
- Form submission includes payment_option
- Payment processor displays correctly
- Loading state shows during payment

**Files to Modify:** `salon/src/components/public/BookingForm.tsx`  
**Reusable Component:** `PaymentProcessor.tsx` from POS system

---

### 2.2 Update BookingConfirmation to Show Payment Info
- [ ] Modify `salon/src/components/public/BookingConfirmation.tsx`
- [ ] Display payment status if payment was made
- [ ] Show payment receipt/transaction ID
- [ ] Add links to cancellation and rescheduling pages
- [ ] Add link to notification preferences
- [ ] Show booking management options
- [ ] Test with payment and non-payment bookings

**Acceptance Criteria:**
- Payment status displays if applicable
- Receipt/transaction ID shows
- Cancellation/rescheduling links work
- Notification preferences link works
- Mobile responsive

**Files to Modify:** `salon/src/components/public/BookingConfirmation.tsx`

---

### 2.3 Create Backend Endpoint for Payment Initialization
- [ ] Modify `backend/app/routes/public_booking.py`
- [ ] Update `create_public_booking` to handle payment_option
- [ ] If payment_option is "now", initialize payment with Paystack
- [ ] Return payment authorization URL in response
- [ ] Handle payment failures gracefully
- [ ] Log all payment attempts
- [ ] Test with real Paystack account

**Acceptance Criteria:**
- Payment initializes when payment_option is "now"
- Authorization URL returned in response
- Payment failures handled gracefully
- All payment attempts logged
- Works with real Paystack account

**Backend Support:** Already exists in `create_public_booking` function

---

### 2.4 Update Email Template with Payment Info
- [ ] Modify `backend/app/templates/booking_confirmation.html`
- [ ] Add payment status section if payment was made
- [ ] Include payment receipt/transaction ID
- [ ] Add payment method used
- [ ] Add refund policy information
- [ ] Test email rendering on mobile
- [ ] Test with payment and non-payment bookings

**Acceptance Criteria:**
- Payment info displays in email if applicable
- Receipt/transaction ID shows
- Email renders correctly on mobile
- Refund policy information included
- Professional appearance

---

## Phase 3: Booking Management (2 days)

### 3.1 Create Backend Endpoint for Cancellation
- [ ] Create `backend/app/routes/public_booking_management.py`
- [ ] Implement `POST /public/bookings/{id}/cancel` endpoint
- [ ] Validate cancellation is allowed (not within 2 hours)
- [ ] Update booking status to "cancelled"
- [ ] Process refund if payment was made
- [ ] Send cancellation email
- [ ] Invalidate availability cache
- [ ] Log cancellation with reason
- [ ] Test with various scenarios

**Acceptance Criteria:**
- Cancellation endpoint works
- Validation prevents cancellations too close to appointment
- Booking status updated to "cancelled"
- Refund processed if applicable
- Cancellation email sent
- Availability cache invalidated

**Files to Create:** `backend/app/routes/public_booking_management.py`  
**Reusable Service:** `PublicBookingService.cancel_public_booking()`

---

### 3.2 Create Backend Endpoint for Rescheduling
- [ ] Implement `POST /public/bookings/{id}/reschedule` endpoint
- [ ] Validate rescheduling is allowed (at least 24 hours before)
- [ ] Check availability for new date/time
- [ ] Update booking with new date/time
- [ ] Send rescheduling confirmation email
- [ ] Invalidate availability cache
- [ ] Log rescheduling with old and new times
- [ ] Test with various scenarios

**Acceptance Criteria:**
- Rescheduling endpoint works
- Validation prevents rescheduling too close to appointment
- Availability checked for new slot
- Booking updated with new date/time
- Confirmation email sent
- Availability cache invalidated

**Reusable Service:** `PublicBookingService.reschedule_public_booking()`

---

### 3.3 Create BookingStatusPage
- [ ] Create `salon/src/pages/public/BookingStatus.tsx`
- [ ] Fetch booking details from `/public/bookings/{id}`
- [ ] Display booking status, date, time, staff, service
- [ ] Show cancellation option if applicable
- [ ] Show rescheduling option if applicable
- [ ] Show review option if booking completed
- [ ] Add loading and error states
- [ ] Test on mobile and desktop

**Acceptance Criteria:**
- Booking details display correctly
- Status-specific actions show
- Cancellation works
- Rescheduling works
- Review option works
- Mobile responsive

**Files to Create:** `salon/src/pages/public/BookingStatus.tsx`

---

### 3.4 Create Cancellation Page
- [ ] Create `salon/src/pages/public/BookingCancellation.tsx`
- [ ] Display booking details
- [ ] Show cancellation reason input
- [ ] Confirm cancellation with warning
- [ ] Call cancellation endpoint
- [ ] Show success message
- [ ] Offer rescheduling option
- [ ] Test cancellation flow

**Acceptance Criteria:**
- Booking details display
- Cancellation reason collected
- Confirmation dialog shows
- Cancellation endpoint called
- Success message shows
- Rescheduling option offered

**Files to Create:** `salon/src/pages/public/BookingCancellation.tsx`

---

### 3.5 Create Rescheduling Page
- [ ] Create `salon/src/pages/public/BookingReschedule.tsx`
- [ ] Display current booking details
- [ ] Show date/time picker for new slot
- [ ] Check availability in real-time
- [ ] Call rescheduling endpoint
- [ ] Show success message
- [ ] Test rescheduling flow

**Acceptance Criteria:**
- Current booking details display
- Date/time picker works
- Availability checked in real-time
- Rescheduling endpoint called
- Success message shows
- Mobile responsive

**Files to Create:** `salon/src/pages/public/BookingReschedule.tsx`

---

## Phase 4: Notifications & Reminders (1 day)

### 4.1 Verify Booking Confirmation Email
- [ ] Check `backend/app/services/public_booking_service.py`
- [ ] Verify `send_booking_confirmation_email()` is called after booking
- [ ] Verify email template includes all required info
- [ ] Test email delivery
- [ ] Test email rendering on mobile
- [ ] Verify cancellation/rescheduling links in email

**Acceptance Criteria:**
- Confirmation email sent within 1 minute
- Email includes booking details
- Email includes cancellation/rescheduling links
- Email renders correctly on mobile
- Email is branded with salon colors

**Backend Support:** Already implemented

---

### 4.2 Create Celery Task for Reminder Emails
- [ ] Modify `backend/app/tasks/notifications.py`
- [ ] Create `send_booking_reminders()` task
- [ ] Find bookings 24 hours away (not yet reminded)
- [ ] Find bookings 1 hour away (not yet reminded)
- [ ] Send email reminders
- [ ] Update booking with reminder status
- [ ] Handle failures gracefully
- [ ] Test task execution

**Acceptance Criteria:**
- Task finds bookings correctly
- 24h reminders sent
- 1h reminders sent
- Booking status updated
- Failures handled gracefully
- Task runs on schedule

**Files to Modify:** `backend/app/tasks/notifications.py`

---

### 4.3 Create Notification Preferences Page
- [ ] Create `salon/src/pages/public/NotificationPreferences.tsx`
- [ ] Display toggle switches for each notification type
- [ ] Save preferences to backend
- [ ] Show success message after saving
- [ ] Test preference updates
- [ ] Test on mobile and desktop

**Acceptance Criteria:**
- Preference toggles display
- Preferences save to backend
- Success message shows
- Preferences persist on reload
- Mobile responsive

**Files to Create:** `salon/src/pages/public/NotificationPreferences.tsx`  
**Backend Endpoint Needed:** `POST /public/bookings/{id}/notification-preferences`

---

### 4.4 Create Backend Endpoint for Notification Preferences
- [ ] Create `POST /public/bookings/{id}/notification-preferences` endpoint
- [ ] Accept notification preference toggles
- [ ] Save preferences to database
- [ ] Return success response
- [ ] Validate booking exists
- [ ] Test endpoint

**Acceptance Criteria:**
- Endpoint accepts preference toggles
- Preferences saved to database
- Success response returned
- Booking validation works
- Preferences persist

**Files to Create:** New model `PublicBookingNotificationPreference`

---

## Phase 5: Enhanced Service & Staff Information (1 day)

### 5.1 Enhance ServiceSelector Component
- [ ] Modify `salon/src/components/public/ServiceSelector.tsx`
- [ ] Add service benefits/features display
- [ ] Improve service card layout
- [ ] Add hover effects and animations
- [ ] Improve mobile responsiveness
- [ ] Test with real service data

**Acceptance Criteria:**
- Service benefits display
- Card layout improved
- Hover effects work
- Mobile responsive
- Animations smooth

**Files to Modify:** `salon/src/components/public/ServiceSelector.tsx`

---

### 5.2 Enhance StaffSelector Component
- [ ] Modify `salon/src/components/public/StaffSelector.tsx`
- [ ] Add specialties display as tags
- [ ] Add rating display with star icons
- [ ] Improve staff card layout
- [ ] Add hover effects and animations
- [ ] Improve mobile responsiveness
- [ ] Test with real staff data

**Acceptance Criteria:**
- Specialties display as tags
- Rating displays with stars
- Card layout improved
- Hover effects work
- Mobile responsive

**Files to Modify:** `salon/src/components/public/StaffSelector.tsx`

---

### 5.3 Update Backend Schemas
- [ ] Update `PublicServiceResponse` schema to include benefits
- [ ] Update `PublicStaffResponse` schema to include specialties and rating
- [ ] Ensure Service model has benefits field
- [ ] Ensure Staff model has specialties and rating fields
- [ ] Test schema updates

**Acceptance Criteria:**
- Schemas include all required fields
- Service model has benefits
- Staff model has specialties and rating
- Endpoints return all fields

**Files to Modify:** `backend/app/schemas/public_booking.py`

---

## Testing & Verification

### 4.1 Unit Tests
- [ ] Test booking creation with payment_option
- [ ] Test cancellation logic
- [ ] Test rescheduling logic
- [ ] Test notification preference updates
- [ ] Test testimonial filtering
- [ ] Test statistics calculation

**Files to Create:** `backend/tests/unit/test_public_booking_enhancement.py`

---

### 4.2 Integration Tests
- [ ] Test full booking flow (service → staff → time → form → confirmation)
- [ ] Test payment flow (booking → payment → confirmation)
- [ ] Test cancellation flow (booking → cancellation → refund)
- [ ] Test reminder sending (Celery task)
- [ ] Test email delivery

**Files to Create:** `backend/tests/integration/test_public_booking_enhancement.py`

---

### 4.3 E2E Tests
- [ ] Test complete booking journey on desktop
- [ ] Test complete booking journey on mobile
- [ ] Test payment flow with Paystack
- [ ] Test email delivery
- [ ] Test cancellation flow
- [ ] Test rescheduling flow

**Files to Create:** `salon/src/pages/public/__tests__/PublicBookingApp.e2e.test.tsx`

---

### 4.4 Performance Tests
- [ ] Test page load time (target: < 2 seconds)
- [ ] Test booking creation response time (target: < 1 second)
- [ ] Test with 1000 concurrent users
- [ ] Optimize if needed

**Tools:** Lighthouse, WebPageTest, Load testing tool

---

## Deployment & Documentation

### 5.1 Database Migrations
- [ ] Create migration for PublicBookingNotificationPreference model
- [ ] Add fields to PublicBooking model (payment_option, payment_status, etc.)
- [ ] Create indexes for performance
- [ ] Test migrations on staging

**Files to Create:** `backend/migrations/add_public_booking_enhancements.py`

---

### 5.2 Documentation
- [ ] Update API documentation with new endpoints
- [ ] Create user guide for public booking page
- [ ] Document cancellation/rescheduling policies
- [ ] Document notification preferences
- [ ] Create troubleshooting guide

**Files to Create:** `PUBLIC_BOOKING_ENHANCEMENT_GUIDE.md`

---

### 5.3 Deployment Checklist
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

---

## Summary

**Total Tasks:** 25  
**Estimated Effort:** 5-6 days  
**Priority:** High  
**Expected Impact:** +20-30% conversion rate, +15-20% revenue, -30-40% no-shows

**Phase Breakdown:**
- Phase 1 (Branding & Trust): 5 tasks, 1 day
- Phase 2 (Payment): 4 tasks, 1-2 days
- Phase 3 (Booking Management): 5 tasks, 2 days
- Phase 4 (Notifications): 4 tasks, 1 day
- Phase 5 (Enhanced Info): 3 tasks, 1 day
- Testing & Deployment: 4 tasks, 1 day

