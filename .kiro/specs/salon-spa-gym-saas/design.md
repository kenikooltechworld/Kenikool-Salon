# Design Document: Multi-Tenant SaaS Platform for Salon, Spa & Gym Management

## 1. System Architecture Overview

### High-Level Architecture

The platform is built on a modern, cloud-native architecture designed for multi-tenancy, scalability, and reliability. The system follows a layered architecture pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                              │
│  (Web App, Mobile App, Admin Dashboard, Staff Portal)       │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/WebSocket
┌────────────────────▼────────────────────────────────────────┐
│                    API Gateway Layer                         │
│  (Rate Limiting, Authentication, Request Routing)           │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Application Services Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Appointment  │  │   Billing    │  │  Inventory   │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Staff      │  │  Customer    │  │ Notification │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Data Access Layer                               │
│  (ORM, Query Builder, Tenant Filtering)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Infrastructure Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │    Redis     │  │  Message     │      │
│  │  Database    │  │    Cache     │  │   Queue      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack (Africa-Focused SaaS)

**Backend:**
- **Runtime**: Python 3.11+
- **Framework**: FastAPI (async, high-performance REST API)
- **Database**: MongoDB Atlas (cloud-hosted, no local setup required)
- **ODM**: Mongoengine or Motor (async MongoDB driver)
- **Cache**: Redis 7+ (for sessions and caching)
- **Message Queue**: Celery with RabbitMQ (async task processing)
- **Search**: MongoDB Atlas Search

**Frontend (React 19+ with TypeScript):**
- **Framework**: React 19.2.0 with TypeScript 5.9.3
- **Build Tool**: Vite 7.3.1 (fast, modern build tool)
- **State Management**: Zustand (lightweight, simple) - *To be installed*
- **Data Fetching**: @tanstack/react-query (powerful data sync) - *To be installed*
- **Real-time**: Socket.io (real-time notifications and updates) - *To be installed*
- **HTTP Client**: Axios (integrated with React Query) - *To be installed*
- **Styling**: Tailwind CSS with @tailwindcss/vite plugin
- **UI Components**: 35+ custom production-ready components built with Tailwind CSS
  - Form components: Button, Input, Textarea, Select, Checkbox, Radio, Switch, Label, Slider
  - Display components: Card, Badge, Avatar, Spinner, Skeleton, Progress, Alert, Toast
  - Dialog components: Modal, Dialog, ConfirmationModal, MobileModal
  - Navigation: Dropdown, Tabs, Tooltip
  - Advanced: Calendar, Table, ScrollArea, ErrorBoundary, LazyLoad, ImageLightbox, ThemeSelector
- **Icons**: 100+ custom SVG icons (business, navigation, finance, services, etc.)
- **Theme System**: 3 complete themes (Default, Elegant, Vibrant) × 2 modes (Light, Dark) = 6 variations
- **Mobile Optimization**: Touch-friendly targets, responsive grids, safe area insets, smooth scrolling
- **Accessibility**: WCAG compliance features, focus states, keyboard navigation, reduced motion support
- **Code Quality**: ESLint configured, TypeScript strict mode, Vite HMR

**AI/ML:**
- **ML Frameworks**: TensorFlow or PyTorch (Python)
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Model Serving**: FastAPI endpoints
- **Use Cases**: Recommendations, churn prediction, dynamic pricing

**Payments:**
- **Payment Gateway**: Paystack (Africa-focused payment processor)
- **Integration**: Paystack Python SDK

**Infrastructure & DevOps:**
- **Containerization**: Docker & Docker Compose (all services except MongoDB)
- **Database**: MongoDB Atlas (managed cloud service)
- **Container Registry**: Docker Hub or AWS ECR
- **Cloud Provider**: AWS, Google Cloud, or Azure
- **Container Orchestration**: Docker Compose (dev), Kubernetes (production)
- **CI/CD**: GitHub Actions or GitLab CI
- **Monitoring**: Prometheus + Grafana or DataDog
- **Logging**: ELK Stack or CloudWatch

**Testing:**
- **Unit Tests**: pytest (Python), Jest + React Testing Library (TypeScript)
- **Property-Based Tests**: Hypothesis (Python), fast-check (TypeScript)
- **API Testing**: pytest with httpx
- **E2E Testing**: Cypress or Playwright

### Deployment Architecture

**Multi-Region Deployment:**
- Primary region for main application
- Secondary regions for disaster recovery
- CDN for static assets and API caching
- Database replication across regions with failover

**Environment Strategy:**
- Development: Local development environment
- Staging: Pre-production environment mirroring production
- Production: High-availability setup with load balancing

### Scalability Approach

**Horizontal Scaling:**
- Stateless application servers behind load balancer
- Database connection pooling (PgBouncer)
- Read replicas for reporting queries
- Database sharding by tenant_id for very large deployments (>10,000 tenants)

**Vertical Scaling:**
- Increase server resources as needed
- Database optimization through indexing and query optimization

### Performance Targets

- API response time: 95th percentile < 500ms
- Page load time: < 2 seconds
- Database query time: < 100ms (95th percentile)
- Availability: 99.9% uptime SLA
- Concurrent users: 10,000+ per region


## 2. Database Design

### Overall Database Schema Approach

**MongoDB Atlas with Document-Based Architecture:**

The platform uses MongoDB Atlas (cloud-hosted MongoDB) with a document-based data model. This approach provides:
- Flexible schema for evolving requirements
- Horizontal scaling through sharding
- Built-in replication for high availability
- Native support for complex data types (arrays, nested objects)
- Efficient querying with MongoDB Query Language

**Multi-Tenancy Strategy:**
- Tenant ID included in every document as a required field
- Database-level access control through MongoDB roles
- Collection-level permissions per tenant
- Aggregation pipeline for tenant-filtered queries

### Core Data Model Relationships

MongoDB uses a document-oriented model with embedded and referenced relationships:

```
Tenant (root document)
├── User (embedded or referenced)
├── Staff (collection with tenant_id)
├── Customer (collection with tenant_id)
├── Service (collection with tenant_id)
├── Appointment (collection with tenant_id)
├── Invoice (collection with tenant_id)
├── Inventory (collection with tenant_id)
├── Location (collection with tenant_id)
└── AuditLog (collection with tenant_id)
```

### Tenant Isolation Strategy

**Application-Level Filtering:**
- Every query includes `{tenant_id: current_tenant_id}` filter
- ODM (Mongoengine/Motor) automatically adds tenant_id to queries
- Query validation layer prevents accidental cross-tenant queries
- Audit logging tracks all data access

**MongoDB Security:**
- Database users scoped to specific databases
- Role-based access control (RBAC) at database level
- IP whitelist for Atlas cluster access
- Encryption at rest and in transit (TLS)

### Indexing Strategy for Performance

**Primary Indexes:**
- `{tenant_id: 1, _id: 1}` on all collections for fast lookups
- `{tenant_id: 1, created_at: -1}` for time-series queries
- `{tenant_id: 1, status: 1}` for status filtering
- `{tenant_id: 1, user_id: 1}` for user-specific queries

**Secondary Indexes:**
- `{tenant_id: 1, appointment_id: 1}` on appointments
- `{tenant_id: 1, customer_id: 1}` on customer-related collections
- `{tenant_id: 1, staff_id: 1}` on staff-related collections
- `{tenant_id: 1, start_time: 1, end_time: 1}` for availability queries

**Text Search Indexes:**
- `{tenant_id: 1, customer_name: "text"}` for customer search
- `{tenant_id: 1, service_name: "text"}` for service search

### Backup and Disaster Recovery Approach

**Backup Strategy:**
- MongoDB Atlas automated backups (daily)
- Point-in-time recovery (PITR) for 35 days
- Continuous backup snapshots
- Per-tenant backup capability for data export

**Recovery Procedures:**
- RTO (Recovery Time Objective): 15 minutes
- RPO (Recovery Point Objective): 5 minutes
- Automated failover to replica set members
- Manual restore from backups if needed

### Data Encryption

**At Rest:**
- MongoDB Atlas encryption at rest (AES-256)
- Customer-managed encryption keys (CMEK) option
- Encrypted backups

**In Transit:**
- TLS 1.3 for all network communication
- Certificate pinning for API clients
- Encrypted database connections

### Key Data Entities (MongoDB Documents)

**Tenant Collection:**
```javascript
{
  _id: ObjectId,
  name: String,
  subscription_tier: String, // 'starter', 'professional', 'enterprise'
  status: String, // 'active', 'suspended', 'deleted'
  region: String,
  created_at: Date,
  updated_at: Date,
  deleted_at: Date || null,
  settings: {
    branding_logo_url: String,
    primary_color: String,
    secondary_color: String,
    features_enabled: [String],
    custom_domain: String || null,
    timezone: String,
    language: String
  }
}
```

**User Collection:**
```javascript
{
  _id: ObjectId,
  tenant_id: ObjectId,
  email: String,
  password_hash: String,
  first_name: String,
  last_name: String,
  phone: String,
  role_id: ObjectId,
  status: String, // 'active', 'inactive', 'suspended'
  mfa_enabled: Boolean,
  mfa_method: String, // 'totp', 'sms'
  created_at: Date,
  updated_at: Date,
  last_login: Date
}
```

**Appointment Collection:**
```javascript
{
  _id: ObjectId,
  tenant_id: ObjectId,
  customer_id: ObjectId,
  staff_id: ObjectId,
  service_id: ObjectId,
  location_id: ObjectId,
  start_time: Date,
  end_time: Date,
  status: String, // 'scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show'
  notes: String,
  cancellation_reason: String || null,
  no_show_reason: String || null,
  created_at: Date,
  updated_at: Date
}
```

**Invoice Collection:**
```javascript
{
  _id: ObjectId,
  tenant_id: ObjectId,
  appointment_id: ObjectId || null,
  customer_id: ObjectId,
  amount: Number,
  tax: Number,
  discount: Number,
  total: Number,
  status: String, // 'draft', 'sent', 'paid', 'overdue', 'cancelled'
  due_date: Date,
  paid_at: Date || null,
  created_at: Date,
  updated_at: Date
}
```


## 3. Frontend Architecture

### Project Structure

The frontend is built with React 19.2.0, TypeScript 5.9.3, and Vite 7.3.1. The project structure follows a modular, scalable approach:

```
salon/
├── src/
│   ├── components/
│   │   ├── icons/
│   │   │   └── index.tsx (100+ custom SVG icons)
│   │   └── ui/ (35+ production-ready components)
│   ├── lib/
│   │   ├── themes/ (3 themes × 2 modes)
│   │   ├── utils/ (utilities - to be created)
│   │   └── hooks/ (custom hooks - to be created)
│   ├── stores/ (Zustand stores - to be created)
│   ├── services/ (API client - to be created)
│   ├── pages/ (feature pages - to be created)
│   ├── layouts/ (page layouts - to be created)
│   ├── App.tsx (main app component)
│   ├── main.tsx (entry point)
│   └── index.css (global styles + mobile optimizations)
├── public/
├── vite.config.ts (Vite + Tailwind CSS configured)
├── tsconfig.json (TypeScript strict mode)
├── package.json (React 19.2.0, TypeScript 5.9.3)
└── eslint.config.js (ESLint configured)
```

### UI Component Library (35+ Components)

**Form Components (10):**
- Button (8 variants: primary, secondary, accent, outline, ghost, link, destructive, success, warning)
- Input (text input with variants)
- Textarea (multi-line text)
- Select (dropdown)
- Checkbox (checkbox input)
- Radio (radio button)
- RadioGroup (radio group container)
- Switch (toggle switch)
- Label (form label)
- Slider (range slider)

**Display Components (10):**
- Card (4 variants: default, elevated, outlined, muted, gradient)
- Badge (tag/badge)
- Avatar (user avatar with fallback)
- Spinner (loading spinner)
- Skeleton (skeleton loader)
- Progress (progress bar)
- Alert (alert message)
- Toast (toast notification)
- Divider (divider)
- Separator (visual separator)

**Dialog Components (4):**
- Modal (full-featured modal with overlay)
- Dialog (dialog component)
- ConfirmationModal (confirmation dialog)
- MobileModal (mobile-optimized bottom sheet)

**Navigation Components (3):**
- Dropdown (dropdown menu)
- Tabs (tab navigation)
- Tooltip (tooltip)

**Advanced Components (8):**
- Calendar (calendar picker)
- Table (data table)
- ScrollArea (scrollable area)
- ErrorBoundary (error boundary)
- LazyLoad (lazy loading wrapper)
- ImageLightbox (image lightbox)
- ServiceDetailsSkeleton (service skeleton)
- ThemeSelector (theme switcher)

### Icon System (100+ SVG Icons)

