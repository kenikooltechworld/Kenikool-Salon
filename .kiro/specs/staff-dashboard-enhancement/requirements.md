# Staff Dashboard Enhancement Requirements

## Introduction

The Staff Dashboard Enhancement feature provides comprehensive staff-facing pages and functionalities to replace the current basic placeholder. This feature enables staff members to manage their appointments, shifts, time off requests, and earnings through dedicated, role-isolated pages. The implementation maintains complete separation of concerns between staff and owner/manager interfaces, with no conditional rendering based on roles in owner settings pages.

## Glossary

- **Staff**: A user with the staff role who provides services
- **Staff_Dashboard**: The primary interface for staff members to view and manage their work-related information
- **Appointment**: A scheduled service session between a staff member and a customer
- **Shift**: A scheduled work period assigned to a staff member
- **Time_Off_Request**: A request submitted by staff to take time away from work
- **Earnings**: Commission or payment earned by staff from completed appointments and services
- **Metrics**: Key performance indicators displayed on the dashboard (appointments, shifts, time off, earnings)
- **Activity_Feed**: A chronological list of recent events related to staff work
- **Status**: The current state of an appointment, shift, or time off request (scheduled, in-progress, completed, pending, approved, denied)
- **Commission**: Payment earned by staff for services rendered
- **Availability**: The time periods when a staff member is available to work
- **Customer_Rating**: A numerical or textual evaluation provided by a customer for a completed appointment

## Requirements

### Phase 1: Core Features (High Priority)

### Requirement 1: Staff Dashboard Home Page

**User Story:** As a staff member, I want to view my dashboard home page, so that I can quickly see my key metrics and recent activity.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/dashboard`, THE Staff_Dashboard SHALL display the staff home page (not the owner dashboard)
2. THE Staff_Dashboard SHALL display today's appointment count as a metric card
3. THE Staff_Dashboard SHALL display upcoming shifts count as a metric card
4. THE Staff_Dashboard SHALL display pending time off requests count as a metric card
5. THE Staff_Dashboard SHALL display earnings summary as a metric card
6. THE Staff_Dashboard SHALL include quick action buttons for common tasks (view appointments, request time off, view earnings)
7. THE Staff_Dashboard SHALL display a recent activity feed showing the last 10 events
8. WHEN the page loads, THE Staff_Dashboard SHALL fetch and display all metrics within 2 seconds
9. THE Staff_Dashboard SHALL refresh metrics every 5 minutes automatically
10. IF a metric fails to load, THE Staff_Dashboard SHALL display an error message and allow manual refresh

---

### Requirement 2: My Appointments Page

**User Story:** As a staff member, I want to view and manage my appointments, so that I can track my schedule and mark appointments as completed.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/appointments`, THE Appointments_Page SHALL display only appointments assigned to that staff member
2. THE Appointments_Page SHALL display appointments in a list view with appointment details (customer name, service, date, time, status)
3. THE Appointments_Page SHALL provide a calendar view option to visualize appointments by date
4. THE Appointments_Page SHALL filter appointments by status (scheduled, in-progress, completed, cancelled)
5. WHEN a staff member clicks on an appointment, THE Appointments_Page SHALL display detailed appointment information including customer contact details and service notes
6. WHEN a staff member marks an appointment as completed, THE Appointments_Page SHALL update the appointment status to completed
7. THE Appointments_Page SHALL display appointment history (past appointments)
8. THE Appointments_Page SHALL sort appointments by date in ascending order by default
9. IF no appointments exist, THE Appointments_Page SHALL display a message indicating no appointments are scheduled

---

### Requirement 3: My Shifts Page

