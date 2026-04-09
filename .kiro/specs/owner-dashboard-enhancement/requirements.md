# Requirements: Owner Dashboard Enhancement & Real-Time Notification Integration

## Overview

The Owner Dashboard Enhancement transforms the current empty dashboard placeholder (`<div>Dashboard Page</div>`) into a comprehensive business intelligence and operations center. This feature provides salon/spa/gym owners with real-time visibility into critical business metrics, upcoming appointments, pending actions, and integrated notifications for immediate awareness of important events.

### Current State Analysis

**What Exists**:
- Notification infrastructure fully implemented (models, services, routes, components, hooks)
- Financial reporting APIs with revenue, payment, and balance endpoints
- Appointment management system with list, calendar, and detail views
- Staff management with metrics endpoints
- Inventory system with tracking
- Existing NotificationCenter and NotificationList components ready to use
- React Query setup for data fetching and caching
- Tailwind CSS for styling

**What's Missing**:
- Owner dashboard page is just a placeholder (empty div)
- No dashboard metrics being calculated or displayed
- No integration of notifications into the dashboard UI
- No real-time updates on the dashboard
- No pending actions aggregation
- No revenue analytics visualization
- No staff performance display

### Solution Approach

The feature leverages existing notification infrastructure, financial reporting APIs, and appointment management systems to create a unified dashboard experience. Rather than building from scratch, we aggregate existing data sources into a single, real-time dashboard interface that enables owners to monitor and manage their business effectively from one location.

**Key Integration Points**:
1. **Financial Reports API** → Revenue metrics and pending payments
2. **Appointments API** → Upcoming appointments and satisfaction scores
3. **Staff API** → Staff metrics and performance data
4. **Inventory API** → Low stock alerts
5. **Notifications API** → Real-time event delivery
6. **Existing Components** → NotificationCenter, NotificationList reused

## Business Context

**Problem Statement**: 
- Owner dashboard is non-functional (empty placeholder)
- Notification system infrastructure exists but isn't integrated into owner experience
- Owners lack visibility into critical business metrics and real-time alerts
- No centralized location to view business status and pending actions

**Solution**: 
Build a comprehensive dashboard that displays business metrics, upcoming appointments, pending actions, and integrates real-time notifications for critical business events.

**Success Metrics**:
- Dashboard loads with all metrics within 2 seconds
- Owners receive notifications for critical events within 5 seconds
- 90% of owners use dashboard daily after implementation
- Reduction in response time to critical issues (payment failures, staff no-shows, etc.)

## User Stories

### Story 1: Owner Views Business Overview Dashboard

**As an** owner  
**I want to** see a comprehensive overview of my business metrics and status  
**So that** I can quickly understand my business performance and identify issues

**Acceptance Criteria**:
1. Dashboard displays 6-8 key metric cards on initial load
2. Each metric card shows current value, trend (up/down/neutral), and period comparison
3. Metrics update automatically every 30 seconds without page refresh
4. Dashboard is responsive and works on mobile, tablet, and desktop
5. All data is filtered to show only current tenant's data
6. Dashboard loads within 2 seconds on first load
7. Metrics are cached to reduce database load

**Metrics to Display**:
- **Total Revenue**: Current month vs previous month with trend
- **Total Appointments**: Today, this week, this month with trend
- **Customer Satisfaction Score**: Average rating from completed appointments
- **Staff Utilization Rate**: Percentage of available time booked
- **Pending Payments**: Count and total amount due
- **Inventory Status**: Count of low stock items

### Story 2: Owner Views Upcoming Appointments

**As an** owner  
**I want to** see upcoming appointments for the next 7 days  
**So that** I can plan staffing and resources effectively

**Acceptance Criteria**:
1. Dashboard displays upcoming appointments in chronological order
2. Shows next 5-10 appointments by default
3. Each appointment shows: customer name, service, staff member, time, status
4. Owner can click appointment to view details or reschedule
5. Appointments are color-coded by status (confirmed, pending, completed, cancelled)
6. Shows "No appointments" message if none exist
7. Appointments update in real-time as new bookings are made
8. Includes both internal and public bookings

### Story 3: Owner Receives Real-Time Notifications

**As an** owner  
**I want to** receive real-time notifications for critical business events  
**So that** I can respond quickly to important issues

**Acceptance Criteria**:
1. Notification badge appears in header showing unread count
2. Clicking badge opens notification center panel
3. Notifications are categorized by type (bookings, payments, staff, inventory, system)
4. Each notification shows: type icon, title, description, timestamp
5. Owner can mark notifications as read/unread
6. Owner can delete individual notifications or clear all
7. Notifications persist across page refreshes
8. Owner can set notification preferences (which types to receive)
9. Notifications appear within 5 seconds of event trigger