**Categories:**
- Navigation (Menu, Chevrons, Arrows, Home, LogOut)
- UI (Check, X, Plus, Minus, Edit, Trash, Eye, Copy, Share, Download, Upload)
- Business (Calendar, Clock, User, Users, Building, MapPin, Phone, Mail, CreditCard)
- Services (Scissors, Sparkles, Heart, Trophy, Gift, Package, ShoppingCart)
- Status (CheckCircle, XCircle, AlertTriangle, AlertCircle, Info, Activity)
- Finance (Dollar, Wallet, Bank, Receipt, Refund, Percent)
- Analytics (Chart, BarChart, TrendingUp, TrendingDown)
- Media (Image, Camera, Printer, QrCode, Scan)
- Communication (Bell, Mail, MessageSquare, Send, Mic)
- Settings (Settings, Lock, Shield, Languages, Keyboard, Monitor)
- Salon-Specific (Chair, AC, Coffee, Wifi, Parking, Wheelchair, Cake)
- Theme (Sun, Moon, Star, Lightbulb)
- File (File, FileText, Archive, ClipboardList)
- Loading (Loader2, RefreshCw, RefreshCcw)

### Theme System

**3 Complete Themes:**
1. **Default Theme** - Clean, professional, neutral colors
2. **Elegant Theme** - Sophisticated, premium feel
3. **Vibrant Theme** - Bold, energetic colors

**Each Theme Includes:**
- Light mode colors
- Dark mode colors
- Full color palette (primary, secondary, accent, destructive, success, warning, info, muted)
- Radius definitions (sm, md, lg, xl, full)
- Shadow definitions (sm, md, lg, xl)
- Typography (font families, sizes, weights)

**Theme Features:**
- CSS variable-based system for dynamic switching
- Automatic dark mode detection
- Per-component customization
- Smooth theme transitions

### Mobile Optimization

**Touch-Friendly Design:**
- 44px minimum tap targets for all interactive elements
- Mobile-optimized modals (bottom sheet style)
- Swipeable calendar support
- Responsive grid layouts
- Safe area insets for notched devices

**Performance:**
- Smooth scrolling (-webkit-overflow-scrolling)
- GPU acceleration for animations
- Reduced motion support (@prefers-reduced-motion)
- Lazy loading for images and components

**Responsive Breakpoints:**
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Accessibility Features

**WCAG 2.1 AA Compliance:**
- Focus visible states on all interactive elements
- ARIA labels and roles
- Semantic HTML structure
- Keyboard navigation support
- Color contrast compliance
- Reduced motion preferences
- Screen reader support

### State Management (To Be Implemented)

**Zustand Stores:**
- Auth store (user, token, permissions)
- Tenant store (current tenant, settings)
- UI store (theme, modals, notifications)
- User preferences store (language, timezone, etc.)

### Data Fetching (To Be Implemented)

**React Query Setup:**
- Query client configuration
- API hooks for all resources
- Automatic caching and synchronization
- Background refetching
- Optimistic updates
- Pagination and infinite queries

### Real-Time Communication (To Be Implemented)

**Socket.io Integration:**
- Real-time appointment updates
- Live notifications
- Presence tracking
- Automatic reconnection
- Fallback to polling

### Utility Functions (To Be Created)

- `cn()` - Class name merger (Tailwind CSS utilities)
- Date utilities (format, parse, calculate)
- Format utilities (currency, phone, etc.)
- Validation utilities (email, phone, etc.)
- API client with Axios (request/response interceptors)


## 4. API Design

### RESTful API Structure

**Base URL:** `https://api.platform.com/v1`

**Resource Endpoints:**
```
/tenants/{tenantId}/appointments
/tenants/{tenantId}/customers
/tenants/{tenantId}/staff
/tenants/{tenantId}/services
/tenants/{tenantId}/invoices
/tenants/{tenantId}/inventory
/tenants/{tenantId}/locations
/tenants/{tenantId}/reports
```

**Standard HTTP Methods:**
- `GET /resource` - List resources
- `GET /resource/{id}` - Get single resource
- `POST /resource` - Create resource
- `PUT /resource/{id}` - Update resource
- `DELETE /resource/{id}` - Delete resource
- `PATCH /resource/{id}` - Partial update

### Authentication and Authorization Flow

**OAuth 2.0 with JWT:**
1. User submits credentials to `/auth/login`
2. Server validates credentials and returns JWT token
3. Client includes token in `Authorization: Bearer {token}` header
4. Server validates token and extracts tenant_id and user_id
5. Request proceeds with tenant context

**Token Structure:**
```json
{
  "sub": "user_id",
  "tenant_id": "tenant_id",
  "role": "manager",
  "permissions": ["appointments:read", "appointments:write"],
  "iat": 1234567890,
  "exp": 1234571490
}
```

**MFA Flow:**
1. User submits credentials
2. Server returns temporary token requiring MFA
3. User submits MFA code
4. Server validates code and returns full JWT token

### Rate Limiting and Throttling

**Rate Limits:**
- 100 requests/minute per user
- 1000 requests/minute per tenant
- 10,000 requests/minute per API key

**Throttling Strategy:**
- Token bucket algorithm
- Exponential backoff for retries
- 429 Too Many Requests response with Retry-After header

### Error Handling and Status Codes

**Standard Response Format:**
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

**Error Response Format:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

**HTTP Status Codes:**
- 200 OK - Successful request
- 201 Created - Resource created
- 204 No Content - Successful deletion
- 400 Bad Request - Invalid input
- 401 Unauthorized - Missing/invalid authentication
- 403 Forbidden - Insufficient permissions
- 404 Not Found - Resource not found
- 409 Conflict - Resource conflict (e.g., double-booking)
- 429 Too Many Requests - Rate limit exceeded
- 500 Internal Server Error - Server error
- 503 Service Unavailable - Maintenance/overload

### API Versioning Strategy

**URL-Based Versioning:**
- `/v1/` - Current stable version
- `/v2/` - Next major version (in development)
- Deprecation: 12-month notice before removing old versions

**Backward Compatibility:**
- New fields added with defaults
- Old fields maintained for compatibility
- Deprecation headers in responses

### Webhook Support for Integrations

**Webhook Events:**
- `appointment.created`
- `appointment.updated`
- `appointment.cancelled`
- `payment.completed`
- `payment.failed`
- `customer.created`
- `staff.created`

**Webhook Delivery:**
- HTTPS POST to registered URL
- Retry up to 3 times with exponential backoff
- Signature verification using HMAC-SHA256
- Delivery tracking and status dashboard

**Webhook Payload:**
```json
{
  "id": "webhook_id",
  "event": "appointment.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": { ... },
  "signature": "sha256=..."
}
```


## 4. Integration Architecture

### Third-Party Integration Patterns

**Payment Gateways (Stripe, Square, PayPal):**
- Tokenization for secure payment processing
- Webhook handling for payment status updates
- Reconciliation with invoices
- Refund processing through gateway

**SMS Provider (Twilio):**
- Queue-based SMS sending
- Delivery tracking
- Opt-out management
- Cost tracking per tenant

**Email Provider (SendGrid, Mailgun):**
- Template-based email sending
- Delivery tracking and bounce handling
- Unsubscribe management
- Analytics tracking

**Calendar Sync (Google, Outlook):**
- OAuth 2.0 authentication
- Bidirectional sync of appointments
- Conflict resolution
- Timezone handling

**Accounting Software (QuickBooks, Xero):**
- Invoice sync
- Expense tracking
- Financial reconciliation
- Tax reporting

**Social Media (Facebook, Instagram):**
- Post scheduling
- Analytics tracking
- Lead capture
- Review monitoring

**Review Platforms (Google, Yelp):**
- Review monitoring
- Response management
- Rating aggregation
- Reputation tracking

### Webhook Handling

**Webhook Processing:**
1. Receive webhook from third-party service
2. Verify signature using shared secret
3. Queue webhook for processing
4. Process asynchronously to prevent blocking
5. Update system state based on webhook data
6. Send acknowledgment to third-party service

**Error Handling:**
- Retry failed webhooks up to 3 times
- Exponential backoff (1 min, 5 min, 15 min)
- Dead letter queue for permanently failed webhooks
- Alert on repeated failures

### Data Synchronization Strategy

**Appointment Sync with Calendar:**
- Bidirectional sync every 5 minutes
- Conflict resolution: local changes take precedence
- Timezone conversion for different calendar systems
- Soft delete handling (mark as cancelled instead of deleting)

**Financial Sync with Accounting Software:**
- Daily sync of invoices and payments
- Reconciliation of amounts
- Tax calculation sync
- Expense categorization

### Error Handling and Retry Logic

**Retry Strategy:**
- Exponential backoff: 1s, 2s, 4s, 8s, 16s
- Maximum 5 retries
- Circuit breaker pattern for failing services
- Fallback to cached data if available

**Error Logging:**
- Log all integration errors with context
- Alert on repeated failures
- Manual intervention queue for critical failures

### Integration Monitoring and Alerting

**Metrics to Track:**
- Integration success rate
- Average response time
- Error rate by integration
- Data sync lag

**Alerts:**
- Integration failure (immediate)
- High error rate (>5% in 5 minutes)
- Sync lag >1 hour
- API quota exceeded


## 5. Security Architecture

### Authentication and Authorization

**Authentication Methods:**
- Email/password with Bcrypt hashing (salt rounds ≥12); minimum 8 characters with complexity requirements
- OAuth 2.0 for third-party integrations
- API keys for service-to-service communication
- Multi-factor authentication (TOTP, SMS)

**Authorization Model:**
- Role-Based Access Control (RBAC)
- Resource-level permissions
- Attribute-Based Access Control (ABAC) for complex rules
- Permission caching with 5-minute TTL

**Session Management:**
- JWT tokens with 24-hour expiration
- Refresh tokens with 30-day expiration
- Session tracking and management
- Concurrent session limits (5 per user)

### Data Encryption

**At Rest:**
- AES-256 encryption for sensitive data
- Tenant-specific encryption keys
- Encrypted backups
- Key rotation every 90 days

**In Transit:**
- TLS 1.3 for all connections
- Certificate pinning for mobile apps
- HTTPS enforcement with HSTS headers
- Encrypted database connections

### API Security

**Request Validation:**
- Input validation on all endpoints
- Rate limiting (100 req/min per user)
- CORS policy enforcement
- CSRF token validation

**Response Security:**
- No sensitive data in error messages
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- Content Security Policy (CSP)
- Secure cookie flags (HttpOnly, Secure, SameSite)

### Audit Logging

**Logged Events:**
- User authentication (login, logout, MFA)
- Data access (read, write, delete)
- Permission changes
- Configuration changes
- API key usage
- Integration events

**Audit Log Storage:**
- Immutable append-only log
- Encrypted storage
- 7-year retention for compliance
- Tamper detection

### Compliance Controls

**GDPR:**
- Data portability (export in standard format)
- Right to be forgotten (secure deletion)
- Consent management
- Data processing agreements
- Privacy by design

**HIPAA (if storing health data):**
- Encryption at rest and in transit
- Access controls and audit logging
- Business associate agreements
- Breach notification procedures
- Minimum necessary principle

**PCI-DSS (if storing payment data):**
- Never store full credit card numbers
- Tokenization for payment processing
- Secure key management
- Regular security assessments
- Compliance certification

**SOC 2:**
- Access controls
- Audit logging
- Data encryption
- Incident response procedures
- Change management

### Incident Response Procedures

**Incident Response Plan:**
1. Detection and alerting
2. Containment (isolate affected systems)
3. Investigation (determine scope and impact)
4. Remediation (fix the issue)
5. Recovery (restore normal operations)
6. Post-incident review (lessons learned)

**Communication:**
- Notify affected customers within 24 hours
- Provide regular updates during incident
- Post-incident report within 7 days
- Regulatory notification if required


## 6. Performance Architecture

### Caching Strategy

**Redis Cache Layers:**
- Session cache (24-hour TTL)
- Permission cache (5-minute TTL)
- Appointment availability cache (1-minute TTL)
- Customer profile cache (10-minute TTL)
- Service catalog cache (1-hour TTL)

**Cache Invalidation:**
- Time-based expiration (TTL)
- Event-based invalidation (on data changes)
- Manual invalidation for critical updates
- Cache warming on startup

**CDN for Static Assets:**
- CloudFront, Cloudflare, or Akamai
- Cache static assets (JS, CSS, images)
- 1-hour TTL for versioned assets
- Automatic cache invalidation on deployment

### Database Query Optimization

**Query Optimization Techniques:**
- Proper indexing on frequently queried columns
- Query analysis and optimization
- Connection pooling (PgBouncer)
- Read replicas for reporting queries
- Materialized views for complex aggregations

**N+1 Query Prevention:**
- Eager loading of related data
- Batch queries for multiple records
- GraphQL for flexible data fetching

**Slow Query Monitoring:**
- Log queries >100ms
- Alert on queries >1 second
- Regular query analysis and optimization

### Asynchronous Processing

**Message Queue (RabbitMQ/SQS):**
- Appointment reminders
- Email/SMS sending
- Invoice generation
- Report generation
- Integration webhooks
- Data exports

