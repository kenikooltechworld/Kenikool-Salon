# Phase 2 Frontend Implementation Plan - Booking System

**Date:** February 14, 2026  
**Status:** Planning  
**Frontend Framework:** React 19 + TypeScript + Vite  
**UI Library:** Custom Tailwind CSS Components

## Overview

Phase 2 frontend focuses on implementing the booking system UI components that integrate with the backend APIs. This includes service management, staff availability, booking creation, and calendar views. All components will use the existing React Query hooks and Zustand stores for state management.

---

## Project Structure

```
salon/src/
├── pages/
│   ├── bookings/                    (NEW - Booking management)
│   │   ├── Bookings.tsx             (Main bookings page)
│   │   ├── BookingList.tsx          (List view with filters)
│   │   ├── BookingDetail.tsx        (Single booking details)
│   │   ├── CreateBooking.tsx        (Booking creation wizard)
│   │   ├── BookingCalendar.tsx      (Calendar view)
│   │   └── BookingConfirmation.tsx  (Confirmation page)
│   ├── services/                    (EXISTING - Service management)
│   │   ├── Services.tsx             (Update with API integration)
│   │   ├── ServiceForm.tsx          (Create/edit service)
│   │   └── ServiceDetail.tsx        (Service details)
│   └── appointments/                (RENAME from appointments to bookings)
│       └── Appointments.tsx         (Redirect or rename)
├── components/
│   ├── bookings/                    (NEW - Booking components)
│   │   ├── BookingCard.tsx          (Booking card display)
│   │   ├── BookingForm.tsx          (Booking form)
│   │   ├── AvailabilityPicker.tsx   (Staff/time availability picker)
│   │   ├── ServiceSelector.tsx      (Service selection)
│   │   ├── TimeSlotPicker.tsx       (Time slot selection)
│   │   ├── BookingStatusBadge.tsx   (Status indicator)
│   │   └── BookingActions.tsx       (Confirm/cancel actions)
│   ├── services/                    (NEW - Service components)
│   │   ├── ServiceCard.tsx          (Service card)
│   │   ├── ServiceForm.tsx          (Service form)
│   │   └── ServiceFilter.tsx        (Service filtering)
│   └── calendar/                    (NEW - Calendar components)
│       ├── CalendarView.tsx         (Calendar display)
│       ├── DayView.tsx              (Day view)
│       ├── WeekView.tsx             (Week view)
│       └── MonthView.tsx            (Month view)
├── hooks/
│   ├── useBookings.ts               (RENAME from useAppointments)
│   ├── useServices.ts               (EXISTING - Update)
│   ├── useAvailability.ts           (NEW - Availability hook)
│   ├── useTimeSlots.ts              (NEW - Time slots hook)
│   └── useBookingForm.ts            (NEW - Booking form state)
├── types/
│   ├── booking.ts                   (NEW - Booking types)
│   ├── service.ts                   (NEW - Service types)
│   ├── availability.ts              (NEW - Availability types)
│   └── timeSlot.ts                  (NEW - Time slot types)
└── stores/
    └── bookings.ts                  (NEW - Booking state store)
```

---

## API Integration Details

### Backend Endpoints Used

**Services API:**
```
GET    /v1/services                  - List all services
GET    /v1/services/{id}             - Get service details
POST   /v1/services                  - Create service
PUT    /v1/services/{id}             - Update service
DELETE /v1/services/{id}             - Delete service
```

**Availability API:**
```
GET    /v1/availability              - List availability
GET    /v1/availability/{id}         - Get availability details
POST   /v1/availability              - Create availability
PUT    /v1/availability/{id}         - Update availability
DELETE /v1/availability/{id}         - Delete availability
GET    /v1/availability/slots/available - Get available slots
```

**Bookings API:**
```
GET    /v1/appointments              - List bookings
GET    /v1/appointments/{id}         - Get booking details
POST   /v1/appointments              - Create booking
PUT    /v1/appointments/{id}         - Update booking
POST   /v1/appointments/{id}/confirm - Confirm booking
POST   /v1/appointments/{id}/cancel  - Cancel booking
GET    /v1/appointments/available-slots/{staff_id}/{service_id} - Get available slots
GET    /v1/appointments/calendar/day - Day view
GET    /v1/appointments/calendar/week - Week view
GET    /v1/appointments/calendar/month - Month view
```

