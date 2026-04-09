# Staff Dashboard Enhancement - Design Document

## Overview

The Staff Dashboard Enhancement provides a comprehensive, role-isolated interface for staff members to manage their work-related activities. This feature replaces the basic placeholder with dedicated pages for appointments, shifts, time off requests, earnings, performance metrics, and settings. The design maintains complete separation between staff and owner interfaces, with no conditional rendering based on roles in shared pages.

### Key Design Principles

1. **Role Isolation**: Staff pages are completely separate from owner/manager pages
2. **Consistency**: Reuse existing UI components and patterns from the codebase
3. **Data Privacy**: Staff can only view their own data (appointments, shifts, earnings, etc.)
4. **Progressive Enhancement**: Phase 1 covers core features; later phases add advanced functionality
5. **Performance**: Metrics load within 2 seconds; auto-refresh every 5 minutes

---

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Staff Dashboard                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Navigation & Layout (DashboardLayout)               │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│         ┌────────────────┼────────────────┐                │
│         │                │                │                │
│    ┌────▼────┐    ┌─────▼──────┐   ┌────▼────┐           │
│    │  Home   │    │ Appointments│   │ Shifts  │           │
│    │ Page    │    │   Page      │   │  Page   │           │
│    └────┬────┘    └─────┬──────┘   └────┬────┘           │
│         │                │                │                │
│    ┌────▼────┐    ┌─────▼──────┐   ┌────▼────┐           │
│    │ Time Off │    │ Earnings   │   │Settings │           │
│    │ Page     │    │ Page       │   │ Page    │           │
│    └─────────┘    └────────────┘   └────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │                    │                    │
    ┌────▼────────────────────▼────────────────────▼────┐
    │         Custom Hooks (useMyAppointments, etc)     │
    └────┬────────────────────┬────────────────────┬────┘
         │                    │                    │
    ┌────▼────────────────────▼────────────────────▼────┐
    │              API Client Layer                     │
    └────┬────────────────────┬────────────────────┬────┘
         │                    │                    │
    ┌────▼────────────────────▼────────────────────▼────┐
    │         Backend API Routes (staff-specific)       │
    └────┬────────────────────┬────────────────────┬────┘
         │                    │                    │
    ┌────▼────────────────────▼────────────────────▼────┐
    │    Database (Appointments, Shifts, TimeOff, etc)  │
    └─────────────────────────────────────────────────────┘
```

### Frontend Architecture

**Route Structure**:
```
/staff/
  ├── dashboard          (Home page with metrics)
  ├── appointments       (My Appointments)
  ├── shifts            (My Shifts)
  ├── time-off          (Time Off Requests)
  ├── earnings          (My Earnings - Phase 2)
  ├── performance       (Performance & Ratings - Phase 2)
  ├── settings          (Enhanced Settings - Phase 3)
  ├── attendance        (Attendance - Phase 4)
  ├── documents         (Documents - Phase 4)
  ├── goals             (Goals - Phase 4)
  ├── messages          (Messages - Phase 4)
  └── feedback          (Feedback - Phase 4)
```

**Component Structure**:
```
salon/src/components/staff/
├── StaffDashboardHome.tsx
├── StaffAppointmentsList.tsx
├── StaffAppointmentCard.tsx
├── StaffShiftsList.tsx
├── StaffShiftCard.tsx
├── StaffTimeOffForm.tsx
├── StaffTimeOffList.tsx
├── StaffTimeOffCard.tsx
├── StaffEarningsChart.tsx
├── StaffEarningsBreakdown.tsx
├── StaffPerformanceMetrics.tsx
├── StaffSettingsForm.tsx
├── MetricCard.tsx
├── ActivityFeed.tsx
└── [Additional components for Phase 2-4]