**Notification Types**:
- **Bookings**: New public booking, booking cancelled, booking rescheduled
- **Payments**: Payment received, payment failed, refund processed
- **Staff**: Staff member called in sick, staff no-show, shift reminder
- **Inventory**: Low stock alert, inventory expiring soon
- **System**: Backup completed, system maintenance, error alerts
- **Reviews**: New customer review, review response needed

### Story 4: Owner Views Pending Actions

**As an** owner  
**I want to** see a list of pending actions that require my attention  
**So that** I don't miss important tasks

**Acceptance Criteria**:
1. Dashboard displays "Pending Actions" section with prioritized list
2. Actions are sorted by priority (high, medium, low)
3. Each action shows: description, due date/time, priority level
4. Owner can mark action as complete or dismiss
5. Completed actions are removed from list
6. Actions include: pending payments, staff requests, customer issues, inventory alerts
7. Actions update in real-time as new issues arise
8. Maximum 10 pending actions displayed (with "View All" link)

**Example Pending Actions**:
- "Payment from John Doe ($150) pending for 3 days" (High)
- "Staff member Sarah requested time off for March 25" (Medium)
- "Inventory: Hair dye stock below minimum threshold" (Medium)
- "Customer review needs response" (Low)
- "Appointment cancellation request from Jane Smith" (High)

### Story 5: Owner Views Revenue Analytics

**As an** owner  
**I want to** see revenue trends and analytics  
**So that** I can understand my business financial performance

**Acceptance Criteria**:
1. Dashboard displays revenue chart showing last 30 days
2. Chart shows daily revenue as line or bar chart
3. Owner can toggle between daily, weekly, monthly views
4. Chart shows revenue by service type (pie chart or breakdown)
5. Chart shows revenue by staff member (top 5 performers)
6. Displays total revenue, average daily revenue, and growth percentage
7. Owner can export revenue report as PDF or CSV
8. Chart updates when new payments are received

### Story 6: Owner Views Staff Performance

**As an** owner  
**I want to** see staff performance metrics  
**So that** I can identify top performers and areas for improvement

**Acceptance Criteria**:
1. Dashboard displays staff performance section
2. Shows top 5 staff members by revenue generated
3. Shows staff utilization rate (% of available time booked)
4. Shows staff satisfaction score (average customer rating)
5. Shows staff attendance rate (% of shifts attended)
6. Owner can click staff member to view detailed performance
7. Performance data updates daily
8. Includes comparison to previous period

### Story 7: Owner Configures Notification Preferences

**As an** owner  
**I want to** configure which notifications I receive and how  
**So that** I'm not overwhelmed with unnecessary alerts

**Acceptance Criteria**:
1. Owner can access notification preferences from settings
2. Owner can enable/disable each notification type
3. Owner can set notification delivery method (in-app, email, SMS)
4. Owner can set quiet hours (no notifications during certain times)
5. Owner can set notification frequency (real-time, hourly digest, daily digest)
6. Preferences are saved and persist across sessions
7. Owner can reset to default preferences
8. Changes take effect immediately

### Story 8: Owner Views Dashboard on Mobile

**As an** owner  
**I want to** view my dashboard on mobile devices  
**So that** I can check business metrics on the go

**Acceptance Criteria**:
1. Dashboard is fully responsive on mobile (320px+)
2. Metric cards stack vertically on mobile
3. Charts are readable on small screens
4. Notification badge is visible and accessible
5. All interactive elements are touch-friendly
6. Performance is optimized for mobile networks
7. No horizontal scrolling required

## Technical Requirements

### Frontend Requirements

**Performance**:
- Dashboard initial load time: < 2 seconds
- Metric updates: < 500ms
- Notification delivery: < 5 seconds from event trigger
- Support for 1000+ notifications in notification center
- Metrics cached for 30 seconds to reduce API calls

**Compatibility**:
- Works on Chrome, Firefox, Safari, Edge (latest 2 versions)
- Responsive design for mobile (320px+), tablet (768px+), desktop (1024px+)
- Accessibility: WCAG 2.1 AA compliance
- Touch-friendly on mobile devices

**Browser Features**:
- WebSocket support for real-time updates
- LocalStorage for notification preferences
- IndexedDB for offline notification caching

**Libraries & Dependencies**:
- React Query for data fetching and caching
- Chart.js or Recharts for data visualization
- Socket.io or native WebSocket for real-time updates
- Tailwind CSS for styling (existing)

### Backend Requirements