**Time Slots API:**
```
GET    /v1/time-slots                - List time slots
GET    /v1/time-slots/{id}           - Get time slot details
POST   /v1/time-slots                - Create time slot
POST   /v1/time-slots/{id}/confirm   - Confirm time slot
```

---

## Component Implementation Details

### 1. Bookings Page (`salon/src/pages/bookings/Bookings.tsx`)

**Purpose:** Main booking management page with tabs for different views

**Features:**
- Tab navigation (List, Calendar, Create)
- Booking list with filters (status, date range, staff)
- Quick actions (view, confirm, cancel)
- Create new booking button
- Real-time updates via Socket.io

**State Management:**
- Use `useBookings()` hook for fetching bookings
- Use Zustand store for UI state (active tab, filters)
- Use React Query for caching and synchronization

**Props:** None (page component)

**Dependencies:**
- `useBookings()` - Custom hook for booking queries
- `BookingList` - Booking list component
- `BookingCalendar` - Calendar view component
- `CreateBooking` - Booking creation wizard

---

### 2. Booking List (`salon/src/components/bookings/BookingList.tsx`)

**Purpose:** Display bookings in a table/card format with filtering and pagination

**Features:**
- Responsive table/card layout
- Filters: status, date range, staff member, service
- Pagination (10, 25, 50 items per page)
- Sort by: date, status, customer name
- Quick actions: view, confirm, cancel
- Empty state handling

**Props:**
```typescript
interface BookingListProps {
  bookings: Booking[];
  isLoading: boolean;
  onViewBooking: (id: string) => void;
  onConfirmBooking: (id: string) => void;
  onCancelBooking: (id: string) => void;
  filters?: BookingFilters;
  onFiltersChange?: (filters: BookingFilters) => void;
}
```

**State:**
- Current page
- Items per page
- Sort field and direction
- Active filters

---

### 3. Create Booking Wizard (`salon/src/pages/bookings/CreateBooking.tsx`)

**Purpose:** Multi-step wizard for creating new bookings

**Steps:**
1. **Select Service** - Choose service from list
2. **Select Staff** - Choose staff member
3. **Select Date & Time** - Pick available time slot
4. **Customer Details** - Enter/select customer
5. **Confirm & Create** - Review and create booking

**Features:**
- Step validation before proceeding
- Back/Next navigation
- Real-time availability checking
- Conflict prevention
- Confirmation summary

**State Management:**
- Use `useBookingForm()` hook for form state
- Use React Query mutations for API calls
- Use Zustand for wizard step tracking

---

### 4. Availability Picker (`salon/src/components/bookings/AvailabilityPicker.tsx`)

**Purpose:** Interactive component for selecting available time slots

**Features:**
- Calendar date picker
- Staff member selector
- Service duration display
- Available time slots display
- 10-minute slot intervals
- Timezone support
- Conflict highlighting

**Props:**
```typescript
interface AvailabilityPickerProps {
  staffId: string;
  serviceId: string;
  serviceDuration: number;
  onSlotSelect: (slot: TimeSlot) => void;
  minDate?: Date;
  maxDate?: Date;
  excludeDates?: Date[];
}
```

**API Integration:**
- Fetch availability: `GET /v1/availability`
- Get available slots: `GET /v1/appointments/available-slots/{staff_id}/{service_id}`
- Create time slot: `POST /v1/time-slots`

---

### 5. Booking Calendar (`salon/src/pages/bookings/BookingCalendar.tsx`)

**Purpose:** Calendar view of bookings with day/week/month options

**Features:**
- Day view: Hourly timeline with bookings
- Week view: 7-day grid with bookings
- Month view: Monthly grid with booking indicators
- View switching
- Booking details on click
- Color-coded by status
- Timezone support

**Props:**
```typescript
interface BookingCalendarProps {
  view?: 'day' | 'week' | 'month';
  onViewChange?: (view: 'day' | 'week' | 'month') => void;
  onBookingClick?: (bookingId: string) => void;
  staffId?: string;
}
```

**API Integration:**
- Day view: `GET /v1/appointments/calendar/day?date=YYYY-MM-DD`
- Week view: `GET /v1/appointments/calendar/week?start_date=YYYY-MM-DD`
- Month view: `GET /v1/appointments/calendar/month?month=YYYY-MM`

---

