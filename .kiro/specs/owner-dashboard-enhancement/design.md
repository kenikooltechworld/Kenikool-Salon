# Owner Dashboard Enhancement - Design Document

## Overview

The Owner Dashboard Enhancement provides a comprehensive, real-time business intelligence interface for salon/spa/gym owners. This feature replaces the empty placeholder with a fully functional dashboard displaying key performance indicators, upcoming appointments, pending actions, and integrated real-time notifications. The design maintains consistency with existing UI patterns while introducing new components for data visualization and real-time updates.

### Current Implementation Status

**Existing Components Ready to Use**:
- `NotificationCenter.tsx` - Notification panel with filtering and management
- `NotificationList.tsx` - List of notifications with read/unread states
- `useNotifications` hook - Fetch and manage notifications
- `useUnreadNotificationCount` hook - Get unread count
- `useNotificationPreferences` hook - Manage preferences

**Existing APIs Available**:
- `GET /financial-reports/revenue` - Revenue data with date ranges
- `GET /financial-reports/outstanding-balance` - Pending payments
- `GET /appointments` - List appointments with filtering
- `GET /staff/{id}/metrics` - Staff performance metrics
- `GET /notifications` - Fetch notifications
- `POST /notifications/preferences` - Update preferences

**What We're Building**:
- New aggregation endpoints that combine multiple data sources
- Dashboard components that visualize this data
- Real-time update mechanism via WebSocket
- Notification integration into the dashboard UI
- Responsive layout for all device sizes

### Architecture Philosophy

The dashboard follows a **data aggregation pattern** where:
1. **Backend** aggregates data from multiple sources into single endpoints
2. **Frontend** fetches aggregated data via React Query with caching
3. **Real-time layer** uses WebSocket to push updates
4. **UI layer** displays data with automatic refresh on cache invalidation

This approach minimizes frontend complexity and leverages existing backend infrastructure.

---

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Owner Dashboard                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Header with Notification Badge & Settings           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Metric Cards (Revenue, Appointments, etc)           │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐             │  │
│  │  │ Revenue  │ │Appts     │ │Satisfaction           │  │
│  │  └──────────┘ └──────────┘ └──────────┘             │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐             │  │
│  │  │Utilization│ │Payments  │ │Inventory │             │  │
│  │  └──────────┘ └──────────┘ └──────────┘             │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Upcoming Appointments Section                       │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ Appointment 1 | Appointment 2 | Appointment 3 │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Pending Actions Section                            │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ Action 1 (High) | Action 2 (Medium) | ...     │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                          │                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Revenue Analytics & Staff Performance              │  │
│  │  ┌──────────────────┐ ┌──────────────────┐          │  │
│  │  │ Revenue Chart    │ │ Staff Performance│          │  │
│  │  └──────────────────┘ └──────────────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         │                    │                    │
    ┌────▼────────────────────▼────────────────────▼────┐
    │    Custom Hooks (useOwnerDashboard, etc)          │
    └────┬────────────────────┬────────────────────┬────┘
         │                    │                    │
    ┌────▼────────────────────▼────────────────────▼────┐
    │         API Client Layer (React Query)            │
    └────┬────────────────────┬────────────────────┬────┘
         │                    │                    │
    ┌────▼────────────────────▼────────────────────▼────┐
    │    Backend API Routes & WebSocket                 │
    └────┬────────────────────┬────────────────────┬────┘
         │                    │                    │
    ┌────▼────────────────────▼────────────────────▼────┐
    │  Database (Appointments, Payments, Inventory)     │
    └─────────────────────────────────────────────────────┘
```

### Frontend Architecture

**Route Structure**:
```
/dashboard
  ├── Main dashboard page (owner home)
  └── Notification center (modal/panel)

/settings/notifications
  └── Notification preferences page
```

**Component Structure**:
```
salon/src/components/owner/
├── OwnerDashboard.tsx (Main container)
├── MetricCard.tsx (Reusable metric display)
├── MetricCardSkeleton.tsx (Loading state)
├── UpcomingAppointments.tsx (Appointments list)
├── AppointmentCard.tsx (Individual appointment)
├── PendingActions.tsx (Actions list)
├── ActionItem.tsx (Individual action)
├── RevenueChart.tsx (Revenue visualization)
├── StaffPerformance.tsx (Staff metrics)
├── DashboardHeader.tsx (Header with notification badge)
└── NotificationBadge.tsx (Unread count badge)