**User Story:** As a staff member, I want to view my assigned shifts, so that I can manage my work schedule.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/shifts`, THE Shifts_Page SHALL display only shifts assigned to that staff member
2. THE Shifts_Page SHALL display shift information including start time, end time, date, and status
3. THE Shifts_Page SHALL display shift status (scheduled, in-progress, completed)
4. THE Shifts_Page SHALL provide a calendar view to visualize shifts by date
5. THE Shifts_Page SHALL display shift history (past shifts)
6. THE Shifts_Page SHALL sort shifts by date in ascending order by default
7. WHEN a staff member clicks on a shift, THE Shifts_Page SHALL display detailed shift information
8. IF no shifts are assigned, THE Shifts_Page SHALL display a message indicating no shifts are scheduled

---

### Requirement 4: Time Off Requests Page

**User Story:** As a staff member, I want to submit and manage time off requests, so that I can request time away from work and track request status.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/time-off`, THE TimeOff_Page SHALL display a form to submit new time off requests
2. THE TimeOff_Page SHALL display all time off requests submitted by that staff member
3. THE TimeOff_Page SHALL display request status (pending, approved, denied)
4. THE TimeOff_Page SHALL display the reason for denial if a request is denied
5. WHEN a staff member submits a time off request, THE TimeOff_Page SHALL validate that the start date is before the end date
6. WHEN a staff member submits a time off request, THE TimeOff_Page SHALL validate that the request is for a future date
7. WHEN a staff member submits a time off request, THE TimeOff_Page SHALL create the request and display a success message
8. THE TimeOff_Page SHALL display the staff member's time off balance (remaining days)
9. THE TimeOff_Page SHALL sort requests by date in descending order by default
10. IF a request submission fails, THE TimeOff_Page SHALL display an error message with details

---

### Phase 2: Medium Priority Features

### Requirement 5: My Earnings Page

**User Story:** As a staff member, I want to view my earnings and commission details, so that I can track my income.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/earnings`, THE Earnings_Page SHALL display personal commission and earnings dashboard
2. THE Earnings_Page SHALL display total earnings for the current period
3. THE Earnings_Page SHALL display earnings breakdown by service type
4. THE Earnings_Page SHALL display earnings breakdown by date range (daily, weekly, monthly)
5. THE Earnings_Page SHALL display payment history with transaction details
6. THE Earnings_Page SHALL allow filtering by date range
7. THE Earnings_Page SHALL display commission rate information
8. IF no earnings data exists, THE Earnings_Page SHALL display a message indicating no earnings recorded

---

### Requirement 6: Performance & Ratings View

**User Story:** As a staff member, I want to view my customer ratings and performance metrics, so that I can track my performance.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/performance`, THE Performance_Page SHALL display customer ratings and reviews
2. THE Performance_Page SHALL display average rating score
3. THE Performance_Page SHALL display individual customer reviews with ratings
4. THE Performance_Page SHALL display performance metrics (appointments completed, customer satisfaction)
5. THE Performance_Page SHALL sort reviews by date in descending order by default
6. IF no ratings exist, THE Performance_Page SHALL display a message indicating no ratings recorded

---

### Phase 3: Nice to Have Features

### Requirement 7: Enhanced Staff Settings

**User Story:** As a staff member, I want to manage my availability preferences and work settings, so that I can customize my work experience.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/settings`, THE Settings_Page SHALL display staff-specific settings form
2. THE Settings_Page SHALL allow updating availability preferences (working hours, days off)
3. THE Settings_Page SHALL allow updating emergency contact information
4. THE Settings_Page SHALL allow updating work preferences (service specializations, preferred customer types)
5. WHEN a staff member updates settings, THE Settings_Page SHALL validate all input fields
6. WHEN a staff member updates settings, THE Settings_Page SHALL save changes and display a success message
7. IF settings update fails, THE Settings_Page SHALL display an error message with details

---

### Phase 4: Extended Nice to Have Features

### Requirement 13: Attendance & Check-in/Check-out

**User Story:** As a staff member, I want to clock in and out to track my work hours, so that I can maintain accurate attendance records.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/attendance`, THE Attendance_Page SHALL display a clock in/out button
2. WHEN a staff member clicks clock in, THE Attendance_Page SHALL record the check-in time and display current status
3. WHEN a staff member clicks clock out, THE Attendance_Page SHALL record the check-out time and calculate hours worked
4. THE Attendance_Page SHALL display attendance history with check-in/check-out times
5. THE Attendance_Page SHALL display late arrivals and early departures
6. THE Attendance_Page SHALL display total hours worked for the current period
7. IF clock in/out fails, THE Attendance_Page SHALL display an error message and allow retry

---

### Requirement 14: Appointment Cancellation/Rescheduling

**User Story:** As a staff member, I want to cancel or reschedule my appointments, so that I can manage unexpected changes.

#### Acceptance Criteria