**Worker Processes:**
- Multiple workers for parallel processing
- Dead letter queue for failed messages
- Retry logic with exponential backoff
- Monitoring and alerting

### Real-Time Updates

**WebSocket Implementation:**
- Real-time appointment updates
- Live calendar synchronization
- Instant notification delivery
- Presence tracking (who's online)

**WebSocket Architecture:**
- Connection pooling
- Message broadcasting
- Graceful disconnection handling
- Automatic reconnection

### Monitoring and Alerting

**Metrics to Track:**
- API response time (p50, p95, p99)
- Database query time
- Cache hit rate
- Error rate
- Throughput (requests/second)
- Resource utilization (CPU, memory, disk)

**Monitoring Tools:**
- Prometheus for metrics collection
- Grafana for visualization
- DataDog or New Relic for APM
- CloudWatch for infrastructure metrics

**Alerting Rules:**
- Response time >500ms (p95)
- Error rate >1%
- Cache hit rate <80%
- Database connection pool >80% utilized
- Disk usage >80%
- Memory usage >85%


## 7. Data Models (Detailed)

### Phase 1 - MVP Core Entities

**Tenant Entity:**
- ID (UUID, primary key)
- Name (string, 255 chars)
- Subscription tier (enum: starter/professional/enterprise)
- Status (enum: active/suspended/deleted)
- Region (string for data residency)
- Created at (timestamp)
- Updated at (timestamp)
- Deleted at (timestamp, nullable)

**User Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Email (string, unique per tenant)
- Password hash (string, Bcrypt)
- First name (string)
- Last name (string)
- Role ID (UUID, foreign key)
- Status (enum: active/inactive/suspended)
- MFA enabled (boolean)
- MFA method (enum: totp/sms)
- Created at (timestamp)
- Updated at (timestamp)
- Last login (timestamp)

**Role Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Name (string)
- Description (text)
- Permissions (JSON array)
- Is custom (boolean)
- Created at (timestamp)

**Staff Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- User ID (UUID, foreign key)
- First name (string)
- Last name (string)
- Email (string)
- Phone (string)
- Specialties (JSON array)
- Certifications (JSON array)
- Hourly rate (decimal)
- Hire date (date)
- Status (enum: active/inactive/terminated)
- Created at (timestamp)
- Updated at (timestamp)

**Customer Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- User ID (UUID, foreign key, nullable)
- Phone (string)
- Date of birth (date, nullable)
- Address (string)
- City (string)
- State (string)
- Zip code (string)
- Medical info (text, encrypted)
- Allergy info (text, encrypted)
- Emergency contact (string)
- Created at (timestamp)
- Updated at (timestamp)

**Service Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Name (string)
- Description (text)
- Duration minutes (integer)
- Price (decimal)
- Category (string)
- Is active (boolean)
- Requires deposit (boolean)
- Deposit amount (decimal)
- Created at (timestamp)
- Updated at (timestamp)

**Appointment Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Customer ID (UUID, foreign key)
- Staff ID (UUID, foreign key)
- Service ID (UUID, foreign key)
- Location ID (UUID, foreign key)
- Start time (timestamp)
- End time (timestamp)
- Status (enum: scheduled/confirmed/in_progress/completed/cancelled/no_show)
- Notes (text)
- Cancellation reason (string, nullable)
- No show reason (string, nullable)
- Created at (timestamp)
- Updated at (timestamp)

**Invoice Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Appointment ID (UUID, foreign key, nullable)
- Customer ID (UUID, foreign key)
- Amount (decimal)
- Tax (decimal)
- Discount (decimal)
- Total (decimal)
- Status (enum: draft/sent/paid/overdue/cancelled)
- Due date (date)
- Paid at (timestamp, nullable)
- Created at (timestamp)
- Updated at (timestamp)

**Payment Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Invoice ID (UUID, foreign key)
- Amount (decimal)
- Method (enum: credit_card/debit_card/digital_wallet)
- Status (enum: pending/processing/completed/failed/refunded)
- Transaction ID (string)
- Gateway response (JSON)
- Created at (timestamp)
- Completed at (timestamp, nullable)

**Availability Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Staff ID (UUID, foreign key)
- Day of week (enum: 0-6)
- Start time (time)
- End time (time)
- Is recurring (boolean)
- Effective from (date)
- Effective to (date, nullable)

**Resource Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Name (string)
- Type (enum: room/chair/equipment/tool)
- Location ID (UUID, foreign key)
- Capacity (integer)
- Status (enum: available/maintenance/retired)
- Created at (timestamp)
- Updated at (timestamp)

**Inventory Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Name (string)
- SKU (string)
- Category (string)
- Quantity (integer)
- Reorder level (integer)
- Unit cost (decimal)
- Supplier ID (UUID, foreign key)
- Created at (timestamp)
- Updated at (timestamp)

### Phase 2 - Operations & Financial Entities

**Expense Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Category (string)
- Amount (decimal)
- Description (text)
- Date (date)
- Vendor (string)
- Receipt URL (string, nullable)
- Created at (timestamp)

**Shift Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Staff ID (UUID, foreign key)
- Start time (timestamp)
- End time (timestamp)
- Shift type (enum: regular/overtime/on_call)
- Status (enum: scheduled/confirmed/completed/cancelled)
- Notes (text)
- Created at (timestamp)

**TimeOffRequest Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Staff ID (UUID, foreign key)
- Start date (date)
- End date (date)
- Reason (string)
- Status (enum: pending/approved/denied)
- Requested at (timestamp)
- Approved by (UUID, foreign key)
- Approval date (date, nullable)

### Phase 3 - Customer Engagement Entities

**Promotion Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Name (string)
- Type (enum: birthday/anniversary/seasonal/referral)
- Discount type (enum: percentage/fixed)
- Discount value (decimal)
- Start date (date)
- End date (date)
- Status (enum: active/inactive)
- Created at (timestamp)

**CustomerSegment Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Name (string)
- Criteria (JSON)
- Customer count (integer)
- Created at (timestamp)

**Membership Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Customer ID (UUID, foreign key)
- Type (string)
- Start date (date)
- End date (date)
- Status (enum: active/expired/cancelled)
- Credits remaining (integer)
- Created at (timestamp)

**Review Entity:**
- ID (UUID, primary key)
- Tenant ID (UUID, foreign key)
- Customer ID (UUID, foreign key)
- Rating (integer, 1-5)
- Comment (text)
- Platform (enum: google/yelp/facebook/internal)
- Status (enum: pending/approved/rejected)
- Created at (timestamp)


## 8. API Endpoints (by Feature)

### Appointment Management

**List Appointments:**
```
GET /tenants/{tenantId}/appointments
Query params: start_date, end_date, staff_id, customer_id, status
Response: Array of appointments with pagination
```

**Get Appointment:**
```
GET /tenants/{tenantId}/appointments/{appointmentId}
Response: Single appointment with full details
```

**Create Appointment:**
```
POST /tenants/{tenantId}/appointments
Body: {
  customer_id, staff_id, service_id, start_time, end_time, notes
}
Response: Created appointment with ID
```

**Update Appointment:**
```
PUT /tenants/{tenantId}/appointments/{appointmentId}
Body: {
  status, notes, start_time, end_time
}
Response: Updated appointment
```

**Cancel Appointment:**
```
DELETE /tenants/{tenantId}/appointments/{appointmentId}
Body: { reason }
Response: Cancelled appointment
```

**Get Available Slots:**
```
GET /tenants/{tenantId}/appointments/availability
Query params: staff_id, service_id, date, duration
Response: Array of available time slots
```

### Customer Management

**List Customers:**
```
GET /tenants/{tenantId}/customers
Query params: search, status, segment_id
Response: Array of customers with pagination
```

**Get Customer:**
```
GET /tenants/{tenantId}/customers/{customerId}
Response: Customer profile with history
```

**Create Customer:**
```
POST /tenants/{tenantId}/customers
Body: {
  email, phone, first_name, last_name, preferences, medical_info
}
Response: Created customer
```

**Update Customer:**
```
PUT /tenants/{tenantId}/customers/{customerId}
Body: { phone, preferences, medical_info, allergy_info }
Response: Updated customer
```

**Get Customer History:**
```
GET /tenants/{tenantId}/customers/{customerId}/history
Response: Array of past appointments and services
```

### Staff Management

**List Staff:**
```
GET /tenants/{tenantId}/staff
Query params: status, specialty
Response: Array of staff members
```

**Get Staff:**
```
GET /tenants/{tenantId}/staff/{staffId}
Response: Staff profile with schedule
```

**Create Staff:**
```
POST /tenants/{tenantId}/staff
Body: {
  user_id, specialties, certifications, hourly_rate
}
Response: Created staff member
```

**Update Staff:**
```
PUT /tenants/{tenantId}/staff/{staffId}
Body: { specialties, certifications, hourly_rate, status }
Response: Updated staff member
```

**Get Staff Schedule:**
```
GET /tenants/{tenantId}/staff/{staffId}/schedule
Query params: start_date, end_date
Response: Array of shifts and appointments
```

### Billing & Payments

**List Invoices:**
```
GET /tenants/{tenantId}/invoices
Query params: status, customer_id, date_range
Response: Array of invoices
```

**Get Invoice:**
```
GET /tenants/{tenantId}/invoices/{invoiceId}
Response: Invoice with line items
```

**Create Invoice:**
```
POST /tenants/{tenantId}/invoices
Body: {
  appointment_id, customer_id, amount, tax, discount
}
Response: Created invoice
```

**Process Payment:**
```
POST /tenants/{tenantId}/invoices/{invoiceId}/pay
Body: {
  amount, method, payment_token
}
Response: Payment confirmation
```

**Refund Payment:**
```
POST /tenants/{tenantId}/payments/{paymentId}/refund
Body: { amount, reason }
Response: Refund confirmation
```

### Notifications

**Send Notification:**
```
POST /tenants/{tenantId}/notifications
Body: {
  recipient_id, type, channel, content
}
Response: Notification ID
```

**Get Notification Status:**
```
GET /tenants/{tenantId}/notifications/{notificationId}
Response: Notification with delivery status
```

**Update Preferences:**
```
PUT /tenants/{tenantId}/customers/{customerId}/notification-preferences
Body: {
  notification_type, channel, enabled
}
Response: Updated preferences
```

### Inventory Management

**List Inventory:**
```
GET /tenants/{tenantId}/inventory
Query params: category, low_stock
Response: Array of inventory items
```

**Get Inventory Item:**
```
GET /tenants/{tenantId}/inventory/{itemId}
Response: Inventory item with stock levels
```

**Update Stock:**
```
PUT /tenants/{tenantId}/inventory/{itemId}
Body: { quantity, reorder_level }
Response: Updated inventory
```

**Create Purchase Order:**
```
POST /tenants/{tenantId}/inventory/purchase-orders
Body: {
  supplier_id, items, delivery_date
}
Response: Created purchase order
```

### Reports & Analytics

**Revenue Report:**
```
GET /tenants/{tenantId}/reports/revenue
Query params: start_date, end_date, group_by
Response: Revenue data with breakdown
```

**Staff Performance:**
```
GET /tenants/{tenantId}/reports/staff-performance
Query params: staff_id, start_date, end_date
Response: Performance metrics
```

**Customer Analytics:**
```
GET /tenants/{tenantId}/reports/customers
Query params: metric (lifetime_value, churn, retention)
Response: Customer analytics
```

**No-Show Analysis:**
```
GET /tenants/{tenantId}/reports/no-shows
Query params: start_date, end_date
Response: No-show rate and trends
```


## 9. Integration Specifications

### Payment Gateway Integration (Stripe, Square, PayPal)

**Stripe Integration:**
- Create payment intent for each invoice
- Handle 3D Secure authentication
- Webhook handling for payment status updates
- Refund processing through Stripe API
- PCI-DSS compliance through tokenization

**Square Integration:**
- Square Payment Form for card entry
- Nonce-based payment processing
- Webhook handling for payment updates
- Inventory sync with Square
- Customer profile sync

**PayPal Integration:**
- PayPal Checkout integration
- Express Checkout for quick payments
- Webhook handling for payment status
- Refund processing through PayPal API

**Common Payment Flow:**
1. Create invoice in system
2. Generate payment token/intent
3. Send to payment gateway
4. Receive payment confirmation
5. Update invoice status
6. Send receipt to customer

### SMS Provider Integration (Twilio)

**Twilio Integration:**
- Send SMS notifications
- Receive SMS responses
- Track delivery status
- Handle opt-out requests
- Cost tracking per tenant

**SMS Flow:**
1. Queue SMS message
2. Send through Twilio API
3. Track delivery status
4. Handle failures with retry
5. Log for audit trail

### Email Provider Integration (SendGrid, Mailgun)

**SendGrid Integration:**
- Send transactional emails
- Template-based email sending
- Track opens and clicks
- Handle bounces
- Manage unsubscribe lists

**Mailgun Integration:**
- Send emails through Mailgun API
- Track delivery and opens
- Handle bounces and complaints
- Manage mailing lists

**Email Flow:**
1. Render email template with variables
2. Send through email provider
3. Track delivery status
4. Handle bounces
5. Log for audit trail

### Calendar Sync (Google, Outlook)

**Google Calendar Integration:**
- OAuth 2.0 authentication
- Bidirectional sync of appointments
- Conflict resolution
- Timezone handling
- Recurring appointment support

**Outlook Calendar Integration:**
- OAuth 2.0 authentication
- Sync appointments to Outlook
- Handle conflicts
- Timezone conversion

**Calendar Sync Flow:**
1. User authorizes calendar access
2. Fetch existing appointments
3. Sync new appointments
4. Handle conflicts (local takes precedence)
5. Periodic sync every 5 minutes

### Accounting Software (QuickBooks, Xero)

**QuickBooks Integration:**
- OAuth 2.0 authentication
- Sync invoices to QuickBooks
- Sync expenses
- Sync payments
- Tax category mapping

**Xero Integration:**
- OAuth 2.0 authentication
- Sync invoices
- Sync expenses
- Sync payments
- Tax code mapping

**Accounting Sync Flow:**
1. Authenticate with accounting software
2. Map chart of accounts
3. Sync invoices daily
4. Sync expenses daily
5. Reconcile payments
6. Handle sync errors

### Social Media Integration (Facebook, Instagram)

**Facebook Integration:**
- Post scheduling
- Lead capture from ads
- Review monitoring
- Analytics tracking

**Instagram Integration:**
- Post scheduling
- Story creation
- Analytics tracking
- Hashtag management

**Social Media Flow:**
1. Connect social media account
2. Schedule posts
3. Monitor engagement
4. Track leads
5. Analyze performance

### Review Platform Integration (Google, Yelp)

**Google Reviews Integration:**
- Monitor new reviews
- Respond to reviews
- Track rating changes
- Aggregate reviews

**Yelp Integration:**
- Monitor Yelp reviews
- Respond to reviews
- Track rating
- Manage business information

**Review Management Flow:**
1. Monitor for new reviews
2. Alert business owner
3. Enable response to reviews
4. Track response rate
5. Analyze sentiment


## 10. Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Data Isolation Properties

Property 1: No Cross-Tenant Data Leakage
*For any* two distinct tenants and any query executed as one tenant, the query results SHALL only include data belonging to that tenant and never include data from other tenants.
**Validates: Requirements 1.1, 1.2, 1.3**

Property 2: Tenant Deletion Completeness
*For any* tenant with associated data, after deletion, querying the system SHALL return no data belonging to that tenant.
**Validates: Requirements 1.4**

Property 3: User Access Control Enforcement
*For any* user attempting to access data from a different tenant, the system SHALL deny access and log the unauthorized attempt.
**Validates: Requirements 1.2, 2.4**

### Authentication & Authorization Properties

Property 4: Role-Based Access Control
*For any* user with a specific role, the user SHALL only be able to access features and data permitted by that role.
**Validates: Requirements 2.2, 2.3, 2.4, 2.5**

Property 5: Permission Consistency After Role Change
*For any* user whose role is changed, the user's permissions SHALL be immediately updated to match the new role.
**Validates: Requirements 2.6**

Property 6: Session Invalidation on Logout
*For any* user who logs out, their session token SHALL become invalid and subsequent requests with that token SHALL be rejected.
**Validates: Requirements 2.7**

Property 7: Authentication Token Validity
*For any* valid user credentials, authentication SHALL produce a valid JWT token that can be used for subsequent requests.
**Validates: Requirements 2.1**

### Appointment Booking Properties

Property 8: Double-Booking Prevention
*For any* staff member or resource, the system SHALL prevent booking overlapping appointments at the same time.
**Validates: Requirements 3.5, 8.2**

Property 9: Availability Calculation Accuracy
*For any* staff member with defined availability and services with specified durations, the system SHALL calculate available time slots that do not conflict with existing appointments or unavailable periods.
**Validates: Requirements 3.1, 3.4**

Property 10: Slot Reservation Consistency
*For any* customer who selects a time slot, that slot SHALL be reserved for 10 minutes and not available for other customers during that period.
**Validates: Requirements 3.2**

Property 11: Appointment Confirmation Notification
*For any* confirmed appointment, a confirmation notification SHALL be sent to the customer within 1 minute.
**Validates: Requirements 3.3, 7.1**

Property 12: Appointment Cancellation Slot Release
*For any* cancelled appointment, the time slot SHALL be immediately released and available for new bookings.
**Validates: Requirements 3.7**

### Staff Management Properties

Property 13: Staff Profile Data Completeness
*For any* staff member, the system SHALL store and retrieve all required profile information (name, contact, specialties, certifications, hourly rate).
**Validates: Requirements 4.1**

Property 14: Shift Conflict Detection
*For any* staff member, the system SHALL prevent assigning overlapping shifts.
**Validates: Requirements 4.3**

Property 15: Labor Cost Calculation Accuracy
*For any* shift, the system SHALL calculate labor cost as hourly_rate × (end_time - start_time) / 60.
**Validates: Requirements 4.6**

Property 16: Availability Update Propagation
*For any* change to staff availability, the change SHALL be immediately reflected in the customer booking interface.
**Validates: Requirements 4.7**

### Customer Profile Properties

Property 17: Customer History Completeness
*For any* customer, the system SHALL maintain a complete history of all appointments with dates, services, and staff information.
**Validates: Requirements 5.2**

Property 18: Preference Storage and Retrieval
*For any* customer preference update, the system SHALL store the preference and retrieve it correctly on subsequent requests.
**Validates: Requirements 5.3**

Property 19: Service Recommendation Accuracy
*For any* customer booking an appointment, the system SHALL suggest services based on their appointment history.
**Validates: Requirements 5.5**

Property 20: Data Access Audit Logging
*For any* access to customer data, the system SHALL create an audit log entry with user, timestamp, and action.
**Validates: Requirements 5.6, 41.1**

### Billing & Payment Properties

Property 21: Invoice Generation Accuracy
*For any* completed appointment, the system SHALL generate an invoice with correct amount = service_price - discount + tax.
**Validates: Requirements 6.1, 20.1**

Property 22: Payment Processing Idempotence
*For any* payment request, processing the same payment twice SHALL result in only one charge to the customer.
**Validates: Requirements 6.2**

Property 23: Payment Retry Logic
*For any* failed payment, the system SHALL retry up to 3 times with exponential backoff before notifying the customer.
**Validates: Requirements 6.3**

Property 24: Refund Amount Validation
*For any* refund request, the refund amount SHALL not exceed the original payment amount.
**Validates: Requirements 6.4**

Property 25: Financial Report Accuracy
*For any* financial report, total_revenue SHALL equal the sum of all completed appointment payments.
**Validates: Requirements 6.5, 19.1**

Property 26: Outstanding Balance Enforcement
*For any* customer with outstanding balance, the system SHALL prevent new appointment booking.
**Validates: Requirements 6.6**

Property 27: Payment Receipt Delivery
*For any* successful payment, a receipt notification SHALL be sent to the customer.
**Validates: Requirements 6.7, 7.6**

### Notification Properties

Property 28: Appointment Reminder Timing
*For any* appointment, reminder notifications SHALL be sent at 24 hours and 1 hour before the appointment time.
**Validates: Requirements 7.2, 13.1**

Property 29: Cancellation Notification Delivery
*For any* cancelled appointment, notifications SHALL be sent to both customer and staff.
**Validates: Requirements 7.3**

Property 30: Notification Retry on Failure
*For any* failed notification, the system SHALL retry up to 3 times before logging the failure.
**Validates: Requirements 7.7**

### Resource Management Properties

Property 31: Resource Conflict Prevention
*For any* resource, the system SHALL prevent assigning overlapping appointments to the same resource.
**Validates: Requirements 8.2**

Property 32: Maintenance Status Enforcement
*For any* resource marked as maintenance, the system SHALL prevent booking appointments requiring that resource.
**Validates: Requirements 8.3**

### Waiting Room Properties

Property 33: Queue Order Consistency
*For any* waiting room queue, customers SHALL be served in the order they checked in.
**Validates: Requirements 9.1, 9.2**

### Capacity Management Properties

Property 34: Capacity Limit Enforcement
*For any* service with defined capacity, the system SHALL prevent booking more appointments than the capacity allows.
**Validates: Requirements 11.1**

Property 35: Waitlist Management
*For any* appointment when capacity is reached, the customer SHALL be added to a waitlist and notified when space opens.
**Validates: Requirements 11.2**

### Service Dependencies Properties

Property 36: Dependency Enforcement
*For any* service with dependencies, the system SHALL prevent booking dependent services out of sequence.
**Validates: Requirements 12.1**

### Expense Tracking Properties

Property 37: Expense Categorization
*For any* recorded expense, the system SHALL categorize it and include it in financial reports.
**Validates: Requirements 15.1**

### Tax Reporting Properties

Property 38: Tax Calculation Accuracy
*For any* tax report, calculated_tax SHALL equal revenue × applicable_tax_rate.
**Validates: Requirements 16.1**

### Refund Policy Properties

Property 39: Refund Policy Enforcement
*For any* cancellation within the refund window, the system SHALL process a refund according to the defined policy.
**Validates: Requirements 17.1**

### Deposit Management Properties

Property 40: Deposit Application
*For any* customer deposit, the system SHALL hold it and apply it to future services.
**Validates: Requirements 18.1**

### Inventory Properties

Property 41: Inventory Deduction Accuracy
*For any* service using products, the system SHALL deduct the product quantity from inventory.
**Validates: Requirements 27.1**

Property 42: Stock Alert Triggering
*For any* inventory item, when quantity falls below reorder_level, the system SHALL alert the manager.
**Validates: Requirements 28.1**

Property 43: Inventory Reconciliation Accuracy
*For any* inventory reconciliation, the system SHALL identify discrepancies between physical count and system records.
**Validates: Requirements 30.1**

### Marketing Properties

Property 44: Birthday Promotion Delivery
*For any* customer with a birthday, the system SHALL send a birthday promotion on their birthday.
**Validates: Requirements 31.1**

Property 45: Referral Tracking Accuracy
*For any* referral, the system SHALL track the referrer and referee and apply rewards correctly.
**Validates: Requirements 32.1, 38.1**

Property 46: Customer Segmentation Accuracy
*For any* customer segment, all customers in the segment SHALL meet the segment criteria.
**Validates: Requirements 33.1**

Property 47: Membership Credit Tracking
*For any* membership purchase, the system SHALL track credits and enforce usage limits.
**Validates: Requirements 34.1**

### Compliance Properties

Property 48: Audit Trail Completeness
*For any* data access or modification, the system SHALL create an audit log entry with user, timestamp, and action.
**Validates: Requirements 41.1, 64.1**

Property 49: Backup Encryption
*For any* backup, the system SHALL encrypt the backup using AES-256 encryption.
**Validates: Requirements 42.1**

Property 50: Two-Factor Authentication Enforcement
*For any* user with 2FA enabled, the system SHALL require a second authentication factor.
**Validates: Requirements 43.1**

### Integration Properties

Property 51: Payment Gateway Compliance
*For any* payment processed, the system SHALL never store full credit card numbers and SHALL comply with PCI-DSS.
**Validates: Requirements 45.1**

Property 52: SMS Delivery Tracking
*For any* SMS sent, the system SHALL track delivery status through the SMS provider.
**Validates: Requirements 46.1**

Property 53: Calendar Sync Consistency
*For any* appointment synced with external calendar, the system SHALL maintain consistency between local and external calendars.
**Validates: Requirements 47.1**

Property 54: Accounting Software Sync Accuracy
*For any* financial data synced with accounting software, the system SHALL map data correctly and maintain accuracy.
**Validates: Requirements 48.1**

Property 55: Email Delivery Tracking
*For any* email sent, the system SHALL track delivery status through the email provider.
**Validates: Requirements 49.1**


## 11. Error Handling

### Error Categories

**Validation Errors (400):**
- Invalid input format
- Missing required fields
- Out-of-range values
- Constraint violations

**Authentication Errors (401):**
- Missing authentication token
- Invalid token
- Expired token
- Invalid credentials

**Authorization Errors (403):**
- Insufficient permissions
- Cross-tenant access attempt
- Resource access denied

**Not Found Errors (404):**
- Resource not found
- Endpoint not found

**Conflict Errors (409):**
- Double-booking conflict
- Duplicate resource
- State conflict

**Rate Limit Errors (429):**
- Too many requests
- Quota exceeded

**Server Errors (500):**
- Unexpected error
- Database error
- Integration error

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_FORMAT"
      }
    ],
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456"
  }
}
```

### Error Handling Strategy

**Client-Side:**
- Validate input before sending
- Display user-friendly error messages
- Retry on transient errors
- Implement exponential backoff

**Server-Side:**
- Validate all input
- Log errors with context
- Return appropriate status codes
- Provide actionable error messages
- Never expose sensitive information

**Integration Errors:**
- Retry with exponential backoff
- Fall back to cached data if available
- Alert on repeated failures
- Queue for manual review

## 12. Testing Strategy

### Dual Testing Approach

The platform uses both unit testing and property-based testing to ensure comprehensive coverage:

**Unit Tests:**
- Specific examples and edge cases
- Integration points between components
- Error conditions and boundary cases
- Concrete scenarios with known inputs/outputs

**Property-Based Tests:**
- Universal properties across all inputs
- Comprehensive input coverage through randomization
- Invariants that must hold for all valid data
- Round-trip properties for serialization/deserialization

### Property-Based Testing Configuration

**Testing Framework:**
- JavaScript/TypeScript: fast-check
- Python: Hypothesis
- Java: QuickCheck or jqwik

**Test Configuration:**
- Minimum 100 iterations per property test
- Seed-based reproducibility for failures
- Shrinking to find minimal failing examples
- Timeout: 30 seconds per test

**Test Tagging:**
Each property test includes a comment with:
```
Feature: salon-spa-gym-saas, Property N: [Property Title]
Validates: Requirements X.Y, X.Z
```

### Unit Test Examples

**Appointment Booking:**
- Book appointment with valid data
- Attempt to book overlapping appointment
- Book appointment with invalid staff
- Book appointment in the past
- Book appointment beyond advance booking limit

**Payment Processing:**
- Process payment with valid card
- Process payment with invalid card
- Process payment with insufficient funds
- Refund payment
- Refund more than original payment

**Inventory Management:**
- Add inventory item
- Deduct inventory on service
- Alert when stock below reorder level
- Reconcile inventory discrepancies

### Property Test Examples

**Property 1: Double-Booking Prevention**
```javascript
// Feature: salon-spa-gym-saas, Property 8: Double-Booking Prevention
// Validates: Requirements 3.5, 8.2