salon/src/pages/dashboard/
├── Dashboard.tsx (Main page - replaces placeholder)
└── [Existing notification pages]

salon/src/hooks/owner/
├── useOwnerDashboard.ts (Main dashboard hook)
├── useOwnerMetrics.ts (Metrics fetching)
├── useUpcomingAppointments.ts (Appointments)
├── usePendingActions.ts (Pending actions)
├── useRevenueAnalytics.ts (Revenue data)
└── useStaffPerformance.ts (Staff metrics)
```

---

## Components and Interfaces

### Phase 1: Core Components

#### 1. Owner Dashboard Home Page (`/dashboard`)

**Purpose**: Display key metrics and business overview for quick status check

**Components**:
- `OwnerDashboard.tsx` - Main container
- `DashboardHeader.tsx` - Header with notification badge
- `MetricCard.tsx` - Reusable metric display card
- `UpcomingAppointments.tsx` - Appointments section
- `PendingActions.tsx` - Actions section
- `RevenueChart.tsx` - Revenue visualization
- `StaffPerformance.tsx` - Staff metrics

**Data Flow**:
```
OwnerDashboard
├── useOwnerMetrics()
│   ├── Revenue (current month vs previous)
│   ├── Appointments (today, week, month)
│   ├── Satisfaction score
│   ├── Staff utilization
│   ├── Pending payments
│   └── Inventory status
├── useUpcomingAppointments()
│   └── Next 5-10 appointments
├── usePendingActions()
│   └── Prioritized action list
├── useRevenueAnalytics()
│   └── Revenue trends and breakdown
└── useStaffPerformance()
    └── Top performers and metrics