salon/src/pages/staff/
├── Dashboard.tsx
├── Appointments.tsx
├── Shifts.tsx
├── TimeOff.tsx
├── Earnings.tsx
├── Performance.tsx
├── Settings.tsx
├── Attendance.tsx
├── Documents.tsx
├── Goals.tsx
├── Messages.tsx
└── Feedback.tsx
```

---

## Components and Interfaces

### Phase 1: Core Components

#### 1. Staff Dashboard Home Page (`/staff/dashboard`)

**Purpose**: Display key metrics and recent activity for quick overview

**Components**:
- `StaffDashboardHome.tsx` - Main container
- `MetricCard.tsx` - Reusable metric display card
- `ActivityFeed.tsx` - Recent activity list

**Data Flow**:
```
StaffDashboardHome
├── useMyAppointments() → Today's count
├── useMyShifts() → Upcoming count
├── useMyTimeOffRequests() → Pending count
├── useMyEarnings() → Summary
└── useActivityFeed() → Recent events
```

**Key Features**:
- 4 metric cards (today's appointments, upcoming shifts, pending time off, earnings)
- Quick action buttons
- Recent activity feed (last 10 events)
- Auto-refresh every 5 minutes
- Error handling with manual refresh

#### 2. My Appointments Page (`/staff/appointments`)

**Purpose**: View and manage staff's own appointments

**Components**:
- `Appointments.tsx` - Main page
- `StaffAppointmentsList.tsx` - List view
- `StaffAppointmentCard.tsx` - Card view
- Reuse `BookingCalendar.tsx` for calendar view

**Features**:
- List view with appointment details
- Calendar view
- Status filtering (scheduled, in-progress, completed, cancelled)
- Mark as completed action
- Appointment history
- Default sort by date ascending

#### 3. My Shifts Page (`/staff/shifts`)

**Purpose**: View assigned shifts and work schedule

**Components**:
- `Shifts.tsx` - Main page
- `StaffShiftsList.tsx` - List view
- `StaffShiftCard.tsx` - Card view

**Features**:
- Display shift details (start time, end time, date, status)
- Calendar view
- Shift history
- Default sort by date ascending

#### 4. Time Off Requests Page (`/staff/time-off`)

**Purpose**: Submit and manage time off requests

**Components**:
- `TimeOff.tsx` - Main page
- `StaffTimeOffForm.tsx` - Form for new requests
- `StaffTimeOffList.tsx` - List of requests
- `StaffTimeOffCard.tsx` - Individual request card

**Features**:
- Form to submit new requests
- Validation (start date < end date, future date)
- Display all requests with status
- Show denial reasons
- Display time off balance
- Default sort by date descending

### Phase 2: Medium Priority Components

#### 5. My Earnings Page (`/staff/earnings`)

**Purpose**: Track income and commission details

**Components**:
- `Earnings.tsx` - Main page
- `StaffEarningsChart.tsx` - Visual earnings data
- `StaffEarningsBreakdown.tsx` - Breakdown by service/date

**Features**:
- Total earnings for current period
- Breakdown by service type
- Breakdown by date range (daily, weekly, monthly)
- Payment history
- Date range filtering
- Commission rate information

#### 6. Performance & Ratings Page (`/staff/performance`)

**Purpose**: View customer ratings and performance metrics

**Components**:
- `Performance.tsx` - Main page
- `StaffPerformanceMetrics.tsx` - Metrics display
- `StaffReviewsList.tsx` - Reviews list

**Features**:
- Average rating score
- Individual customer reviews
- Performance metrics (appointments completed, satisfaction)
- Sort reviews by date descending

### Phase 3: Enhanced Settings

#### 7. Enhanced Staff Settings (`/staff/settings`)

**Purpose**: Manage availability and work preferences

**Components**:
- `Settings.tsx` - Main page (already exists)
- `StaffAvailabilityForm.tsx` - Working hours/days off
- `StaffPreferencesForm.tsx` - Service specializations

**Features**:
- Update availability preferences
- Update emergency contact
- Update work preferences
- Input validation
- Success/error messages

---

## Data Models

### Frontend Data Structures

```typescript
// Appointment (staff view)
interface StaffAppointment {
  id: string;
  customerId: string;
  customerName: string;
  customerPhone: string;
  customerEmail: string;
  serviceId: string;
  serviceName: string;
  startTime: string;
  endTime: string;
  status: "scheduled" | "confirmed" | "in_progress" | "completed" | "cancelled";
  notes: string;
  price: number;
  createdAt: string;
}

// Shift (staff view)
interface StaffShift {
  id: string;
  startTime: string;
  endTime: string;
  status: "scheduled" | "in_progress" | "completed" | "cancelled";
  laborCost: number;
  createdAt: string;
}

// Time Off Request
interface TimeOffRequest {
  id: string;
  startDate: string;
  endDate: string;
  reason: string;
  status: "pending" | "approved" | "denied";
  denialReason?: string;
  createdAt: string;
}

// Commission/Earnings
interface Commission {
  id: string;
  staffId: string;
  transactionId: string;
  commissionAmount: number;
  commissionRate: number;
  commissionType: "percentage" | "fixed";
  calculatedAt: string;
}