fc.assert(
  fc.property(
    fc.uuid(),
    fc.date(),
    fc.integer({ min: 30, max: 480 }),
    (staffId, date, durationMinutes) => {
      const appointment1 = createAppointment(staffId, date, durationMinutes);
      const appointment2 = createAppointment(staffId, date, durationMinutes);
      
      expect(appointment2).toThrow('Double-booking conflict');
    }
  ),
  { numRuns: 100 }
);
```

**Property 2: Invoice Accuracy**
```javascript
// Feature: salon-spa-gym-saas, Property 21: Invoice Generation Accuracy
// Validates: Requirements 6.1, 20.1

fc.assert(
  fc.property(
    fc.integer({ min: 1000, max: 100000 }),
    fc.integer({ min: 0, max: 5000 }),
    fc.integer({ min: 0, max: 2000 }),
    (servicePrice, discount, tax) => {
      const invoice = generateInvoice(servicePrice, discount, tax);
      const expectedTotal = servicePrice - discount + tax;
      
      expect(invoice.total).toBe(expectedTotal);
    }
  ),
  { numRuns: 100 }
);
```

**Property 3: Tenant Isolation**
```javascript
// Feature: salon-spa-gym-saas, Property 1: No Cross-Tenant Data Leakage
// Validates: Requirements 1.1, 1.2, 1.3