### 6. Booking Detail (`salon/src/pages/bookings/BookingDetail.tsx`)

**Purpose:** Display full booking details with actions

**Features:**
- Booking information (customer, service, staff, time)
- Status display with timeline
- Customer history
- Notes/comments section
- Action buttons (confirm, cancel, reschedule)
- Notification history

**Props:**
```typescript
interface BookingDetailProps {
  bookingId: string;
  onClose?: () => void;
  onConfirm?: (id: string) => void;
  onCancel?: (id: string) => void;
}
```

**API Integration:**
- Get booking: `GET /v1/appointments/{id}`
- Confirm booking: `POST /v1/appointments/{id}/confirm`
- Cancel booking: `POST /v1/appointments/{id}/cancel`

---

### 7. Service Management (`salon/src/pages/services/Services.tsx`)

**Purpose:** Manage salon/spa/gym services

**Features:**
- Service list with search and filters
- Create new service
- Edit service
- Delete service
- Category filtering
- Price and duration display
- Availability status

**API Integration:**
- List services: `GET /v1/services`
- Get service: `GET /v1/services/{id}`
- Create service: `POST /v1/services`
- Update service: `PUT /v1/services/{id}`
- Delete service: `DELETE /v1/services/{id}`

---

## Custom Hooks

### `useBookings(filters?: BookingFilters)`

**Purpose:** Fetch and manage bookings with filtering

**Returns:**
```typescript
{
  bookings: Booking[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
  createBooking: (data: CreateBookingInput) => Promise<Booking>;
  confirmBooking: (id: string) => Promise<void>;
  cancelBooking: (id: string, reason: string) => Promise<void>;
}
```

**Implementation:**
- Use React Query `useQuery` for fetching
- Use React Query `useMutation` for mutations
- Auto-refetch on window focus
- Cache invalidation on mutations

---

### `useAvailability(staffId: string, serviceId: string, date: Date)`

**Purpose:** Fetch available time slots for booking

**Returns:**
```typescript
{
  slots: TimeSlot[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}
```

**Implementation:**
- Fetch from `GET /v1/appointments/available-slots/{staff_id}/{service_id}`
- Cache with 1-minute stale time
- Auto-refetch when date changes

---

### `useTimeSlots()`

**Purpose:** Manage time slot reservations

**Returns:**
```typescript
{
  createSlot: (data: CreateTimeSlotInput) => Promise<TimeSlot>;
  confirmSlot: (id: string) => Promise<void>;
  isLoading: boolean;
  error: Error | null;
}
```

**Implementation:**
- Use React Query mutations
- Handle 10-minute reservation window
- Auto-cleanup on unmount

---

### `useBookingForm()`

**Purpose:** Manage booking creation form state

**Returns:**
```typescript
{
  step: number;
  formData: BookingFormData;
  setStep: (step: number) => void;
  updateFormData: (data: Partial<BookingFormData>) => void;
  canProceed: () => boolean;
  submit: () => Promise<Booking>;
  isSubmitting: boolean;
  error: Error | null;
}
```

**Implementation:**
- Use Zustand for state management
- Validate each step before proceeding
- Handle form submission

---

## Type Definitions

### `Booking`
```typescript
interface Booking {
  id: string;
  customerId: string;
  serviceId: string;
  staffId: string;
  startTime: Date;
  endTime: Date;
  status: 'scheduled' | 'confirmed' | 'completed' | 'cancelled' | 'no_show';
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}
```

### `Service`
```typescript
interface Service {
  id: string;
  name: string;
  description: string;
  duration: number; // in minutes
  price: number;
  category: string;
  isActive: boolean;
  isPublished: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

### `Availability`
```typescript
interface Availability {
  id: string;
  staffId: string;
  isRecurring: boolean;
  dayOfWeek?: number; // 0-6 for recurring
  startTime: string; // HH:MM format
  endTime: string;
  breakStart?: string;
  breakEnd?: string;
  startDate?: Date; // for custom ranges
  endDate?: Date;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}
```

### `TimeSlot`
```typescript
interface TimeSlot {
  id: string;
  staffId: string;
  serviceId: string;
  startTime: Date;
  endTime: Date;
  isReserved: boolean;
  reservationExpiresAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}