```

**Key Features**:
- 6-8 metric cards with trends and comparisons
- Auto-refresh every 30 seconds
- Responsive grid layout (1 column mobile, 2 columns tablet, 3+ columns desktop)
- Error handling with manual refresh button
- Loading states with skeleton screens
- Real-time notification badge in header

**Implementation Example**:
```typescript
// salon/src/pages/dashboard/Dashboard.tsx
export default function Dashboard() {
  const { data: metrics, isLoading, error } = useOwnerMetrics();
  const { data: appointments } = useUpcomingAppointments();
  const { data: actions } = usePendingActions();
  
  if (isLoading) return <DashboardSkeleton />;
  if (error) return <DashboardError onRetry={() => refetch()} />;
  
  return (
    <div className="space-y-6">
      <DashboardHeader />
      
      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <MetricCard
          title="Total Revenue"
          value={metrics.revenue.current}
          unit="$"
          trend={metrics.revenue.trend}
          trendPercentage={metrics.revenue.trendPercentage}
          comparison={`vs ${metrics.revenue.previous} last month`}
          icon={<DollarIcon />}
        />
        {/* More metric cards... */}
      </div>
      
      {/* Upcoming Appointments */}
      <UpcomingAppointments appointments={appointments} />
      
      {/* Pending Actions */}
      <PendingActions actions={actions} />
      
      {/* Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RevenueChart />
        <StaffPerformance />
      </div>
    </div>
  );
}
```

**Data Fetching Strategy**:
- Use React Query with 30-second cache TTL
- Auto-refetch every 30 seconds
- Invalidate cache on WebSocket events
- Show loading skeleton on first load
- Show stale data while refetching in background

#### 2. Metric Card Component

**Purpose**: Display individual metric with value, trend, and comparison

**Props**:
```typescript
interface MetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendPercentage?: number;
  comparison?: string; // e.g., "vs last month"
  icon?: React.ReactNode;
  onClick?: () => void;
  isLoading?: boolean;
  error?: string;
}
```

**Features**:
- Displays current value with unit
- Shows trend indicator (up/down/neutral arrow)
- Displays trend percentage
- Shows comparison text
- Loading skeleton state
- Error state with retry
- Click handler for drill-down

#### 3. Upcoming Appointments Component

**Purpose**: Display next 5-10 appointments in chronological order

**Features**:
- Chronological list of appointments
- Color-coded by status (confirmed, pending, completed, cancelled)
- Shows: customer name, service, staff, time, status
- Click to view details or reschedule
- "No appointments" message if empty
- Real-time updates as new bookings arrive
- Includes both internal and public bookings

#### 4. Pending Actions Component

**Purpose**: Display prioritized list of actions requiring attention

**Features**:
- Sorted by priority (high, medium, low)
- Shows: description, due date, priority level
- Mark as complete or dismiss
- Maximum 10 displayed with "View All" link
- Real-time updates
- Color-coded by priority

#### 5. Revenue Chart Component

**Purpose**: Visualize revenue trends over time

**Features**:
- Line or bar chart showing last 30 days
- Toggle between daily, weekly, monthly views
- Shows revenue by service type (pie chart)
- Shows revenue by staff member (top 5)
- Displays total, average, and growth percentage
- Export as PDF or CSV
- Responsive and mobile-friendly

#### 6. Staff Performance Component

**Purpose**: Display staff metrics and performance indicators

**Features**:
- Top 5 staff by revenue generated
- Staff utilization rate
- Staff satisfaction score
- Staff attendance rate
- Click to view detailed performance
- Daily updates
- Comparison to previous period

### Data Models

#### Dashboard Metrics Response
```typescript
interface DashboardMetrics {
  revenue: {
    current: number;
    previous: number;
    trend: 'up' | 'down' | 'neutral';
    trendPercentage: number;
  };
  appointments: {
    today: number;
    thisWeek: number;
    thisMonth: number;
    trend: 'up' | 'down' | 'neutral';
  };
  satisfaction: {
    score: number; // 0-5
    count: number;
    trend: 'up' | 'down' | 'neutral';
  };
  staffUtilization: {
    percentage: number;
    bookedHours: number;
    availableHours: number;
  };
  pendingPayments: {
    count: number;
    totalAmount: number;
    oldestDate: string;
  };
  inventoryStatus: {
    lowStockCount: number;
    expiringCount: number;
  };
}
```

#### Upcoming Appointment
```typescript
interface UpcomingAppointment {
  id: string;
  customerName: string;
  serviceName: string;
  staffName: string;
  startTime: string;
  endTime: string;
  status: 'confirmed' | 'pending' | 'completed' | 'cancelled';
  isPublicBooking: boolean;
}
```

#### Pending Action
```typescript
interface PendingAction {
  id: string;
  description: string;
  dueDate: string;
  priority: 'high' | 'medium' | 'low';
  type: 'payment' | 'staff' | 'inventory' | 'customer' | 'system';
  actionUrl?: string;
}
```

### Hooks

#### useOwnerDashboard
```typescript
function useOwnerDashboard() {
  return {
    metrics: DashboardMetrics;
    appointments: UpcomingAppointment[];
    actions: PendingAction[];
    isLoading: boolean;
    error: Error | null;
    refetch: () => Promise<void>;
  };
}
```

#### useOwnerMetrics
```typescript
function useOwnerMetrics() {
  return {
    data: DashboardMetrics;
    isLoading: boolean;
    error: Error | null;
    refetch: () => Promise<void>;
  };
}
```

#### useUpcomingAppointments
```typescript
function useUpcomingAppointments(limit?: number) {
  return {
    data: UpcomingAppointment[];
    isLoading: boolean;
    error: Error | null;
    refetch: () => Promise<void>;
  };
}
```

#### usePendingActions
```typescript
function usePendingActions() {
  return {
    data: PendingAction[];
    isLoading: boolean;
    error: Error | null;
    markComplete: (actionId: string) => Promise<void>;
    dismiss: (actionId: string) => Promise<void>;
  };
}
```

---

## Real-Time Updates Strategy

### WebSocket Connection
- Establish WebSocket connection on dashboard mount
- Listen for events: `new_appointment`, `payment_received`, `payment_failed`, `staff_alert`, `inventory_alert`
- Update relevant metrics and lists in real-time
- Reconnect automatically on disconnect
- Clean up connection on unmount

### Polling Fallback
- If WebSocket unavailable, fall back to polling every 30 seconds
- Use React Query's `refetchInterval` for automatic polling
- Stale time: 30 seconds (cache results for 30 seconds)

### Cache Invalidation
- Invalidate metrics cache on relevant events
- Invalidate appointments cache on new booking
- Invalidate actions cache on action completion
- Use React Query's `invalidateQueries` for cache management

---

## Notification Integration

### Notification Badge
- Display in header showing unread count
- Update in real-time as notifications arrive
- Click to open notification center panel
- Show notification type icon

### Notification Center Panel
- Reuse existing `NotificationCenter` component
- Display notifications categorized by type
- Show recent notifications first
- Mark as read/unread
- Delete individual or all notifications
- Filter by notification type

### Notification Preferences
- Access from settings page
- Enable/disable notification types
- Set delivery method (in-app, email, SMS)
- Set quiet hours
- Set frequency (real-time, hourly, daily)
- Save preferences to backend

---

## Responsive Design

### Mobile (320px - 767px)
- Single column layout
- Metric cards stack vertically
- Charts are simplified or hidden
- Notification badge is prominent
- Touch-friendly buttons and links
- Horizontal scrolling avoided

### Tablet (768px - 1023px)
- Two column layout
- Metric cards in 2x3 grid
- Charts are readable
- Sidebar navigation if applicable
- Optimized for touch

### Desktop (1024px+)
- Three+ column layout
- Metric cards in 3x2 grid
- Full charts with interactions
- Sidebar navigation
- Optimized for mouse and keyboard

---

## Performance Optimization

### Caching Strategy
- Cache dashboard metrics for 30 seconds
- Cache revenue data for 1 hour
- Cache staff performance for 1 hour
- Invalidate cache on relevant events

### Code Splitting
- Lazy load chart components
- Lazy load analytics sections
- Load notification center on demand

### Image Optimization
- Use SVG for icons
- Optimize chart rendering
- Lazy load images

### API Optimization
- Combine multiple metrics into single endpoint
- Use pagination for large lists
- Implement request debouncing
- Use compression for responses

---

## Accessibility

### WCAG 2.1 AA Compliance
- Semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Color contrast ratios ≥ 4.5:1
- Focus indicators visible
- Screen reader support

### Keyboard Navigation
- Tab through all interactive elements
- Enter/Space to activate buttons
- Arrow keys for list navigation
- Escape to close modals

### Screen Reader Support
- Descriptive alt text for images
- ARIA labels for icons
- Announce loading states
- Announce real-time updates

---

## Error Handling

### API Errors
- Display user-friendly error messages
- Provide manual refresh button
- Log errors for debugging
- Retry failed requests automatically

### Network Errors
- Show offline indicator
- Cache last known data
- Retry on reconnection
- Queue actions for later

### Data Validation
- Validate API responses
- Handle missing or malformed data
- Display fallback values
- Log validation errors

---

## Security Considerations

### Data Isolation
- Only display current tenant's data
- Validate tenant context on all requests
- Filter data at API level
- Prevent cross-tenant data leakage

### Authentication
- Verify user is authenticated
- Check user has owner role
- Validate session token
- Refresh token on expiration

### Authorization
- Verify user has access to dashboard
- Check notification preferences
- Validate action permissions
- Prevent unauthorized actions

---

## Testing Strategy

### Unit Tests
- Test metric calculations
- Test data transformations
- Test error handling
- Test component rendering

### Integration Tests
- Test API integration
- Test WebSocket connection
- Test cache invalidation
- Test real-time updates

### E2E Tests
- Test dashboard load
- Test metric display
- Test notification delivery
- Test user interactions

### Performance Tests
- Test dashboard load time
- Test metric update time
- Test notification delivery time
- Test with 100+ concurrent users

---

## Future Enhancements (Out of Scope)

- Custom dashboard layouts (drag-and-drop widgets)
- Advanced analytics (predictive analytics, ML-based insights)
- Multi-user dashboard sharing
- Historical data export
- Integration with external analytics platforms
- SMS notifications
- Mobile app notifications
- Custom notification templates
- Notification scheduling