fc.assert(
  fc.property(
    fc.uuid(),
    fc.uuid(),
    fc.array(fc.object()),
    (tenant1Id, tenant2Id, data) => {
      createTenant(tenant1Id);
      createTenant(tenant2Id);
      
      insertData(tenant1Id, data);
      
      const results = queryData(tenant2Id);
      
      expect(results).toHaveLength(0);
    }
  ),
  { numRuns: 100 }
);
```

### Test Coverage Goals

- Unit test coverage: >80%
- Property test coverage: All critical properties
- Integration test coverage: Key workflows
- End-to-end test coverage: Happy paths and error scenarios

### Continuous Testing

- Run tests on every commit
- Run full test suite before deployment
- Monitor test performance
- Alert on test failures
- Track coverage trends

## 13. Deployment Architecture

### Infrastructure as Code

**Technology:**
- Terraform for infrastructure provisioning
- Docker for containerization
- Kubernetes for orchestration

**Version Control:**
- Infrastructure code in Git
- Code review process for changes
- Automated testing of infrastructure changes

### CI/CD Pipeline

**Build Stage:**
- Compile code
- Run linters
- Run unit tests
- Build Docker image
- Push to container registry

**Test Stage:**
- Run integration tests
- Run property-based tests
- Run security scans
- Run performance tests

**Deploy Stage:**
- Deploy to staging environment
- Run smoke tests
- Deploy to production
- Monitor for errors

### Environment Strategy

**Development:**
- Local development environment
- Docker Compose for local services
- Seed data for testing

**Staging:**
- Mirror of production environment
- Full test suite runs
- Performance testing
- Security testing

**Production:**
- High-availability setup
- Load balancing
- Database replication
- CDN for static assets

### Database Migration Strategy

**Migration Process:**
1. Create migration script
2. Test on staging environment
3. Schedule maintenance window
4. Run migration on production
5. Verify data integrity
6. Monitor for issues

**Rollback Procedures:**
- Keep previous database backup
- Document rollback steps
- Test rollback procedure
- Execute rollback if needed

## 14. Monitoring and Observability

### Metrics to Track

**Performance Metrics:**
- API response time (p50, p95, p99)
- Database query time
- Cache hit rate
- Throughput (requests/second)

**Business Metrics:**
- Revenue
- No-show rate
- Customer satisfaction
- Staff utilization

**Compliance Metrics:**
- Audit log entries
- Data access events
- Security incidents
- Backup success rate

### Logging Strategy

**Log Levels:**
- ERROR: Errors that need immediate attention
- WARN: Warnings that should be investigated
- INFO: General informational messages
- DEBUG: Detailed debugging information

**Log Aggregation:**
- Centralized logging (ELK Stack, CloudWatch)
- Structured logging (JSON format)
- Log retention: 90 days
- Searchable and filterable

### Alerting Rules

**Critical Alerts:**
- API error rate >5%
- Database connection pool >90% utilized
- Disk usage >90%
- Backup failure

**Warning Alerts:**
- API response time p95 >500ms
- Cache hit rate <80%
- Memory usage >85%
- Integration failure

### Dashboards

**Operations Dashboard:**
- System health overview
- Error rates and trends
- Performance metrics
- Active alerts

**Business Dashboard:**
- Revenue and bookings
- Customer metrics
- Staff utilization
- No-show rates

**Security Dashboard:**
- Failed login attempts
- Unauthorized access attempts
- Data access patterns
- Compliance status

### Incident Response Procedures

**Detection:**
- Automated alerting
- Manual monitoring
- Customer reports

**Response:**
1. Acknowledge incident
2. Assess severity
3. Engage on-call team
4. Investigate root cause
5. Implement fix
6. Deploy fix
7. Monitor for stability
8. Post-incident review


## 15. Scalability and Performance Optimization

### Horizontal Scaling Strategy

**Application Servers:**
- Stateless application servers behind load balancer
- Auto-scaling based on CPU and memory usage
- Minimum 2 instances for high availability
- Maximum instances based on cost constraints

**Load Balancing:**
- Round-robin load balancing
- Health checks every 10 seconds
- Connection draining on shutdown
- Session affinity for WebSocket connections

**Database Connection Pooling:**
- PgBouncer for connection pooling
- Pool size: 20-50 connections per application instance
- Connection timeout: 30 seconds
- Idle connection timeout: 5 minutes

### Database Sharding Approach

**Sharding Strategy (for >10,000 tenants):**
- Shard by tenant_id
- Consistent hashing for shard assignment
- 10-20 shards initially
- Add shards as needed

**Shard Management:**
- Shard directory service
- Automatic shard discovery
- Shard rebalancing procedures
- Backup per shard

### Caching Layers

**Redis Cache:**
- Session cache (24-hour TTL)
- Permission cache (5-minute TTL)
- Appointment availability cache (1-minute TTL)
- Customer profile cache (10-minute TTL)
- Service catalog cache (1-hour TTL)

**Cache Invalidation:**
- Time-based expiration (TTL)
- Event-based invalidation (on data changes)
- Manual invalidation for critical updates
- Cache warming on startup

**CDN for Static Assets:**
- CloudFront, Cloudflare, or Akamai
- Cache static assets (JS, CSS, images)
- 1-hour TTL for versioned assets
- Automatic cache invalidation on deployment

### Database Query Optimization

**Indexing Strategy:**
- Primary index: (tenant_id, id)
- Composite indexes for common queries
- Partial indexes for filtered queries
- Regular index analysis and optimization

**Query Optimization:**
- Query analysis and optimization
- Avoid N+1 queries through eager loading
- Batch queries for multiple records
- Materialized views for complex aggregations

**Read Replicas:**
- Separate read replicas for reporting queries
- Asynchronous replication
- Automatic failover to primary if replica fails

### Asynchronous Processing

**Message Queue:**
- RabbitMQ or AWS SQS
- Appointment reminders
- Email/SMS sending
- Invoice generation
- Report generation
- Integration webhooks
- Data exports

**Worker Processes:**
- Multiple workers for parallel processing
- Dead letter queue for failed messages
- Retry logic with exponential backoff
- Monitoring and alerting

### Real-Time Updates

**WebSocket Implementation:**
- Real-time appointment updates
- Live calendar synchronization
- Instant notification delivery
- Presence tracking

**WebSocket Architecture:**
- Connection pooling
- Message broadcasting
- Graceful disconnection handling
- Automatic reconnection

### Performance Targets

- API response time: 95th percentile <500ms
- Page load time: <2 seconds
- Database query time: <100ms (95th percentile)
- Cache hit rate: >95%
- Availability: 99.9% uptime SLA
- Concurrent users: 10,000+ per region

## 16. Disaster Recovery and Business Continuity

### Recovery Objectives

**RTO (Recovery Time Objective):** 15 minutes
**RPO (Recovery Point Objective):** 5 minutes

### Backup Strategy

**Backup Frequency:**
- Continuous replication to standby database
- Daily full backups to object storage
- Hourly incremental backups
- Point-in-time recovery (PITR) for 30 days

**Backup Storage:**
- Primary backup: AWS S3 or equivalent
- Secondary backup: Different region
- Encryption: AES-256
- Retention: 7 years for compliance

**Backup Testing:**
- Monthly restore tests
- Automated backup verification
- Restore time measurement
- Documentation of restore procedures

### Failover Procedures

**Automatic Failover:**
- Standby database automatically promoted on primary failure
- Application automatically redirects to new primary
- DNS failover to secondary region if needed
- Monitoring alerts on failover

**Manual Failover:**
- Documented procedures for manual failover
- Runbook for failover steps
- Communication plan for stakeholders
- Post-failover verification steps

### Data Recovery Procedures

**Point-in-Time Recovery:**
1. Identify recovery point
2. Restore from backup to recovery point
3. Verify data integrity
4. Promote recovered database to primary
5. Monitor for issues

**Partial Recovery:**
- Recover specific tenant data
- Recover specific time period
- Recover specific tables
- Merge recovered data with current data

### Business Continuity Plan

**Communication:**
- Notify customers of incident
- Provide status updates every 30 minutes
- Post-incident report within 24 hours
- Root cause analysis within 7 days

**Escalation:**
- Page on-call engineer for critical issues
- Escalate to management if RTO exceeded
- Escalate to executive team if data loss

**Prevention:**
- Regular disaster recovery drills
- Chaos engineering tests
- Security audits
- Performance optimization

## 17. Security Considerations

### Threat Model

**External Threats:**
- Unauthorized access to customer data
- Payment fraud
- DDoS attacks
- SQL injection attacks
- Cross-site scripting (XSS)

**Internal Threats:**
- Malicious insiders
- Accidental data exposure
- Configuration errors
- Unpatched vulnerabilities

### Security Controls

**Access Controls:**
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)
- API key management
- Session management

**Data Protection:**
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Data masking for sensitive fields
- Secure key management

**Application Security:**
- Input validation
- Output encoding
- CSRF protection
- Rate limiting
- Security headers

**Infrastructure Security:**
- Firewall rules
- Network segmentation
- VPC isolation
- DDoS protection

### Vulnerability Management

**Vulnerability Scanning:**
- Regular vulnerability scans
- Dependency scanning
- Container image scanning
- Infrastructure scanning

**Patch Management:**
- Regular security updates
- Automated patching for non-critical updates
- Scheduled maintenance windows for critical updates
- Rollback procedures for failed patches

**Penetration Testing:**
- Annual penetration testing
- Quarterly security assessments
- Bug bounty program
- Responsible disclosure policy

### Security Incident Response

**Incident Response Plan:**
1. Detection and alerting
2. Containment (isolate affected systems)
3. Investigation (determine scope and impact)
4. Remediation (fix the issue)
5. Recovery (restore normal operations)
6. Post-incident review (lessons learned)

**Communication:**
- Notify affected customers within 24 hours
- Provide regular updates during incident
- Post-incident report within 7 days
- Regulatory notification if required

## 18. Compliance and Regulatory Requirements

### GDPR Compliance

**Data Subject Rights:**
- Right to access (data export)
- Right to rectification (data correction)
- Right to erasure (right to be forgotten)
- Right to restrict processing
- Right to data portability
- Right to object

**Data Protection Measures:**
- Data encryption at rest and in transit
- Access controls and audit logging
- Data minimization (only collect necessary data)
- Purpose limitation (only use for stated purpose)
- Storage limitation (delete after retention period)

**Data Processing Agreements:**
- Signed DPA with all customers
- Sub-processor agreements with vendors
- Data processing documentation
- Breach notification procedures

### HIPAA Compliance (if storing health data)

**Security Requirements:**
- Encryption at rest and in transit
- Access controls and audit logging
- Integrity controls
- Transmission security

**Privacy Requirements:**
- Minimum necessary principle
- Authorization and consent
- Patient rights
- Breach notification

**Business Associate Agreements:**
- Signed BAA with all customers
- Sub-contractor agreements
- Breach notification procedures

### PCI-DSS Compliance (if storing payment data)

**Security Requirements:**
- Never store full credit card numbers
- Tokenization for payment processing
- Secure key management
- Regular security assessments
- Compliance certification

**Compliance Validation:**
- Annual compliance audit
- Quarterly vulnerability scans
- Penetration testing
- Compliance certification

### SOC 2 Compliance

**Trust Service Criteria:**
- Security (access controls, encryption, monitoring)
- Availability (uptime, disaster recovery)
- Processing Integrity (data accuracy, completeness)
- Confidentiality (data privacy, encryption)
- Privacy (data handling, consent)

**Compliance Activities:**
- Annual SOC 2 audit
- Documented policies and procedures
- Evidence collection and documentation
- Remediation of findings

## 19. Technology Stack Summary

### Backend
- **Runtime**: Node.js 18+ or Python 3.11+
- **Framework**: Express.js/NestJS or FastAPI/Django
- **Database**: PostgreSQL 14+ with RLS
- **Cache**: Redis 7+
- **Message Queue**: RabbitMQ or AWS SQS
- **Search**: Elasticsearch (optional)

### Frontend
- **Web**: React 18+ with TypeScript
- **Mobile**: React Native or Flutter
- **State Management**: Redux or Zustand
- **UI Framework**: Material-UI or Tailwind CSS

### Infrastructure
- **Cloud**: AWS, Google Cloud, or Azure
- **Container**: Docker
- **Orchestration**: Kubernetes or Docker Compose
- **CI/CD**: GitHub Actions, GitLab CI, or Jenkins
- **Monitoring**: Prometheus + Grafana or DataDog
- **Logging**: ELK Stack or CloudWatch

### Testing
- **Unit Testing**: Jest, Pytest, or JUnit
- **Property Testing**: fast-check, Hypothesis, or jqwik
- **Integration Testing**: Postman or REST Assured
- **E2E Testing**: Cypress or Selenium

## 20. Implementation Roadmap

### Phase 1 - MVP (Weeks 1-12)
- Multi-tenant architecture
- User authentication and RBAC
- Appointment booking system
- Staff scheduling
- Customer profiles
- Billing and payments
- Email/SMS notifications
- Basic reporting

### Phase 2 - Operations & Financial (Weeks 13-24)
- Appointment reminders
- Customer feedback system
- Expense tracking
- Tax reporting
- Refund policies
- Deposit management
- Financial reconciliation
- Invoice generation
- Performance metrics
- Staff training tracking
- Attendance monitoring
- Shift swapping
- Staff reviews
- Skill tracking
- Inventory management

### Phase 3 - Customer Engagement & Marketing (Weeks 25-36)
- Birthday/anniversary promotions
- Referral program
- Customer segmentation
- Membership/packages
- Email marketing automation
- Social media integration
- Review management
- Seasonal promotions
- Customer retention analytics

### Phase 4 - Integrations & Advanced Features (Weeks 37-48)
- Payment gateway integrations
- SMS provider integration
- Email provider integration
- Calendar sync
- Accounting software integration
- Social media integration
- Review platform integration
- Advanced reporting
- White-label support
- API key management
- Webhook support
- Advanced integrations

### Phase 5 - Enterprise & Optimization (Weeks 49+)
- Advanced security features
- Compliance reporting
- Performance optimization
- Scalability improvements
- Advanced analytics
- Machine learning features
- Mobile app optimization
- Enterprise support


### 2.1 Salon Registration System Design

The salon registration system is a critical onboarding component that enables new salon owners to self-service register with email verification and automatic tenant provisioning. The system follows a three-phase approach to ensure data integrity, prevent incomplete registrations, and provide a seamless user experience.

#### Registration Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Registration Flow                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Phase 1: Validation          Phase 2: Verification         │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │ Check Email      │         │ Generate Code    │          │
│  │ Check Phone      │────────▶│ Store Temp Data  │          │
│  │ Check Salon Name │         │ Send Email       │          │
│  │ NO DB WRITES     │         │ TTL: 24 hours    │          │
│  └──────────────────┘         └──────────────────┘          │
│                                        │                     │
│                                        │ Code Verified       │
│                                        ▼                     │
│                              Phase 3: Creation              │
│                              ┌──────────────────┐            │
│                              │ Create Tenant    │            │
│                              │ Create User      │            │
│                              │ Create Salon     │            │
│                              │ Create Subscription           │
│                              │ Track Referral   │            │
│                              └──────────────────┘            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

#### Phase 1: Registration Request & Validation

**Purpose:** Validate all inputs without writing to database to prevent data pollution

**Process:**
1. Client submits registration form with: salon_name, owner_name, email, phone, password, address, bank_account (optional), referral_code (optional)
2. Server performs validation checks:
   - Email format validation (RFC 5322 compliant)
   - Email uniqueness check across all users
   - Phone format validation (African country codes +20-+299; minimum 10 digits total)
   - Phone uniqueness check across all tenants
   - Salon name length validation (3-255 characters)
   - Salon name uniqueness check across all tenants
   - Password strength validation (min 8 chars, uppercase, lowercase, number, special char)
   - Address validation (not empty, reasonable length)
3. If any validation fails, return specific error message without storing data
4. If all validations pass, proceed to Phase 2

**Database Operations:** NONE (read-only queries only)

**Error Responses:**
- 400 Bad Request: Invalid email format
- 409 Conflict: Email already registered
- 409 Conflict: Phone already registered
- 409 Conflict: Salon name already taken
- 400 Bad Request: Password does not meet requirements

#### Phase 2: Temporary Registration & Verification Code

**Purpose:** Generate verification code and store temporary registration data with TTL

**Process:**
1. Generate unique subdomain from salon_name:
   - Convert to lowercase
   - Replace spaces with hyphens
   - Remove special characters
   - Check uniqueness in subdomains collection
   - If conflict, append counter (e.g., acme-salon-1, acme-salon-2)
2. Generate 6-digit verification code:
   - Use cryptographically secure random number generator
   - Range: 100000-999999 (ensures 6 digits)
   - Not sequential or predictable
3. Hash password using Bcrypt:
   - Salt rounds: 12
   - Cost factor: 2^12 iterations
4. Create temporary registration document in temp_registrations collection with TTL index
5. Send verification email with 6-digit code
6. Return success response with message to check email

**Database Operations:**
- INSERT into temp_registrations collection
- CREATE TTL index on expires_at field

#### Phase 3: Email Verification & Account Creation

**Purpose:** Verify code and create permanent records (tenant, user, subscription, marketplace salon)

**Process:**
1. Client submits verification code
2. Server retrieves temporary registration by email
3. Validate verification code:
   - Code matches stored code
   - Code hasn't expired (within 15 minutes)
   - Account not locked (after 5 failed attempts)
4. If validation fails:
   - Increment attempt_count
   - If attempt_count >= 5, set locked_until = now + 15 minutes
   - Return error: "Invalid code" or "Too many attempts, try again in 15 minutes"
5. If validation passes, create permanent records in transaction:
   - Create Tenant with subscription_plan="trial", is_published=true
   - Create User (Owner) with role="owner", email_verified=true
   - Create Salon (Marketplace) with is_published=true
   - Create PlatformSubscription with trial_ends_at=now+30days
   - Track Referral (if referral_code provided)
6. Delete temporary registration document
7. Generate JWT token for automatic login
8. Return success response with token and redirect URL

**Database Operations:**
- INSERT Tenant
- INSERT User
- INSERT Salon
- INSERT PlatformSubscription
- INSERT Referral (if applicable)
- DELETE from temp_registrations
- All operations in single transaction for atomicity

#### Subdomain Routing Architecture

**DNS Configuration:**
- Wildcard DNS record: `*.kenikool.com` → API Gateway IP
- All subdomains route to same API Gateway

**API Gateway Routing:**
1. Extract subdomain from request hostname
2. Query subdomains collection for matching tenant
3. Set tenant_id in request context
4. Route to appropriate handler
5. All subsequent queries automatically filtered by tenant_id

**Example:**
- Request: `https://acme-salon.kenikool.com/api/appointments`
- Subdomain extracted: `acme-salon`
- Tenant lookup: Find tenant with subdomain="acme-salon"
- Context: Set tenant_id in request
- Query: `db.appointments.find({tenant_id: tenant_id})`