// Activity Feed Event
interface ActivityEvent {
  id: string;
  type: "appointment" | "shift" | "timeoff" | "earnings" | "review";
  title: string;
  description: string;
  timestamp: string;
  metadata: Record<string, any>;
}

// Staff Settings
interface StaffSettings {
  id: string;
  staffId: string;
  workingHoursStart: string;
  workingHoursEnd: string;
  daysOff: string[];
  emergencyContact: string;
  emergencyPhone: string;
  specializations: string[];
  preferredCustomerTypes: string[];
  notificationPreferences: {
    emailNotifications: boolean;
    inAppNotifications: boolean;
    appointmentReminders: boolean;
    shiftReminders: boolean;
  };
}
```

### Backend Data Models (Existing)

**Appointment Model**:
- `customer_id`, `staff_id`, `service_id`
- `start_time`, `end_time`
- `status` (scheduled, confirmed, in_progress, completed, cancelled, no_show)
- `notes`, `price`, `payment_id`
- `created_at`, `updated_at`

**Shift Model**:
- `staff_id`
- `start_time`, `end_time`
- `status` (scheduled, in_progress, completed, cancelled)
- `labor_cost`
- `created_at`, `updated_at`

**TimeOffRequest Model**:
- `staff_id`
- `start_date`, `end_date`
- `reason`
- `status` (pending, approved, denied)
- `created_at`, `updated_at`

**Staff Model**:
- `user_id`
- `specialties`, `certifications`
- `payment_type`, `payment_rate`
- `hire_date`, `bio`, `profile_image_url`
- `status` (active, inactive, on_leave, terminated)
- `rating`, `review_count`

**StaffCommission Model**:
- `staff_id`
- `transaction_id`
- `commission_amount`, `commission_rate`
- `commission_type` (percentage, fixed)
- `calculated_at`

---

## API Endpoints

### Existing Endpoints (Reuse)

**Appointments**:
- `GET /appointments?staff_id={id}` - Get staff's appointments
- `GET /appointments/{id}` - Get appointment details
- `PUT /appointments/{id}` - Update appointment
- `PUT /appointments/{id}/complete` - Mark as completed
- `PUT /appointments/{id}/cancel` - Cancel appointment

**Shifts**:
- `GET /shifts?staff_id={id}` - Get staff's shifts
- `GET /shifts/{id}` - Get shift details
- `PUT /shifts/{id}` - Update shift

**Time Off Requests**:
- `GET /time-off-requests?staff_id={id}` - Get staff's requests
- `POST /time-off-requests` - Create new request
- `GET /time-off-requests/{id}` - Get request details

**Commissions**:
- `GET /commissions/staff/{id}` - Get staff's commissions
- `GET /commissions/payouts` - Get payout history

**Staff Settings**:
- `GET /staff-settings/{staff_id}` - Get settings
- `PUT /staff-settings/{staff_id}` - Update settings

### New Endpoints (If Needed)

**Activity Feed**:
- `GET /staff/{id}/activity-feed?limit=10` - Get recent activity

**Staff Dashboard Metrics**:
- `GET /staff/{id}/metrics` - Get dashboard metrics (appointments today, upcoming shifts, pending time off, earnings summary)

---

## State Management

### Hook Patterns

**Custom Hooks for Staff Data**:

```typescript
// useMyAppointments.ts
export function useMyAppointments(filters?: {
  status?: string;
  dateRange?: { start: string; end: string };
}) {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["my-appointments", filters],
    queryFn: () => apiClient.get(`/appointments?staff_id=${user.id}`, { params: filters }),
    enabled: !!user?.id,
  });
}

// useMyShifts.ts
export function useMyShifts(filters?: {
  status?: string;
  dateRange?: { start: string; end: string };
}) {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["my-shifts", filters],
    queryFn: () => apiClient.get(`/shifts?staff_id=${user.id}`, { params: filters }),
    enabled: !!user?.id,
  });
}

// useMyTimeOffRequests.ts
export function useMyTimeOffRequests(filters?: {
  status?: string;
}) {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["my-time-off-requests", filters],
    queryFn: () => apiClient.get(`/time-off-requests?staff_id=${user.id}`, { params: filters }),
    enabled: !!user?.id,
  });
}

// useMyEarnings.ts
export function useMyEarnings(filters?: {
  dateRange?: { start: string; end: string };
  serviceType?: string;
}) {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["my-earnings", filters],
    queryFn: () => apiClient.get(`/commissions/staff/${user.id}`, { params: filters }),
    enabled: !!user?.id,
  });
}