1. WHEN a staff member views an appointment, THE Appointment_Detail SHALL display cancel and reschedule options
2. WHEN a staff member cancels an appointment, THE System SHALL require a cancellation reason
3. WHEN a staff member cancels an appointment, THE System SHALL notify the customer
4. WHEN a staff member reschedules an appointment, THE System SHALL show available time slots
5. WHEN a staff member reschedules an appointment, THE System SHALL update the appointment and notify the customer
6. THE System SHALL maintain cancellation and reschedule history
7. IF cancellation/reschedule fails, THE System SHALL display an error message with details

---

### Requirement 15: Notifications & Reminders

**User Story:** As a staff member, I want to receive notifications about appointments, shifts, and approvals, so that I stay informed.

#### Acceptance Criteria

1. THE System SHALL send appointment reminders 24 hours before scheduled appointments
2. THE System SHALL send shift reminders at the start of each shift
3. THE System SHALL send time off approval/denial notifications
4. THE System SHALL send commission payment notifications
5. THE System SHALL display notifications in the staff dashboard
6. THE System SHALL allow staff to customize notification preferences
7. THE System SHALL support email and in-app notifications

---

### Requirement 16: Documents & Certifications

**User Story:** As a staff member, I want to upload and manage my professional certifications, so that I can keep my credentials current.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/documents`, THE Documents_Page SHALL display a list of uploaded documents
2. THE Documents_Page SHALL allow uploading certification files (PDF, images)
3. THE Documents_Page SHALL display document expiration dates
4. THE Documents_Page SHALL display document verification status (pending, verified, expired)
5. THE System SHALL send expiration reminders 30 days before document expiration
6. THE Documents_Page SHALL allow downloading uploaded documents
7. IF document upload fails, THE Documents_Page SHALL display an error message with details

---

### Requirement 17: Goals & Targets

**User Story:** As a staff member, I want to view my personal sales and commission targets, so that I can track my progress.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/goals`, THE Goals_Page SHALL display personal sales targets
2. THE Goals_Page SHALL display commission targets
3. THE Goals_Page SHALL display progress toward targets (percentage complete)
4. THE Goals_Page SHALL display target achievement history
5. THE Goals_Page SHALL display bonus/incentive information
6. THE Goals_Page SHALL display performance metrics relative to targets
7. IF goals data fails to load, THE Goals_Page SHALL display an error message and allow manual refresh

---

### Requirement 18: Team Communication

**User Story:** As a staff member, I want to receive messages and announcements from my manager, so that I stay informed about team updates.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/messages`, THE Messages_Page SHALL display messages from manager
2. THE Messages_Page SHALL display team announcements
3. THE Messages_Page SHALL display message timestamps and sender information
4. THE Messages_Page SHALL allow marking messages as read/unread
5. THE Messages_Page SHALL display unread message count in navigation
6. THE Messages_Page SHALL support message search functionality
7. IF messages fail to load, THE Messages_Page SHALL display an error message and allow manual refresh

---

### Requirement 19: Appointment Notes & Service Details

**User Story:** As a staff member, I want to add and view notes for appointments, so that I can track service details and customer requests.

#### Acceptance Criteria

1. WHEN a staff member views an appointment, THE Appointment_Detail SHALL display a notes section
2. THE Appointment_Detail SHALL allow adding private notes to appointments
3. THE Appointment_Detail SHALL display customer service notes and special requests
4. THE Appointment_Detail SHALL display follow-up notes from previous appointments
5. THE Appointment_Detail SHALL allow editing notes before appointment completion
6. THE Appointment_Detail SHALL display note history with timestamps
7. IF note save fails, THE Appointment_Detail SHALL display an error message and allow retry

---

### Requirement 20: Commission Breakdown Details

**User Story:** As a staff member, I want to see detailed commission breakdown per appointment, so that I can understand my earnings better.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/earnings`, THE Earnings_Page SHALL display commission breakdown by appointment
2. THE Earnings_Page SHALL display service-wise commission rates
3. THE Earnings_Page SHALL display commission amount per appointment
4. THE Earnings_Page SHALL display bonus and incentive details
5. THE Earnings_Page SHALL display deductions (if any) with reasons
6. THE Earnings_Page SHALL allow filtering by date range and service type
7. THE Earnings_Page SHALL display total commission calculation with breakdown

---

### Requirement 21: Customer Feedback & Reviews

**User Story:** As a staff member, I want to view customer feedback and reviews, so that I can understand customer satisfaction.