```

---

## Implementation Tasks

### Phase 2A: Core Components (Week 1)

- [ ] Create `salon/src/pages/bookings/` directory structure
- [ ] Implement `BookingList.tsx` component
- [ ] Implement `BookingCard.tsx` component
- [ ] Implement `BookingStatusBadge.tsx` component
- [ ] Create `useBookings()` hook
- [ ] Create booking types in `salon/src/types/booking.ts`
- [ ] Write unit tests for components
- [ ] Write integration tests for API calls

### Phase 2B: Booking Creation (Week 2)

- [ ] Implement `CreateBooking.tsx` wizard
- [ ] Implement `ServiceSelector.tsx` component
- [ ] Implement `AvailabilityPicker.tsx` component
- [ ] Implement `TimeSlotPicker.tsx` component
- [ ] Create `useBookingForm()` hook
- [ ] Create `useAvailability()` hook
- [ ] Create `useTimeSlots()` hook
- [ ] Write unit tests for wizard flow

### Phase 2C: Calendar Views (Week 3)

- [ ] Implement `BookingCalendar.tsx` component
- [ ] Implement `DayView.tsx` component
- [ ] Implement `WeekView.tsx` component
- [ ] Implement `MonthView.tsx` component
- [ ] Add calendar navigation
- [ ] Add booking details modal
- [ ] Write unit tests for calendar views

### Phase 2D: Service Management (Week 4)

- [ ] Update `Services.tsx` with API integration
- [ ] Implement `ServiceForm.tsx` component
- [ ] Implement `ServiceCard.tsx` component
- [ ] Implement `ServiceFilter.tsx` component
- [ ] Add create/edit/delete functionality
- [ ] Add search and filtering
- [ ] Write unit tests for service management

### Phase 2E: Integration & Polish (Week 5)

- [ ] Connect all components
- [ ] Add real-time updates via Socket.io
- [ ] Add error handling and loading states
- [ ] Add success notifications
- [ ] Add confirmation dialogs
- [ ] Optimize performance
- [ ] Write integration tests
- [ ] User acceptance testing

---

## State Management Strategy

### Zustand Stores

**`stores/bookings.ts`:**
- Current booking filters
- Active calendar view
- Selected booking
- Wizard step
- UI state (modals, notifications)

**`stores/auth.ts` (existing):**
- User information
- Permissions
- Authentication state

**`stores/ui.ts` (existing):**
- Theme
- Notifications
- Modal states

### React Query

**Query Keys:**
```typescript
// Bookings
['bookings', filters]
['booking', id]

// Services
['services', filters]
['service', id]

// Availability
['availability', staffId, date]
['availableSlots', staffId, serviceId, date]

// Time Slots
['timeSlots', filters]
['timeSlot', id]
```

---

## Error Handling

**Common Errors:**
- Double-booking prevention
- Expired time slot reservations
- Invalid availability
- Network errors
- Validation errors

**User Feedback:**
- Toast notifications for errors
- Inline validation messages
- Retry buttons for failed requests
- Fallback UI for loading states

---

## Performance Optimization

- Lazy load calendar components
- Virtualize long booking lists
- Debounce search/filter inputs
- Memoize expensive computations
- Optimize re-renders with React.memo
- Use React Query for caching
- Implement pagination for large datasets

---

## Testing Strategy

### Unit Tests
- Component rendering
- User interactions
- Form validation
- Hook logic

### Integration Tests
- API integration
- State management
- Navigation flows
- Error handling

### E2E Tests
- Complete booking flow
- Calendar interactions
- Service management
- Real-time updates

---

## Accessibility Requirements

- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- Color contrast ratios
- ARIA labels and roles
- Focus management
- Semantic HTML

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Dependencies

**Already Installed:**
- React 19.2.0
- TypeScript 5.9.3
- Zustand 4.4+
- @tanstack/react-query 5.28+
- Axios 1.6+
- Tailwind CSS 3.4+

**May Need:**
- react-big-calendar (for calendar views)
- date-fns (for date utilities)
- react-hook-form (for form management)

---

## Next Steps

1. Review and approve this implementation plan
2. Create directory structure
3. Implement Phase 2A components
4. Test with backend APIs
5. Iterate based on feedback
6. Complete remaining phases

---

## Notes

- All components use existing UI component library
- All API calls use existing hooks and utilities
- All state management uses existing stores
- All styling uses Tailwind CSS
- All types are TypeScript
- All components are fully responsive
- All components support light/dark modes