**API Endpoints** (New):
- `GET /api/owner/dashboard/metrics` - Get all dashboard metrics
- `GET /api/owner/dashboard/appointments` - Get upcoming appointments
- `GET /api/owner/dashboard/pending-actions` - Get pending actions
- `GET /api/owner/dashboard/revenue-analytics` - Get revenue data
- `GET /api/owner/dashboard/staff-performance` - Get staff metrics
- `WebSocket /ws/notifications` - Real-time notification stream

**API Endpoints** (Existing - to be used):
- `GET /api/financial-reports/revenue` - Revenue data
- `GET /api/financial-reports/outstanding-balance` - Pending payments
- `GET /api/appointments` - Appointments list
- `GET /api/staff/{id}/metrics` - Staff metrics
- `GET /api/notifications` - Notifications list
- `POST /api/notifications/preferences` - Update preferences

**Data Requirements**:
- Dashboard metrics calculated from existing data (appointments, payments, inventory)
- Metrics cached for 30 seconds to reduce database load
- Notifications stored in database with read/unread status
- Notification preferences stored per user

**Performance**:
- Dashboard metrics endpoint response time: < 500ms
- Support concurrent connections for 100+ users
- Real-time notifications delivered within 5 seconds
- Metrics endpoint should use caching layer

### Database Requirements

**Existing Tables to Use**:
- `notifications` - Already exists
- `notification_preferences` - Already exists
- `appointments` - Already exists
- `payments` - Already exists
- `staff` - Already exists
- `inventory` - Already exists

**New Indexes** (if needed):
- `notifications(user_id, created_at DESC)` - For fetching recent notifications
- `notification_preferences(user_id, notification_type)` - For preference lookup

**Caching Strategy**:
- Cache dashboard metrics for 30 seconds
- Cache revenue data for 1 hour
- Cache staff performance for 1 hour
- Invalidate cache on relevant events (new payment, new appointment, etc.)

## Acceptance Criteria (Feature Level)

1. **Dashboard Loads Successfully**
   - Owner navigates to `/dashboard`
   - Dashboard displays all 6-8 metric cards within 2 seconds
   - No console errors or warnings
   - All data is accurate for current tenant

2. **Metrics Display Correctly**
   - All metrics show accurate data for current tenant
   - Metrics update every 30 seconds
   - Trends (up/down) display correctly
   - Period comparisons are accurate
   - Metric cards are responsive on all screen sizes

3. **Notifications Work End-to-End**
   - New booking creates notification for owner
   - Notification appears in header badge within 5 seconds
   - Owner can open notification center and see notification
   - Owner can mark as read/unread
   - Owner can delete notification
   - Notification preferences are respected
   - Notifications persist across page refreshes

4. **Responsive Design**
   - Dashboard is usable on mobile (320px width)
   - Dashboard is usable on tablet (768px width)
   - Dashboard is usable on desktop (1024px+ width)
   - All interactive elements are touch-friendly on mobile
   - No horizontal scrolling on any device

5. **Real-Time Updates**
   - New appointments appear in upcoming list within 5 seconds
   - Pending actions update in real-time
   - Metrics update without page refresh
   - No duplicate notifications
   - WebSocket connection is stable and reconnects on disconnect

6. **Data Security**
   - Only current tenant's data is displayed
   - No cross-tenant data leakage
   - Notifications only show for current user
   - All API calls include tenant context
   - Sensitive data (payment amounts) is properly formatted

7. **Performance**
   - Dashboard initial load: < 2 seconds
   - Metric updates: < 500ms
   - Notification delivery: < 5 seconds
   - No memory leaks or performance degradation over time
   - Supports 100+ concurrent users

## Out of Scope

- Advanced analytics (predictive analytics, ML-based insights)
- Custom dashboard layouts (drag-and-drop widgets)
- Multi-user dashboard sharing
- Historical data export (beyond current month)
- Integration with external analytics platforms
- SMS notifications (email and in-app only for MVP)
- Mobile app notifications (web only for MVP)
- Custom notification templates (use existing templates)
- Notification scheduling (send at specific times)

## Dependencies

- Existing notification infrastructure (models, services, routes)
- Existing appointment, payment, inventory systems
- Existing financial reporting APIs
- WebSocket support in backend
- React Query for data fetching and caching
- Chart library (Chart.js or Recharts)
- Existing authentication and authorization system

## Success Criteria

- Dashboard is fully functional and displays all metrics
- Notifications are delivered in real-time
- Owner can manage notification preferences
- All acceptance criteria are met
- Performance targets are achieved
- No regressions in existing functionality
- Dashboard is accessible and responsive on all devices
- Code follows established patterns and conventions
