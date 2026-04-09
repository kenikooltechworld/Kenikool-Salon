# Implementation Plan: Staff Dashboard Enhancement

## Overview

This implementation plan breaks down the staff dashboard enhancement into discrete, incremental coding tasks organized by phase. Phase 1 focuses on core features (dashboard home, appointments, shifts, time off), while Phases 2-4 add medium-priority, nice-to-have, and extended features. Each task builds on previous work with no orphaned code.

---

## Phase 1: Core Features (High Priority)

### 1. Project Setup and Route Structure

- [x] 1.1 Create staff route structure and layout
  - Create `/staff` route group in `salon/src/pages/staff/`
  - Create `StaffLayout.tsx` component with navigation sidebar
  - Set up route protection middleware for `/staff/*` routes
  - Verify non-staff users are redirected to appropriate dashboard
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 9.2, 9.4_

- [x] 1.2 Create custom hooks for staff data fetching
  - Create `useMyAppointments.ts` hook with filtering and sorting
  - Create `useMyShifts.ts` hook with filtering and sorting
  - Create `useMyTimeOffRequests.ts` hook with filtering and sorting
  - Create `useMyEarnings.ts` hook (basic version for Phase 1)
  - Create `useStaffMetrics.ts` hook for dashboard metrics
  - Create `useActivityFeed.ts` hook for recent activity
  - Implement proper error handling and loading states in all hooks
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [x] 1.3 Write property tests for hook data isolation
  - **Property 1: Staff Data Isolation** - Verify staff can only see their own data
  - **Property 21: Hook State Handling** - Verify hooks properly handle loading, error, and success states
  - **Validates: Requirements 10.5, 10.6**

### 2. Dashboard Home Page