// useStaffMetrics.ts
export function useStaffMetrics() {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["staff-metrics"],
    queryFn: () => apiClient.get(`/staff/${user.id}/metrics`),
    enabled: !!user?.id,
    refetchInterval: 5 * 60 * 1000, // 5 minutes
  });
}

// useActivityFeed.ts
export function useActivityFeed(limit = 10) {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["activity-feed", limit],
    queryFn: () => apiClient.get(`/staff/${user.id}/activity-feed?limit=${limit}`),
    enabled: !!user?.id,
    refetchInterval: 5 * 60 * 1000, // 5 minutes
  });
}
```

### Query Client Configuration

```typescript
// In App.tsx or main query setup
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

---

## Error Handling

### Error Handling Strategy

**Frontend Error Handling**:

1. **Loading States**: Show skeleton loaders while fetching
2. **Error States**: Display error messages with retry buttons
3. **Validation Errors**: Show field-level validation messages
4. **Network Errors**: Display user-friendly error messages
5. **Timeout Handling**: Implement request timeouts with retry logic

**Error Display Components**:

```typescript
// ErrorBoundary for page-level errors
<ErrorBoundary fallback={<ErrorPage />}>
  <StaffDashboard />
</ErrorBoundary>

// Toast notifications for action errors
addToast({
  title: "Error",
  description: "Failed to update appointment",
  variant: "error",
});

// Inline error messages for form validation
{errors.startDate && (
  <p className="text-sm text-destructive">{errors.startDate}</p>
)}
```

### Common Error Scenarios

1. **Unauthorized Access**: Redirect to login
2. **Forbidden Access**: Redirect to appropriate dashboard
3. **Not Found**: Display "No data" message
4. **Server Error**: Display error message with retry
5. **Network Error**: Display offline message with retry
6. **Validation Error**: Display field-level errors

---

## Loading States

### Loading Patterns

**Skeleton Loaders**:
- Use existing `Skeleton` component from UI library
- Show skeleton for each metric card on dashboard
- Show skeleton for list items while loading

**Loading Indicators**:
- Use `Spinner` component for inline loading
- Show loading state on buttons during mutations
- Disable interactions while loading

**Optimistic Updates**:
- Update UI immediately on user action
- Revert on error
- Show success toast on completion

---

## Testing Strategy

### Unit Testing

**Component Tests**:
- Test metric card rendering with different data
- Test appointment list filtering and sorting
- Test form validation and submission
- Test error state rendering
- Test loading state rendering

**Hook Tests**:
- Test data fetching with mocked API
- Test error handling
- Test refetch logic
- Test query invalidation

**Example Test Structure**:
```typescript
describe("StaffDashboardHome", () => {
  it("should display metric cards with data", () => {
    // Test metric rendering
  });

  it("should refresh metrics every 5 minutes", () => {
    // Test auto-refresh
  });

  it("should display error message on fetch failure", () => {
    // Test error handling
  });
});
```

### Integration Testing

**API Integration**:
- Test staff can only view their own data
- Test appointment status updates
- Test time off request submission
- Test earnings calculation

**Route Protection**:
- Test non-staff users are redirected
- Test staff users can access staff routes
- Test invalid tokens redirect to login

### Property-Based Testing

**Properties to Test**:
- Staff data isolation (staff can only see their own data)
- Appointment status transitions
- Time off request validation
- Earnings calculation accuracy

---

## Security Considerations

### Access Control

1. **Route Protection**: All `/staff/*` routes require staff role
2. **Data Filtering**: Backend filters data by `staff_id`
3. **API Authorization**: Verify staff_id matches authenticated user
4. **Token Validation**: Verify JWT token on every request

### Implementation

```typescript
// Route guard
<ProtectedRoute
  path="/staff/*"
  requiredRole="staff"
  fallback={<Navigate to="/dashboard" />}
>
  <StaffLayout />
</ProtectedRoute>

// API request with staff_id
const response = await apiClient.get(
  `/appointments?staff_id=${user.id}`
);
```

---

## Performance Optimization

### Optimization Strategies

1. **Code Splitting**: Lazy load staff pages
2. **Query Caching**: Cache staff data with 5-minute stale time
3. **Pagination**: Paginate large lists (appointments, earnings history)
4. **Memoization**: Memoize expensive computations
5. **Image Optimization**: Optimize profile images

### Implementation