#### Security Considerations

**Password Security:**
- Bcrypt hashing with 12 salt rounds
- Minimum 12 characters with uppercase, lowercase, number, special character
- Never log or display passwords
- Use constant-time comparison for verification

**Verification Code Security:**
- Cryptographically secure random generation
- 6-digit format (1 million possible combinations)
- 15-minute expiration
- Account lockout after 5 failed attempts (15-minute cooldown)
- Rate limiting on verification endpoint (5 attempts per minute per email)

**Temporary Data Security:**
- Stored in separate collection with TTL index
- Automatically deleted after 24 hours
- Contains hashed password (never plain text)
- Encrypted at rest (MongoDB Atlas encryption)

**Subdomain Security:**
- Unique constraint prevents tenant confusion
- URL-safe format prevents injection attacks
- Prevents phishing through subdomain spoofing

**Email Verification:**
- Prevents fake email registrations
- Ensures owner has access to email
- Reduces spam registrations

#### Performance Optimization

**Validation Phase:** <100ms (indexed queries, no DB writes)
**Verification Code Phase:** <1 second (async email sending)
**Account Creation Phase:** <2 seconds (transaction with 5 inserts)

**Caching:**
- Cache subdomain-to-tenant mapping in Redis (1-hour TTL)
- Cache tenant settings in Redis (5-minute TTL)
- Invalidate cache on tenant updates

#### Error Handling & Recovery

**Validation Phase Errors:**
- Return specific error message
- No data stored
- User can retry immediately

**Verification Code Errors:**
- Code expired: Allow requesting new code
- Code incorrect: Show remaining attempts
- Account locked: Show cooldown timer
- Email not found: Suggest re-registering

**Account Creation Errors:**
- Transaction rollback on any failure
- Temporary registration remains for retry
- Log error for debugging
- Return generic error to user

#### Monitoring & Analytics

**Metrics to Track:**
- Registration attempts per day
- Validation failure rate by field
- Verification code success rate
- Average time to complete registration
- Email delivery success rate
- Referral conversion rate

**Alerts:**
- High validation failure rate (>20%)
- Email delivery failures (>5%)
- Unusual registration patterns (spike detection)
- Subdomain generation conflicts



## 9. Phase 6 - Public Booking Via Subdomain Design

### Overview

Requirement 2 encompasses three interconnected features:

1. **Salon Owner Registration**: Self-service registration with email verification and automatic subdomain generation
2. **Subdomain Routing**: DNS-based routing that automatically identifies tenants and injects context into requests
3. **Public Booking Interface**: Customer-facing booking interface accessible via subdomain without authentication

Together, these features create a complete onboarding and customer booking experience. New salon owners can register in minutes, receive a unique branded subdomain, and immediately start accepting customer bookings.

### Architecture

**Complete Registration & Public Booking Flow:**

