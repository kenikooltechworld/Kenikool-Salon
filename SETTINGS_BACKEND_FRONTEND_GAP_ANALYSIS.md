# Settings Backend vs Frontend Gap Analysis

## Backend Tenant Settings Schema (Complete)

The backend has a comprehensive `TenantSettingsSchema` with these core fields:

### Basic Information
- `salon_name` - Business name
- `email` - Business email
- `phone` - Business phone
- `address` - Business address

### Business Configuration
- `tax_rate` - Tax rate percentage (0-100)
- `currency` - Currency code (NGN, USD, etc.)
- `timezone` - Timezone (e.g., Africa/Lagos)
- `language` - Language code (e.g., en)

### Business Hours
- `business_hours` - Dict with day-of-week keys containing:
  - `open_time` - Opening time (HH:MM format)
  - `close_time` - Closing time (HH:MM format)
  - `is_closed` - Whether closed that day

### Notifications
- `notification_email` - Enable email notifications
- `notification_sms` - Enable SMS notifications
- `notification_push` - Enable push notifications

### Branding
- `logo_url` - Logo URL
- `primary_color` - Primary brand color (hex)
- `secondary_color` - Secondary brand color (hex)

### Advanced Settings
- `appointment_reminder_hours` - Hours before appointment to send reminder (1-168)
- `allow_online_booking` - Allow customers to book online
- `require_customer_approval` - Require customer approval for bookings
- `auto_confirm_bookings` - Automatically confirm bookings

---

## Frontend Settings Pages (Current Implementation)

### 1. SystemConfiguration.tsx
**Covers:** Security & Infrastructure
- Middleware settings (audit logging, rate limiting, DDoS, WAF, intrusion detection, enumeration prevention)
- Security settings (SAST, dependency check, pentest framework)
- Feature flags

### 2. SecurityPolicies.tsx
**Covers:** Access Control & Compliance
- (Not fully reviewed, but likely covers RBAC, audit policies)

### 3. IntegrationSettings.tsx
**Covers:** Third-party Integrations
- (Not fully reviewed, but likely covers payment gateways, SMS providers, etc.)

### 4. CommissionSettings.tsx
**Covers:** Staff & Service Commissions
- (Not fully reviewed, but likely covers commission percentages)

### 5. OperationalSettings.tsx
**Covers:** Resources & Inventory
- Resource management (rooms, equipment, capacity)
- Inventory thresholds (low, critical, reorder quantities)
- Waiting room configuration (max queue size, estimated wait time)

### 6. FinancialSettings.tsx
**Covers:** Financial Policies
- Balance enforcement (enabled, minimum threshold)
- Refund policy (enabled, refund window days)
- Commission tracking (staff %, service %)
- Invoice configuration (prefix, starting number)

---

## CRITICAL GAPS - Missing from Frontend

### Missing Basic Business Information Page
The backend has core business settings that are NOT in any frontend page:

**MISSING FIELDS:**
- ✗ `salon_name` - Business name
- ✗ `email` - Business email
- ✗ `phone` - Business phone
- ✗ `address` - Business address
- ✗ `tax_rate` - Tax rate percentage
- ✗ `currency` - Currency code
- ✗ `timezone` - Timezone
- ✗ `language` - Language code
- ✗ `business_hours` - Business hours by day
- ✗ `notification_email` - Email notifications toggle
- ✗ `notification_sms` - SMS notifications toggle
- ✗ `notification_push` - Push notifications toggle
- ✗ `logo_url` - Logo URL
- ✗ `primary_color` - Primary brand color
- ✗ `secondary_color` - Secondary brand color
- ✗ `appointment_reminder_hours` - Reminder timing
- ✗ `allow_online_booking` - Online booking toggle
- ✗ `require_customer_approval` - Booking approval requirement
- ✗ `auto_confirm_bookings` - Auto-confirm toggle

### Summary
**19 core business settings fields** from the backend schema are completely missing from the frontend settings pages. These are fundamental tenant configuration options that should be accessible to users.

---

## Recommendation

Create a new frontend page: **`BusinessSettings.tsx`** (or rename existing `SystemSettings.tsx`) that covers:

1. **Basic Information** - Name, email, phone, address
2. **Business Configuration** - Tax rate, currency, timezone, language
3. **Business Hours** - Day-by-day hours configuration
4. **Notifications** - Email, SMS, push notification toggles
5. **Branding** - Logo, primary color, secondary color
6. **Booking Settings** - Online booking, approval requirements, auto-confirm, reminder hours

This would align the frontend with the complete backend schema and provide users with essential business configuration options.