- [x] 2.1 Implement Staff Dashboard Home page
  - Create `salon/src/pages/staff/Dashboard.tsx` main page component
  - Create `MetricCard.tsx` component for displaying metric cards
  - Create `ActivityFeed.tsx` component for recent activity list
  - Fetch and display 4 metric cards (today's appointments, upcoming shifts, pending time off, earnings summary)
  - Display quick action buttons for common tasks
  - Display recent activity feed (last 10 events)
  - Implement auto-refresh every 5 minutes using `useStaffMetrics` and `useActivityFeed`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_

- [x] 2.2 Implement error handling and manual refresh for dashboard
  - Add error state display with retry button for failed metrics
  - Implement manual refresh button for each metric card
  - Display loading skeletons while metrics are fetching
  - Show user-friendly error messages for network failures
  - _Requirements: 1.10_

- [x] 2.3 Write property tests for dashboard metrics
  - **Property 5: Metric Refresh Consistency** - Verify metrics reflect current state within 2 seconds
  - **Property 15: Metric Card Display** - Verify all 4 metric cards display with valid data or appropriate states
  - **Property 16: Activity Feed Limit** - Verify activity feed shows exactly last 10 events
  - **Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.7, 1.8, 1.9**

- [x] 2.4 Checkpoint - Ensure dashboard home page works correctly
  - Verify all metric cards load and display data
  - Verify auto-refresh works every 5 minutes
  - Verify error handling displays appropriate messages
  - Verify quick action buttons navigate to correct pages
  - Ask the user if questions arise.

### 3. My Appointments Page

- [x] 3.1 Create appointment list and card components
  - Create `StaffAppointmentsList.tsx` component for list view
  - Create `StaffAppointmentCard.tsx` component for individual appointment display
  - Display appointment details (customer name, service, date, time, status)
  - Implement status filtering (scheduled, in-progress, completed, cancelled)
  - Implement default sort by date ascending
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.8_

- [x] 3.2 Implement My Appointments page with list and calendar views
  - Create `salon/src/pages/staff/Appointments.tsx` main page
  - Integrate list view using `StaffAppointmentsList.tsx`
  - Integrate calendar view using existing `BookingCalendar.tsx` component
  - Add view toggle between list and calendar
  - Implement status filter dropdown
  - Display appointment history (past appointments)
  - Show "no appointments" message when list is empty
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.7, 2.8, 2.9_

- [x] 3.3 Implement appointment detail view and mark as completed
  - Create appointment detail modal/page showing full details
  - Display customer contact details and service notes
  - Implement "Mark as Completed" button with confirmation
  - Update appointment status to completed via API
  - Show success message after status update
  - _Requirements: 2.5, 2.6_

- [x] 3.4 Write property tests for appointments
  - **Property 2: Appointment Status Transitions** - Verify marking as completed updates status persistently
  - **Property 9: Appointment Filtering by Status** - Verify filtered results only include selected status
  - **Property 17: Appointment Detail Completeness** - Verify all required information displays
  - **Validates: Requirements 2.4, 2.5, 2.6**

- [x] 3.5 Checkpoint - Ensure appointments page works correctly
  - Verify list view displays all staff appointments
  - Verify calendar view shows appointments by date
  - Verify status filtering works correctly
  - Verify mark as completed updates status
  - Ask the user if questions arise.

### 4. My Shifts Page

- [x] 4.1 Create shift list and card components
  - Create `StaffShiftsList.tsx` component for list view
  - Create `StaffShiftCard.tsx` component for individual shift display
  - Display shift information (start time, end time, date, status)
  - Implement default sort by date ascending
  - _Requirements: 3.1, 3.2, 3.3, 3.6_

- [x] 4.2 Implement My Shifts page with list and calendar views
  - Create `salon/src/pages/staff/Shifts.tsx` main page
  - Integrate list view using `StaffShiftsList.tsx`
  - Integrate calendar view using existing `BookingCalendar.tsx` component
  - Add view toggle between list and calendar
  - Display shift history (past shifts)
  - Show "no shifts" message when list is empty
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.8_

- [x] 4.3 Implement shift detail view
  - Create shift detail modal/page showing full details
  - Display all shift information (start time, end time, date, status)
  - _Requirements: 3.7_

- [x] 4.4 Write property tests for shifts
  - **Property 8: Shift Status Consistency** - Verify displayed status matches backend and transitions are atomic
  - **Property 10: Shift Sorting Order** - Verify shifts sorted by date ascending by default
  - **Property 18: Shift Detail Completeness** - Verify all required information displays
  - **Validates: Requirements 3.3, 3.6, 3.7**

- [x] 4.5 Checkpoint - Ensure shifts page works correctly
  - Verify list view displays all staff shifts
  - Verify calendar view shows shifts by date
  - Verify default sort by date ascending works
  - Verify shift history displays past shifts
  - Ask the user if questions arise.

### 5. Time Off Requests Page

- [x] 5.1 Create time off form and list components
  - Create `StaffTimeOffForm.tsx` component for submitting new requests
  - Create `StaffTimeOffList.tsx` component for displaying requests
  - Create `StaffTimeOffCard.tsx` component for individual request display
  - Implement form validation (start date < end date, future date)
  - Display request status (pending, approved, denied)
  - Display denial reason if applicable
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 5.2 Implement My Time Off Requests page
  - Create `salon/src/pages/staff/TimeOff.tsx` main page
  - Integrate form using `StaffTimeOffForm.tsx`
  - Integrate list using `StaffTimeOffList.tsx`
  - Display time off balance (remaining days)
  - Implement default sort by date descending
  - Show "no requests" message when list is empty
  - _Requirements: 4.1, 4.2, 4.3, 4.8, 4.9_

- [x] 5.3 Implement time off request submission
  - Handle form submission with validation
  - Create time off request via API
  - Display success message after creation
  - Display error message if submission fails
  - Refresh list after successful submission
  - _Requirements: 4.7, 4.10_

- [x] 5.4 Write property tests for time off requests
  - **Property 3: Time Off Request Validation** - Verify invalid date ranges are rejected
  - **Property 6: Time Off Balance Accuracy** - Verify balance equals allocated days minus approved requests
  - **Property 11: Time Off Request Sorting Order** - Verify requests sorted by date descending by default
  - **Validates: Requirements 4.5, 4.6, 4.8, 4.9**

- [x] 5.5 Checkpoint - Ensure time off page works correctly
  - Verify form validation works for invalid dates
  - Verify successful submission creates request
  - Verify list displays all requests with correct status
  - Verify time off balance displays correctly
  - Ask the user if questions arise.

### 6. Route Protection and Access Control

- [x] 6.1 Implement route protection for staff pages
  - Create route guard component for `/staff/*` routes
  - Verify staff role on route access
  - Redirect non-staff users to appropriate dashboard
  - Redirect invalid tokens to login page
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 6.2 Write property tests for route protection
  - **Property 12: Route Protection for Non-Staff Users** - Verify non-staff redirected from `/staff/*` routes
  - **Property 13: Staff Route Access** - Verify staff can access `/staff/*` routes
  - **Property 14: Invalid Token Redirect** - Verify invalid tokens redirect to login
  - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**

- [x] 6.3 Checkpoint - Ensure route protection works correctly
  - Verify staff users can access `/staff/*` routes
  - Verify non-staff users are redirected
  - Verify invalid tokens redirect to login
  - Ask the user if questions arise.

### 7. Phase 1 Integration and Final Testing

- [x] 7.1 Wire all Phase 1 components together
  - Ensure all pages are accessible from staff layout navigation
  - Verify quick action buttons on dashboard navigate correctly
  - Test navigation between all Phase 1 pages
  - Verify back buttons and breadcrumbs work correctly
  - _Requirements: 1.6, 9.2, 9.3, 9.4_

- [x] 7.2 Write integration tests for Phase 1 features
  - Test end-to-end flow: dashboard → appointments → appointment detail → mark complete
  - Test end-to-end flow: dashboard → shifts → shift detail
  - Test end-to-end flow: dashboard → time off → submit request → view in list
  - Test role-based access control for all Phase 1 pages
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 8.1_

- [x] 7.3 Final checkpoint - Ensure Phase 1 is complete and working
  - Verify all Phase 1 pages load and display data correctly
  - Verify all user interactions work as expected
  - Verify error handling displays appropriate messages
  - Verify role-based access control works correctly
  - Ask the user if questions arise.

---

## Phase 2: Medium Priority Features

### 8. My Earnings Page

- [x] 8.1 Create earnings components and hooks
  - Create `StaffEarningsChart.tsx` component for visual earnings data
  - Create `StaffEarningsBreakdown.tsx` component for breakdown display
  - Enhance `useMyEarnings.ts` hook with date range and service type filtering
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 8.2 Implement My Earnings page
  - Create `salon/src/pages/staff/Earnings.tsx` main page
  - Display total earnings for current period
  - Display earnings breakdown by service type
  - Display earnings breakdown by date range (daily, weekly, monthly)
  - Display payment history with transaction details
  - Implement date range filtering
  - Display commission rate information
  - Show "no earnings" message when no data exists
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

- [x] 8.3 Write property tests for earnings
  - **Property 4: Earnings Calculation Accuracy** - Verify total equals sum of individual commissions
  - **Validates: Requirements 5.2, 5.3, 5.4**

- [x] 8.4 Checkpoint - Ensure earnings page works correctly
  - Verify earnings data displays correctly
  - Verify date range filtering works
  - Verify breakdown calculations are accurate
  - Ask the user if questions arise.

### 9. Performance & Ratings Page

- [x] 9.1 Create performance components
  - Create `StaffPerformanceMetrics.tsx` component for metrics display
  - Create `StaffReviewsList.tsx` component for reviews list
  - Create `StaffReviewCard.tsx` component for individual review display
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 9.2 Implement Performance & Ratings page
  - Create `salon/src/pages/staff/Performance.tsx` main page
  - Display customer ratings and reviews
  - Display average rating score
  - Display individual customer reviews with ratings
  - Display performance metrics (appointments completed, customer satisfaction)
  - Implement default sort by date descending
  - Show "no ratings" message when no data exists
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 9.3 Write property tests for performance
  - **Validates: Requirements 6.2, 6.3, 6.4, 6.5**

- [x] 9.4 Checkpoint - Ensure performance page works correctly
  - Verify ratings and reviews display correctly
  - Verify average rating calculation is accurate
  - Verify performance metrics display correctly
  - Ask the user if questions arise.

---

## Phase 3: Nice to Have Features

### 10. Enhanced Staff Settings

- [x] 10.1 Create staff settings components
  - Create `StaffAvailabilityForm.tsx` component for working hours/days off
  - Create `StaffPreferencesForm.tsx` component for service specializations
  - Enhance existing `Settings.tsx` page with staff-specific forms
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 10.2 Implement Enhanced Staff Settings page
  - Create/enhance `salon/src/pages/staff/Settings.tsx` main page
  - Display staff-specific settings form
  - Allow updating availability preferences (working hours, days off)
  - Allow updating emergency contact information
  - Allow updating work preferences (service specializations, preferred customer types)
  - Implement input validation
  - Display success/error messages
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [x] 10.3 Write property tests for settings
  - **Property 19: Settings Update Persistence** - Verify updated settings persist and are retrieved correctly
  - **Property 20: Settings Validation** - Verify invalid input is rejected with error messages
  - **Validates: Requirements 7.2, 7.3, 7.4, 7.5, 7.6**

- [x] 10.4 Checkpoint - Ensure settings page works correctly
  - Verify settings form displays current values
  - Verify settings update works correctly
  - Verify validation errors display appropriately
  - Ask the user if questions arise.

---

## Phase 4: Extended Features (Optional)

### 11. Attendance & Check-in/Check-out

- [x] 11.1 Create attendance components
  - Create `StaffAttendanceTracker.tsx` component for clock in/out
  - Create `AttendanceHistory.tsx` component for history display
  - Create `useAttendance.ts` hook for attendance data
  - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [x] 11.2 Implement Attendance page
  - Create `salon/src/pages/staff/Attendance.tsx` main page
  - Display clock in/out button
  - Record check-in time and display current status
  - Record check-out time and calculate hours worked
  - Display attendance history with check-in/check-out times
  - Display late arrivals and early departures
  - Display total hours worked for current period
  - Handle errors with retry capability
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7_

- [x] 11.3 Write property tests for attendance
  - **Validates: Requirements 13.2, 13.3, 13.6**

### 12. Appointment Cancellation/Rescheduling

- [x] 12.1 Create cancellation/rescheduling components
  - Create `AppointmentCancellationModal.tsx` component
  - Create `AppointmentRescheduleModal.tsx` component
  - Enhance appointment detail view with cancel/reschedule options
  - _Requirements: 14.1, 14.2, 14.4_

- [x] 12.2 Implement appointment cancellation
  - Add cancel button to appointment detail view
  - Display cancellation reason form
  - Submit cancellation via API
  - Notify customer of cancellation
  - Maintain cancellation history
  - Display error messages on failure
  - _Requirements: 14.1, 14.2, 14.3, 14.6, 14.7_

- [x] 12.3 Implement appointment rescheduling
  - Add reschedule button to appointment detail view
  - Display available time slots
  - Allow selecting new time slot
  - Update appointment and notify customer
  - Maintain reschedule history
  - Display error messages on failure
  - _Requirements: 14.1, 14.4, 14.5, 14.6, 14.7_

- [x] 12.4 Write property tests for cancellation/rescheduling
  - **Validates: Requirements 14.2, 14.3, 14.5, 14.6**

### 13. Notifications & Reminders

- [x] 13.1 Create notification components
  - Create `NotificationCenter.tsx` component for displaying notifications
  - Create `NotificationPreferences.tsx` component for preferences
  - Create `useNotifications.ts` hook for notification data
  - _Requirements: 15.5, 15.6_

- [x] 13.2 Implement notification system
  - Display appointment reminders 24 hours before
  - Display shift reminders at start of shift
  - Display time off approval/denial notifications
  - Display commission payment notifications
  - Display notifications in staff dashboard
  - Allow customizing notification preferences
  - Support email and in-app notifications
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7_

- [x] 13.3 Write property tests for notifications
  - **Validates: Requirements 15.1, 15.2, 15.3, 15.4**

### 14. Documents & Certifications

- [x] 14.1 Create document components
  - Create `DocumentUploader.tsx` component for file upload
  - Create `DocumentList.tsx` component for document display
  - Create `useDocuments.ts` hook for document data
  - _Requirements: 16.1, 16.2_

- [x] 14.2 Implement Documents page
  - Create `salon/src/pages/staff/Documents.tsx` main page
  - Display list of uploaded documents
  - Allow uploading certification files (PDF, images)
  - Display document expiration dates
  - Display verification status (pending, verified, expired)
  - Send expiration reminders 30 days before
  - Allow downloading documents
  - Handle upload errors with messages
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7_

- [x] 14.3 Write property tests for documents
  - **Validates: Requirements 16.3, 16.4, 16.5**

### 15. Goals & Targets

- [x] 15.1 Create goals components
  - Create `GoalsDisplay.tsx` component for goals display
  - Create `TargetProgress.tsx` component for progress visualization
  - Create `useGoals.ts` hook for goals data
  - _Requirements: 17.1, 17.2, 17.3_

- [x] 15.2 Implement Goals page
  - Create `salon/src/pages/staff/Goals.tsx` main page
  - Display personal sales targets
  - Display commission targets
  - Display progress toward targets (percentage complete)
  - Display target achievement history
  - Display bonus/incentive information
  - Display performance metrics relative to targets
  - Handle errors with retry capability
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7_

- [x] 15.3 Write property tests for goals
  - **Validates: Requirements 17.3, 17.4, 17.6**

### 16. Team Communication

- [x] 16.1 Create messaging components
  - Create `MessagesList.tsx` component for messages display
  - Create `MessageDetail.tsx` component for individual message
  - Create `useMessages.ts` hook for message data
  - _Requirements: 18.1, 18.2_

- [x] 16.2 Implement Messages page
  - Create `salon/src/pages/staff/Messages.tsx` main page
  - Display messages from manager
  - Display team announcements
  - Display message timestamps and sender information
  - Allow marking messages as read/unread
  - Display unread message count in navigation
  - Implement message search functionality
  - Handle errors with retry capability
  - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7_

- [x] 16.3 Write property tests for messages
  - **Validates: Requirements 18.3, 18.4, 18.5**

### 17. Appointment Notes & Service Details

- [x] 17.1 Create appointment notes components
  - Create `AppointmentNotesSection.tsx` component for notes display
  - Create `NotesEditor.tsx` component for editing notes
  - Enhance appointment detail view with notes section
  - _Requirements: 19.1, 19.2_

- [x] 17.2 Implement appointment notes functionality
  - Display notes section in appointment detail
  - Allow adding private notes to appointments
  - Display customer service notes and special requests
  - Display follow-up notes from previous appointments
  - Allow editing notes before appointment completion
  - Display note history with timestamps
  - Handle save errors with retry capability
  - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7_

- [x] 17.3 Write property tests for appointment notes
  - **Validates: Requirements 19.2, 19.5, 19.6**

### 18. Commission Breakdown Details

- [x] 18.1 Create commission breakdown components
  - Create `CommissionBreakdownTable.tsx` component for detailed breakdown
  - Create `CommissionCalculationDetails.tsx` component for calculation display
  - Enhance earnings page with commission breakdown
  - _Requirements: 20.1, 20.2_

- [x] 18.2 Implement commission breakdown details
  - Display commission breakdown by appointment
  - Display service-wise commission rates
  - Display commission amount per appointment
  - Display bonus and incentive details
  - Display deductions with reasons
  - Allow filtering by date range and service type
  - Display total commission calculation with breakdown
  - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7_

- [x] 18.3 Write property tests for commission breakdown
  - **Property 4: Earnings Calculation Accuracy** - Verify total equals sum of individual commissions
  - **Validates: Requirements 20.3, 20.4, 20.7**

### 19. Customer Feedback & Reviews

- [x] 19.1 Create feedback components
  - Create `FeedbackList.tsx` component for feedback display
  - Create `FeedbackDetail.tsx` component for individual feedback
  - Create `FeedbackResponse.tsx` component for responding to feedback
  - Create `useFeedback.ts` hook for feedback data
  - _Requirements: 21.1, 21.2_

- [x] 19.2 Implement Feedback page
  - Create `salon/src/pages/staff/Feedback.tsx` main page
  - Display individual customer feedback
  - Display customer ratings and comments
  - Display feedback response capability
  - Display feedback history and trends
  - Display average satisfaction score
  - Allow filtering by date range and rating
  - Handle errors with retry capability
  - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7_

- [x] 19.3 Write property tests for feedback
  - **Validates: Requirements 21.2, 21.4, 21.5**

---

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Phase 1 is the main deliverable; Phases 2-4 are enhancements
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- All code should follow existing patterns in the codebase
- Reuse existing UI components (Button, Badge, Card, Spinner, ConfirmationModal)
- Use existing icons from `@/components/icons`
- Maintain responsive design for mobile devices
- Implement proper error handling and user feedback for all features