```
PHASE 1: SALON OWNER REGISTRATION
┌─────────────────────────────────────────────────────────────┐
│ 1. Owner visits registration page                           │
│ 2. Submits: salon_name, owner_name, email, phone, password │
│ 3. System validates (email, phone, salon_name uniqueness)   │
│ 4. System generates subdomain & verification code           │
│ 5. System sends verification code to email                  │
│ 6. Owner enters verification code                           │
│ 7. System creates: Tenant, User, Subscription, Salon record │
│ 8. Owner is logged in and sees dashboard                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
PHASE 2: SUBDOMAIN ROUTING SETUP
┌─────────────────────────────────────────────────────────────┐
│ DNS Configuration: *.kenikool.com → API Gateway IP          │
│ SubdomainRouting table: subdomain → tenant_id mapping       │
│ Middleware: Extract subdomain, lookup tenant, inject context│
└─────────────────────────────────────────────────────────────┘
                            ↓
PHASE 3: CUSTOMER PUBLIC BOOKING
┌─────────────────────────────────────────────────────────────┐
│ Customer Browser Request: https://acme-salon.kenikool.com   │
│                           ↓                                  │
│ Subdomain Routing Middleware                                │
│   ├─ Extract subdomain: "acme-salon"                        │
│   ├─ Query: db.subdomains.find_one({subdomain: "acme-salon"})
│   ├─ Lookup tenant_id from SubdomainRouting table           │
│   ├─ Verify tenant is_published=true and is_active=true     │
│   ├─ Set: request.state.tenant_id = tenant._id              │
│   └─ Set: request.state.is_public = true                    │
│                           ↓                                  │
│ Public Booking API Routes (no auth required)                │
│   ├─ GET /public/services (filtered by tenant_id)           │
│   ├─ GET /public/staff (filtered by tenant_id)              │
│   ├─ GET /public/availability (filtered by tenant_id)       │
│   ├─ POST /public/bookings (create guest booking)           │
│   └─ GET /public/bookings/{id} (get confirmation)           │
│                           ↓                                  │
│ Frontend React SPA (Salon-Branded Interface)                │
│   ├─ Display salon branding (logo, colors, name)            │
│   ├─ Show published services with descriptions              │
│   ├─ Show available staff with photos/bios                  │
│   ├─ Display real-time availability calendar                │
│   └─ Collect booking details (name, email, phone)           │
│                           ↓                                  │
│ Booking Creation & Confirmation                             │
│   ├─ Validate inputs (email, phone format)                  │
│   ├─ Check availability (no double-booking)                 │
│   ├─ Create PublicBooking record                            │
│   ├─ Create/link Customer if new email                      │
│   ├─ Create Appointment record                              │
│   ├─ Send confirmation email to customer                    │
│   └─ Display confirmation page with details                 │
└─────────────────────────────────────────────────────────────┘
```

### Components and Interfaces

**Backend Components:**

1. **RegistrationRouter** (routes/registration.py)
   - POST /auth/register - Submit registration form
   - POST /auth/verify-email - Verify email with code
   - POST /auth/resend-code - Resend verification code
   - GET /auth/check-availability - Check email/phone/salon name availability

2. **RegistrationService** (services/registration_service.py)
   - validate_registration_data(data) - Validate inputs without writing to DB
   - generate_subdomain(salon_name) - Generate unique subdomain
   - generate_verification_code() - Generate 6-digit code
   - create_temp_registration(data) - Store temporary registration
   - verify_email_code(email, code) - Verify code and create permanent records
   - resend_verification_code(email) - Generate and send new code

3. **SubdomainRoutingMiddleware** (middleware/subdomain_context.py)
   - Extract subdomain from Host header
   - Query SubdomainRouting table for tenant_id
   - Validate tenant is_published and is_active
   - Inject tenant_id into request context
   - Set is_public flag for public routes

4. **PublicBookingRouter** (routes/public_booking.py)
   - GET /public/services - List published services
   - GET /public/staff - List available staff
   - GET /public/availability - Get available time slots
   - POST /public/bookings - Create booking
   - GET /public/bookings/{id} - Get booking details (for confirmation)

5. **PublicBookingService** (services/public_booking_service.py)
   - get_published_services(tenant_id) - Fetch published services
   - get_available_staff(tenant_id, service_id) - Fetch staff for service
   - get_available_slots(tenant_id, staff_id, service_id, date) - Calculate available time slots
   - create_public_booking(tenant_id, booking_data) - Create appointment from public booking
   - send_booking_confirmation(booking) - Send confirmation email

6. **PublicBookingMiddleware** (middleware/public_booking.py)
   - Validate tenant is active and allows public bookings
   - Set is_public flag in request context
   - Apply rate limiting (10 bookings per minute per IP)
   - Log all public booking requests

7. **AvailabilityCalculator** (utils/availability.py)
   - Calculate available time slots based on:
     - Staff schedule/shifts
     - Existing appointments
     - Service duration
     - Buffer time between appointments
     - Salon operating hours

**Frontend Components:**

1. **Registration Pages** (pages/auth/)
   - Register.tsx - Registration form with validation
   - Verify.tsx - Email verification code entry
   - RegisterSuccess.tsx - Success page with subdomain URL

2. **PublicBookingApp** (pages/public/PublicBookingApp.tsx)
   - Main public booking interface
   - Displays salon branding
   - Routes to service selection, staff selection, time selection, confirmation

3. **ServiceSelector** (components/public/ServiceSelector.tsx)
   - Display published services
   - Show service details (description, price, duration)
   - Allow service selection

4. **StaffSelector** (components/public/StaffSelector.tsx)
   - Display available staff for selected service
   - Show staff photos and bios
   - Allow staff selection

5. **TimeSlotSelector** (components/public/TimeSlotSelector.tsx)
   - Display calendar with available dates
   - Show available time slots for selected date
   - Allow time slot selection

6. **BookingForm** (components/public/BookingForm.tsx)
   - Collect customer details (name, email, phone)
   - Optional notes field
   - Submit booking

7. **BookingConfirmation** (components/public/BookingConfirmation.tsx)
   - Display booking confirmation
   - Show appointment details
   - Offer account creation option

### Data Models

**TempRegistration Collection (Temporary, expires in 24 hours):**
```javascript
{
  _id: ObjectId,
  email: String,  // Unique per pending registration
  phone: String,
  salon_name: String,
  owner_name: String,
  address: String,
  bank_account: String || null,
  password_hash: String,  // Bcrypt hashed
  subdomain: String,  // Generated, unique
  verification_code: String,  // 6-digit code
  verification_code_expires: Date,  // 15 minutes from generation
  referral_code: String || null,
  tenant_id_for_referral: ObjectId || null,
  created_at: Date,
  expires_at: Date  // TTL index deletes after 24 hours
}
```

**SubdomainRouting Collection:**
```javascript
{
  _id: ObjectId,
  tenant_id: ObjectId,  // Foreign key to Tenant
  subdomain: String,  // Unique, URL-safe
  is_active: Boolean,  // Can be disabled
  created_at: Date,
  updated_at: Date
}
```

**PublicBooking Collection:**
```javascript
{
  _id: ObjectId,
  tenant_id: ObjectId,
  customer_id: ObjectId || null,  // null for guest bookings
  service_id: ObjectId,
  staff_id: ObjectId,
  appointment_id: ObjectId,
  customer_name: String,
  customer_email: String,
  customer_phone: String,
  booking_date: Date,
  booking_time: String,  // HH:MM format
  notes: String || null,
  status: String,  // 'pending', 'confirmed', 'completed', 'cancelled'
  created_at: Date,
  updated_at: Date,
  ip_address: String,  // For rate limiting and fraud detection
  user_agent: String   // For device tracking
}
```

**Tenant Collection (Extended):**
```javascript
{
  _id: ObjectId,
  name: String,  // Salon name
  subdomain: String,  // Unique, URL-safe
  owner_name: String,
  phone: String,
  email: String,
  address: String,
  subscription_plan: String,  // 'trial', 'starter', 'professional', 'enterprise'
  is_active: Boolean,
  is_published: Boolean,  // Controls visibility in marketplace and public booking
  created_at: Date,
  updated_at: Date,
  deleted_at: Date || null
}
```

**Service Collection (Extended):**
```javascript
{
  // ... existing fields ...
  is_published: Boolean,  // Controls visibility in public booking
  public_description: String,  // Customer-facing description
  public_image_url: String,  // Service image for public interface
  allow_public_booking: Boolean  // Enable/disable public booking for this service
}
```

**Staff Collection (Extended):**
```javascript
{
  // ... existing fields ...
  is_available_for_public_booking: Boolean,  // Controls visibility in public booking
  public_bio: String,  // Staff bio for public interface
  public_photo_url: String  // Staff photo for public interface
}
```

### Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

**Property 1: Registration Data Validation**
*For any* registration request with invalid email, phone, or duplicate salon name, the system should reject the request without writing to the database and return appropriate error message.
**Validates: Requirements 2.1, 2.14, 2.15**

**Property 2: Subdomain Uniqueness**
*For any* salon registration, the generated subdomain should be unique across all tenants, and if a conflict occurs, the system should auto-append a counter to ensure uniqueness.
**Validates: Requirements 2.2**

**Property 3: Verification Code Expiry**
*For any* verification code generated, if more than 15 minutes pass without verification, the code should expire and become invalid for verification attempts.
**Validates: Requirements 2.9**

**Property 4: Tenant Isolation in Public Booking**
*For any* public booking request and any two different tenants, the system should only return services, staff, and availability data belonging to the requested tenant, never from other tenants.
**Validates: Requirements 2.20**

**Property 5: No Double-Booking**
*For any* staff member and time slot, if a booking is created for that staff member at that time, subsequent booking attempts for the same staff member and overlapping time should be rejected.
**Validates: Requirements 2.18**

**Property 6: Availability Calculation Accuracy**
*For any* staff member, service, and date, the available time slots returned should exclude all times that conflict with existing appointments or staff schedules, and should respect service duration and buffer times.
**Validates: Requirements 2.4**

**Property 7: Booking Confirmation Email Delivery**
*For any* public booking created, a confirmation email should be sent to the customer's email address within 5 seconds of booking creation.
**Validates: Requirements 2.19**

**Property 8: Rate Limiting Enforcement**
*For any* IP address, if more than 10 booking requests are submitted within a 60-second window, subsequent requests should be rejected with HTTP 429 status.
**Validates: Requirements 2.21**

**Property 9: Guest Booking Account Creation**
*For any* guest booking, if the customer provides an email that doesn't exist in the system, a new customer account should be created with that email and phone number.
**Validates: Requirements 2.18**

**Property 10: Published Service Visibility**
*For any* service in the public booking interface, the service should only be visible if is_published=true and allow_public_booking=true.
**Validates: Requirements 2.17**

**Property 11: Subdomain Routing Accuracy**
*For any* request to a subdomain URL, the system should correctly extract the subdomain from the Host header and route to the correct tenant without cross-tenant data leakage.
**Validates: Requirements 2.16**

**Property 12: Temporary Registration Cleanup**
*For any* temporary registration not completed within 24 hours, the system should automatically delete the registration data and free up the email/phone/salon name for reuse.
**Validates: Requirements 2.10**

### Error Handling

**Registration Validation Errors:**
- Email already registered → Return 400 with "Email already registered"
- Phone already registered → Return 400 with "Phone already registered"
- Salon name already taken → Return 400 with "Salon name already taken"
- Invalid email format → Return 400 with "Invalid email format"
- Invalid phone format → Return 400 with "Invalid phone format"
- Password too weak → Return 400 with "Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
- Missing required field → Return 400 with "Missing required field: {field}"

**Verification Errors:**
- Verification code expired → Return 400 with "Verification code expired, please request a new code"
- Verification code invalid → Return 400 with "Invalid verification code"
- Verification code locked (5 failed attempts) → Return 429 with "Too many failed attempts, please try again in 15 minutes"
- Registration expired (24 hours) → Return 400 with "Registration expired, please register again"

**Subdomain Routing Errors:**
- Subdomain not found → Return 404 with "Salon not found"
- Tenant inactive → Return 403 with "Salon is currently unavailable"
- Tenant not published → Return 404 with "Salon not found"

**Public Booking Validation Errors:**
- Invalid email format → Return 400 with "Invalid email format"
- Missing required fields → Return 400 with "Missing required field: {field}"
- Invalid phone format → Return 400 with "Invalid phone format"
- Service not found → Return 404 with "Service not found"
- Staff not found → Return 404 with "Staff not found"
- Time slot not available → Return 409 with "Time slot not available"

**Business Logic Errors:**
- Double-booking detected → Return 409 with "Time slot no longer available"
- Rate limit exceeded → Return 429 with "Too many booking requests, please try again later"

**System Errors:**
- Database error → Return 500 with "An error occurred, please try again"
- Email sending failed → Return 500 with "Booking created but confirmation email failed to send"

### Testing Strategy

**Unit Tests:**
- Test registration validation (email, phone, salon name uniqueness)
- Test subdomain generation and uniqueness
- Test verification code generation and expiry
- Test availability calculation with various schedules and appointments
- Test tenant isolation (verify queries filter by tenant_id)
- Test rate limiting logic
- Test email validation
- Test phone validation
- Test booking creation with valid and invalid data
- Test subdomain extraction from Host header
- Test temporary registration cleanup