#### Acceptance Criteria

1. WHEN a staff member navigates to `/staff/feedback`, THE Feedback_Page SHALL display individual customer feedback
2. THE Feedback_Page SHALL display customer ratings and comments
3. THE Feedback_Page SHALL display feedback response capability
4. THE Feedback_Page SHALL display feedback history and trends
5. THE Feedback_Page SHALL display average satisfaction score
6. THE Feedback_Page SHALL allow filtering by date range and rating
7. IF feedback data fails to load, THE Feedback_Page SHALL display an error message and allow manual refresh

---

### Requirement 8: Role-Based Route Protection

**User Story:** As a system, I want to ensure staff pages are only accessible to staff members, so that I maintain security and proper access control.

#### Acceptance Criteria

1. WHEN a non-staff user attempts to access `/staff/*` routes, THE Router SHALL redirect to the appropriate dashboard for their role
2. WHEN a staff member accesses `/staff/*` routes, THE Router SHALL allow access and display the staff page
3. THE Router SHALL verify staff role on every protected route access
4. IF authentication token is invalid, THE Router SHALL redirect to login page

---

### Requirement 9: Complete Separation of Staff and Owner Interfaces

**User Story:** As a system, I want to maintain complete separation between staff and owner interfaces, so that there is no role-based conditional rendering in owner pages.

#### Acceptance Criteria

1. THE Owner_Settings_Page SHALL NOT contain any conditional rendering based on staff role
2. THE Staff_Pages SHALL be isolated in `/staff/*` routes
3. THE Staff_Components SHALL be located in `salon/src/components/staff/` directory
4. THE Staff_Pages SHALL be located in `salon/src/pages/staff/` directory
5. WHEN an owner accesses settings, THE Owner_Settings_Page SHALL display only owner-relevant options
6. WHEN a staff member accesses settings, THE Staff_Settings_Page SHALL display only staff-relevant options

---

### Requirement 10: Data Fetching and State Management

**User Story:** As a developer, I want to use consistent hook patterns for staff data, so that the codebase maintains consistency.

#### Acceptance Criteria

1. THE Staff_Hooks SHALL follow existing hook patterns (useAppointments, useShifts, useTimeOffRequests)
2. THE Staff_Hooks SHALL include useMyAppointments hook for fetching staff's own appointments
3. THE Staff_Hooks SHALL include useMyShifts hook for fetching staff's own shifts
4. THE Staff_Hooks SHALL include useMyEarnings hook for fetching staff's own earnings
5. THE Staff_Hooks SHALL handle loading, error, and success states
6. THE Staff_Hooks SHALL implement proper error handling and user feedback

---

### Requirement 11: UI Component Consistency

**User Story:** As a developer, I want to reuse existing UI components, so that the staff dashboard maintains visual consistency.

#### Acceptance Criteria

1. THE Staff_Components SHALL use existing Button, Badge, Card, Spinner, ConfirmationModal components
2. THE Staff_Components SHALL use existing icons from `@/components/icons`
3. THE Staff_Components SHALL follow existing styling patterns from the codebase
4. THE Staff_Components SHALL be responsive and work on mobile devices
5. THE Staff_Components SHALL maintain accessibility standards

---

### Requirement 12: Backend Integration

**User Story:** As a developer, I want to use existing backend models and routes, so that I minimize backend changes.

#### Acceptance Criteria

1. THE Backend_Integration SHALL use existing Shift model and routes
2. THE Backend_Integration SHALL use existing TimeOffRequest model and routes
3. THE Backend_Integration SHALL use existing StaffCommission model and routes
4. THE Backend_Integration SHALL use existing Staff_Settings model and routes
5. THE Backend_Integration SHALL add new routes only if existing routes don't support required functionality
6. WHEN fetching staff-specific data, THE Backend_Integration SHALL filter by staff_id

---

## Acceptance Criteria Patterns

### Correctness Properties

1. **Invariants**: Staff can only view their own data (appointments, shifts, earnings, time off requests)
2. **Round-Trip Properties**: Time off request submission → retrieval → display shows consistent data
3. **Idempotence**: Marking an appointment as completed multiple times results in the same state
4. **Metamorphic Properties**: Earnings total equals sum of individual service earnings
5. **Error Conditions**: Invalid date ranges, missing required fields, and network errors are properly handled