```typescript
// Lazy load staff pages
const StaffDashboard = lazy(() => import("@/pages/staff/Dashboard"));
const StaffAppointments = lazy(() => import("@/pages/staff/Appointments"));

// Pagination in hooks
export function useMyAppointments(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["my-appointments", page, pageSize],
    queryFn: () => apiClient.get(`/appointments?staff_id=${user.id}&page=${page}&pageSize=${pageSize}`),
  });
}
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Staff Data Isolation

**For any** staff member and any other staff member, when fetching appointments, the system SHALL only return appointments assigned to that specific staff member, never appointments from other staff members.

**Validates: Requirements 2.1, 10.6, 12.6**

### Property 2: Appointment Status Transitions

**For any** appointment, marking it as completed SHALL update the appointment status to "completed" and persist the change such that subsequent queries return the updated status.

**Validates: Requirements 2.6**

### Property 3: Time Off Request Validation

**For any** time off request submission, if the start date is not before the end date, the system SHALL reject the request and maintain the current state unchanged.

**Validates: Requirements 4.5, 4.6**

### Property 4: Earnings Calculation Accuracy

**For any** staff member, the total earnings displayed SHALL equal the sum of all individual commission amounts for that staff member in the specified period.

**Validates: Requirements 5.2, 20.7**

### Property 5: Metric Refresh Consistency

**For any** dashboard metrics, after a refresh is triggered, the displayed values SHALL reflect the current state from the backend within 2 seconds.

**Validates: Requirements 1.8, 1.9**

### Property 6: Time Off Balance Accuracy

**For any** staff member, the displayed time off balance SHALL equal the total allocated days minus approved time off requests.

**Validates: Requirements 4.8**

### Property 7: Appointment History Completeness

**For any** staff member, the appointment history view SHALL display all past appointments (status = "completed" or "cancelled") sorted by date in ascending order.

**Validates: Requirements 2.7, 2.8**

### Property 8: Shift Status Consistency

**For any** shift, the displayed status SHALL match the current status in the backend, and status transitions SHALL be atomic.

**Validates: Requirements 3.3**

### Property 9: Appointment Filtering by Status

**For any** status filter applied to the appointments list, all returned appointments SHALL have a status matching the selected filter, and no appointments with other statuses SHALL be included.

**Validates: Requirements 2.4**

### Property 10: Shift Sorting Order

**For any** set of shifts, when displayed without explicit sorting, they SHALL be sorted by date in ascending order by default.

**Validates: Requirements 3.6**

### Property 11: Time Off Request Sorting Order

**For any** set of time off requests, when displayed without explicit sorting, they SHALL be sorted by date in descending order by default.

**Validates: Requirements 4.9**

### Property 12: Route Protection for Non-Staff Users

**For any** non-staff user attempting to access `/staff/*` routes, the system SHALL redirect them to the appropriate dashboard for their role and prevent access to staff pages.

**Validates: Requirements 8.1, 8.3**

### Property 13: Staff Route Access

**For any** staff member with valid authentication, accessing `/staff/*` routes SHALL allow access and display the requested staff page without redirection.

**Validates: Requirements 8.2**

### Property 14: Invalid Token Redirect

**For any** request with an invalid or expired authentication token, accessing protected `/staff/*` routes SHALL redirect to the login page.

**Validates: Requirements 8.4**

### Property 15: Metric Card Display

**For any** dashboard load, all four metric cards (today's appointments, upcoming shifts, pending time off, earnings summary) SHALL be displayed with valid data or appropriate loading/error states.

**Validates: Requirements 1.2, 1.3, 1.4, 1.5**

### Property 16: Activity Feed Limit

**For any** activity feed display, the system SHALL show exactly the last 10 events, never more or fewer (unless fewer than 10 events exist).

**Validates: Requirements 1.7**

### Property 17: Appointment Detail Completeness

**For any** appointment detail view, all required information (customer name, contact details, service, date, time, status, notes) SHALL be displayed.

**Validates: Requirements 2.5**

### Property 18: Shift Detail Completeness

**For any** shift detail view, all required information (start time, end time, date, status) SHALL be displayed.

**Validates: Requirements 3.7**

### Property 19: Settings Update Persistence

**For any** staff settings update, after successful submission, subsequent queries for that staff member's settings SHALL return the updated values.

**Validates: Requirements 7.2, 7.3, 7.4, 7.6**

### Property 20: Settings Validation

**For any** staff settings form submission with invalid input (e.g., invalid email format, missing required fields), the system SHALL reject the submission and display validation error messages.

**Validates: Requirements 7.5**

### Property 21: Hook State Handling

**For any** custom staff hook (useMyAppointments, useMyShifts, useMyEarnings, useMyTimeOffRequests), the hook SHALL properly handle loading, error, and success states, providing appropriate data or error information to consumers.

**Validates: Requirements 10.5, 10.6**

### Property 22: Component Responsiveness

**For any** staff component, when rendered on mobile devices (viewport width < 768px), the component SHALL remain functional and readable without horizontal scrolling or layout breakage.

**Validates: Requirements 11.4**

---

## Implementation Roadmap

### Phase 1: Core Features (High Priority)

**Sprint 1**:
- Create staff route structure and layout
- Implement Dashboard Home page with metrics
- Create custom hooks (useMyAppointments, useMyShifts, etc.)

**Sprint 2**:
- Implement My Appointments page (list + calendar views)
- Implement My Shifts page
- Implement Time Off Requests page

### Phase 2: Medium Priority Features

**Sprint 3**:
- Implement My Earnings page
- Implement Performance & Ratings page

### Phase 3: Nice to Have Features

**Sprint 4**:
- Enhance Staff Settings page

### Phase 4: Extended Features

**Sprint 5+**:
- Implement Attendance, Documents, Goals, Messages, Feedback pages
- Add advanced features (appointment notes, commission breakdown, etc.)

---

## Integration Points

### With Existing Systems

1. **Authentication**: Use existing auth system with staff role verification
2. **Appointments**: Reuse existing Appointment model and routes
3. **Shifts**: Reuse existing Shift model and routes
4. **Time Off**: Reuse existing TimeOffRequest model and routes
5. **Commissions**: Reuse existing StaffCommission model and routes
6. **UI Components**: Reuse Button, Badge, Card, Spinner, ConfirmationModal
7. **Icons**: Use existing icons from @/components/icons
8. **Hooks**: Follow existing hook patterns (useQuery, useMutation)

### Backend Changes Required

**Minimal Changes**:
- Add `/staff/{id}/metrics` endpoint for dashboard metrics
- Add `/staff/{id}/activity-feed` endpoint for activity feed
- Ensure existing endpoints filter by staff_id

**No Changes Required**:
- Appointment routes (already support staff_id filtering)
- Shift routes (already support staff_id filtering)
- TimeOffRequest routes (already support staff_id filtering)
- Commission routes (already support staff_id filtering)

---

## Deployment Considerations

### Feature Flags

Use feature flags to gradually roll out staff dashboard:
```typescript
if (featureFlags.staffDashboard) {
  // Show staff dashboard
}
```

### Database Migrations

No database migrations required - all models already exist.

### Backward Compatibility

- No breaking changes to existing APIs
- Staff pages are new routes, don't affect existing functionality
- Existing owner/manager pages remain unchanged

---

## Monitoring and Observability

### Metrics to Track

1. **Page Load Time**: Dashboard should load within 2 seconds
2. **API Response Time**: Appointments, shifts, earnings endpoints
3. **Error Rate**: Failed requests, validation errors
4. **User Engagement**: Page views, feature usage

### Logging

- Log all staff data access for audit trail
- Log errors with context for debugging
- Log performance metrics for optimization

---

## Future Enhancements

### Phase 4+ Features

1. **Attendance & Check-in/Check-out**: Clock in/out functionality
2. **Appointment Cancellation/Rescheduling**: Staff-initiated changes
3. **Notifications & Reminders**: Email and in-app notifications
4. **Documents & Certifications**: Upload and manage documents
5. **Goals & Targets**: Track sales and commission targets
6. **Team Communication**: Messages from manager
7. **Appointment Notes**: Add notes to appointments
8. **Commission Breakdown**: Detailed commission analysis
9. **Customer Feedback**: View and respond to reviews

---

## References

### Existing Patterns

- **Dashboard Pattern**: `salon/src/pages/pos/POSDashboard.tsx`
- **Bookings Pattern**: `salon/src/pages/bookings/Bookings.tsx`
- **Settings Pattern**: `salon/src/pages/owner/settings/SystemSettings.tsx`
- **Card Pattern**: `salon/src/components/bookings/BookingCard.tsx`
- **Hook Pattern**: `salon/src/hooks/useCommissions.ts`

### Related Documentation

- Requirements: `.kiro/specs/staff-dashboard-enhancement/requirements.md`
- Staff Settings Implementation: `STAFF_SETTINGS_IMPLEMENTATION.md`
- Existing Staff Routes: `backend/app/routes/staff.py`