**Property-Based Tests:**
- Property 1: Registration Data Validation - Generate random invalid inputs, verify rejection without DB write
- Property 2: Subdomain Uniqueness - Generate random salon names, verify unique subdomains
- Property 3: Verification Code Expiry - Generate codes, verify expiry after 15 minutes
- Property 4: Tenant Isolation - Generate random tenants and bookings, verify no cross-tenant data
- Property 5: No Double-Booking - Generate random bookings for same staff/time, verify conflicts detected
- Property 6: Availability Calculation - Generate random schedules and appointments, verify availability is correct
- Property 7: Email Delivery - Generate random bookings, verify confirmation emails sent
- Property 8: Rate Limiting - Generate rapid booking requests, verify rate limiting enforced
- Property 9: Guest Booking - Generate guest bookings with new emails, verify accounts created
- Property 10: Published Service Visibility - Generate services with various publish states, verify visibility
- Property 11: Subdomain Routing - Generate random subdomains, verify correct tenant routing
- Property 12: Temporary Registration Cleanup - Generate registrations, verify cleanup after 24 hours

**Integration Tests:**
- Test complete registration flow from form submission to dashboard access
- Test subdomain routing to public booking interface
- Test complete booking flow from service selection to confirmation
- Test email sending with real email service
- Test database transactions for booking creation
- Test concurrent booking attempts for same time slot
- Test verification code resend functionality
- Test registration expiry and cleanup

**Performance Tests:**
- Verify page load time <2 seconds
- Verify subdomain routing adds <50ms overhead
- Verify registration completion within 2 seconds
- Verify verification code sending within 1 second
- Verify service listing <500ms
- Verify availability calculation <1 second
- Verify booking creation <2 seconds
- Verify email sending <5 seconds



---

## 10. Phase 7 - Point of Sale (POS) System Design

### 8.1 POS Architecture

#### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    POS Frontend                              │
│  (Transaction Entry, Payment, Receipt, Offline Mode)        │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/WebSocket
┌────────────────────▼────────────────────────────────────────┐
│                    POS API Layer                             │
│  (Transaction Routes, Payment Routes, Receipt Routes)       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              POS Services Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Transaction  │  │   Payment    │  │  Inventory   │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Receipt    │  │   Discount   │  │   Refund     │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Data Access Layer                               │
│  (ORM, Query Builder, Tenant Filtering)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Infrastructure Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  MongoDB     │  │    Redis     │  │   Paystack   │      │
│  │  Database    │  │    Cache     │  │   Gateway    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

#### Component Responsibilities

**POS Frontend:**
- Transaction entry interface
- Payment processing UI
- Receipt display and printing
- Offline mode management
- Real-time inventory updates

**POS API Layer:**
- Transaction endpoints (create, read, update, refund)
- Payment endpoints (initiate, verify, reconcile)
- Receipt endpoints (generate, print, email)
- Inventory endpoints (deduct, restore, check)
- Discount endpoints (apply, validate)
- Refund endpoints (process, approve, reverse)

**POS Services Layer:**
- Transaction processing logic
- Payment gateway integration
- Inventory management
- Receipt generation
- Discount calculation
- Refund processing
- Commission calculation
- Audit logging

**Data Access Layer:**
- MongoDB queries with tenant filtering
- Transaction persistence
- Inventory updates
- Audit log recording

### 8.2 POS Data Models

#### Transaction Model

```python
class Transaction(Document):
    tenant_id = ObjectIdField(required=True)
    customer_id = ObjectIdField(required=True)
    staff_id = ObjectIdField(required=True)
    appointment_id = ObjectIdField()  # Optional, nullable
    
    transaction_type = StringField(
        choices=['service', 'product', 'package', 'refund'],
        required=True
    )
    
    items = ListField(EmbeddedDocumentField('TransactionItem'))
    
    subtotal = DecimalField(required=True)  # Before tax and discount
    tax_amount = DecimalField(required=True)
    discount_amount = DecimalField(default=0)
    total = DecimalField(required=True)  # After tax and discount
    
    payment_method = StringField(
        choices=['cash', 'card', 'mobile_money', 'check', 'bank_transfer'],
        required=True
    )
    payment_status = StringField(
        choices=['pending', 'completed', 'failed', 'refunded'],
        default='pending'
    )
    
    reference_number = StringField(unique_with='tenant_id')
    paystack_reference = StringField()  # Paystack transaction reference
    
    notes = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'indexes': [
            ('tenant_id', 'created_at'),
            ('tenant_id', 'customer_id'),
            ('tenant_id', 'staff_id'),
            ('tenant_id', 'payment_status'),
            ('reference_number', 'tenant_id')
        ]
    }
```

#### Receipt Model

```python
class Receipt(Document):
    tenant_id = ObjectIdField(required=True)
    transaction_id = ObjectIdField(required=True)
    
    receipt_number = StringField(unique_with='tenant_id')
    receipt_date = DateTimeField(default=datetime.utcnow)
    
    customer_name = StringField(required=True)
    customer_email = StringField()
    customer_phone = StringField()
    
    items = ListField(EmbeddedDocumentField('ReceiptItem'))
    
    subtotal = DecimalField(required=True)
    tax_amount = DecimalField(required=True)
    discount_amount = DecimalField(required=True)
    total = DecimalField(required=True)
    
    payment_method = StringField(required=True)
    payment_reference = StringField()
    
    receipt_format = StringField(
        choices=['thermal', 'standard', 'email', 'digital'],
        default='thermal'
    )
    
    printed_at = DateTimeField()
    emailed_at = DateTimeField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'indexes': [
            ('tenant_id', 'receipt_date'),
            ('transaction_id', 'tenant_id')
        ]
    }
```

#### Refund Model

```python
class Refund(Document):
    tenant_id = ObjectIdField(required=True)
    original_transaction_id = ObjectIdField(required=True)
    
    refund_amount = DecimalField(required=True)
    refund_reason = StringField(required=True)
    
    refund_status = StringField(
        choices=['pending', 'approved', 'completed', 'rejected'],
        default='pending'
    )
    
    approved_by = ObjectIdField()
    approved_at = DateTimeField()
    
    completed_at = DateTimeField()
    
    notes = StringField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'indexes': [
            ('tenant_id', 'refund_status'),
            ('original_transaction_id', 'tenant_id')
        ]
    }
```

#### Discount Model

```python
class Discount(Document):
    tenant_id = ObjectIdField(required=True)
    
    discount_code = StringField(unique_with='tenant_id')
    discount_type = StringField(
        choices=['percentage', 'fixed', 'loyalty', 'bulk'],
        required=True
    )
    discount_value = DecimalField(required=True)
    
    applicable_to = StringField(
        choices=['transaction', 'item', 'service', 'product'],
        default='transaction'
    )
    
    conditions = DictField()  # JSON conditions for applying discount
    max_discount = DecimalField()  # Maximum discount amount
    
    active = BooleanField(default=True)
    valid_from = DateTimeField()
    valid_until = DateTimeField()
    
    usage_count = IntField(default=0)
    usage_limit = IntField()  # Maximum uses
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'indexes': [
            ('tenant_id', 'discount_code'),
            ('tenant_id', 'active')
        ]
    }
```

### 8.3 Payment Integration with Paystack

#### Payment Flow

```
1. Customer initiates payment
   ↓
2. System creates payment record
   ↓
3. System redirects to Paystack
   ↓
4. Customer enters payment details
   ↓
5. Paystack processes payment
   ↓
6. Paystack redirects to callback URL
   ↓
7. System verifies payment with Paystack
   ↓
8. System updates transaction status
   ↓
9. System sends confirmation to customer
```

#### Paystack Service Implementation

```python
class PaystackService:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.base_url = "https://api.paystack.co"
    
    def initialize_payment(self, amount, email, reference):
        """Initialize payment with Paystack"""
        # Create payment authorization URL
        # Return authorization URL for redirect
    
    def verify_payment(self, reference):
        """Verify payment status with Paystack"""
        # Query Paystack for payment status
        # Return payment details
    
    def process_refund(self, reference, amount):
        """Process refund through Paystack"""
        # Create refund request
        # Return refund status
    
    def handle_webhook(self, payload, signature):
        """Handle Paystack webhook"""
        # Verify webhook signature
        # Process payment status update
        # Update transaction status
```

### 8.4 Inventory Deduction Workflow

#### Deduction Process

```
1. Transaction is completed
   ↓
2. For each product item in transaction:
   a. Check inventory availability
   b. If insufficient, rollback transaction
   c. If sufficient, deduct inventory
   d. Create inventory movement record
   ↓
3. If inventory falls below reorder point:
   a. Generate low-stock alert
   b. Notify manager
   ↓
4. Update inventory cache in Redis
```

### 8.5 Receipt Generation System

#### Receipt Template

The receipt template is an HTML template with CSS styling that includes:
- Salon name, address, phone, website
- Receipt number and date
- Customer information
- Itemized list of products/services
- Subtotal, tax, discount, and total
- Payment method and reference
- QR code for receipt verification
- Thank you message

#### Receipt Service

The receipt service handles:
- Receipt generation from transaction data
- PDF conversion from HTML template
- Printing to thermal or standard printers
- Email delivery to customers
- QR code generation for receipt verification

### 8.6 Offline Sync Mechanism

#### Offline Storage

Uses IndexedDB for browser-based offline storage with collections for:
- Transactions (pending, synced)
- Carts (active, completed, abandoned)
- Inventory (cached product data)
- Sync queue (pending operations)

#### Sync Process

```javascript
class OfflineSyncManager {
    async syncTransactions() {
        // Get all pending transactions from IndexedDB
        // Send to server
        // Update status to synced
        // Handle conflicts intelligently
    }
    
    async handleConflict(localTransaction, serverTransaction) {
        // Compare timestamps
        // Use newer version
        // Notify user of conflict resolution
    }
}
```

### 8.7 POS Correctness Properties

#### Property 1: Transaction Immutability
*For any* completed transaction, the transaction record SHALL NOT be modified; only refunds are allowed for corrections.
**Validates: Requirements 70.4**

#### Property 2: Inventory Deduction Accuracy
*For any* transaction with product items, the inventory quantity SHALL be reduced by the exact quantity sold.
**Validates: Requirements 72.1**

#### Property 3: Payment Status Consistency
*For any* transaction, the payment status SHALL match the Paystack payment status after webhook processing.
**Validates: Requirements 71.3**

#### Property 4: Receipt Generation Completeness
*For any* completed transaction, a receipt SHALL be generated automatically with all transaction details.
**Validates: Requirements 74.1**

#### Property 5: Refund Inventory Restoration
*For any* refunded transaction, the inventory quantities SHALL be restored to pre-transaction levels.
**Validates: Requirements 78.3**

#### Property 6: Discount Calculation Accuracy
*For any* transaction with applied discount, the discount amount SHALL be calculated correctly based on discount type and value.
**Validates: Requirements 77.1**

#### Property 7: Tax Calculation Accuracy
*For any* transaction, the tax amount SHALL be calculated correctly based on the discounted subtotal and applicable tax rate.
**Validates: Requirements 77.5**

#### Property 8: Commission Calculation Accuracy
*For any* completed transaction, the staff commission SHALL be calculated correctly based on the commission structure.
**Validates: Requirements 79.2**

#### Property 9: Offline Sync Idempotence
*For any* transaction synced multiple times from offline mode, the final state SHALL be identical to syncing once.
**Validates: Requirements 75.3**

#### Property 10: Audit Trail Completeness
*For any* transaction modification, an audit log entry SHALL be created with user, timestamp, and old/new values.
**Validates: Requirements 80.1**

### 8.8 POS Error Handling

#### Transaction Errors

- **InsufficientInventoryError**: Raised when product inventory is insufficient
- **PaymentFailedError**: Raised when payment processing fails
- **InvalidDiscountError**: Raised when discount code is invalid or expired
- **DuplicateTransactionError**: Raised when duplicate transaction is detected
- **RefundNotAllowedError**: Raised when refund is not allowed for transaction

#### Error Responses

```json
{
    "success": false,
    "error": {
        "code": "INSUFFICIENT_INVENTORY",
        "message": "Insufficient inventory for product",
        "details": {
            "product_id": "...",
            "requested": 5,
            "available": 2
        }
    }
}
```

### 8.9 POS Testing Strategy

#### Unit Tests

- Transaction creation and validation
- Inventory deduction logic
- Discount calculation
- Tax calculation
- Commission calculation
- Receipt generation
- Refund processing

#### Property-Based Tests

- Transaction immutability (Property 1)
- Inventory deduction accuracy (Property 2)
- Payment status consistency (Property 3)
- Receipt generation completeness (Property 4)
- Refund inventory restoration (Property 5)
- Discount calculation accuracy (Property 6)
- Tax calculation accuracy (Property 7)
- Commission calculation accuracy (Property 8)
- Offline sync idempotence (Property 9)
- Audit trail completeness (Property 10)

#### Integration Tests

- Complete transaction flow from cart to receipt
- Payment processing with Paystack
- Inventory deduction and restoration
- Offline mode and sync
- Refund processing
- Commission calculation and payout
