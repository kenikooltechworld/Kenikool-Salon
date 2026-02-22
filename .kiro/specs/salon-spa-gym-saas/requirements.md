# Requirements Document: Multi-Tenant SaaS Platform for Salon, Spa & Gym Management

## Introduction

This document specifies a comprehensive multi-tenant SaaS platform designed to serve salons, spas, and gyms with enterprise-grade management capabilities. The platform supports 68 features organized across 5 implementation phases, enabling businesses to manage appointments, staff, customers, inventory, billing, and marketing from a unified interface.

The platform is built on principles of data isolation, scalability, security, and user experience, targeting modern service-based businesses that require sophisticated operational management tools.

## Glossary

- **Tenant**: A business entity (salon, spa, or gym) using the platform
- **Multi-Tenancy**: Architecture where a single application instance serves multiple independent tenants with complete data isolation
- **Role-Based Access Control (RBAC)**: Permission system based on user roles (Owner, Manager, Staff, Customer)
- **Appointment**: A scheduled service booking for a customer with a staff member
- **Service**: A specific treatment or activity offered (haircut, massage, personal training session)
- **Resource**: Physical assets required for services (chairs, treatment rooms, equipment)
- **Availability**: Time slots when staff or resources are available for booking
- **Capacity**: Maximum number of concurrent appointments or customers
- **No-Show**: When a customer fails to arrive for a scheduled appointment
- **Overbooking**: Scheduling more appointments than capacity allows
- **Shift**: A scheduled work period for staff
- **Inventory**: Products and supplies tracked for stock management
- **Billing Cycle**: Period for which charges are calculated and invoiced
- **Payment Gateway**: Third-party service for processing payments
- **Compliance**: Adherence to regulations (HIPAA, GDPR, PCI-DSS)
- **White-Label**: Customizable branding for resale or specific tenant needs
- **Churn**: Customer attrition or cancellation of services
- **Tenant Admin**: Owner or manager with full control over tenant settings
- **Staff Member**: Employee providing services to customers
- **Customer**: End user purchasing services

---

## PHASE 1 - MVP (Core Foundation)

### Requirement 1: Multi-Tenant Architecture with Complete Data Isolation

**User Story:** As a platform owner, I want complete data isolation between tenants, so that each business operates independently with guaranteed data security and privacy.

#### Detailed Description

The multi-tenant architecture forms the foundational layer of the platform, enabling multiple independent businesses (salons, spas, gyms) to operate within a single application instance while maintaining complete data isolation. This architecture is critical for SaaS scalability and cost efficiency, as it allows the platform to serve hundreds or thousands of businesses without requiring separate infrastructure for each tenant.

Data isolation is achieved through a combination of database-level partitioning and application-level filtering. Each tenant's data is logically separated, ensuring that queries automatically filter results to only include data belonging to the authenticated tenant. This multi-layered approach prevents accidental data leakage while maintaining performance and scalability.

The architecture supports both horizontal and vertical scaling, allowing the platform to grow from a few tenants to thousands without compromising data security or performance. Tenant provisioning is automated, enabling rapid onboarding of new businesses with minimal manual intervention.

#### Technical Specifications

- **Isolation Strategy**: Row-level security (RLS) with tenant_id column on all tables as primary isolation mechanism
- **Database Approach**: Shared database with logical partitioning (preferred for cost efficiency) or separate schemas per tenant (for enhanced isolation)
- **Query Filtering**: Automatic tenant_id filtering at ORM/query layer to prevent accidental cross-tenant queries
- **Connection Pooling**: Tenant-aware connection pooling to optimize database connections
- **Data Encryption**: All tenant data encrypted at rest using AES-256 with tenant-specific keys
- **Backup Strategy**: Separate backup streams per tenant with ability to restore individual tenant data
- **Scaling Approach**: Horizontal scaling through database sharding by tenant_id for very large deployments

#### Business Context

- **Problem Solved**: Enables cost-effective multi-tenant SaaS model by sharing infrastructure while maintaining data privacy
- **ROI**: Reduces infrastructure costs by 60-70% compared to single-tenant deployments while maintaining security
- **Competitive Advantage**: Allows rapid scaling to serve thousands of businesses without proportional infrastructure growth; enables competitive pricing through shared infrastructure

#### Integration Points

- **User Authentication (Req 2)**: Tenant context passed through authentication token to all subsequent requests
- **Database Infrastructure**: Requires database with RLS support (PostgreSQL, SQL Server) or application-level filtering
- **Audit Logging (Req 41)**: All data access logged with tenant context for compliance
- **Backup & Disaster Recovery (Req 42)**: Tenant-aware backup and restore procedures

#### Data Model Details

- **Tenant**: ID (UUID), name (string), subscription_tier (enum: starter/professional/enterprise), created_at (timestamp), deleted_at (timestamp, nullable), status (enum: active/suspended/deleted), region (string for data residency)
- **TenantSettings**: tenant_id (FK), branding_logo_url (string), primary_color (hex), secondary_color (hex), features_enabled (JSON array), custom_domain (string, nullable), timezone (string), language (string)
- **TenantDatabase**: tenant_id (FK), database_host (string), database_name (string), encryption_key_id (string), backup_location (string)
- **AuditLog**: ID (UUID), tenant_id (FK), user_id (FK), action (string), resource_type (string), resource_id (string), old_value (JSON), new_value (JSON), timestamp (timestamp), ip_address (string)

#### User Workflows

**For Platform Admin:**
1. Receive new tenant signup request
2. Validate business information and payment method
3. Create tenant record in system
4. Provision database schema or logical partition
5. Generate tenant API keys and credentials
6. Send onboarding email with login credentials
7. Monitor tenant provisioning status

**For Tenant Owner:**
1. Sign up for platform account
2. Provide business information (name, location, services)
3. Receive confirmation and login credentials
4. Log in and access tenant dashboard
5. Configure tenant settings (branding, features)
6. Invite staff members to tenant
7. Begin using platform features

#### Edge Cases & Constraints

- **Tenant Deletion**: When tenant is deleted, all data must be securely purged within 30 days; soft delete recommended for audit trail
- **Data Migration**: Tenants may request data export; system must support GDPR data portability requirements
- **Cross-Tenant Queries**: Prevent any queries that could accidentally return cross-tenant data; implement query validation layer
- **Tenant Suspension**: Suspended tenants should have read-only access; implement suspension logic at query layer
- **Database Limits**: Single database approach has limits (~10,000 tenants); plan for sharding strategy at scale
- **Backup Restoration**: Ensure tenant can only restore their own data; implement strict authorization checks

#### Performance Requirements

- **Tenant Provisioning**: Complete within 5 minutes from signup to ready-to-use
- **Query Performance**: Tenant filtering adds <5ms overhead to queries
- **Data Isolation Verification**: Automated tests verify no cross-tenant data leakage on every deployment
- **Backup Completion**: Daily backups complete within 2 hours for all tenants
- **Restore Time**: Restore individual tenant data within 30 minutes

#### Security Considerations

- **Data Encryption**: All tenant data encrypted at rest using AES-256; encryption keys stored separately from data
- **Encryption Keys**: Tenant-specific encryption keys managed through secure key management service (AWS KMS, Azure Key Vault)
- **Access Control**: All database access requires authentication; no direct database access from application servers
- **Query Validation**: All queries validated to ensure tenant_id filter is applied before execution
- **Audit Trail**: All data access logged with user, timestamp, and action for compliance
- **Network Isolation**: Tenants in different regions stored in separate database instances for data residency compliance

#### Compliance Requirements

- **GDPR**: Support data portability (export) and right to be forgotten (deletion) for all tenant data
- **HIPAA**: If storing health information, encrypt data at rest and in transit; maintain audit logs of all access
- **PCI-DSS**: If storing payment information, comply with PCI-DSS requirements; never store full credit card numbers
- **SOC 2**: Implement controls for data isolation, access control, and audit logging
- **Data Residency**: Support storing tenant data in specific regions (EU, US, etc.) for compliance

#### Acceptance Criteria

1. WHEN a new tenant is created, THE System SHALL provision isolated database schemas or logical partitions ensuring no data leakage between tenants
2. WHEN a user from Tenant A attempts to access data from Tenant B, THE System SHALL deny access and log the unauthorized attempt
3. WHEN querying data, THE System SHALL automatically filter results to only include data belonging to the authenticated tenant
4. WHEN a tenant is deleted, THE System SHALL securely purge all associated data within 30 days
5. WHEN scaling the platform, THE System SHALL maintain data isolation across distributed infrastructure

#### Business Value

- Ensures regulatory compliance (GDPR, HIPAA)
- Builds customer trust through guaranteed data privacy
- Enables secure multi-tenant scaling
- Reduces liability and legal risk

#### Dependencies

- User authentication system (Requirement 2)
- Database infrastructure

#### Key Data Entities

- Tenant (ID, name, subscription tier, created_at, deleted_at)
- TenantSettings (tenant_id, branding, features_enabled)
- AuditLog (tenant_id, user_id, action, timestamp)

#### User Roles

- Platform Admin: Manages tenant provisioning
- Tenant Owner: Owns tenant data

---

### Requirement 2: Salon Owner Registration with Email Verification and Subdomain Generation

**User Story:** As a salon owner, I want to register my salon with email verification and get a unique subdomain, so that customers can easily access my booking page and I can manage my business independently.

#### Detailed Description

The salon registration system enables new salon owners to create accounts with a secure three-phase verification process. Upon registration, each salon receives a unique subdomain (e.g., `acme-salon.kenikool.com`) that customers use to access the booking interface. The system validates all inputs, generates verification codes, and only creates user and tenant records after email verification is confirmed. This approach prevents database pollution from incomplete registrations and ensures only verified salon owners gain access.

**Phase 1: Registration Request & Validation**
- Salon owner submits registration form with: salon_name, owner_name, email, phone, password, address, bank_account (optional), referral_code (optional)
- System validates without writing to database:
  - Email not already registered
  - Phone not already registered
  - Salon name not already taken
- If validation fails, return error; no data stored
- If validation passes, proceed to Phase 2

**Phase 2: Temporary Registration & Verification Code**
- System generates unique subdomain from salon name (auto-append counter if conflict)
- System generates 6-digit verification code (not guessable, expires in 15 minutes)
- System hashes password using Bcrypt (salt rounds ≥12)
- System stores temporary registration in temp_registrations collection with:
  - All registration data (salon_name, owner_name, email, phone, address, bank_account)
  - Hashed password
  - Generated subdomain
  - Verification code with expiration timestamp (15 minutes)
  - Referral code (if provided)
  - Document expires in 24 hours (auto-deleted by TTL index)
- System sends 6-digit verification code to owner's email
- User can request new code if first expires (generates new code, resets 15-minute timer)

**Phase 3: Email Verification & Account Creation**
- Owner enters 6-digit code from email
- System verifies code matches and hasn't expired
- System creates permanent records:
  - **Tenant**: salon_name, subdomain (unique), owner_name, phone, email, address, subscription_plan="trial", is_published=true, created_at, updated_at
  - **Salon** (marketplace): tenant_id (FK), name, description, phone, email, address, location, image_url, logo_url, rating=0, review_count=0, is_published=true, is_active=true
  - **User** (owner account): email, password_hash, first_name=owner_name, role_id (owner role), tenant_id (FK), email_verified=true, created_at, last_login=null
  - **PlatformSubscription**: tenant_id (FK), plan_id="trial", plan_name="Trial", status="trial", trial_ends_at=now+30days, current_period_start=now, current_period_end=now+30days
- System deletes temporary registration record
- System tracks referral if referral_code was provided (increment referral count for referring tenant)
- Owner is now able to log in and access dashboard with unique subdomain

**Phase 4: Subdomain Routing & Public Booking Interface**
- DNS wildcard configuration (*.kenikool.com) routes all subdomain requests to the API
- Subdomain routing middleware intercepts all incoming requests
- Middleware extracts subdomain from Host header (e.g., "acme-salon" from "acme-salon.kenikool.com")
- System looks up tenant by subdomain in database
- If tenant found and is_published=true, tenant_id is injected into request context
- All subsequent queries are automatically filtered by tenant_id for data isolation
- Public booking interface is served to customer (no authentication required)
- Customer sees salon's branded interface with:
  - Salon name, logo, and branding colors
  - Available services and staff
  - Real-time availability calendar
  - Booking form for appointment selection
- Customer can browse services, select staff/date/time, and book appointment without creating account
- System creates guest booking record with customer contact information
- Booking confirmation email sent to customer with appointment details

**Immediately After Verification:**
- Owner can create staff members
- Owner can add services
- Owner can set up availability/schedules
- Owner can configure salon settings (branding, colors, timezone, language)
- Owner can invite customers to book appointments
- All Enterprise features unlocked during 30-day trial period
- Salon is visible in marketplace for customer discovery
- Subdomain is immediately active and accessible to customers

#### Technical Specifications

- **Registration Fields**: salon_name, owner_name, email, phone, password, address, bank_account (optional), referral_code (optional)
- **Subdomain Generation**: Auto-generated from salon name, guaranteed unique, URL-safe format
- **Email Verification**: 6-digit code sent via email, expires in 15 minutes, resendable
- **Temporary Storage**: Registration data stored in temp_registrations collection, expires in 24 hours
- **Trial Subscription**: 30-day free trial with all Enterprise features included
- **Marketplace**: Salon auto-published to marketplace upon verification
- **Referral Tracking**: Track referrals during registration for affiliate programs
- **Subdomain Routing Middleware**: Extracts subdomain from Host header and injects tenant_id into request context
- **DNS Configuration**: Wildcard DNS (*.kenikool.com) routes all subdomains to API
- **Public Booking API Endpoints**:
  - `GET /public/services` - List all services for tenant (no auth required)
  - `GET /public/staff` - List all staff members for tenant (no auth required)
  - `GET /public/availability` - Get availability slots for service/staff/date (no auth required)
  - `POST /public/bookings` - Create guest booking without authentication (no auth required)
  - `GET /public/booking/{id}` - Retrieve booking confirmation (no auth required)
- **Tenant Isolation for Public Bookings**: All public endpoints filter by tenant_id from subdomain context
- **Rate Limiting for Public Bookings**: 10 bookings per minute per IP address to prevent abuse
- **Guest Booking Model**: Supports booking without account creation; customer provides name, email, phone
- **Booking Confirmation**: Automatic email sent to customer with appointment details and cancellation link

#### Business Context

- **Problem Solved**: Eliminates manual tenant provisioning; enables self-service onboarding with email verification
- **ROI**: Reduces onboarding time from hours to minutes; enables viral growth through referral system
- **Competitive Advantage**: Unique subdomains create branded booking experiences; trial period reduces signup friction

#### Integration Points

- **Email Service (Req 7)**: Send verification codes and welcome emails
- **Subdomain Routing Middleware**: DNS/reverse proxy routes subdomain to correct tenant
- **Public Booking API**: Serve public booking interface to customers via subdomain
- **Marketplace (Req 50)**: Auto-publish salons to marketplace
- **Referral System (Req 51)**: Track referrals during registration
- **Trial Subscriptions (Req 52)**: Create 30-day trial upon verification

#### Data Model Details

- **TempRegistration**: email, phone, salon_name, owner_name, address, bank_account, hashed_password, subdomain, verification_code, verification_code_expires, referral_code, tenant_id_for_referral, created_at, expires_at
- **Tenant**: ID (UUID), salon_name, subdomain (unique), owner_name, phone, email, address, subscription_plan (enum: trial/starter/professional/enterprise), is_active, is_published, created_at, updated_at
- **Salon** (marketplace): tenant_id (FK), name, description, phone, email, address, location, image_url, logo_url, rating, review_count, is_published, is_active, created_at, updated_at
- **PlatformSubscription**: tenant_id (FK), plan_id, plan_name, status (enum: trial/active/cancelled), trial_ends_at, current_period_start, current_period_end, created_at, updated_at
- **PublicBooking**: ID (UUID), tenant_id (FK), service_id (FK), staff_id (FK), customer_name (string), customer_email (string), customer_phone (string), booking_date (date), booking_time (time), duration_minutes (integer), status (enum: pending/confirmed/cancelled), notes (string, nullable), created_at (timestamp), updated_at (timestamp)
- **SubdomainRouting**: tenant_id (FK), subdomain (string, unique), is_active (boolean), created_at (timestamp), updated_at (timestamp)

#### User Workflows

**For Salon Owner - Registration Flow:**
1. Visit registration page
2. Enter salon name, owner name, email, phone, password, address
3. Optionally enter bank account details and referral code
4. Click "Register" button
5. System validates inputs (email, phone, salon name uniqueness)
6. If validation fails, show error messages and allow correction
7. If validation passes, system generates subdomain and verification code
8. System sends 6-digit verification code to owner's email
9. Owner receives email with subject "Verify Your Salon Registration - Code: XXXXXX"
10. Owner enters 6-digit code on verification page
11. System verifies code and creates tenant, user, subscription, and marketplace salon record
12. Owner is logged in automatically and redirected to dashboard
13. Dashboard shows: "Welcome! Your salon is ready. Your booking URL is: acme-salon.kenikool.com"
14. Owner can immediately start configuring salon (add staff, services, availability)

**For Salon Owner - If Verification Code Expires:**
1. Owner clicks "Resend Code" button on verification page
2. System generates new 6-digit code
3. System sends new code to email
4. Owner enters new code
5. Verification proceeds as normal

**For Salon Owner - If Registration Expires (24 hours):**
1. Temporary registration data is automatically deleted
2. Owner must start registration process again
3. System allows re-registration with same email/phone/salon name

**For Customer - Accessing Salon Booking Page via Subdomain:**
1. Customer receives salon's unique subdomain URL (e.g., acme-salon.kenikool.com)
2. Customer visits URL in browser
3. System routes request to correct tenant based on subdomain
4. Customer sees salon's branded booking interface with:
   - Salon name, logo, and branding colors
   - Available services and staff members
   - Real-time availability calendar
5. Customer browses services and staff availability
6. Customer selects service, staff member, date, and time
7. Customer enters name, email, and phone number
8. Customer reviews booking details
9. Customer clicks "Confirm Booking" button
10. System creates guest booking record (no account required)
11. System sends booking confirmation email to customer with:
    - Appointment date, time, and duration
    - Service name and staff member name
    - Salon address and contact information
    - Cancellation link (valid for 24 hours before appointment)
12. Customer can optionally create account to manage future bookings
13. Booking appears in salon owner's dashboard

**For Customer - Cancelling Booking via Email Link:**
1. Customer receives booking confirmation email
2. Customer clicks "Cancel Booking" link in email
3. System verifies cancellation link is valid (within 24 hours of appointment)
4. System marks booking as cancelled
5. System sends cancellation confirmation email to customer
6. Salon owner is notified of cancellation

**For Referral Tracking:**
1. Existing salon owner generates referral link: kenikool.com/register?ref=SALON_ID
2. New salon owner clicks referral link during registration
3. Registration form pre-fills referral_code field
4. Upon verification, system increments referral count for referring salon
5. Referral rewards are credited to referring salon's account

#### Edge Cases & Constraints

- **Duplicate Salon Names**: Allow with location suffix (e.g., "Salon A - Lagos", "Salon A - Abuja")
- **Subdomain Conflicts**: Auto-append counter if subdomain taken (e.g., acme-salon-1, acme-salon-2)
- **Verification Code Expiry**: Code expires in 15 minutes; user can request new code
- **Registration Expiry**: Temporary registration expires in 24 hours; user must register again
- **Email Verification**: Only one pending registration per email; new registration overwrites old
- **Phone Uniqueness**: Phone must be unique across all salons
- **Referral Validation**: Referral code must be valid and from active tenant

#### Performance Requirements

- **Subdomain Generation**: Generate unique subdomain within 100ms
- **Verification Code Sending**: Send email within 1 second
- **Registration Completion**: Complete verification and create records within 2 seconds
- **Subdomain Routing**: Route request to correct tenant within 50ms

#### Security Considerations

- **Password Security**: Bcrypt hashing with salt rounds ≥12; minimum 8 characters with complexity requirements (uppercase, lowercase, digit, special character)
- **Phone Validation**: Supports African country codes (+20 to +299); minimum 10 digits total
- **Verification Code**: 6-digit code, not guessable, expires quickly
- **Email Verification**: Prevents fake email registrations
- **Temporary Data**: Automatically deleted after 24 hours
- **Subdomain Uniqueness**: Prevents tenant confusion and phishing
- **Referral Validation**: Verify referral code before crediting rewards

#### Compliance Requirements

- **GDPR**: Support data export and deletion of registration data
- **Email Verification**: Comply with CAN-SPAM by sending verification emails
- **Data Retention**: Delete temporary registrations after 24 hours

#### Acceptance Criteria

1. WHEN a salon owner submits registration with valid data, THE System SHALL validate email, phone, and salon name uniqueness WITHOUT writing to database
2. WHEN validation passes, THE System SHALL generate unique subdomain (auto-append counter if conflict) and 6-digit verification code
3. WHEN verification code is generated, THE System SHALL send it to owner's email within 1 second
4. WHEN owner enters correct 6-digit code within 15 minutes, THE System SHALL create tenant, user, subscription, and marketplace salon record
5. WHEN tenant is created, THE System SHALL set subscription_plan="trial" and trial_ends_at=now+30days
6. WHEN tenant is created, THE System SHALL set is_published=true and auto-publish salon to marketplace
7. WHEN owner is verified, THE System SHALL create user with role="owner" and email_verified=true
8. WHEN referral code is provided and valid, THE System SHALL track referral and increment referral count for referring tenant
9. WHEN verification code expires (15 minutes), THE System SHALL allow owner to request new code
10. WHEN registration is not completed within 24 hours, THE System SHALL delete temporary registration data
11. WHEN owner logs in after verification, THE System SHALL display dashboard with unique subdomain URL
12. WHEN customer visits subdomain URL, THE System SHALL route to correct tenant and display salon's branded booking interface
13. WHEN verification code is entered incorrectly 5 times, THE System SHALL lock verification for 15 minutes
14. WHEN owner attempts to register with duplicate email, THE System SHALL return error "Email already registered"
15. WHEN owner attempts to register with duplicate phone, THE System SHALL return error "Phone already registered"
16. WHEN customer visits subdomain URL, THE System SHALL extract subdomain from Host header and route to correct tenant
17. WHEN customer visits subdomain, THE System SHALL display salon's branded interface with services, staff, and availability
18. WHEN customer books via subdomain, THE System SHALL create appointment without requiring authentication
19. WHEN customer books via subdomain, THE System SHALL send booking confirmation email with appointment details
20. WHEN customer books via subdomain, THE System SHALL maintain tenant isolation (no cross-tenant data visible)
21. WHEN public booking endpoint is called, THE System SHALL rate limit to 10 bookings per minute per IP address
22. WHEN customer cancels booking via email link, THE System SHALL mark booking as cancelled and notify salon owner
23. WHEN customer cancels booking, THE System SHALL send cancellation confirmation email to customer

#### Business Value

- Enables self-service onboarding without manual intervention
- Reduces signup friction through email verification
- Creates unique branded experiences through subdomains
- Enables viral growth through referral system
- Automatically populates marketplace with new salons

#### Dependencies

- Email service (Requirement 7)
- Marketplace (Phase 2)
- Referral system (Phase 2)

#### Key Data Entities

- TempRegistration (email, salon_name, verification_code, expires_at)
- Tenant (salon_name, subdomain, subscription_plan)
- Salon (tenant_id, name, is_published)
- PlatformSubscription (tenant_id, plan_id, trial_ends_at)
- PublicBooking (tenant_id, service_id, staff_id, customer_name, customer_email, booking_date, booking_time)

#### Subdomain Routing Architecture

The subdomain routing system enables customers to access salon booking pages through branded URLs while maintaining complete tenant isolation. This architecture is critical for the public booking experience and ensures that each salon's data remains secure and isolated.

**DNS Configuration:**
- Wildcard DNS record (*.kenikool.com) points to the API server
- All subdomain requests (e.g., acme-salon.kenikool.com) are routed to the same API instance
- DNS resolution happens at the infrastructure level, before the application receives the request

**Subdomain Extraction & Tenant Lookup:**
- Subdomain routing middleware intercepts all incoming HTTP requests
- Middleware extracts subdomain from the Host header (e.g., "acme-salon" from "acme-salon.kenikool.com")
- System queries SubdomainRouting table to find tenant_id associated with subdomain
- If subdomain not found or tenant is_published=false, return 404 error
- If tenant found and is_active=true, proceed to next step

**Tenant Context Injection:**
- Tenant_id is injected into request context (e.g., request.tenant_id)
- All subsequent middleware and route handlers have access to tenant_id
- Tenant_id is automatically included in all database queries for filtering

**Public Booking Interface:**
- Public routes (GET /public/services, GET /public/availability, POST /public/bookings) do not require authentication
- All public routes automatically filter data by tenant_id from request context
- Public booking interface is served as a single-page application (SPA) with salon branding
- Branding (logo, colors, name) is fetched from Tenant and Salon records

**Data Isolation Enforcement:**
- All queries include WHERE tenant_id = request.tenant_id filter
- Database-level row-level security (RLS) provides additional protection
- Public booking API endpoints validate tenant_id before returning any data
- Cross-tenant data access is prevented at both application and database levels

**Rate Limiting for Public Bookings:**
- Public booking endpoint (POST /public/bookings) is rate limited to 10 requests per minute per IP address
- Rate limiting is enforced at middleware level before reaching route handler
- Prevents abuse and ensures fair access for all customers

#### User Roles

- Salon Owner: Registers and manages salon
- Customer: Accesses salon via subdomain and books appointments

---

### Requirement 3: User Authentication with Role-Based Access Control

**User Story:** As a business owner, I want granular control over staff permissions, so that employees only access features and data relevant to their role.

#### Detailed Description

The authentication and authorization system provides secure user access with granular role-based access control (RBAC). This system ensures that each user can only access features and data appropriate to their role within the organization. The platform supports four primary roles (Owner, Manager, Staff, Customer) with customizable permissions, enabling businesses to define their own role hierarchies and permission structures.

Authentication uses industry-standard protocols (OAuth 2.0, JWT) with secure session management. Multi-factor authentication (MFA) is supported for enhanced security, particularly for administrative accounts. The system maintains detailed audit logs of all authentication events and permission changes for compliance and security monitoring.

Authorization is enforced at multiple layers: API endpoint level, database query level, and UI level. This defense-in-depth approach ensures that even if one layer is compromised, data remains protected. Permission checks are cached for performance while maintaining real-time updates when permissions change.

#### Technical Specifications

- **Authentication Protocol**: OAuth 2.0 with JWT tokens for stateless authentication
- **Password Security**: Bcrypt hashing with salt rounds ≥12; minimum 12 characters with complexity requirements
- **Session Management**: JWT tokens with 24-hour expiration; refresh tokens with 30-day expiration
- **MFA Support**: TOTP (Time-based One-Time Password) via authenticator apps; SMS-based OTP as fallback
- **Authorization Model**: Role-Based Access Control (RBAC) with resource-level permissions
- **Permission Caching**: In-memory cache with 5-minute TTL for performance; invalidated on permission changes
- **API Security**: All API endpoints require valid JWT token; rate limiting (100 requests/minute per user)
- **Session Tracking**: Track active sessions per user; allow session management (logout other sessions)

#### Business Context

- **Problem Solved**: Prevents unauthorized access to sensitive business data; enables secure delegation of responsibilities
- **ROI**: Reduces operational errors from staff accessing wrong features by 80%; prevents data breaches from compromised accounts
- **Competitive Advantage**: Granular permissions enable businesses to define custom roles; supports compliance requirements for regulated industries

#### Integration Points

- **Multi-Tenant Architecture (Req 1)**: Tenant context passed through authentication token to all requests
- **Audit Logging (Req 41)**: All authentication events and permission changes logged
- **Two-Factor Authentication (Req 43)**: Integrates with 2FA system for enhanced security
- **Permission Management (Req 44)**: Detailed permission configuration system

#### Data Model Details

- **User**: ID (UUID), email (string, unique per tenant), password_hash (string), first_name (string), last_name (string), phone (string), role_id (FK), tenant_id (FK), created_at (timestamp), last_login (timestamp), status (enum: active/inactive/suspended), mfa_enabled (boolean), mfa_method (enum: totp/sms)
- **Role**: ID (UUID), name (string), description (string), tenant_id (FK), created_at (timestamp), is_custom (boolean), permissions (JSON array of permission IDs)
- **Permission**: ID (UUID), resource (string), action (enum: view/create/edit/delete/export), description (string), tenant_id (FK)
- **Session**: ID (UUID), user_id (FK), token (string), refresh_token (string), created_at (timestamp), expires_at (timestamp), ip_address (string), user_agent (string), status (enum: active/revoked)
- **AuthenticationLog**: ID (UUID), user_id (FK), event_type (enum: login/logout/failed_login/mfa_enabled), timestamp (timestamp), ip_address (string), user_agent (string), status (enum: success/failure), failure_reason (string)

#### User Workflows

**For Owner (Full Access):**
1. Log in with email and password
2. Complete MFA if enabled
3. Access dashboard with all features
4. Manage staff and permissions
5. View all business data and reports
6. Configure system settings

**For Manager (Operational Access):**
1. Log in with email and password
2. Complete MFA if enabled
3. Access staff management features
4. View and manage appointments
5. View financial reports
6. Cannot access system settings or staff permissions

**For Staff (Limited Access):**
1. Log in with email and password
2. View only their assigned appointments
3. Access customer profiles for their appointments
4. Cannot access financial data or staff management
5. Can update their own profile

**For Customer (Self-Service):**
1. Sign up or log in
2. View their own appointments
3. Book new appointments
4. Manage their profile
5. View their invoices and payment history

#### Edge Cases & Constraints

- **Password Reset**: Implement secure password reset via email link (valid for 1 hour only)
- **Account Lockout**: Lock account after 5 failed login attempts for 30 minutes
- **Session Hijacking**: Detect and invalidate sessions from unusual locations/devices
- **Permission Inheritance**: Child roles inherit parent permissions; prevent circular role hierarchies
- **Inactive Accounts**: Automatically disable accounts inactive for 90 days; require password reset on reactivation
- **Concurrent Sessions**: Limit to 5 concurrent sessions per user; allow user to manage active sessions
- **API Token Rotation**: Support API token rotation for service accounts; maintain backward compatibility during rotation

#### Performance Requirements

- **Login Time**: Complete authentication within 500ms
- **Permission Check**: Verify permissions within 10ms (cached)
- **Token Validation**: Validate JWT token within 5ms
- **Session Lookup**: Retrieve session data within 20ms
- **Permission Cache Hit Rate**: Maintain >95% cache hit rate for permission checks

#### Security Considerations

- **Password Storage**: Never store plain text passwords; use Bcrypt with salt rounds ≥12; minimum 8 characters with complexity requirements
- **Token Security**: JWT tokens signed with RS256 algorithm; tokens include tenant_id and user_id
- **HTTPS Only**: All authentication traffic over HTTPS; set Secure and HttpOnly flags on cookies
- **CSRF Protection**: Implement CSRF tokens for state-changing operations
- **Brute Force Protection**: Rate limit login attempts; implement exponential backoff
- **Session Fixation**: Generate new session ID after successful login
- **Privilege Escalation**: Prevent users from modifying their own permissions or role
- **Audit Trail**: Log all authentication events and permission changes

#### Compliance Requirements

- **GDPR**: Support user data export and deletion; maintain audit logs of data access
- **SOC 2**: Implement access controls, audit logging, and session management
- **HIPAA**: If storing health information, enforce MFA for all users; maintain detailed audit logs
- **PCI-DSS**: If handling payments, enforce strong authentication; never store payment credentials

#### Acceptance Criteria

1. WHEN a user logs in with valid credentials, THE System SHALL authenticate them and create a secure session
2. WHEN a user with Owner role accesses settings, THE System SHALL grant full platform access
3. WHEN a user with Manager role accesses staff management, THE System SHALL allow viewing and editing staff schedules
4. WHEN a user with Staff role attempts to access billing, THE System SHALL deny access and show permission error
5. WHEN a user with Customer role logs in, THE System SHALL display only their own appointments and profile
6. WHEN a user's role changes, THE System SHALL immediately revoke previous permissions and grant new ones
7. WHEN a user logs out, THE System SHALL invalidate their session and clear authentication tokens

#### Business Value

- Prevents unauthorized access to sensitive data
- Reduces operational errors from staff accessing wrong features
- Enables secure delegation of responsibilities
- Supports compliance requirements

#### Dependencies

- Multi-tenant architecture (Requirement 1)
- User management system

#### Key Data Entities

- User (ID, email, password_hash, role, tenant_id, created_at)
- Role (ID, name, permissions)
- Permission (ID, resource, action)
- Session (ID, user_id, token, expires_at)

#### User Roles

- Owner: Full platform access
- Manager: Staff and operational management
- Staff: Limited to assigned services and schedule
- Customer: Self-service appointment booking and profile

---

### Requirement 4: Appointment Booking System with Calendar Views and Availability

**User Story:** As a customer, I want to book appointments online with real-time availability, so that I can schedule services at my convenience without calling the business.

#### Detailed Description

The appointment booking system is the core revenue-generating feature of the platform, enabling customers to self-service book appointments with real-time availability. The system intelligently manages availability based on staff schedules, resource availability, and service duration, preventing double-booking while maximizing utilization. Real-time availability updates ensure customers always see current slots, reducing frustration from booking unavailable times.

The system supports multiple calendar views (day, week, month) for different user needs. Customers can filter by staff member, service type, or location. The booking process includes a temporary reservation period (10 minutes) to prevent race conditions where multiple customers book the same slot simultaneously. Confirmation emails are sent immediately upon booking, and reminders are sent 24 hours and 1 hour before the appointment.

The system tracks appointment status throughout the lifecycle (scheduled, confirmed, in-progress, completed, cancelled, no-show) and supports rescheduling and cancellation with configurable policies. Analytics track booking patterns, peak times, and no-show rates to inform business decisions.

#### Technical Specifications

- **Availability Calculation**: Real-time calculation based on staff schedules, resource availability, and service duration
- **Slot Reservation**: Temporary 10-minute reservation to prevent race conditions; automatic release if not confirmed
- **Double-Booking Prevention**: Database-level constraints to prevent overlapping appointments
- **Calendar Views**: Day (hourly slots), Week (7-day grid), Month (overview with event counts)
- **Filtering**: By staff member, service type, location, date range
- **Timezone Support**: Store all times in UTC; display in user's local timezone
- **Recurring Appointments**: Support recurring bookings (weekly, bi-weekly, monthly)
- **Waitlist**: Automatic waitlist when no slots available; notify when slots open

#### Business Context

- **Problem Solved**: Eliminates phone-based booking bottleneck; enables 24/7 self-service booking
- **ROI**: Increases bookings by 30-40% through convenience; reduces administrative overhead by 50%
- **Competitive Advantage**: Modern booking experience expected by customers; differentiates from competitors with phone-only booking

#### Integration Points

- **Staff Scheduling (Req 4)**: Availability based on staff schedules and shifts
- **Resource Management (Req 8)**: Availability based on resource availability
- **Notifications (Req 7)**: Send confirmation and reminder emails/SMS
- **Billing & Payment (Req 6)**: Create invoice upon appointment completion
- **Customer Profiles (Req 5)**: Display customer history and preferences
- **Waiting Room (Req 9)**: Track check-in and queue status

#### Data Model Details

- **Appointment**: ID (UUID), customer_id (FK), staff_id (FK), service_id (FK), location_id (FK), start_time (timestamp), end_time (timestamp), status (enum: scheduled/confirmed/in-progress/completed/cancelled/no-show), notes (text), created_at (timestamp), updated_at (timestamp), tenant_id (FK), cancellation_reason (string, nullable), no_show_reason (string, nullable)
- **Service**: ID (UUID), name (string), description (text), duration_minutes (integer), price (decimal), category (string), tenant_id (FK), is_active (boolean), requires_deposit (boolean), deposit_amount (decimal)
- **Availability**: ID (UUID), staff_id (FK), day_of_week (enum: 0-6), start_time (time), end_time (time), is_recurring (boolean), effective_from (date), effective_to (date, nullable), tenant_id (FK)
- **TimeSlot**: ID (UUID), appointment_id (FK), reserved_until (timestamp), reservation_token (string)
- **AppointmentHistory**: ID (UUID), appointment_id (FK), status_change (enum), changed_at (timestamp), changed_by (FK), reason (string)

#### User Workflows

**For Customer Booking:**
1. Visit booking page or open mobile app
2. Select service type (optional filter)
3. Select preferred staff member (optional)
4. Select date and view available time slots
5. Select preferred time slot
6. Confirm appointment details (service, staff, time, price)
7. Complete payment if required
8. Receive confirmation email with appointment details
9. Receive reminder emails 24 hours and 1 hour before appointment

**For Staff Viewing Appointments:**
1. Log in to staff dashboard
2. View calendar with their appointments
3. See customer details and appointment notes
4. Mark appointment as in-progress when customer arrives
5. Mark appointment as completed when finished
6. Add notes or follow-up items

**For Manager Managing Appointments:**
1. View all appointments across all staff
2. Manually create appointments for customers
3. Reschedule appointments if needed
4. Cancel appointments with reason
5. View no-show analytics
6. Identify peak times and capacity issues

#### Edge Cases & Constraints

- **Race Condition**: Multiple customers booking same slot simultaneously; prevent with database-level locking
- **Timezone Issues**: Handle daylight saving time transitions; store all times in UTC
- **Recurring Appointments**: Handle series cancellation vs. single instance cancellation
- **Service Duration**: Some services may require multiple staff members or resources
- **Minimum Notice**: Enforce minimum booking notice (e.g., 24 hours) for some services
- **Maximum Advance Booking**: Limit how far in advance customers can book (e.g., 90 days)
- **Cancellation Policies**: Different cancellation policies for different services or time windows
- **No-Show Handling**: Track no-shows; implement no-show fees or account suspension after threshold

#### Performance Requirements

- **Availability Calculation**: Calculate available slots within 500ms
- **Slot Reservation**: Reserve slot within 100ms
- **Calendar Load**: Load calendar view within 1 second
- **Booking Confirmation**: Send confirmation email within 1 minute
- **Concurrent Bookings**: Support 1000 concurrent booking requests without race conditions

#### Security Considerations

- **Customer Data**: Verify customer owns appointment before allowing modifications
- **Staff Data**: Prevent customers from seeing staff personal information
- **Payment Data**: Never store full credit card numbers; use tokenization
- **Audit Trail**: Log all appointment changes with user and timestamp
- **Rate Limiting**: Limit booking requests per customer to prevent abuse

#### Compliance Requirements

- **GDPR**: Support appointment data export and deletion
- **HIPAA**: If storing health information, encrypt and audit access
- **Accessibility**: Ensure booking interface is WCAG 2.1 AA compliant

#### Acceptance Criteria

1. WHEN a customer views the booking interface, THE System SHALL display available time slots based on staff availability and service duration
2. WHEN a customer selects a time slot, THE System SHALL reserve it temporarily for 10 minutes while they complete booking
3. WHEN a customer confirms booking, THE System SHALL create the appointment and send confirmation email
4. WHEN staff availability changes, THE System SHALL immediately update available slots for customers
5. WHEN an appointment is booked, THE System SHALL prevent double-booking of the same staff member or resource
6. WHEN viewing calendar, THE System SHALL display appointments in day, week, and month views
7. WHEN a customer cancels an appointment, THE System SHALL release the time slot and notify staff

#### Business Value

- Increases appointment bookings through convenience
- Reduces phone call volume and administrative overhead
- Minimizes no-shows through confirmation emails
- Improves customer satisfaction

#### Dependencies

- User authentication (Requirement 2)
- Staff scheduling (Requirement 4)
- Resource management (Requirement 8)
- Notifications (Requirement 7)

#### Key Data Entities

- Appointment (ID, customer_id, staff_id, service_id, start_time, end_time, status, tenant_id)
- Service (ID, name, duration, price, tenant_id)
- Availability (ID, staff_id, day_of_week, start_time, end_time, tenant_id)
- TimeSlot (ID, appointment_id, reserved_until)

#### User Roles

- Customer: Books appointments
- Staff: Views their appointments
- Manager: Manages all appointments

---

### Requirement 5: Staff Profiles, Scheduling, and Shift Management

**User Story:** As a manager, I want to manage staff schedules and shifts efficiently, so that I can ensure adequate coverage and optimize labor costs.

#### Detailed Description

The staff management system enables managers to create and maintain staff profiles, define work schedules, and manage shifts efficiently. Each staff member has a comprehensive profile including contact information, specialties, certifications, and hourly rates. The system supports flexible scheduling with recurring weekly patterns, custom date ranges, and one-off shifts.

Shift management includes automatic conflict detection to prevent double-booking, labor cost calculation based on hourly rates, and integration with payroll systems. The system tracks staff availability in real-time, enabling the appointment booking system to display accurate availability to customers. Staff can request time off through the system, with manager approval workflows.

The system provides visibility into labor costs, enabling managers to optimize staffing levels and identify opportunities for cost reduction. Analytics track staff utilization, productivity, and performance metrics to inform hiring and training decisions.

#### Technical Specifications

- **Schedule Types**: Recurring weekly patterns, custom date ranges, one-off shifts
- **Conflict Detection**: Prevent overlapping shifts; validate staff availability before booking
- **Labor Cost Calculation**: Automatic calculation based on hourly rate and shift duration
- **Shift Templates**: Pre-defined shift patterns (e.g., 9-5, split shifts) for quick scheduling
- **Bulk Scheduling**: Import schedules from CSV or calendar files
- **Shift Swapping**: Enable staff to swap shifts with manager approval
- **Time Tracking**: Optional clock-in/clock-out for accurate time tracking
- **Payroll Integration**: Export shift data for payroll processing

#### Business Context

- **Problem Solved**: Eliminates manual scheduling overhead; prevents scheduling conflicts and understaffing
- **ROI**: Reduces scheduling errors by 90%; saves 5-10 hours per week in scheduling work
- **Competitive Advantage**: Transparent scheduling improves staff satisfaction and retention

#### Integration Points

- **Appointment Booking (Req 3)**: Availability based on staff schedules
- **Notifications (Req 7)**: Notify staff of shift assignments and changes
- **Time-Off Requests (Req 10)**: Manage time off requests and approvals
- **Payroll Systems**: Export shift data for payroll processing
- **Performance Metrics (Req 21)**: Track staff productivity and utilization

#### Data Model Details

- **Staff**: ID (UUID), user_id (FK), first_name (string), last_name (string), email (string), phone (string), specialties (JSON array), certifications (JSON array), hourly_rate (decimal), hire_date (date), status (enum: active/inactive/terminated), tenant_id (FK)
- **Shift**: ID (UUID), staff_id (FK), start_time (timestamp), end_time (timestamp), shift_type (enum: regular/overtime/on-call), status (enum: scheduled/confirmed/completed/cancelled), notes (text), tenant_id (FK)
- **Availability**: ID (UUID), staff_id (FK), recurring_pattern (JSON), start_date (date), end_date (date, nullable), tenant_id (FK)
- **TimeOffRequest**: ID (UUID), staff_id (FK), start_date (date), end_date (date), reason (string), status (enum: pending/approved/denied), requested_at (timestamp), approved_by (FK), approval_date (date, nullable), tenant_id (FK)
- **ShiftTemplate**: ID (UUID), name (string), start_time (time), end_time (time), tenant_id (FK)

#### User Workflows

**For Manager Creating Shifts:**
1. Access shift scheduling interface
2. Select staff member and date range
3. Choose shift template or create custom shift
4. Set hourly rate and shift type
5. Validate no conflicts exist
6. Save shift and notify staff
7. Monitor shift coverage

**For Staff Viewing Schedule:**
1. Log in to staff dashboard
2. View their schedule for current and future weeks
3. See shift details (time, location, notes)
4. Request time off or shift swap
5. Clock in/out if time tracking enabled
6. View their earnings and hours

**For Manager Managing Time Off:**
1. Receive time off request from staff
2. Review request and check coverage
3. Approve or deny request
4. Notify staff of decision
5. Update schedule if approved
6. Plan coverage for approved time off

#### Edge Cases & Constraints

- **Shift Conflicts**: Prevent overlapping shifts; detect conflicts before saving
- **Minimum Rest Period**: Enforce minimum rest period between shifts (e.g., 11 hours)
- **Maximum Hours**: Enforce maximum hours per week to prevent burnout
- **Shift Swaps**: Validate both staff members are qualified for each other's shifts
- **Shift Cancellation**: Handle cancellation with appropriate notice period
- **Payroll Cutoff**: Lock shifts after payroll cutoff date to prevent changes
- **Recurring Shifts**: Handle changes to recurring shifts (single instance vs. series)

#### Performance Requirements

- **Schedule Load**: Load staff schedule within 500ms
- **Conflict Detection**: Detect conflicts within 100ms
- **Bulk Import**: Import 1000 shifts within 5 seconds
- **Labor Cost Calculation**: Calculate costs for all staff within 1 second

#### Security Considerations

- **Salary Information**: Restrict access to hourly rates to managers and payroll
- **Personal Information**: Restrict access to staff personal information
- **Audit Trail**: Log all schedule changes with user and timestamp
- **Shift Modifications**: Require manager approval for shift changes after confirmation

#### Compliance Requirements

- **Labor Laws**: Enforce minimum rest periods and maximum hours per labor laws
- **Overtime Tracking**: Track and flag overtime for compliance
- **Payroll Accuracy**: Maintain accurate records for payroll and tax purposes

#### Acceptance Criteria

1. WHEN creating a staff profile, THE System SHALL capture name, contact info, specialties, certifications, and hourly rate
2. WHEN setting staff availability, THE System SHALL allow recurring weekly schedules or custom date ranges
3. WHEN a staff member is assigned to a shift, THE System SHALL validate no scheduling conflicts exist
4. WHEN viewing staff schedule, THE System SHALL display all shifts, appointments, and breaks in a calendar view
5. WHEN a staff member requests time off, THE System SHALL notify the manager for approval
6. WHEN a shift is created, THE System SHALL calculate labor costs based on hourly rate and duration
7. WHEN staff availability is updated, THE System SHALL immediately reflect changes in customer booking interface

#### Business Value

- Reduces scheduling conflicts and overtime costs
- Improves staff satisfaction through transparent scheduling
- Enables data-driven labor planning
- Prevents understaffing situations

#### Dependencies

- User authentication (Requirement 2)
- Appointment booking (Requirement 3)
- Notifications (Requirement 7)

#### Key Data Entities

- Staff (ID, user_id, specialties, certifications, hourly_rate, tenant_id)
- Shift (ID, staff_id, start_time, end_time, status, tenant_id)
- Availability (ID, staff_id, recurring_pattern, tenant_id)
- TimeOffRequest (ID, staff_id, start_date, end_date, status, tenant_id)

#### User Roles

- Manager: Creates and manages shifts
- Staff: Views their schedule and requests time off
- Owner: Views labor cost analytics

---

### Requirement 6: Customer Profiles with History and Preferences

**User Story:** As a staff member, I want to access customer history and preferences, so that I can provide personalized service and improve customer satisfaction.

#### Detailed Description

The customer profile system maintains comprehensive customer information including contact details, service history, preferences, and medical/allergy information. Staff members can quickly access customer history before appointments to provide personalized service. The system tracks all customer interactions, enabling businesses to understand customer preferences and tailor services accordingly.

Customer profiles support storing sensitive health information (with appropriate security and compliance measures), enabling personalized recommendations and preventing allergic reactions or contraindications. Customers can manage their own profiles, updating preferences and contact information. The system maintains audit logs of all profile access for compliance.

Analytics track customer lifetime value, visit frequency, and service preferences to inform marketing and service decisions. The system supports customer segmentation based on profile data, enabling targeted marketing campaigns.

#### Technical Specifications

- **Profile Data**: Contact info, service history, preferences, medical/allergy information, communication preferences
- **Medical Information**: Encrypted storage with audit logging of all access
- **Service History**: Complete record of all appointments, services, and staff
- **Preferences**: Preferred staff, service types, communication methods, time preferences
- **Data Export**: Support GDPR data export in standard format (JSON, CSV)
- **Data Deletion**: Support GDPR right to be forgotten with secure deletion
- **Audit Logging**: Log all profile access with user, timestamp, and action

#### Business Context

- **Problem Solved**: Enables personalized service delivery; prevents allergic reactions and service issues
- **ROI**: Increases customer satisfaction by 25-30%; enables upselling through preference-based recommendations
- **Competitive Advantage**: Personalized service differentiates from competitors; builds customer loyalty

#### Integration Points

- **Appointment Booking (Req 3)**: Display customer history and preferences during booking
- **Notifications (Req 7)**: Use preferences for communication method selection
- **Customer Feedback (Req 14)**: Track feedback and preferences over time
- **Audit Logging (Req 41)**: Log all profile access for compliance

#### Data Model Details

- **Customer**: ID (UUID), user_id (FK), phone (string), date_of_birth (date, nullable), address (string), city (string), state (string), zip_code (string), medical_info (text, encrypted), allergy_info (text, encrypted), emergency_contact (string), tenant_id (FK), created_at (timestamp), updated_at (timestamp)
- **CustomerPreference**: ID (UUID), customer_id (FK), preferred_staff_ids (JSON array), preferred_service_types (JSON array), communication_method (enum: email/sms/phone), preferred_time_slots (JSON), language (string), tenant_id (FK)
- **AppointmentHistory**: ID (UUID), customer_id (FK), appointment_id (FK), service_id (FK), staff_id (FK), notes (text), rating (integer 1-5), feedback (text), tenant_id (FK)
- **AccessLog**: ID (UUID), customer_id (FK), accessed_by (FK), access_type (enum: view/edit/export), timestamp (timestamp), ip_address (string), tenant_id (FK)

#### User Workflows

**For Staff Viewing Customer Profile:**
1. Search for customer by name or phone
2. View customer profile with history
3. See medical/allergy information
4. Review previous appointments and services
5. See customer preferences and notes
6. Provide personalized service based on history

**For Customer Managing Profile:**
1. Log in to customer portal
2. View and edit personal information
3. Update preferences (preferred staff, services, communication)
4. View appointment history
5. Export profile data if needed
6. Request profile deletion

**For Manager Analyzing Customers:**
1. View customer segmentation
2. Identify high-value customers
3. Track customer lifetime value
4. Analyze service preferences
5. Plan targeted marketing campaigns

#### Edge Cases & Constraints

- **Medical Information**: Encrypt sensitive health data; restrict access to authorized staff only
- **Data Retention**: Comply with data retention policies; delete data after customer inactivity period
- **Profile Merging**: Handle duplicate customer profiles; merge data safely
- **Data Export**: Support GDPR data export in standard format
- **Profile Deletion**: Securely delete all customer data upon request; maintain audit trail
- **Consent Management**: Track customer consent for data processing and marketing

#### Performance Requirements

- **Profile Load**: Load customer profile within 200ms
- **History Display**: Display appointment history within 500ms
- **Search**: Search customers by name/phone within 300ms
- **Data Export**: Export customer data within 5 seconds

#### Security Considerations

- **Medical Information**: Encrypt sensitive health data at rest and in transit
- **Access Control**: Restrict access to medical information to authorized staff only
- **Audit Trail**: Log all profile access with user, timestamp, and action
- **Data Minimization**: Only collect necessary information; delete unnecessary data
- **Consent**: Obtain explicit consent for storing sensitive information

#### Compliance Requirements

- **GDPR**: Support data export and deletion; maintain audit logs of data access
- **HIPAA**: If storing health information, encrypt and audit all access
- **CCPA**: Support consumer privacy rights (access, deletion, opt-out)

#### Acceptance Criteria

1. WHEN a customer creates an account, THE System SHALL capture name, contact info, preferences, and medical/allergy information
2. WHEN viewing a customer profile, THE System SHALL display complete appointment history with dates, services, and staff
3. WHEN a customer updates preferences, THE System SHALL store preferred staff, service types, and communication methods
4. WHEN a staff member views a customer before appointment, THE System SHALL display relevant history and preferences
5. WHEN a customer books an appointment, THE System SHALL suggest services based on history
6. WHEN customer data is accessed, THE System SHALL log the access for audit purposes
7. WHEN a customer requests data export, THE System SHALL provide their complete profile in standard format

#### Business Value

- Enables personalized service delivery
- Increases customer loyalty through preference tracking
- Supports compliance with data access regulations
- Improves service quality through historical context

#### Dependencies

- User authentication (Requirement 2)
- Appointment booking (Requirement 3)
- Notifications (Requirement 7)

#### Key Data Entities

- Customer (ID, user_id, phone, preferences, medical_info, tenant_id)
- CustomerPreference (ID, customer_id, preferred_staff, service_types, communication_method)
- AppointmentHistory (ID, customer_id, appointment_id, notes, tenant_id)
- AccessLog (ID, customer_id, accessed_by, timestamp, tenant_id)

#### User Roles

- Customer: Manages their profile
- Staff: Views customer profiles
- Manager: Manages customer data policies

---

### Requirement 7: Billing & Payment Processing

**User Story:** As a business owner, I want automated billing and payment processing, so that I can collect revenue efficiently and reduce administrative overhead.

#### Detailed Description

The billing and payment processing system automates invoice generation, payment collection, and financial reconciliation. Upon appointment completion, invoices are automatically generated based on service pricing, applied discounts, and taxes. The system integrates with multiple payment gateways (Stripe, Square, PayPal) to process payments securely.

The system handles payment failures gracefully, retrying failed payments up to 3 times with exponential backoff. Customers receive payment receipts immediately upon successful payment. The system tracks payment status, enabling businesses to identify outstanding payments and follow up with customers. Refunds are processed through the payment gateway, maintaining audit trails for compliance.

Financial dashboards provide real-time visibility into revenue, outstanding payments, and payment success rates. The system supports multiple billing models including per-appointment billing, package/membership billing, and subscription billing.

#### Technical Specifications

- **Invoice Generation**: Automatic upon appointment completion; includes service details, pricing, taxes, discounts
- **Payment Processing**: Integration with Stripe, Square, PayPal; PCI-DSS compliant
- **Payment Retry**: Automatic retry up to 3 times with exponential backoff (1 min, 5 min, 15 min)
- **Refund Processing**: Process refunds through payment gateway; maintain audit trail
- **Tax Calculation**: Automatic tax calculation based on service type and location
- **Discount Support**: Support percentage and fixed-amount discounts; track discount usage
- **Payment Methods**: Credit card, debit card, digital wallets (Apple Pay, Google Pay)
- **Billing Models**: Per-appointment, package/membership, subscription

#### Business Context

- **Problem Solved**: Eliminates manual invoicing and payment collection; reduces payment processing errors
- **ROI**: Increases cash flow by 20-30% through faster payment collection; reduces administrative overhead by 40%
- **Competitive Advantage**: Automated billing improves customer experience; enables flexible billing models

#### Integration Points

- **Appointment Booking (Req 3)**: Create invoice upon appointment completion
- **Customer Profiles (Req 5)**: Store customer payment information securely
- **Notifications (Req 7)**: Send payment receipts and reminders
- **Payment Gateways (Req 45)**: Process payments through multiple gateways
- **Accounting Software (Req 48)**: Sync financial data to accounting software
- **Financial Reconciliation (Req 19)**: Reconcile payments with invoices

#### Data Model Details

- **Invoice**: ID (UUID), appointment_id (FK), customer_id (FK), amount (decimal), tax (decimal), discount (decimal), total (decimal), status (enum: draft/sent/paid/overdue/cancelled), created_at (timestamp), due_date (date), paid_at (timestamp, nullable), tenant_id (FK)
- **InvoiceLineItem**: ID (UUID), invoice_id (FK), service_id (FK), quantity (integer), unit_price (decimal), total (decimal), tenant_id (FK)
- **Payment**: ID (UUID), invoice_id (FK), amount (decimal), method (enum: credit_card/debit_card/digital_wallet), status (enum: pending/processing/completed/failed/refunded), transaction_id (string), gateway_response (JSON), created_at (timestamp), completed_at (timestamp, nullable), tenant_id (FK)
- **Refund**: ID (UUID), payment_id (FK), amount (decimal), reason (string), status (enum: pending/processing/completed/failed), transaction_id (string), created_at (timestamp), completed_at (timestamp, nullable), tenant_id (FK)
- **CustomerBalance**: ID (UUID), customer_id (FK), balance (decimal), last_updated (timestamp), tenant_id (FK)

#### User Workflows

**For Customer Making Payment:**
1. Receive invoice via email
2. Click payment link or log into customer portal
3. View invoice details and amount due
4. Select payment method
5. Enter payment information
6. Complete payment
7. Receive payment receipt

**For Manager Processing Refund:**
1. Receive refund request from customer
2. Verify refund eligibility based on policy
3. Calculate refund amount
4. Initiate refund through payment gateway
5. Notify customer of refund
6. Track refund status

**For Owner Viewing Financial Dashboard:**
1. View total revenue for period
2. See outstanding payments
3. Track payment success rate
4. Identify overdue invoices
5. View refund trends
6. Export financial reports

#### Edge Cases & Constraints

- **Payment Failures**: Retry failed payments up to 3 times; notify customer after final failure
- **Partial Payments**: Support partial payments; track remaining balance
- **Refund Policies**: Enforce refund policies based on cancellation time
- **Tax Calculation**: Handle different tax rates by location and service type
- **Currency**: Support multiple currencies; handle currency conversion
- **Duplicate Payments**: Prevent duplicate payments through idempotency keys
- **Payment Disputes**: Track disputed payments; escalate to payment gateway

#### Performance Requirements

- **Invoice Generation**: Generate invoice within 1 second of appointment completion
- **Payment Processing**: Process payment within 3 seconds
- **Payment Retry**: Retry failed payments within configured intervals
- **Financial Dashboard**: Load dashboard within 2 seconds
- **Refund Processing**: Process refund within 5 seconds

#### Security Considerations

- **PCI-DSS Compliance**: Never store full credit card numbers; use tokenization
- **Payment Data**: Encrypt payment data at rest and in transit
- **API Keys**: Store payment gateway API keys securely; rotate regularly
- **Audit Trail**: Log all payment transactions with user, timestamp, and amount
- **Fraud Detection**: Implement fraud detection for unusual payment patterns

#### Compliance Requirements

- **PCI-DSS**: Comply with PCI-DSS requirements for payment processing
- **GDPR**: Support payment data export and deletion
- **SOC 2**: Implement controls for payment processing and audit logging

#### Acceptance Criteria

1. WHEN an appointment is completed, THE System SHALL automatically generate an invoice based on service price and applied discounts
2. WHEN a customer pays, THE System SHALL process payment through integrated payment gateway and confirm transaction
3. WHEN payment fails, THE System SHALL retry up to 3 times and notify customer of payment issues
4. WHEN a refund is requested, THE System SHALL process it through the payment gateway and update invoice status
5. WHEN generating reports, THE System SHALL calculate total revenue, outstanding payments, and payment success rates
6. WHEN a customer has outstanding balance, THE System SHALL prevent new appointment booking until resolved
7. WHEN payment is received, THE System SHALL send receipt and update customer account balance

#### Business Value

- Increases cash flow through automated collection
- Reduces payment processing errors
- Improves financial visibility
- Enables subscription and package management

#### Dependencies

- Appointment booking (Requirement 3)
- Customer profiles (Requirement 5)
- Payment gateway integration (Phase 4)
- Notifications (Requirement 7)

#### Key Data Entities

- Invoice (ID, appointment_id, amount, status, created_at, tenant_id)
- Payment (ID, invoice_id, amount, method, status, transaction_id, tenant_id)
- Refund (ID, payment_id, amount, reason, status, tenant_id)
- CustomerBalance (ID, customer_id, balance, tenant_id)

#### User Roles

- Owner: Views financial reports
- Manager: Processes refunds
- Customer: Views invoices and makes payments

---

### Requirement 8: Email/SMS Notifications

**User Story:** As a business owner, I want automated notifications to reduce no-shows and improve communication, so that customers stay informed and staff can coordinate effectively.

#### Detailed Description

The notification system sends automated emails and SMS messages to customers and staff at key points in the appointment lifecycle. Notifications include appointment confirmations, reminders (24 hours and 1 hour before), cancellations, and payment receipts. The system is highly configurable, allowing businesses to customize notification templates, timing, and channels.

Notifications are sent asynchronously to prevent blocking the main application. The system tracks delivery status, enabling businesses to identify failed notifications and take corrective action. Customers can manage notification preferences, opting out of specific notification types or channels. The system respects customer preferences, ensuring compliance with anti-spam regulations.

Analytics track notification effectiveness, measuring open rates, click rates, and impact on no-show rates. The system supports A/B testing of notification templates to optimize effectiveness.

#### Technical Specifications

- **Channels**: Email (SMTP), SMS (Twilio), push notifications (mobile app)
- **Async Processing**: Queue-based system for reliable delivery; retry failed notifications
- **Template System**: Customizable templates with variable substitution (customer name, appointment time, etc.)
- **Scheduling**: Send notifications at specific times (e.g., 24 hours before appointment)
- **Delivery Tracking**: Track delivery status (sent, delivered, failed, bounced)
- **Preference Management**: Allow customers to opt out of specific notification types
- **Rate Limiting**: Prevent notification spam; limit to 1 notification per customer per hour
- **Internationalization**: Support multiple languages for notifications

#### Business Context

- **Problem Solved**: Reduces no-show rates by 30-40% through timely reminders
- **ROI**: Prevents revenue loss from no-shows; reduces administrative follow-up work
- **Competitive Advantage**: Proactive communication improves customer experience and satisfaction

#### Integration Points

- **Appointment Booking (Req 3)**: Send confirmation and reminder notifications
- **Email Provider (Req 49)**: Send emails through reliable email provider
- **SMS Provider (Req 46)**: Send SMS through Twilio or similar
- **Customer Profiles (Req 5)**: Use customer preferences for notification channels
- **Notifications (Req 7)**: Core notification system

#### Data Model Details

- **Notification**: ID (UUID), recipient_id (FK), recipient_type (enum: customer/staff), type (enum: confirmation/reminder/cancellation/payment), content (text), channel (enum: email/sms/push), status (enum: pending/sent/delivered/failed/bounced), created_at (timestamp), sent_at (timestamp, nullable), delivered_at (timestamp, nullable), tenant_id (FK)
- **NotificationTemplate**: ID (UUID), type (enum), channel (enum), subject (string), body (text), variables (JSON array), tenant_id (FK)
- **NotificationLog**: ID (UUID), notification_id (FK), status (enum), error_message (text, nullable), retry_count (integer), last_retry_at (timestamp, nullable), tenant_id (FK)
- **NotificationPreference**: ID (UUID), customer_id (FK), notification_type (enum), channel (enum), enabled (boolean), tenant_id (FK)

#### User Workflows

**For Customer Receiving Notification:**
1. Receive appointment confirmation email/SMS
2. Click link to view appointment details
3. Receive reminder 24 hours before appointment
4. Receive reminder 1 hour before appointment
5. Receive payment receipt after appointment
6. Manage notification preferences in customer portal

**For Manager Configuring Notifications:**
1. Access notification settings
2. Customize notification templates
3. Set notification timing (e.g., 24 hours before)
4. Select notification channels (email, SMS)
5. Test notifications
6. Enable/disable notification types

**For Owner Analyzing Notification Effectiveness:**
1. View notification delivery rates
2. Track open rates and click rates
3. Measure impact on no-show rates
4. Analyze notification performance by type
5. Identify failed notifications
6. Optimize notification templates

#### Edge Cases & Constraints

- **Delivery Failures**: Retry failed notifications up to 3 times with exponential backoff
- **Bounced Emails**: Track bounced emails; disable notifications for invalid addresses
- **Opt-Out**: Respect customer opt-out preferences; maintain compliance with anti-spam laws
- **Timezone Issues**: Send notifications in customer's local timezone
- **Rate Limiting**: Prevent notification spam; limit to 1 per customer per hour
- **Template Variables**: Handle missing variables gracefully; use defaults if needed
- **Internationalization**: Support multiple languages; use customer's preferred language

#### Performance Requirements

- **Notification Sending**: Send notification within 1 second of trigger event
- **Delivery Tracking**: Update delivery status within 5 seconds
- **Template Rendering**: Render template with variables within 100ms
- **Retry Processing**: Process retries within configured intervals

#### Security Considerations

- **Data Privacy**: Never include sensitive information in notifications
- **Unsubscribe Links**: Include unsubscribe link in all marketing notifications
- **Authentication**: Verify recipient identity before sending sensitive information
- **Audit Trail**: Log all notifications sent with recipient, timestamp, and content

#### Compliance Requirements

- **GDPR**: Obtain consent before sending marketing notifications; provide unsubscribe option
- **CAN-SPAM**: Include business address and unsubscribe link in all emails
- **TCPA**: Obtain consent before sending SMS; respect do-not-call lists

#### Acceptance Criteria

1. WHEN an appointment is booked, THE System SHALL send confirmation email/SMS to customer within 1 minute
2. WHEN an appointment is 24 hours away, THE System SHALL send reminder notification to customer
3. WHEN an appointment is cancelled, THE System SHALL notify both customer and staff
4. WHEN a staff member is assigned to a shift, THE System SHALL send notification with shift details
5. WHEN a customer requests time off, THE System SHALL notify manager for approval
6. WHEN payment is received, THE System SHALL send receipt notification to customer
7. WHEN a notification fails to send, THE System SHALL retry up to 3 times and log the failure

#### Business Value

- Reduces no-show rates by 30-40%
- Improves staff coordination
- Enhances customer communication
- Reduces manual follow-up work

#### Dependencies

- Appointment booking (Requirement 3)
- Customer profiles (Requirement 5)
- Email/SMS provider integration (Phase 4)

#### Key Data Entities

- Notification (ID, recipient_id, type, content, status, sent_at, tenant_id)
- NotificationTemplate (ID, type, subject, body, tenant_id)
- NotificationLog (ID, notification_id, status, error_message, retry_count, tenant_id)

#### User Roles

- Owner: Configures notification templates
- System: Sends notifications automatically

---

### Requirement 9: Resource Management (Chairs, Treatment Rooms, Equipment)

**User Story:** As a manager, I want to track and manage physical resources, so that I can optimize utilization and prevent resource conflicts.

#### Detailed Description

The resource management system tracks physical assets required for service delivery, including treatment rooms, chairs, equipment, and other resources. Each resource has an availability schedule, enabling the system to prevent double-booking and optimize utilization. Resources can be assigned to specific locations and staff members.

The system supports resource maintenance scheduling, marking resources as unavailable during maintenance periods. Analytics track resource utilization, identifying underutilized resources and opportunities for optimization. The system supports resource capacity tracking, enabling businesses to manage limited resources effectively.

Resources can have dependencies on other resources (e.g., a service requires both a treatment room and specific equipment). The system validates these dependencies during booking, ensuring all required resources are available.

#### Technical Specifications

- **Resource Types**: Treatment rooms, chairs, equipment, tools, supplies
- **Availability Scheduling**: Define availability by day of week or custom date ranges
- **Capacity Tracking**: Track quantity of each resource type
- **Maintenance Scheduling**: Mark resources unavailable for maintenance
- **Resource Dependencies**: Define which resources are required for each service
- **Utilization Analytics**: Track usage patterns and identify optimization opportunities
- **Resource Assignment**: Assign resources to locations and staff members
- **Bulk Operations**: Import/export resource data

#### Business Context

- **Problem Solved**: Prevents resource conflicts and double-booking; optimizes resource utilization
- **ROI**: Increases resource utilization by 20-30%; prevents service disruptions from resource unavailability
- **Competitive Advantage**: Efficient resource management enables higher capacity and better service quality

#### Integration Points

- **Appointment Booking (Req 3)**: Automatically assign available resources during booking
- **Staff Scheduling (Req 4)**: Assign resources to staff members
- **Maintenance Tracking**: Schedule maintenance and mark resources unavailable

#### Data Model Details

- **Resource**: ID (UUID), name (string), type (enum: room/chair/equipment/tool), location_id (FK), quantity (integer), status (enum: active/inactive/maintenance), purchase_date (date), depreciation_value (decimal), tenant_id (FK)
- **ResourceAvailability**: ID (UUID), resource_id (FK), day_of_week (enum: 0-6), start_time (time), end_time (time), is_recurring (boolean), effective_from (date), effective_to (date, nullable), tenant_id (FK)
- **ResourceAssignment**: ID (UUID), appointment_id (FK), resource_id (FK), quantity_used (integer), tenant_id (FK)
- **ResourceUtilization**: ID (UUID), resource_id (FK), date (date), usage_hours (decimal), utilization_percent (decimal), tenant_id (FK)
- **ResourceMaintenance**: ID (UUID), resource_id (FK), maintenance_type (string), scheduled_date (date), completed_date (date, nullable), notes (text), tenant_id (FK)

#### User Workflows

**For Manager Creating Resource:**
1. Access resource management interface
2. Enter resource details (name, type, quantity)
3. Set availability schedule
4. Assign to location
5. Define resource dependencies
6. Save and enable resource

**For Manager Scheduling Maintenance:**
1. Select resource needing maintenance
2. Enter maintenance type and date
3. Mark resource unavailable during maintenance
4. Notify staff of unavailability
5. Mark maintenance complete when finished
6. Re-enable resource

**For System Assigning Resources:**
1. Receive appointment booking request
2. Check required resources for service
3. Verify resource availability
4. Assign available resources
5. Prevent booking if resources unavailable
6. Suggest alternative times if needed

#### Edge Cases & Constraints

- **Resource Conflicts**: Prevent double-booking of same resource
- **Resource Dependencies**: Validate all required resources available before booking
- **Maintenance Scheduling**: Prevent bookings during maintenance periods
- **Resource Capacity**: Track limited quantity resources; prevent over-allocation
- **Resource Depreciation**: Track asset depreciation for accounting
- **Resource Retirement**: Archive retired resources; prevent future bookings

#### Performance Requirements

- **Resource Availability Check**: Check availability within 100ms
- **Resource Assignment**: Assign resources within 200ms
- **Utilization Calculation**: Calculate utilization within 1 second
- **Maintenance Scheduling**: Schedule maintenance within 500ms

#### Security Considerations

- **Resource Data**: Restrict access to resource information to authorized staff
- **Maintenance Records**: Maintain audit trail of maintenance activities
- **Asset Tracking**: Track resource location and assignment for security

#### Compliance Requirements

- **Asset Management**: Maintain records for asset depreciation and tax purposes
- **Maintenance Records**: Keep maintenance records for warranty and compliance

#### Acceptance Criteria

1. WHEN creating a resource, THE System SHALL capture name, type, location, and availability schedule
2. WHEN booking an appointment, THE System SHALL automatically assign available resources based on service requirements
3. WHEN a resource is unavailable, THE System SHALL prevent appointments requiring that resource
4. WHEN viewing resource utilization, THE System SHALL display usage statistics and peak times
5. WHEN a resource needs maintenance, THE System SHALL mark it unavailable and notify staff
6. WHEN multiple services require the same resource, THE System SHALL prevent double-booking
7. WHEN a resource is deleted, THE System SHALL archive it and prevent future bookings

#### Business Value

- Maximizes resource utilization
- Prevents scheduling conflicts
- Enables capacity planning
- Reduces operational inefficiencies

#### Dependencies

- Appointment booking (Requirement 3)
- Staff scheduling (Requirement 4)

#### Key Data Entities

- Resource (ID, name, type, location, tenant_id)
- ResourceAvailability (ID, resource_id, start_time, end_time, status, tenant_id)
- ResourceAssignment (ID, appointment_id, resource_id, tenant_id)
- ResourceUtilization (ID, resource_id, date, usage_hours, tenant_id)

#### User Roles

- Manager: Manages resources
- Staff: Views resource availability
- Owner: Views utilization reports

---

### Requirement 10: Waiting Room Management & Queue Tracking

**User Story:** As a staff member, I want to manage the waiting room queue, so that I can serve customers in order and reduce wait times.

#### Detailed Description

The waiting room management system tracks customers as they arrive for appointments, managing the queue and providing real-time wait time estimates. When customers check in, they are added to the waiting queue. Staff members can see the queue and call the next customer when ready. The system automatically removes customers from the queue after 15 minutes if they don't check in (no-show handling).

The system displays estimated wait times to waiting customers, improving their experience and reducing perceived wait times. Analytics track queue metrics including average wait time, peak times, and queue length. This data informs staffing decisions and capacity planning.

The system supports multiple service areas or waiting rooms, enabling larger facilities to manage separate queues for different services or locations.

#### Technical Specifications

- **Queue Management**: FIFO queue with real-time updates
- **Check-In**: Customers check in via kiosk, mobile app, or staff entry
- **Wait Time Estimation**: Calculate based on current queue and average service time
- **No-Show Handling**: Automatically remove customers after 15 minutes
- **Multiple Queues**: Support separate queues for different services or locations
- **Real-Time Updates**: Push updates to waiting customers and staff
- **Analytics**: Track queue metrics and trends
- **Notifications**: Notify customers when approaching their turn

#### Business Context

- **Problem Solved**: Improves customer experience through transparency; reduces perceived wait times
- **ROI**: Improves customer satisfaction by 15-20%; enables better staff coordination
- **Competitive Advantage**: Modern waiting room experience differentiates from competitors

#### Integration Points

- **Appointment Booking (Req 3)**: Track appointment status through queue
- **Notifications (Req 7)**: Notify customers when approaching their turn
- **Performance Metrics (Req 21)**: Track queue metrics for analytics

#### Data Model Details

- **QueueEntry**: ID (UUID), appointment_id (FK), customer_id (FK), check_in_time (timestamp), status (enum: waiting/called/in-service/completed/no-show), position (integer), tenant_id (FK)
- **WaitingRoom**: ID (UUID), tenant_id (FK), location_id (FK), name (string), current_queue_count (integer), average_wait_time (integer), last_updated (timestamp)
- **QueueHistory**: ID (UUID), appointment_id (FK), check_in_time (timestamp), called_time (timestamp, nullable), service_start_time (timestamp, nullable), service_end_time (timestamp, nullable), wait_duration (integer), service_duration (integer), tenant_id (FK)

#### User Workflows

**For Customer Checking In:**
1. Arrive at facility
2. Check in via kiosk or mobile app
3. Receive queue position and estimated wait time
4. Wait in waiting area
5. Receive notification when approaching their turn
6. Proceed to service area when called

**For Staff Managing Queue:**
1. View waiting room queue
2. See customer details and appointment info
3. Call next customer when ready
4. Mark customer as in-service
5. Mark customer as completed when finished
6. View queue metrics

**For Manager Analyzing Queue:**
1. View queue metrics by time period
2. Identify peak times and bottlenecks
3. Analyze average wait times
4. Track no-show rates
5. Plan staffing based on queue data

#### Edge Cases & Constraints

- **No-Show Handling**: Automatically remove customers after 15 minutes; track as no-show
- **Queue Position**: Update positions when customers are called or removed
- **Wait Time Estimation**: Handle variable service times; use average for estimation
- **Multiple Queues**: Support separate queues for different services or locations
- **Priority Customers**: Support VIP or priority customers (move to front of queue)
- **Queue Overflow**: Handle situations where queue exceeds capacity

#### Performance Requirements

- **Check-In**: Process check-in within 500ms
- **Queue Update**: Update queue display within 1 second
- **Wait Time Calculation**: Calculate wait time within 100ms
- **Notification**: Send notification within 2 seconds of customer approaching turn

#### Security Considerations

- **Customer Privacy**: Don't display full customer names in public queue display
- **Appointment Data**: Restrict access to appointment details to authorized staff
- **Queue Data**: Maintain audit trail of queue operations

#### Compliance Requirements

- **Accessibility**: Ensure check-in interface is accessible to customers with disabilities
- **Privacy**: Comply with privacy regulations when displaying customer information

#### Acceptance Criteria

1. WHEN a customer arrives for appointment, THE System SHALL check them in and add them to waiting queue
2. WHEN viewing waiting room, THE System SHALL display customer queue in order with estimated wait times
3. WHEN a staff member is ready, THE System SHALL notify the next customer in queue
4. WHEN a customer is served, THE System SHALL remove them from queue and mark appointment as in-progress
5. WHEN a customer is no-show, THE System SHALL remove them from queue after 15 minutes
6. WHEN queue is long, THE System SHALL display estimated wait time to waiting customers
7. WHEN appointment is completed, THE System SHALL update queue status and notify next customer

#### Business Value

- Improves customer experience through transparency
- Reduces perceived wait times
- Enables efficient staff coordination
- Provides data for capacity planning

#### Dependencies

- Appointment booking (Requirement 3)
- Notifications (Requirement 7)

#### Key Data Entities

- QueueEntry (ID, appointment_id, customer_id, check_in_time, status, tenant_id)
- WaitingRoom (ID, tenant_id, current_queue_count, average_wait_time)
- QueueHistory (ID, appointment_id, wait_duration, tenant_id)

#### User Roles

- Staff: Manages queue
- Customer: Views wait time
- Manager: Views queue analytics

---

### Requirement 11: Staff Break Scheduling & Time-Off Requests

**User Story:** As a staff member, I want to schedule breaks and request time off, so that I can maintain work-life balance and the business can plan coverage.

#### Detailed Description

The break and time-off management system enables staff members to schedule breaks during their shifts and request time off for personal reasons. Breaks are blocked from customer bookings, ensuring staff get required rest periods. The system enforces labor law requirements for break duration and frequency.

Time-off requests go through a manager approval workflow. Managers can see the impact on coverage and approve or deny requests accordingly. The system tracks approved time off and updates staff availability automatically. Analytics track time-off patterns, identifying trends and potential staffing issues.

The system supports different types of time off (vacation, sick leave, personal day) with different approval workflows and accrual rules. Integration with payroll systems ensures breaks are handled correctly for compensation purposes.

#### Technical Specifications

- **Break Types**: Lunch break, short break, other
- **Break Duration**: Configurable by business (typically 30-60 minutes for lunch)
- **Break Frequency**: Enforce minimum breaks per shift (e.g., 1 lunch break per 8-hour shift)
- **Time-Off Types**: Vacation, sick leave, personal day, unpaid leave
- **Approval Workflow**: Manager approval required for time-off requests
- **Accrual Tracking**: Track accrued vacation and sick leave
- **Payroll Integration**: Export break and time-off data for payroll
- **Notifications**: Notify staff and managers of approvals/denials

#### Business Context

- **Problem Solved**: Ensures staff get required breaks; enables transparent time-off management
- **ROI**: Improves staff satisfaction and retention; ensures labor law compliance
- **Competitive Advantage**: Transparent time-off policies improve staff satisfaction

#### Integration Points

- **Staff Scheduling (Req 4)**: Update availability based on approved time off
- **Notifications (Req 7)**: Notify staff and managers of approvals/denials
- **Payroll Systems**: Export break and time-off data for payroll

#### Data Model Details

- **Break**: ID (UUID), staff_id (FK), start_time (timestamp), end_time (timestamp), type (enum: lunch/short/other), status (enum: scheduled/completed/cancelled), tenant_id (FK)
- **TimeOffRequest**: ID (UUID), staff_id (FK), start_date (date), end_date (date), type (enum: vacation/sick/personal/unpaid), reason (string), status (enum: pending/approved/denied), requested_at (timestamp), approved_by (FK), approval_date (date, nullable), denial_reason (string, nullable), tenant_id (FK)
- **TimeOffApproval**: ID (UUID), request_id (FK), approved_by (FK), approval_date (timestamp), coverage_plan (text), tenant_id (FK)
- **TimeOffAccrual**: ID (UUID), staff_id (FK), type (enum: vacation/sick), accrued_hours (decimal), used_hours (decimal), balance_hours (decimal), year (integer), tenant_id (FK)

#### User Workflows

**For Staff Scheduling Break:**
1. Log in to staff dashboard
2. View their shift
3. Select time for break
4. Confirm break duration
5. Break is blocked from customer bookings
6. Clock out for break
7. Clock back in after break

**For Staff Requesting Time Off:**
1. Log in to staff dashboard
2. Click "Request Time Off"
3. Select dates and type of time off
4. Enter reason (optional)
5. Submit request
6. Receive notification when approved/denied
7. See updated schedule if approved

**For Manager Approving Time Off:**
1. Receive time-off request notification
2. Review request and check coverage
3. See impact on staffing
4. Approve or deny request
5. Notify staff of decision
6. Update schedule if approved
7. Plan coverage for approved time off

#### Edge Cases & Constraints

- **Break Overlap**: Prevent breaks that overlap with appointments
- **Minimum Rest**: Enforce minimum rest period between shifts (e.g., 11 hours)
- **Break Duration**: Enforce minimum break duration (e.g., 30 minutes for lunch)
- **Accrual Rules**: Handle different accrual rules for vacation and sick leave
- **Carryover**: Handle vacation carryover to next year (if allowed)
- **Expiration**: Handle vacation expiration (if applicable)
- **Unpaid Leave**: Handle unpaid leave without accrual

#### Performance Requirements

- **Break Scheduling**: Schedule break within 500ms
- **Time-Off Request**: Submit request within 500ms
- **Approval Processing**: Process approval within 1 second
- **Accrual Calculation**: Calculate accrual within 1 second

#### Security Considerations

- **Salary Information**: Restrict access to time-off accrual to authorized managers
- **Personal Information**: Restrict access to time-off reasons to authorized managers
- **Audit Trail**: Log all time-off requests and approvals

#### Compliance Requirements

- **Labor Laws**: Enforce minimum break requirements per labor laws
- **Payroll Accuracy**: Maintain accurate records for payroll and tax purposes
- **FMLA**: Support Family and Medical Leave Act requirements (if applicable)

#### Acceptance Criteria

1. WHEN a staff member schedules a break, THE System SHALL block that time from customer bookings
2. WHEN a staff member requests time off, THE System SHALL notify manager for approval
3. WHEN time off is approved, THE System SHALL update availability and notify staff
4. WHEN time off is denied, THE System SHALL notify staff with reason
5. WHEN viewing staff schedule, THE System SHALL display breaks and approved time off
6. WHEN calculating labor costs, THE System SHALL account for unpaid breaks
7. WHEN a break overlaps with appointment, THE System SHALL prevent the break scheduling

#### Business Value

- Improves staff satisfaction and retention
- Ensures adequate coverage planning
- Reduces burnout and improves service quality
- Enables accurate labor cost calculation

#### Dependencies

- Staff scheduling (Requirement 4)
- Notifications (Requirement 7)

#### Key Data Entities

- Break (ID, staff_id, start_time, end_time, type, tenant_id)
- TimeOffRequest (ID, staff_id, start_date, end_date, reason, status, tenant_id)
- TimeOffApproval (ID, request_id, approved_by, approval_date, tenant_id)

#### User Roles

- Staff: Requests breaks and time off
- Manager: Approves time off requests
- Owner: Views time off analytics

---

### Requirement 12: Capacity Planning & Overbooking Prevention

**User Story:** As a manager, I want to prevent overbooking and plan capacity, so that I can maintain service quality and staff satisfaction.

#### Detailed Description

The capacity planning system prevents overbooking by enforcing capacity limits on staff members and resources. Managers define maximum concurrent appointments per staff member or resource, and the system prevents bookings that would exceed these limits. When capacity is reached, the system suggests alternative time slots to customers.

The system provides analytics on capacity utilization, identifying peak times and opportunities for optimization. Managers can set alerts when capacity reaches 80%, enabling proactive planning. The system supports complex capacity scenarios where services require multiple staff members or resources.

Capacity planning data informs hiring decisions, enabling businesses to expand capacity based on demand. The system tracks historical capacity utilization, enabling forecasting of future capacity needs.

#### Technical Specifications

- **Capacity Limits**: Define maximum concurrent appointments per staff member or resource
- **Capacity Validation**: Check capacity before allowing booking
- **Alternative Slots**: Suggest alternative times when capacity is reached
- **Capacity Alerts**: Alert managers when capacity reaches threshold (e.g., 80%)
- **Multi-Staff Services**: Handle services requiring multiple staff members
- **Capacity Analytics**: Track utilization and identify optimization opportunities
- **Forecasting**: Project future capacity needs based on trends
- **Bulk Capacity**: Support bulk capacity updates

#### Business Context

- **Problem Solved**: Prevents service quality degradation from overbooking; prevents staff burnout
- **ROI**: Maintains service quality; improves staff satisfaction and retention
- **Competitive Advantage**: Consistent service quality builds customer loyalty

#### Integration Points

- **Appointment Booking (Req 3)**: Enforce capacity limits during booking
- **Staff Scheduling (Req 4)**: Consider capacity when scheduling staff
- **Resource Management (Req 8)**: Enforce resource capacity limits
- **Performance Metrics (Req 21)**: Track capacity utilization metrics

#### Data Model Details

- **CapacityLimit**: ID (UUID), staff_id (FK, nullable), resource_id (FK, nullable), max_concurrent (integer), effective_from (date), effective_to (date, nullable), tenant_id (FK)
- **CapacityUtilization**: ID (UUID), date (date), hour (integer), staff_id (FK, nullable), resource_id (FK, nullable), current_appointments (integer), max_capacity (integer), utilization_percent (decimal), tenant_id (FK)
- **CapacityAlert**: ID (UUID), type (enum: threshold_reached/capacity_exceeded), threshold_percent (integer), triggered_at (timestamp), acknowledged_at (timestamp, nullable), tenant_id (FK)
- **CapacityForecast**: ID (UUID), period (date), forecasted_demand (integer), recommended_capacity (integer), tenant_id (FK)

#### User Workflows

**For Manager Setting Capacity Limits:**
1. Access capacity settings
2. Select staff member or resource
3. Set maximum concurrent appointments
4. Set effective date range
5. Save capacity limit
6. System enforces limit on future bookings

**For System Enforcing Capacity:**
1. Receive appointment booking request
2. Check capacity limits for staff/resources
3. Calculate current utilization
4. If capacity available, allow booking
5. If capacity exceeded, suggest alternatives
6. Notify customer of alternatives

**For Manager Analyzing Capacity:**
1. View capacity utilization by staff/resource
2. Identify peak times and bottlenecks
3. See capacity alerts
4. Review capacity forecast
5. Plan hiring or resource expansion
6. Adjust capacity limits as needed

#### Edge Cases & Constraints

- **Multi-Staff Services**: Handle services requiring multiple staff members; check all staff availability
- **Resource Capacity**: Handle limited quantity resources; prevent over-allocation
- **Concurrent Appointments**: Accurately calculate concurrent appointments considering service duration
- **Capacity Changes**: Handle capacity limit changes; don't affect existing bookings
- **Overbooking Prevention**: Prevent race conditions where multiple bookings exceed capacity simultaneously
- **Alternative Slots**: Suggest realistic alternatives within reasonable time window

#### Performance Requirements

- **Capacity Check**: Check capacity within 100ms
- **Utilization Calculation**: Calculate utilization within 500ms
- **Forecast Generation**: Generate forecast within 5 seconds
- **Alert Triggering**: Trigger alert within 1 second of threshold reached

#### Security Considerations

- **Capacity Data**: Restrict access to capacity settings to authorized managers
- **Audit Trail**: Log all capacity limit changes

#### Compliance Requirements

- **Labor Laws**: Ensure capacity limits comply with labor laws (e.g., maximum hours per week)

#### Acceptance Criteria

1. WHEN setting capacity limits, THE System SHALL define maximum concurrent appointments per staff member or resource
2. WHEN a customer attempts to book, THE System SHALL check capacity and prevent booking if limit is reached
3. WHEN capacity is exceeded, THE System SHALL suggest alternative time slots
4. WHEN viewing capacity analytics, THE System SHALL display utilization rates and peak times
5. WHEN a service requires multiple staff members, THE System SHALL check all staff availability
6. WHEN a resource has limited quantity, THE System SHALL track usage and prevent over-allocation
7. WHEN capacity is at 80%, THE System SHALL alert manager to consider additional resources

#### Business Value

- Maintains service quality through capacity management
- Prevents staff burnout from overbooking
- Improves customer satisfaction
- Enables data-driven expansion decisions

#### Dependencies

- Appointment booking (Requirement 3)
- Staff scheduling (Requirement 4)
- Resource management (Requirement 8)

#### Key Data Entities

- CapacityLimit (ID, staff_id, resource_id, max_concurrent, tenant_id)
- CapacityUtilization (ID, date, hour, utilization_percent, tenant_id)
- CapacityAlert (ID, type, threshold, triggered_at, tenant_id)

#### User Roles

- Manager: Sets capacity limits
- Owner: Views capacity analytics
- System: Enforces capacity rules

---

### Requirement 13: Service Dependencies Management

**User Story:** As a manager, I want to define service dependencies, so that I can ensure services are booked in the correct sequence and with proper prerequisites.

#### Detailed Description

The service dependencies system enables managers to define prerequisite services that must be completed before customers can book certain services. For example, a spa might require a consultation before a treatment, or a gym might require a fitness assessment before personal training. The system enforces these dependencies during booking, preventing customers from booking services without completing prerequisites.

When customers attempt to book a service with unmet prerequisites, the system suggests booking the prerequisite service first. The system tracks prerequisite completion, enabling customers to see their progress toward booking desired services. Analytics track dependency patterns, identifying opportunities for upselling through prerequisite services.

The system supports complex dependency chains where services have multiple prerequisites or where prerequisites have their own prerequisites. Managers can update dependencies, with the system intelligently handling existing bookings.

#### Technical Specifications

- **Dependency Types**: Required (must complete before), recommended (suggested but not required)
- **Dependency Chains**: Support multiple levels of dependencies
- **Completion Tracking**: Track which prerequisites have been completed
- **Booking Validation**: Prevent booking without required prerequisites
- **Suggestion Engine**: Suggest prerequisite services during booking
- **Dependency Updates**: Handle dependency changes; don't affect existing bookings
- **Analytics**: Track dependency completion rates and upselling impact
- **Bulk Operations**: Import/export dependency definitions

#### Business Context

- **Problem Solved**: Ensures proper service sequence; prevents customer dissatisfaction from incomplete prerequisites
- **ROI**: Improves service quality by 15-20%; enables upselling through prerequisite services
- **Competitive Advantage**: Structured service workflows improve customer experience and outcomes

#### Integration Points

- **Appointment Booking (Req 3)**: Validate prerequisites during booking
- **Customer Profiles (Req 5)**: Track prerequisite completion in customer history
- **Performance Metrics (Req 21)**: Track dependency completion rates

#### Data Model Details

- **Service**: ID (UUID), name (string), description (text), duration_minutes (integer), price (decimal), category (string), tenant_id (FK)
- **ServiceDependency**: ID (UUID), service_id (FK), prerequisite_service_id (FK), dependency_type (enum: required/recommended), required_completion_days (integer, nullable), tenant_id (FK)
- **CustomerServiceHistory**: ID (UUID), customer_id (FK), service_id (FK), completed_at (timestamp), staff_id (FK), notes (text), tenant_id (FK)
- **DependencyCompletion**: ID (UUID), customer_id (FK), service_id (FK), prerequisite_service_id (FK), completed_at (timestamp, nullable), tenant_id (FK)

#### User Workflows

**For Manager Defining Dependencies:**
1. Access service management
2. Select service to define dependencies for
3. Add prerequisite services
4. Set dependency type (required/recommended)
5. Set completion window (if applicable)
6. Save dependencies
7. System enforces on future bookings

**For Customer Booking Service with Dependencies:**
1. Browse available services
2. Select service with prerequisites
3. System checks prerequisite completion
4. If prerequisites not met, system suggests booking them first
5. Customer can book prerequisite or skip (if recommended)
6. After prerequisites completed, customer can book desired service

**For Manager Analyzing Dependencies:**
1. View dependency completion rates
2. Identify services with low prerequisite completion
3. See upselling impact of prerequisites
4. Adjust dependencies based on data
5. Track customer progression through service chains

#### Edge Cases & Constraints

- **Circular Dependencies**: Prevent circular dependency chains (A requires B, B requires A)
- **Dependency Chains**: Handle multiple levels of dependencies
- **Completion Windows**: Handle time-based prerequisites (e.g., consultation valid for 30 days)
- **Dependency Removal**: Handle removal of dependencies; don't affect existing bookings
- **Bulk Booking**: Handle bulk bookings where multiple services are booked together
- **Prerequisite Expiration**: Handle expiration of prerequisite completion (e.g., consultation valid for 30 days)

#### Performance Requirements

- **Dependency Check**: Check prerequisites within 100ms
- **Dependency Validation**: Validate dependency chain within 200ms
- **Completion Tracking**: Update completion status within 500ms
- **Analytics Calculation**: Calculate completion rates within 2 seconds

#### Security Considerations

- **Dependency Data**: Restrict access to dependency definitions to authorized managers
- **Audit Trail**: Log all dependency changes

#### Compliance Requirements

- **Service Quality**: Ensure dependencies support service quality and safety requirements

#### Acceptance Criteria

1. WHEN creating a service, THE System SHALL allow defining prerequisite services that must be completed first
2. WHEN a customer attempts to book a service, THE System SHALL check if prerequisites are met
3. WHEN prerequisites are not met, THE System SHALL prevent booking and suggest prerequisite services
4. WHEN a prerequisite service is completed, THE System SHALL update dependency status
5. WHEN viewing service details, THE System SHALL display all dependencies and completion status
6. WHEN a service has multiple dependencies, THE System SHALL enforce all prerequisites
7. WHEN a dependency is removed, THE System SHALL update all affected bookings

#### Business Value

- Ensures proper service sequence (e.g., consultation before treatment)
- Improves service quality through structured workflows
- Prevents customer dissatisfaction from incomplete prerequisites
- Enables upselling through dependency management

#### Dependencies

- Appointment booking (Requirement 3)
- Service management

#### Key Data Entities

- Service (ID, name, duration, price, tenant_id)
- ServiceDependency (ID, service_id, prerequisite_service_id, required, tenant_id)
- CustomerServiceHistory (ID, customer_id, service_id, completed_at, tenant_id)

#### User Roles

- Manager: Defines service dependencies
- Staff: Views dependencies during booking
- Customer: Sees suggested prerequisites

---

## PHASE 2 - Operations & Financial

### Requirement 14: Appointment Reminders (Reduce No-Shows)

**User Story:** As a business owner, I want automated appointment reminders, so that I can reduce no-show rates and improve revenue.

#### Detailed Description

The appointment reminder system sends automated notifications to customers at configurable intervals before their appointments, significantly reducing no-show rates. Reminders are sent via email and SMS based on customer preferences. The system tracks reminder delivery and customer responses, enabling businesses to measure reminder effectiveness.

Customers can confirm receipt of reminders through email links or SMS replies, providing businesses with confirmation that customers received the reminder. The system tracks confirmation rates, identifying customers who may not have received reminders. Analytics measure the impact of reminders on no-show rates, enabling businesses to optimize reminder timing and messaging.

The system supports customizable reminder templates, allowing businesses to personalize messages with customer names, appointment details, and business information. Reminders can include links to reschedule or cancel appointments, enabling customers to manage their bookings directly from the reminder.

#### Technical Specifications

- **Reminder Timing**: Configurable intervals (24 hours, 1 hour before appointment)
- **Channels**: Email, SMS, push notifications
- **Customizable Templates**: Support variable substitution (customer name, appointment time, etc.)
- **Delivery Tracking**: Track delivery status and customer responses
- **Confirmation Tracking**: Track customer confirmations via email/SMS
- **Retry Logic**: Retry failed reminders up to 3 times
- **Opt-Out Support**: Respect customer preferences for reminder channels
- **Analytics**: Track reminder effectiveness and impact on no-shows

#### Business Context

- **Problem Solved**: Reduces no-show rates by 25-35% through timely reminders
- **ROI**: Prevents revenue loss from no-shows; reduces administrative follow-up
- **Competitive Advantage**: Proactive communication improves customer experience

#### Integration Points

- **Appointment Booking (Req 3)**: Send reminders based on appointment schedule
- **Notifications (Req 7)**: Use notification system for delivery
- **Customer Profiles (Req 5)**: Use customer preferences for reminder channels
- **Performance Metrics (Req 21)**: Track reminder effectiveness

#### Data Model Details

- **ReminderSchedule**: ID (UUID), appointment_id (FK), reminder_time (timestamp), reminder_type (enum: 24h/1h/custom), status (enum: pending/sent/delivered/failed), sent_at (timestamp, nullable), tenant_id (FK)
- **ReminderLog**: ID (UUID), appointment_id (FK), reminder_type (enum), status (enum: sent/delivered/failed), delivery_status (enum: success/bounce/complaint), sent_at (timestamp), delivered_at (timestamp, nullable), tenant_id (FK)
- **ReminderConfirmation**: ID (UUID), reminder_log_id (FK), confirmed_at (timestamp), confirmation_method (enum: email_link/sms_reply), tenant_id (FK)
- **NoShowAnalytics**: ID (UUID), date (date), no_show_count (integer), reminder_sent_count (integer), reminder_confirmed_count (integer), no_show_rate_percent (decimal), tenant_id (FK)

#### User Workflows

**For System Sending Reminders:**
1. Identify appointments scheduled for next 24 hours
2. Check customer reminder preferences
3. Generate reminder message from template
4. Send via preferred channel (email/SMS)
5. Track delivery status
6. Retry if delivery fails
7. Log reminder in analytics

**For Customer Receiving Reminder:**
1. Receive reminder email or SMS
2. View appointment details
3. Optionally confirm receipt (via email link or SMS reply)
4. Optionally reschedule or cancel from reminder
5. Attend appointment or notify business of cancellation

**For Manager Analyzing Reminders:**
1. View reminder delivery rates
2. Track confirmation rates
3. Measure impact on no-show rates
4. Identify customers not receiving reminders
5. Adjust reminder timing based on data
6. Optimize reminder templates

#### Edge Cases & Constraints

- **Delivery Failures**: Retry failed reminders up to 3 times with exponential backoff
- **Bounced Emails**: Track bounced emails; disable reminders for invalid addresses
- **Opt-Out**: Respect customer opt-out preferences; maintain compliance with anti-spam laws
- **Timezone Issues**: Send reminders in customer's local timezone
- **Appointment Cancellation**: Don't send reminders for cancelled appointments
- **Duplicate Reminders**: Prevent sending duplicate reminders if appointment is rescheduled

#### Performance Requirements

- **Reminder Sending**: Send reminder within 1 second of scheduled time
- **Delivery Tracking**: Update delivery status within 5 seconds
- **Analytics Calculation**: Calculate no-show rates within 5 seconds

#### Security Considerations

- **Customer Data**: Never include sensitive information in reminders
- **Unsubscribe Links**: Include unsubscribe link in all email reminders
- **Audit Trail**: Log all reminders sent with recipient and timestamp

#### Compliance Requirements

- **GDPR**: Obtain consent before sending marketing reminders
- **CAN-SPAM**: Include business address and unsubscribe link in all emails
- **TCPA**: Obtain consent before sending SMS reminders

#### Acceptance Criteria

1. WHEN an appointment is scheduled, THE System SHALL automatically send reminders at configurable intervals (24h, 1h before)
2. WHEN a reminder is sent, THE System SHALL log the send time and delivery status
3. WHEN a customer confirms receipt, THE System SHALL update appointment status to confirmed
4. WHEN a customer cancels via reminder, THE System SHALL release the time slot immediately
5. WHEN a reminder fails to send, THE System SHALL retry and log the failure
6. WHEN viewing no-show analytics, THE System SHALL display reduction in no-shows after reminder implementation
7. WHEN a customer opts out of reminders, THE System SHALL respect their preference

#### Business Value

- Reduces no-show rates by 25-35%
- Increases revenue through improved attendance
- Reduces staff idle time
- Improves customer communication

#### Dependencies

- Appointment booking (Requirement 3)
- Notifications (Requirement 7)

#### Key Data Entities

- ReminderSchedule (ID, appointment_id, reminder_time, status, sent_at, tenant_id)
- ReminderLog (ID, appointment_id, reminder_type, status, delivery_status, tenant_id)
- NoShowAnalytics (ID, date, no_show_count, reminder_sent_count, tenant_id)

#### User Roles

- Owner: Configures reminder settings
- System: Sends reminders automatically
- Customer: Receives reminders

---

### Requirement 15: Customer Feedback & Reviews System

**User Story:** As a manager, I want to collect customer feedback, so that I can improve service quality and identify issues early.

#### Detailed Description

The customer feedback system collects ratings and comments from customers after appointments, providing valuable insights into service quality. Customers receive feedback requests via email or SMS, with a simple rating scale (1-5 stars) and optional comments. The system aggregates feedback by staff member and service type, enabling managers to identify top performers and areas for improvement.

Negative feedback triggers alerts to managers, enabling quick response and issue resolution. Staff members receive notifications of their ratings, providing motivation and identifying areas for development. The system supports staff responses to feedback, enabling two-way communication with customers.

Analytics track feedback trends over time, identifying patterns and opportunities for improvement. The system supports exporting feedback data for quality assurance and training purposes.

#### Technical Specifications

- **Rating Scale**: 1-5 stars with optional comments
- **Feedback Channels**: Email, SMS, in-app
- **Aggregation**: By staff member, service type, time period
- **Alerts**: Automatic alerts for negative feedback
- **Staff Responses**: Allow staff to respond to feedback
- **Analytics**: Track trends and patterns
- **Export**: Support exporting feedback data
- **Sentiment Analysis**: Analyze sentiment of comments

#### Business Context

- **Problem Solved**: Identifies service quality issues early; enables continuous improvement
- **ROI**: Improves service quality by 15-20%; increases customer satisfaction
- **Competitive Advantage**: Responsive to customer feedback builds loyalty

#### Integration Points

- **Appointment Booking (Req 3)**: Send feedback requests after appointments
- **Customer Profiles (Req 5)**: Store feedback in customer history
- **Notifications (Req 7)**: Send feedback requests and alerts
- **Performance Metrics (Req 21)**: Track feedback metrics

#### Data Model Details

- **Feedback**: ID (UUID), appointment_id (FK), customer_id (FK), staff_id (FK), service_id (FK), rating (integer 1-5), comments (text), created_at (timestamp), tenant_id (FK)
- **StaffRating**: ID (UUID), staff_id (FK), average_rating (decimal), review_count (integer), last_review_date (date), tenant_id (FK)
- **FeedbackResponse**: ID (UUID), feedback_id (FK), response_text (text), responded_by (FK), responded_at (timestamp), tenant_id (FK)
- **FeedbackAnalytics**: ID (UUID), date (date), average_rating (decimal), feedback_count (integer), negative_feedback_count (integer), tenant_id (FK)

#### User Workflows

**For Customer Providing Feedback:**
1. Receive feedback request email/SMS after appointment
2. Click link to feedback form
3. Rate appointment (1-5 stars)
4. Optionally add comments
5. Submit feedback
6. Receive thank you message

**For Staff Viewing Feedback:**
1. Log in to staff dashboard
2. View their average rating
3. See recent feedback and comments
4. Respond to feedback if desired
5. View feedback trends over time

**For Manager Analyzing Feedback:**
1. View feedback analytics dashboard
2. See average ratings by staff and service
3. Identify negative feedback
4. Review feedback trends
5. Plan training or coaching
6. Export feedback for quality assurance

#### Edge Cases & Constraints

- **Negative Feedback**: Automatically alert manager for ratings ≤2 stars
- **Feedback Timing**: Send feedback request 1-2 hours after appointment
- **Duplicate Feedback**: Prevent multiple feedback submissions for same appointment
- **Anonymous Feedback**: Support anonymous feedback option
- **Feedback Deletion**: Handle customer requests to delete feedback

#### Performance Requirements

- **Feedback Submission**: Submit feedback within 500ms
- **Analytics Calculation**: Calculate ratings within 2 seconds
- **Alert Triggering**: Trigger alert within 1 second of negative feedback

#### Security Considerations

- **Feedback Privacy**: Protect customer privacy in feedback
- **Staff Privacy**: Don't share customer names with other staff
- **Audit Trail**: Log all feedback access

#### Compliance Requirements

- **GDPR**: Support feedback data export and deletion

#### Acceptance Criteria

1. WHEN an appointment is completed, THE System SHALL send feedback request to customer
2. WHEN a customer submits feedback, THE System SHALL capture rating (1-5 stars) and comments
3. WHEN feedback is submitted, THE System SHALL notify staff member of their rating
4. WHEN viewing feedback analytics, THE System SHALL display average ratings by staff and service
5. WHEN feedback is negative, THE System SHALL alert manager for follow-up
6. WHEN a customer leaves a review, THE System SHALL allow staff to respond
7. WHEN exporting data, THE System SHALL include feedback trends and patterns

#### Business Value

- Improves service quality through feedback
- Identifies underperforming staff early
- Builds customer loyalty through engagement
- Provides social proof for marketing

#### Dependencies

- Appointment booking (Requirement 3)
- Customer profiles (Requirement 5)
- Notifications (Requirement 7)

#### Key Data Entities

- Feedback (ID, appointment_id, customer_id, rating, comments, created_at, tenant_id)
- StaffRating (ID, staff_id, average_rating, review_count, tenant_id)
- FeedbackResponse (ID, feedback_id, response_text, responded_by, responded_at, tenant_id)

#### User Roles

- Customer: Submits feedback
- Staff: Views their ratings
- Manager: Views feedback analytics

---

### Requirement 16: Detailed Expense Tracking

**User Story:** As a business owner, I want to track all expenses, so that I can understand profitability and make informed financial decisions.

#### Detailed Description

The expense tracking system records all business expenses, categorizing them for financial analysis. Expenses are tracked by category (supplies, rent, utilities, payroll, marketing, etc.), enabling businesses to understand cost structure and identify optimization opportunities. The system supports recurring expenses (rent, subscriptions) and one-time expenses.

Expense data integrates with financial dashboards, providing real-time visibility into spending. The system calculates profit margins by comparing revenue to expenses, enabling businesses to understand profitability by service, staff member, or time period. Expense data is exported for accounting and tax purposes.

The system supports budget management, enabling businesses to set spending limits by category and receive alerts when spending exceeds budget. Analytics track expense trends, identifying opportunities for cost reduction.

#### Technical Specifications

- **Expense Categories**: Supplies, rent, utilities, payroll, marketing, equipment, insurance, other
- **Recurring Expenses**: Support monthly, quarterly, annual recurring expenses
- **Budget Management**: Set spending limits by category; track against budget
- **Profit Calculation**: Calculate profit margins by service, staff, time period
- **Export**: Support exporting expense data for accounting
- **Attachments**: Support attaching receipts and invoices
- **Approval Workflow**: Optional approval workflow for large expenses
- **Analytics**: Track expense trends and patterns

#### Business Context

- **Problem Solved**: Provides visibility into spending; enables profitability analysis
- **ROI**: Identifies cost reduction opportunities; improves financial decision-making
- **Competitive Advantage**: Data-driven financial management improves profitability

#### Integration Points

- **Billing & Payment (Req 6)**: Track revenue alongside expenses
- **Accounting Software (Req 48)**: Sync expense data to accounting software
- **Performance Metrics (Req 21)**: Track profitability metrics

#### Data Model Details

- **Expense**: ID (UUID), category_id (FK), amount (decimal), date (date), description (text), receipt_url (string, nullable), approved_by (FK, nullable), status (enum: pending/approved/rejected), tenant_id (FK)
- **ExpenseCategory**: ID (UUID), name (string), budget_limit (decimal, nullable), tenant_id (FK)
- **ExpenseReport**: ID (UUID), start_date (date), end_date (date), total_by_category (JSON), total_expenses (decimal), tenant_id (FK)
- **BudgetAlert**: ID (UUID), category_id (FK), alert_threshold_percent (integer), triggered_at (timestamp, nullable), tenant_id (FK)

#### User Workflows

**For Manager Recording Expense:**
1. Access expense tracking
2. Select expense category
3. Enter amount and date
4. Add description and receipt
5. Submit for approval (if required)
6. Expense recorded in system

**For Owner Analyzing Expenses:**
1. View expense dashboard
2. See total expenses by category
3. Compare to budget
4. View expense trends
5. Identify cost reduction opportunities
6. Export expense data for accounting

**For Accountant Exporting Data:**
1. Access expense reports
2. Select date range
3. Export expense data
4. Import into accounting software
5. Reconcile with bank statements

#### Edge Cases & Constraints

- **Recurring Expenses**: Automatically create recurring expense entries
- **Budget Alerts**: Alert when spending exceeds budget threshold
- **Expense Approval**: Require approval for expenses above threshold
- **Receipt Tracking**: Support attaching receipts for audit trail
- **Expense Correction**: Allow correcting expense entries with audit trail

#### Performance Requirements

- **Expense Recording**: Record expense within 500ms
- **Report Generation**: Generate expense report within 5 seconds
- **Analytics Calculation**: Calculate profitability within 5 seconds

#### Security Considerations

- **Financial Data**: Restrict access to expense data to authorized managers
- **Audit Trail**: Log all expense changes with user and timestamp
- **Receipt Storage**: Securely store receipt images

#### Compliance Requirements

- **Tax Compliance**: Maintain accurate expense records for tax purposes
- **Audit Trail**: Maintain audit trail for all expenses

#### Acceptance Criteria

1. WHEN recording an expense, THE System SHALL capture category, amount, date, and description
2. WHEN categorizing expenses, THE System SHALL support predefined categories (supplies, rent, utilities, payroll, etc.)
3. WHEN viewing expense reports, THE System SHALL display total expenses by category and time period
4. WHEN comparing revenue to expenses, THE System SHALL calculate profit margins
5. WHEN exporting data, THE System SHALL provide detailed expense breakdowns for accounting
6. WHEN an expense is recorded, THE System SHALL update financial dashboards in real-time
7. WHEN expenses exceed budget, THE System SHALL alert manager

#### Business Value

- Improves financial visibility
- Enables profitability analysis
- Supports tax preparation
- Enables budget management

#### Dependencies

- Billing & payment processing (Requirement 6)

#### Key Data Entities

- Expense (ID, category, amount, date, description, tenant_id)
- ExpenseCategory (ID, name, budget_limit, tenant_id)
- ExpenseReport (ID, start_date, end_date, total_by_category, tenant_id)

#### User Roles

- Manager: Records expenses
- Owner: Views expense reports
- Accountant: Exports expense data

---

### Requirement 17: Tax Reporting & Compliance

**User Story:** As a business owner, I want automated tax reporting, so that I can ensure compliance and reduce accounting overhead.

#### Detailed Description

The tax reporting system automates calculation of taxable income, sales tax, and other tax obligations. The system calculates taxable income by subtracting expenses from revenue, providing accurate figures for tax filing. Sales tax is calculated and categorized by jurisdiction, enabling businesses to file sales tax returns accurately.

The system generates tax reports in required formats (1099, W2, etc.) for different business structures. Tax rates are updated automatically as regulations change, ensuring calculations remain accurate. The system sends reminders as tax filing deadlines approach, helping businesses stay compliant.

Tax data integrates with accounting software, enabling seamless export for professional tax preparation. The system supports multiple tax jurisdictions, enabling multi-location businesses to manage tax obligations across different states and countries.

#### Technical Specifications

- **Tax Calculation**: Automatic calculation of taxable income, sales tax, payroll taxes
- **Tax Rates**: Support multiple tax rates by jurisdiction; auto-update
- **Report Generation**: Generate reports in required formats (1099, W2, etc.)
- **Sales Tax**: Calculate and categorize by jurisdiction
- **Payroll Taxes**: Calculate withholdings and employer taxes
- **Deadline Tracking**: Track tax filing deadlines; send reminders
- **Multi-Jurisdiction**: Support multiple tax jurisdictions
- **Export**: Export tax data for professional preparation

#### Business Context

- **Problem Solved**: Ensures tax compliance; reduces accounting costs
- **ROI**: Prevents penalties and fines; reduces accounting overhead
- **Competitive Advantage**: Automated tax compliance reduces business risk

#### Integration Points

- **Billing & Payment (Req 6)**: Track revenue for tax calculation
- **Expense Tracking (Req 15)**: Track expenses for tax deduction
- **Accounting Software (Req 48)**: Export tax data to accounting software

#### Data Model Details

- **TaxReport**: ID (UUID), period (date), taxable_income (decimal), tax_liability (decimal), tax_rate (decimal), tenant_id (FK)
- **SalesTax**: ID (UUID), transaction_id (FK), amount (decimal), jurisdiction (string), tax_rate (decimal), tax_amount (decimal), tenant_id (FK)
- **TaxSetting**: ID (UUID), tenant_id (FK), business_structure (enum: sole_proprietor/llc/s_corp/c_corp), tax_id (string), tax_rate (decimal), filing_frequency (enum: monthly/quarterly/annual)
- **TaxDeadline**: ID (UUID), tax_type (enum: income/sales/payroll), due_date (date), reminder_sent (boolean), tenant_id (FK)

#### User Workflows

**For Owner Generating Tax Report:**
1. Access tax reporting section
2. Select tax period
3. Review calculated taxable income
4. Review sales tax by jurisdiction
5. Generate tax report
6. Export for tax preparation

**For Accountant Preparing Taxes:**
1. Access tax reports
2. Review calculations
3. Export data to tax software
4. File tax returns
5. Track filing status

**For System Managing Tax Deadlines:**
1. Track tax filing deadlines
2. Send reminders 30 days before deadline
3. Send reminders 7 days before deadline
4. Track filing status

#### Edge Cases & Constraints

- **Tax Rate Changes**: Handle tax rate changes; apply to future transactions
- **Multi-Jurisdiction**: Handle different tax rates by location
- **Exemptions**: Support tax exemptions (e.g., non-profit status)
- **Deductions**: Support various deduction types
- **Estimated Taxes**: Calculate estimated tax payments

#### Performance Requirements

- **Tax Calculation**: Calculate taxes within 5 seconds
- **Report Generation**: Generate report within 10 seconds
- **Export**: Export tax data within 5 seconds

#### Security Considerations

- **Tax Data**: Restrict access to tax data to authorized users
- **Audit Trail**: Log all tax calculations and changes
- **Data Encryption**: Encrypt sensitive tax information

#### Compliance Requirements

- **Tax Compliance**: Ensure calculations comply with tax regulations
- **Audit Trail**: Maintain audit trail for tax compliance

#### Acceptance Criteria

1. WHEN generating tax reports, THE System SHALL calculate taxable income based on revenue and expenses
2. WHEN a tax period ends, THE System SHALL generate reports in required format (1099, W2, etc.)
3. WHEN tracking sales tax, THE System SHALL calculate and categorize by jurisdiction
4. WHEN exporting for accountant, THE System SHALL provide complete financial data in standard format
5. WHEN tax rates change, THE System SHALL update calculations automatically
6. WHEN viewing tax summary, THE System SHALL display estimated tax liability
7. WHEN filing deadline approaches, THE System SHALL send reminder to owner

#### Business Value

- Ensures tax compliance
- Reduces accounting costs
- Prevents penalties and fines
- Simplifies year-end reporting

#### Dependencies

- Billing & payment processing (Requirement 6)
- Expense tracking (Requirement 15)

#### Key Data Entities

- TaxReport (ID, period, taxable_income, tax_liability, tenant_id)
- SalesTax (ID, transaction_id, amount, jurisdiction, tax_rate, tenant_id)
- TaxSetting (ID, tenant_id, tax_id, tax_rate, filing_frequency)

#### User Roles

- Owner: Views tax reports
- Accountant: Exports tax data
- System: Calculates taxes

---

### Requirement 18: Refund & Cancellation Policies

**User Story:** As a business owner, I want to define and enforce refund policies, so that I can manage customer expectations and protect revenue.

#### Detailed Description

The refund and cancellation policy system enables businesses to define clear policies for appointment cancellations and refunds. Policies specify cancellation windows (e.g., 24 hours notice) and corresponding refund percentages (e.g., 100% refund if cancelled 24+ hours before, 50% if cancelled 1-24 hours before, 0% if cancelled less than 1 hour before).

When customers cancel appointments, the system automatically calculates the refund amount based on the policy and cancellation time. Refunds are processed through the payment gateway, with customers receiving confirmation. The system tracks refund rates and reasons, enabling businesses to optimize policies.

Policies can vary by service type or staff member, enabling businesses to implement different policies for different services. The system enforces policies consistently, preventing disputes and ensuring fairness.

#### Technical Specifications

- **Policy Definition**: Define cancellation windows and refund percentages
- **Automatic Calculation**: Automatically calculate refund based on policy
- **Multiple Policies**: Support different policies by service or staff
- **Refund Processing**: Process refunds through payment gateway
- **Dispute Handling**: Track and manage refund disputes
- **Analytics**: Track refund rates and reasons
- **Policy Updates**: Update policies; apply to future cancellations only
- **Customer Communication**: Clearly communicate policies to customers

#### Business Context

- **Problem Solved**: Protects revenue through clear policies; reduces customer disputes
- **ROI**: Reduces refund disputes by 80%; improves customer satisfaction
- **Competitive Advantage**: Clear, fair policies build customer trust

#### Integration Points

- **Billing & Payment (Req 6)**: Process refunds through payment gateway
- **Appointment Booking (Req 3)**: Apply policies during cancellation
- **Notifications (Req 7)**: Communicate policies to customers

#### Data Model Details

- **RefundPolicy**: ID (UUID), tenant_id (FK), service_id (FK, nullable), staff_id (FK, nullable), cancellation_window_hours (integer), refund_percentage (integer), effective_date (date), end_date (date, nullable)
- **RefundRequest**: ID (UUID), appointment_id (FK), customer_id (FK), amount (decimal), reason (string), status (enum: pending/approved/rejected/processed), requested_at (timestamp), processed_at (timestamp, nullable), tenant_id (FK)
- **RefundAnalytics**: ID (UUID), date (date), refund_count (integer), total_refunded (decimal), refund_rate_percent (decimal), tenant_id (FK)

#### User Workflows

**For Owner Defining Policy:**
1. Access refund policy settings
2. Define cancellation windows and refund percentages
3. Set effective date
4. Apply to specific services or all services
5. Save policy
6. Communicate policy to customers

**For Customer Cancelling Appointment:**
1. Log into customer portal
2. Select appointment to cancel
3. View refund policy and calculated refund
4. Confirm cancellation
5. Receive refund confirmation
6. Refund processed to original payment method

**For Manager Handling Disputes:**
1. Receive refund dispute from customer
2. Review refund policy and cancellation time
3. Approve or reject dispute
4. Process refund if approved
5. Communicate decision to customer

#### Edge Cases & Constraints

- **Policy Changes**: Apply new policies to future cancellations only; don't affect existing bookings
- **Partial Refunds**: Handle partial refunds based on policy
- **No-Shows**: Handle no-shows differently from cancellations (typically no refund)
- **Service Completion**: Don't allow refunds for completed services (except disputes)
- **Dispute Resolution**: Support dispute resolution process for contested refunds

#### Performance Requirements

- **Refund Calculation**: Calculate refund within 100ms
- **Refund Processing**: Process refund within 5 seconds
- **Policy Application**: Apply policy within 500ms

#### Security Considerations

- **Policy Data**: Restrict access to policy settings to authorized managers
- **Refund Data**: Maintain audit trail of all refunds
- **Payment Data**: Never store full credit card numbers

#### Compliance Requirements

- **Consumer Protection**: Comply with consumer protection laws regarding refunds
- **Payment Processing**: Comply with payment processor requirements

#### Acceptance Criteria

1. WHEN creating a refund policy, THE System SHALL define cancellation windows and refund percentages
2. WHEN a customer cancels, THE System SHALL calculate refund amount based on policy and cancellation time
3. WHEN a refund is requested, THE System SHALL process it through payment gateway
4. WHEN a refund is processed, THE System SHALL update customer balance and send confirmation
5. WHEN viewing refund analytics, THE System SHALL display refund rates and reasons
6. WHEN a policy is updated, THE System SHALL apply to future cancellations only
7. WHEN a customer disputes a refund, THE System SHALL flag for manager review

#### Business Value

- Protects revenue through clear policies
- Reduces customer disputes
- Improves customer satisfaction
- Enables data-driven policy optimization

#### Dependencies

- Billing & payment processing (Requirement 6)
- Appointment booking (Requirement 3)

#### Key Data Entities

- RefundPolicy (ID, tenant_id, cancellation_window_hours, refund_percentage, effective_date)
- RefundRequest (ID, appointment_id, customer_id, amount, reason, status, tenant_id)
- RefundAnalytics (ID, date, refund_count, total_refunded, tenant_id)

#### User Roles

- Owner: Defines refund policies
- Manager: Processes refunds
- Customer: Requests refunds

---

### Requirement 19: Deposit Management

**User Story:** As a business owner, I want to manage customer deposits, so that I can secure revenue and improve cash flow.

#### Detailed Description

The deposit management system enables businesses to collect customer deposits for services or packages. Deposits create credit balances that customers can use for future appointments. When appointments are completed, service costs are deducted from the deposit balance. The system tracks deposit balances, notifying customers when balances are low.

Deposits improve cash flow by collecting payment upfront, reducing payment processing costs and bad debt. The system supports deposit expiration policies, enabling businesses to encourage customers to use deposits within a specified timeframe. Customers can request refunds of remaining deposit balances, with refunds processed through the payment gateway.

Analytics track deposit utilization, identifying customers with unused deposits and opportunities for follow-up marketing. The system distinguishes between deposits and completed services in financial reporting, enabling accurate revenue recognition.

#### Technical Specifications

- **Deposit Creation**: Accept deposits from customers; create credit balance
- **Deposit Tracking**: Track deposit balance and usage
- **Automatic Deduction**: Automatically deduct service costs from deposit
- **Expiration**: Support deposit expiration policies
- **Refund Processing**: Process refunds of remaining balance
- **Low Balance Alerts**: Notify customers when balance is low
- **Analytics**: Track deposit utilization and revenue impact
- **Financial Reporting**: Distinguish deposits from revenue

#### Business Context

- **Problem Solved**: Improves cash flow through advance payments; reduces payment processing costs
- **ROI**: Improves cash flow by 15-20%; reduces payment processing costs by 30%
- **Competitive Advantage**: Deposit-based pricing enables package offerings

#### Integration Points

- **Billing & Payment (Req 6)**: Process deposits and deductions
- **Customer Profiles (Req 5)**: Track customer deposits
- **Notifications (Req 7)**: Notify customers of low balance

#### Data Model Details

- **Deposit**: ID (UUID), customer_id (FK), amount (decimal), balance (decimal), created_at (timestamp), expires_at (date, nullable), status (enum: active/expired/refunded), tenant_id (FK)
- **DepositTransaction**: ID (UUID), deposit_id (FK), type (enum: deposit/deduction/refund), amount (decimal), appointment_id (FK, nullable), created_at (timestamp), tenant_id (FK)
- **DepositPolicy**: ID (UUID), tenant_id (FK), expiration_days (integer, nullable), refund_policy (enum: full/partial/none), minimum_deposit (decimal)

#### User Workflows

**For Customer Making Deposit:**
1. Log into customer portal
2. Select "Add Deposit"
3. Enter deposit amount
4. Complete payment
5. Receive confirmation
6. Deposit balance updated

**For System Deducting from Deposit:**
1. Appointment completed
2. Calculate service cost
3. Deduct from deposit balance
4. Update customer balance
5. Send receipt

**For Customer Requesting Refund:**
1. Log into customer portal
2. View deposit balance
3. Request refund
4. Refund processed to original payment method
5. Receive confirmation

#### Edge Cases & Constraints

- **Partial Deduction**: Handle services costing less than deposit balance
- **Insufficient Balance**: Handle appointments when deposit balance is insufficient
- **Expiration**: Automatically expire deposits after specified period
- **Refund Policies**: Enforce refund policies (full, partial, or no refund)
- **Multiple Deposits**: Support multiple active deposits per customer

#### Performance Requirements

- **Deposit Creation**: Create deposit within 500ms
- **Balance Update**: Update balance within 100ms
- **Refund Processing**: Process refund within 5 seconds

#### Security Considerations

- **Deposit Data**: Restrict access to deposit information to authorized users
- **Payment Data**: Never store full credit card numbers
- **Audit Trail**: Log all deposit transactions

#### Compliance Requirements

- **Financial Reporting**: Properly account for deposits in financial statements
- **Consumer Protection**: Comply with consumer protection laws regarding deposits

#### Acceptance Criteria

1. WHEN a customer makes a deposit, THE System SHALL record it and create a credit balance
2. WHEN an appointment is completed, THE System SHALL deduct service cost from deposit
3. WHEN deposit balance is low, THE System SHALL notify customer to add funds
4. WHEN a customer requests refund, THE System SHALL process remaining deposit balance
5. WHEN viewing deposit analytics, THE System SHALL display total deposits held and utilization
6. WHEN a deposit expires, THE System SHALL notify customer per policy
7. WHEN calculating revenue, THE System SHALL distinguish between deposits and completed services

#### Business Value

- Improves cash flow through advance payments
- Reduces payment processing costs
- Increases customer commitment
- Simplifies billing for package services

#### Dependencies

- Billing & payment processing (Requirement 6)
- Customer profiles (Requirement 5)

#### Key Data Entities

- Deposit (ID, customer_id, amount, balance, created_at, expires_at, tenant_id)
- DepositTransaction (ID, deposit_id, type, amount, appointment_id, tenant_id)
- DepositPolicy (ID, tenant_id, expiration_days, refund_policy)

#### User Roles

- Customer: Makes deposits
- Manager: Manages deposits
- Owner: Views deposit analytics

---

### Requirement 20: Financial Reconciliation

**User Story:** As an accountant, I want to reconcile financial records, so that I can ensure accuracy and identify discrepancies.

#### Detailed Description

The financial reconciliation system matches invoices to payment records, identifying discrepancies and ensuring financial accuracy. The system compares system records to bank statements, identifying timing differences and potential errors. Reconciliation reports display matched and unmatched transactions, enabling accountants to investigate discrepancies.

The system supports manual reconciliation where accountants can mark transactions as reconciled, and automated reconciliation using bank feeds. When discrepancies are found, the system flags them for review and correction. The system maintains detailed audit trails of all reconciliation activities for compliance.

Reconciliation data integrates with accounting software, enabling seamless export for professional accounting. The system supports multi-currency reconciliation for businesses operating in multiple countries.

#### Technical Specifications

- **Transaction Matching**: Match invoices to payments automatically
- **Discrepancy Detection**: Identify unmatched and mismatched transactions
- **Bank Feed Integration**: Import bank statements for automated reconciliation
- **Manual Reconciliation**: Support manual marking of reconciled transactions
- **Audit Trail**: Maintain detailed audit trail of reconciliation activities
- **Multi-Currency**: Support reconciliation in multiple currencies
- **Export**: Export reconciliation data for accounting software
- **Reporting**: Generate reconciliation reports

#### Business Context

- **Problem Solved**: Ensures financial accuracy; identifies fraud or errors early
- **ROI**: Reduces accounting errors by 95%; improves financial controls
- **Competitive Advantage**: Accurate financial records support business decisions

#### Integration Points

- **Billing & Payment (Req 6)**: Track payments for reconciliation
- **Expense Tracking (Req 15)**: Track expenses for reconciliation
- **Accounting Software (Req 48)**: Export reconciliation data

#### Data Model Details

- **ReconciliationRecord**: ID (UUID), invoice_id (FK), payment_id (FK), status (enum: matched/unmatched/discrepancy), discrepancy_amount (decimal, nullable), reconciled_at (timestamp, nullable), reconciled_by (FK, nullable), tenant_id (FK)
- **ReconciliationReport**: ID (UUID), period (date), matched_count (integer), unmatched_count (integer), total_discrepancy (decimal), reconciled_at (timestamp), reconciled_by (FK), tenant_id (FK)
- **AuditTrail**: ID (UUID), transaction_id (FK), change_type (enum: created/modified/reconciled), changed_by (FK), changed_at (timestamp), old_value (JSON), new_value (JSON), tenant_id (FK)

#### User Workflows

**For Accountant Reconciling Transactions:**
1. Access reconciliation interface
2. Select date range
3. View matched and unmatched transactions
4. Investigate discrepancies
5. Mark transactions as reconciled
6. Generate reconciliation report

**For System Matching Transactions:**
1. Receive payment notification
2. Match to corresponding invoice
3. If match found, mark as reconciled
4. If no match, flag as unmatched
5. Alert accountant of discrepancies

**For Manager Correcting Discrepancies:**
1. Receive discrepancy alert
2. Investigate cause
3. Correct transaction if needed
4. Update reconciliation status
5. Document correction in audit trail

#### Edge Cases & Constraints

- **Timing Differences**: Handle timing differences between invoice and payment
- **Partial Payments**: Handle partial payments and multiple payments per invoice
- **Refunds**: Handle refunds and credit memos
- **Currency Conversion**: Handle currency conversion differences
- **Duplicate Transactions**: Detect and handle duplicate transactions

#### Performance Requirements

- **Transaction Matching**: Match transactions within 1 second
- **Discrepancy Detection**: Detect discrepancies within 2 seconds
- **Report Generation**: Generate report within 10 seconds

#### Security Considerations

- **Financial Data**: Restrict access to reconciliation data to authorized accountants
- **Audit Trail**: Maintain detailed audit trail of all reconciliation activities
- **Data Integrity**: Ensure data integrity of financial records

#### Compliance Requirements

- **Audit Trail**: Maintain audit trail for compliance
- **Financial Accuracy**: Ensure accuracy of financial records

#### Acceptance Criteria

1. WHEN reconciling payments, THE System SHALL match invoices to payment records
2. WHEN a discrepancy is found, THE System SHALL flag it for review
3. WHEN viewing reconciliation report, THE System SHALL display matched and unmatched transactions
4. WHEN exporting reconciliation data, THE System SHALL provide detailed transaction logs
5. WHEN a transaction is corrected, THE System SHALL update all related records
6. WHEN reconciliation is complete, THE System SHALL generate audit trail
7. WHEN comparing to bank statements, THE System SHALL identify timing differences

#### Business Value

- Ensures financial accuracy
- Identifies fraud or errors early
- Supports audit requirements
- Improves financial controls

#### Dependencies

- Billing & payment processing (Requirement 6)
- Expense tracking (Requirement 15)

#### Key Data Entities

- ReconciliationRecord (ID, invoice_id, payment_id, status, discrepancy_amount, tenant_id)
- ReconciliationReport (ID, period, matched_count, unmatched_count, total_discrepancy, tenant_id)
- AuditTrail (ID, transaction_id, change_type, changed_by, changed_at, tenant_id)

#### User Roles

- Accountant: Performs reconciliation
- Owner: Reviews reconciliation reports
- Manager: Corrects discrepancies

---

### Requirement 21: Invoice Generation

**User Story:** As a business owner, I want to generate professional invoices, so that I can maintain records and improve customer communication.

#### Detailed Description

The invoice generation system automatically creates professional invoices upon appointment completion. Invoices include service details, pricing, taxes, discounts, and payment terms. Businesses can customize invoice templates with their logo, colors, and payment instructions. Invoices are automatically emailed to customers and stored in the system for record-keeping.

The system supports invoice customization, enabling businesses to add notes, payment terms, or special instructions. Invoices can be generated manually for past appointments or bulk-generated for a date range. The system tracks invoice status (draft, sent, paid, overdue, cancelled), enabling businesses to follow up on unpaid invoices.

Customers can view and download invoices from their customer portal. The system supports invoice disputes, enabling customers to flag issues and managers to add notes and adjustments. Analytics track invoice metrics including average invoice value, payment time, and dispute rates.

#### Technical Specifications

- **Automatic Generation**: Generate invoice upon appointment completion
- **Customizable Templates**: Support custom logo, colors, payment terms
- **Email Delivery**: Automatically email invoices to customers
- **PDF Export**: Export invoices as PDF
- **Manual Generation**: Generate invoices manually for past appointments
- **Bulk Generation**: Generate invoices for date range
- **Invoice Tracking**: Track invoice status and payment
- **Dispute Handling**: Support invoice disputes and adjustments

#### Business Context

- **Problem Solved**: Maintains professional records; improves customer communication
- **ROI**: Reduces invoicing time by 90%; improves payment collection
- **Competitive Advantage**: Professional invoices improve business image

#### Integration Points

- **Billing & Payment (Req 6)**: Create invoices for appointments
- **Appointment Booking (Req 3)**: Generate invoices upon completion
- **Notifications (Req 7)**: Email invoices to customers
- **Customer Profiles (Req 5)**: Store invoices in customer history

#### Data Model Details

- **Invoice**: ID (UUID), appointment_id (FK), customer_id (FK), amount (decimal), tax (decimal), discount (decimal), total (decimal), status (enum: draft/sent/paid/overdue/cancelled), created_at (timestamp), due_date (date), paid_at (timestamp, nullable), tenant_id (FK)
- **InvoiceLineItem**: ID (UUID), invoice_id (FK), service_id (FK), quantity (integer), unit_price (decimal), total (decimal), tenant_id (FK)
- **InvoiceTemplate**: ID (UUID), tenant_id (FK), logo_url (string), primary_color (hex), secondary_color (hex), payment_terms (text), footer_text (text)
- **InvoiceDispute**: ID (UUID), invoice_id (FK), customer_id (FK), reason (text), status (enum: pending/resolved), created_at (timestamp), resolved_at (timestamp, nullable), tenant_id (FK)

#### User Workflows

**For System Generating Invoice:**
1. Appointment completed
2. Calculate service cost, taxes, discounts
3. Generate invoice from template
4. Email to customer
5. Store in system
6. Track payment status

**For Customer Viewing Invoice:**
1. Log into customer portal
2. View invoices section
3. Select invoice to view
4. Download as PDF
5. View payment status
6. Make payment if unpaid

**For Manager Customizing Invoice:**
1. Access invoice template settings
2. Upload logo
3. Set colors and fonts
4. Add payment terms and instructions
5. Add footer text
6. Preview invoice
7. Save template

#### Edge Cases & Constraints

- **Partial Invoices**: Handle partial invoices for partial payments
- **Credit Memos**: Support credit memos for refunds
- **Invoice Corrections**: Allow correcting invoices with audit trail
- **Duplicate Prevention**: Prevent generating duplicate invoices
- **Invoice Numbering**: Support custom invoice numbering schemes

#### Performance Requirements

- **Invoice Generation**: Generate invoice within 1 second
- **Email Delivery**: Email invoice within 1 minute
- **PDF Export**: Export as PDF within 2 seconds
- **Bulk Generation**: Generate 1000 invoices within 30 seconds

#### Security Considerations

- **Invoice Data**: Restrict access to invoices to authorized users
- **Payment Data**: Never store full credit card numbers
- **Audit Trail**: Log all invoice changes

#### Compliance Requirements

- **Financial Records**: Maintain invoices for financial and tax purposes
- **Data Privacy**: Comply with privacy regulations when storing customer information

#### Acceptance Criteria

1. WHEN an appointment is completed, THE System SHALL automatically generate invoice
2. WHEN generating invoice, THE System SHALL include service details, pricing, taxes, and discounts
3. WHEN customizing invoice, THE System SHALL allow adding business logo and payment terms
4. WHEN sending invoice, THE System SHALL email to customer and store in system
5. WHEN viewing invoice history, THE System SHALL display all invoices with payment status
6. WHEN exporting invoices, THE System SHALL provide PDF format
7. WHEN a customer disputes invoice, THE System SHALL allow adding notes and adjustments

#### Business Value

- Improves customer communication
- Maintains professional records
- Simplifies accounting
- Enables invoice tracking

#### Dependencies

- Billing & payment processing (Requirement 6)
- Appointment booking (Requirement 3)

#### Key Data Entities

- Invoice (ID, appointment_id, customer_id, amount, tax, discount, status, created_at, tenant_id)
- InvoiceLineItem (ID, invoice_id, service_id, quantity, unit_price, total, tenant_id)
- InvoiceTemplate (ID, tenant_id, logo_url, payment_terms, footer_text)

#### User Roles

- System: Generates invoices
- Manager: Customizes invoices
- Customer: Views invoices

---

### Requirement 22: Performance Metrics & KPIs

**User Story:** As a business owner, I want to track key performance indicators, so that I can measure business health and make strategic decisions.

#### Detailed Description

The performance metrics system provides comprehensive dashboards displaying key business indicators including revenue, appointments, no-shows, customer satisfaction, and staff productivity. Metrics are calculated automatically and updated in real-time, enabling businesses to monitor performance continuously. Managers can set targets for each KPI and track progress toward goals.

The system supports comparing metrics across different time periods (day, week, month, year), identifying trends and anomalies. Alerts notify managers when KPIs fall below thresholds, enabling proactive management. The system provides insights and recommendations based on metric trends, helping businesses optimize operations.

Analytics support drill-down analysis, enabling managers to understand which services, staff members, or locations are driving performance. The system exports detailed reports for strategic planning and board presentations.

#### Technical Specifications

- **Real-Time Calculation**: Calculate metrics in real-time as data changes
- **Multiple Time Periods**: Support day, week, month, year comparisons
- **Target Tracking**: Set and track progress toward KPI targets
- **Alerts**: Alert when KPIs fall below thresholds
- **Drill-Down Analysis**: Analyze metrics by service, staff, location
- **Trend Analysis**: Identify trends and anomalies
- **Forecasting**: Project future metrics based on trends
- **Export**: Export detailed reports

#### Business Context

- **Problem Solved**: Enables data-driven decision making; identifies trends and opportunities
- **ROI**: Improves business performance by 20-30% through data-driven decisions
- **Competitive Advantage**: Data-driven management improves competitiveness

#### Integration Points

- **Appointment Booking (Req 3)**: Track appointment metrics
- **Billing & Payment (Req 6)**: Track revenue metrics
- **Customer Feedback (Req 14)**: Track satisfaction metrics
- **Staff Scheduling (Req 4)**: Track staff productivity

#### Data Model Details

- **KPI**: ID (UUID), name (string), calculation_method (string), target_value (decimal), current_value (decimal), threshold_value (decimal), tenant_id (FK)
- **KPIHistory**: ID (UUID), kpi_id (FK), date (date), value (decimal), tenant_id (FK)
- **Dashboard**: ID (UUID), tenant_id (FK), selected_kpis (JSON array), refresh_frequency (integer), tenant_id (FK)

#### User Workflows

**For Owner Viewing Dashboard:**
1. Log into dashboard
2. View key metrics (revenue, appointments, satisfaction)
3. See trends and comparisons
4. Identify areas needing attention
5. Drill down into specific metrics
6. Export reports for analysis

**For Manager Setting Targets:**
1. Access KPI settings
2. Select KPI to set target for
3. Enter target value
4. Set alert threshold
5. Save target
6. Track progress toward target

**For System Calculating Metrics:**
1. Collect data from various sources
2. Calculate metrics using defined formulas
3. Compare to targets and thresholds
4. Generate alerts if needed
5. Update dashboards
6. Store historical data

#### Edge Cases & Constraints

- **Data Delays**: Handle delays in data collection; use cached data for real-time display
- **Metric Definitions**: Support custom metric definitions
- **Seasonal Variations**: Account for seasonal variations in metrics
- **Data Quality**: Handle missing or incomplete data gracefully

#### Performance Requirements

- **Metric Calculation**: Calculate metrics within 5 seconds
- **Dashboard Load**: Load dashboard within 2 seconds
- **Alert Triggering**: Trigger alert within 1 second of threshold breach

#### Security Considerations

- **Metric Data**: Restrict access to metrics to authorized managers
- **Audit Trail**: Log all metric changes and alerts

#### Compliance Requirements

- **Data Accuracy**: Ensure accuracy of metric calculations

#### Acceptance Criteria

1. WHEN viewing dashboard, THE System SHALL display key metrics (revenue, appointments, no-shows, customer satisfaction)
2. WHEN tracking KPIs, THE System SHALL calculate metrics by day, week, month, and year
3. WHEN comparing periods, THE System SHALL show growth trends and anomalies
4. WHEN setting targets, THE System SHALL track progress toward goals
5. WHEN exporting reports, THE System SHALL provide detailed KPI breakdowns
6. WHEN a KPI falls below threshold, THE System SHALL alert owner
7. WHEN analyzing performance, THE System SHALL provide insights and recommendations

#### Business Value

- Enables data-driven decision making
- Identifies trends and opportunities
- Measures business growth
- Supports strategic planning

#### Dependencies

- Appointment booking (Requirement 3)
- Billing & payment processing (Requirement 6)
- Customer feedback (Requirement 14)

#### Key Data Entities

- KPI (ID, name, calculation_method, target_value, current_value, tenant_id)
- KPIHistory (ID, kpi_id, date, value, tenant_id)
- Dashboard (ID, tenant_id, selected_kpis, refresh_frequency)

#### User Roles

- Owner: Views KPIs
- Manager: Tracks KPIs
- System: Calculates KPIs

---

### Requirement 23: Training & Certification Tracking

**User Story:** As a manager, I want to track staff training and certifications, so that I can ensure compliance and maintain service quality.

#### Detailed Description

The training and certification tracking system maintains records of all staff certifications, licenses, and training. Managers can define required certifications for each service, and the system prevents staff from offering services without required certifications. The system sends alerts when certifications are expiring, enabling proactive renewal.

The system tracks training completion, enabling managers to identify staff needing additional training. Training records support compliance requirements, enabling businesses to demonstrate staff qualifications to regulators. The system supports assigning services to staff only after required training is completed.

Analytics track certification compliance rates, identifying gaps and training needs. The system supports bulk certification uploads and integrations with training providers for automated completion tracking.

#### Technical Specifications

- **Certification Tracking**: Track certifications with issue and expiration dates
- **Expiration Alerts**: Alert when certifications expiring
- **Service Requirements**: Define required certifications for each service
- **Compliance Verification**: Verify staff has required certifications before service assignment
- **Training Records**: Track training completion and dates
- **Bulk Upload**: Support bulk certification uploads
- **Compliance Reports**: Generate compliance reports
- **Integration**: Support integration with training providers

#### Business Context

- **Problem Solved**: Ensures regulatory compliance; maintains service quality standards
- **ROI**: Prevents compliance violations; reduces liability
- **Competitive Advantage**: Certified staff improves customer confidence

#### Integration Points

- **Staff Profiles (Req 4)**: Store certifications in staff profiles
- **Appointment Booking (Req 3)**: Verify certifications before booking
- **Notifications (Req 7)**: Alert staff of expiring certifications

#### Data Model Details

- **Certification**: ID (UUID), staff_id (FK), name (string), issue_date (date), expiration_date (date), issuing_body (string), credential_id (string), tenant_id (FK)
- **Training**: ID (UUID), staff_id (FK), name (string), completion_date (date), trainer (string), certificate_url (string), tenant_id (FK)
- **ServiceRequirement**: ID (UUID), service_id (FK), required_certification (string), tenant_id (FK)

#### User Workflows

**For Manager Tracking Certifications:**
1. Access staff certification section
2. View all staff certifications
3. See expiration dates
4. Receive alerts for expiring certifications
5. Track training completion
6. Generate compliance reports

**For Staff Updating Certifications:**
1. Log into staff portal
2. Upload new certification
3. Enter certification details
4. Submit for approval
5. Receive confirmation

**For System Verifying Certifications:**
1. Receive appointment booking request
2. Check service requirements
3. Verify staff has required certifications
4. Allow or prevent booking based on certifications

#### Edge Cases & Constraints

- **Expiration Handling**: Handle expired certifications; prevent service assignment
- **Renewal Tracking**: Track certification renewals
- **Multiple Certifications**: Support multiple certifications per staff member
- **Certification Chains**: Handle certifications with prerequisites

#### Performance Requirements

- **Certification Verification**: Verify certifications within 100ms
- **Compliance Report**: Generate report within 10 seconds

#### Security Considerations

- **Certification Data**: Restrict access to certification data to authorized managers
- **Audit Trail**: Log all certification changes

#### Compliance Requirements

- **Regulatory Compliance**: Ensure certifications meet regulatory requirements
- **Audit Trail**: Maintain audit trail for compliance

#### Acceptance Criteria

1. WHEN hiring staff, THE System SHALL track required certifications and training
2. WHEN a certification expires, THE System SHALL alert manager for renewal
3. WHEN staff completes training, THE System SHALL update their profile and unlock new services
4. WHEN viewing staff profile, THE System SHALL display all certifications with expiration dates
5. WHEN assigning services, THE System SHALL verify staff has required certifications
6. WHEN generating compliance report, THE System SHALL show certification status for all staff
7. WHEN a certification is missing, THE System SHALL prevent staff from offering that service

#### Business Value

- Ensures regulatory compliance
- Maintains service quality standards
- Reduces liability
- Improves staff development

#### Dependencies

- Staff profiles (Requirement 4)
- User authentication (Requirement 2)

#### Key Data Entities

- Certification (ID, staff_id, name, issue_date, expiration_date, issuing_body, tenant_id)
- Training (ID, staff_id, name, completion_date, trainer, tenant_id)
- ServiceRequirement (ID, service_id, required_certification, tenant_id)

#### User Roles

- Manager: Tracks certifications
- Staff: Updates their certifications
- Owner: Views compliance reports

---

### Requirement 24: Attendance & Punctuality Monitoring

**User Story:** As a manager, I want to monitor staff attendance, so that I can ensure reliability and address issues early.

#### Detailed Description

The attendance monitoring system tracks staff clock-in and clock-out times, comparing actual arrival times to scheduled shifts. The system automatically logs tardiness and absences, alerting managers to attendance issues. Attendance data integrates with payroll systems, ensuring accurate compensation based on actual hours worked.

The system generates attendance reports showing attendance rates, tardiness patterns, and absence trends. Managers can identify chronic attendance issues and take corrective action. The system supports excused absences and tardiness, enabling managers to distinguish between legitimate reasons and problematic patterns.

Attendance data is used for performance reviews and disciplinary actions, with audit trails documenting all attendance records and actions taken.

#### Technical Specifications

- **Clock In/Out**: Record arrival and departure times
- **Tardiness Tracking**: Automatically detect and log tardiness
- **Absence Tracking**: Track absences and no-shows
- **Excused Absences**: Support marking absences as excused
- **Attendance Reports**: Generate attendance reports by staff and period
- **Payroll Integration**: Export attendance data for payroll
- **Alerts**: Alert managers to attendance issues
- **Audit Trail**: Maintain audit trail of attendance records

#### Business Context

- **Problem Solved**: Improves staff reliability; enables accurate payroll
- **ROI**: Reduces scheduling disruptions; improves payroll accuracy
- **Competitive Advantage**: Reliable staff improves customer satisfaction

#### Integration Points

- **Staff Scheduling (Req 4)**: Compare actual to scheduled times
- **Notifications (Req 7)**: Alert managers to attendance issues
- **Payroll Systems**: Export attendance data for payroll

#### Data Model Details

- **Attendance**: ID (UUID), staff_id (FK), date (date), clock_in_time (timestamp), clock_out_time (timestamp), status (enum: present/late/absent/excused), notes (text), tenant_id (FK)
- **AttendanceReport**: ID (UUID), staff_id (FK), period (date), attendance_rate (decimal), tardiness_count (integer), absence_count (integer), tenant_id (FK)
- **AttendanceAlert**: ID (UUID), staff_id (FK), type (enum: tardiness/absence/pattern), triggered_at (timestamp), acknowledged_at (timestamp, nullable), tenant_id (FK)

#### User Workflows

**For Staff Clocking In:**
1. Arrive at facility
2. Clock in via kiosk or mobile app
3. System records arrival time
4. Compare to scheduled shift
5. Flag if late

**For Manager Reviewing Attendance:**
1. Access attendance dashboard
2. View attendance by staff member
3. See tardiness and absence patterns
4. Review attendance alerts
5. Take corrective action if needed

**For Payroll Processing:**
1. Access attendance records
2. Export attendance data
3. Calculate hours worked
4. Process payroll

#### Edge Cases & Constraints

- **Shift Overlap**: Handle overlapping shifts or split shifts
- **Excused Absences**: Support marking absences as excused
- **Tardiness Threshold**: Define threshold for marking as tardy (e.g., 5 minutes)
- **Chronic Issues**: Identify patterns of chronic tardiness or absences

#### Performance Requirements

- **Clock In/Out**: Process within 500ms
- **Attendance Report**: Generate within 5 seconds
- **Alert Triggering**: Trigger alert within 1 second

#### Security Considerations

- **Attendance Data**: Restrict access to authorized managers
- **Audit Trail**: Log all attendance changes

#### Compliance Requirements

- **Labor Laws**: Comply with labor laws regarding work hours
- **Payroll Accuracy**: Ensure accurate payroll based on attendance

#### Acceptance Criteria

1. WHEN staff clocks in, THE System SHALL record arrival time and compare to scheduled shift
2. WHEN staff is late, THE System SHALL log tardiness and notify manager
3. WHEN staff is absent, THE System SHALL alert manager and trigger coverage procedures
4. WHEN viewing attendance report, THE System SHALL display attendance rate and patterns
5. WHEN a staff member has excessive absences, THE System SHALL flag for manager review
6. WHEN calculating payroll, THE System SHALL account for attendance records
7. WHEN staff clocks out, THE System SHALL record departure time and calculate hours worked

#### Business Value

- Improves staff reliability
- Reduces scheduling disruptions
- Enables accurate payroll
- Identifies attendance issues early

#### Dependencies

- Staff scheduling (Requirement 4)
- Notifications (Requirement 7)

#### Key Data Entities

- Attendance (ID, staff_id, date, clock_in_time, clock_out_time, status, tenant_id)
- AttendanceReport (ID, staff_id, period, attendance_rate, tardiness_count, absence_count, tenant_id)
- AttendanceAlert (ID, staff_id, type, triggered_at, tenant_id)

#### User Roles

- Staff: Clocks in/out
- Manager: Views attendance
- Owner: Views attendance analytics

---

### Requirement 25: Shift Swapping & Coverage Management

**User Story:** As a staff member, I want to swap shifts with colleagues, so that I can manage my schedule flexibly.

#### Detailed Description

The shift swapping system enables staff members to request shift swaps with colleagues, improving schedule flexibility. When a swap is requested, the system notifies potential swap partners and verifies both staff members are qualified for each other's shifts. Managers can approve or deny swaps, ensuring coverage is maintained. The system automatically updates schedules and notifies affected customers when shifts are swapped.

#### Technical Specifications

- **Swap Requests**: Staff request swaps with specific colleagues or open requests
- **Qualification Verification**: Verify both staff qualified for each other's shifts
- **Manager Approval**: Optional manager approval workflow
- **Automatic Updates**: Update schedules and notify customers
- **Swap History**: Track all swaps for audit purposes
- **Conflict Detection**: Prevent swaps that create conflicts

#### Business Context

- **Problem Solved**: Improves staff satisfaction; reduces scheduling conflicts
- **ROI**: Reduces manager scheduling overhead; improves staff retention
- **Competitive Advantage**: Flexible scheduling improves staff satisfaction

#### Integration Points

- **Staff Scheduling (Req 4)**: Update schedules based on swaps
- **Notifications (Req 7)**: Notify staff and customers
- **Appointment Booking (Req 3)**: Update customer appointments

#### Data Model Details

- **ShiftSwapRequest**: ID (UUID), requester_id (FK), proposed_swap_with_id (FK), shift_id (FK), status (enum: pending/approved/rejected), created_at (timestamp), tenant_id (FK)
- **ShiftSwapApproval**: ID (UUID), swap_request_id (FK), approved_by (FK), approval_date (timestamp), tenant_id (FK)

#### User Workflows

**For Staff Requesting Swap:**
1. View their schedule
2. Select shift to swap
3. Request swap with specific colleague or open request
4. Colleague receives notification
5. Colleague accepts or declines
6. Manager approves if required
7. Schedules updated

**For Manager Approving Swaps:**
1. Receive swap request notification
2. Verify coverage maintained
3. Approve or deny swap
4. Notify staff of decision

#### Edge Cases & Constraints

- **Qualification Mismatch**: Prevent swaps if staff not qualified for each other's shifts
- **Coverage Issues**: Prevent swaps that create coverage gaps
- **Appointment Conflicts**: Handle customer appointments affected by swaps

#### Performance Requirements

- **Swap Request**: Submit within 500ms
- **Approval Processing**: Process within 1 second
- **Schedule Update**: Update within 2 seconds

#### Security Considerations

- **Swap Data**: Restrict access to authorized staff and managers
- **Audit Trail**: Log all swaps

#### Compliance Requirements

- **Labor Laws**: Ensure swaps comply with labor laws

#### Acceptance Criteria

1. WHEN requesting a shift swap, THE System SHALL notify potential swap partners
2. WHEN a swap is proposed, THE System SHALL verify both staff members are qualified for each other's shifts
3. WHEN a swap is accepted, THE System SHALL update schedules and notify manager
4. WHEN a swap is rejected, THE System SHALL notify requester
5. WHEN viewing swap requests, THE System SHALL display pending and completed swaps
6. WHEN a swap affects appointments, THE System SHALL notify affected customers
7. WHEN a swap is completed, THE System SHALL update payroll and scheduling records

#### Business Value

- Improves staff satisfaction
- Reduces scheduling conflicts
- Maintains coverage without manager intervention
- Increases schedule flexibility

#### Dependencies

- Staff scheduling (Requirement 4)
- Notifications (Requirement 7)

#### Key Data Entities

- ShiftSwapRequest (ID, requester_id, proposed_swap_with_id, shift_id, status, created_at, tenant_id)
- ShiftSwapApproval (ID, swap_request_id, approved_by, approval_date, tenant_id)

#### User Roles

- Staff: Requests and accepts swaps
- Manager: Approves swaps
- System: Validates swap eligibility

---

### Requirement 26: Staff Reviews & Feedback

**User Story:** As a manager, I want to conduct staff reviews, so that I can support development and identify high performers.

#### Detailed Description

The staff review system enables managers to conduct performance reviews, capturing ratings, feedback, and development goals. Reviews are scheduled periodically (annually, semi-annually) and tracked in staff profiles. The system notifies staff of upcoming reviews and provides review templates to ensure consistency. High performers are identified for recognition or promotion, while underperformers receive development plans.

#### Technical Specifications

- **Review Templates**: Standardized review forms
- **Performance Ratings**: Rate staff on various competencies
- **Goal Setting**: Set development goals and track progress
- **Review History**: Track all reviews over time
- **Improvement Plans**: Create and track improvement plans
- **High Performer Identification**: Identify top performers
- **Notifications**: Notify staff of reviews and results

#### Business Context

- **Problem Solved**: Improves staff performance; supports career development
- **ROI**: Improves staff retention by 20-30%; identifies high performers
- **Competitive Advantage**: Structured development improves staff quality

#### Integration Points

- **Staff Profiles (Req 4)**: Store reviews in staff profiles
- **Performance Metrics (Req 21)**: Track performance metrics
- **Notifications (Req 7)**: Notify staff of reviews

#### Data Model Details

- **StaffReview**: ID (UUID), staff_id (FK), reviewer_id (FK), rating (decimal), feedback (text), goals (JSON), review_date (date), tenant_id (FK)
- **ReviewHistory**: ID (UUID), staff_id (FK), review_count (integer), average_rating (decimal), last_review_date (date), tenant_id (FK)
- **ImprovementPlan**: ID (UUID), staff_id (FK), review_id (FK), goals (text), target_date (date), status (enum: active/completed/failed), tenant_id (FK)

#### User Workflows

**For Manager Conducting Review:**
1. Select staff member to review
2. Complete review form
3. Rate performance on competencies
4. Provide feedback
5. Set development goals
6. Submit review
7. Notify staff

**For Staff Receiving Review:**
1. Receive review notification
2. View review results
3. Discuss with manager
4. Acknowledge review
5. Work on development goals

**For Owner Analyzing Reviews:**
1. View review analytics
2. Identify high performers
3. Identify underperformers
4. Plan promotions or training

#### Edge Cases & Constraints

- **Review Timing**: Enforce review schedules
- **Confidentiality**: Protect review confidentiality
- **Improvement Plans**: Track progress on improvement plans

#### Performance Requirements

- **Review Submission**: Submit within 500ms
- **Analytics Calculation**: Calculate within 5 seconds

#### Security Considerations

- **Review Confidentiality**: Restrict access to authorized managers
- **Audit Trail**: Log all reviews

#### Compliance Requirements

- **HR Documentation**: Maintain reviews for HR purposes

#### Acceptance Criteria

1. WHEN conducting a review, THE System SHALL capture performance ratings, feedback, and goals
2. WHEN a review is completed, THE System SHALL notify staff and schedule follow-up
3. WHEN viewing staff profile, THE System SHALL display review history and performance trends
4. WHEN comparing staff, THE System SHALL show performance metrics and ratings
5. WHEN identifying high performers, THE System SHALL highlight for recognition or promotion
6. WHEN addressing performance issues, THE System SHALL track improvement plans
7. WHEN exporting reviews, THE System SHALL provide confidential reports for HR

#### Business Value

- Improves staff performance
- Supports career development
- Identifies high performers
- Maintains HR documentation

#### Dependencies

- Staff profiles (Requirement 4)
- Performance metrics (Requirement 21)

#### Key Data Entities

- StaffReview (ID, staff_id, reviewer_id, rating, feedback, goals, review_date, tenant_id)
- ReviewHistory (ID, staff_id, review_count, average_rating, last_review_date, tenant_id)
- ImprovementPlan (ID, staff_id, review_id, goals, target_date, status, tenant_id)

#### User Roles

- Manager: Conducts reviews
- Staff: Receives feedback
- Owner: Views review analytics

---

### Requirement 27: Skill/Specialty Tracking

**User Story:** As a manager, I want to track staff skills and specialties, so that I can assign appropriate services and plan training.

#### Detailed Description

The skill tracking system maintains a comprehensive inventory of staff skills and specialties with proficiency levels. Managers can assign services to staff only if they have required skills at appropriate proficiency levels. The system identifies skill gaps and recommends training. Analytics track skill distribution across the team, enabling workforce planning.

#### Technical Specifications

- **Skill Inventory**: Track all skills and specialties
- **Proficiency Levels**: Define proficiency levels (beginner, intermediate, advanced, expert)
- **Service Requirements**: Define required skills for each service
- **Skill Gaps**: Identify missing skills
- **Training Recommendations**: Recommend training based on gaps
- **Skill Matrix**: Display skill distribution across team
- **Skill Development**: Track skill development over time

#### Business Context

- **Problem Solved**: Improves service quality through skill matching; enables targeted training
- **ROI**: Improves service quality by 20-30%; reduces training costs
- **Competitive Advantage**: Skilled staff improves customer satisfaction

#### Integration Points

- **Staff Profiles (Req 4)**: Store skills in staff profiles
- **Training & Certification (Req 22)**: Track skill development through training
- **Appointment Booking (Req 3)**: Match customers to skilled staff

#### Data Model Details

- **Skill**: ID (UUID), name (string), category (string), proficiency_levels (JSON), tenant_id (FK)
- **StaffSkill**: ID (UUID), staff_id (FK), skill_id (FK), proficiency_level (enum: beginner/intermediate/advanced/expert), acquired_date (date), tenant_id (FK)
- **SkillMatrix**: ID (UUID), tenant_id (FK), skill_id (FK), staff_count_by_level (JSON)

#### User Workflows

**For Manager Managing Skills:**
1. Access skill inventory
2. Add new skills
3. Assign skills to staff
4. Set proficiency levels
5. Track skill development
6. Identify skill gaps

**For Staff Updating Skills:**
1. Log into staff portal
2. Add new skills
3. Update proficiency levels
4. Request training for new skills

**For System Matching Skills:**
1. Receive appointment booking request
2. Check service requirements
3. Match to staff with required skills
4. Suggest skilled staff to customer

#### Edge Cases & Constraints

- **Skill Levels**: Handle different proficiency levels
- **Skill Prerequisites**: Handle skills with prerequisites
- **Skill Expiration**: Handle skills that expire without practice

#### Performance Requirements

- **Skill Matching**: Match skills within 100ms
- **Skill Matrix**: Generate within 5 seconds

#### Security Considerations

- **Skill Data**: Restrict access to authorized managers
- **Audit Trail**: Log skill changes

#### Compliance Requirements

- **Service Quality**: Ensure skills meet service quality requirements

#### Acceptance Criteria

1. WHEN creating staff profile, THE System SHALL capture skills and specialties
2. WHEN assigning services, THE System SHALL verify staff has required skills
3. WHEN staff develops new skills, THE System SHALL update their profile
4. WHEN viewing staff, THE System SHALL display skill matrix and proficiency levels
5. WHEN planning training, THE System SHALL identify skill gaps
6. WHEN a customer requests specialist, THE System SHALL match to qualified staff
7. WHEN exporting staff data, THE System SHALL include skill inventory

#### Business Value

- Improves service quality through skill matching
- Enables targeted training
- Supports customer satisfaction
- Optimizes staff utilization

#### Dependencies

- Staff profiles (Requirement 4)
- Training & certification tracking (Requirement 22)

#### Key Data Entities

- Skill (ID, name, category, proficiency_levels, tenant_id)
- StaffSkill (ID, staff_id, skill_id, proficiency_level, acquired_date, tenant_id)
- SkillMatrix (ID, tenant_id, skill_id, staff_count_by_level)

#### User Roles

- Manager: Manages skills
- Staff: Updates skills
- Owner: Views skill inventory

---

### Requirement 28: Product/Supply Tracking

**User Story:** As a manager, I want to track products and supplies used in services, so that I can manage costs and ensure availability.

#### Detailed Description

The product and supply tracking system maintains inventory of products and supplies used in service delivery. When services are completed, used products are automatically deducted from inventory. The system tracks product costs and calculates product cost per service, enabling accurate pricing. Low stock alerts notify managers to reorder before stockouts occur.

#### Technical Specifications

- **Product Catalog**: Maintain product and supply inventory
- **Service Products**: Define products required for each service
- **Automatic Deduction**: Deduct used products from inventory
- **Cost Tracking**: Track product costs and usage
- **Low Stock Alerts**: Alert when stock falls below minimum
- **Supplier Integration**: Track supplier information
- **Usage Analytics**: Analyze product usage by service and staff

#### Business Context

- **Problem Solved**: Improves cost management; prevents stockouts
- **ROI**: Reduces waste by 15-20%; prevents service disruptions
- **Competitive Advantage**: Efficient supply management improves profitability

#### Integration Points

- **Appointment Booking (Req 3)**: Deduct products upon completion
- **Expense Tracking (Req 15)**: Track product costs
- **Stock Level Management (Req 28)**: Manage inventory levels

#### Data Model Details

- **Product**: ID (UUID), name (string), category (string), unit_cost (decimal), supplier_id (FK), tenant_id (FK)
- **ServiceProduct**: ID (UUID), service_id (FK), product_id (FK), quantity_per_service (decimal), tenant_id (FK)
- **ProductUsage**: ID (UUID), appointment_id (FK), product_id (FK), quantity_used (decimal), cost (decimal), tenant_id (FK)

#### User Workflows

**For Manager Managing Products:**
1. Access product inventory
2. Add new products
3. Set unit costs
4. Define products for services
5. Monitor stock levels
6. Receive low stock alerts

**For System Tracking Usage:**
1. Appointment completed
2. Identify products used
3. Deduct from inventory
4. Calculate cost
5. Update financial records

#### Edge Cases & Constraints

- **Partial Usage**: Handle partial product usage
- **Waste**: Track product waste separately
- **Expiration**: Handle product expiration dates

#### Performance Requirements

- **Product Deduction**: Deduct within 500ms
- **Usage Report**: Generate within 5 seconds

#### Security Considerations

- **Product Data**: Restrict access to authorized managers
- **Cost Data**: Restrict access to cost information

#### Compliance Requirements

- **Inventory Accuracy**: Maintain accurate inventory records

#### Acceptance Criteria

1. WHEN creating a service, THE System SHALL define products/supplies required
2. WHEN an appointment is completed, THE System SHALL deduct used products from inventory
3. WHEN product stock is low, THE System SHALL alert manager to reorder
4. WHEN viewing inventory, THE System SHALL display stock levels and usage rates
5. WHEN calculating service cost, THE System SHALL include product costs
6. WHEN exporting reports, THE System SHALL show product usage by service and staff
7. WHEN a product is discontinued, THE System SHALL archive it and update services

#### Business Value

- Improves cost management
- Prevents stockouts
- Enables accurate pricing
- Optimizes inventory levels

#### Dependencies

- Appointment booking (Requirement 3)
- Expense tracking (Requirement 15)

#### Key Data Entities

- Product (ID, name, category, unit_cost, supplier_id, tenant_id)
- ServiceProduct (ID, service_id, product_id, quantity_per_service, tenant_id)
- ProductUsage (ID, appointment_id, product_id, quantity_used, cost, tenant_id)

#### User Roles

- Manager: Manages products
- Staff: Uses products
- Owner: Views product analytics

---

### Requirement 29: Stock Level Management

**User Story:** As a manager, I want to manage stock levels, so that I can prevent stockouts and minimize waste.

#### Detailed Description

The stock level management system tracks inventory quantities, reorder points, and reorder quantities. When stock falls below the reorder point, the system alerts managers to reorder. The system supports multiple inventory valuation methods (FIFO, weighted average) for accurate financial reporting. Inventory counts enable reconciliation of physical stock to system records.

#### Technical Specifications

- **Stock Tracking**: Track quantity on hand for each product
- **Reorder Points**: Define minimum stock levels
- **Reorder Quantities**: Define quantities to order
- **Inventory Valuation**: Support FIFO and weighted average methods
- **Inventory Counts**: Support physical inventory counts
- **Variance Tracking**: Track differences between physical and system counts
- **Expiration Tracking**: Track product expiration dates
- **Stock Movements**: Log all stock movements

#### Business Context

- **Problem Solved**: Prevents stockouts and service disruptions; reduces waste
- **ROI**: Reduces waste by 20-30%; prevents revenue loss from stockouts
- **Competitive Advantage**: Reliable supply availability improves customer satisfaction

#### Integration Points

- **Product/Supply Tracking (Req 27)**: Track product usage
- **Supplier Management (Req 29)**: Manage reorders
- **Inventory Reconciliation (Req 30)**: Reconcile physical to system counts

#### Data Model Details

- **StockLevel**: ID (UUID), product_id (FK), quantity_on_hand (decimal), reorder_point (decimal), reorder_quantity (decimal), tenant_id (FK)
- **StockMovement**: ID (UUID), product_id (FK), type (enum: purchase/usage/adjustment/return), quantity (decimal), reference_id (string), timestamp (timestamp), tenant_id (FK)
- **InventoryCount**: ID (UUID), product_id (FK), physical_count (decimal), system_count (decimal), variance (decimal), count_date (date), tenant_id (FK)

#### User Workflows

**For Manager Managing Stock:**
1. View stock levels
2. Receive low stock alerts
3. Create purchase orders
4. Receive inventory
5. Update stock levels
6. Conduct inventory counts

**For System Tracking Stock:**
1. Product received
2. Update stock level
3. Check against reorder point
4. Alert if below reorder point
5. Track all movements

#### Edge Cases & Constraints

- **Negative Stock**: Prevent negative stock levels
- **Expiration**: Handle expired products
- **Variance**: Investigate stock variances

#### Performance Requirements

- **Stock Update**: Update within 100ms
- **Inventory Count**: Process within 5 seconds

#### Security Considerations

- **Stock Data**: Restrict access to authorized managers
- **Audit Trail**: Log all stock movements

#### Compliance Requirements

- **Inventory Accuracy**: Maintain accurate inventory records

#### Acceptance Criteria

1. WHEN receiving inventory, THE System SHALL update stock levels and record supplier
2. WHEN stock is used, THE System SHALL automatically deduct from inventory
3. WHEN stock falls below minimum, THE System SHALL alert manager
4. WHEN viewing stock report, THE System SHALL display current levels and reorder points
5. WHEN calculating inventory value, THE System SHALL use FIFO or weighted average method
6. WHEN conducting inventory count, THE System SHALL compare physical to system records
7. WHEN stock expires, THE System SHALL alert manager and prevent use

#### Business Value

- Prevents stockouts and service disruptions
- Reduces waste and spoilage
- Improves cash flow through inventory optimization
- Enables accurate financial reporting

#### Dependencies

- Product/supply tracking (Requirement 27)
- Expense tracking (Requirement 15)

#### Key Data Entities

- StockLevel (ID, product_id, quantity_on_hand, reorder_point, reorder_quantity, tenant_id)
- StockMovement (ID, product_id, type, quantity, reference_id, timestamp, tenant_id)
- InventoryCount (ID, product_id, physical_count, system_count, variance, count_date, tenant_id)

#### User Roles

- Manager: Manages stock
- Staff: Uses stock
- Owner: Views inventory reports

---

### Requirement 30: Supplier Management & Ordering

**User Story:** As a manager, I want to manage suppliers and automate ordering, so that I can reduce procurement overhead and ensure supply continuity.

#### Detailed Description

The supplier management system maintains a database of suppliers with contact information, pricing, and lead times. The system suggests reorder quantities based on usage patterns and lead times. Purchase orders are created automatically or manually, with tracking of delivery status. The system compares supplier pricing and performance, enabling data-driven supplier selection.

#### Technical Specifications

- **Supplier Database**: Maintain supplier information and pricing
- **Pricing Comparison**: Compare prices across suppliers
- **Purchase Orders**: Create and track purchase orders
- **Delivery Tracking**: Track order delivery status
- **Performance Metrics**: Track supplier performance (on-time delivery, quality)
- **Reorder Suggestions**: Suggest reorder quantities based on usage
- **Supplier Ratings**: Rate suppliers based on performance
- **Bulk Ordering**: Support bulk orders and discounts

#### Business Context

- **Problem Solved**: Reduces procurement time and costs; ensures supply continuity
- **ROI**: Reduces procurement costs by 10-15%; prevents stockouts
- **Competitive Advantage**: Efficient procurement improves profitability

#### Integration Points

- **Stock Level Management (Req 28)**: Trigger reorders based on stock levels
- **Expense Tracking (Req 15)**: Track supplier costs
- **Inventory Reconciliation (Req 30)**: Reconcile received orders

#### Data Model Details

- **Supplier**: ID (UUID), name (string), contact_info (JSON), payment_terms (string), lead_time_days (integer), tenant_id (FK)
- **SupplierProduct**: ID (UUID), supplier_id (FK), product_id (FK), unit_price (decimal), minimum_order (decimal), tenant_id (FK)
- **PurchaseOrder**: ID (UUID), supplier_id (FK), order_date (date), delivery_date (date, nullable), total_cost (decimal), status (enum: pending/shipped/delivered/cancelled), tenant_id (FK)
- **PurchaseOrderLineItem**: ID (UUID), purchase_order_id (FK), product_id (FK), quantity (decimal), unit_price (decimal), total (decimal), tenant_id (FK)

#### User Workflows

**For Manager Managing Suppliers:**
1. Add new supplier
2. Enter supplier information
3. Add products and pricing
4. Compare supplier pricing
5. Rate supplier performance
6. Create purchase orders

**For System Creating Orders:**
1. Stock falls below reorder point
2. Suggest reorder quantity
3. Compare supplier pricing
4. Create purchase order
5. Track delivery

#### Edge Cases & Constraints

- **Lead Times**: Account for supplier lead times in reorder timing
- **Minimum Orders**: Handle supplier minimum order quantities
- **Bulk Discounts**: Support bulk order discounts
- **Delivery Delays**: Handle delayed deliveries

#### Performance Requirements

- **Order Creation**: Create within 500ms
- **Pricing Comparison**: Compare within 2 seconds

#### Security Considerations

- **Supplier Data**: Restrict access to authorized managers
- **Pricing Data**: Restrict access to pricing information

#### Compliance Requirements

- **Procurement Records**: Maintain procurement records

#### Acceptance Criteria

1. WHEN adding a supplier, THE System SHALL capture contact info, pricing, and lead times
2. WHEN stock is low, THE System SHALL suggest reorder quantities based on usage
3. WHEN creating purchase order, THE System SHALL calculate costs and track delivery
4. WHEN order is received, THE System SHALL update inventory and verify quantities
5. WHEN comparing suppliers, THE System SHALL display pricing and performance metrics
6. WHEN managing supplier relationships, THE System SHALL track payment history
7. WHEN exporting supplier data, THE System SHALL provide performance reports

#### Business Value

- Reduces procurement time and costs
- Ensures supply continuity
- Enables supplier performance tracking
- Improves cash flow management

#### Dependencies

- Product/supply tracking (Requirement 27)
- Stock level management (Requirement 28)
- Expense tracking (Requirement 15)

#### Key Data Entities

- Supplier (ID, name, contact_info, payment_terms, lead_time_days, tenant_id)
- SupplierProduct (ID, supplier_id, product_id, unit_price, minimum_order, tenant_id)
- PurchaseOrder (ID, supplier_id, order_date, delivery_date, total_cost, status, tenant_id)
- PurchaseOrderLineItem (ID, purchase_order_id, product_id, quantity, unit_price, total, tenant_id)

#### User Roles

- Manager: Manages suppliers and orders
- Owner: Views supplier performance
- Accountant: Tracks supplier payments

---

### Requirement 31: Inventory Reconciliation

**User Story:** As a manager, I want to reconcile physical inventory with system records, so that I can identify discrepancies and prevent losses.

#### Detailed Description

The inventory reconciliation system enables managers to conduct physical inventory counts and compare results to system records. Discrepancies are flagged for investigation, with the system providing usage history to identify causes. Adjustments are recorded with reasons and approvals, maintaining audit trails for compliance. The system identifies patterns of losses, enabling investigation of theft or waste.

#### Technical Specifications

- **Inventory Counts**: Provide checklist of all products
- **Count Entry**: Enter physical counts and compare to system
- **Discrepancy Detection**: Flag variances for investigation
- **Variance Analysis**: Review usage history and movements
- **Adjustments**: Record adjustments with reasons and approvals
- **Loss Tracking**: Identify patterns of losses
- **Reconciliation Reports**: Generate detailed reconciliation reports
- **Audit Trail**: Maintain audit trail of all adjustments

#### Business Context

- **Problem Solved**: Identifies inventory losses and theft; ensures accurate financial records
- **ROI**: Reduces losses by 30-50%; improves inventory accuracy
- **Competitive Advantage**: Accurate inventory management improves profitability

#### Integration Points

- **Stock Level Management (Req 28)**: Compare physical to system counts
- **Product/Supply Tracking (Req 27)**: Track product movements
- **Expense Tracking (Req 15)**: Record adjustments as expenses

#### Data Model Details

- **InventoryCount**: ID (UUID), product_id (FK), physical_count (decimal), system_count (decimal), variance (decimal), count_date (date), counted_by (FK), tenant_id (FK)
- **InventoryAdjustment**: ID (UUID), product_id (FK), adjustment_quantity (decimal), reason (string), approved_by (FK), adjustment_date (date), tenant_id (FK)
- **InventoryReconciliationReport**: ID (UUID), count_date (date), total_variance (decimal), high_variance_items (JSON), reconciled_by (FK), tenant_id (FK)

#### User Workflows

**For Manager Conducting Count:**
1. Access inventory count interface
2. Provide checklist of all products
3. Enter physical counts
4. System compares to system records
5. Flag discrepancies
6. Investigate variances
7. Record adjustments

**For System Analyzing Variances:**
1. Compare physical to system counts
2. Calculate variance
3. Review usage history
4. Identify potential causes
5. Flag for investigation

**For Manager Investigating Losses:**
1. Review high-variance items
2. Check usage history
3. Identify patterns
4. Investigate potential theft or waste
5. Take corrective action

#### Edge Cases & Constraints

- **Counting Errors**: Handle counting errors and recounts
- **Timing Differences**: Account for transactions during count
- **Partial Counts**: Support partial inventory counts
- **Variance Thresholds**: Define thresholds for investigation

#### Performance Requirements

- **Count Entry**: Enter within 500ms
- **Variance Analysis**: Analyze within 5 seconds
- **Report Generation**: Generate within 10 seconds

#### Security Considerations

- **Count Data**: Restrict access to authorized managers
- **Audit Trail**: Log all adjustments and approvals

#### Compliance Requirements

- **Audit Trail**: Maintain audit trail for compliance
- **Inventory Accuracy**: Ensure accuracy of inventory records

#### Acceptance Criteria

1. WHEN conducting inventory count, THE System SHALL provide checklist of all products
2. WHEN entering physical counts, THE System SHALL compare to system records
3. WHEN discrepancies are found, THE System SHALL flag for investigation
4. WHEN investigating variance, THE System SHALL review usage history and movements
5. WHEN reconciliation is complete, THE System SHALL generate report with adjustments
6. WHEN adjusting inventory, THE System SHALL record reason and approver
7. WHEN tracking losses, THE System SHALL identify patterns and high-loss items

#### Business Value

- Identifies inventory losses and theft
- Ensures accurate financial records
- Improves inventory management
- Supports audit requirements

#### Dependencies

- Stock level management (Requirement 28)
- Product/supply tracking (Requirement 27)

#### Key Data Entities

- InventoryCount (ID, product_id, physical_count, system_count, variance, count_date, tenant_id)
- InventoryAdjustment (ID, product_id, adjustment_quantity, reason, approved_by, adjustment_date, tenant_id)
- InventoryReconciliationReport (ID, count_date, total_variance, high_variance_items, tenant_id)

#### User Roles

- Manager: Conducts counts
- Owner: Reviews reconciliation
- Accountant: Adjusts inventory

---

## PHASE 3 - Customer Engagement & Marketing

### Requirement 32: Birthday/Anniversary Promotions

**User Story:** As a marketing manager, I want to send birthday and anniversary promotions, so that I can increase customer engagement and loyalty.

#### Detailed Description

The birthday and anniversary promotion system automatically sends personalized promotional offers to customers on significant dates. The system tracks customer birthdays and service anniversaries, automatically triggering promotions at configured times. Promotions include customizable discount percentages and service eligibility. Analytics track redemption rates and revenue impact, enabling optimization of promotion strategies.

#### Technical Specifications

- **Date Tracking**: Track customer birthdays and service anniversaries
- **Automatic Triggers**: Send promotions automatically on specified dates
- **Customizable Offers**: Define discount percentages and eligible services
- **Promotion Codes**: Generate unique promotion codes
- **Redemption Tracking**: Track promotion usage and redemption
- **Analytics**: Measure promotion effectiveness and ROI
- **Multi-Channel**: Send via email, SMS, or push notifications

#### Business Context

- **Problem Solved**: Increases customer engagement and loyalty through personalized offers
- **ROI**: Increases repeat bookings by 20-30% during key dates
- **Competitive Advantage**: Personalized marketing improves customer experience

#### Integration Points

- **Customer Profiles (Req 5)**: Store birthday and anniversary dates
- **Notifications (Req 7)**: Send promotional notifications
- **Billing & Payment (Req 6)**: Apply discounts automatically

#### Data Model Details

- **Promotion**: ID (UUID), type (enum: birthday/anniversary), discount_percentage (integer), start_date (date), end_date (date), eligible_services (JSON), tenant_id (FK)
- **CustomerPromotion**: ID (UUID), customer_id (FK), promotion_id (FK), redeemed (boolean), redeemed_date (date, nullable), tenant_id (FK)
- **PromotionAnalytics**: ID (UUID), promotion_id (FK), impressions (integer), redemptions (integer), revenue_impact (decimal), tenant_id (FK)

#### User Workflows

**For Marketing Manager Creating Promotion:**
1. Access promotion settings
2. Select promotion type (birthday/anniversary)
3. Define discount percentage
4. Select eligible services
5. Set promotion dates
6. Save and activate

**For Customer Receiving Promotion:**
1. Receive promotional email/SMS on birthday/anniversary
2. View promotion details and discount
3. Book appointment using promotion code
4. Discount applied automatically

**For Owner Analyzing Promotions:**
1. View promotion analytics
2. See redemption rates
3. Measure revenue impact
4. Optimize promotion strategy

#### Edge Cases & Constraints

- **Date Accuracy**: Handle customers without birthday information
- **Timezone Issues**: Send promotions in customer's local timezone
- **Promotion Stacking**: Prevent combining multiple promotions
- **Expiration**: Handle promotion expiration

#### Performance Requirements

- **Promotion Sending**: Send within 1 second of trigger
- **Analytics Calculation**: Calculate within 5 seconds

#### Security Considerations

- **Promotion Codes**: Prevent code reuse and fraud
- **Audit Trail**: Log all promotion usage

#### Compliance Requirements

- **GDPR**: Obtain consent before sending marketing promotions
- **CAN-SPAM**: Include unsubscribe link in all emails

#### Acceptance Criteria

1. WHEN a customer's birthday approaches, THE System SHALL automatically send promotional offer
2. WHEN creating promotion, THE System SHALL define discount percentage and service eligibility
3. WHEN a customer uses birthday promotion, THE System SHALL apply discount automatically
4. WHEN viewing promotion analytics, THE System SHALL display redemption rates and revenue impact
5. WHEN a promotion expires, THE System SHALL remove it from customer's available offers
6. WHEN tracking anniversaries, THE System SHALL recognize customer tenure milestones
7. WHEN exporting promotion data, THE System SHALL show effectiveness by customer segment

#### Business Value

- Increases customer engagement and loyalty
- Drives repeat bookings during key dates
- Improves customer lifetime value
- Enables personalized marketing

#### Dependencies

- Customer profiles (Requirement 5)
- Notifications (Requirement 7)
- Billing & payment processing (Requirement 6)

#### Key Data Entities

- Promotion (ID, type, discount_percentage, start_date, end_date, eligible_services, tenant_id)
- CustomerPromotion (ID, customer_id, promotion_id, redeemed, redeemed_date, tenant_id)
- PromotionAnalytics (ID, promotion_id, impressions, redemptions, revenue_impact, tenant_id)

#### User Roles

- Marketing Manager: Creates promotions
- Customer: Receives and uses promotions
- Owner: Views promotion analytics

---

### Requirement 33: Referral Program Tracking

**User Story:** As a business owner, I want to track referrals, so that I can incentivize word-of-mouth marketing and grow customer base.

#### Detailed Description

The referral program tracking system enables businesses to harness word-of-mouth marketing by incentivizing customers to refer friends and family. Each customer receives a unique referral code that they can share through email, SMS, or social media. When a referred customer books their first appointment using the code, both the referrer and referred customer receive rewards. The system automatically tracks all referrals, calculates rewards, and applies them to customer accounts.

The referral program is highly configurable, allowing businesses to define reward amounts, eligible services, and referral tiers. Advanced businesses can implement tiered rewards where customers earn increasing rewards for multiple successful referrals. The system prevents fraud through validation checks, ensuring referred customers are genuinely new to the business.

Analytics provide deep insights into referral program effectiveness, showing which customers are top referrers, which services drive the most referrals, and the overall ROI of the program. Businesses can identify their most valuable referral sources and optimize their referral strategy accordingly.

#### Technical Specifications

- **Unique Codes**: Generate cryptographically secure referral codes with expiration dates
- **Code Validation**: Validate codes during booking; prevent reuse and fraud
- **Reward Calculation**: Automatic calculation based on configurable reward rules
- **Tiered Rewards**: Support multiple reward tiers based on referral count
- **Fraud Prevention**: Validate referred customers are new; prevent self-referrals
- **Reward Application**: Apply rewards as account credit, discounts, or free services
- **Analytics**: Track referral sources, conversion rates, and program ROI
- **Notifications**: Notify referrers when referral is successful and reward is earned

#### Business Context

- **Problem Solved**: Enables cost-effective customer acquisition through word-of-mouth marketing
- **ROI**: Reduces customer acquisition cost by 40-60% compared to paid advertising; referred customers have 25% higher lifetime value
- **Competitive Advantage**: Referral programs build community and loyalty; referred customers are more engaged and less likely to churn

#### Integration Points

- **Customer Profiles (Req 5)**: Store referral codes and referral history in customer profile
- **Appointment Booking (Req 3)**: Validate referral codes during booking; apply rewards
- **Notifications (Req 7)**: Notify referrers of successful referrals and reward earnings
- **Billing & Payment (Req 6)**: Apply referral rewards as account credit or discounts
- **Performance Metrics (Req 21)**: Track referral program metrics and ROI

#### Data Model Details

- **ReferralCode**: ID (UUID), customer_id (FK), code (string, unique), created_at (timestamp), expires_at (timestamp), status (enum: active/expired/used), tenant_id (FK)
- **Referral**: ID (UUID), referrer_id (FK), referred_customer_id (FK), referral_code (string), status (enum: pending/completed/cancelled), reward_amount (decimal), reward_type (enum: credit/discount/free_service), earned_at (timestamp), redeemed_at (timestamp, nullable), tenant_id (FK)
- **ReferralRewardRule**: ID (UUID), referral_count (integer), reward_amount (decimal), reward_type (enum), eligible_services (JSON array), tenant_id (FK)
- **ReferralAnalytics**: ID (UUID), date (date), referral_count (integer), conversion_rate (decimal), revenue_from_referrals (decimal), top_referrers (JSON), tenant_id (FK)

#### User Workflows

**For Customer Generating Referral Code:**
1. Log in to customer portal or app
2. Navigate to "Refer a Friend" section
3. View their unique referral code
4. Copy code or generate shareable link
5. Share via email, SMS, or social media
6. Track referral status in dashboard

**For Referred Customer Using Code:**
1. Receive referral link from friend
2. Click link or enter referral code during booking
3. Complete appointment booking
4. System validates code and tracks referral
5. Both referrer and referred customer receive rewards

**For Business Owner Managing Program:**
1. Access referral program settings
2. Define reward amounts and tiers
3. Set eligible services for referrals
4. View referral analytics and top referrers
5. Adjust program rules based on performance
6. Export referral data for marketing analysis

#### Edge Cases & Constraints

- **Self-Referrals**: Prevent customers from referring themselves; validate email domain
- **Duplicate Referrals**: Prevent same customer from being referred multiple times
- **Code Expiration**: Implement expiration dates for codes; allow renewal
- **Reward Limits**: Set maximum rewards per customer per period to prevent abuse
- **Fraud Detection**: Validate referred customers are genuinely new; flag suspicious patterns
- **Reward Redemption**: Handle cases where customer cancels before reward is redeemed
- **Program Changes**: Handle changes to reward rules; apply retroactively or prospectively

#### Performance Requirements

- **Code Generation**: Generate unique code within 100ms
- **Code Validation**: Validate code during booking within 200ms
- **Reward Calculation**: Calculate rewards within 500ms
- **Analytics Calculation**: Calculate referral analytics within 5 seconds
- **Referral Tracking**: Track referral within 1 second of booking completion

#### Security Considerations

- **Code Security**: Generate cryptographically secure codes; prevent guessing
- **Fraud Prevention**: Implement checks to prevent self-referrals and duplicate referrals
- **Reward Integrity**: Prevent unauthorized reward modifications
- **Audit Trail**: Log all referral activities with user and timestamp
- **Data Privacy**: Protect referrer and referred customer information

#### Compliance Requirements

- **GDPR**: Obtain consent before using customer data for referral tracking
- **CAN-SPAM**: Include unsubscribe option in referral emails
- **Fraud Prevention**: Comply with anti-fraud regulations; report suspicious activity

#### Acceptance Criteria

1. WHEN a customer requests referral code, THE System SHALL generate unique code and display sharing options
2. WHEN a referred customer books using code, THE System SHALL validate code and track referral
3. WHEN referral is completed, THE System SHALL credit both referrer and referred customer with rewards
4. WHEN viewing referral analytics, THE System SHALL display referral sources, conversion rates, and program ROI
5. WHEN a referral reward is earned, THE System SHALL notify customer and display reward in account
6. WHEN redeeming referral credit, THE System SHALL apply to customer account automatically
7. WHEN exporting referral data, THE System SHALL show top referrers, program performance, and ROI

#### Business Value

- Drives customer acquisition through word-of-mouth marketing
- Reduces customer acquisition cost by 40-60%
- Increases customer lifetime value through referred customers
- Builds community and loyalty
- Provides low-cost marketing channel

#### Dependencies

- Customer profiles (Requirement 5)
- Appointment booking (Requirement 3)
- Notifications (Requirement 7)
- Billing & payment processing (Requirement 6)

#### Key Data Entities

- ReferralCode (ID, customer_id, code, created_at, expires_at, status, tenant_id)
- Referral (ID, referrer_id, referred_customer_id, status, reward_amount, reward_type, tenant_id)
- ReferralRewardRule (ID, referral_count, reward_amount, reward_type, eligible_services, tenant_id)
- ReferralAnalytics (ID, date, referral_count, conversion_rate, revenue_from_referrals, tenant_id)

#### User Roles

- Customer: Generates and shares referral codes; receives rewards
- Owner: Manages referral program and rules
- System: Tracks referrals and calculates rewards

---

### Requirement 34: Customer Segmentation & Targeting

**User Story:** As a marketing manager, I want to segment customers, so that I can target marketing campaigns effectively.

#### Detailed Description

The customer segmentation system enables businesses to divide their customer base into meaningful groups based on behavior, demographics, and engagement patterns. Segments can be created using simple criteria (e.g., customers who booked in the last 30 days) or complex rules combining multiple conditions (e.g., high-value customers who haven't booked in 60 days). The system automatically manages segment membership, adding and removing customers as they meet or stop meeting segment criteria.

Segments enable highly targeted marketing campaigns, allowing businesses to send personalized messages to specific customer groups. For example, a business might send a "We miss you" campaign to inactive customers while sending an upsell campaign to high-value customers. The system tracks segment performance, showing which segments are most responsive to campaigns and which segments have the highest lifetime value.

Dynamic segments update in real-time as customer behavior changes, ensuring campaigns always target the right audience. Businesses can create unlimited segments and combine them for complex targeting scenarios. Integration with email and SMS providers enables seamless campaign execution to segmented audiences.

#### Technical Specifications

- **Segment Types**: Static (manual), dynamic (rule-based), behavioral (based on actions)
- **Segment Criteria**: Support complex rules with AND/OR logic, date ranges, numeric comparisons
- **Automatic Membership**: Automatically add/remove customers as they meet/stop meeting criteria
- **Real-Time Updates**: Update segment membership in real-time as customer data changes
- **Segment Combination**: Combine multiple segments for complex targeting
- **Performance Tracking**: Track segment size, engagement, and revenue metrics
- **Bulk Operations**: Import/export segment definitions and membership
- **Predictive Segmentation**: Use machine learning to identify high-value customer segments

#### Business Context

- **Problem Solved**: Enables targeted marketing to specific customer groups; improves campaign effectiveness
- **ROI**: Increases campaign response rates by 50-100% through targeted messaging; improves marketing ROI by 30-40%
- **Competitive Advantage**: Personalized marketing improves customer experience and engagement; enables data-driven marketing decisions

#### Integration Points

- **Customer Profiles (Req 5)**: Use customer data to determine segment membership
- **Email Marketing Automation (Req 35)**: Target campaigns to specific segments
- **Performance Metrics (Req 21)**: Track segment performance and engagement
- **Appointment Booking (Req 3)**: Track customer behavior for segmentation
- **Billing & Payment (Req 6)**: Use spending data for segmentation

#### Data Model Details

- **Segment**: ID (UUID), name (string), description (text), type (enum: static/dynamic/behavioral), criteria (JSON), created_at (timestamp), updated_at (timestamp), tenant_id (FK)
- **SegmentCriteria**: ID (UUID), segment_id (FK), field (string), operator (enum: equals/contains/greater_than/less_than/between), value (JSON), logic (enum: AND/OR), tenant_id (FK)
- **SegmentMembership**: ID (UUID), segment_id (FK), customer_id (FK), added_date (timestamp), removed_date (timestamp, nullable), reason (string), tenant_id (FK)
- **SegmentAnalytics**: ID (UUID), segment_id (FK), date (date), member_count (integer), average_spend (decimal), engagement_rate (decimal), revenue (decimal), tenant_id (FK)

#### User Workflows

**For Marketing Manager Creating Segment:**
1. Access segmentation interface
2. Define segment name and description
3. Select segment type (static/dynamic/behavioral)
4. Define segment criteria using rule builder
5. Preview segment members
6. Save segment
7. System automatically manages membership

**For Marketing Manager Targeting Campaign:**
1. Create email or SMS campaign
2. Select target segment(s)
3. Customize message for segment
4. Schedule campaign
5. System sends to all segment members
6. Track campaign performance by segment

**For Owner Analyzing Segments:**
1. View all segments and member counts
2. Analyze segment characteristics
3. Compare segment performance
4. Identify high-value segments
5. Plan marketing strategy based on segments
6. Export segment data for analysis

#### Edge Cases & Constraints

- **Overlapping Segments**: Handle customers in multiple segments; prevent duplicate messaging
- **Segment Changes**: Handle criteria changes; update membership accordingly
- **Large Segments**: Handle segments with millions of members; optimize query performance
- **Inactive Segments**: Archive unused segments; prevent accidental targeting
- **Segment Conflicts**: Handle conflicting criteria; use clear logic operators
- **Data Quality**: Handle missing or incomplete customer data in segmentation

#### Performance Requirements

- **Segment Creation**: Create segment within 1 second
- **Membership Update**: Update membership within 5 seconds of customer data change
- **Segment Query**: Query segment members within 2 seconds
- **Analytics Calculation**: Calculate segment analytics within 10 seconds
- **Campaign Targeting**: Target campaign to segment within 1 second

#### Security Considerations

- **Segment Data**: Restrict access to segment definitions to authorized marketing staff
- **Customer Privacy**: Ensure segmentation complies with privacy regulations
- **Audit Trail**: Log all segment changes and campaign targeting
- **Data Accuracy**: Validate segment criteria to prevent unintended targeting

#### Compliance Requirements

- **GDPR**: Ensure segmentation complies with data protection regulations
- **CAN-SPAM**: Obtain consent before targeting marketing campaigns
- **Fair Marketing**: Ensure segmentation doesn't discriminate based on protected characteristics

#### Acceptance Criteria

1. WHEN creating segment, THE System SHALL define criteria using rule builder with AND/OR logic
2. WHEN customers meet segment criteria, THE System SHALL automatically add them to segment
3. WHEN viewing segments, THE System SHALL display segment size, characteristics, and member list
4. WHEN targeting campaigns, THE System SHALL allow selecting one or multiple segments
5. WHEN a customer's profile changes, THE System SHALL update segment membership in real-time
6. WHEN analyzing segments, THE System SHALL display engagement, revenue, and performance metrics
7. WHEN exporting segment data, THE System SHALL provide customer lists and segment definitions

#### Business Value

- Enables highly targeted marketing campaigns
- Improves marketing ROI by 30-40%
- Increases customer engagement through personalization
- Supports data-driven marketing decisions
- Enables customer lifecycle marketing

#### Dependencies

- Customer profiles (Requirement 5)
- Performance metrics (Requirement 21)
- Email marketing automation (Requirement 35)

#### Key Data Entities

- Segment (ID, name, type, criteria, created_at, tenant_id)
- SegmentCriteria (ID, segment_id, field, operator, value, logic, tenant_id)
- SegmentMembership (ID, segment_id, customer_id, added_date, removed_date, tenant_id)
- SegmentAnalytics (ID, segment_id, date, member_count, average_spend, engagement_rate, tenant_id)

#### User Roles

- Marketing Manager: Creates and manages segments
- Owner: Views segment analytics
- System: Manages segment membership

---

### Requirement 35: Membership/Package Management

**User Story:** As a business owner, I want to offer membership and service packages, so that I can increase customer commitment and predictable revenue.

#### Detailed Description

The membership and package management system enables businesses to create and manage membership tiers and service packages that customers can purchase. Memberships provide customers with a set number of services or credits that they can use over a defined period. For example, a gym might offer a "10 Classes per Month" membership, while a salon might offer a "Unlimited Hair Services" membership.

Packages bundle multiple services at a discounted price, encouraging customers to try new services. For example, a spa might offer a "Relaxation Package" that includes a massage, facial, and body treatment at a bundled price. The system tracks package usage, automatically deducting services as customers book appointments. When packages are expiring, the system sends renewal reminders to encourage continued engagement.

Memberships provide predictable recurring revenue, improving business cash flow and enabling better forecasting. The system supports flexible membership terms (monthly, quarterly, annual) and allows businesses to offer promotional pricing for new members. Analytics track membership adoption, renewal rates, and revenue impact, enabling optimization of membership offerings.

#### Technical Specifications

- **Membership Types**: Service-based (X services per period), credit-based (X credits per period), unlimited
- **Package Types**: Service bundles, time-limited packages, one-time packages
- **Flexible Terms**: Support monthly, quarterly, annual, and custom terms
- **Auto-Renewal**: Support automatic renewal with configurable options
- **Usage Tracking**: Track services used and remaining balance
- **Expiration Handling**: Automatic expiration with renewal reminders
- **Promotional Pricing**: Support introductory pricing and discounts
- **Analytics**: Track adoption, renewal rates, and revenue impact

#### Business Context

- **Problem Solved**: Increases customer commitment and predictable recurring revenue; improves customer lifetime value
- **ROI**: Increases customer lifetime value by 50-100%; improves cash flow through upfront payments; increases customer retention by 30-40%
- **Competitive Advantage**: Membership programs build customer loyalty; predictable revenue enables better business planning

#### Integration Points

- **Appointment Booking (Req 3)**: Validate membership eligibility during booking; deduct services
- **Billing & Payment (Req 6)**: Process membership payments; handle auto-renewal
- **Customer Profiles (Req 5)**: Store membership information and usage history
- **Notifications (Req 7)**: Send renewal reminders and expiration notices
- **Performance Metrics (Req 21)**: Track membership metrics and revenue

#### Data Model Details

- **Membership**: ID (UUID), name (string), description (text), services_included (JSON array), duration_days (integer), price (decimal), renewal_price (decimal, nullable), auto_renew (boolean), max_services (integer, nullable), tenant_id (FK)
- **Package**: ID (UUID), name (string), description (text), services_included (JSON array), price (decimal), valid_days (integer), max_uses (integer, nullable), tenant_id (FK)
- **CustomerMembership**: ID (UUID), customer_id (FK), membership_id (FK), start_date (date), end_date (date), services_remaining (integer), auto_renew (boolean), renewal_date (date, nullable), status (enum: active/expired/cancelled), tenant_id (FK)
- **CustomerPackage**: ID (UUID), customer_id (FK), package_id (FK), purchase_date (date), expiration_date (date), uses_remaining (integer), status (enum: active/expired/used), tenant_id (FK)
- **MembershipAnalytics**: ID (UUID), membership_id (FK), date (date), adoption_rate (decimal), renewal_rate (decimal), revenue (decimal), active_members (integer), tenant_id (FK)

#### User Workflows

**For Owner Creating Membership:**
1. Access membership management
2. Define membership name and description
3. Select services included
4. Set duration and price
5. Configure auto-renewal options
6. Set promotional pricing (optional)
7. Publish membership

**For Customer Purchasing Membership:**
1. Browse available memberships
2. Compare features and pricing
3. Select membership
4. Complete payment
5. Membership activated immediately
6. View membership details and usage

**For Customer Using Membership:**
1. Book appointment
2. System checks membership eligibility
3. If eligible, deduct from membership balance
4. Complete appointment
5. View updated membership balance
6. Receive renewal reminder before expiration

**For Owner Managing Memberships:**
1. View active memberships and adoption rates
2. Track renewal rates and revenue
3. Identify underperforming memberships
4. Adjust pricing or features
5. Create promotional offers
6. Export membership analytics

#### Edge Cases & Constraints

- **Partial Usage**: Handle cases where customer uses partial service (e.g., cancels mid-service)
- **Membership Upgrade**: Allow customers to upgrade to higher tier; handle credit for unused services
- **Membership Downgrade**: Allow downgrade; handle refund for difference
- **Expiration**: Handle expired memberships; offer renewal options
- **Carryover**: Handle unused services; allow carryover to next period (if configured)
- **Cancellation**: Handle mid-term cancellation; calculate refunds based on usage
- **Service Restrictions**: Handle services not included in membership; prevent booking

#### Performance Requirements

- **Membership Validation**: Validate membership eligibility within 100ms
- **Service Deduction**: Deduct service from membership within 200ms
- **Renewal Processing**: Process renewal within 1 second
- **Analytics Calculation**: Calculate membership analytics within 5 seconds
- **Membership Lookup**: Look up customer membership within 50ms

#### Security Considerations

- **Payment Security**: Securely process membership payments; comply with PCI-DSS
- **Membership Integrity**: Prevent unauthorized service deductions
- **Audit Trail**: Log all membership changes and service usage
- **Refund Integrity**: Prevent unauthorized refunds

#### Compliance Requirements

- **GDPR**: Support membership data export and deletion
- **Consumer Protection**: Comply with consumer protection laws for auto-renewal
- **Tax Compliance**: Calculate and report membership revenue correctly

#### Acceptance Criteria

1. WHEN creating membership, THE System SHALL define services included, duration, and price
2. WHEN a customer purchases membership, THE System SHALL activate it and track expiration
3. WHEN a customer uses membership service, THE System SHALL deduct from available services
4. WHEN membership is expiring, THE System SHALL send renewal reminder
5. WHEN viewing membership analytics, THE System SHALL display adoption rates and revenue
6. WHEN a membership expires, THE System SHALL archive it and notify customer
7. WHEN comparing packages, THE System SHALL show value and customer adoption

#### Business Value

- Increases customer commitment and retention by 30-40%
- Provides predictable recurring revenue
- Improves customer lifetime value by 50-100%
- Simplifies pricing and billing
- Enables better business forecasting

#### Dependencies

- Appointment booking (Requirement 3)
- Billing & payment processing (Requirement 6)
- Customer profiles (Requirement 5)
- Notifications (Requirement 7)

#### Key Data Entities

- Membership (ID, name, services_included, duration_days, price, auto_renew, tenant_id)
- Package (ID, name, services_included, price, valid_days, tenant_id)
- CustomerMembership (ID, customer_id, membership_id, start_date, end_date, services_remaining, tenant_id)
- CustomerPackage (ID, customer_id, package_id, purchase_date, expiration_date, uses_remaining, tenant_id)
- MembershipAnalytics (ID, membership_id, date, adoption_rate, renewal_rate, revenue, tenant_id)

#### User Roles

- Owner: Creates and manages memberships
- Manager: Manages customer memberships
- Customer: Purchases and uses memberships

---

### Requirement 36: Email Marketing Automation

**User Story:** As a marketing manager, I want to automate email campaigns, so that I can nurture leads and maintain customer engagement.

#### Detailed Description

The email marketing automation system enables businesses to create sophisticated email campaigns that nurture customers through their lifecycle. Campaigns can be triggered by customer actions (e.g., first appointment booked, membership expiring) or scheduled for specific times. The system supports email templates with dynamic content, personalizing messages with customer names, appointment details, and personalized recommendations.

The system provides comprehensive analytics on campaign performance, tracking open rates, click rates, and conversion rates. A/B testing capabilities enable businesses to test different subject lines, content, and send times to optimize campaign effectiveness. Unsubscribe management ensures compliance with anti-spam regulations while respecting customer preferences.

Integration with customer segmentation enables highly targeted campaigns to specific customer groups. For example, a business might send a "We miss you" campaign to inactive customers while sending an upsell campaign to high-value customers. The system automatically manages unsubscribes and bounces, maintaining list hygiene and improving deliverability.

#### Technical Specifications

- **Campaign Types**: Triggered (event-based), scheduled (time-based), recurring (periodic)
- **Email Templates**: Support HTML templates with dynamic variable substitution
- **Personalization**: Support customer name, appointment details, personalized recommendations
- **A/B Testing**: Test subject lines, content, and send times; recommend best performer
- **Segmentation**: Target campaigns to specific customer segments
- **Scheduling**: Schedule campaigns for optimal send times
- **Analytics**: Track open rates, click rates, conversions, and ROI
- **Unsubscribe Management**: Respect customer preferences; maintain compliance

#### Business Context

- **Problem Solved**: Automates customer nurturing; increases engagement without manual effort
- **ROI**: Increases customer engagement by 50-100%; drives repeat bookings; improves customer lifetime value by 20-30%
- **Competitive Advantage**: Automated campaigns enable consistent communication; personalization improves customer experience

#### Integration Points

- **Customer Profiles (Req 5)**: Use customer data for personalization and targeting
- **Customer Segmentation (Req 33)**: Target campaigns to specific segments
- **Email Provider (Req 49)**: Send emails through reliable provider
- **Notifications (Req 7)**: Integrate with notification system
- **Performance Metrics (Req 21)**: Track campaign performance

#### Data Model Details

- **EmailCampaign**: ID (UUID), name (string), type (enum: triggered/scheduled/recurring), template_id (FK), segment_id (FK, nullable), subject (string), trigger_event (string, nullable), scheduled_time (timestamp, nullable), status (enum: draft/active/paused/completed), created_at (timestamp), tenant_id (FK)
- **EmailTemplate**: ID (UUID), name (string), subject (string), body (text), variables (JSON array), created_at (timestamp), tenant_id (FK)
- **EmailMetrics**: ID (UUID), campaign_id (FK), sent_count (integer), delivered_count (integer), open_count (integer), click_count (integer), conversion_count (integer), bounce_count (integer), unsubscribe_count (integer), tenant_id (FK)
- **EmailUnsubscribe**: ID (UUID), customer_id (FK), campaign_id (FK, nullable), unsubscribe_date (timestamp), reason (string, nullable), tenant_id (FK)
- **ABTest**: ID (UUID), campaign_id (FK), variant_a_subject (string), variant_b_subject (string), winner (enum: a/b/tie), tenant_id (FK)

#### User Workflows

**For Marketing Manager Creating Campaign:**
1. Access email campaign builder
2. Select campaign type (triggered/scheduled/recurring)
3. Choose email template or create new
4. Personalize subject and content
5. Select target segment
6. Configure trigger or schedule
7. Set up A/B test (optional)
8. Review and launch campaign

**For System Executing Campaign:**
1. Monitor for trigger events or scheduled time
2. Query target segment members
3. Render email with personalization
4. Send through email provider
5. Track delivery and engagement
6. Update metrics in real-time

**For Marketing Manager Analyzing Campaign:**
1. View campaign performance dashboard
2. See open rates, click rates, conversions
3. Compare A/B test variants
4. Identify top-performing content
5. Export detailed engagement reports
6. Optimize future campaigns

#### Edge Cases & Constraints

- **Unsubscribed Customers**: Exclude unsubscribed customers from campaigns
- **Bounced Emails**: Track bounced emails; disable future sends to invalid addresses
- **Personalization Failures**: Handle missing variables gracefully; use defaults
- **Timezone Issues**: Send campaigns in customer's local timezone
- **Rate Limiting**: Respect email provider rate limits; queue campaigns
- **Duplicate Sends**: Prevent duplicate sends through idempotency checks
- **Compliance**: Ensure compliance with CAN-SPAM and GDPR

#### Performance Requirements

- **Campaign Launch**: Launch campaign within 1 second
- **Email Rendering**: Render email with personalization within 500ms
- **Email Sending**: Send email within 2 seconds of trigger
- **Metrics Update**: Update metrics within 5 seconds
- **Analytics Calculation**: Calculate campaign analytics within 10 seconds

#### Security Considerations

- **Email Content**: Validate email content to prevent injection attacks
- **Unsubscribe Links**: Include valid unsubscribe links in all emails
- **Authentication**: Verify sender identity; use SPF, DKIM, DMARC
- **Audit Trail**: Log all campaign sends and engagement events
- **Data Privacy**: Protect customer email addresses and engagement data

#### Compliance Requirements

- **CAN-SPAM**: Include business address and unsubscribe link in all emails
- **GDPR**: Obtain consent before sending marketing emails; provide unsubscribe option
- **CASL**: Comply with Canadian anti-spam legislation
- **Email Authentication**: Implement SPF, DKIM, DMARC for sender authentication

#### Acceptance Criteria

1. WHEN creating email campaign, THE System SHALL allow designing template and scheduling
2. WHEN campaign is scheduled, THE System SHALL send to selected segments at specified time
3. WHEN tracking campaign, THE System SHALL measure open rates, click rates, and conversions
4. WHEN a customer unsubscribes, THE System SHALL respect preference and remove from future campaigns
5. WHEN analyzing campaigns, THE System SHALL display performance metrics and ROI
6. WHEN A/B testing, THE System SHALL compare campaign variants and recommend best performer
7. WHEN exporting campaign data, THE System SHALL provide detailed engagement reports

#### Business Value

- Increases customer engagement by 50-100%
- Drives repeat bookings through targeted campaigns
- Improves marketing ROI through automation
- Reduces manual marketing work
- Enables data-driven campaign optimization

#### Dependencies

- Customer profiles (Requirement 5)
- Customer segmentation (Requirement 33)
- Email provider integration (Requirement 49)
- Notifications (Requirement 7)

#### Key Data Entities

- EmailCampaign (ID, name, type, template_id, segment_id, status, tenant_id)
- EmailTemplate (ID, name, subject, body, variables, tenant_id)
- EmailMetrics (ID, campaign_id, sent_count, open_count, click_count, conversion_count, tenant_id)
- EmailUnsubscribe (ID, customer_id, campaign_id, unsubscribe_date, tenant_id)
- ABTest (ID, campaign_id, variant_a_subject, variant_b_subject, winner, tenant_id)

#### User Roles

- Marketing Manager: Creates and manages campaigns
- Owner: Views campaign analytics
- System: Executes campaigns and tracks metrics

---

### Requirement 37: Social Media Integration

**User Story:** As a marketing manager, I want to integrate with social media, so that I can expand reach and engage customers on their preferred platforms.

#### Detailed Description

The social media integration system enables businesses to manage their social media presence directly from the platform. Businesses can connect their Facebook, Instagram, and other social media accounts, then schedule and publish posts directly to these platforms. The system supports multi-platform publishing, allowing businesses to post to multiple platforms simultaneously with platform-specific formatting.

The system tracks social media engagement, capturing likes, shares, comments, and mentions. When customers mention the business on social media, the system captures these mentions and alerts the business owner. Analytics provide insights into social media performance, showing which posts drive the most engagement and which platforms are most effective.

Integration with appointment booking enables tracking of social media-driven bookings. When customers click through from social media to book appointments, the system tracks the source, enabling measurement of social media ROI. The system supports social listening, monitoring mentions and hashtags to identify customer sentiment and opportunities for engagement.

#### Technical Specifications

- **Platform Support**: Facebook, Instagram, Twitter, LinkedIn, TikTok
- **Multi-Platform Publishing**: Schedule and publish to multiple platforms simultaneously
- **Content Scheduling**: Schedule posts for optimal engagement times
- **Engagement Tracking**: Capture likes, shares, comments, mentions
- **Social Listening**: Monitor mentions and hashtags
- **Analytics**: Track engagement metrics and ROI
- **Sentiment Analysis**: Analyze customer sentiment in comments and mentions
- **Integration**: Track social media-driven bookings and conversions

#### Business Context

- **Problem Solved**: Expands marketing reach; enables engagement on customer-preferred platforms
- **ROI**: Increases brand awareness by 50-100%; drives bookings through social media; improves customer engagement
- **Competitive Advantage**: Social media presence builds brand credibility; enables direct customer engagement

#### Integration Points

- **Customer Profiles (Req 5)**: Track customer social media interactions
- **Appointment Booking (Req 3)**: Track social media-driven bookings
- **Notifications (Req 7)**: Alert business of mentions and engagement
- **Performance Metrics (Req 21)**: Track social media metrics and ROI
- **Social Media Platform APIs**: Connect to Facebook, Instagram, etc.

#### Data Model Details

- **SocialMediaAccount**: ID (UUID), tenant_id (FK), platform (enum: facebook/instagram/twitter/linkedin/tiktok), account_id (string), access_token (string), refresh_token (string, nullable), followers_count (integer), connected_at (timestamp), enabled (boolean)
- **SocialPost**: ID (UUID), account_id (FK), content (text), media_urls (JSON array), scheduled_time (timestamp, nullable), published_time (timestamp, nullable), platform_post_id (string, nullable), status (enum: draft/scheduled/published), tenant_id (FK)
- **SocialMetrics**: ID (UUID), post_id (FK), likes (integer), shares (integer), comments (integer), clicks (integer), conversions (integer), reach (integer), impressions (integer), tenant_id (FK)
- **SocialMention**: ID (UUID), account_id (FK), platform (enum), mention_text (text), mentioned_by (string), mentioned_at (timestamp), sentiment (enum: positive/neutral/negative), tenant_id (FK)
- **SocialAnalytics**: ID (UUID), account_id (FK), date (date), total_engagement (integer), reach (integer), impressions (integer), follower_growth (integer), tenant_id (FK)

#### User Workflows

**For Marketing Manager Connecting Account:**
1. Access social media settings
2. Select platform to connect
3. Authenticate with platform
4. Grant permissions
5. Account connected and synced
6. View follower count and account info

**For Marketing Manager Publishing Post:**
1. Create new post
2. Write content and add media
3. Select platforms to publish to
4. Schedule or publish immediately
5. System publishes to all selected platforms
6. Track engagement in real-time

**For Business Owner Monitoring Social Media:**
1. View social media dashboard
2. See recent posts and engagement
3. View mentions and comments
4. Respond to comments and mentions
5. Analyze engagement metrics
6. Identify top-performing content

#### Edge Cases & Constraints

- **Platform Differences**: Handle platform-specific formatting and character limits
- **Media Optimization**: Optimize images for each platform
- **Scheduling**: Handle timezone differences for optimal posting times
- **Rate Limiting**: Respect platform rate limits; queue posts
- **Account Disconnection**: Handle expired tokens; prompt for re-authentication
- **Deleted Posts**: Handle posts deleted on platform; update status
- **Spam Detection**: Detect and filter spam comments and mentions

#### Performance Requirements

- **Post Publishing**: Publish to all platforms within 2 seconds
- **Engagement Tracking**: Update engagement metrics within 5 seconds
- **Mention Detection**: Detect mentions within 1 minute
- **Analytics Calculation**: Calculate social analytics within 10 seconds
- **Account Sync**: Sync account data within 5 minutes

#### Security Considerations

- **Token Security**: Securely store access tokens; encrypt at rest
- **Token Refresh**: Automatically refresh tokens before expiration
- **Audit Trail**: Log all social media posts and engagement
- **Content Moderation**: Moderate comments and mentions for inappropriate content
- **Account Access**: Restrict social media account access to authorized users

#### Compliance Requirements

- **Platform Terms**: Comply with platform terms of service
- **Advertising**: Comply with platform advertising policies
- **Privacy**: Respect customer privacy in social media interactions
- **Data Protection**: Comply with GDPR and other data protection regulations

#### Acceptance Criteria

1. WHEN connecting social media account, THE System SHALL authenticate and sync followers
2. WHEN posting to social media, THE System SHALL allow scheduling and multi-platform publishing
3. WHEN tracking social engagement, THE System SHALL measure likes, shares, and comments
4. WHEN a customer mentions business on social media, THE System SHALL capture mention
5. WHEN analyzing social performance, THE System SHALL display engagement metrics by platform
6. WHEN running social campaigns, THE System SHALL track clicks and conversions to bookings
7. WHEN exporting social data, THE System SHALL provide engagement reports

#### Business Value

- Expands marketing reach through social media
- Increases brand awareness by 50-100%
- Drives customer engagement on preferred platforms
- Enables social listening and sentiment analysis
- Tracks social media ROI

#### Dependencies

- Customer profiles (Requirement 5)
- Appointment booking (Requirement 3)
- Social media platform APIs

#### Key Data Entities

- SocialMediaAccount (ID, tenant_id, platform, account_id, access_token, followers_count, tenant_id)
- SocialPost (ID, account_id, content, scheduled_time, published_time, status, tenant_id)
- SocialMetrics (ID, post_id, likes, shares, comments, clicks, conversions, tenant_id)
- SocialMention (ID, account_id, mention_text, mentioned_by, sentiment, tenant_id)
- SocialAnalytics (ID, account_id, date, total_engagement, reach, impressions, tenant_id)

#### User Roles

- Marketing Manager: Posts to social media
- Owner: Views social analytics
- System: Tracks engagement

---

### Requirement 38: Review Management (Google, Yelp, etc.)

**User Story:** As a business owner, I want to manage online reviews, so that I can maintain reputation and respond to customer feedback.

#### Detailed Description

The review management system aggregates customer reviews from multiple platforms (Google, Yelp, Facebook, TripAdvisor) into a centralized dashboard, enabling businesses to monitor their online reputation in real-time. The system automatically captures new reviews as they're posted, notifies business owners, and tracks review metrics including average rating, review count, and sentiment trends. This centralized approach eliminates the need to check multiple platforms manually.

The system enables businesses to respond to reviews directly from the platform, with responses automatically posted to the original review platform. Managers can draft responses, have them approved by owners, and track response times. The system analyzes review content using natural language processing to identify common themes, issues, and sentiment patterns, providing actionable insights for service improvement.

Review request automation sends targeted requests to customers post-appointment, encouraging satisfied customers to leave reviews while capturing feedback from dissatisfied customers before they post negative reviews. The system tracks review request effectiveness, measuring response rates and conversion to actual reviews. Analytics identify which customer segments are most likely to leave reviews, enabling targeted request campaigns.

#### Technical Specifications

- **Multi-Platform Integration**: Integrate with Google, Yelp, Facebook, TripAdvisor APIs
- **Real-Time Capture**: Capture reviews within 5 minutes of posting
- **Sentiment Analysis**: Use NLP to analyze review sentiment (positive/negative/neutral)
- **Theme Extraction**: Identify common themes and topics in reviews
- **Response Management**: Draft, approve, and post responses to reviews
- **Review Requests**: Send automated requests post-appointment
- **Reputation Scoring**: Calculate reputation score based on ratings and sentiment
- **Competitor Benchmarking**: Compare metrics to competitor averages

#### Business Context

- **Problem Solved**: Enables proactive reputation management; identifies service issues early
- **ROI**: Improves online reputation by 25-30%; increases customer trust and bookings
- **Competitive Advantage**: Proactive reputation management differentiates from competitors; improves search rankings

#### Integration Points

- **Appointment Booking (Req 3)**: Trigger review requests upon appointment completion
- **Notifications (Req 7)**: Notify owner of new reviews and send review requests
- **Customer Profiles (Req 5)**: Track customer review history and preferences
- **Performance Metrics (Req 21)**: Track review metrics and reputation trends

#### Data Model Details

- **Review**: ID (UUID), platform (enum: google/yelp/facebook/tripadvisor), reviewer_name (string), reviewer_id (string, platform-specific), rating (integer 1-5), title (string), content (text), posted_date (timestamp), platform_url (string), sentiment (enum: positive/negative/neutral), sentiment_score (decimal -1 to 1), themes (JSON array), tenant_id (FK)
- **ReviewResponse**: ID (UUID), review_id (FK), response_text (text), drafted_by (FK), approved_by (FK), posted_by (FK), drafted_at (timestamp), approved_at (timestamp, nullable), posted_at (timestamp, nullable), status (enum: draft/approved/posted/rejected), platform_response_id (string, nullable), tenant_id (FK)
- **ReviewRequest**: ID (UUID), appointment_id (FK), customer_id (FK), sent_at (timestamp), response_received_at (timestamp, nullable), review_posted (boolean), review_id (FK, nullable), tenant_id (FK)
- **ReviewAnalytics**: ID (UUID), date (date), platform (enum), average_rating (decimal), review_count (integer), positive_count (integer), negative_count (integer), neutral_count (integer), average_sentiment_score (decimal), response_rate (decimal), response_time_hours (decimal), tenant_id (FK)
- **ReputationScore**: ID (UUID), date (date), overall_score (decimal 0-100), platform_scores (JSON), trend (enum: improving/stable/declining), competitor_comparison (decimal), tenant_id (FK)

#### User Workflows

**For Owner Monitoring Reputation:**
1. Log into dashboard
2. View reputation score and trends
3. See new reviews across all platforms
4. View sentiment analysis and themes
5. Identify service improvement opportunities
6. Track response rate and effectiveness

**For Manager Responding to Reviews:**
1. Receive notification of new review
2. Read review and understand customer feedback
3. Draft response addressing concerns
4. Submit for owner approval
5. Owner approves or requests changes
6. Response posted to platform
7. Track response effectiveness

**For System Requesting Reviews:**
1. Appointment completed
2. Calculate customer satisfaction (based on no-show, cancellation history)
3. Send review request to satisfied customers
4. Track request delivery and response
5. Capture posted reviews
6. Update review metrics

**For Manager Analyzing Reviews:**
1. View review analytics dashboard
2. Filter by platform, date range, rating
3. Analyze sentiment trends
4. Identify common themes and issues
5. Compare to competitor benchmarks
6. Generate improvement recommendations

#### Edge Cases & Constraints

- **Platform API Limits**: Handle rate limiting from review platforms; implement backoff strategy
- **Review Moderation**: Handle fake or spam reviews; flag for manual review
- **Response Approval**: Require approval before posting responses to prevent inappropriate responses
- **Duplicate Reviews**: Detect and handle duplicate reviews from same customer
- **Review Deletion**: Handle reviews deleted by customers or platforms
- **Language Support**: Support reviews in multiple languages; translate for analysis
- **Sentiment Accuracy**: Handle sarcasm and context-dependent sentiment (e.g., "Great service, terrible experience")
- **Review Request Timing**: Don't send requests too frequently; respect customer preferences

#### Performance Requirements

- **Review Capture**: Capture new reviews within 5 minutes of posting
- **Sentiment Analysis**: Analyze sentiment within 1 second
- **Response Posting**: Post response to platform within 2 seconds
- **Analytics Calculation**: Calculate reputation score within 5 seconds
- **Dashboard Load**: Load reputation dashboard within 2 seconds

#### Security Considerations

- **API Credentials**: Store review platform API credentials securely; rotate regularly
- **Response Approval**: Require approval before posting to prevent unauthorized responses
- **Audit Trail**: Log all responses and approvals for compliance
- **Customer Privacy**: Don't display customer personal information in public responses

#### Compliance Requirements

- **Review Authenticity**: Comply with platform policies on review authenticity
- **Response Guidelines**: Follow platform guidelines for response content
- **GDPR**: Respect customer privacy when displaying reviews
- **Defamation**: Ensure responses don't contain defamatory content

#### Acceptance Criteria

1. WHEN a review is posted on Google or Yelp, THE System SHALL capture it and notify owner within 5 minutes
2. WHEN responding to review, THE System SHALL allow composing response and require approval before posting
3. WHEN viewing reviews, THE System SHALL display all reviews with ratings, sentiment, and themes
4. WHEN analyzing reviews, THE System SHALL identify common themes and sentiment trends
5. WHEN tracking review metrics, THE System SHALL display average rating, review count, and reputation score
6. WHEN requesting reviews, THE System SHALL send automated requests to customers post-appointment
7. WHEN exporting review data, THE System SHALL provide sentiment analysis, themes, and trends

#### Business Value

- Maintains and improves online reputation
- Improves search rankings through positive reviews
- Increases customer trust and bookings
- Identifies service improvement opportunities
- Enables proactive reputation management

#### Dependencies

- Customer profiles (Requirement 5)
- Appointment booking (Requirement 3)
- Notifications (Requirement 7)
- Review platform APIs (Google, Yelp, Facebook, TripAdvisor)

#### Key Data Entities

- Review (ID, platform, reviewer_name, rating, content, posted_date, sentiment, themes, tenant_id)
- ReviewResponse (ID, review_id, response_text, status, posted_at, tenant_id)
- ReviewRequest (ID, appointment_id, customer_id, sent_at, review_posted, tenant_id)
- ReviewAnalytics (ID, date, average_rating, review_count, sentiment_score, tenant_id)
- ReputationScore (ID, date, overall_score, trend, tenant_id)

#### User Roles

- Owner: Monitors reputation and approves responses
- Manager: Responds to reviews and requests reviews
- System: Captures reviews and sends requests

---

### Requirement 39: Referral Tracking & Rewards

**User Story:** As a business owner, I want to track referral rewards, so that I can measure program effectiveness and incentivize participation.

#### Detailed Description

The referral tracking system enables businesses to create and manage referral programs that incentivize customers to refer friends and family. When a referred customer books their first appointment, the system automatically credits the referrer with a reward. Rewards can be configured as discounts, store credit, or cash bonuses, enabling businesses to choose incentive structures that align with their business model.

The system tracks the complete referral lifecycle from referral link generation through reward redemption. Customers can share unique referral links via email, SMS, or social media, with the system tracking which channel drove the most referrals. Analytics measure program effectiveness including referral conversion rates, average customer lifetime value of referred customers, and program ROI.

The system supports tiered reward structures where customers earn increasing rewards for multiple successful referrals, encouraging ongoing participation. Managers can configure reward rules, set limits on reward spending, and track program performance in real-time. The system prevents fraud through validation checks and duplicate detection.

#### Technical Specifications

- **Referral Link Generation**: Generate unique referral links per customer
- **Referral Tracking**: Track referral source and conversion
- **Reward Calculation**: Automatically calculate rewards based on program rules
- **Tiered Rewards**: Support multiple reward tiers based on referral count
- **Reward Types**: Support discounts, store credit, cash bonuses
- **Fraud Detection**: Detect and prevent fraudulent referrals
- **Sharing Channels**: Track referrals by channel (email, SMS, social media)
- **Program Analytics**: Track conversion rates, ROI, and customer lifetime value

#### Business Context

- **Problem Solved**: Drives customer acquisition through word-of-mouth; leverages existing customer base
- **ROI**: Reduces customer acquisition cost by 40-50%; referred customers have 25% higher lifetime value
- **Competitive Advantage**: Referral programs build community and increase customer loyalty

#### Integration Points

- **Customer Profiles (Req 5)**: Track referrer and referred customer relationship
- **Appointment Booking (Req 3)**: Trigger reward when referred customer books
- **Billing & Payment (Req 6)**: Apply rewards as discounts or credits
- **Notifications (Req 7)**: Notify referrer of successful referral and reward

#### Data Model Details

- **ReferralProgram**: ID (UUID), tenant_id (FK), name (string), description (text), status (enum: active/inactive), created_at (timestamp), updated_at (timestamp)
- **ReferralRule**: ID (UUID), program_id (FK), referral_count (integer), reward_type (enum: discount/credit/cash), reward_amount (decimal), reward_percentage (decimal, nullable), max_reward_per_customer (decimal, nullable), effective_from (date), effective_to (date, nullable), tenant_id (FK)
- **ReferralLink**: ID (UUID), customer_id (FK), program_id (FK), unique_code (string, unique), created_at (timestamp), expires_at (date, nullable), click_count (integer), conversion_count (integer), tenant_id (FK)
- **Referral**: ID (UUID), referrer_id (FK), referred_customer_id (FK), program_id (FK), referral_link_id (FK), status (enum: pending/converted/expired), referred_at (timestamp), converted_at (timestamp, nullable), first_appointment_id (FK, nullable), tenant_id (FK)
- **ReferralReward**: ID (UUID), referral_id (FK), reward_type (enum: discount/credit/cash), reward_amount (decimal), earned_at (timestamp), redeemed_at (timestamp, nullable), redeemed_on_appointment_id (FK, nullable), status (enum: earned/redeemed/expired), tenant_id (FK)
- **ReferralAnalytics**: ID (UUID), date (date), program_id (FK), total_referrals (integer), converted_referrals (integer), conversion_rate (decimal), total_rewards_earned (decimal), total_rewards_redeemed (decimal), program_roi (decimal), average_referred_customer_ltv (decimal), tenant_id (FK)

#### User Workflows

**For Owner Creating Referral Program:**
1. Access referral program settings
2. Define program name and description
3. Set reward rules (tiers, amounts, types)
4. Set program duration and limits
5. Configure sharing channels
6. Enable program
7. Share program details with customers

**For Customer Participating in Referral:**
1. Log into customer portal
2. View referral program details
3. Generate unique referral link
4. Share link via email, SMS, or social media
5. Track referral status and rewards
6. Redeem earned rewards on future appointments

**For System Processing Referral:**
1. Customer clicks referral link
2. System tracks referral source
3. Referred customer books first appointment
4. System validates referral (not duplicate, not expired)
5. Calculate reward based on rules
6. Credit referrer with reward
7. Notify referrer of successful referral

**For Manager Analyzing Program:**
1. View referral program dashboard
2. Track total referrals and conversions
3. Analyze conversion rates by channel
4. View rewards earned and redeemed
5. Calculate program ROI
6. Compare referred customer LTV to regular customers
7. Identify top referrers

#### Edge Cases & Constraints

- **Duplicate Referrals**: Prevent same customer from being referred multiple times
- **Self-Referrals**: Prevent customers from referring themselves
- **Reward Limits**: Enforce maximum rewards per customer or per program
- **Expiration**: Handle expired referral links and rewards
- **Fraud Detection**: Detect suspicious referral patterns (e.g., multiple referrals from same IP)
- **Reward Redemption**: Handle partial reward redemption and multiple redemptions
- **Program Changes**: Handle changes to reward rules; apply to future referrals only
- **Referred Customer Churn**: Handle case where referred customer churns before reward redemption

#### Performance Requirements

- **Link Generation**: Generate referral link within 100ms
- **Referral Tracking**: Track referral click within 500ms
- **Reward Calculation**: Calculate reward within 1 second
- **Analytics Calculation**: Calculate analytics within 5 seconds
- **Conversion Detection**: Detect conversion within 1 minute of first appointment booking

#### Security Considerations

- **Link Security**: Use cryptographically secure random codes for referral links
- **Fraud Detection**: Implement checks to detect fraudulent referrals
- **Audit Trail**: Log all referrals and rewards for compliance
- **Customer Privacy**: Don't expose customer information in referral links

#### Compliance Requirements

- **Consumer Protection**: Comply with consumer protection laws regarding referral programs
- **Tax Reporting**: Track referral rewards for tax purposes
- **Disclosure**: Clearly disclose program terms and conditions

#### Acceptance Criteria

1. WHEN a referral is completed, THE System SHALL calculate reward amount based on program rules
2. WHEN reward is earned, THE System SHALL credit customer account or send reward
3. WHEN tracking rewards, THE System SHALL display earned and redeemed rewards
4. WHEN analyzing program, THE System SHALL calculate ROI and customer acquisition cost
5. WHEN a customer redeems reward, THE System SHALL apply to their account
6. WHEN exporting reward data, THE System SHALL show top earners and program performance
7. WHEN updating reward rules, THE System SHALL apply to future referrals only

#### Business Value

- Drives customer acquisition through word-of-mouth
- Increases program participation through tiered rewards
- Measures marketing effectiveness
- Builds customer loyalty and community
- Reduces customer acquisition costs

#### Dependencies

- Customer profiles (Requirement 5)
- Appointment booking (Requirement 3)
- Billing & payment processing (Requirement 6)
- Notifications (Requirement 7)

#### Key Data Entities

- ReferralProgram (ID, tenant_id, name, status, created_at)
- ReferralRule (ID, program_id, referral_count, reward_type, reward_amount, tenant_id)
- ReferralLink (ID, customer_id, program_id, unique_code, created_at, tenant_id)
- Referral (ID, referrer_id, referred_customer_id, program_id, status, tenant_id)
- ReferralReward (ID, referral_id, reward_type, reward_amount, status, tenant_id)
- ReferralAnalytics (ID, date, program_id, conversion_rate, program_roi, tenant_id)

#### User Roles

- Owner: Manages referral program
- Customer: Participates in referral program
- Manager: Tracks program performance
- System: Processes referrals and calculates rewards

---

### Requirement 40: Seasonal Promotions

**User Story:** As a marketing manager, I want to create seasonal promotions, so that I can capitalize on seasonal demand and drive revenue.

#### Detailed Description

The seasonal promotions system enables businesses to create time-limited promotions that capitalize on seasonal demand patterns. Managers can define promotions with specific dates, eligible services, discount amounts, and promotional messaging. The system automatically activates promotions on the start date and deactivates them on the end date, with notifications sent to customers about available promotions.

When customers book during a promotion period, the system automatically applies the discount to their invoice. The system tracks promotion performance including bookings, revenue, and discount amount, enabling businesses to measure promotion effectiveness. Analytics identify seasonal trends and patterns, providing recommendations for future promotions.

The system supports complex promotion rules including service-specific discounts, customer segment targeting, and minimum purchase requirements. Managers can create promotions for specific customer groups (new customers, loyal customers, etc.) to maximize effectiveness. The system prevents promotion stacking where multiple promotions could be applied to a single booking.

#### Technical Specifications

- **Promotion Definition**: Define dates, services, discount type (percentage/fixed), and messaging
- **Automatic Activation**: Activate promotions on start date; deactivate on end date
- **Discount Application**: Automatically apply discount during booking
- **Customer Targeting**: Target promotions to specific customer segments
- **Promotion Rules**: Support complex rules (minimum purchase, service combinations, etc.)
- **Promotion Stacking**: Prevent multiple promotions on single booking
- **Performance Tracking**: Track bookings, revenue, and discount amount
- **Seasonal Analytics**: Identify trends and provide recommendations

#### Business Context

- **Problem Solved**: Capitalizes on seasonal demand; drives revenue during peak periods
- **ROI**: Increases bookings by 20-30% during promotion periods; improves revenue during slow seasons
- **Competitive Advantage**: Strategic promotions attract price-sensitive customers and build loyalty

#### Integration Points

- **Appointment Booking (Req 3)**: Apply promotions during booking
- **Billing & Payment (Req 6)**: Calculate discounted price
- **Notifications (Req 7)**: Notify customers about promotions
- **Performance Metrics (Req 21)**: Track promotion performance

#### Data Model Details

- **SeasonalPromotion**: ID (UUID), tenant_id (FK), name (string), description (text), start_date (date), end_date (date), status (enum: draft/active/inactive/archived), created_at (timestamp), updated_at (timestamp)
- **PromotionRule**: ID (UUID), promotion_id (FK), discount_type (enum: percentage/fixed), discount_value (decimal), min_purchase_amount (decimal, nullable), max_discount_amount (decimal, nullable), applicable_services (JSON array of service IDs), target_customer_segment (enum: all/new/loyal/inactive), tenant_id (FK)
- **PromotionCode**: ID (UUID), promotion_id (FK), code (string, unique), usage_limit (integer, nullable), current_usage (integer), created_at (timestamp), expires_at (date, nullable), tenant_id (FK)
- **PromotionApplication**: ID (UUID), appointment_id (FK), promotion_id (FK), discount_amount (decimal), original_price (decimal), discounted_price (decimal), applied_at (timestamp), tenant_id (FK)
- **SeasonalAnalytics**: ID (UUID), promotion_id (FK), date (date), bookings (integer), revenue (decimal), discount_amount (decimal), roi (decimal), customer_acquisition_cost (decimal), tenant_id (FK)
- **SeasonalTrend**: ID (UUID), tenant_id (FK), season (enum: spring/summer/fall/winter), year (integer), average_bookings (integer), average_revenue (decimal), recommended_promotion_discount (decimal), tenant_id (FK)

#### User Workflows

**For Marketing Manager Creating Promotion:**
1. Access seasonal promotions interface
2. Define promotion name and description
3. Set start and end dates
4. Select eligible services
5. Set discount type and amount
6. Target customer segments (optional)
7. Set promotion rules (minimum purchase, etc.)
8. Create promotional codes (optional)
9. Preview promotion messaging
10. Activate promotion

**For System Applying Promotion:**
1. Customer initiates booking
2. Check active promotions for eligible services
3. Check customer segment eligibility
4. Check minimum purchase requirements
5. Calculate discount amount
6. Apply discount to booking
7. Display discounted price to customer
8. Track promotion application

**For Manager Analyzing Promotion:**
1. View promotion dashboard
2. Select promotion to analyze
3. View bookings and revenue during promotion
4. Compare to baseline (non-promotion period)
5. Calculate ROI and customer acquisition cost
6. Identify top-performing services
7. View customer segment performance
8. Generate recommendations for future promotions

**For System Identifying Seasonal Trends:**
1. Analyze historical booking and revenue data
2. Identify seasonal patterns (peak/low seasons)
3. Calculate average metrics by season
4. Recommend promotion timing and discount levels
5. Suggest target customer segments
6. Provide ROI projections

#### Edge Cases & Constraints

- **Promotion Overlap**: Handle overlapping promotions; apply highest discount
- **Promotion Stacking**: Prevent multiple promotions on single booking
- **Expired Promotions**: Automatically deactivate expired promotions
- **Promotion Code Limits**: Enforce usage limits on promotional codes
- **Minimum Purchase**: Validate minimum purchase requirements before applying discount
- **Service Eligibility**: Validate service eligibility before applying discount
- **Customer Segment**: Validate customer segment eligibility
- **Discount Limits**: Enforce maximum discount amount per booking

#### Performance Requirements

- **Promotion Activation**: Activate promotion within 1 minute of start date
- **Discount Calculation**: Calculate discount within 100ms
- **Promotion Application**: Apply promotion during booking within 500ms
- **Analytics Calculation**: Calculate promotion analytics within 5 seconds
- **Trend Analysis**: Analyze seasonal trends within 10 seconds

#### Security Considerations

- **Promotion Code Security**: Use cryptographically secure codes
- **Fraud Detection**: Detect suspicious promotion usage patterns
- **Audit Trail**: Log all promotion applications and changes
- **Authorization**: Restrict promotion creation to authorized managers

#### Compliance Requirements

- **Consumer Protection**: Comply with consumer protection laws regarding promotions
- **Disclosure**: Clearly disclose promotion terms and conditions
- **Tax Reporting**: Track promotion discounts for tax purposes

#### Acceptance Criteria

1. WHEN creating seasonal promotion, THE System SHALL define dates, services, and discount
2. WHEN promotion period starts, THE System SHALL activate promotion and notify customers
3. WHEN customers book during promotion, THE System SHALL apply discount automatically
4. WHEN tracking promotion, THE System SHALL measure bookings and revenue impact
5. WHEN promotion ends, THE System SHALL deactivate and archive
6. WHEN analyzing seasonal trends, THE System SHALL identify peak periods and opportunities
7. WHEN planning next season, THE System SHALL provide recommendations based on historical data

#### Business Value

- Capitalizes on seasonal demand
- Drives revenue during peak periods
- Increases bookings during slow seasons
- Improves customer engagement
- Enables data-driven planning

#### Dependencies

- Appointment booking (Requirement 3)
- Billing & payment processing (Requirement 6)
- Notifications (Requirement 7)
- Performance metrics (Requirement 21)

#### Key Data Entities

- SeasonalPromotion (ID, tenant_id, name, start_date, end_date, status, created_at)
- PromotionRule (ID, promotion_id, discount_type, discount_value, applicable_services, tenant_id)
- PromotionCode (ID, promotion_id, code, usage_limit, created_at, tenant_id)
- PromotionApplication (ID, appointment_id, promotion_id, discount_amount, applied_at, tenant_id)
- SeasonalAnalytics (ID, promotion_id, date, bookings, revenue, discount_amount, roi, tenant_id)
- SeasonalTrend (ID, tenant_id, season, year, average_bookings, average_revenue, tenant_id)

#### User Roles

- Marketing Manager: Creates and manages promotions
- Owner: Views seasonal analytics
- System: Applies promotions and tracks performance

---

### Requirement 41: Customer Retention Analytics

**User Story:** As a business owner, I want to analyze customer retention, so that I can identify at-risk customers and improve retention strategies.

#### Detailed Description

The customer retention analytics system tracks customer engagement patterns and identifies at-risk customers who may churn. The system calculates retention rates by cohort (customers acquired in same period) and time period, enabling businesses to measure retention effectiveness. Cohort analysis reveals how retention changes over time, identifying which customer acquisition periods produced the most loyal customers.

The system identifies at-risk customers through behavioral analysis, flagging customers with declining activity (fewer bookings, longer time between bookings) or negative signals (cancellations, no-shows). Managers receive alerts about at-risk customers, enabling proactive retention campaigns. The system tracks churn reasons through exit surveys and customer feedback, identifying patterns and improvement opportunities.

Analytics measure the impact of retention efforts on customer lifetime value, enabling businesses to optimize retention spending. The system provides retention benchmarks comparing the business to industry averages, identifying competitive positioning. Predictive models forecast future churn, enabling proactive intervention before customers leave.

#### Technical Specifications

- **Cohort Analysis**: Calculate retention by customer acquisition cohort
- **Retention Metrics**: Calculate retention rate, churn rate, and customer lifetime value
- **At-Risk Detection**: Identify at-risk customers through behavioral analysis
- **Churn Prediction**: Predict which customers are likely to churn
- **Churn Reasons**: Track and analyze reasons for churn
- **Retention Campaigns**: Track impact of retention campaigns on churn
- **Benchmarking**: Compare metrics to industry benchmarks
- **Forecasting**: Project future retention and revenue impact

#### Business Context

- **Problem Solved**: Identifies at-risk customers early; enables targeted retention campaigns
- **ROI**: Improves retention by 10-15%; increases customer lifetime value by 20-30%
- **Competitive Advantage**: Proactive retention reduces customer loss and improves profitability

#### Integration Points

- **Customer Profiles (Req 5)**: Track customer engagement and behavior
- **Appointment Booking (Req 3)**: Track booking patterns and frequency
- **Performance Metrics (Req 21)**: Track retention metrics
- **Customer Segmentation (Req 33)**: Segment customers for targeted campaigns
- **Automated Marketing (Req 59)**: Execute retention campaigns

#### Data Model Details

- **RetentionCohort**: ID (UUID), tenant_id (FK), cohort_date (date), initial_customers (integer), month_0_retained (integer), month_1_retained (integer), month_3_retained (integer), month_6_retained (integer), month_12_retained (integer), retention_rate_month_1 (decimal), retention_rate_month_3 (decimal), retention_rate_month_6 (decimal), retention_rate_month_12 (decimal)
- **CustomerEngagement**: ID (UUID), customer_id (FK), date (date), bookings_count (integer), revenue (decimal), days_since_last_booking (integer), cancellation_count (integer), no_show_count (integer), engagement_score (decimal 0-100), at_risk_flag (boolean), at_risk_reason (enum: no_recent_bookings/declining_frequency/cancellations/no_shows), tenant_id (FK)
- **ChurnAnalysis**: ID (UUID), customer_id (FK), churn_date (date), last_activity_date (date), days_inactive (integer), churn_reason (enum: price/service_quality/competition/relocation/other), churn_reason_detail (text), feedback (text), tenant_id (FK)
- **RetentionMetrics**: ID (UUID), date (date), retention_rate (decimal), churn_rate (decimal), average_ltv (decimal), at_risk_customers_count (integer), churned_customers_count (integer), retention_campaign_impact (decimal), tenant_id (FK)
- **RetentionCampaign**: ID (UUID), tenant_id (FK), name (string), target_segment (string), start_date (date), end_date (date), customers_targeted (integer), customers_retained (integer), revenue_impact (decimal), roi (decimal), status (enum: planned/active/completed), tenant_id (FK)
- **ChurnPrediction**: ID (UUID), customer_id (FK), churn_risk_score (decimal 0-100), predicted_churn_date (date, nullable), prediction_confidence (decimal), risk_factors (JSON array), recommended_actions (JSON array), tenant_id (FK)

#### User Workflows

**For Owner Analyzing Retention:**
1. Access retention analytics dashboard
2. View retention rate and trends
3. View cohort analysis to identify best-performing cohorts
4. View at-risk customer count and trends
5. View churn rate and reasons
6. Compare to industry benchmarks
7. Identify retention improvement opportunities

**For Manager Identifying At-Risk Customers:**
1. View at-risk customer list
2. Filter by risk reason (no recent bookings, declining frequency, etc.)
3. View customer engagement history
4. Identify customers to target for retention
5. Create targeted retention campaign
6. Track campaign effectiveness

**For System Detecting At-Risk Customers:**
1. Analyze customer engagement patterns
2. Calculate engagement score
3. Identify customers with declining activity
4. Flag customers with negative signals (cancellations, no-shows)
5. Alert manager about at-risk customers
6. Predict churn probability
7. Recommend retention actions

**For Manager Analyzing Churn:**
1. View churned customers list
2. Analyze churn reasons
3. Identify patterns and trends
4. Compare churn by customer segment
5. Identify service or staff issues
6. Plan improvements based on feedback

#### Edge Cases & Constraints

- **New Customers**: Don't flag new customers as at-risk; allow ramp-up period
- **Seasonal Patterns**: Account for seasonal variations in booking patterns
- **Service Type**: Different services may have different retention patterns
- **Customer Segments**: Different segments may have different retention expectations
- **Churn Definition**: Define churn as no booking for X days (configurable)
- **Prediction Accuracy**: Churn predictions may have false positives; use with caution
- **Campaign Attribution**: Attribute retention to campaigns carefully; account for other factors

#### Performance Requirements

- **Cohort Calculation**: Calculate cohort retention within 10 seconds
- **At-Risk Detection**: Detect at-risk customers within 1 minute
- **Churn Prediction**: Generate predictions within 5 seconds
- **Analytics Dashboard**: Load dashboard within 3 seconds
- **Retention Metrics**: Calculate metrics within 5 seconds

#### Security Considerations

- **Customer Data**: Restrict access to retention data to authorized managers
- **Churn Feedback**: Protect customer feedback and churn reasons
- **Audit Trail**: Log all retention campaign activities

#### Compliance Requirements

- **Privacy**: Comply with privacy regulations when analyzing customer behavior
- **Data Retention**: Maintain retention data for compliance period

#### Acceptance Criteria

1. WHEN tracking retention, THE System SHALL calculate retention rate by cohort and period
2. WHEN identifying at-risk customers, THE System SHALL flag customers with declining activity
3. WHEN analyzing churn, THE System SHALL identify reasons and patterns
4. WHEN viewing retention metrics, THE System SHALL display trends and benchmarks
5. WHEN targeting retention campaigns, THE System SHALL suggest at-risk customer segments
6. WHEN measuring retention efforts, THE System SHALL track impact on customer lifetime value
7. WHEN exporting retention data, THE System SHALL provide detailed cohort analysis

#### Business Value

- Identifies at-risk customers early
- Enables targeted retention campaigns
- Improves customer lifetime value
- Reduces customer acquisition costs
- Improves profitability

#### Dependencies

- Customer profiles (Requirement 5)
- Appointment booking (Requirement 3)
- Performance metrics (Requirement 21)
- Customer segmentation (Requirement 33)
- Automated marketing (Requirement 59)

#### Key Data Entities

- RetentionCohort (ID, cohort_date, initial_customers, retention_rate_month_1, retention_rate_month_12, tenant_id)
- CustomerEngagement (ID, customer_id, date, engagement_score, at_risk_flag, at_risk_reason, tenant_id)
- ChurnAnalysis (ID, customer_id, churn_date, churn_reason, feedback, tenant_id)
- RetentionMetrics (ID, date, retention_rate, churn_rate, average_ltv, tenant_id)
- RetentionCampaign (ID, tenant_id, name, target_segment, customers_retained, roi, tenant_id)
- ChurnPrediction (ID, customer_id, churn_risk_score, predicted_churn_date, tenant_id)

#### User Roles

- Owner: Views retention analytics
- Marketing Manager: Targets retention campaigns
- Manager: Identifies at-risk customers
- System: Calculates retention metrics

---

### Requirement 42: Appointment History & Audit Logs

**User Story:** As a compliance officer, I want to maintain audit logs, so that I can ensure accountability and support regulatory compliance.

#### Detailed Description

The audit logging system maintains comprehensive records of all system activities, enabling businesses to track changes, investigate issues, and demonstrate compliance with regulations. Every appointment creation, modification, or cancellation is logged with the user who made the change, timestamp, and before/after values. This complete audit trail enables businesses to reconstruct the history of any appointment and identify who made changes.

The system logs all data access, tracking which users accessed customer data and when. This access logging is critical for HIPAA and GDPR compliance, enabling businesses to demonstrate that only authorized users accessed sensitive data. The system supports audit log retention policies, maintaining logs for the required compliance period (typically 7 years for financial records).

Audit logs are immutable and tamper-proof, preventing users from modifying or deleting logs to cover up unauthorized actions. The system generates audit reports for compliance reviews, enabling businesses to demonstrate adherence to regulations. Analytics track audit log patterns, identifying suspicious activities or policy violations.

#### Technical Specifications

- **Change Logging**: Log all changes to appointments, customers, staff, and financial records
- **Access Logging**: Log all data access with user, timestamp, and resource
- **Immutable Logs**: Prevent modification or deletion of audit logs
- **Retention Policies**: Support configurable retention periods
- **Audit Reports**: Generate reports for compliance reviews
- **Tamper Detection**: Detect and alert on log tampering attempts
- **Log Encryption**: Encrypt logs at rest and in transit
- **Log Archival**: Archive old logs to long-term storage

#### Business Context

- **Problem Solved**: Ensures accountability and regulatory compliance; enables issue investigation
- **ROI**: Prevents compliance violations and associated penalties; reduces investigation time
- **Competitive Advantage**: Demonstrates compliance to customers and regulators

#### Integration Points

- **Appointment Booking (Req 3)**: Log appointment changes
- **User Authentication (Req 2)**: Log user access and permission changes
- **Billing & Payment (Req 6)**: Log financial transactions
- **Data Backup (Req 42)**: Include audit logs in backups

#### Data Model Details

- **AuditLog**: ID (UUID), tenant_id (FK), entity_type (enum: appointment/customer/staff/payment/etc), entity_id (UUID), action (enum: create/update/delete/view), changed_by (FK), changed_at (timestamp), old_value (JSON), new_value (JSON), ip_address (string), user_agent (string), status (enum: success/failure), failure_reason (string, nullable), tenant_id (FK)
- **AccessLog**: ID (UUID), tenant_id (FK), user_id (FK), resource_type (enum: customer/appointment/financial), resource_id (UUID), access_type (enum: view/export/download), access_time (timestamp), ip_address (string), user_agent (string), tenant_id (FK)
- **AuditLogRetention**: ID (UUID), tenant_id (FK), entity_type (enum), retention_days (integer), archive_location (string, nullable), tenant_id (FK)
- **ComplianceReport**: ID (UUID), tenant_id (FK), report_type (enum: hipaa/gdpr/sox/pci), period_start (date), period_end (date), generated_at (timestamp), generated_by (FK), findings (JSON), tenant_id (FK)

#### User Workflows

**For Compliance Officer Reviewing Logs:**
1. Access audit log interface
2. Filter by entity type, date range, user
3. View change history for specific entity
4. See before/after values
5. Identify suspicious activities
6. Generate compliance report
7. Export logs for external audit

**For System Logging Changes:**
1. User makes change (appointment, customer, etc.)
2. System captures change details
3. Log change with user, timestamp, before/after values
4. Encrypt and store log
5. Verify log integrity
6. Alert if tampering detected

**For Manager Investigating Issue:**
1. Identify issue or discrepancy
2. Access audit logs
3. Search for related changes
4. View complete change history
5. Identify user who made change
6. Contact user for explanation
7. Document investigation in audit trail

**For System Generating Compliance Report:**
1. Collect audit logs for period
2. Analyze access patterns
3. Identify policy violations
4. Generate report with findings
5. Highlight areas of concern
6. Provide recommendations

#### Edge Cases & Constraints

- **Log Volume**: Handle high volume of logs without performance impact
- **Log Retention**: Maintain logs for compliance period; archive old logs
- **Sensitive Data**: Mask sensitive data in logs (e.g., credit card numbers)
- **User Termination**: Preserve logs from terminated users
- **Log Tampering**: Detect and prevent log tampering
- **Performance**: Logging should not significantly impact system performance
- **Storage**: Manage log storage efficiently; archive old logs

#### Performance Requirements

- **Log Writing**: Write log within 100ms of action
- **Log Retrieval**: Retrieve logs within 1 second
- **Report Generation**: Generate compliance report within 10 seconds
- **Log Archival**: Archive old logs without impacting performance

#### Security Considerations

- **Log Encryption**: Encrypt logs at rest and in transit
- **Access Control**: Restrict access to audit logs to authorized users
- **Tamper Detection**: Detect and alert on log tampering
- **Immutability**: Prevent modification or deletion of logs
- **Audit Trail**: Log all access to audit logs

#### Compliance Requirements

- **HIPAA**: Maintain audit logs of all access to health information
- **GDPR**: Maintain audit logs of data processing activities
- **SOX**: Maintain audit logs for financial transactions
- **PCI-DSS**: Maintain audit logs of payment processing

#### Acceptance Criteria

1. WHEN an appointment is created or modified, THE System SHALL log the change with timestamp and user
2. WHEN viewing appointment history, THE System SHALL display all changes and who made them
3. WHEN tracking data access, THE System SHALL log who accessed customer data and when
4. WHEN exporting audit logs, THE System SHALL provide complete change history
5. WHEN investigating issues, THE System SHALL provide detailed audit trail
6. WHEN retaining logs, THE System SHALL maintain logs for compliance period (typically 7 years)
7. WHEN a user is terminated, THE System SHALL preserve their audit trail

#### Business Value

- Ensures accountability
- Supports regulatory compliance
- Enables issue investigation
- Protects against fraud
- Demonstrates compliance to regulators

#### Dependencies

- Appointment booking (Requirement 3)
- User authentication (Requirement 2)
- Billing & payment processing (Requirement 6)

#### Key Data Entities

- AuditLog (ID, entity_type, entity_id, action, changed_by, changed_at, old_value, new_value, tenant_id)
- AccessLog (ID, user_id, resource_type, resource_id, access_time, tenant_id)
- AuditLogRetention (ID, tenant_id, entity_type, retention_days, tenant_id)
- ComplianceReport (ID, tenant_id, report_type, period_start, period_end, findings, tenant_id)

#### User Roles

- Compliance Officer: Reviews audit logs
- System: Records all changes
- Manager: Investigates issues

---

### Requirement 43: Data Backup & Disaster Recovery

**User Story:** As a platform operator, I want automated backups and disaster recovery, so that I can protect customer data and ensure business continuity.

#### Detailed Description

The data backup and disaster recovery system automatically backs up all customer data at regular intervals, protecting against data loss from hardware failures, software bugs, or security breaches. Backups are stored in geographically distributed locations, ensuring that data can be recovered even if the primary data center fails. The system verifies backup integrity regularly, ensuring that backups can be restored successfully.

The system supports point-in-time recovery, enabling businesses to restore data to any point in time within the retention period. This capability is critical for recovering from ransomware attacks or accidental data deletion. Recovery time objective (RTO) and recovery point objective (RPO) are configurable, enabling businesses to choose the backup frequency and retention period that matches their needs.

Disaster recovery procedures are tested regularly to ensure they work when needed. The system maintains detailed logs of all backup and recovery activities, enabling businesses to demonstrate compliance with disaster recovery requirements. Customers can request data restoration, with the system providing a self-service interface for initiating restores.

#### Technical Specifications

- **Backup Frequency**: Configurable (hourly, daily, weekly)
- **Backup Location**: Geographically distributed storage (multiple regions)
- **Backup Encryption**: Encrypt backups at rest and in transit
- **Backup Verification**: Verify backup integrity regularly
- **Point-in-Time Recovery**: Support recovery to any point in time
- **Recovery Testing**: Regularly test recovery procedures
- **Disaster Recovery Plan**: Document RTO and RPO targets
- **Backup Retention**: Configurable retention period (typically 30-90 days)

#### Business Context

- **Problem Solved**: Protects against data loss; ensures business continuity
- **ROI**: Prevents revenue loss from downtime; reduces recovery costs
- **Competitive Advantage**: Demonstrates data protection to customers

#### Integration Points

- **Multi-Tenant Architecture (Req 1)**: Tenant-aware backup and restore
- **Audit Logging (Req 41)**: Log all backup and recovery activities
- **Database Infrastructure**: Backup database and file storage

#### Data Model Details

- **BackupSchedule**: ID (UUID), tenant_id (FK), frequency (enum: hourly/daily/weekly), retention_days (integer), backup_location (string), enabled (boolean), created_at (timestamp), tenant_id (FK)
- **BackupLog**: ID (UUID), tenant_id (FK), backup_time (timestamp), backup_size (bigint), status (enum: success/failure/partial), verification_status (enum: verified/failed/pending), error_message (string, nullable), backup_location (string), tenant_id (FK)
- **DisasterRecoveryPlan**: ID (UUID), tenant_id (FK), rto_minutes (integer), rpo_minutes (integer), backup_frequency (enum), retention_days (integer), last_tested (date), test_result (enum: passed/failed), tenant_id (FK)
- **RestoreRequest**: ID (UUID), tenant_id (FK), requested_by (FK), restore_point_time (timestamp), status (enum: pending/in_progress/completed/failed), started_at (timestamp, nullable), completed_at (timestamp, nullable), error_message (string, nullable), tenant_id (FK)
- **BackupVerification**: ID (UUID), backup_id (FK), verification_time (timestamp), status (enum: verified/failed), error_message (string, nullable), tenant_id (FK)

#### User Workflows

**For Platform Operator Managing Backups:**
1. Configure backup schedule and retention
2. Set backup locations (multiple regions)
3. Enable automated backups
4. Monitor backup status
5. Verify backup integrity
6. Test disaster recovery procedures
7. Document recovery procedures

**For System Performing Backup:**
1. At scheduled time, initiate backup
2. Backup all tenant data
3. Encrypt backup
4. Store in multiple locations
5. Verify backup integrity
6. Log backup completion
7. Alert if backup fails

**For Customer Requesting Restore:**
1. Log into customer portal
2. Request data restore
3. Select restore point in time
4. Confirm restore request
5. System initiates restore
6. Customer receives notification when complete
7. Verify restored data

**For Platform Operator Testing Recovery:**
1. Schedule recovery test
2. Restore backup to test environment
3. Verify data integrity
4. Test application functionality
5. Document test results
6. Update recovery procedures if needed

#### Edge Cases & Constraints

- **Backup Size**: Handle large backups efficiently
- **Backup Frequency**: Balance between data protection and storage costs
- **Restore Time**: Minimize restore time while ensuring data integrity
- **Partial Failures**: Handle partial backup failures gracefully
- **Backup Verification**: Verify backups regularly without impacting performance
- **Retention Policies**: Enforce retention policies; delete old backups
- **Restore Conflicts**: Handle conflicts when restoring to existing data

#### Performance Requirements

- **Backup Completion**: Complete daily backup within 2 hours
- **Backup Verification**: Verify backup within 1 hour
- **Restore Time**: Restore data within 30 minutes
- **Restore Initiation**: Initiate restore within 5 minutes of request

#### Security Considerations

- **Backup Encryption**: Encrypt backups at rest and in transit
- **Encryption Keys**: Store encryption keys separately from backups
- **Access Control**: Restrict access to backups to authorized users
- **Audit Trail**: Log all backup and restore activities

#### Compliance Requirements

- **Data Protection**: Comply with data protection regulations
- **Disaster Recovery**: Maintain disaster recovery plan
- **Business Continuity**: Ensure business continuity

#### Acceptance Criteria

1. WHEN data is created or modified, THE System SHALL automatically backup to secure location
2. WHEN a backup is completed, THE System SHALL verify integrity and log completion
3. WHEN disaster occurs, THE System SHALL restore from latest backup
4. WHEN testing recovery, THE System SHALL verify backup integrity and recovery time
5. WHEN tracking backups, THE System SHALL display backup schedule and status
6. WHEN retaining backups, THE System SHALL maintain multiple backup versions
7. WHEN a customer requests data restore, THE System SHALL restore to specified point in time

#### Business Value

- Protects against data loss
- Ensures business continuity
- Meets compliance requirements
- Reduces downtime risk
- Enables disaster recovery

#### Dependencies

- Multi-tenant architecture (Requirement 1)
- Database infrastructure

#### Key Data Entities

- BackupSchedule (ID, tenant_id, frequency, retention_days, backup_location, tenant_id)
- BackupLog (ID, tenant_id, backup_time, status, verification_status, tenant_id)
- DisasterRecoveryPlan (ID, tenant_id, rto_minutes, rpo_minutes, tenant_id)
- RestoreRequest (ID, tenant_id, restore_point_time, status, tenant_id)

#### User Roles

- Platform Operator: Manages backups
- Owner: Requests data restore

---

### Requirement 44: Two-Factor Authentication

**User Story:** As a security officer, I want to enforce two-factor authentication, so that I can protect user accounts from unauthorized access.

#### Detailed Description

Two-factor authentication (2FA) adds an additional layer of security by requiring users to provide two forms of identification before gaining access. The system supports multiple 2FA methods including SMS-based one-time passwords (OTP), time-based one-time passwords (TOTP) via authenticator apps, and email-based verification. Users can choose their preferred method, with SMS as the default for accessibility.

When 2FA is enabled, users receive a code via their chosen method after entering their password. They must enter this code within a specified time window (typically 5-10 minutes) to complete authentication. If the code expires or is entered incorrectly, users can request a new code. The system tracks failed 2FA attempts, locking accounts after multiple failures to prevent brute force attacks.

For users who lose access to their 2FA method (e.g., lost phone), the system provides backup codes that can be used for authentication. These backup codes are single-use and should be stored securely. The system tracks 2FA adoption rates, enabling security officers to identify users who haven't enabled 2FA and enforce adoption through policies.

#### Technical Specifications

- **2FA Methods**: SMS OTP, TOTP (authenticator apps), email verification
- **Code Generation**: Generate cryptographically secure codes
- **Code Expiration**: Codes expire after 5-10 minutes
- **Backup Codes**: Generate single-use backup codes for account recovery
- **Failed Attempt Tracking**: Track failed 2FA attempts; lock account after threshold
- **Device Trusted**: Option to trust device for 30 days (skip 2FA on trusted devices)
- **2FA Enforcement**: Support mandatory 2FA for specific user roles
- **Recovery Options**: Support account recovery via backup codes or email

#### Business Context

- **Problem Solved**: Significantly improves account security; prevents unauthorized access
- **ROI**: Prevents account compromise and associated data breaches
- **Competitive Advantage**: Demonstrates security commitment to customers

#### Integration Points

- **User Authentication (Req 2)**: Integrate with login process
- **SMS Provider (Req 46)**: Send SMS OTP codes
- **Email Provider (Req 49)**: Send email verification codes
- **Audit Logging (Req 41)**: Log 2FA events

#### Data Model Details

- **TwoFactorAuth**: ID (UUID), user_id (FK), method (enum: sms/totp/email), enabled_at (timestamp), enabled_by (FK), status (enum: active/disabled), secret_key (string, encrypted), phone_number (string, encrypted, nullable), email (string, nullable), tenant_id (FK)
- **BackupCode**: ID (UUID), user_id (FK), code (string, hashed), generated_at (timestamp), used_at (timestamp, nullable), used_for_login (boolean), tenant_id (FK)
- **TwoFactorLog**: ID (UUID), user_id (FK), attempt_time (timestamp), method (enum), status (enum: success/failure/expired), failure_reason (enum: invalid_code/expired_code/too_many_attempts), ip_address (string), user_agent (string), tenant_id (FK)
- **TwoFactorPolicy**: ID (UUID), tenant_id (FK), mandatory_for_roles (JSON array), enforcement_date (date), grace_period_days (integer), tenant_id (FK)

#### User Workflows

**For User Enabling 2FA:**
1. Log into account settings
2. Select "Enable Two-Factor Authentication"
3. Choose 2FA method (SMS, authenticator app, email)
4. For SMS: Enter phone number, receive verification code
5. For TOTP: Scan QR code with authenticator app
6. For Email: Verify email address
7. Generate and save backup codes
8. Confirm 2FA is enabled

**For User Logging In with 2FA:**
1. Enter email and password
2. System verifies credentials
3. System sends 2FA code via chosen method
4. User receives code
5. User enters code within time window
6. System verifies code
7. User gains access
8. Option to trust device for 30 days

**For User Recovering Account:**
1. Attempt login
2. Forget 2FA code or lose access to 2FA method
3. Select "Use Backup Code"
4. Enter backup code
5. System verifies backup code
6. User gains access
7. Prompt to set up new 2FA method

**For Security Officer Enforcing 2FA:**
1. Access 2FA policy settings
2. Select roles that must use 2FA
3. Set enforcement date
4. Set grace period for adoption
5. System tracks adoption
6. Alert users who haven't enabled 2FA
7. Enforce 2FA on enforcement date

#### Edge Cases & Constraints

- **Code Expiration**: Handle expired codes; allow requesting new code
- **Failed Attempts**: Lock account after multiple failed attempts
- **Backup Codes**: Limit number of backup codes; regenerate when depleted
- **Device Trusted**: Handle device trust expiration
- **Lost 2FA Method**: Support account recovery via backup codes or email
- **2FA Bypass**: Support admin bypass for account recovery (with audit trail)
- **Time Sync**: Handle time sync issues with TOTP codes

#### Performance Requirements

- **Code Generation**: Generate code within 100ms
- **Code Verification**: Verify code within 500ms
- **2FA Delivery**: Deliver SMS/email code within 1 minute
- **Login Time**: Complete 2FA login within 2 minutes

#### Security Considerations

- **Code Security**: Use cryptographically secure random codes
- **Code Transmission**: Send codes over secure channels (HTTPS, SMS)
- **Code Storage**: Hash codes before storing
- **Backup Code Security**: Hash backup codes; limit number of codes
- **Brute Force Protection**: Lock account after multiple failed attempts
- **Audit Trail**: Log all 2FA events

#### Compliance Requirements

- **Security Standards**: Comply with security standards (NIST, OWASP)
- **HIPAA**: Enforce 2FA for HIPAA-regulated data access
- **SOC 2**: Implement 2FA as part of access controls

#### Acceptance Criteria

1. WHEN enabling 2FA, THE System SHALL support SMS and authenticator app methods
2. WHEN a user logs in, THE System SHALL require second factor verification
3. WHEN 2FA is enabled, THE System SHALL send code via selected method
4. WHEN user enters code, THE System SHALL verify and grant access
5. WHEN code expires, THE System SHALL require new code
6. WHEN user loses access to 2FA method, THE System SHALL allow recovery via backup codes
7. WHEN tracking 2FA, THE System SHALL display adoption rate and security metrics

#### Business Value

- Significantly improves account security
- Prevents unauthorized access
- Meets security compliance requirements
- Protects sensitive business data
- Reduces account compromise risk

#### Dependencies

- User authentication (Requirement 2)
- SMS provider (Requirement 46)
- Email provider (Requirement 49)
- Audit logging (Requirement 41)

#### Key Data Entities

- TwoFactorAuth (ID, user_id, method, enabled_at, status, tenant_id)
- BackupCode (ID, user_id, code, generated_at, used_at, tenant_id)
- TwoFactorLog (ID, user_id, attempt_time, method, status, tenant_id)
- TwoFactorPolicy (ID, tenant_id, mandatory_for_roles, enforcement_date, tenant_id)

#### User Roles

- User: Enables and uses 2FA
- Security Officer: Tracks 2FA adoption
- System: Enforces 2FA

---

### Requirement 45: Permission Management

**User Story:** As a business owner, I want granular permission management, so that I can control exactly what each user can do.

#### Detailed Description

The permission management system provides fine-grained access control, enabling business owners to define exactly what each user can do within the system. Rather than relying on fixed roles, the system allows creating custom roles with specific permissions. Permissions are defined at the resource level (e.g., appointments, customers, financial reports) and action level (view, create, edit, delete, export).

Managers can create custom roles tailored to specific job functions, such as "Appointment Scheduler" (can view and create appointments but not edit or delete) or "Financial Analyst" (can view financial reports but not modify transactions). The system prevents privilege escalation by preventing users from modifying their own permissions or creating roles with more permissions than they have.

Permission changes take effect immediately, with the system invalidating cached permissions and enforcing new permissions on the next action. The system tracks all permission changes in the audit log, enabling businesses to investigate who changed permissions and when. Analytics track permission usage, identifying unused permissions and opportunities for simplification.

#### Technical Specifications

- **Resource-Level Permissions**: Define permissions at resource level (appointments, customers, etc.)
- **Action-Level Permissions**: Define permissions at action level (view, create, edit, delete, export)
- **Custom Roles**: Create custom roles with specific permissions
- **Permission Inheritance**: Support role hierarchies with permission inheritance
- **Permission Caching**: Cache permissions with TTL for performance
- **Permission Validation**: Validate permissions before allowing actions
- **Privilege Escalation Prevention**: Prevent users from escalating privileges
- **Permission Audit**: Log all permission changes

#### Business Context

- **Problem Solved**: Enables fine-grained access control; prevents unauthorized actions
- **ROI**: Reduces security incidents from unauthorized access
- **Competitive Advantage**: Demonstrates security commitment to customers

#### Integration Points

- **User Authentication (Req 2)**: Integrate with authentication system
- **Audit Logging (Req 41)**: Log all permission changes
- **API Endpoints**: Enforce permissions at API level

#### Data Model Details

- **Role**: ID (UUID), tenant_id (FK), name (string), description (text), created_at (timestamp), updated_at (timestamp), is_custom (boolean), is_system_role (boolean), tenant_id (FK)
- **Permission**: ID (UUID), tenant_id (FK), resource (string), action (enum: view/create/edit/delete/export), description (text), category (enum: appointments/customers/staff/financial/reports/settings), tenant_id (FK)
- **RolePermission**: ID (UUID), role_id (FK), permission_id (FK), granted_at (timestamp), granted_by (FK), tenant_id (FK)
- **UserRole**: ID (UUID), user_id (FK), role_id (FK), assigned_at (timestamp), assigned_by (FK), expires_at (date, nullable), tenant_id (FK)
- **PermissionAudit**: ID (UUID), tenant_id (FK), change_type (enum: role_created/role_modified/permission_granted/permission_revoked), changed_by (FK), changed_at (timestamp), role_id (FK, nullable), permission_id (FK, nullable), old_value (JSON), new_value (JSON), tenant_id (FK)
- **PermissionCache**: ID (UUID), user_id (FK), permissions (JSON array), cached_at (timestamp), expires_at (timestamp), tenant_id (FK)

#### User Workflows

**For Owner Creating Custom Role:**
1. Access permission management interface
2. Click "Create Role"
3. Enter role name and description
4. Select permissions to grant
5. Review permission summary
6. Save role
7. Assign role to users

**For Owner Assigning Permissions:**
1. Select user to modify
2. View current role and permissions
3. Change role or modify individual permissions
4. Review permission changes
5. Save changes
6. System invalidates cached permissions
7. New permissions take effect immediately

**For System Enforcing Permissions:**
1. User attempts action (view, create, edit, delete, export)
2. System checks cached permissions
3. If cache miss, retrieve permissions from database
4. Verify user has required permission
5. If permission granted, allow action
6. If permission denied, deny action and log attempt
7. Update cache

**For Owner Analyzing Permissions:**
1. View permission usage report
2. Identify unused permissions
3. Identify users with excessive permissions
4. Identify roles with excessive permissions
5. Review permission audit trail
6. Identify permission changes
7. Simplify permissions if needed

#### Edge Cases & Constraints

- **Privilege Escalation**: Prevent users from modifying their own permissions
- **Circular Role Hierarchies**: Prevent circular role hierarchies
- **Permission Conflicts**: Handle conflicting permissions (e.g., view but not edit)
- **System Roles**: Protect system roles from modification
- **Permission Inheritance**: Handle permission inheritance in role hierarchies
- **Expired Roles**: Handle role expiration
- **Permission Caching**: Invalidate cache when permissions change

#### Performance Requirements

- **Permission Check**: Check permissions within 10ms (cached)
- **Permission Retrieval**: Retrieve permissions within 100ms (uncached)
- **Cache Invalidation**: Invalidate cache within 1 second
- **Permission Audit**: Log permission changes within 500ms

#### Security Considerations

- **Privilege Escalation**: Prevent users from escalating privileges
- **Audit Trail**: Log all permission changes
- **Permission Validation**: Validate permissions before allowing actions
- **Cache Security**: Secure permission cache from tampering

#### Compliance Requirements

- **Access Control**: Implement access controls per compliance requirements
- **Audit Trail**: Maintain audit trail of permission changes

#### Acceptance Criteria

1. WHEN creating role, THE System SHALL define specific permissions (view, create, edit, delete)
2. WHEN assigning role to user, THE System SHALL grant all associated permissions
3. WHEN modifying permissions, THE System SHALL immediately update user access
4. WHEN viewing permissions, THE System SHALL display all permissions by role
5. WHEN a user attempts unauthorized action, THE System SHALL deny and log attempt
6. WHEN tracking permissions, THE System SHALL display who has access to what
7. WHEN exporting permissions, THE System SHALL provide complete access matrix

#### Business Value

- Enables fine-grained access control
- Prevents unauthorized actions
- Supports compliance requirements
- Improves security posture
- Reduces security incidents

#### Dependencies

- User authentication (Requirement 2)
- Audit logging (Requirement 41)

#### Key Data Entities

- Role (ID, tenant_id, name, description, is_custom, tenant_id)
- Permission (ID, tenant_id, resource, action, category, tenant_id)
- RolePermission (ID, role_id, permission_id, granted_at, tenant_id)
- UserRole (ID, user_id, role_id, assigned_at, tenant_id)
- PermissionAudit (ID, tenant_id, change_type, changed_by, changed_at, tenant_id)

#### User Roles

- Owner: Manages permissions
- System: Enforces permissions

---

## PHASE 4 - Integrations & Compliance

### Requirement 46: Payment Gateways (Stripe, Square, PayPal)

**User Story:** As a business owner, I want to accept payments through multiple gateways, so that I can offer customer choice and reduce payment friction.

#### Detailed Description

The payment gateway integration system enables businesses to accept payments through multiple providers (Stripe, Square, PayPal), offering customers choice and reducing payment friction. The system routes payments to the selected gateway, handles payment processing, and manages transaction status. Businesses can configure multiple gateways and set preferences for which gateway to use by default or for specific payment types.

The system handles payment failures gracefully, automatically retrying failed payments up to 3 times with exponential backoff. Customers receive notifications about payment failures and can retry manually. The system tracks all transactions with detailed information including amount, fees, status, and timestamps. Reconciliation features match gateway records to system records, identifying discrepancies and enabling investigation.

The system supports multiple payment methods including credit cards, debit cards, digital wallets, and bank transfers (where supported by the gateway). PCI-DSS compliance is maintained through tokenization, never storing full credit card numbers. The system generates detailed payment reports by gateway, enabling businesses to compare fees and performance.

#### Technical Specifications

- **Multi-Gateway Support**: Integrate with Stripe, Square, PayPal APIs
- **Payment Routing**: Route payments to selected gateway based on configuration
- **Retry Logic**: Retry failed payments up to 3 times with exponential backoff
- **Webhook Handling**: Receive and process payment confirmations via webhooks
- **Tokenization**: Support card tokenization for PCI-DSS compliance
- **Reconciliation**: Match gateway records to system records
- **Fee Tracking**: Track and report gateway fees
- **Payment Methods**: Support credit cards, debit cards, digital wallets, bank transfers

#### Business Context

- **Problem Solved**: Increases payment success rates; reduces payment friction
- **ROI**: Increases successful payments by 15-20%; reduces payment processing costs
- **Competitive Advantage**: Multiple payment options improve customer satisfaction

#### Integration Points

- **Billing & Payment (Req 6)**: Process payments for invoices
- **Notifications (Req 7)**: Notify customers of payment status
- **Financial Reconciliation (Req 19)**: Reconcile gateway transactions

#### Data Model Details

- **PaymentGateway**: ID (UUID), tenant_id (FK), name (enum: stripe/square/paypal), api_key (string, encrypted), secret_key (string, encrypted), webhook_url (string), webhook_secret (string, encrypted), enabled (boolean), is_default (boolean), created_at (timestamp), tenant_id (FK)
- **GatewayTransaction**: ID (UUID), tenant_id (FK), gateway_id (FK), invoice_id (FK), transaction_id (string, gateway-specific), amount (decimal), currency (string), status (enum: pending/processing/succeeded/failed), payment_method (enum: card/wallet/bank_transfer), card_last_four (string, nullable), fee_amount (decimal), net_amount (decimal), created_at (timestamp), processed_at (timestamp, nullable), error_message (string, nullable), retry_count (integer), tenant_id (FK)
- **PaymentRetry**: ID (UUID), transaction_id (FK), retry_number (integer), attempted_at (timestamp), status (enum: success/failure), error_message (string, nullable), tenant_id (FK)
- **GatewayReconciliation**: ID (UUID), tenant_id (FK), gateway_id (FK), period_start (date), period_end (date), system_total (decimal), gateway_total (decimal), discrepancy (decimal), reconciled_at (timestamp, nullable), reconciled_by (FK, nullable), tenant_id (FK)

#### User Workflows

**For Owner Configuring Gateway:**
1. Access payment gateway settings
2. Select gateway (Stripe, Square, PayPal)
3. Enter API credentials
4. Configure webhook URL
5. Test connection
6. Set as default or for specific payment types
7. Enable gateway

**For System Processing Payment:**
1. Customer initiates payment
2. Select gateway based on configuration
3. Route payment to gateway
4. Receive payment confirmation via webhook
5. Update transaction status
6. Update invoice status
7. Notify customer

**For System Handling Failed Payment:**
1. Payment fails
2. Log failure reason
3. Wait for retry interval
4. Retry payment (up to 3 times)
5. If all retries fail, notify customer
6. Allow manual retry

**For Accountant Reconciling Payments:**
1. Access reconciliation interface
2. Select gateway and date range
3. Compare system records to gateway records
4. Identify discrepancies
5. Investigate discrepancies
6. Mark as reconciled

#### Edge Cases & Constraints

- **Payment Failures**: Handle various failure reasons (insufficient funds, expired card, etc.)
- **Duplicate Transactions**: Prevent duplicate transactions through idempotency keys
- **Currency Conversion**: Handle currency conversion for international payments
- **Partial Refunds**: Support partial refunds and multiple refunds per transaction
- **Webhook Failures**: Handle webhook delivery failures; implement retry logic
- **Gateway Downtime**: Handle gateway downtime gracefully; queue transactions
- **PCI-DSS Compliance**: Never store full credit card numbers; use tokenization

#### Performance Requirements

- **Payment Processing**: Process payment within 3 seconds
- **Webhook Processing**: Process webhook within 1 second
- **Retry Processing**: Retry failed payments within configured intervals
- **Reconciliation**: Reconcile transactions within 10 seconds

#### Security Considerations

- **API Credentials**: Store API credentials securely; rotate regularly
- **Webhook Verification**: Verify webhook signatures to prevent spoofing
- **PCI-DSS Compliance**: Comply with PCI-DSS requirements
- **Audit Trail**: Log all payment transactions

#### Compliance Requirements

- **PCI-DSS**: Comply with PCI-DSS requirements for payment processing
- **GDPR**: Support payment data export and deletion
- **SOC 2**: Implement controls for payment processing

#### Acceptance Criteria

1. WHEN configuring payment gateway, THE System SHALL authenticate and store API credentials securely
2. WHEN a customer pays, THE System SHALL route payment to selected gateway
3. WHEN payment is processed, THE System SHALL receive confirmation and update invoice status
4. WHEN payment fails, THE System SHALL retry up to 3 times and notify customer
5. WHEN tracking payments, THE System SHALL display transaction details and fees
6. WHEN reconciling payments, THE System SHALL match gateway records to system records
7. WHEN exporting payment data, THE System SHALL provide gateway-specific reports

#### Business Value

- Increases payment success rates
- Reduces payment friction
- Supports customer preferences
- Enables competitive fee comparison
- Improves cash flow

#### Dependencies

- Billing & payment processing (Requirement 6)
- Notifications (Requirement 7)
- Payment gateway APIs (Stripe, Square, PayPal)

#### Key Data Entities

- PaymentGateway (ID, tenant_id, name, api_key, webhook_url, enabled, is_default, tenant_id)
- GatewayTransaction (ID, tenant_id, gateway_id, invoice_id, transaction_id, amount, status, fee_amount, tenant_id)
- PaymentRetry (ID, transaction_id, retry_number, attempted_at, status, tenant_id)
- GatewayReconciliation (ID, tenant_id, gateway_id, period_start, period_end, discrepancy, tenant_id)

#### User Roles

- Owner: Configures payment gateways
- Accountant: Reconciles payments
- System: Processes payments
- Customer: Makes payments

---

### Requirement 47: SMS Providers (Twilio)

**User Story:** As a business owner, I want to send SMS notifications, so that I can reach customers through their preferred channel.

#### Detailed Description

The SMS provider integration system enables businesses to send SMS notifications to customers through Twilio or similar providers. The system sends appointment reminders, payment confirmations, and other transactional messages via SMS. SMS delivery is tracked, with the system logging delivery status and enabling businesses to identify failed messages.

The system supports two-way SMS communication, enabling customers to reply to messages. Replies can trigger automated responses or be routed to staff for manual handling. The system tracks SMS costs and usage, enabling businesses to monitor spending and optimize messaging strategies. Rate limiting prevents SMS spam, with the system limiting messages to 1 per customer per hour.

The system supports SMS templates with variable substitution, enabling personalized messages. Customers can opt out of SMS notifications, with the system respecting preferences and complying with anti-spam regulations. The system maintains detailed logs of all SMS messages for compliance and troubleshooting.

#### Technical Specifications

- **SMS Provider**: Integrate with Twilio API
- **Message Sending**: Send SMS messages asynchronously
- **Delivery Tracking**: Track delivery status (sent, delivered, failed)
- **Two-Way SMS**: Support incoming SMS replies
- **Rate Limiting**: Limit messages to 1 per customer per hour
- **Cost Tracking**: Track SMS costs and usage
- **Template System**: Support SMS templates with variable substitution
- **Opt-Out Management**: Respect customer opt-out preferences

#### Business Context

- **Problem Solved**: Reaches customers on preferred channel; improves notification delivery
- **ROI**: Increases notification delivery rates by 30-40%; improves appointment reminders effectiveness
- **Competitive Advantage**: SMS reminders reduce no-shows and improve customer satisfaction

#### Integration Points

- **Notifications (Req 7)**: Send SMS notifications
- **Appointment Booking (Req 3)**: Send appointment reminders
- **Customer Profiles (Req 5)**: Track customer SMS preferences

#### Data Model Details

- **SMSProvider**: ID (UUID), tenant_id (FK), name (enum: twilio), account_sid (string, encrypted), auth_token (string, encrypted), phone_number (string), webhook_url (string), webhook_secret (string, encrypted), enabled (boolean), created_at (timestamp), tenant_id (FK)
- **SMSMessage**: ID (UUID), tenant_id (FK), recipient (string, phone number), content (text), status (enum: pending/sent/delivered/failed), sent_at (timestamp, nullable), delivered_at (timestamp, nullable), error_message (string, nullable), message_sid (string, nullable), cost (decimal), tenant_id (FK)
- **SMSReply**: ID (UUID), message_id (FK), sender (string, phone number), content (text), received_at (timestamp), processed (boolean), processed_at (timestamp, nullable), tenant_id (FK)
- **SMSAnalytics**: ID (UUID), date (date), messages_sent (integer), messages_delivered (integer), delivery_rate (decimal), total_cost (decimal), tenant_id (FK)

#### User Workflows

**For Owner Configuring SMS Provider:**
1. Access SMS provider settings
2. Enter Twilio credentials
3. Configure webhook URL
4. Test connection
5. Enable SMS provider
6. Configure SMS templates

**For System Sending SMS:**
1. Trigger event (appointment reminder, payment confirmation)
2. Check customer SMS preferences
3. Check rate limiting (1 per hour)
4. Render SMS template with variables
5. Send SMS via Twilio
6. Track delivery status
7. Log SMS message

**For System Handling SMS Reply:**
1. Receive SMS reply via webhook
2. Verify webhook signature
3. Log reply
4. Route to appropriate handler (automated response or staff)
5. Send response if applicable

**For Manager Analyzing SMS:**
1. View SMS analytics dashboard
2. Track messages sent and delivered
3. Monitor delivery rates
4. Track SMS costs
5. Identify failed messages
6. Investigate failures

#### Edge Cases & Constraints

- **Delivery Failures**: Handle failed SMS deliveries; retry if applicable
- **Invalid Phone Numbers**: Validate phone numbers before sending
- **Rate Limiting**: Enforce 1 message per customer per hour
- **Opt-Out**: Respect customer opt-out preferences
- **Cost Tracking**: Track SMS costs accurately
- **Webhook Failures**: Handle webhook delivery failures
- **International Numbers**: Support international phone numbers

#### Performance Requirements

- **SMS Sending**: Send SMS within 1 second of trigger
- **Delivery Tracking**: Update delivery status within 5 seconds
- **Webhook Processing**: Process webhook within 1 second
- **Analytics Calculation**: Calculate analytics within 5 seconds

#### Security Considerations

- **Credentials**: Store Twilio credentials securely
- **Webhook Verification**: Verify webhook signatures
- **Message Content**: Don't include sensitive information in SMS
- **Audit Trail**: Log all SMS messages

#### Compliance Requirements

- **TCPA**: Comply with Telephone Consumer Protection Act
- **GDPR**: Respect customer preferences and privacy
- **Anti-Spam**: Comply with anti-spam regulations

#### Acceptance Criteria

1. WHEN configuring SMS provider, THE System SHALL authenticate and store credentials
2. WHEN sending SMS, THE System SHALL route through provider and track delivery
3. WHEN SMS is delivered, THE System SHALL log delivery status
4. WHEN SMS fails, THE System SHALL retry and log failure
5. WHEN tracking SMS, THE System SHALL display sent count and delivery rates
6. WHEN managing SMS costs, THE System SHALL track usage and costs
7. WHEN exporting SMS data, THE System SHALL provide delivery reports

#### Business Value

- Increases notification delivery rates
- Reaches customers on preferred channel
- Improves appointment reminders effectiveness
- Enables two-way communication
- Reduces no-shows

#### Dependencies

- Notifications (Requirement 7)
- Appointment booking (Requirement 3)
- Customer profiles (Requirement 5)
- Twilio API

#### Key Data Entities

- SMSProvider (ID, tenant_id, name, account_sid, auth_token, phone_number, enabled, tenant_id)
- SMSMessage (ID, tenant_id, recipient, content, status, sent_at, delivered_at, cost, tenant_id)
- SMSReply (ID, message_id, sender, content, received_at, tenant_id)
- SMSAnalytics (ID, date, messages_sent, messages_delivered, delivery_rate, total_cost, tenant_id)

#### User Roles

- Owner: Configures SMS provider
- System: Sends SMS messages
- Manager: Analyzes SMS metrics

---

### Requirement 48: Calendar Sync (Google, Outlook)

**User Story:** As a staff member, I want to sync appointments to my calendar, so that I can manage my schedule across platforms.

#### Detailed Description

The calendar sync system enables staff members to synchronize appointments with their personal calendars (Google Calendar, Outlook). When appointments are created, modified, or cancelled in the system, they are automatically synced to the connected calendar. This two-way sync ensures that staff members have a unified view of their schedule across platforms.

The system supports bi-directional sync, enabling appointments created in external calendars to be synced back to the system. This prevents double-booking and ensures consistency. The system handles timezone differences, converting appointment times to the user's local timezone. Sync status is tracked, enabling users to see when the last sync occurred and identify sync failures.

Staff members can disconnect their calendar at any time, with the system preserving sync history for audit purposes. The system respects calendar permissions, only syncing appointments that the user has permission to access. Integration with calendar provider APIs is handled securely, with credentials stored encrypted and tokens refreshed automatically.

#### Technical Specifications

- **Calendar Providers**: Google Calendar, Outlook/Microsoft 365
- **Bi-Directional Sync**: Sync appointments both ways
- **Timezone Handling**: Convert times to user's local timezone
- **Sync Status Tracking**: Track sync status and last sync time
- **Conflict Resolution**: Handle conflicts when syncing bi-directionally
- **Credential Management**: Store and refresh OAuth tokens securely
- **Sync History**: Maintain sync history for audit purposes
- **Error Handling**: Handle sync failures gracefully

#### Business Context

- **Problem Solved**: Improves staff schedule management; reduces double-booking
- **ROI**: Reduces scheduling conflicts by 80%; improves staff satisfaction
- **Competitive Advantage**: Seamless calendar integration improves user experience

#### Integration Points

- **Appointment Booking (Req 3)**: Sync appointments to calendar
- **Staff Scheduling (Req 4)**: Sync shifts to calendar
- **Notifications (Req 7)**: Notify of sync failures

#### Data Model Details

- **CalendarIntegration**: ID (UUID), user_id (FK), provider (enum: google/outlook), access_token (string, encrypted), refresh_token (string, encrypted), token_expires_at (timestamp), calendar_id (string), enabled (boolean), connected_at (timestamp), last_sync_time (timestamp, nullable), sync_status (enum: synced/syncing/failed), error_message (string, nullable), tenant_id (FK)
- **CalendarSync**: ID (UUID), appointment_id (FK), calendar_integration_id (FK), calendar_event_id (string), sync_direction (enum: system_to_calendar/calendar_to_system), synced_at (timestamp), last_updated_at (timestamp), status (enum: synced/pending/failed), error_message (string, nullable), tenant_id (FK)
- **CalendarSyncHistory**: ID (UUID), calendar_integration_id (FK), sync_time (timestamp), appointments_synced (integer), appointments_created (integer), appointments_updated (integer), appointments_deleted (integer), status (enum: success/partial_failure/failure), error_message (string, nullable), tenant_id (FK)

#### User Workflows

**For Staff Connecting Calendar:**
1. Log into account settings
2. Select "Connect Calendar"
3. Choose calendar provider (Google, Outlook)
4. Authorize application
5. Select calendar to sync
6. Confirm connection
7. System initiates first sync

**For System Syncing Appointment:**
1. Appointment created/modified/cancelled
2. Check if user has connected calendar
3. Prepare appointment data
4. Convert to calendar format
5. Sync to calendar via API
6. Log sync status
7. Alert if sync fails

**For Staff Viewing Sync Status:**
1. Log into account settings
2. View connected calendars
3. See last sync time
4. See sync status
5. Manually trigger sync if needed
6. View sync history

**For Staff Disconnecting Calendar:**
1. Log into account settings
2. Select connected calendar
3. Click "Disconnect"
4. Confirm disconnection
5. System stops syncing
6. Preserve sync history

#### Edge Cases & Constraints

- **Timezone Differences**: Handle timezone conversions correctly
- **Bi-Directional Conflicts**: Handle conflicts when syncing both ways
- **Token Expiration**: Refresh OAuth tokens automatically
- **Sync Failures**: Handle sync failures gracefully; retry
- **Calendar Permissions**: Respect calendar permissions
- **Deleted Events**: Handle deleted events in both directions
- **Recurring Events**: Handle recurring appointments correctly

#### Performance Requirements

- **Sync Initiation**: Initiate sync within 1 second of appointment change
- **Sync Completion**: Complete sync within 5 seconds
- **Token Refresh**: Refresh tokens before expiration
- **Conflict Resolution**: Resolve conflicts within 2 seconds

#### Security Considerations

- **OAuth Tokens**: Store tokens securely; refresh before expiration
- **Credential Encryption**: Encrypt all credentials
- **Audit Trail**: Log all sync activities
- **Permission Validation**: Validate permissions before syncing

#### Compliance Requirements

- **Data Privacy**: Comply with calendar provider privacy policies
- **GDPR**: Respect user privacy and data protection

#### Acceptance Criteria

1. WHEN connecting calendar, THE System SHALL authenticate with Google or Outlook
2. WHEN an appointment is created, THE System SHALL sync to connected calendar
3. WHEN appointment is modified, THE System SHALL update calendar event
4. WHEN appointment is cancelled, THE System SHALL remove from calendar
5. WHEN calendar event is created externally, THE System SHALL sync to appointments
6. WHEN tracking sync, THE System SHALL display sync status and last sync time
7. WHEN disconnecting calendar, THE System SHALL stop syncing and preserve history

#### Business Value

- Improves staff schedule management
- Reduces double-booking
- Enables cross-platform scheduling
- Improves staff satisfaction
- Reduces scheduling errors

#### Dependencies

- Appointment booking (Requirement 3)
- Staff scheduling (Requirement 4)
- Calendar provider APIs (Google, Outlook)

#### Key Data Entities

- CalendarIntegration (ID, user_id, provider, access_token, refresh_token, calendar_id, enabled, tenant_id)
- CalendarSync (ID, appointment_id, calendar_integration_id, calendar_event_id, sync_direction, synced_at, tenant_id)
- CalendarSyncHistory (ID, calendar_integration_id, sync_time, appointments_synced, status, tenant_id)

#### User Roles

- Staff: Connects and manages calendar sync
- System: Syncs appointments

---

### Requirement 49: Accounting Software (QuickBooks, Xero)

**User Story:** As an accountant, I want to sync financial data to accounting software, so that I can streamline bookkeeping and reduce manual entry.

#### Detailed Description

The accounting software integration system enables businesses to sync financial data to QuickBooks, Xero, or similar accounting platforms. Invoices, payments, expenses, and other financial transactions are automatically synced, eliminating manual data entry and reducing errors. The system maintains data consistency between the salon management system and accounting software.

The system supports bi-directional sync, enabling chart of accounts and other master data to be synced from accounting software. This ensures that the salon system uses the same account structure as the accounting software. Sync status is tracked, enabling accountants to identify sync failures and investigate discrepancies. The system supports reconciliation, comparing records between systems and identifying differences.

The system handles complex scenarios including partial payments, refunds, and adjustments. Tax information is preserved during sync, ensuring accurate tax reporting. The system supports multiple accounting software platforms, enabling businesses to choose their preferred platform.

#### Technical Specifications

- **Accounting Platforms**: QuickBooks, Xero
- **Data Sync**: Sync invoices, payments, expenses, customers
- **Bi-Directional Sync**: Sync master data from accounting software
- **Reconciliation**: Compare records between systems
- **Error Handling**: Handle sync failures gracefully
- **Credential Management**: Store and manage API credentials securely
- **Sync History**: Maintain sync history for audit purposes
- **Tax Handling**: Preserve tax information during sync

#### Business Context

- **Problem Solved**: Reduces accounting overhead; improves financial accuracy
- **ROI**: Reduces accounting time by 50-70%; eliminates manual data entry errors
- **Competitive Advantage**: Streamlined accounting improves financial visibility

#### Integration Points

- **Billing & Payment (Req 6)**: Sync invoices and payments
- **Expense Tracking (Req 15)**: Sync expenses
- **Financial Reconciliation (Req 19)**: Reconcile with accounting software

#### Data Model Details

- **AccountingIntegration**: ID (UUID), tenant_id (FK), software_name (enum: quickbooks/xero), api_key (string, encrypted), api_secret (string, encrypted, nullable), realm_id (string, nullable), access_token (string, encrypted), refresh_token (string, encrypted, nullable), token_expires_at (timestamp, nullable), enabled (boolean), connected_at (timestamp), last_sync_time (timestamp, nullable), sync_status (enum: synced/syncing/failed), error_message (string, nullable), tenant_id (FK)
- **AccountingSync**: ID (UUID), accounting_integration_id (FK), transaction_id (UUID), transaction_type (enum: invoice/payment/expense), accounting_entry_id (string), sync_direction (enum: system_to_accounting/accounting_to_system), synced_at (timestamp), status (enum: synced/pending/failed), error_message (string, nullable), tenant_id (FK)
- **AccountingSyncHistory**: ID (UUID), accounting_integration_id (FK), sync_time (timestamp), invoices_synced (integer), payments_synced (integer), expenses_synced (integer), status (enum: success/partial_failure/failure), error_message (string, nullable), tenant_id (FK)

#### User Workflows

**For Accountant Connecting Accounting Software:**
1. Log into accounting settings
2. Select "Connect Accounting Software"
3. Choose platform (QuickBooks, Xero)
4. Authorize application
5. Configure sync settings
6. Confirm connection
7. System initiates first sync

**For System Syncing Financial Data:**
1. Invoice created/payment received/expense recorded
2. Check if accounting software connected
3. Prepare financial data
4. Sync to accounting software via API
5. Log sync status
6. Alert if sync fails

**For Accountant Reconciling Data:**
1. Access reconciliation interface
2. Select accounting software
3. Compare system records to accounting software records
4. Identify discrepancies
5. Investigate discrepancies
6. Mark as reconciled

**For Accountant Viewing Sync Status:**
1. Log into accounting settings
2. View connected accounting software
3. See last sync time
4. See sync status
5. View sync history
6. Manually trigger sync if needed

#### Edge Cases & Constraints

- **Partial Payments**: Handle partial payments correctly
- **Refunds**: Handle refunds and credit memos
- **Adjustments**: Handle adjustments and corrections
- **Tax Handling**: Preserve tax information during sync
- **Currency**: Handle multi-currency transactions
- **Sync Conflicts**: Handle conflicts when syncing bi-directionally
- **Token Expiration**: Refresh OAuth tokens automatically

#### Performance Requirements

- **Sync Initiation**: Initiate sync within 1 second of transaction
- **Sync Completion**: Complete sync within 10 seconds
- **Reconciliation**: Reconcile records within 10 seconds
- **Token Refresh**: Refresh tokens before expiration

#### Security Considerations

- **API Credentials**: Store credentials securely
- **Token Management**: Refresh tokens automatically
- **Audit Trail**: Log all sync activities
- **Data Encryption**: Encrypt data in transit

#### Compliance Requirements

- **Financial Accuracy**: Ensure accurate financial data
- **Audit Trail**: Maintain audit trail of syncs
- **Tax Compliance**: Preserve tax information

#### Acceptance Criteria

1. WHEN connecting accounting software, THE System SHALL authenticate and store credentials
2. WHEN transactions occur, THE System SHALL sync to accounting software
3. WHEN invoices are created, THE System SHALL create corresponding entries in accounting software
4. WHEN payments are received, THE System SHALL record in accounting software
5. WHEN expenses are recorded, THE System SHALL sync to accounting software
6. WHEN tracking sync, THE System SHALL display sync status and last sync time
7. WHEN reconciling, THE System SHALL compare records between systems

#### Business Value

- Reduces accounting overhead
- Improves financial accuracy
- Streamlines bookkeeping
- Enables real-time financial visibility
- Reduces manual data entry

#### Dependencies

- Billing & payment processing (Requirement 6)
- Expense tracking (Requirement 15)
- Accounting software APIs (QuickBooks, Xero)

#### Key Data Entities

- AccountingIntegration (ID, tenant_id, software_name, api_key, access_token, enabled, tenant_id)
- AccountingSync (ID, accounting_integration_id, transaction_id, transaction_type, accounting_entry_id, synced_at, tenant_id)
- AccountingSyncHistory (ID, accounting_integration_id, sync_time, invoices_synced, payments_synced, status, tenant_id)

#### User Roles

- Accountant: Configures integration and reconciles data
- System: Syncs financial data

---

### Requirement 50: Email Providers (SendGrid, Mailgun)

**User Story:** As a business owner, I want to use reliable email providers, so that I can ensure email delivery and track engagement.

#### Detailed Description

The email provider integration system enables businesses to send emails through reliable providers (SendGrid, Mailgun) with high deliverability rates. The system routes all transactional emails (appointment confirmations, reminders, invoices) through the selected provider. Email delivery is tracked, with the system logging delivery status and enabling businesses to identify failed emails.

The system tracks email engagement including open rates and click rates, providing insights into email effectiveness. Bounce and complaint rates are monitored, enabling businesses to maintain sender reputation. The system supports email templates with variable substitution, enabling personalized emails. Unsubscribe links are automatically included in all emails, complying with anti-spam regulations.

The system handles email failures gracefully, retrying failed emails and notifying administrators. Email logs are maintained for compliance and troubleshooting. The system supports multiple email addresses per tenant, enabling different email addresses for different purposes (notifications, marketing, support).

#### Technical Specifications

- **Email Providers**: SendGrid, Mailgun
- **Email Sending**: Send transactional emails asynchronously
- **Delivery Tracking**: Track delivery status (sent, delivered, bounced, complained)
- **Engagement Tracking**: Track opens and clicks
- **Bounce Management**: Monitor bounce rates and manage bounce list
- **Complaint Management**: Monitor complaint rates
- **Template System**: Support email templates with variable substitution
- **Unsubscribe Management**: Include unsubscribe links in all emails

#### Business Context

- **Problem Solved**: Improves email deliverability; tracks email engagement
- **ROI**: Increases email delivery rates by 20-30%; improves email effectiveness
- **Competitive Advantage**: Reliable email delivery improves customer communication

#### Integration Points

- **Notifications (Req 7)**: Send transactional emails
- **Email Marketing (Req 35)**: Send marketing emails
- **Customer Profiles (Req 5)**: Track customer email preferences

#### Data Model Details

- **EmailProvider**: ID (UUID), tenant_id (FK), name (enum: sendgrid/mailgun), api_key (string, encrypted), domain (string), from_email (string), from_name (string), webhook_url (string), webhook_secret (string, encrypted), enabled (boolean), created_at (timestamp), tenant_id (FK)
- **EmailMessage**: ID (UUID), tenant_id (FK), recipient (string, email), subject (string), body (text), status (enum: pending/sent/delivered/bounced/complained), sent_at (timestamp, nullable), delivered_at (timestamp, nullable), opened_at (timestamp, nullable), clicked_at (timestamp, nullable), bounce_type (enum: hard/soft, nullable), complaint_type (enum: abuse/fraud/other, nullable), message_id (string, nullable), tenant_id (FK)
- **EmailEngagement**: ID (UUID), message_id (FK), event_type (enum: open/click/bounce/complaint), event_time (timestamp), link_url (string, nullable), tenant_id (FK)
- **EmailAnalytics**: ID (UUID), date (date), messages_sent (integer), messages_delivered (integer), delivery_rate (decimal), open_rate (decimal), click_rate (decimal), bounce_rate (decimal), complaint_rate (decimal), tenant_id (FK)

#### User Workflows

**For Owner Configuring Email Provider:**
1. Access email provider settings
2. Select provider (SendGrid, Mailgun)
3. Enter API credentials
4. Configure domain
5. Set from email and name
6. Configure webhook URL
7. Test connection
8. Enable provider

**For System Sending Email:**
1. Trigger event (appointment confirmation, reminder, invoice)
2. Render email template with variables
3. Send email via provider
4. Track delivery status
5. Log email message

**For System Tracking Engagement:**
1. Receive engagement event via webhook (open, click, bounce, complaint)
2. Verify webhook signature
3. Log engagement event
4. Update email status
5. Update analytics

**For Manager Analyzing Email:**
1. View email analytics dashboard
2. Track delivery rates
3. Track open rates and click rates
4. Monitor bounce and complaint rates
5. Identify failed emails
6. Investigate failures

#### Edge Cases & Constraints

- **Delivery Failures**: Handle failed email deliveries
- **Bounces**: Handle hard and soft bounces
- **Complaints**: Handle abuse and fraud complaints
- **Unsubscribes**: Respect unsubscribe requests
- **Rate Limiting**: Handle provider rate limits
- **Webhook Failures**: Handle webhook delivery failures
- **Invalid Emails**: Validate email addresses before sending

#### Performance Requirements

- **Email Sending**: Send email within 1 second of trigger
- **Delivery Tracking**: Update delivery status within 5 seconds
- **Webhook Processing**: Process webhook within 1 second
- **Analytics Calculation**: Calculate analytics within 5 seconds

#### Security Considerations

- **API Credentials**: Store credentials securely
- **Webhook Verification**: Verify webhook signatures
- **Email Content**: Don't include sensitive information in emails
- **Audit Trail**: Log all emails

#### Compliance Requirements

- **CAN-SPAM**: Include unsubscribe link in all emails
- **GDPR**: Respect customer preferences and privacy
- **Anti-Spam**: Comply with anti-spam regulations

#### Acceptance Criteria

1. WHEN configuring email provider, THE System SHALL authenticate and store credentials
2. WHEN sending email, THE System SHALL route through provider
3. WHEN email is delivered, THE System SHALL log delivery status
4. WHEN email is opened, THE System SHALL track open event
5. WHEN email link is clicked, THE System SHALL track click event
6. WHEN tracking email, THE System SHALL display delivery and engagement rates
7. WHEN managing email reputation, THE System SHALL monitor bounce and complaint rates

#### Business Value

- Improves email deliverability
- Tracks email engagement
- Enables email analytics
- Maintains sender reputation
- Improves customer communication

#### Dependencies

- Notifications (Requirement 7)
- Email marketing automation (Requirement 35)
- Customer profiles (Requirement 5)
- Email provider APIs (SendGrid, Mailgun)

#### Key Data Entities

- EmailProvider (ID, tenant_id, name, api_key, domain, from_email, enabled, tenant_id)
- EmailMessage (ID, tenant_id, recipient, subject, status, sent_at, delivered_at, opened_at, tenant_id)
- EmailEngagement (ID, message_id, event_type, event_time, tenant_id)
- EmailAnalytics (ID, date, messages_sent, delivery_rate, open_rate, click_rate, tenant_id)

#### User Roles

- Owner: Configures email provider
- System: Sends emails
- Manager: Analyzes email metrics

---

### Requirement 51: Social Media Platforms (Facebook, Instagram)

**User Story:** As a marketing manager, I want to integrate with social media, so that I can manage presence and track engagement.

#### Detailed Description

The social media integration system enables businesses to manage their presence on Facebook and Instagram from a centralized dashboard. Managers can schedule posts, publish content, and track engagement metrics including likes, shares, comments, and follower growth. The system supports social listening, capturing mentions of the business and enabling managers to respond to customer feedback.

The system enables businesses to promote services and special offers on social media, driving traffic to the booking system. Customer reviews and testimonials can be shared on social media, building social proof. The system tracks social media performance, measuring reach, engagement, and conversion to bookings.

The system supports multiple social media accounts, enabling businesses with multiple locations or brands to manage separate accounts. Content calendars enable planning and scheduling posts in advance. Analytics provide insights into which content performs best, enabling data-driven content strategy.

#### Technical Specifications

- **Social Platforms**: Facebook, Instagram
- **Post Scheduling**: Schedule posts in advance
- **Content Publishing**: Publish content to multiple platforms
- **Engagement Tracking**: Track likes, shares, comments
- **Mention Tracking**: Capture mentions of business
- **Follower Tracking**: Track follower count and growth
- **Analytics**: Track reach, engagement, and conversion
- **Multi-Account Support**: Manage multiple accounts

#### Business Context

- **Problem Solved**: Expands marketing reach; increases brand awareness
- **ROI**: Increases social media followers by 30-50%; drives bookings from social media
- **Competitive Advantage**: Active social media presence builds brand awareness

#### Integration Points

- **Social Media Marketing (Req 36)**: Manage social media presence
- **Notifications (Req 7)**: Notify of mentions and engagement
- **Performance Metrics (Req 21)**: Track social media metrics

#### Data Model Details

- **SocialMediaIntegration**: ID (UUID), tenant_id (FK), platform (enum: facebook/instagram), account_id (string), account_name (string), access_token (string, encrypted), refresh_token (string, encrypted, nullable), token_expires_at (timestamp, nullable), enabled (boolean), connected_at (timestamp), last_sync_time (timestamp, nullable), follower_count (integer), tenant_id (FK)
- **SocialMediaPost**: ID (UUID), social_media_integration_id (FK), content (text), image_url (string, nullable), scheduled_at (timestamp, nullable), published_at (timestamp, nullable), post_id (string, nullable), status (enum: draft/scheduled/published), likes_count (integer), shares_count (integer), comments_count (integer), reach (integer), engagement_rate (decimal), tenant_id (FK)
- **SocialMediaMention**: ID (UUID), social_media_integration_id (FK), author (string), content (text), mentioned_at (timestamp), platform_url (string), sentiment (enum: positive/negative/neutral), processed (boolean), processed_at (timestamp, nullable), tenant_id (FK)
- **SocialMediaAnalytics**: ID (UUID), date (date), social_media_integration_id (FK), posts_published (integer), total_likes (integer), total_shares (integer), total_comments (integer), total_reach (integer), follower_growth (integer), engagement_rate (decimal), tenant_id (FK)

#### User Workflows

**For Marketing Manager Connecting Social Media:**
1. Log into social media settings
2. Select "Connect Social Media"
3. Choose platform (Facebook, Instagram)
4. Authorize application
5. Select account to connect
6. Confirm connection
7. System syncs initial data

**For Marketing Manager Publishing Post:**
1. Create new post
2. Enter content and upload image
3. Schedule post or publish immediately
4. Confirm publication
5. System publishes to platform
6. Track engagement

**For System Tracking Engagement:**
1. Periodically fetch engagement metrics
2. Update post engagement counts
3. Track follower growth
4. Capture mentions
5. Update analytics

**For Marketing Manager Analyzing Performance:**
1. View social media analytics dashboard
2. Track posts published and engagement
3. Analyze reach and engagement rate
4. Identify top-performing content
5. View mentions and sentiment
6. Plan content strategy

#### Edge Cases & Constraints

- **Token Expiration**: Refresh OAuth tokens automatically
- **Rate Limiting**: Handle platform rate limits
- **Post Scheduling**: Handle scheduled posts correctly
- **Engagement Tracking**: Handle engagement metrics accurately
- **Mention Tracking**: Capture all mentions
- **Multi-Account**: Support multiple accounts per platform
- **Content Moderation**: Handle inappropriate content

#### Performance Requirements

- **Post Publishing**: Publish post within 2 seconds
- **Engagement Tracking**: Update engagement within 5 minutes
- **Analytics Calculation**: Calculate analytics within 10 seconds
- **Mention Detection**: Detect mentions within 5 minutes

#### Security Considerations

- **OAuth Tokens**: Store tokens securely; refresh before expiration
- **Credential Encryption**: Encrypt all credentials
- **Audit Trail**: Log all social media activities
- **Content Moderation**: Moderate content before publishing

#### Compliance Requirements

- **Platform Policies**: Comply with platform policies
- **Content Guidelines**: Follow platform content guidelines
- **Privacy**: Respect user privacy

#### Acceptance Criteria

1. WHEN connecting social media account, THE System SHALL authenticate and store credentials
2. WHEN posting, THE System SHALL publish to connected platforms
3. WHEN tracking engagement, THE System SHALL capture likes, shares, comments
4. WHEN a customer mentions business, THE System SHALL capture mention
5. WHEN tracking followers, THE System SHALL display follower count and growth
6. WHEN analyzing performance, THE System SHALL display engagement metrics
7. WHEN disconnecting account, THE System SHALL stop posting and preserve history

#### Business Value

- Expands marketing reach
- Increases brand awareness
- Enables social listening
- Drives customer engagement
- Builds social proof

#### Dependencies

- Social media marketing (Requirement 36)
- Notifications (Requirement 7)
- Performance metrics (Requirement 21)
- Social media platform APIs (Facebook, Instagram)

#### Key Data Entities

- SocialMediaIntegration (ID, tenant_id, platform, account_id, access_token, enabled, tenant_id)
- SocialMediaPost (ID, social_media_integration_id, content, published_at, post_id, status, likes_count, tenant_id)
- SocialMediaMention (ID, social_media_integration_id, author, content, mentioned_at, sentiment, tenant_id)
- SocialMediaAnalytics (ID, date, social_media_integration_id, posts_published, total_likes, engagement_rate, tenant_id)

#### User Roles

- Marketing Manager: Manages social media presence
- System: Tracks engagement and publishes posts

---

### Requirement 52: HIPAA/GDPR Compliance

**User Story:** As a compliance officer, I want to ensure HIPAA and GDPR compliance, so that I can protect customer data and avoid penalties.

#### Detailed Description

The compliance management system ensures that the platform meets stringent regulatory requirements including HIPAA (Health Insurance Portability and Accountability Act) and GDPR (General Data Protection Regulation). This system is critical for businesses operating in regulated industries or serving customers in the EU, as non-compliance can result in substantial fines (up to 4% of annual revenue for GDPR violations) and reputational damage.

The system implements comprehensive data protection measures including encryption, access controls, audit logging, and data retention policies. It provides tools for compliance officers to manage consent records, conduct data access audits, and generate compliance reports. The system supports automated data deletion and export workflows to fulfill customer rights requests within required timeframes.

The system maintains detailed audit trails of all data access and modifications, enabling forensic analysis in case of data breaches. Automated compliance monitoring alerts administrators to potential violations, enabling proactive remediation. The system supports multiple compliance frameworks, allowing businesses to configure compliance rules based on their specific regulatory requirements.

#### Technical Specifications

- **Data Encryption**: AES-256 encryption for data at rest; TLS 1.3 for data in transit
- **Encryption Key Management**: Separate encryption keys per tenant; keys stored in secure key management service (AWS KMS, Azure Key Vault)
- **Access Control**: Role-based access control with principle of least privilege; multi-factor authentication for sensitive operations
- **Audit Logging**: Comprehensive logging of all data access, modifications, and deletions with user, timestamp, and action details
- **Data Retention**: Configurable retention policies; automatic deletion of data after retention period expires
- **Data Export**: Support for exporting data in standard formats (CSV, JSON, XML) for data portability
- **Consent Management**: Track customer consent for data processing; support for granular consent preferences
- **Breach Notification**: Automated breach notification system with configurable notification templates and delivery methods

#### Business Context

- **Problem Solved**: Enables compliance with HIPAA, GDPR, and other data protection regulations; prevents regulatory fines and reputational damage
- **ROI**: Avoids GDPR fines (up to €20 million or 4% of revenue); avoids HIPAA fines (up to $1.5 million per violation); builds customer trust
- **Competitive Advantage**: Demonstrates commitment to data privacy; enables serving regulated industries and EU customers; differentiates from non-compliant competitors

#### Integration Points

- **Multi-Tenant Architecture (Req 1)**: Compliance policies applied per tenant; data isolation ensures compliance
- **User Authentication (Req 2)**: Access control enforces principle of least privilege
- **Audit Logging (Req 41)**: Comprehensive audit trail for compliance verification
- **Data Backup & Disaster Recovery (Req 42)**: Backup and restore procedures comply with data protection requirements
- **Customer Profiles (Req 5)**: Consent records linked to customer profiles

#### Data Model Details

- **CompliancePolicy**: ID (UUID), tenant_id (FK), policy_type (enum: GDPR/HIPAA/CCPA/other), requirements (JSON), effective_date (date), last_updated (timestamp), created_by (FK), tenant_id (FK)
- **ConsentRecord**: ID (UUID), customer_id (FK), consent_type (enum: marketing/analytics/health_data/other), granted_at (timestamp), expires_at (timestamp, nullable), revoked_at (timestamp, nullable), consent_method (enum: explicit/implicit), ip_address (string), user_agent (string), tenant_id (FK)
- **DataBreachLog**: ID (UUID), tenant_id (FK), breach_date (date), discovery_date (date), affected_records (integer), breach_type (string), description (text), notification_sent (boolean), notification_date (date, nullable), notification_method (enum: email/phone/mail), affected_customers (JSON array), remediation_steps (text), tenant_id (FK)
- **DataAccessLog**: ID (UUID), tenant_id (FK), user_id (FK), resource_type (string), resource_id (string), action (enum: view/export/delete), access_time (timestamp), ip_address (string), user_agent (string), justification (text), tenant_id (FK)
- **DataRetentionPolicy**: ID (UUID), tenant_id (FK), data_type (string), retention_period_days (integer), deletion_method (enum: soft_delete/hard_delete/anonymization), effective_date (date), tenant_id (FK)

#### User Workflows

**For Compliance Officer Setting Up Compliance:**
1. Access compliance settings
2. Select applicable regulations (GDPR, HIPAA, CCPA)
3. Configure compliance policies
4. Set data retention periods
5. Configure breach notification procedures
6. Set up audit logging
7. Enable automated compliance monitoring

**For Customer Requesting Data Export:**
1. Submit data export request through customer portal
2. System verifies customer identity
3. System compiles all customer data
4. System generates export file in requested format
5. System sends export file to customer email
6. System logs data export request

**For Customer Requesting Data Deletion:**
1. Submit data deletion request through customer portal
2. System verifies customer identity
3. System schedules data deletion (within 30 days)
4. System sends confirmation email
5. System performs data deletion
6. System sends deletion confirmation
7. System logs data deletion

**For Compliance Officer Conducting Audit:**
1. Access audit dashboard
2. Select audit period and scope
3. Review data access logs
4. Identify suspicious access patterns
5. Generate audit report
6. Export audit report
7. Share with auditors or regulators

**For System Detecting Data Breach:**
1. Detect unauthorized data access or modification
2. Alert compliance officer immediately
3. Compile list of affected customers
4. Generate breach notification
5. Send notifications to affected customers
6. Log breach details
7. Generate breach report

#### Edge Cases & Constraints

- **Data Portability**: Support exporting data in multiple formats; handle large exports (>1GB) efficiently
- **Right to be Forgotten**: Ensure complete deletion of customer data; handle cascading deletions across related records
- **Consent Expiration**: Automatically revoke expired consents; prevent data processing after expiration
- **Breach Notification Timing**: Notify customers within required timeframe (72 hours for GDPR); handle notification failures
- **Data Minimization**: Prevent storing unnecessary data; implement data minimization policies
- **Cross-Border Transfers**: Restrict data transfers to countries with adequate data protection
- **Regulatory Changes**: Support updating compliance policies as regulations change
- **Audit Trail Integrity**: Ensure audit logs cannot be modified or deleted; implement immutable audit logs

#### Performance Requirements

- **Data Export**: Export customer data within 5 minutes for typical customer (< 100MB)
- **Data Deletion**: Complete data deletion within 30 days of request
- **Audit Log Query**: Query audit logs within 2 seconds
- **Breach Notification**: Send breach notifications within 1 hour of detection
- **Compliance Report Generation**: Generate compliance report within 10 minutes

#### Security Considerations

- **Encryption Keys**: Store encryption keys separately from encrypted data; rotate keys annually
- **Access Control**: Enforce multi-factor authentication for compliance officer access
- **Audit Log Protection**: Implement immutable audit logs; prevent unauthorized modification or deletion
- **Breach Detection**: Implement intrusion detection systems to identify unauthorized access
- **Data Minimization**: Collect only necessary data; delete data when no longer needed
- **Vendor Management**: Ensure third-party vendors comply with data protection requirements

#### Compliance Requirements

- **GDPR**: Support data portability, right to be forgotten, consent management, breach notification (72 hours)
- **HIPAA**: Encrypt health information; maintain audit logs; implement access controls; support business associate agreements
- **CCPA**: Support consumer rights (access, deletion, opt-out); maintain privacy policy; implement opt-out mechanisms
- **SOC 2**: Implement access controls, audit logging, encryption, and incident response procedures
- **ISO 27001**: Implement information security management system; conduct regular security audits

#### Acceptance Criteria

1. WHEN storing health information, THE System SHALL encrypt data at rest using AES-256 and in transit using TLS 1.3
2. WHEN a customer requests data export, THE System SHALL provide complete data in standard format (CSV, JSON, XML) within 5 minutes
3. WHEN a customer requests deletion, THE System SHALL securely delete all personal data within 30 days and confirm deletion
4. WHEN tracking data access, THE System SHALL log all access to sensitive data with user, timestamp, and action details
5. WHEN conducting audit, THE System SHALL provide compliance reports with data access logs and audit trails
6. WHEN a data breach occurs, THE System SHALL notify affected customers within 1 hour and provide breach details
7. WHEN managing consent, THE System SHALL track customer consent for data processing and prevent processing after consent revocation

#### Business Value

- Ensures regulatory compliance with GDPR, HIPAA, CCPA, and other regulations
- Protects customer privacy and builds trust
- Avoids regulatory fines and penalties
- Enables serving regulated industries and EU customers
- Demonstrates commitment to data protection

#### Dependencies

- Multi-tenant architecture (Requirement 1)
- User authentication (Requirement 2)
- Audit logging (Requirement 41)
- Data backup & disaster recovery (Requirement 42)

#### Key Data Entities

- CompliancePolicy (ID, tenant_id, policy_type, requirements, effective_date, last_updated)
- ConsentRecord (ID, customer_id, consent_type, granted_at, expires_at, revoked_at, consent_method)
- DataBreachLog (ID, tenant_id, breach_date, affected_records, notification_sent, notification_date)
- DataAccessLog (ID, tenant_id, user_id, resource_type, action, access_time, ip_address)
- DataRetentionPolicy (ID, tenant_id, data_type, retention_period_days, deletion_method)

#### User Roles

- Compliance Officer: Manages compliance policies, conducts audits, handles breach notifications
- System: Enforces compliance rules, logs data access, manages data retention
- Customer: Requests data export and deletion, manages consent preferences

---

### Requirement 53: Revenue Analytics by Service/Staff/Time

**User Story:** As a business owner, I want detailed revenue analytics, so that I can identify top performers and optimize pricing.

#### Detailed Description

The revenue analytics system provides comprehensive financial insights into business performance, enabling data-driven decision-making about pricing, staffing, and service offerings. The system breaks down revenue by multiple dimensions (service, staff member, location, time period) to identify which services and staff members generate the most revenue and profit.

The system tracks revenue in real-time, updating analytics as appointments are completed and payments are processed. Historical data is aggregated into daily, weekly, monthly, and yearly summaries for trend analysis. The system identifies high-margin services and underperforming services, enabling managers to optimize service mix and pricing. Forecasting capabilities project future revenue based on historical trends and seasonal patterns.

The system supports drill-down analysis, enabling managers to explore revenue data at multiple levels of detail. Custom reports can be generated for specific time periods, services, or staff members. Revenue data is exported in multiple formats (CSV, Excel, PDF) for use in business planning and financial reporting.

#### Technical Specifications

- **Real-Time Analytics**: Update revenue metrics in real-time as appointments complete and payments process
- **Multi-Dimensional Analysis**: Break down revenue by service, staff member, location, time period, customer segment
- **Aggregation**: Daily, weekly, monthly, yearly aggregations for trend analysis
- **Forecasting**: Project future revenue using time series analysis and seasonal decomposition
- **Drill-Down**: Enable exploring revenue data at multiple levels of detail
- **Custom Reports**: Generate custom reports for specific time periods, services, or staff members
- **Export Formats**: Support CSV, Excel, PDF export formats
- **Caching**: Cache aggregated data for performance; invalidate cache when new data arrives

#### Business Context

- **Problem Solved**: Provides visibility into revenue drivers; enables identifying top performers and underperformers; supports pricing optimization
- **ROI**: Increases revenue by 15-20% through pricing optimization; identifies underperforming services for discontinuation or improvement
- **Competitive Advantage**: Data-driven insights enable competitive pricing and service mix optimization; enables identifying growth opportunities

#### Integration Points

- **Billing & Payment Processing (Req 6)**: Revenue data sourced from completed appointments and payments
- **Performance Metrics (Req 21)**: Revenue metrics integrated into overall performance dashboard
- **Staff Scheduling (Req 4)**: Revenue per staff member enables identifying top performers
- **Appointment Booking (Req 3)**: Appointment data used to calculate revenue metrics

#### Data Model Details

- **RevenueAnalytics**: ID (UUID), date (date), service_id (FK), staff_id (FK), location_id (FK), revenue (decimal), transaction_count (integer), average_transaction_value (decimal), profit (decimal), profit_margin (decimal), tenant_id (FK)
- **RevenueReport**: ID (UUID), tenant_id (FK), period (enum: daily/weekly/monthly/yearly), period_start (date), period_end (date), total_revenue (decimal), revenue_by_service (JSON), revenue_by_staff (JSON), revenue_by_location (JSON), top_services (JSON array), bottom_services (JSON array), created_at (timestamp), tenant_id (FK)
- **RevenueForecast**: ID (UUID), tenant_id (FK), forecast_date (date), service_id (FK), forecasted_revenue (decimal), confidence_interval (decimal), actual_revenue (decimal, nullable), forecast_accuracy (decimal, nullable), tenant_id (FK)
- **RevenueMetrics**: ID (UUID), tenant_id (FK), date (date), total_revenue (decimal), average_transaction_value (decimal), transaction_count (integer), revenue_per_staff_hour (decimal), revenue_per_location (decimal), tenant_id (FK)

#### User Workflows

**For Owner Analyzing Revenue:**
1. Access revenue analytics dashboard
2. Select time period (day, week, month, year)
3. View total revenue and key metrics
4. Drill down by service to see service-level revenue
5. Drill down by staff member to see staff performance
6. Identify top-performing and underperforming services
7. Compare revenue trends over time
8. Export report for business planning

**For Manager Optimizing Pricing:**
1. Access revenue analytics
2. Identify high-margin services
3. Identify low-margin services
4. Analyze customer demand for each service
5. Recommend price increases for high-demand services
6. Recommend price decreases or discontinuation for low-demand services
7. Track revenue impact of pricing changes

**For Manager Identifying Top Performers:**
1. Access revenue analytics
2. View revenue generated by each staff member
3. Identify top revenue generators
4. Identify underperforming staff
5. Analyze revenue per appointment for each staff member
6. Identify staff with highest customer satisfaction
7. Use data for performance reviews and compensation decisions

**For System Generating Forecasts:**
1. Analyze historical revenue data
2. Identify seasonal patterns and trends
3. Generate revenue forecasts for next period
4. Calculate confidence intervals
5. Compare forecasts to actual revenue
6. Refine forecasting model based on accuracy

#### Edge Cases & Constraints

- **Partial Periods**: Handle revenue calculations for partial periods (e.g., first day of month)
- **Refunds and Cancellations**: Adjust revenue for refunds and cancellations; track net revenue
- **Multiple Currencies**: Support multiple currencies; convert to base currency for reporting
- **Seasonal Variations**: Account for seasonal patterns in forecasting
- **Outliers**: Identify and handle revenue outliers (e.g., large group bookings)
- **Staff Changes**: Handle staff joining/leaving mid-period; calculate revenue per staff hour accurately
- **Service Changes**: Handle service price changes; calculate revenue accurately for changed services
- **Data Delays**: Handle delays in payment processing; use estimated revenue for real-time analytics

#### Performance Requirements

- **Real-Time Updates**: Update revenue metrics within 5 minutes of appointment completion
- **Report Generation**: Generate custom reports within 30 seconds
- **Forecast Calculation**: Calculate revenue forecasts within 1 minute
- **Dashboard Load**: Load analytics dashboard within 2 seconds
- **Export**: Export reports within 30 seconds

#### Security Considerations

- **Data Access**: Restrict revenue data access to authorized users (Owner, Manager)
- **Audit Trail**: Log all revenue data access and report generation
- **Data Accuracy**: Implement controls to ensure revenue data accuracy
- **Sensitive Data**: Don't expose individual customer payment information in reports

#### Compliance Requirements

- **Financial Reporting**: Ensure revenue data complies with accounting standards (GAAP, IFRS)
- **Tax Reporting**: Support tax reporting requirements; maintain audit trail for tax purposes
- **Data Privacy**: Ensure revenue reports don't expose customer personal information

#### Acceptance Criteria

1. WHEN analyzing revenue, THE System SHALL break down by service, staff member, location, and time period
2. WHEN comparing services, THE System SHALL display revenue, volume, profitability, and margin
3. WHEN comparing staff, THE System SHALL display revenue generated, average transaction value, and revenue per hour
4. WHEN analyzing trends, THE System SHALL display revenue by day, week, month, year with trend indicators
5. WHEN identifying opportunities, THE System SHALL highlight high-margin services and underperforming services
6. WHEN forecasting, THE System SHALL project revenue based on trends with confidence intervals
7. WHEN exporting analytics, THE System SHALL provide detailed breakdowns in CSV, Excel, and PDF formats

#### Business Value

- Identifies top-performing services and staff members
- Enables pricing optimization and revenue maximization
- Supports strategic planning and business decisions
- Improves profitability through data-driven insights
- Enables identifying growth opportunities

#### Dependencies

- Billing & payment processing (Requirement 6)
- Performance metrics (Requirement 21)
- Appointment booking (Requirement 3)
- Staff scheduling (Requirement 4)

#### Key Data Entities

- RevenueAnalytics (ID, date, service_id, staff_id, location_id, revenue, transaction_count, profit_margin)
- RevenueReport (ID, tenant_id, period, total_revenue, revenue_by_service, revenue_by_staff, top_services)
- RevenueForecast (ID, tenant_id, forecast_date, service_id, forecasted_revenue, confidence_interval)
- RevenueMetrics (ID, tenant_id, date, total_revenue, average_transaction_value, revenue_per_staff_hour)

#### User Roles

- Owner: Views and analyzes revenue analytics
- Manager: Analyzes revenue trends and optimizes pricing
- System: Calculates and aggregates revenue metrics

---

### Requirement 54: Customer Lifetime Value Tracking

**User Story:** As a business owner, I want to track customer lifetime value, so that I can measure customer profitability and optimize acquisition spending.

#### Detailed Description

The Customer Lifetime Value (CLV) tracking system calculates and monitors the total profit a business can expect from a customer over their entire relationship. CLV is a critical metric for understanding customer profitability and making informed decisions about customer acquisition spending, retention investments, and customer segmentation.

The system calculates CLV by summing all revenue from a customer and subtracting acquisition costs and service costs. CLV is tracked over time, enabling businesses to identify high-value customers and low-value customers. The system segments customers by CLV, enabling targeted retention and acquisition strategies. Cohort analysis tracks CLV by customer acquisition date, enabling businesses to measure the effectiveness of acquisition campaigns.

The system forecasts future CLV based on customer behavior, enabling businesses to predict which customers will become high-value customers. The system recommends optimal customer acquisition spending based on CLV, enabling businesses to maximize return on acquisition investment. Analytics identify factors that drive high CLV, enabling businesses to focus acquisition efforts on high-value customer segments.

#### Technical Specifications

- **CLV Calculation**: Sum all revenue from customer minus acquisition cost and service costs
- **Acquisition Cost Tracking**: Track acquisition cost per customer (marketing spend, referral fees, etc.)
- **Service Cost Tracking**: Track service costs (staff time, materials, overhead allocation)
- **CLV Forecasting**: Project future CLV based on customer behavior and historical patterns
- **Cohort Analysis**: Track CLV by customer acquisition date and source
- **Segmentation**: Segment customers by CLV (high-value, medium-value, low-value)
- **Benchmarking**: Compare customer CLV to industry benchmarks
- **Acquisition Recommendations**: Recommend optimal acquisition spending based on CLV

#### Business Context

- **Problem Solved**: Enables identifying high-value customers for retention focus; enables optimizing acquisition spending; enables measuring customer profitability
- **ROI**: Increases profitability by 20-30% through optimized acquisition spending; enables focusing retention efforts on high-value customers
- **Competitive Advantage**: Data-driven customer acquisition strategy enables competing on customer profitability rather than just customer count

#### Integration Points

- **Customer Profiles (Req 5)**: CLV linked to customer profiles; customer acquisition source tracked
- **Billing & Payment Processing (Req 6)**: Revenue data sourced from customer payments
- **Performance Metrics (Req 21)**: CLV metrics integrated into overall performance dashboard
- **Marketing Campaigns (Req 35, 36)**: Acquisition cost tracked per campaign; CLV used to measure campaign ROI

#### Data Model Details

- **CustomerLifetimeValue**: ID (UUID), customer_id (FK), total_revenue (decimal), acquisition_cost (decimal), service_costs (decimal), clv (decimal), clv_calculated_at (timestamp), clv_forecast (decimal), forecast_confidence (decimal), customer_status (enum: active/inactive/churned), tenant_id (FK)
- **CLVAnalytics**: ID (UUID), tenant_id (FK), date (date), average_clv (decimal), median_clv (decimal), clv_by_cohort (JSON), clv_distribution (JSON), high_value_customers (integer), low_value_customers (integer), tenant_id (FK)
- **CLVSegment**: ID (UUID), tenant_id (FK), segment_name (string), clv_min (decimal), clv_max (decimal), customer_count (integer), average_clv (decimal), retention_rate (decimal), tenant_id (FK)
- **AcquisitionCost**: ID (UUID), customer_id (FK), acquisition_source (enum: organic/paid_search/social/referral/other), campaign_id (FK, nullable), cost (decimal), acquisition_date (date), tenant_id (FK)
- **CLVForecast**: ID (UUID), customer_id (FK), forecast_date (date), forecasted_clv (decimal), confidence_interval (decimal), forecast_factors (JSON), actual_clv (decimal, nullable), forecast_accuracy (decimal, nullable), tenant_id (FK)

#### User Workflows

**For Owner Analyzing Customer Profitability:**
1. Access CLV analytics dashboard
2. View average CLV and CLV distribution
3. Identify high-value customer segment
4. Identify low-value customer segment
5. Analyze CLV by customer acquisition source
6. Compare CLV across cohorts
7. Identify factors driving high CLV
8. Make decisions about acquisition spending

**For Marketing Manager Optimizing Acquisition:**
1. Access CLV analytics
2. View CLV by acquisition source
3. Calculate ROI for each acquisition channel
4. Identify highest-ROI acquisition channels
5. Recommend increasing spending on high-ROI channels
6. Recommend decreasing spending on low-ROI channels
7. Set acquisition spending limits based on CLV

**For Manager Identifying Retention Opportunities:**
1. Access CLV analytics
2. Identify high-value customers at risk of churn
3. Identify low-value customers with potential to increase value
4. Create targeted retention campaigns for high-value customers
5. Create upsell campaigns for medium-value customers
6. Track impact of retention campaigns on CLV

**For System Calculating CLV:**
1. Retrieve customer revenue history
2. Retrieve customer acquisition cost
3. Estimate service costs
4. Calculate CLV = total revenue - acquisition cost - service costs
5. Update CLV in customer record
6. Generate CLV analytics
7. Forecast future CLV

#### Edge Cases & Constraints

- **New Customers**: CLV for new customers may be negative (acquisition cost > revenue); handle appropriately
- **Churned Customers**: Track CLV for churned customers; identify factors that led to churn
- **Acquisition Cost Attribution**: Handle multi-touch attribution for acquisition cost
- **Service Cost Allocation**: Allocate shared service costs fairly across customers
- **Refunds and Cancellations**: Adjust CLV for refunds and cancellations
- **Seasonal Variations**: Account for seasonal patterns in CLV forecasting
- **Long-Term Relationships**: Handle customers with very long relationships; ensure CLV calculations remain accurate
- **Acquisition Source Tracking**: Ensure acquisition source is accurately tracked for all customers

#### Performance Requirements

- **CLV Calculation**: Calculate CLV within 5 seconds per customer
- **Batch CLV Updates**: Update CLV for all customers within 1 hour
- **CLV Analytics**: Generate CLV analytics within 30 seconds
- **Forecast Calculation**: Calculate CLV forecasts within 2 minutes
- **Dashboard Load**: Load CLV dashboard within 2 seconds

#### Security Considerations

- **Data Access**: Restrict CLV data access to authorized users (Owner, Manager)
- **Audit Trail**: Log all CLV calculations and data access
- **Data Accuracy**: Implement controls to ensure CLV data accuracy
- **Sensitive Data**: Don't expose individual customer payment information in CLV reports

#### Compliance Requirements

- **Financial Reporting**: Ensure CLV calculations comply with accounting standards
- **Data Privacy**: Ensure CLV reports don't expose customer personal information
- **GDPR**: Support CLV data export and deletion for customer data portability

#### Acceptance Criteria

1. WHEN calculating CLV, THE System SHALL sum all revenue from customer minus acquisition cost and service costs
2. WHEN tracking CLV, THE System SHALL display CLV by customer and cohort with historical trends
3. WHEN comparing customers, THE System SHALL identify high-value, medium-value, and low-value customer segments
4. WHEN analyzing CLV trends, THE System SHALL display changes over time and identify trends
5. WHEN forecasting CLV, THE System SHALL project future value based on customer behavior with confidence intervals
6. WHEN optimizing acquisition, THE System SHALL recommend spending limits based on CLV and ROI
7. WHEN exporting CLV data, THE System SHALL provide detailed customer value analysis in multiple formats

#### Business Value

- Identifies high-value customers for retention focus
- Optimizes customer acquisition spending
- Improves profitability through data-driven decisions
- Enables measuring customer profitability
- Supports strategic customer segmentation

#### Dependencies

- Customer profiles (Requirement 5)
- Billing & payment processing (Requirement 6)
- Performance metrics (Requirement 21)
- Marketing campaigns (Requirements 35, 36)

#### Key Data Entities

- CustomerLifetimeValue (ID, customer_id, total_revenue, acquisition_cost, service_costs, clv, clv_forecast)
- CLVAnalytics (ID, tenant_id, date, average_clv, clv_by_cohort, high_value_customers)
- CLVSegment (ID, tenant_id, segment_name, clv_min, clv_max, customer_count, average_clv)
- AcquisitionCost (ID, customer_id, acquisition_source, campaign_id, cost, acquisition_date)
- CLVForecast (ID, customer_id, forecast_date, forecasted_clv, confidence_interval)

#### User Roles

- Owner: Views and analyzes CLV analytics
- Marketing Manager: Uses CLV for acquisition decisions
- Manager: Identifies retention opportunities
- System: Calculates and forecasts CLV

---

### Requirement 55: Churn Analysis

**User Story:** As a business owner, I want to analyze customer churn, so that I can identify at-risk customers and improve retention.

#### Detailed Description

The churn analysis system identifies customers at risk of leaving and provides insights into why customers churn. Churn is one of the most critical metrics for service businesses, as retaining existing customers is typically 5-25 times cheaper than acquiring new customers. The system tracks customer engagement patterns and identifies customers who haven't booked appointments in a specified period, flagging them as at-risk.

The system analyzes churn reasons by tracking customer feedback, support interactions, and behavioral patterns. It identifies common reasons for churn (price, service quality, competition, life changes) and enables targeted retention campaigns. Predictive analytics forecast which customers are likely to churn based on behavioral patterns, enabling proactive intervention.

The system measures churn rate by customer cohort, enabling businesses to identify which customer segments have the highest churn. Seasonal analysis identifies periods of high churn, enabling businesses to plan retention campaigns accordingly. The system tracks the effectiveness of retention campaigns, measuring impact on churn rate and customer lifetime value.

#### Technical Specifications

- **Inactivity Detection**: Identify customers inactive for configurable period (default 30 days)
- **Churn Risk Scoring**: Calculate churn risk score based on engagement patterns, booking frequency, and customer feedback
- **Churn Prediction**: Use machine learning to predict which customers are likely to churn
- **Churn Reason Tracking**: Categorize churn reasons (price, service quality, competition, life changes, other)
- **Cohort Analysis**: Track churn rate by customer acquisition date and source
- **Seasonal Analysis**: Identify seasonal patterns in churn
- **Retention Campaign Tracking**: Track impact of retention campaigns on churn rate
- **Churn Forecasting**: Project future churn rate based on trends

#### Business Context

- **Problem Solved**: Enables identifying at-risk customers early; enables targeted retention campaigns; reduces customer loss
- **ROI**: Reduces churn by 20-30% through targeted retention; improves customer lifetime value by 30-50%
- **Competitive Advantage**: Proactive retention strategy differentiates from competitors; enables competing on customer loyalty

#### Integration Points

- **Customer Profiles (Req 5)**: Churn risk linked to customer profiles; customer engagement tracked
- **Appointment Booking (Req 3)**: Booking frequency used to calculate churn risk
- **Notifications (Req 7)**: Send retention campaign notifications to at-risk customers
- **Marketing Campaigns (Req 35, 36)**: Retention campaigns targeted at at-risk customers
- **Performance Metrics (Req 21)**: Churn metrics integrated into overall performance dashboard

#### Data Model Details

- **ChurnAnalysis**: ID (UUID), customer_id (FK), last_booking_date (date), days_inactive (integer), churn_risk_score (decimal), churn_risk_level (enum: low/medium/high), churn_reason (enum: price/quality/competition/life_change/other), churn_reason_details (text, nullable), predicted_churn_probability (decimal), analysis_date (date), tenant_id (FK)
- **ChurnReport**: ID (UUID), tenant_id (FK), period (enum: daily/weekly/monthly), period_start (date), period_end (date), churn_rate (decimal), churned_customers (integer), at_risk_customers (integer), churn_reasons (JSON), churn_by_cohort (JSON), seasonal_factors (JSON), tenant_id (FK)
- **RetentionCampaign**: ID (UUID), tenant_id (FK), campaign_name (string), target_segment (string), start_date (date), end_date (date, nullable), campaign_type (enum: discount/loyalty/engagement/other), message_template (text), status (enum: active/paused/completed), created_at (timestamp), tenant_id (FK)
- **RetentionCampaignResult**: ID (UUID), retention_campaign_id (FK), customer_id (FK), campaign_sent_at (timestamp), customer_responded (boolean), response_date (date, nullable), customer_retained (boolean, nullable), retention_check_date (date, nullable), tenant_id (FK)
- **ChurnPrediction**: ID (UUID), customer_id (FK), prediction_date (date), predicted_churn_probability (decimal), confidence_interval (decimal), risk_factors (JSON), actual_churned (boolean, nullable), prediction_accuracy (decimal, nullable), tenant_id (FK)

#### User Workflows

**For Owner Analyzing Churn:**
1. Access churn analytics dashboard
2. View overall churn rate and trends
3. View at-risk customer list
4. Analyze churn reasons
5. Identify high-churn customer segments
6. Compare churn across cohorts
7. Identify seasonal churn patterns
8. Make decisions about retention strategy

**For Marketing Manager Creating Retention Campaign:**
1. Access churn analysis
2. Identify at-risk customer segment
3. Create retention campaign
4. Define campaign message and offer
5. Select target customers
6. Launch campaign
7. Track campaign engagement
8. Measure impact on churn rate

**For Manager Identifying At-Risk Customers:**
1. Access churn analysis
2. View at-risk customer list sorted by churn risk
3. Review customer engagement history
4. Identify reasons for inactivity
5. Contact customer to understand needs
6. Offer incentive or service improvement
7. Track customer response

**For System Predicting Churn:**
1. Analyze customer engagement patterns
2. Calculate churn risk score
3. Identify customers at high risk
4. Generate churn predictions
5. Alert managers to at-risk customers
6. Track prediction accuracy

#### Edge Cases & Constraints

- **New Customers**: Don't flag new customers as at-risk; use different inactivity threshold
- **Seasonal Businesses**: Account for seasonal inactivity; adjust inactivity threshold by season
- **Churned Customers**: Track churned customers separately; analyze reasons for churn
- **Reactivation**: Track customers who return after inactivity; measure reactivation success
- **Multiple Services**: Handle customers who use multiple services; calculate churn risk across all services
- **Acquisition Source**: Track churn by acquisition source; identify sources with highest churn
- **Retention Campaign Fatigue**: Avoid over-contacting customers; limit retention campaign frequency
- **False Positives**: Minimize false positives in churn prediction; validate predictions with customer feedback

#### Performance Requirements

- **Churn Risk Calculation**: Calculate churn risk for all customers within 1 hour
- **Churn Prediction**: Generate churn predictions within 2 minutes
- **At-Risk Customer List**: Generate at-risk customer list within 30 seconds
- **Churn Analytics**: Generate churn analytics within 30 seconds
- **Dashboard Load**: Load churn dashboard within 2 seconds

#### Security Considerations

- **Data Access**: Restrict churn data access to authorized users (Owner, Manager)
- **Audit Trail**: Log all churn analysis and retention campaign activities
- **Customer Privacy**: Don't expose customer personal information in churn reports
- **Sensitive Data**: Handle customer feedback and churn reasons confidentially

#### Compliance Requirements

- **Data Privacy**: Ensure churn analysis doesn't violate customer privacy
- **GDPR**: Support churn data export and deletion for customer data portability
- **Marketing Compliance**: Ensure retention campaigns comply with anti-spam regulations

#### Acceptance Criteria

1. WHEN analyzing churn, THE System SHALL identify customers who haven't booked in configurable period (default 30 days)
2. WHEN tracking churn reasons, THE System SHALL categorize reasons (price, service quality, competition, life changes, other)
3. WHEN identifying at-risk customers, THE System SHALL flag for retention campaigns with risk scores
4. WHEN measuring churn rate, THE System SHALL calculate by cohort, acquisition source, and time period
5. WHEN analyzing churn trends, THE System SHALL identify patterns, seasonality, and high-churn segments
6. WHEN forecasting churn, THE System SHALL predict which customers are likely to churn with confidence intervals
7. WHEN exporting churn data, THE System SHALL provide detailed analysis including at-risk customers and churn reasons

#### Business Value

- Identifies at-risk customers early for proactive retention
- Enables targeted retention campaigns
- Reduces customer loss and improves retention rate
- Improves customer lifetime value
- Identifies churn patterns for strategic planning

#### Dependencies

- Customer profiles (Requirement 5)
- Appointment booking (Requirement 3)
- Notifications (Requirement 7)
- Marketing campaigns (Requirements 35, 36)
- Performance metrics (Requirement 21)

#### Key Data Entities

- ChurnAnalysis (ID, customer_id, last_booking_date, days_inactive, churn_risk_score, churn_reason)
- ChurnReport (ID, tenant_id, period, churn_rate, churned_customers, at_risk_customers, churn_reasons)
- RetentionCampaign (ID, tenant_id, campaign_name, target_segment, campaign_type, status)
- RetentionCampaignResult (ID, retention_campaign_id, customer_id, customer_responded, customer_retained)
- ChurnPrediction (ID, customer_id, prediction_date, predicted_churn_probability, risk_factors)

#### User Roles

- Owner: Views churn analysis and makes retention decisions
- Marketing Manager: Creates and manages retention campaigns
- Manager: Identifies at-risk customers and contacts them
- System: Calculates churn risk and predicts churn

---

### Requirement 56: Peak Hours Analysis

**User Story:** As a manager, I want to analyze peak hours, so that I can optimize staffing and capacity planning.

#### Detailed Description

The peak hours analysis system identifies the busiest times of day, week, and year, enabling managers to optimize staffing levels and capacity planning. By understanding demand patterns, businesses can ensure adequate staff during peak times to minimize wait times and maximize revenue, while reducing staff during slow periods to minimize labor costs.

The system tracks appointment volume by hour, day of week, and season, identifying consistent patterns. It calculates capacity utilization by hour, showing when the business is operating at full capacity and when there is available capacity. The system identifies bottlenecks where demand exceeds capacity, enabling managers to add staff or resources. Forecasting predicts future peak hours based on historical patterns and seasonal factors.

The system provides staffing recommendations based on demand forecasts, enabling managers to schedule the right number of staff at the right times. Analytics track the effectiveness of staffing changes, measuring impact on wait times, customer satisfaction, and revenue. The system supports scenario planning, enabling managers to model the impact of staffing changes before implementing them.

#### Technical Specifications

- **Appointment Volume Tracking**: Track appointment count by hour, day of week, month, year
- **Capacity Utilization Calculation**: Calculate utilization percentage by hour (appointments / capacity)
- **Bottleneck Identification**: Identify hours when demand exceeds capacity
- **Staffing Recommendations**: Recommend staff levels based on demand forecasts
- **Seasonal Analysis**: Identify seasonal patterns in demand
- **Forecasting**: Predict future demand based on historical patterns
- **Scenario Planning**: Model impact of staffing changes
- **Wait Time Tracking**: Track average wait time by hour

#### Business Context

- **Problem Solved**: Optimizes staffing levels; reduces wait times; maximizes revenue; minimizes labor costs
- **ROI**: Reduces labor costs by 10-15% through optimized staffing; increases revenue by 5-10% through reduced wait times
- **Competitive Advantage**: Optimized staffing enables providing better customer experience; enables competing on service quality

#### Integration Points

- **Appointment Booking (Req 3)**: Appointment data used to calculate peak hours
- **Staff Scheduling (Req 4)**: Staffing recommendations inform scheduling
- **Performance Metrics (Req 21)**: Peak hour metrics integrated into performance dashboard
- **Waiting Room (Req 9)**: Wait time data used to identify bottlenecks

#### Data Model Details

- **PeakHourAnalysis**: ID (UUID), tenant_id (FK), date (date), hour (integer), day_of_week (integer), appointment_count (integer), capacity (integer), capacity_utilization (decimal), average_wait_time (integer), service_id (FK, nullable), location_id (FK, nullable), tenant_id (FK)
- **PeakHourReport**: ID (UUID), tenant_id (FK), period (enum: daily/weekly/monthly), period_start (date), period_end (date), peak_hours (JSON array), off_peak_hours (JSON array), staffing_recommendations (JSON), bottleneck_hours (JSON array), average_utilization (decimal), tenant_id (FK)
- **StaffingRecommendation**: ID (UUID), tenant_id (FK), date (date), hour (integer), current_staff_count (integer), recommended_staff_count (integer), demand_forecast (integer), confidence_interval (decimal), tenant_id (FK)
- **CapacityForecast**: ID (UUID), tenant_id (FK), forecast_date (date), hour (integer), forecasted_appointments (integer), confidence_interval (decimal), seasonal_factor (decimal), actual_appointments (integer, nullable), forecast_accuracy (decimal, nullable), tenant_id (FK)

#### User Workflows

**For Manager Analyzing Peak Hours:**
1. Access peak hours analytics dashboard
2. Select time period (day, week, month)
3. View appointment volume by hour
4. View capacity utilization by hour
5. Identify peak hours and off-peak hours
6. Identify bottleneck hours
7. Analyze trends over time
8. Compare to previous periods

**For Manager Optimizing Staffing:**
1. Access peak hours analysis
2. View staffing recommendations
3. Review current staffing schedule
4. Compare current staffing to recommendations
5. Identify understaffed periods
6. Identify overstaffed periods
7. Adjust staffing schedule
8. Track impact on wait times and revenue

**For Manager Planning Capacity:**
1. Access peak hours analysis
2. View capacity utilization trends
3. Identify periods of high utilization
4. Identify periods of low utilization
5. Forecast future capacity needs
6. Plan capacity additions (staff, resources)
7. Model impact of capacity changes
8. Implement capacity changes

**For System Generating Forecasts:**
1. Analyze historical appointment data
2. Identify seasonal patterns
3. Identify day-of-week patterns
4. Identify hour-of-day patterns
5. Generate demand forecasts
6. Calculate staffing recommendations
7. Estimate confidence intervals
8. Compare forecasts to actual demand

#### Edge Cases & Constraints

- **Holidays**: Account for holidays in demand forecasting; use different patterns for holidays
- **Special Events**: Handle special events that drive unusual demand
- **Seasonal Variations**: Account for seasonal patterns (summer vs. winter, etc.)
- **New Services**: Handle new services with limited historical data
- **Staff Absences**: Account for staff absences when calculating capacity
- **Resource Constraints**: Account for resource availability (chairs, treatment rooms, equipment)
- **Multiple Locations**: Handle peak hours analysis for multiple locations
- **Forecast Accuracy**: Validate forecasts against actual demand; refine forecasting model

#### Performance Requirements

- **Peak Hour Calculation**: Calculate peak hours for all hours within 1 hour
- **Staffing Recommendations**: Generate staffing recommendations within 5 minutes
- **Demand Forecasting**: Generate demand forecasts within 2 minutes
- **Analytics Dashboard**: Load analytics dashboard within 2 seconds
- **Report Generation**: Generate peak hours report within 30 seconds

#### Security Considerations

- **Data Access**: Restrict peak hours data access to authorized users (Manager, Owner)
- **Audit Trail**: Log all peak hours analysis and staffing changes
- **Sensitive Data**: Don't expose individual customer information in peak hours reports

#### Compliance Requirements

- **Labor Laws**: Ensure staffing recommendations comply with labor laws (minimum breaks, maximum hours, etc.)
- **Scheduling Fairness**: Ensure staffing schedule is fair to staff (equitable distribution of peak hours)

#### Acceptance Criteria

1. WHEN analyzing peak hours, THE System SHALL identify busiest times by hour, day of week, and service
2. WHEN tracking capacity utilization, THE System SHALL display utilization percentage by hour
3. WHEN identifying bottlenecks, THE System SHALL highlight hours when demand exceeds capacity
4. WHEN planning staffing, THE System SHALL recommend staff levels by hour based on demand forecasts
5. WHEN analyzing trends, THE System SHALL display peak hour patterns by day of week and season
6. WHEN forecasting demand, THE System SHALL predict peak hours based on historical patterns with confidence intervals
7. WHEN exporting analysis, THE System SHALL provide detailed peak hour reports with staffing recommendations

#### Business Value

- Optimizes staffing levels and reduces labor costs
- Improves capacity utilization
- Reduces wait times and improves customer satisfaction
- Increases revenue through optimized staffing
- Enables data-driven capacity planning

#### Dependencies

- Appointment booking (Requirement 3)
- Staff scheduling (Requirement 4)
- Performance metrics (Requirement 21)
- Waiting room (Requirement 9)

#### Key Data Entities

- PeakHourAnalysis (ID, tenant_id, date, hour, appointment_count, capacity, capacity_utilization, average_wait_time)
- PeakHourReport (ID, tenant_id, period, peak_hours, staffing_recommendations, bottleneck_hours)
- StaffingRecommendation (ID, tenant_id, date, hour, current_staff_count, recommended_staff_count)
- CapacityForecast (ID, tenant_id, forecast_date, hour, forecasted_appointments, confidence_interval)

#### User Roles

- Manager: Views peak hours analysis and optimizes staffing
- Owner: Uses for capacity planning
- System: Calculates peak hours and generates forecasts

---

### Requirement 57: Staff Productivity Metrics

**User Story:** As a manager, I want to track staff productivity, so that I can identify top performers and address underperformance.

#### Detailed Description

The staff productivity metrics system tracks how efficiently staff members are working, measuring appointments completed, revenue generated, and customer satisfaction. Productivity metrics enable managers to identify top performers for recognition and advancement, and to identify underperformers who may need additional training or support.

The system calculates multiple productivity metrics including appointments per hour, revenue per hour, customer satisfaction rating, and no-show rate. These metrics are tracked over time, enabling managers to identify trends and measure the impact of training or process improvements. Benchmarking compares individual staff productivity to team averages and industry benchmarks, providing context for performance evaluation.

The system identifies factors that drive high productivity, such as specific services, customer segments, or time periods. This enables managers to replicate high-productivity practices across the team. Performance improvement plans can be created for underperforming staff, with tracking of progress toward improvement goals. The system supports fair and objective performance evaluation based on data rather than subjective impressions.

#### Technical Specifications

- **Appointments Per Hour**: Calculate appointments completed per hour worked
- **Revenue Per Hour**: Calculate revenue generated per hour worked
- **Customer Satisfaction**: Track average customer satisfaction rating
- **No-Show Rate**: Calculate percentage of appointments where customer didn't show
- **Cancellation Rate**: Calculate percentage of appointments cancelled by customer
- **Average Transaction Value**: Calculate average revenue per appointment
- **Benchmarking**: Compare individual productivity to team average and industry benchmarks
- **Trend Analysis**: Track productivity changes over time

#### Business Context

- **Problem Solved**: Enables identifying top performers and underperformers; enables fair performance evaluation; enables measuring impact of training
- **ROI**: Increases overall productivity by 15-20% through identifying and replicating best practices; enables targeted training for underperformers
- **Competitive Advantage**: Data-driven performance management enables building high-performing team; enables competing on service quality

#### Integration Points

- **Appointment Booking (Req 3)**: Appointment data used to calculate productivity metrics
- **Staff Profiles (Req 4)**: Productivity metrics linked to staff profiles
- **Performance Metrics (Req 21)**: Productivity metrics integrated into overall performance dashboard
- **Customer Satisfaction (Req 11)**: Customer satisfaction ratings used in productivity calculation

#### Data Model Details

- **StaffProductivity**: ID (UUID), staff_id (FK), date (date), appointments_count (integer), hours_worked (decimal), revenue (decimal), revenue_per_hour (decimal), appointments_per_hour (decimal), average_customer_satisfaction (decimal), no_show_count (integer), no_show_rate (decimal), cancellation_count (integer), cancellation_rate (decimal), average_transaction_value (decimal), tenant_id (FK)
- **ProductivityReport**: ID (UUID), staff_id (FK), tenant_id (FK), period (enum: daily/weekly/monthly), period_start (date), period_end (date), average_productivity (decimal), productivity_trend (decimal), productivity_vs_team_average (decimal), productivity_vs_benchmark (decimal), top_performing_service (string), top_performing_time_period (string), tenant_id (FK)
- **ProductivityBenchmark**: ID (UUID), tenant_id (FK), role (string), appointments_per_hour_target (decimal), revenue_per_hour_target (decimal), customer_satisfaction_target (decimal), no_show_rate_target (decimal), industry_benchmark (JSON), tenant_id (FK)
- **PerformanceImprovement**: ID (UUID), staff_id (FK), tenant_id (FK), start_date (date), end_date (date, nullable), improvement_goal (text), current_performance (decimal), target_performance (decimal), progress (decimal), status (enum: active/completed/failed), created_by (FK), tenant_id (FK)

#### User Workflows

**For Manager Analyzing Staff Productivity:**
1. Access staff productivity dashboard
2. Select time period (day, week, month)
3. View productivity metrics for each staff member
4. Compare staff productivity to team average
5. Compare staff productivity to benchmarks
6. Identify top performers
7. Identify underperformers
8. Analyze productivity trends

**For Manager Identifying Top Performers:**
1. Access staff productivity metrics
2. Sort staff by productivity
3. Identify top 10% performers
4. Analyze what makes them productive
5. Identify high-performing services and time periods
6. Recognize and reward top performers
7. Share best practices with team

**For Manager Addressing Underperformance:**
1. Access staff productivity metrics
2. Identify underperforming staff
3. Review performance history
4. Analyze reasons for underperformance
5. Meet with staff member to discuss
6. Create performance improvement plan
7. Track progress toward improvement goals
8. Provide additional training or support

**For Manager Measuring Training Impact:**
1. Measure staff productivity before training
2. Conduct training
3. Measure staff productivity after training
4. Compare before and after metrics
5. Calculate training ROI
6. Identify training effectiveness
7. Adjust training program if needed

#### Edge Cases & Constraints

- **New Staff**: Don't compare new staff to benchmarks; use different metrics for ramp-up period
- **Part-Time Staff**: Normalize metrics for part-time staff; compare to part-time benchmarks
- **Specialized Services**: Handle staff who specialize in specific services; compare to service-specific benchmarks
- **Seasonal Variations**: Account for seasonal variations in productivity
- **Staff Absences**: Exclude days when staff is absent from productivity calculations
- **Training Periods**: Exclude training periods from productivity calculations
- **Outliers**: Identify and handle productivity outliers (e.g., unusually high or low days)
- **Fair Comparison**: Ensure productivity comparisons are fair; account for differences in customer mix and service mix

#### Performance Requirements

- **Productivity Calculation**: Calculate productivity metrics for all staff within 1 hour
- **Report Generation**: Generate productivity report within 30 seconds
- **Dashboard Load**: Load productivity dashboard within 2 seconds
- **Trend Analysis**: Calculate productivity trends within 1 minute

#### Security Considerations

- **Data Access**: Restrict productivity data access to authorized users (Manager, Owner)
- **Audit Trail**: Log all productivity data access and performance reviews
- **Fair Evaluation**: Ensure productivity metrics are used fairly; prevent discrimination
- **Sensitive Data**: Don't expose individual customer information in productivity reports

#### Compliance Requirements

- **Labor Laws**: Ensure performance evaluation complies with labor laws
- **Fair Evaluation**: Ensure performance evaluation is fair and non-discriminatory
- **Privacy**: Protect staff privacy; don't expose personal information

#### Acceptance Criteria

1. WHEN calculating productivity, THE System SHALL measure appointments per hour, revenue per hour, and customer satisfaction
2. WHEN comparing staff, THE System SHALL display productivity metrics by staff member with team averages
3. WHEN analyzing trends, THE System SHALL display productivity changes over time with trend indicators
4. WHEN identifying top performers, THE System SHALL highlight high-productivity staff with factors driving performance
5. WHEN addressing underperformance, THE System SHALL flag low-productivity staff and enable creating improvement plans
6. WHEN forecasting productivity, THE System SHALL project future productivity based on trends
7. WHEN exporting metrics, THE System SHALL provide detailed productivity reports with benchmarking

#### Business Value

- Identifies top performers for recognition and advancement
- Addresses underperformance through targeted support
- Improves overall team productivity
- Enables fair and objective performance evaluation
- Supports staff development and training

#### Dependencies

- Appointment booking (Requirement 3)
- Staff profiles (Requirement 4)
- Performance metrics (Requirement 21)
- Customer satisfaction (Requirement 11)

#### Key Data Entities

- StaffProductivity (ID, staff_id, date, appointments_count, hours_worked, revenue, revenue_per_hour, customer_satisfaction)
- ProductivityReport (ID, staff_id, tenant_id, period, average_productivity, productivity_trend, productivity_vs_benchmark)
- ProductivityBenchmark (ID, tenant_id, role, appointments_per_hour_target, revenue_per_hour_target, customer_satisfaction_target)
- PerformanceImprovement (ID, staff_id, tenant_id, improvement_goal, current_performance, target_performance, progress)

#### User Roles

- Manager: Views and analyzes staff productivity
- Owner: Reviews overall team productivity
- System: Calculates productivity metrics and benchmarks

---

### Requirement 58: Inventory Turnover Analysis

**User Story:** As a manager, I want to analyze inventory turnover, so that I can optimize stock levels and reduce waste.

#### Detailed Description

The inventory turnover analysis system measures how quickly inventory is used or sold, providing insights into inventory efficiency and identifying opportunities for optimization. Inventory turnover is a critical metric for service businesses that use products and supplies, as high turnover indicates efficient inventory management while low turnover indicates excess inventory or obsolete products.

The system calculates turnover rate by dividing the cost of goods sold by average inventory value. Turnover is tracked by product, category, and location, enabling managers to identify which products are moving quickly and which are slow-moving. Slow-moving inventory ties up cash and may become obsolete, while fast-moving inventory indicates strong demand. The system identifies products with unusually low or high turnover, enabling managers to investigate and take action.

The system forecasts future inventory needs based on turnover rates and demand forecasts, enabling managers to optimize stock levels. The system identifies products that should be discontinued due to low turnover, and identifies opportunities to increase stock of fast-moving products. Analytics track the effectiveness of inventory optimization efforts, measuring impact on cash flow and waste reduction.

#### Technical Specifications

- **Turnover Rate Calculation**: Calculate turnover rate = cost of goods sold / average inventory value
- **Turnover by Product**: Calculate turnover rate for each product
- **Turnover by Category**: Calculate turnover rate for each product category
- **Turnover by Location**: Calculate turnover rate for each location
- **Slow-Moving Identification**: Identify products with turnover below threshold
- **Fast-Moving Identification**: Identify products with turnover above threshold
- **Inventory Forecasting**: Forecast future inventory needs based on turnover and demand
- **Obsolescence Detection**: Identify products that haven't been used in extended period

#### Business Context

- **Problem Solved**: Optimizes inventory levels; reduces waste and spoilage; improves cash flow; identifies obsolete inventory
- **ROI**: Reduces inventory carrying costs by 20-30%; reduces waste by 15-25%; improves cash flow by 10-15%
- **Competitive Advantage**: Optimized inventory enables lower prices; reduces waste improves sustainability

#### Integration Points

- **Product/Supply Tracking (Req 27)**: Product data used to calculate turnover
- **Stock Level Management (Req 28)**: Inventory levels optimized based on turnover analysis
- **Performance Metrics (Req 21)**: Turnover metrics integrated into performance dashboard
- **Purchasing (Req 29)**: Purchasing decisions informed by turnover analysis

#### Data Model Details

- **InventoryTurnover**: ID (UUID), product_id (FK), location_id (FK, nullable), period (enum: daily/weekly/monthly), period_start (date), period_end (date), units_sold (integer), cost_of_goods_sold (decimal), average_inventory_value (decimal), turnover_rate (decimal), days_inventory_outstanding (integer), tenant_id (FK)
- **TurnoverReport**: ID (UUID), tenant_id (FK), period (enum: daily/weekly/monthly), period_start (date), period_end (date), average_turnover (decimal), slow_moving_items (JSON array), fast_moving_items (JSON array), obsolete_items (JSON array), inventory_optimization_recommendations (JSON), tenant_id (FK)
- **InventoryForecast**: ID (UUID), product_id (FK), location_id (FK, nullable), forecast_date (date), forecasted_units_needed (integer), forecasted_cost (decimal), confidence_interval (decimal), actual_units_used (integer, nullable), forecast_accuracy (decimal, nullable), tenant_id (FK)
- **InventoryOptimization**: ID (UUID), tenant_id (FK), product_id (FK), optimization_type (enum: increase_stock/decrease_stock/discontinue/other), current_stock_level (integer), recommended_stock_level (integer), expected_impact (JSON), status (enum: recommended/implemented/rejected), implemented_date (date, nullable), tenant_id (FK)

#### User Workflows

**For Manager Analyzing Inventory Turnover:**
1. Access inventory turnover dashboard
2. Select time period (week, month, quarter)
3. View average turnover rate
4. View turnover by product
5. View turnover by category
6. Identify slow-moving products
7. Identify fast-moving products
8. Analyze trends over time

**For Manager Optimizing Inventory Levels:**
1. Access inventory turnover analysis
2. Review slow-moving inventory
3. Analyze reasons for low turnover
4. Decide to reduce stock, discontinue, or promote
5. Review fast-moving inventory
6. Analyze demand forecasts
7. Increase stock for fast-moving products
8. Implement inventory changes

**For Manager Reducing Waste:**
1. Access inventory turnover analysis
2. Identify obsolete products (not used in 6+ months)
3. Review expiration dates
4. Identify products at risk of expiration
5. Create plan to use or dispose of products
6. Track waste reduction
7. Measure impact on costs

**For System Forecasting Inventory Needs:**
1. Analyze historical usage patterns
2. Analyze demand forecasts
3. Calculate optimal inventory levels
4. Generate inventory forecasts
5. Identify products needing reorder
6. Generate purchase recommendations
7. Track forecast accuracy

#### Edge Cases & Constraints

- **Seasonal Products**: Account for seasonal variations in turnover
- **New Products**: Don't calculate turnover for new products; use different metrics for ramp-up period
- **Discontinued Products**: Track turnover for discontinued products; identify reasons for discontinuation
- **Expiration Dates**: Account for product expiration dates in turnover calculations
- **Multiple Locations**: Handle turnover analysis for multiple locations
- **Bulk Purchases**: Handle bulk purchases that may skew turnover calculations
- **Waste and Spoilage**: Account for waste and spoilage in turnover calculations
- **Seasonal Stockpiling**: Account for seasonal stockpiling that may temporarily reduce turnover

#### Performance Requirements

- **Turnover Calculation**: Calculate turnover for all products within 1 hour
- **Report Generation**: Generate turnover report within 30 seconds
- **Forecast Calculation**: Generate inventory forecasts within 2 minutes
- **Dashboard Load**: Load turnover dashboard within 2 seconds

#### Security Considerations

- **Data Access**: Restrict turnover data access to authorized users (Manager, Owner)
- **Audit Trail**: Log all inventory changes and optimization decisions
- **Sensitive Data**: Don't expose supplier pricing in turnover reports

#### Compliance Requirements

- **Inventory Accounting**: Ensure turnover calculations comply with accounting standards
- **Waste Tracking**: Track waste and spoilage for compliance and sustainability reporting

#### Acceptance Criteria

1. WHEN calculating turnover, THE System SHALL measure how quickly inventory is used (units sold / average inventory)
2. WHEN analyzing turnover, THE System SHALL display turnover rate by product, category, and location
3. WHEN identifying slow-moving items, THE System SHALL flag products with turnover below threshold
4. WHEN identifying fast-moving items, THE System SHALL highlight products with turnover above threshold
5. WHEN analyzing trends, THE System SHALL display turnover changes over time with trend indicators
6. WHEN forecasting demand, THE System SHALL predict future turnover based on trends and demand forecasts
7. WHEN exporting analysis, THE System SHALL provide detailed turnover reports with optimization recommendations

#### Business Value

- Optimizes inventory levels and reduces carrying costs
- Reduces waste and spoilage
- Improves cash flow through better inventory management
- Identifies obsolete inventory for discontinuation
- Enables data-driven purchasing decisions

#### Dependencies

- Product/supply tracking (Requirement 27)
- Stock level management (Requirement 28)
- Performance metrics (Requirement 21)
- Purchasing (Requirement 29)

#### Key Data Entities

- InventoryTurnover (ID, product_id, location_id, period, units_sold, cost_of_goods_sold, average_inventory_value, turnover_rate)
- TurnoverReport (ID, tenant_id, period, average_turnover, slow_moving_items, fast_moving_items, obsolete_items)
- InventoryForecast (ID, product_id, location_id, forecast_date, forecasted_units_needed, confidence_interval)
- InventoryOptimization (ID, tenant_id, product_id, optimization_type, current_stock_level, recommended_stock_level)

#### User Roles

- Manager: Views turnover analysis and optimizes inventory
- Owner: Reviews inventory optimization impact
- System: Calculates turnover and generates forecasts

---

## PHASE 5 - Advanced Features

### Requirement 59: AI-Powered Recommendations

**User Story:** As a customer, I want personalized service recommendations, so that I can discover new services that match my preferences.

#### Detailed Description

The AI-powered recommendations system uses machine learning to analyze customer behavior and preferences, providing personalized service recommendations that increase service discovery and drive upselling. The system learns from customer booking history, service preferences, customer feedback, and similar customer behavior to generate relevant recommendations.

The system tracks recommendation effectiveness by measuring click-through rates and conversion rates. Recommendations are continuously refined based on feedback, improving accuracy over time. The system supports multiple recommendation strategies including collaborative filtering (recommend services booked by similar customers), content-based filtering (recommend similar services), and popularity-based recommendations (recommend trending services).

The system displays recommendations in multiple contexts including the customer dashboard, booking interface, and email campaigns. Recommendations are personalized to each customer, increasing relevance and engagement. A/B testing enables testing different recommendation algorithms and strategies to optimize conversion rates.

#### Technical Specifications

- **Collaborative Filtering**: Recommend services booked by similar customers
- **Content-Based Filtering**: Recommend services similar to customer's previous bookings
- **Popularity-Based**: Recommend trending services
- **Hybrid Approach**: Combine multiple recommendation strategies
- **Real-Time Personalization**: Generate recommendations in real-time based on current context
- **Feedback Loop**: Learn from customer interactions to improve recommendations
- **A/B Testing**: Test different recommendation algorithms
- **Explainability**: Explain why each service is recommended

#### Business Context

- **Problem Solved**: Increases service discovery; drives upselling and cross-selling; improves customer satisfaction
- **ROI**: Increases average transaction value by 15-25%; increases booking frequency by 10-20%
- **Competitive Advantage**: Personalized recommendations improve customer experience; drive revenue growth

#### Integration Points

- **Customer Profiles (Req 5)**: Customer history and preferences used for recommendations
- **Appointment Booking (Req 3)**: Recommendations displayed during booking
- **Email Marketing (Req 35)**: Recommendations included in marketing emails
- **Performance Metrics (Req 21)**: Recommendation metrics integrated into performance dashboard

#### Data Model Details

- **Recommendation**: ID (UUID), customer_id (FK), service_id (FK), score (decimal), recommendation_type (enum: collaborative/content_based/popularity/hybrid), created_at (timestamp), expires_at (timestamp), tenant_id (FK)
- **RecommendationClick**: ID (UUID), recommendation_id (FK), clicked_at (timestamp), context (enum: dashboard/booking/email/other), tenant_id (FK)
- **RecommendationConversion**: ID (UUID), recommendation_id (FK), appointment_id (FK), converted_at (timestamp), revenue (decimal), tenant_id (FK)
- **RecommendationAnalytics**: ID (UUID), tenant_id (FK), date (date), recommendations_generated (integer), click_through_rate (decimal), conversion_rate (decimal), average_revenue_per_recommendation (decimal), tenant_id (FK)
- **RecommendationModel**: ID (UUID), tenant_id (FK), model_type (enum: collaborative/content_based/popularity/hybrid), version (integer), accuracy (decimal), last_trained (timestamp), training_data_size (integer), tenant_id (FK)

#### User Workflows

**For Customer Viewing Recommendations:**
1. Log into customer dashboard
2. View recommended services
3. Click on recommended service to learn more
4. Book recommended service or continue browsing
5. Provide feedback on recommendation

**For System Generating Recommendations:**
1. Retrieve customer booking history
2. Identify similar customers
3. Identify services booked by similar customers
4. Score recommendations based on relevance
5. Filter out services already booked
6. Rank recommendations by score
7. Display top recommendations

**For Manager Analyzing Recommendation Performance:**
1. Access recommendation analytics
2. View click-through rates
3. View conversion rates
4. View revenue impact
5. Identify high-performing recommendations
6. Identify low-performing recommendations
7. Adjust recommendation strategy

**For System Training Recommendation Model:**
1. Collect customer interaction data
2. Analyze booking patterns
3. Train machine learning model
4. Evaluate model accuracy
5. Deploy improved model
6. Monitor model performance
7. Retrain periodically

#### Edge Cases & Constraints

- **New Customers**: Limited booking history; use popularity-based recommendations initially
- **New Services**: Limited booking data; use content-based recommendations
- **Cold Start Problem**: Handle customers with no booking history
- **Recommendation Diversity**: Avoid recommending only similar services; include diverse recommendations
- **Seasonal Services**: Account for seasonal availability in recommendations
- **Recommendation Freshness**: Update recommendations regularly; avoid stale recommendations
- **Privacy**: Don't expose customer data in recommendations; maintain privacy
- **Bias**: Avoid biased recommendations; ensure fair representation of services

#### Performance Requirements

- **Recommendation Generation**: Generate recommendations within 500ms
- **Real-Time Personalization**: Personalize recommendations in real-time
- **Model Training**: Train recommendation model within 1 hour
- **Analytics Calculation**: Calculate recommendation analytics within 30 seconds

#### Security Considerations

- **Data Privacy**: Don't expose customer personal information in recommendations
- **Audit Trail**: Log all recommendations and customer interactions
- **Model Transparency**: Explain why each service is recommended

#### Compliance Requirements

- **GDPR**: Support recommendation data export and deletion
- **Fairness**: Ensure recommendations are fair and non-discriminatory

#### Acceptance Criteria

1. WHEN a customer views the app, THE System SHALL display recommended services based on booking history
2. WHEN analyzing customer behavior, THE System SHALL identify service preferences and patterns
3. WHEN recommending services, THE System SHALL consider customer history, preferences, and similar customers
4. WHEN a customer books recommended service, THE System SHALL track recommendation effectiveness
5. WHEN analyzing recommendations, THE System SHALL display click-through and conversion rates
6. WHEN improving recommendations, THE System SHALL use machine learning to refine algorithm
7. WHEN exporting recommendations, THE System SHALL provide recommendation performance data

#### Business Value

- Increases service discovery and customer engagement
- Drives upselling and cross-selling
- Improves customer satisfaction through personalization
- Increases average transaction value
- Enables data-driven service strategy

#### Dependencies

- Customer profiles (Requirement 5)
- Appointment booking (Requirement 3)
- Email marketing (Requirement 35)
- Performance metrics (Requirement 21)

#### Key Data Entities

- Recommendation (ID, customer_id, service_id, score, recommendation_type, created_at)
- RecommendationClick (ID, recommendation_id, clicked_at, context)
- RecommendationConversion (ID, recommendation_id, appointment_id, converted_at, revenue)
- RecommendationAnalytics (ID, tenant_id, date, recommendations_generated, click_through_rate, conversion_rate)
- RecommendationModel (ID, tenant_id, model_type, version, accuracy, last_trained)

#### User Roles

- Customer: Receives and interacts with recommendations
- Manager: Analyzes recommendation performance
- System: Generates recommendations and trains models

---

### Requirement 60: Automated Marketing Campaigns

**User Story:** As a marketing manager, I want to automate marketing campaigns, so that I can nurture customers with minimal manual effort.

#### Detailed Description

The automated marketing campaigns system enables marketing managers to create sophisticated customer nurturing campaigns that trigger automatically based on customer behavior. Campaigns can be triggered by events (first appointment, appointment completion, no booking in 30 days) or by customer attributes (new customer, high-value customer, at-risk customer).

The system supports multi-step campaigns where customers receive a series of messages over time. Each step can include email, SMS, or push notifications. Campaigns can include personalized offers, educational content, or service recommendations. A/B testing enables testing different messages and offers to optimize engagement and conversion.

The system tracks campaign performance including open rates, click rates, and conversion rates. Analytics identify which campaigns are most effective, enabling optimization of future campaigns. Automated campaign optimization adjusts messaging and timing based on performance data. The system prevents campaign fatigue by limiting the number of campaigns a customer receives.

#### Technical Specifications

- **Trigger-Based Campaigns**: Trigger campaigns based on events or customer attributes
- **Multi-Step Campaigns**: Support campaigns with multiple steps over time
- **Personalization**: Personalize messages with customer name, history, and preferences
- **A/B Testing**: Test different messages, offers, and timing
- **Multi-Channel**: Support email, SMS, and push notifications
- **Campaign Scheduling**: Schedule campaigns for optimal send times
- **Performance Tracking**: Track open rates, click rates, and conversion rates
- **Campaign Optimization**: Automatically optimize campaigns based on performance

#### Business Context

- **Problem Solved**: Automates customer nurturing; increases customer engagement; drives repeat bookings
- **ROI**: Increases customer engagement by 30-50%; increases repeat bookings by 20-30%; reduces manual marketing work by 70%
- **Competitive Advantage**: Automated campaigns enable competing on customer engagement; enables personalized communication at scale

#### Integration Points

- **Email Marketing (Req 35)**: Campaigns sent via email provider
- **Customer Segmentation (Req 33)**: Campaigns targeted at specific customer segments
- **Customer Profiles (Req 5)**: Customer data used for personalization
- **Notifications (Req 7)**: Campaign messages sent via notification system
- **Performance Metrics (Req 21)**: Campaign metrics integrated into performance dashboard

#### Data Model Details

- **AutomatedCampaign**: ID (UUID), tenant_id (FK), name (string), description (text), trigger_type (enum: event/attribute), trigger_condition (JSON), message_template (text), channels (JSON array), status (enum: active/paused/completed), created_at (timestamp), created_by (FK), tenant_id (FK)
- **CampaignStep**: ID (UUID), campaign_id (FK), step_number (integer), delay_days (integer), message_template (text), channels (JSON array), offer (JSON, nullable), tenant_id (FK)
- **CampaignExecution**: ID (UUID), campaign_id (FK), customer_id (FK), step_number (integer), sent_at (timestamp), channel (enum: email/sms/push), opened_at (timestamp, nullable), clicked_at (timestamp, nullable), converted_at (timestamp, nullable), revenue (decimal, nullable), tenant_id (FK)
- **CampaignAnalytics**: ID (UUID), campaign_id (FK), tenant_id (FK), total_sent (integer), open_rate (decimal), click_rate (decimal), conversion_rate (decimal), revenue (decimal), roi (decimal), tenant_id (FK)
- **CampaignABTest**: ID (UUID), campaign_id (FK), variant_a_template (text), variant_b_template (text), winner (enum: a/b/tie), confidence (decimal), tenant_id (FK)

#### User Workflows

**For Marketing Manager Creating Campaign:**
1. Access campaign builder
2. Define campaign trigger (event or attribute)
3. Create campaign message
4. Select channels (email, SMS, push)
5. Define campaign steps and timing
6. Add personalization tokens
7. Set up A/B test (optional)
8. Review and launch campaign

**For System Executing Campaign:**
1. Monitor for campaign triggers
2. When trigger occurs, identify matching customers
3. Send first campaign message
4. Wait for configured delay
5. Send next campaign message
6. Track customer interactions
7. Update campaign analytics
8. Optimize campaign based on performance

**For Marketing Manager Analyzing Campaign:**
1. Access campaign analytics
2. View campaign performance metrics
3. View open rates and click rates
4. View conversion rates and revenue
5. Compare to previous campaigns
6. Identify high-performing campaigns
7. Identify low-performing campaigns
8. Optimize future campaigns

**For System Optimizing Campaign:**
1. Analyze campaign performance
2. Identify underperforming messages
3. Test alternative messages
4. Identify optimal send times
5. Adjust campaign based on performance
6. Monitor impact of changes
7. Continue optimization

#### Edge Cases & Constraints

- **Campaign Fatigue**: Limit number of campaigns per customer; prevent over-contacting
- **Unsubscribe**: Respect customer unsubscribe preferences; remove from campaigns
- **Timing**: Handle timezone differences; send at optimal time for each customer
- **Personalization**: Handle missing customer data gracefully; use defaults
- **Duplicate Triggers**: Prevent duplicate campaign executions for same trigger
- **Campaign Conflicts**: Handle overlapping campaigns; prioritize based on rules
- **Compliance**: Ensure campaigns comply with anti-spam regulations
- **Performance**: Handle large-scale campaign execution efficiently

#### Performance Requirements

- **Campaign Trigger Detection**: Detect triggers within 5 minutes
- **Campaign Execution**: Send campaign message within 1 minute of trigger
- **Analytics Calculation**: Calculate campaign analytics within 30 seconds
- **Campaign Optimization**: Optimize campaigns within 1 hour

#### Security Considerations

- **Data Privacy**: Don't expose customer personal information in campaigns
- **Audit Trail**: Log all campaign executions and customer interactions
- **Compliance**: Ensure campaigns comply with anti-spam regulations

#### Compliance Requirements

- **CAN-SPAM**: Include unsubscribe link in all emails
- **GDPR**: Respect customer preferences and privacy
- **Anti-Spam**: Comply with anti-spam regulations

#### Acceptance Criteria

1. WHEN creating campaign, THE System SHALL define triggers (e.g., first appointment, no booking in 30 days)
2. WHEN trigger is met, THE System SHALL automatically send campaign to matching customers
3. WHEN tracking campaign, THE System SHALL measure engagement and conversion
4. WHEN optimizing campaign, THE System SHALL test variations and recommend improvements
5. WHEN analyzing campaign, THE System SHALL display ROI and customer acquisition cost
6. WHEN managing campaigns, THE System SHALL allow pausing or stopping campaigns
7. WHEN exporting campaign data, THE System SHALL provide detailed performance reports

#### Business Value

- Automates customer nurturing and engagement
- Increases customer engagement and repeat bookings
- Reduces manual marketing work
- Enables personalized communication at scale
- Improves customer lifetime value

#### Dependencies

- Email marketing automation (Requirement 35)
- Customer segmentation (Requirement 33)
- Customer profiles (Requirement 5)
- Notifications (Requirement 7)
- Performance metrics (Requirement 21)

#### Key Data Entities

- AutomatedCampaign (ID, tenant_id, name, trigger_type, trigger_condition, message_template, status)
- CampaignStep (ID, campaign_id, step_number, delay_days, message_template, channels, offer)
- CampaignExecution (ID, campaign_id, customer_id, step_number, sent_at, channel, opened_at, clicked_at, converted_at)
- CampaignAnalytics (ID, campaign_id, tenant_id, total_sent, open_rate, click_rate, conversion_rate, roi)
- CampaignABTest (ID, campaign_id, variant_a_template, variant_b_template, winner)

#### User Roles

- Marketing Manager: Creates and manages campaigns
- System: Executes campaigns and optimizes performance
- Owner: Views campaign analytics

---

### Requirement 61: Customer Self-Service Portal

**User Story:** As a customer, I want a self-service portal, so that I can manage my account without contacting support.

#### Detailed Description

The customer self-service portal provides customers with a comprehensive interface to manage their account, appointments, and payments without requiring support staff intervention. The portal reduces support overhead by enabling customers to handle common tasks independently, improving customer satisfaction through 24/7 availability.

The portal displays a personalized dashboard showing upcoming appointments, appointment history, and account information. Customers can reschedule or cancel appointments, update their profile information, manage payment methods, and view invoices. The portal includes a support ticket system enabling customers to submit questions or issues, with automated responses for common questions.

The portal provides transparency into account status, including appointment history, payment history, and loyalty program status. Customers can manage communication preferences, controlling which notifications they receive. The portal supports multiple languages and is fully responsive for mobile access.

#### Technical Specifications

- **Customer Dashboard**: Display key account information and upcoming appointments
- **Appointment Management**: Allow rescheduling and cancellation with configurable policies
- **Profile Management**: Allow updating contact information and preferences
- **Payment Management**: Display invoices and payment history; allow making payments
- **Support Tickets**: Allow submitting support requests with automated responses
- **Communication Preferences**: Allow managing notification preferences
- **Multi-Language**: Support multiple languages
- **Mobile Responsive**: Fully responsive design for mobile access

#### Business Context

- **Problem Solved**: Reduces support overhead; improves customer satisfaction; enables 24/7 self-service
- **ROI**: Reduces support costs by 40-50%; improves customer satisfaction by 20-30%
- **Competitive Advantage**: Modern self-service experience expected by customers; differentiates from competitors

#### Integration Points

- **Customer Profiles (Req 5)**: Customer data displayed and updated in portal
- **Appointment Booking (Req 3)**: Appointment management integrated into portal
- **Billing & Payment (Req 6)**: Payment and invoice management in portal
- **Notifications (Req 7)**: Communication preferences managed in portal

#### Data Model Details

- **CustomerPortal**: ID (UUID), customer_id (FK), last_login (timestamp), preferences (JSON), language (string), timezone (string), tenant_id (FK)
- **SupportTicket**: ID (UUID), customer_id (FK), subject (string), description (text), status (enum: open/in_progress/resolved/closed), priority (enum: low/medium/high), created_at (timestamp), updated_at (timestamp), resolved_at (timestamp, nullable), assigned_to (FK, nullable), tenant_id (FK)
- **TicketResponse**: ID (UUID), ticket_id (FK), responder_id (FK), response_text (text), is_automated (boolean), created_at (timestamp), tenant_id (FK)
- **CommunicationPreference**: ID (UUID), customer_id (FK), notification_type (enum: appointment_reminder/promotional/transactional/other), channel (enum: email/sms/push), enabled (boolean), tenant_id (FK)

#### User Workflows

**For Customer Accessing Portal:**
1. Log into customer portal
2. View personalized dashboard
3. See upcoming appointments
4. See account balance and payment status
5. Access appointment history
6. Access payment history
7. Manage profile and preferences

**For Customer Managing Appointments:**
1. View upcoming appointments
2. Click on appointment to view details
3. Reschedule appointment (if allowed)
4. Cancel appointment (if allowed)
5. Receive confirmation

**For Customer Managing Profile:**
1. Access profile settings
2. Update contact information
3. Update preferences
4. Manage communication preferences
5. Save changes

**For Customer Submitting Support Request:**
1. Click "Submit Support Request"
2. Select issue category
3. Enter description
4. Receive automated response
5. Track ticket status
6. Receive response from support team

#### Edge Cases & Constraints

- **Cancellation Policies**: Enforce cancellation policies; prevent cancellations outside allowed window
- **Rescheduling Limits**: Limit number of reschedules; prevent abuse
- **Payment Methods**: Support multiple payment methods; handle payment failures
- **Sensitive Data**: Don't expose sensitive information (full credit card numbers, etc.)
- **Accessibility**: Ensure portal is accessible (WCAG 2.1 AA compliant)
- **Performance**: Handle high concurrent users efficiently
- **Mobile**: Ensure mobile experience is smooth and responsive

#### Performance Requirements

- **Portal Load**: Load portal within 2 seconds
- **Appointment Update**: Update appointment within 1 second
- **Profile Update**: Update profile within 1 second
- **Support Ticket Submission**: Submit ticket within 1 second

#### Security Considerations

- **Authentication**: Require strong authentication; support MFA
- **Data Privacy**: Don't expose sensitive information
- **Audit Trail**: Log all portal activities
- **Payment Security**: Use tokenization for payment methods; never store full credit card numbers

#### Compliance Requirements

- **GDPR**: Support data export and deletion
- **Accessibility**: Ensure portal is WCAG 2.1 AA compliant
- **PCI-DSS**: If handling payments, comply with PCI-DSS requirements

#### Acceptance Criteria

1. WHEN logging into portal, THE System SHALL display customer dashboard with key information
2. WHEN managing profile, THE System SHALL allow updating contact info and preferences
3. WHEN viewing appointments, THE System SHALL display upcoming and past appointments
4. WHEN managing appointments, THE System SHALL allow rescheduling and cancellation with policies
5. WHEN viewing invoices, THE System SHALL display invoices and payment history
6. WHEN making payments, THE System SHALL allow paying outstanding balance securely
7. WHEN requesting support, THE System SHALL allow submitting support tickets with tracking

#### Business Value

- Reduces support overhead and costs
- Improves customer satisfaction through 24/7 self-service
- Enables customers to manage accounts independently
- Reduces support staff workload
- Improves customer retention

#### Dependencies

- Customer profiles (Requirement 5)
- Appointment booking (Requirement 3)
- Billing & payment processing (Requirement 6)
- Notifications (Requirement 7)

#### Key Data Entities

- CustomerPortal (ID, customer_id, last_login, preferences, language, timezone)
- SupportTicket (ID, customer_id, subject, description, status, priority, created_at)
- TicketResponse (ID, ticket_id, responder_id, response_text, is_automated, created_at)
- CommunicationPreference (ID, customer_id, notification_type, channel, enabled)

#### User Roles

- Customer: Uses self-service portal
- Support: Manages support tickets
- System: Provides portal functionality

---

### Requirement 62: Mobile App Support (iOS/Android)

**User Story:** As a customer, I want to book appointments on mobile, so that I can manage my schedule on the go.

#### Detailed Description

The mobile app provides iOS and Android versions of the platform, enabling customers to book appointments, manage their account, and receive notifications on their mobile devices. The mobile app provides a streamlined interface optimized for mobile screens, with touch-friendly controls and fast loading times.

The app supports offline functionality, caching appointment data and allowing customers to browse services and staff even without internet connectivity. When connectivity is restored, the app automatically syncs data with the server. Push notifications alert customers to appointment reminders, special offers, and other important updates.

The app integrates with device features including camera (for profile photos), calendar (for syncing appointments), and location services (for finding nearby locations). The app supports biometric authentication (fingerprint, face recognition) for quick and secure login.

#### Technical Specifications

- **iOS App**: Native iOS app using Swift; supports iOS 13+
- **Android App**: Native Android app using Kotlin; supports Android 8+
- **Offline Functionality**: Cache data locally; sync when online
- **Push Notifications**: Send push notifications for reminders and updates
- **Biometric Authentication**: Support fingerprint and face recognition
- **Device Integration**: Integrate with camera, calendar, location services
- **Performance**: Optimize for mobile performance; minimize data usage
- **Accessibility**: Ensure app is accessible (WCAG 2.1 AA compliant)

#### Business Context

- **Problem Solved**: Enables mobile booking; increases appointment bookings; improves customer convenience
- **ROI**: Increases appointment bookings by 20-30%; improves customer engagement by 30-40%
- **Competitive Advantage**: Mobile app expected by modern customers; enables competing on convenience

#### Integration Points

- **Appointment Booking (Req 3)**: Booking functionality in mobile app
- **Customer Profiles (Req 5)**: Customer data synced to mobile app
- **Notifications (Req 7)**: Push notifications sent to mobile app
- **Billing & Payment (Req 6)**: Payment functionality in mobile app

#### Data Model Details

- **MobileDevice**: ID (UUID), customer_id (FK), platform (enum: ios/android), device_id (string), app_version (string), os_version (string), last_sync (timestamp), push_token (string), enabled (boolean), tenant_id (FK)
- **PushNotification**: ID (UUID), device_id (FK), title (string), body (text), action_url (string, nullable), sent_at (timestamp), delivered_at (timestamp, nullable), opened_at (timestamp, nullable), tenant_id (FK)
- **AppAnalytics**: ID (UUID), tenant_id (FK), date (date), active_users (integer), sessions (integer), bookings (integer), average_session_duration (integer), crash_rate (decimal), tenant_id (FK)

#### User Workflows

**For Customer Downloading App:**
1. Search for app in App Store or Google Play
2. Download and install app
3. Launch app
4. Create account or log in
5. Grant permissions (notifications, location, etc.)
6. View personalized dashboard

**For Customer Booking via App:**
1. Open app
2. Browse services
3. Select service and staff
4. Select date and time
5. Confirm booking
6. Receive confirmation notification

**For Customer Receiving Notifications:**
1. Receive push notification
2. Tap notification to open app
3. View notification details
4. Take action (e.g., reschedule appointment)

**For System Syncing Data:**
1. Detect app online
2. Sync local changes to server
3. Download server updates
4. Update local cache
5. Notify app of sync completion

#### Edge Cases & Constraints

- **Offline Functionality**: Handle offline mode gracefully; sync when online
- **Push Notification Delivery**: Handle failed push notifications; retry delivery
- **Device Storage**: Minimize app size; cache only necessary data
- **Battery Usage**: Optimize for battery usage; minimize background activity
- **Network Connectivity**: Handle slow or unreliable connections
- **App Updates**: Support app updates without losing user data
- **Permissions**: Handle permission denials gracefully

#### Performance Requirements

- **App Launch**: Launch app within 2 seconds
- **Booking**: Complete booking within 3 seconds
- **Data Sync**: Sync data within 5 seconds
- **Push Notification**: Deliver notification within 1 minute
- **App Size**: Keep app size under 100MB

#### Security Considerations

- **Authentication**: Require strong authentication; support biometric authentication
- **Data Encryption**: Encrypt data in transit and at rest
- **Secure Storage**: Store sensitive data securely on device
- **API Security**: Use secure API communication (HTTPS, API keys)
- **Audit Trail**: Log all app activities

#### Compliance Requirements

- **App Store Policies**: Comply with App Store and Google Play policies
- **Privacy**: Comply with privacy regulations (GDPR, CCPA)
- **Accessibility**: Ensure app is accessible (WCAG 2.1 AA compliant)

#### Acceptance Criteria

1. WHEN downloading app, THE System SHALL provide iOS and Android versions
2. WHEN logging in, THE System SHALL authenticate and sync customer data
3. WHEN browsing services, THE System SHALL display available services and staff
4. WHEN booking appointment, THE System SHALL allow selecting time and staff
5. WHEN managing appointments, THE System SHALL allow rescheduling and cancellation
6. WHEN receiving notifications, THE System SHALL send push notifications for reminders
7. WHEN using offline, THE System SHALL cache data and sync when online

#### Business Value

- Increases appointment bookings through mobile convenience
- Improves customer engagement through push notifications
- Enables 24/7 access to booking and account management
- Improves customer satisfaction
- Increases customer retention

#### Dependencies

- Appointment booking (Requirement 3)
- Customer profiles (Requirement 5)
- Notifications (Requirement 7)
- Billing & payment processing (Requirement 6)

#### Key Data Entities

- MobileDevice (ID, customer_id, platform, device_id, app_version, os_version, last_sync, push_token)
- PushNotification (ID, device_id, title, body, action_url, sent_at, delivered_at, opened_at)
- AppAnalytics (ID, tenant_id, date, active_users, sessions, bookings, average_session_duration)

#### User Roles

- Customer: Uses mobile app
- System: Sends push notifications and syncs data

---

### Requirement 63: Video Consultations

**User Story:** As a staff member, I want to conduct video consultations, so that I can provide remote services and consultations.

#### Detailed Description

The video consultations feature enables staff members to conduct remote consultations and services via video call. This expands service offerings to include remote consultations, enabling businesses to serve customers who cannot visit in person. Video consultations are scheduled like regular appointments, with customers receiving video meeting links.

The system integrates with video conferencing platforms (Zoom, Google Meet, Microsoft Teams) to provide reliable video calling. Sessions can be recorded with customer consent, enabling staff to review sessions and provide follow-up recommendations. The system automatically generates invoices for video consultations, with pricing configured per service.

Analytics track video consultation usage, duration, and customer satisfaction. The system identifies opportunities to expand video consultation offerings based on demand. Integration with appointment booking enables customers to select video consultation as an option when booking.

#### Technical Specifications

- **Video Conferencing Integration**: Integrate with Zoom, Google Meet, Microsoft Teams
- **Meeting Link Generation**: Generate unique meeting links for each consultation
- **Session Recording**: Record sessions with customer consent
- **Automatic Invoicing**: Generate invoices for completed consultations
- **Session Analytics**: Track session duration, participant count, and engagement
- **Customer Satisfaction**: Collect feedback after consultations
- **Scheduling**: Integrate with appointment booking system
- **Notifications**: Send meeting links and reminders to participants

#### Business Context

- **Problem Solved**: Enables remote services; expands service offerings; increases accessibility
- **ROI**: Increases service offerings by 20-30%; enables serving remote customers; increases revenue
- **Competitive Advantage**: Remote services expected by modern customers; enables competing on accessibility

#### Integration Points

- **Appointment Booking (Req 3)**: Video consultations scheduled as appointments
- **Billing & Payment (Req 6)**: Invoices generated for consultations
- **Notifications (Req 7)**: Meeting links and reminders sent via notifications
- **Performance Metrics (Req 21)**: Consultation metrics integrated into performance dashboard

#### Data Model Details

- **VideoConsultation**: ID (UUID), appointment_id (FK), meeting_link (string), recording_url (string, nullable), duration_minutes (integer), status (enum: scheduled/in_progress/completed/cancelled), recording_consent (boolean), created_at (timestamp), started_at (timestamp, nullable), ended_at (timestamp, nullable), tenant_id (FK)
- **ConsultationParticipant**: ID (UUID), consultation_id (FK), user_id (FK), role (enum: staff/customer), joined_at (timestamp, nullable), left_at (timestamp, nullable), tenant_id (FK)
- **ConsultationAnalytics**: ID (UUID), tenant_id (FK), date (date), consultation_count (integer), average_duration (integer), customer_satisfaction (decimal), no_show_rate (decimal), tenant_id (FK)
- **ConsultationFeedback**: ID (UUID), consultation_id (FK), customer_id (FK), rating (integer), comments (text, nullable), submitted_at (timestamp), tenant_id (FK)

#### User Workflows

**For Staff Scheduling Video Consultation:**
1. Create appointment for video consultation
2. Select video consultation service type
3. System generates meeting link
4. Send meeting link to customer
5. Receive confirmation from customer

**For Customer Joining Consultation:**
1. Receive meeting link via email or SMS
2. Click link to join meeting
3. Join video call with staff member
4. Conduct consultation
5. Receive follow-up recommendations

**For Staff Conducting Consultation:**
1. Log into meeting at scheduled time
2. Wait for customer to join
3. Conduct consultation
4. Record session (if consented)
5. End meeting
6. System generates invoice

**For System Processing Consultation:**
1. Generate meeting link
2. Send link to participants
3. Track session duration
4. Record session (if consented)
5. Generate invoice
6. Collect feedback
7. Update analytics

#### Edge Cases & Constraints

- **No-Shows**: Handle customers who don't join meeting; track no-show rate
- **Technical Issues**: Handle connection failures; provide support
- **Recording Consent**: Require explicit consent before recording
- **Privacy**: Ensure privacy during consultations; secure recording storage
- **Time Zones**: Handle time zone differences; send reminders in customer's timezone
- **Multiple Participants**: Support consultations with multiple staff or customers
- **Recording Storage**: Securely store recordings; comply with data retention policies

#### Performance Requirements

- **Meeting Link Generation**: Generate link within 1 second
- **Meeting Start**: Start meeting within 5 seconds of joining
- **Recording**: Start recording within 2 seconds
- **Invoice Generation**: Generate invoice within 1 minute of consultation end

#### Security Considerations

- **Meeting Security**: Use secure meeting links; require authentication
- **Recording Security**: Encrypt recordings; store securely
- **Privacy**: Ensure privacy during consultations
- **Audit Trail**: Log all consultations and recordings

#### Compliance Requirements

- **Recording Consent**: Require explicit consent before recording
- **Privacy**: Comply with privacy regulations (GDPR, CCPA)
- **Data Retention**: Comply with data retention policies

#### Acceptance Criteria

1. WHEN scheduling video consultation, THE System SHALL create video meeting link
2. WHEN starting consultation, THE System SHALL initiate video call with customer
3. WHEN conducting consultation, THE System SHALL record session if customer consents
4. WHEN ending consultation, THE System SHALL save recording and generate invoice
5. WHEN tracking consultations, THE System SHALL display consultation history
6. WHEN analyzing consultations, THE System SHALL display usage and customer satisfaction
7. WHEN exporting consultation data, THE System SHALL provide consultation reports

#### Business Value

- Enables remote services and consultations
- Expands service offerings
- Increases accessibility for remote customers
- Increases revenue through new service offerings
- Improves customer satisfaction

#### Dependencies

- Appointment booking (Requirement 3)
- Billing & payment processing (Requirement 6)
- Notifications (Requirement 7)
- Performance metrics (Requirement 21)

#### Key Data Entities

- VideoConsultation (ID, appointment_id, meeting_link, recording_url, duration_minutes, status, recording_consent)
- ConsultationParticipant (ID, consultation_id, user_id, role, joined_at, left_at)
- ConsultationAnalytics (ID, tenant_id, date, consultation_count, average_duration, customer_satisfaction)
- ConsultationFeedback (ID, consultation_id, customer_id, rating, comments, submitted_at)

#### User Roles

- Staff: Conducts consultations
- Customer: Participates in consultations
- System: Manages consultations and recordings

---

### Requirement 64: Waitlist Management with Auto-Notifications

**User Story:** As a customer, I want to join a waitlist, so that I can get notified when appointments become available.

#### Detailed Description

The waitlist management system captures demand for fully booked services, enabling businesses to identify capacity gaps and notify customers when appointments become available. When a customer attempts to book an appointment but no slots are available, they can join a waitlist. When an appointment becomes available (through cancellation or rescheduling), the system automatically notifies waitlist customers in order.

The system tracks waitlist position, enabling customers to see their position in the queue. Customers can set preferences for which times they prefer, enabling the system to match them with suitable available slots. The system tracks waitlist conversion rates, identifying which services have high demand and which times are most popular.

Analytics identify capacity gaps, enabling managers to add staff or resources to meet demand. The system supports automatic booking, where customers can authorize the system to book the first available slot matching their preferences. Waitlist data informs capacity planning and staffing decisions.

#### Technical Specifications

- **Waitlist Queueing**: Maintain queue of customers waiting for appointments
- **Position Tracking**: Track customer position in queue
- **Preference Matching**: Match available slots to customer preferences
- **Auto-Notification**: Automatically notify customers when slots become available
- **Auto-Booking**: Automatically book appointments if customer authorizes
- **Conversion Tracking**: Track waitlist conversion rates
- **Capacity Analysis**: Identify capacity gaps based on waitlist data
- **Expiration**: Remove customers from waitlist after configurable period

#### Business Context

- **Problem Solved**: Captures demand for fully booked services; increases booking conversion; improves customer satisfaction
- **ROI**: Increases bookings by 10-15% through waitlist conversions; identifies capacity gaps for expansion
- **Competitive Advantage**: Waitlist management improves customer experience; enables data-driven capacity planning

#### Integration Points

- **Appointment Booking (Req 3)**: Waitlist integrated into booking system
- **Notifications (Req 7)**: Waitlist notifications sent via email/SMS/push
- **Performance Metrics (Req 21)**: Waitlist metrics integrated into performance dashboard
- **Staff Scheduling (Req 4)**: Waitlist data informs staffing decisions

#### Data Model Details

- **Waitlist**: ID (UUID), service_id (FK), staff_id (FK, nullable), date (date, nullable), customer_id (FK), position (integer), preferred_times (JSON array, nullable), auto_book_enabled (boolean), created_at (timestamp), expires_at (timestamp), tenant_id (FK)
- **WaitlistNotification**: ID (UUID), waitlist_id (FK), notification_sent_at (timestamp), notification_method (enum: email/sms/push), available_slot (JSON), customer_response (enum: accepted/declined/no_response, nullable), response_date (date, nullable), tenant_id (FK)
- **WaitlistAnalytics**: ID (UUID), tenant_id (FK), date (date), waitlist_size (integer), conversion_rate (decimal), average_wait_time (integer), popular_services (JSON array), popular_times (JSON array), tenant_id (FK)

#### User Workflows

**For Customer Joining Waitlist:**
1. Attempt to book appointment
2. See "No availability" message
3. Click "Join Waitlist"
4. Set preferences (optional)
5. Authorize auto-booking (optional)
6. Receive confirmation
7. Receive notification when slot available

**For Customer Responding to Notification:**
1. Receive notification of available slot
2. Review available time
3. Accept or decline
4. If accepted, appointment is booked
5. If declined, remain on waitlist

**For System Managing Waitlist:**
1. Monitor for appointment cancellations
2. When slot becomes available, identify matching waitlist customers
3. Send notification to first customer
4. Wait for response (configurable timeout)
5. If accepted, book appointment and remove from waitlist
6. If declined or no response, notify next customer
7. Update waitlist position for remaining customers

**For Manager Analyzing Waitlist:**
1. Access waitlist analytics
2. View waitlist size and trends
3. Identify popular services and times
4. Analyze conversion rates
5. Identify capacity gaps
6. Plan capacity additions

#### Edge Cases & Constraints

- **Waitlist Expiration**: Remove customers from waitlist after configurable period (e.g., 30 days)
- **Multiple Preferences**: Handle customers with multiple time preferences
- **Cancellation**: Allow customers to cancel waitlist request
- **Position Changes**: Update positions when customers ahead cancel
- **Notification Failures**: Handle failed notifications; retry delivery
- **Auto-Booking**: Handle auto-booking failures; notify customer
- **Overbooking**: Prevent overbooking when multiple customers accept same slot
- **Fairness**: Ensure fair queue management; prevent queue jumping

#### Performance Requirements

- **Waitlist Join**: Add customer to waitlist within 1 second
- **Notification Send**: Send notification within 1 minute of slot availability
- **Position Update**: Update positions within 5 seconds
- **Analytics Calculation**: Calculate analytics within 30 seconds

#### Security Considerations

- **Data Privacy**: Don't expose other customers' information
- **Audit Trail**: Log all waitlist activities
- **Auto-Booking**: Require explicit authorization for auto-booking

#### Compliance Requirements

- **GDPR**: Support waitlist data export and deletion
- **Fairness**: Ensure fair queue management

#### Acceptance Criteria

1. WHEN appointment is fully booked, THE System SHALL offer waitlist option
2. WHEN customer joins waitlist, THE System SHALL add them to queue with position
3. WHEN appointment becomes available, THE System SHALL notify waitlist customers in order
4. WHEN customer accepts available slot, THE System SHALL book appointment and remove from waitlist
5. WHEN customer declines, THE System SHALL keep them on waitlist and notify next customer
6. WHEN tracking waitlist, THE System SHALL display waitlist size and conversion rate
7. WHEN analyzing waitlist, THE System SHALL identify popular services and times

#### Business Value

- Captures demand for fully booked services
- Increases booking conversion through waitlist
- Improves customer satisfaction
- Identifies capacity gaps for expansion
- Enables data-driven capacity planning

#### Dependencies

- Appointment booking (Requirement 3)
- Notifications (Requirement 7)
- Performance metrics (Requirement 21)
- Staff scheduling (Requirement 4)

#### Key Data Entities

- Waitlist (ID, service_id, staff_id, date, customer_id, position, preferred_times, auto_book_enabled, created_at)
- WaitlistNotification (ID, waitlist_id, notification_sent_at, notification_method, available_slot, customer_response)
- WaitlistAnalytics (ID, tenant_id, date, waitlist_size, conversion_rate, average_wait_time, popular_services)

#### User Roles

- Customer: Joins waitlist and responds to notifications
- Manager: Analyzes waitlist data
- System: Manages waitlist and sends notifications

---

### Requirement 65: Multi-Location Management

**User Story:** As a business owner, I want to manage multiple locations, so that I can scale my business across multiple sites.

#### Detailed Description

The multi-location management system enables businesses to operate multiple locations (salons, spas, gyms) from a single platform, with each location maintaining separate staff, resources, inventory, and operations. This enables businesses to scale across multiple sites while maintaining centralized management and reporting.

Each location operates independently with its own staff, resources, and inventory, but shares the same customer database and billing system. Customers can book appointments at any location, with the system managing location-specific availability and pricing. Managers can view and manage each location separately, while owners can view consolidated company-wide metrics.

The system supports location-specific configurations including hours of operation, services offered, staff assignments, and pricing. Analytics provide location-level insights into revenue, appointments, and performance, enabling location managers to optimize operations. Company-wide analytics consolidate metrics across all locations, enabling strategic planning.

#### Technical Specifications

- **Location Hierarchy**: Support multiple locations per tenant with independent operations
- **Location-Specific Configuration**: Configure hours, services, staff, resources per location
- **Location-Specific Inventory**: Track inventory separately per location
- **Location-Specific Pricing**: Support different pricing per location
- **Location-Specific Analytics**: Generate analytics per location
- **Consolidated Reporting**: Consolidate metrics across all locations
- **Location Assignment**: Assign staff and resources to locations
- **Location Filtering**: Filter appointments, staff, and resources by location

#### Business Context

- **Problem Solved**: Enables multi-location expansion; maintains separate operations per location; enables centralized management
- **ROI**: Enables scaling to multiple locations; reduces management overhead through centralized platform
- **Competitive Advantage**: Centralized management of multiple locations enables competing with larger chains; enables franchise model

#### Integration Points

- **Multi-Tenant Architecture (Req 1)**: Multi-location built on multi-tenant foundation
- **Appointment Booking (Req 3)**: Customers select location when booking
- **Staff Scheduling (Req 4)**: Staff assigned to locations
- **Inventory Management (Req 27, 28)**: Inventory tracked per location
- **Performance Metrics (Req 21)**: Analytics generated per location and company-wide

#### Data Model Details

- **Location**: ID (UUID), tenant_id (FK), name (string), address (string), city (string), state (string), zip (string), phone (string), email (string), hours_monday_start (time), hours_monday_end (time), ... (repeat for each day), timezone (string), manager_id (FK, nullable), created_at (timestamp), tenant_id (FK)
- **LocationResource**: ID (UUID), location_id (FK), resource_id (FK), quantity (integer), tenant_id (FK)
- **LocationInventory**: ID (UUID), location_id (FK), product_id (FK), quantity (integer), reorder_level (integer), tenant_id (FK)
- **LocationAnalytics**: ID (UUID), location_id (FK), date (date), revenue (decimal), appointments (integer), customers (integer), staff_count (integer), utilization_rate (decimal), tenant_id (FK)
- **LocationPricing**: ID (UUID), location_id (FK), service_id (FK), price (decimal), tenant_id (FK)

#### User Workflows

**For Owner Adding Location:**
1. Access location management
2. Click "Add Location"
3. Enter location details (name, address, phone, hours)
4. Configure services offered
5. Assign manager
6. Set up initial inventory
7. Publish location

**For Manager Managing Location:**
1. Log into location dashboard
2. View location-specific metrics
3. Manage staff assignments
4. Manage resources and inventory
5. View location appointments
6. Manage location settings

**For Owner Viewing Company-Wide Metrics:**
1. Access company dashboard
2. View consolidated revenue
3. View consolidated appointments
4. Compare locations
5. Identify top-performing locations
6. Identify underperforming locations
7. Make strategic decisions

**For Customer Booking at Location:**
1. Visit booking interface
2. Select location (if multiple available)
3. View services at selected location
4. View staff at selected location
5. Book appointment at location

#### Edge Cases & Constraints

- **Inventory Transfers**: Handle inventory transfers between locations
- **Staff Transfers**: Handle staff transfers between locations
- **Pricing Variations**: Support different pricing per location
- **Hours Variations**: Support different hours per location
- **Service Variations**: Support different services per location
- **Resource Sharing**: Handle shared resources across locations
- **Consolidated Reporting**: Ensure consolidated reports are accurate
- **Location Closure**: Handle location closure; migrate customers and staff

#### Performance Requirements

- **Location Creation**: Create location within 5 seconds
- **Location Analytics**: Generate location analytics within 30 seconds
- **Consolidated Analytics**: Generate company-wide analytics within 1 minute
- **Location Filtering**: Filter data by location within 1 second

#### Security Considerations

- **Location Isolation**: Ensure location data is properly isolated
- **Access Control**: Restrict location managers to their location
- **Audit Trail**: Log all location changes
- **Data Accuracy**: Ensure location data is accurate

#### Compliance Requirements

- **Multi-Location Compliance**: Ensure each location complies with local regulations
- **Data Residency**: Support storing location data in specific regions

#### Acceptance Criteria

1. WHEN adding location, THE System SHALL create separate location with own staff, resources, and inventory
2. WHEN managing locations, THE System SHALL allow viewing and managing each location separately
3. WHEN booking appointment, THE System SHALL allow selecting location with location-specific availability
4. WHEN viewing analytics, THE System SHALL display metrics by location and company-wide
5. WHEN managing staff, THE System SHALL allow assigning staff to locations
6. WHEN managing inventory, THE System SHALL track inventory separately per location
7. WHEN consolidating reports, THE System SHALL display company-wide metrics with location breakdowns

#### Business Value

- Enables multi-location expansion
- Maintains separate operations per location
- Provides location-level analytics and insights
- Supports franchise model
- Enables centralized management of multiple locations

#### Dependencies

- Multi-tenant architecture (Requirement 1)
- Appointment booking (Requirement 3)
- Staff scheduling (Requirement 4)
- Inventory management (Requirements 27, 28)
- Performance metrics (Requirement 21)

#### Key Data Entities

- Location (ID, tenant_id, name, address, city, state, zip, phone, email, hours, timezone, manager_id)
- LocationResource (ID, location_id, resource_id, quantity)
- LocationInventory (ID, location_id, product_id, quantity, reorder_level)
- LocationAnalytics (ID, location_id, date, revenue, appointments, customers, utilization_rate)
- LocationPricing (ID, location_id, service_id, price)

#### User Roles

- Owner: Manages all locations and views company-wide metrics
- Location Manager: Manages individual location
- Staff: Works at assigned location

---

### Requirement 66: Predictive Analytics (No-Show Forecasting)

**User Story:** As a manager, I want to predict no-shows, so that I can take preventive action and reduce revenue loss.

#### Detailed Description

The predictive analytics system uses machine learning to forecast which customers are likely to miss their appointments (no-show), enabling managers to take preventive action. No-shows represent significant revenue loss for service businesses, as staff time and resources are wasted. By identifying high-risk appointments early, managers can send additional reminders, request confirmation, or offer incentives to encourage attendance.

The system analyzes historical no-show patterns to identify factors that predict no-shows, such as customer demographics, booking patterns, time of day, day of week, and service type. A machine learning model is trained on historical data to predict no-show probability for each appointment. Predictions are continuously refined as new data becomes available.

The system recommends preventive actions based on no-show risk, such as sending additional reminders, requesting confirmation, or offering incentives. Analytics track the effectiveness of preventive actions, measuring impact on no-show rates. The system forecasts future no-show rates based on trends, enabling capacity planning.

#### Technical Specifications

- **No-Show Pattern Analysis**: Analyze historical no-show patterns to identify predictive factors
- **Machine Learning Model**: Train model to predict no-show probability
- **Risk Scoring**: Calculate no-show risk score for each appointment (0-100)
- **Preventive Actions**: Recommend preventive actions based on risk score
- **Action Tracking**: Track effectiveness of preventive actions
- **Forecast Accuracy**: Measure prediction accuracy and refine model
- **Trend Analysis**: Identify no-show trends by customer segment, service, time
- **Capacity Planning**: Forecast no-show rates for capacity planning

#### Business Context

- **Problem Solved**: Reduces no-show rates; prevents revenue loss; enables proactive management
- **ROI**: Reduces no-show rates by 20-30% through preventive actions; prevents revenue loss of 5-10%
- **Competitive Advantage**: Proactive no-show management improves resource utilization; enables better customer experience

#### Integration Points

- **Appointment Booking (Req 3)**: No-show predictions integrated into appointment system
- **Notifications (Req 7)**: Preventive action notifications sent via email/SMS/push
- **Performance Metrics (Req 21)**: No-show metrics integrated into performance dashboard
- **Staff Scheduling (Req 4)**: No-show forecasts inform staffing decisions

#### Data Model Details

- **NoShowPrediction**: ID (UUID), appointment_id (FK), risk_score (decimal), predicted_no_show (boolean), confidence_interval (decimal), risk_factors (JSON), preventive_action (enum: reminder/confirmation/incentive/none), action_taken (boolean), action_date (date, nullable), actual_no_show (boolean, nullable), prediction_accuracy (decimal, nullable), tenant_id (FK)
- **NoShowAnalytics**: ID (UUID), tenant_id (FK), date (date), predicted_no_shows (integer), actual_no_shows (integer), prediction_accuracy (decimal), no_show_rate (decimal), prevented_no_shows (integer), tenant_id (FK)
- **NoShowModel**: ID (UUID), tenant_id (FK), model_version (integer), accuracy (decimal), precision (decimal), recall (decimal), last_trained (timestamp), training_data_size (integer), tenant_id (FK)
- **PreventiveAction**: ID (UUID), appointment_id (FK), action_type (enum: reminder/confirmation/incentive), action_date (date), action_result (enum: success/failed/no_response), tenant_id (FK)

#### User Workflows

**For System Predicting No-Shows:**
1. Retrieve appointment details
2. Analyze customer history
3. Calculate risk factors
4. Run prediction model
5. Generate risk score
6. Recommend preventive action
7. Store prediction

**For Manager Viewing Predictions:**
1. Access no-show analytics dashboard
2. View high-risk appointments
3. Review risk factors
4. View recommended preventive actions
5. Take action or dismiss
6. Track action effectiveness

**For System Taking Preventive Action:**
1. Identify high-risk appointment
2. Send reminder or confirmation request
3. Track customer response
4. If no response, escalate
5. Measure action effectiveness
6. Update model based on outcome

**For Manager Analyzing No-Show Trends:**
1. Access no-show analytics
2. View no-show rate trends
3. Identify high-risk customer segments
4. Identify high-risk services
5. Identify high-risk times
6. Plan preventive strategies

#### Edge Cases & Constraints

- **New Customers**: Limited history; use different model for new customers
- **New Services**: Limited data; use service-specific model
- **Seasonal Variations**: Account for seasonal patterns in no-shows
- **External Factors**: Account for weather, holidays, events
- **Model Drift**: Retrain model regularly to account for changing patterns
- **False Positives**: Minimize false positives; avoid over-contacting customers
- **Privacy**: Don't expose customer personal information in predictions
- **Fairness**: Ensure predictions are fair and non-discriminatory

#### Performance Requirements

- **Prediction Generation**: Generate predictions for all appointments within 1 hour
- **Risk Score Calculation**: Calculate risk score within 500ms
- **Preventive Action**: Send preventive action within 24 hours of appointment
- **Analytics Calculation**: Calculate analytics within 30 seconds
- **Model Training**: Train model within 2 hours

#### Security Considerations

- **Data Privacy**: Don't expose customer personal information in predictions
- **Audit Trail**: Log all predictions and preventive actions
- **Model Transparency**: Explain why each appointment is predicted as high-risk

#### Compliance Requirements

- **Fairness**: Ensure predictions are fair and non-discriminatory
- **GDPR**: Support prediction data export and deletion

#### Acceptance Criteria

1. WHEN analyzing no-show patterns, THE System SHALL identify factors that predict no-shows
2. WHEN booking appointment, THE System SHALL calculate no-show risk score
3. WHEN risk is high, THE System SHALL recommend preventive actions (reminder, confirmation, incentive)
4. WHEN tracking predictions, THE System SHALL measure prediction accuracy
5. WHEN analyzing trends, THE System SHALL identify high-risk customer segments and times
6. WHEN forecasting no-shows, THE System SHALL predict no-show rate for future periods
7. WHEN exporting predictions, THE System SHALL provide no-show risk reports with preventive actions

#### Business Value

- Reduces no-show rates through preventive actions
- Prevents revenue loss from no-shows
- Enables proactive management
- Improves resource utilization
- Enables data-driven capacity planning

#### Dependencies

- Appointment booking (Requirement 3)
- Notifications (Requirement 7)
- Performance metrics (Requirement 21)
- Staff scheduling (Requirement 4)

#### Key Data Entities

- NoShowPrediction (ID, appointment_id, risk_score, predicted_no_show, confidence_interval, risk_factors, preventive_action)
- NoShowAnalytics (ID, tenant_id, date, predicted_no_shows, actual_no_shows, prediction_accuracy, no_show_rate)
- NoShowModel (ID, tenant_id, model_version, accuracy, precision, recall, last_trained)
- PreventiveAction (ID, appointment_id, action_type, action_date, action_result)

#### User Roles

- Manager: Views predictions and takes preventive actions
- System: Generates predictions and recommends actions
- Owner: Analyzes no-show trends

---

### Requirement 67: Dynamic Pricing Based on Demand

**User Story:** As a business owner, I want to adjust pricing based on demand, so that I can maximize revenue during peak times.

#### Detailed Description

The dynamic pricing system automatically adjusts service prices based on real-time demand, enabling businesses to maximize revenue during peak times while encouraging bookings during slow periods. This revenue optimization strategy is commonly used in airlines, hotels, and ride-sharing services, and is increasingly adopted by service businesses.

The system defines base prices and demand multipliers for each service. When demand is high (many bookings, few available slots), prices increase automatically. When demand is low (few bookings, many available slots), prices decrease to encourage bookings. Pricing adjustments are applied in real-time as customers browse and book appointments.

The system tracks the impact of dynamic pricing on revenue, bookings, and customer satisfaction. Analytics identify optimal pricing strategies for each service and time period. The system supports manual price overrides for special promotions or events. Customers see the dynamic price when booking, with transparency about why the price is different from the base price.

#### Technical Specifications

- **Base Price Configuration**: Define base price for each service
- **Demand Multiplier**: Define multiplier based on demand level (0.5x to 2.0x)
- **Real-Time Calculation**: Calculate dynamic price in real-time based on current demand
- **Demand Metrics**: Track available slots, bookings, and utilization
- **Price Transparency**: Show base price and dynamic price to customers
- **Manual Overrides**: Support manual price overrides for promotions
- **Impact Tracking**: Track impact on revenue, bookings, and satisfaction
- **Optimization**: Recommend optimal pricing based on analytics

#### Business Context

- **Problem Solved**: Maximizes revenue during peak times; increases bookings during low demand; optimizes pricing automatically
- **ROI**: Increases revenue by 10-20% through dynamic pricing; increases bookings by 5-15% during low demand
- **Competitive Advantage**: Dynamic pricing enables competing on revenue optimization; enables maximizing profitability

#### Integration Points

- **Appointment Booking (Req 3)**: Dynamic prices applied during booking
- **Billing & Payment (Req 6)**: Dynamic prices used for invoicing
- **Peak Hours Analysis (Req 55)**: Demand data used for dynamic pricing
- **Performance Metrics (Req 21)**: Pricing metrics integrated into performance dashboard

#### Data Model Details

- **DynamicPricingRule**: ID (UUID), tenant_id (FK), service_id (FK), base_price (decimal), demand_multiplier_low (decimal), demand_multiplier_medium (decimal), demand_multiplier_high (decimal), utilization_threshold_low (decimal), utilization_threshold_high (decimal), effective_from (date), effective_to (date, nullable), enabled (boolean), tenant_id (FK)
- **DynamicPrice**: ID (UUID), appointment_id (FK), service_id (FK), base_price (decimal), dynamic_price (decimal), demand_factor (decimal), utilization_rate (decimal), calculated_at (timestamp), tenant_id (FK)
- **DynamicPricingAnalytics**: ID (UUID), tenant_id (FK), date (date), service_id (FK), average_base_price (decimal), average_dynamic_price (decimal), revenue_impact (decimal), booking_impact (decimal), customer_satisfaction_impact (decimal), tenant_id (FK)
- **PriceOverride**: ID (UUID), tenant_id (FK), service_id (FK), override_price (decimal), reason (string), effective_from (date), effective_to (date), created_by (FK), tenant_id (FK)

#### User Workflows

**For Owner Setting Pricing Rules:**
1. Access dynamic pricing settings
2. Select service
3. Set base price
4. Set demand multipliers (low, medium, high)
5. Set utilization thresholds
6. Enable dynamic pricing
7. Monitor impact

**For System Calculating Dynamic Price:**
1. Retrieve service base price
2. Calculate current utilization rate
3. Determine demand level based on utilization
4. Apply demand multiplier
5. Calculate dynamic price
6. Store dynamic price
7. Display to customer

**For Customer Viewing Dynamic Price:**
1. Browse services
2. See base price and dynamic price
3. See explanation of dynamic pricing
4. Book at dynamic price
5. Receive invoice with dynamic price

**For Owner Analyzing Pricing Impact:**
1. Access pricing analytics
2. View revenue impact
3. View booking impact
4. View customer satisfaction impact
5. Identify optimal pricing strategies
6. Adjust pricing rules
7. Monitor impact of changes

#### Edge Cases & Constraints

- **Price Sensitivity**: Account for customer price sensitivity; avoid excessive price increases
- **Competitor Pricing**: Monitor competitor pricing; avoid pricing too high
- **Customer Fairness**: Ensure pricing is perceived as fair; provide transparency
- **Minimum Price**: Set minimum price to avoid pricing too low
- **Maximum Price**: Set maximum price to avoid pricing too high
- **Promotion Conflicts**: Handle conflicts between dynamic pricing and promotions
- **Seasonal Pricing**: Support seasonal pricing adjustments
- **Service Variations**: Support different pricing strategies for different services

#### Performance Requirements

- **Price Calculation**: Calculate dynamic price within 100ms
- **Price Update**: Update prices in real-time as demand changes
- **Analytics Calculation**: Calculate pricing analytics within 30 seconds
- **Pricing Report**: Generate pricing report within 1 minute

#### Security Considerations

- **Price Accuracy**: Ensure prices are calculated accurately
- **Audit Trail**: Log all price changes and overrides
- **Fraud Prevention**: Prevent unauthorized price changes

#### Compliance Requirements

- **Price Transparency**: Ensure customers understand dynamic pricing
- **Fair Pricing**: Ensure pricing is fair and non-discriminatory
- **Regulatory Compliance**: Comply with pricing regulations in each jurisdiction

#### Acceptance Criteria

1. WHEN setting pricing rules, THE System SHALL define base price and demand multipliers
2. WHEN demand is high, THE System SHALL increase price automatically based on multiplier
3. WHEN demand is low, THE System SHALL decrease price to encourage bookings
4. WHEN booking appointment, THE System SHALL apply dynamic price based on current demand
5. WHEN tracking pricing, THE System SHALL display price changes and revenue impact
6. WHEN analyzing pricing, THE System SHALL measure elasticity and optimization
7. WHEN exporting pricing data, THE System SHALL provide dynamic pricing reports with impact analysis

#### Business Value

- Maximizes revenue during peak times
- Increases bookings during low demand
- Optimizes pricing automatically
- Improves profitability
- Enables data-driven pricing strategy

#### Dependencies

- Appointment booking (Requirement 3)
- Billing & payment processing (Requirement 6)
- Peak hours analysis (Requirement 55)
- Performance metrics (Requirement 21)

#### Key Data Entities

- DynamicPricingRule (ID, tenant_id, service_id, base_price, demand_multiplier_low, demand_multiplier_medium, demand_multiplier_high)
- DynamicPrice (ID, appointment_id, service_id, base_price, dynamic_price, demand_factor, utilization_rate)
- DynamicPricingAnalytics (ID, tenant_id, date, service_id, average_base_price, average_dynamic_price, revenue_impact)
- PriceOverride (ID, tenant_id, service_id, override_price, reason, effective_from, effective_to)

#### User Roles

- Owner: Sets pricing rules and analyzes impact
- System: Calculates dynamic prices
- Manager: Monitors pricing impact

---

### Requirement 68: AI Chatbot for Customer Support

**User Story:** As a customer, I want to chat with AI support, so that I can get instant answers to common questions.

#### Detailed Description

The AI chatbot system provides 24/7 customer support through an intelligent conversational interface, answering common questions and resolving issues without human intervention. The chatbot uses natural language processing (NLP) to understand customer questions and retrieve relevant answers from a knowledge base.

The chatbot handles common questions about services, pricing, booking, cancellation policies, and account management. For questions it cannot answer, the chatbot escalates to human support staff, providing context about the customer's question. The system learns from customer interactions, continuously improving its ability to answer questions.

The chatbot is available through multiple channels including the customer portal, mobile app, and email. Customers can chat with the chatbot in their preferred language. Analytics track chatbot performance, identifying common questions and gaps in the knowledge base. The system measures customer satisfaction with chatbot responses, enabling continuous improvement.

#### Technical Specifications

- **Natural Language Processing**: Understand customer questions using NLP
- **Knowledge Base**: Store answers to common questions
- **Intent Recognition**: Identify customer intent from questions
- **Entity Extraction**: Extract relevant information from questions
- **Response Generation**: Generate natural responses to questions
- **Escalation**: Escalate to human support when needed
- **Multi-Channel**: Support chatbot through portal, app, email
- **Multi-Language**: Support multiple languages
- **Learning**: Learn from customer interactions to improve responses

#### Business Context

- **Problem Solved**: Reduces support overhead; provides 24/7 support; improves customer satisfaction
- **ROI**: Reduces support costs by 30-50%; improves customer satisfaction by 20-30%; reduces support response time
- **Competitive Advantage**: 24/7 AI support expected by modern customers; enables competing on customer service

#### Integration Points

- **Customer Self-Service Portal (Req 60)**: Chatbot integrated into portal
- **Notifications (Req 7)**: Chatbot responses sent via notifications
- **Customer Profiles (Req 5)**: Customer context used for personalized responses
- **Performance Metrics (Req 21)**: Chatbot metrics integrated into performance dashboard

#### Data Model Details

- **ChatbotConversation**: ID (UUID), customer_id (FK), start_time (timestamp), end_time (timestamp, nullable), messages (JSON array), resolution_status (enum: resolved/escalated/abandoned), escalated_to_human (boolean), escalated_to_staff_id (FK, nullable), satisfaction_rating (integer, nullable), tenant_id (FK)
- **ChatbotMessage**: ID (UUID), conversation_id (FK), sender (enum: customer/chatbot), message_text (text), intent (string, nullable), confidence (decimal, nullable), timestamp (timestamp), tenant_id (FK)
- **ChatbotAnalytics**: ID (UUID), tenant_id (FK), date (date), conversation_count (integer), resolution_rate (decimal), escalation_rate (decimal), average_satisfaction (decimal), average_response_time (integer), tenant_id (FK)
- **KnowledgeBase**: ID (UUID), tenant_id (FK), question (text), answer (text), category (string), keywords (JSON array), created_at (timestamp), updated_at (timestamp), usage_count (integer), tenant_id (FK)
- **ChatbotFeedback**: ID (UUID), conversation_id (FK), feedback_type (enum: helpful/not_helpful/incorrect), comments (text, nullable), submitted_at (timestamp), tenant_id (FK)

#### User Workflows

**For Customer Chatting with Chatbot:**
1. Open chatbot interface
2. Type question
3. Receive chatbot response
4. Ask follow-up questions
5. If satisfied, end chat
6. If not satisfied, escalate to human support
7. Provide feedback on chatbot response

**For System Processing Chat:**
1. Receive customer message
2. Analyze message using NLP
3. Identify intent and entities
4. Search knowledge base for answer
5. Generate response
6. Send response to customer
7. Track conversation

**For Support Staff Handling Escalation:**
1. Receive escalated chat
2. Review conversation history
3. Provide human response
4. Resolve customer issue
5. Close chat
6. Provide feedback to chatbot

**For Manager Analyzing Chatbot Performance:**
1. Access chatbot analytics
2. View conversation count and trends
3. View resolution rate
4. View escalation rate
5. View customer satisfaction
6. Identify common questions
7. Identify gaps in knowledge base
8. Update knowledge base

#### Edge Cases & Constraints

- **Ambiguous Questions**: Handle ambiguous questions; ask for clarification
- **Out-of-Scope Questions**: Handle questions outside chatbot scope; escalate appropriately
- **Sensitive Information**: Don't expose sensitive information in responses
- **Language Support**: Support multiple languages; handle language detection
- **Context Awareness**: Maintain conversation context across multiple messages
- **Escalation**: Ensure smooth escalation to human support
- **Knowledge Base Accuracy**: Ensure knowledge base answers are accurate and up-to-date
- **Continuous Learning**: Learn from customer interactions to improve responses

#### Performance Requirements

- **Response Time**: Respond to customer message within 2 seconds
- **Intent Recognition**: Recognize intent with >90% accuracy
- **Resolution Rate**: Resolve >70% of questions without escalation
- **Escalation Time**: Escalate to human support within 1 minute
- **Analytics Calculation**: Calculate analytics within 30 seconds

#### Security Considerations

- **Data Privacy**: Don't expose customer personal information in responses
- **Audit Trail**: Log all chatbot conversations
- **Sensitive Data**: Handle sensitive information securely
- **Fraud Prevention**: Prevent chatbot abuse

#### Compliance Requirements

- **Privacy**: Comply with privacy regulations (GDPR, CCPA)
- **Accessibility**: Ensure chatbot is accessible (WCAG 2.1 AA compliant)
- **Fairness**: Ensure chatbot responses are fair and non-discriminatory

#### Acceptance Criteria

1. WHEN customer initiates chat, THE System SHALL connect to AI chatbot
2. WHEN customer asks question, THE System SHALL provide answer from knowledge base
3. WHEN chatbot cannot answer, THE System SHALL escalate to human support
4. WHEN tracking chatbot, THE System SHALL display conversation count and resolution rate
5. WHEN analyzing chatbot, THE System SHALL identify common questions and gaps
6. WHEN improving chatbot, THE System SHALL train on new questions and answers
7. WHEN exporting chatbot data, THE System SHALL provide support analytics

#### Business Value

- Reduces support overhead and costs
- Provides 24/7 customer support
- Improves customer satisfaction
- Reduces support response time
- Enables scaling support without hiring

#### Dependencies

- Customer self-service portal (Requirement 60)
- Notifications (Requirement 7)
- Customer profiles (Requirement 5)
- Performance metrics (Requirement 21)

#### Key Data Entities

- ChatbotConversation (ID, customer_id, start_time, end_time, messages, resolution_status, escalated_to_human)
- ChatbotMessage (ID, conversation_id, sender, message_text, intent, confidence, timestamp)
- ChatbotAnalytics (ID, tenant_id, date, conversation_count, resolution_rate, escalation_rate, average_satisfaction)
- KnowledgeBase (ID, tenant_id, question, answer, category, keywords, usage_count)
- ChatbotFeedback (ID, conversation_id, feedback_type, comments, submitted_at)

#### User Roles

- Customer: Chats with chatbot
- Support Staff: Handles escalated chats
- Manager: Analyzes chatbot performance and updates knowledge base
- System: Provides chatbot responses

---

### Requirement 69: White-Label Options

**User Story:** As a reseller, I want white-label options, so that I can rebrand the platform for my customers.

#### Detailed Description

The white-label system enables resellers and partners to rebrand the platform with their own branding, enabling them to offer the platform as their own product to their customers. This enables a reseller business model where partners can white-label the platform and sell it under their own brand, creating a new revenue stream.

The white-label system supports customizing the platform's appearance including logo, colors, fonts, and domain name. Customers accessing a white-labeled instance see only the reseller's branding, with no indication that the platform is powered by the underlying SaaS provider. All emails, reports, and communications use the reseller's branding.

The system supports multiple white-label configurations, enabling different resellers to have different branding. Each white-label configuration is associated with a specific tenant or group of tenants. The system tracks white-label usage and customization, enabling resellers to manage their branding.

#### Technical Specifications

- **Logo Customization**: Upload custom logo for display in UI
- **Color Customization**: Customize primary and secondary colors
- **Font Customization**: Customize fonts for branding consistency
- **Domain Customization**: Use custom domain (e.g., salon.reseller.com)
- **Email Branding**: Use custom branding in email templates
- **Report Branding**: Use custom branding in reports and exports
- **Favicon Customization**: Customize favicon for browser tab
- **Help Text Customization**: Customize help text and documentation

#### Business Context

- **Problem Solved**: Enables reseller business model; allows custom branding; increases reseller value
- **ROI**: Enables new revenue stream through reseller model; enables partners to offer platform under their brand
- **Competitive Advantage**: White-label options enable building partner ecosystem; enables scaling through resellers

#### Integration Points

- **Multi-Tenant Architecture (Req 1)**: White-label built on multi-tenant foundation
- **User Authentication (Req 2)**: Custom domain routing based on authentication
- **Notifications (Req 7)**: Emails use white-label branding
- **Performance Metrics (Req 21)**: White-label usage tracked

#### Data Model Details

- **WhiteLabelConfig**: ID (UUID), tenant_id (FK), reseller_id (FK, nullable), logo_url (string), primary_color (hex), secondary_color (hex), accent_color (hex), font_family (string), custom_domain (string, nullable), favicon_url (string, nullable), created_at (timestamp), updated_at (timestamp), enabled (boolean), tenant_id (FK)
- **WhiteLabelBranding**: ID (UUID), white_label_config_id (FK), email_template_id (FK), email_header_logo_url (string), email_footer_text (text), report_header_logo_url (string), report_footer_text (text), tenant_id (FK)
- **WhiteLabelCustomization**: ID (UUID), white_label_config_id (FK), customization_type (enum: logo/color/font/domain/email/report), customization_value (JSON), created_at (timestamp), updated_at (timestamp), tenant_id (FK)
- **WhiteLabelAnalytics**: ID (UUID), white_label_config_id (FK), date (date), active_users (integer), sessions (integer), bookings (integer), revenue (decimal), tenant_id (FK)

#### User Workflows

**For Reseller Configuring White-Label:**
1. Access white-label settings
2. Upload logo
3. Customize colors
4. Customize fonts
5. Set custom domain
6. Customize email templates
7. Customize reports
8. Preview white-labeled platform
9. Publish white-label configuration

**For Customer Accessing White-Labeled Platform:**
1. Visit custom domain
2. See reseller's branding
3. Log in
4. Use platform with reseller's branding
5. Receive emails with reseller's branding
6. Download reports with reseller's branding

**For Reseller Managing White-Label:**
1. Access white-label dashboard
2. View white-label usage
3. View active users
4. View revenue
5. Update branding
6. Track customization status

**For System Applying White-Label:**
1. Detect custom domain
2. Load white-label configuration
3. Apply branding to UI
4. Apply branding to emails
5. Apply branding to reports
6. Track usage

#### Edge Cases & Constraints

- **Domain Routing**: Handle custom domain routing correctly
- **Branding Consistency**: Ensure branding is consistent across all interfaces
- **Email Branding**: Ensure emails use correct branding
- **Report Branding**: Ensure reports use correct branding
- **Logo Sizing**: Handle logos of different sizes and formats
- **Color Contrast**: Ensure color choices meet accessibility standards
- **Font Compatibility**: Ensure custom fonts are compatible across browsers
- **Fallback Branding**: Use default branding if custom branding not configured

#### Performance Requirements

- **White-Label Load**: Load white-label configuration within 500ms
- **Branding Application**: Apply branding to UI within 1 second
- **Email Generation**: Generate branded email within 2 seconds
- **Report Generation**: Generate branded report within 5 seconds

#### Security Considerations

- **Domain Verification**: Verify custom domain ownership
- **Branding Isolation**: Ensure branding doesn't leak between white-label instances
- **Audit Trail**: Log all white-label configuration changes
- **Access Control**: Restrict white-label configuration to authorized users

#### Compliance Requirements

- **Trademark**: Ensure white-label branding doesn't violate trademarks
- **Accessibility**: Ensure white-label branding meets accessibility standards (WCAG 2.1 AA)
- **Data Privacy**: Ensure white-label configuration doesn't expose sensitive data

#### Acceptance Criteria

1. WHEN configuring white-label, THE System SHALL allow customizing logo, colors, fonts, and domain
2. WHEN customer accesses platform, THE System SHALL display white-labeled branding
3. WHEN sending emails, THE System SHALL use white-labeled branding
4. WHEN generating reports, THE System SHALL include white-labeled branding
5. WHEN tracking white-label usage, THE System SHALL display customization status and usage metrics
6. WHEN managing white-label, THE System SHALL allow updating branding anytime
7. WHEN exporting white-label data, THE System SHALL provide branding configuration

#### Business Value

- Enables reseller business model
- Allows custom branding for partners
- Increases reseller value and differentiation
- Supports franchise model
- Enables building partner ecosystem

#### Dependencies

- Multi-tenant architecture (Requirement 1)
- User authentication (Requirement 2)
- Notifications (Requirement 7)
- Performance metrics (Requirement 21)

#### Key Data Entities

- WhiteLabelConfig (ID, tenant_id, reseller_id, logo_url, primary_color, secondary_color, custom_domain, favicon_url)
- WhiteLabelBranding (ID, white_label_config_id, email_header_logo_url, email_footer_text, report_header_logo_url)
- WhiteLabelCustomization (ID, white_label_config_id, customization_type, customization_value, created_at)
- WhiteLabelAnalytics (ID, white_label_config_id, date, active_users, sessions, bookings, revenue)

#### User Roles

- Reseller: Configures white-label branding
- Owner: Uses white-labeled platform
- System: Applies white-label branding

---

### Requirement 69: Public Booking via Subdomain

**User Story:** As a customer, I want to visit a salon's unique subdomain to view available services and book appointments without authentication, so that I can easily discover and book services from any device.

#### Detailed Description

The public booking feature enables customers to access a salon's booking interface through the salon's unique subdomain (e.g., `acme-salon.kenikool.com`) without requiring authentication. This creates a frictionless booking experience where customers can browse services, check staff availability, and create appointments in minutes. The public interface is completely isolated from the authenticated admin dashboard, ensuring customers only see relevant information.

The public booking system leverages the existing subdomain routing infrastructure to identify the tenant, then serves a lightweight, customer-focused interface. All data is filtered to show only published services and available time slots. Customers can book as guests or create accounts during the booking process. The system maintains complete tenant isolation, ensuring customers only see their salon's data.

#### Technical Specifications

- **Public Interface**: Lightweight React SPA served from subdomain
- **Service Listing**: Display all published services with descriptions, pricing, duration, and staff assignments
- **Staff Availability**: Show real-time availability for each staff member based on appointments and schedules
- **Booking Creation**: Allow customers to select service, staff, date, time, and provide contact information
- **Guest Booking**: Support booking without account creation; send confirmation via email
- **Account Creation**: Optional account creation during booking for future bookings
- **Tenant Isolation**: All queries filtered by tenant_id; no cross-tenant data leakage
- **Caching**: Cache service and staff data in Redis (5-minute TTL) for performance
- **Rate Limiting**: Limit booking creation to 10 per minute per IP to prevent abuse

#### Business Context

- **Problem Solved**: Eliminates friction in booking process; enables customers to book without signup
- **ROI**: Increases booking conversion by 40-60% through frictionless experience
- **Competitive Advantage**: Unique subdomains create branded experiences; reduces customer support burden

#### Integration Points

- **Subdomain Routing (Req 2)**: Uses existing subdomain routing to identify tenant
- **Service Management (Req 5)**: Display published services
- **Staff Management (Req 6)**: Show staff availability
- **Appointment Management (Req 4)**: Create appointments from public interface
- **Email Notifications (Req 7)**: Send booking confirmations to customers
- **Customer Management (Req 8)**: Create customer records from public bookings

#### Data Model Details

- **PublicBooking**: ID (UUID), tenant_id (FK), customer_id (FK, nullable for guest bookings), service_id (FK), staff_id (FK), appointment_id (FK), customer_name (string), customer_email (string), customer_phone (string), booking_date (date), booking_time (time), status (enum: pending/confirmed/completed/cancelled), created_at (timestamp), updated_at (timestamp)
- **PublicService**: Inherits from Service; includes is_published (boolean), public_description (string), public_image_url (string)
- **PublicStaff**: Inherits from Staff; includes is_available_for_public_booking (boolean), public_bio (string)

#### User Workflows

**For Customer - Browsing and Booking:**
1. Customer receives salon's subdomain URL (e.g., acme-salon.kenikool.com)
2. Customer visits URL in browser
3. System routes to public booking interface
4. Customer sees salon's branded interface with logo, colors, and name
5. Customer browses available services (filtered to published only)
6. Customer selects service and sees available staff members
7. Customer selects staff member and sees available time slots
8. Customer selects date and time
9. Customer enters name, email, phone
10. Customer clicks "Book Appointment"
11. System creates appointment and sends confirmation email
12. Customer receives confirmation with appointment details and salon contact info
13. Customer can optionally create account for future bookings

**For Salon Owner - Managing Public Booking:**
1. Owner logs into dashboard
2. Owner navigates to "Services" section
3. Owner marks services as "Published" to show in public booking
4. Owner marks staff as "Available for Public Booking"
5. Owner configures public booking settings (colors, logo, description)
6. Owner shares subdomain URL with customers
7. Owner receives notifications for new public bookings
8. Owner can view public bookings in appointment calendar

**For Customer - Creating Account During Booking:**
1. After booking, customer sees "Create Account" option
2. Customer enters password
3. System creates customer account with email and phone
4. Customer can now log in and view booking history
5. Customer can manage future bookings

#### Edge Cases & Constraints

- **Guest Bookings**: Support booking without account; send confirmation via email only
- **Availability Conflicts**: Prevent double-booking; show only available slots
- **Service Duration**: Calculate available slots based on service duration and staff availability
- **Timezone Handling**: Display times in salon's timezone; convert from customer's timezone if needed
- **Capacity Limits**: Respect service capacity limits; prevent overbooking
- **Cancellation**: Allow customers to cancel bookings up to 24 hours before appointment
- **Rescheduling**: Allow customers to reschedule bookings to different time slots
- **No-Show Handling**: Track no-shows; optionally charge cancellation fee

#### Performance Requirements

- **Page Load**: Public booking page loads within 2 seconds
- **Service Listing**: Display services within 500ms
- **Availability Check**: Calculate available slots within 1 second
- **Booking Creation**: Complete booking within 2 seconds
- **Email Sending**: Send confirmation email within 5 seconds

#### Security Considerations

- **Tenant Isolation**: All queries filtered by tenant_id; prevent cross-tenant data access
- **Rate Limiting**: Limit booking creation to prevent abuse (10 per minute per IP)
- **Input Validation**: Validate all customer inputs (email, phone, name)
- **CSRF Protection**: Implement CSRF tokens for booking form
- **XSS Prevention**: Sanitize all customer inputs before storing
- **Email Verification**: Optional email verification for guest bookings
- **Spam Prevention**: Implement CAPTCHA for public booking form

#### Compliance Requirements

- **GDPR**: Support data export and deletion for customer data
- **Email Compliance**: Comply with CAN-SPAM for booking confirmations
- **Accessibility**: Ensure public booking interface meets WCAG 2.1 AA standards
- **Data Privacy**: Encrypt customer data at rest and in transit

#### Acceptance Criteria

1. WHEN customer visits salon's subdomain, THE System SHALL display public booking interface with salon's branding
2. WHEN customer browses services, THE System SHALL display only published services with descriptions and pricing
3. WHEN customer selects service, THE System SHALL display available staff members and time slots
4. WHEN customer selects staff and time, THE System SHALL check availability and prevent double-booking
5. WHEN customer enters booking details, THE System SHALL validate email, phone, and name
6. WHEN customer submits booking, THE System SHALL create appointment and send confirmation email within 5 seconds
7. WHEN customer books as guest, THE System SHALL create appointment without requiring account creation
8. WHEN customer creates account during booking, THE System SHALL link account to appointment
9. WHEN booking is created, THE System SHALL prevent cross-tenant data access (only show salon's data)
10. WHEN multiple bookings are submitted simultaneously, THE System SHALL prevent double-booking through locking
11. WHEN customer cancels booking, THE System SHALL update appointment status and send cancellation email
12. WHEN customer reschedules booking, THE System SHALL update appointment time and send confirmation
13. WHEN booking rate limit is exceeded, THE System SHALL return 429 Too Many Requests

#### Business Value

- Increases booking conversion by 40-60% through frictionless experience
- Reduces customer support burden by enabling self-service bookings
- Creates branded customer experiences through unique subdomains
- Enables viral growth through easy sharing of booking links
- Captures customer data for marketing and retention

#### Dependencies

- Subdomain routing (Requirement 2)
- Service management (Requirement 5)
- Staff management (Requirement 6)
- Appointment management (Requirement 4)
- Email notifications (Requirement 7)
- Customer management (Requirement 8)

#### Key Data Entities

- PublicBooking (tenant_id, customer_id, service_id, staff_id, appointment_id, customer_name, customer_email, customer_phone)
- PublicService (tenant_id, name, description, pricing, is_published)
- PublicStaff (tenant_id, name, is_available_for_public_booking)

#### User Roles

- Customer: Books appointments via public interface
- Salon Owner: Manages public booking settings and views bookings
- System: Routes requests to correct tenant and enforces isolation

---

## Summary

This comprehensive requirements document specifies 69 features organized across 5 implementation phases:

- **Phase 1 (MVP)**: 12 core features for basic operations
- **Phase 2 (Operations & Financial)**: 18 features for advanced operations and financial management
- **Phase 3 (Customer Engagement & Marketing)**: 14 features for marketing and customer retention
- **Phase 4 (Integrations & Compliance)**: 13 features for third-party integrations and compliance
- **Phase 5 (Advanced Features)**: 11 features for AI and advanced capabilities
- **Public Booking**: 1 feature for customer-facing booking interface

Each feature includes detailed acceptance criteria, business value, dependencies, data entities, and user roles to guide implementation.



---

## PHASE 6 - Public Booking Via Subdomain

### Requirement 69: Public Booking Interface via Subdomain

**User Story:** As a customer, I want to book appointments through a salon's unique subdomain without creating an account, so that I can quickly schedule services.

#### Detailed Description

The public booking interface enables customers to browse services, view staff availability, and book appointments through a salon's branded subdomain (e.g., acme-salon.kenikool.com). Customers can complete the entire booking process without creating an account, providing only their name, email, and phone number. The system maintains complete tenant isolation, ensuring customers only see the specific salon's services and availability.

The public booking experience includes:
1. **Service Selection**: Browse published services with descriptions, pricing, and duration
2. **Staff Selection**: Choose preferred staff member or allow system to assign
3. **Availability Selection**: View real-time availability and select preferred time slot
4. **Customer Information**: Enter name, email, phone (no account creation required)
5. **Booking Confirmation**: Receive confirmation email with appointment details
6. **Cancellation**: Cancel booking via email link (valid 24 hours before appointment)

#### Technical Specifications

- **Subdomain Routing**: Wildcard DNS (*.kenikool.com) routes all subdomains to API
- **Tenant Extraction**: Middleware extracts subdomain and injects tenant_id into request context
- **Public Endpoints**: GET /public/services, GET /public/staff, GET /public/availability, POST /public/bookings, GET /public/bookings/{id}
- **Rate Limiting**: 10 bookings per minute per IP address to prevent abuse
- **Guest Booking**: Support booking without account creation
- **Booking Confirmation**: Send confirmation email with appointment details and cancellation link
- **Cancellation**: Allow cancellation via email link (valid 24 hours before appointment)
- **Tenant Isolation**: All queries filtered by tenant_id from subdomain context

#### Business Context

- **Problem Solved**: Enables customers to book appointments without friction; increases conversion rate
- **ROI**: Reduces booking friction by 80%; increases booking volume by 40-60%
- **Competitive Advantage**: Branded booking experience; no account creation required; mobile-optimized

#### Integration Points

- **Subdomain Routing (Req 2)**: Uses subdomain routing from registration feature
- **Service Management (Req 5)**: Display published services
- **Staff Management (Req 6)**: Display available staff
- **Appointment Management (Req 4)**: Create appointments from public bookings
- **Email Notifications (Req 7)**: Send booking confirmation and cancellation emails
- **Customer Management (Req 8)**: Create guest customer records

#### Data Model Details

- **PublicBooking**: ID (UUID), tenant_id (FK), service_id (FK), staff_id (FK), customer_name (string), customer_email (string), customer_phone (string), booking_date (date), booking_time (time), duration_minutes (integer), status (enum: pending/confirmed/cancelled), notes (string, nullable), created_at (timestamp), updated_at (timestamp)
- **PublicService**: Extends Service model with is_published (boolean), public_description (string), public_image_url (string), allow_public_booking (boolean)
- **PublicStaff**: Extends Staff model with is_available_for_public_booking (boolean), public_bio (string), public_photo_url (string)

#### User Workflows

**For Customer - Booking via Subdomain:**
1. Customer receives salon's subdomain URL (e.g., acme-salon.kenikool.com)
2. Customer visits URL in browser
3. System routes request to correct tenant based on subdomain
4. Customer sees salon's branded booking interface with services, staff, and availability
5. Customer selects service, staff member, date, and time
6. Customer enters name, email, and phone number
7. Customer reviews booking details
8. Customer clicks "Confirm Booking" button
9. System creates guest booking record (no account required)
10. System sends booking confirmation email to customer with appointment details
11. Customer receives email with appointment details and cancellation link
12. Customer can optionally create account to manage future bookings

**For Customer - Cancelling Booking:**
1. Customer receives booking confirmation email
2. Customer clicks "Cancel Booking" link in email
3. System verifies cancellation link is valid (within 24 hours of appointment)
4. System marks booking as cancelled
5. System sends cancellation confirmation email to customer
6. Salon owner is notified of cancellation

**For Salon Owner - Managing Public Bookings:**
1. Owner logs into dashboard
2. Owner views public bookings in appointments list
3. Owner can confirm, reschedule, or cancel public bookings
4. Owner receives notifications for new public bookings
5. Owner can configure which services are available for public booking
6. Owner can configure which staff members are available for public booking

#### Edge Cases & Constraints

- **Subdomain Not Found**: Return 404 if subdomain doesn't match any tenant
- **Tenant Inactive**: Return 403 if tenant is not published or is inactive
- **No Available Slots**: Show message if no availability for selected service/date
- **Double-Booking Prevention**: Prevent booking same time slot twice
- **Timezone Handling**: Convert customer timezone to salon timezone for availability
- **Cancellation Window**: Only allow cancellation 24 hours before appointment
- **Guest Customer Deduplication**: Check if email already exists before creating guest customer

#### Performance Requirements

- **Subdomain Routing**: Route request to correct tenant within 50ms
- **Availability Calculation**: Calculate available slots within 200ms
- **Booking Creation**: Create booking within 500ms
- **Email Sending**: Send confirmation email within 2 seconds
- **Page Load**: Public booking page loads within 2 seconds

#### Security Considerations

- **Tenant Isolation**: All queries include tenant_id filter to prevent cross-tenant data access
- **Rate Limiting**: Limit bookings to 10 per minute per IP to prevent abuse
- **Input Validation**: Validate all customer inputs (email, phone, name)
- **CSRF Protection**: Include CSRF token in booking form
- **Email Verification**: Verify customer email before confirming booking (optional)
- **Cancellation Link Security**: Use secure token in cancellation link, valid for 24 hours only

#### Compliance Requirements

- **GDPR**: Support data export and deletion of guest customer data
- **Email Compliance**: Comply with CAN-SPAM by including unsubscribe option
- **Data Retention**: Delete guest customer data after 1 year of inactivity
- **Privacy**: Display privacy policy and terms of service on booking page

#### Acceptance Criteria

1. WHEN customer visits subdomain URL, THE System SHALL route to correct tenant and display salon's branded interface
2. WHEN customer selects service, THE System SHALL display available staff members
3. WHEN customer selects staff, THE System SHALL display available time slots
4. WHEN customer enters booking details, THE System SHALL validate email and phone format
5. WHEN customer confirms booking, THE System SHALL create appointment without requiring account
6. WHEN booking is created, THE System SHALL send confirmation email to customer
7. WHEN customer clicks cancellation link, THE System SHALL cancel booking if within 24 hours
8. WHEN booking is cancelled, THE System SHALL send cancellation confirmation to customer
9. WHEN public booking endpoint is called, THE System SHALL rate limit to 10 bookings per minute per IP
10. WHEN customer data is accessed, THE System SHALL maintain tenant isolation (no cross-tenant data visible)
11. WHEN availability is calculated, THE System SHALL account for staff schedule, existing appointments, and service duration
12. WHEN double-booking is attempted, THE System SHALL prevent and show error message
13. WHEN guest customer email already exists, THE System SHALL link to existing customer instead of creating duplicate
14. WHEN timezone conversion is needed, THE System SHALL convert customer timezone to salon timezone

#### Business Value

- Enables customers to book without friction or account creation
- Increases booking conversion rate by 40-60%
- Reduces support burden by enabling self-service booking
- Creates branded booking experience for each salon
- Enables viral growth through shared subdomain URLs

#### Dependencies

- Salon Owner Registration (Requirement 2) - Provides subdomain routing
- Service Management (Requirement 5) - Provides services for public booking
- Staff Management (Requirement 6) - Provides staff for public booking
- Appointment Management (Requirement 4) - Creates appointments from public bookings
- Email Notifications (Requirement 7) - Sends confirmation and cancellation emails
- Customer Management (Requirement 8) - Creates guest customer records

#### Key Data Entities

- PublicBooking (tenant_id, service_id, staff_id, customer_name, customer_email, customer_phone, booking_date, booking_time)
- PublicService (tenant_id, name, description, pricing, is_published)
- PublicStaff (tenant_id, name, is_available_for_public_booking)

#### User Roles

- Customer: Books appointments via public interface without account
- Salon Owner: Manages public booking settings and views bookings
- System: Routes requests to correct tenant and enforces isolation

---

## PHASE 7 - Point of Sale (POS) System

### Requirement 70: POS Transaction Recording and Processing

**User Story:** As a salon manager, I want to record transactions at the point of sale, so that I can track all sales and maintain accurate financial records.

#### Detailed Description

The POS transaction system records all sales transactions including services, products, and packages. Each transaction captures customer information, items purchased, pricing, taxes, discounts, and payment method. Transactions are linked to appointments when applicable, creating a complete audit trail of all business activities.

The system supports multiple transaction types:
- **Service Transactions**: Charges for services rendered (haircut, massage, training session)
- **Product Transactions**: Sales of retail products (shampoo, supplements, equipment)
- **Package Transactions**: Sales of service packages (10-session package, monthly membership)
- **Refund Transactions**: Refunds for previous transactions

Each transaction generates a unique transaction ID, captures timestamp, staff member, customer, and payment details. Transactions are immutable once recorded, with all modifications tracked in audit logs.

#### Technical Specifications

- **Transaction Model**: ID (UUID), tenant_id (FK), customer_id (FK), staff_id (FK), appointment_id (FK, nullable), transaction_type (enum: service/product/package/refund), items (JSON array), subtotal (decimal), tax (decimal), discount (decimal), total (decimal), payment_method (enum: cash/card/mobile_money/check), payment_status (enum: pending/completed/failed), reference_number (string), notes (string), created_at (timestamp), updated_at (timestamp)
- **Transaction Item**: transaction_id (FK), item_type (enum: service/product/package), item_id (FK), quantity (integer), unit_price (decimal), line_total (decimal), tax_amount (decimal)
- **Transaction Audit**: transaction_id (FK), action (string), old_value (JSON), new_value (JSON), modified_by (FK), modified_at (timestamp)
- **Immutability**: Transactions cannot be deleted; only refunds allowed for corrections
- **Audit Trail**: All transaction modifications logged with user, timestamp, and reason

#### Acceptance Criteria

1. WHEN a transaction is created, THE System SHALL generate unique transaction ID and timestamp
2. WHEN transaction items are added, THE System SHALL calculate subtotal, tax, and total automatically
3. WHEN transaction is completed, THE System SHALL link to appointment if applicable
4. WHEN transaction is recorded, THE System SHALL create immutable record in database
5. WHEN transaction is modified, THE System SHALL log modification in audit trail
6. WHEN transaction is refunded, THE System SHALL create refund transaction linked to original

---

### Requirement 71: Payment Processing Integration with Paystack

**User Story:** As a salon owner, I want to process payments through Paystack, so that I can accept card payments securely and receive funds in my bank account.

#### Detailed Description

The payment processing system integrates with Paystack to securely process card payments, mobile money transfers, and bank transfers. The system handles payment authorization, settlement, and reconciliation. Paystack webhooks notify the system of payment status changes, enabling real-time transaction updates.

The system supports:
- **Card Payments**: Visa, Mastercard, Verve
- **Mobile Money**: MTN Mobile Money, Airtel Money, Vodafone Cash
- **Bank Transfers**: Direct bank account transfers
- **Payment Plans**: Installment payments for large transactions
- **Recurring Payments**: Automatic billing for subscriptions and memberships

#### Technical Specifications

- **Paystack Integration**: Use Paystack Python SDK for API calls
- **Payment Authorization**: Tokenize cards for secure storage
- **Webhook Handling**: Process payment status updates from Paystack
- **Reconciliation**: Match Paystack transactions with system transactions
- **Error Handling**: Retry failed payments with exponential backoff
- **Logging**: Log all payment attempts and results for audit trail

#### Acceptance Criteria

1. WHEN payment is initiated, THE System SHALL create payment record and redirect to Paystack
2. WHEN payment is authorized, THE System SHALL update transaction status to completed
3. WHEN payment fails, THE System SHALL update transaction status to failed and allow retry
4. WHEN Paystack webhook is received, THE System SHALL verify signature and update payment status
5. WHEN payment is reconciled, THE System SHALL match with transaction and update settlement status

---

### Requirement 72: Inventory Deduction on Transaction

**User Story:** As a salon manager, I want inventory to be automatically deducted when products are sold, so that I can maintain accurate stock levels.

#### Detailed Description

The inventory deduction system automatically reduces inventory quantities when products are sold through the POS system. The system tracks inventory movements, prevents overselling, and generates low-stock alerts.

The system supports:
- **Automatic Deduction**: Inventory automatically reduced when transaction is completed
- **Oversell Prevention**: Prevent selling more than available stock
- **Inventory Tracking**: Track all inventory movements with timestamps
- **Low Stock Alerts**: Alert when inventory falls below minimum threshold
- **Inventory Adjustments**: Manual adjustments for damaged/lost items
- **Inventory Reconciliation**: Periodic physical inventory counts

#### Technical Specifications

- **Inventory Model**: ID (UUID), tenant_id (FK), product_id (FK), quantity_on_hand (integer), quantity_reserved (integer), quantity_available (integer), reorder_point (integer), reorder_quantity (integer), last_counted_at (timestamp)
- **Inventory Movement**: ID (UUID), tenant_id (FK), product_id (FK), movement_type (enum: purchase/sale/adjustment/return), quantity (integer), reference_id (string), created_at (timestamp)
- **Deduction Logic**: When transaction is completed, for each product item, reduce quantity_on_hand by quantity sold
- **Oversell Prevention**: Check quantity_available >= quantity_requested before allowing sale
- **Low Stock Alert**: Generate alert when quantity_on_hand <= reorder_point

#### Acceptance Criteria

1. WHEN transaction is completed, THE System SHALL deduct inventory for each product item
2. WHEN inventory is insufficient, THE System SHALL prevent transaction and show error
3. WHEN inventory falls below reorder point, THE System SHALL generate low-stock alert
4. WHEN inventory is deducted, THE System SHALL create inventory movement record
5. WHEN inventory is adjusted, THE System SHALL log adjustment reason and user

---

### Requirement 73: POS Reporting and Analytics

**User Story:** As a salon owner, I want to view POS reports and analytics, so that I can understand sales trends and optimize business operations.

#### Detailed Description

The POS reporting system provides comprehensive analytics on sales, revenue, inventory, and customer behavior. Reports include daily/weekly/monthly summaries, top-selling items, customer purchase patterns, and revenue forecasts.

The system supports:
- **Sales Reports**: Daily, weekly, monthly sales summaries
- **Revenue Reports**: Revenue by service, product, staff member, customer
- **Inventory Reports**: Stock levels, turnover rates, low-stock items
- **Customer Reports**: Purchase history, lifetime value, repeat purchase rate
- **Payment Reports**: Payment method breakdown, failed payment analysis
- **Trend Analysis**: Sales trends, seasonal patterns, growth forecasts

#### Technical Specifications

- **Report Generation**: Generate reports on-demand or scheduled
- **Data Aggregation**: Aggregate transaction data for reporting
- **Caching**: Cache report data in Redis for performance
- **Export**: Export reports as PDF, CSV, Excel
- **Visualization**: Display charts and graphs for visual analysis
- **Scheduling**: Schedule report generation and email delivery

#### Acceptance Criteria

1. WHEN generating sales report, THE System SHALL aggregate transactions by date/period
2. WHEN generating revenue report, THE System SHALL calculate revenue by category
3. WHEN generating inventory report, THE System SHALL show stock levels and turnover
4. WHEN generating customer report, THE System SHALL show purchase history and lifetime value
5. WHEN exporting report, THE System SHALL generate PDF/CSV/Excel file

---

### Requirement 74: Receipt Generation and Printing

**User Story:** As a salon staff member, I want to generate and print receipts, so that customers have proof of purchase.

#### Detailed Description

The receipt generation system creates professional receipts for all transactions. Receipts include transaction details, itemization, taxes, discounts, payment method, and salon contact information. Receipts can be printed, emailed, or displayed on screen.

The system supports:
- **Receipt Templates**: Customizable receipt templates with salon branding
- **Itemization**: Detailed breakdown of items, quantities, prices, taxes
- **Discounts**: Show applied discounts and discount codes
- **Taxes**: Show tax calculation and total tax amount
- **Payment Details**: Show payment method and reference number
- **Branding**: Include salon logo, name, address, phone, website
- **QR Code**: Include QR code linking to receipt details
- **Printing**: Print to thermal printer or regular printer
- **Email**: Email receipt to customer
- **Digital**: Display receipt on screen or mobile device

#### Technical Specifications

- **Receipt Template**: HTML template with CSS styling
- **Data Binding**: Bind transaction data to template
- **PDF Generation**: Generate PDF from HTML template
- **Printing**: Send PDF to printer via print server
- **Email**: Send PDF as email attachment
- **QR Code**: Generate QR code linking to receipt verification URL
- **Customization**: Allow customizing receipt template per tenant

#### Acceptance Criteria

1. WHEN transaction is completed, THE System SHALL generate receipt automatically
2. WHEN receipt is generated, THE System SHALL include all transaction details
3. WHEN receipt is printed, THE System SHALL send to configured printer
4. WHEN receipt is emailed, THE System SHALL send to customer email address
5. WHEN receipt is displayed, THE System SHALL show on screen or mobile device

---

### Requirement 75: Offline Mode for POS

**User Story:** As a salon staff member, I want to use POS in offline mode, so that I can continue processing transactions even when internet is unavailable.

#### Detailed Description

The offline mode enables the POS system to continue operating when internet connectivity is lost. Transactions are recorded locally and synced to the server when connectivity is restored. The system maintains data consistency and prevents data loss during offline periods.

The system supports:
- **Local Storage**: Store transactions locally using IndexedDB or SQLite
- **Offline Sync**: Sync transactions to server when connectivity restored
- **Conflict Resolution**: Handle conflicts when same transaction modified offline and online
- **Offline Indicators**: Show clear indication when operating in offline mode
- **Sync Status**: Show sync progress and status
- **Data Validation**: Validate data before syncing to prevent corruption

#### Technical Specifications

- **Local Database**: Use IndexedDB (browser) or SQLite (desktop) for local storage
- **Sync Queue**: Queue transactions for syncing when online
- **Conflict Detection**: Detect conflicts between local and server versions
- **Merge Strategy**: Merge local and server changes intelligently
- **Retry Logic**: Retry failed syncs with exponential backoff
- **Offline Indicator**: Show visual indicator when offline
- **Sync Progress**: Show progress bar during sync

#### Acceptance Criteria

1. WHEN internet is unavailable, THE System SHALL continue accepting transactions
2. WHEN transaction is recorded offline, THE System SHALL store locally
3. WHEN internet is restored, THE System SHALL sync transactions to server
4. WHEN syncing, THE System SHALL validate data before uploading
5. WHEN conflict occurs, THE System SHALL resolve intelligently and notify user

---

### Requirement 76: Quick Checkout and Split Payments

**User Story:** As a salon staff member, I want to quickly process checkouts and split payments, so that I can serve customers efficiently.

#### Detailed Description

The quick checkout system streamlines the payment process, enabling staff to complete transactions in seconds. The system supports split payments, allowing customers to pay with multiple payment methods.

The system supports:
- **Quick Checkout**: One-click checkout for repeat customers
- **Payment Splitting**: Split payment across multiple payment methods
- **Saved Payment Methods**: Save customer payment methods for quick checkout
- **Payment Shortcuts**: Quick buttons for common payment amounts
- **Tip Handling**: Add tips to transaction
- **Receipt Options**: Quick selection of receipt delivery method

#### Technical Specifications

- **Quick Checkout**: Pre-fill customer and payment method for repeat customers
- **Split Payment**: Allow multiple payment methods in single transaction
- **Payment Method Storage**: Securely store payment methods with customer consent
- **Tip Calculation**: Calculate tip as percentage or fixed amount
- **Receipt Delivery**: Quick selection of print, email, or SMS receipt

#### Acceptance Criteria

1. WHEN customer is repeat, THE System SHALL offer quick checkout option
2. WHEN quick checkout is selected, THE System SHALL pre-fill customer and payment method
3. WHEN split payment is selected, THE System SHALL allow multiple payment methods
4. WHEN payment is split, THE System SHALL allocate amounts to each method
5. WHEN tip is added, THE System SHALL include in total amount

---

### Requirement 77: Discounts, Taxes, and Promotions

**User Story:** As a salon manager, I want to apply discounts, taxes, and promotions, so that I can offer deals and maintain accurate financial records.

#### Detailed Description

The discount and promotion system enables applying various discounts and promotions to transactions. The system supports percentage discounts, fixed amount discounts, promotional codes, loyalty discounts, and bulk discounts.

The system supports:
- **Percentage Discounts**: Apply percentage discount to transaction
- **Fixed Discounts**: Apply fixed amount discount
- **Promotional Codes**: Apply discount codes for promotions
- **Loyalty Discounts**: Apply discounts based on customer loyalty status
- **Bulk Discounts**: Apply discounts for bulk purchases
- **Staff Discounts**: Apply employee discounts
- **Tax Calculation**: Calculate taxes based on discount amount
- **Discount Limits**: Set maximum discount per transaction

#### Technical Specifications

- **Discount Model**: ID (UUID), tenant_id (FK), discount_type (enum: percentage/fixed/code/loyalty/bulk), discount_value (decimal), applicable_to (enum: transaction/item/service/product), conditions (JSON), max_discount (decimal), active (boolean)
- **Discount Application**: Apply discount to transaction or specific items
- **Tax Calculation**: Calculate tax on discounted amount
- **Audit Trail**: Log all discounts applied with reason

#### Acceptance Criteria

1. WHEN discount is applied, THE System SHALL calculate discount amount correctly
2. WHEN percentage discount is applied, THE System SHALL calculate based on subtotal
3. WHEN promotional code is used, THE System SHALL validate code and apply discount
4. WHEN loyalty discount is applied, THE System SHALL verify customer loyalty status
5. WHEN tax is calculated, THE System SHALL calculate on discounted amount

---

### Requirement 78: Refund Processing

**User Story:** As a salon manager, I want to process refunds, so that I can handle customer returns and complaints.

#### Detailed Description

The refund processing system enables processing refunds for transactions. The system supports full refunds, partial refunds, and refund reasons. Refunds are tracked separately from original transactions, creating an audit trail.

The system supports:
- **Full Refunds**: Refund entire transaction amount
- **Partial Refunds**: Refund specific items or amounts
- **Refund Reasons**: Track reason for refund
- **Refund Status**: Track refund status (pending, approved, completed, rejected)
- **Refund Timeline**: Show refund processing timeline
- **Refund Reversal**: Reverse refund if needed
- **Inventory Restoration**: Restore inventory when refund is processed

#### Technical Specifications

- **Refund Model**: ID (UUID), tenant_id (FK), original_transaction_id (FK), refund_amount (decimal), refund_reason (string), refund_status (enum: pending/approved/completed/rejected), approved_by (FK), approved_at (timestamp), completed_at (timestamp), created_at (timestamp)
- **Refund Processing**: Create refund transaction linked to original
- **Inventory Restoration**: Restore inventory quantities when refund is completed
- **Payment Reversal**: Reverse payment through Paystack

#### Acceptance Criteria

1. WHEN refund is requested, THE System SHALL create refund record
2. WHEN refund is approved, THE System SHALL process refund through payment gateway
3. WHEN refund is completed, THE System SHALL restore inventory
4. WHEN refund is reversed, THE System SHALL reverse inventory restoration
5. WHEN refund is processed, THE System SHALL send confirmation to customer

---

### Requirement 79: Staff Tracking and Commission

**User Story:** As a salon manager, I want to track staff performance and calculate commissions, so that I can manage staff compensation fairly.

#### Detailed Description

The staff tracking system records which staff member processed each transaction, enabling tracking of staff performance and commission calculation. The system supports various commission structures including percentage of sales, fixed amount per transaction, and tiered commissions.

The system supports:
- **Staff Assignment**: Assign staff member to transaction
- **Commission Calculation**: Calculate commission based on transaction amount
- **Commission Structures**: Support percentage, fixed, and tiered commissions
- **Commission Tracking**: Track commission earned by each staff member
- **Commission Payouts**: Process commission payments
- **Performance Metrics**: Track staff performance metrics
- **Audit Trail**: Log all commission calculations

#### Technical Specifications

- **Staff Commission**: ID (UUID), tenant_id (FK), staff_id (FK), transaction_id (FK), commission_amount (decimal), commission_rate (decimal), commission_type (enum: percentage/fixed/tiered), calculated_at (timestamp)
- **Commission Structure**: ID (UUID), tenant_id (FK), staff_id (FK), commission_type (enum: percentage/fixed/tiered), commission_value (decimal), effective_from (date), effective_to (date, nullable)
- **Commission Payout**: ID (UUID), tenant_id (FK), staff_id (FK), payout_period (string), total_commission (decimal), payout_status (enum: pending/approved/completed), payout_date (date)

#### Acceptance Criteria

1. WHEN transaction is completed, THE System SHALL assign staff member
2. WHEN commission is calculated, THE System SHALL apply correct commission structure
3. WHEN commission is tracked, THE System SHALL show commission earned by staff
4. WHEN commission payout is processed, THE System SHALL calculate total commission
5. WHEN commission is paid, THE System SHALL update payout status

---

### Requirement 80: Audit Trail and Compliance

**User Story:** As a salon owner, I want complete audit trail of all POS transactions, so that I can ensure compliance and detect fraud.

#### Detailed Description

The audit trail system records all POS activities including transaction creation, modification, refunds, discounts, and payment processing. The system maintains immutable records for compliance and fraud detection.

The system supports:
- **Transaction Audit**: Log all transaction modifications
- **Payment Audit**: Log all payment attempts and results
- **Discount Audit**: Log all discounts applied
- **Refund Audit**: Log all refunds processed
- **User Audit**: Log which user performed each action
- **Timestamp Audit**: Record exact timestamp of each action
- **Compliance Reports**: Generate compliance reports for audits

#### Technical Specifications

- **Audit Log**: ID (UUID), tenant_id (FK), user_id (FK), action (string), resource_type (string), resource_id (string), old_value (JSON), new_value (JSON), timestamp (timestamp), ip_address (string)
- **Immutability**: Audit logs cannot be modified or deleted
- **Retention**: Retain audit logs for 7 years for compliance
- **Encryption**: Encrypt sensitive audit log data

#### Acceptance Criteria

1. WHEN transaction is created, THE System SHALL log creation with user and timestamp
2. WHEN transaction is modified, THE System SHALL log modification with old and new values
3. WHEN refund is processed, THE System SHALL log refund with reason and approver
4. WHEN discount is applied, THE System SHALL log discount with reason
5. WHEN audit log is queried, THE System SHALL return immutable records

---

## Summary

This comprehensive requirements document specifies 80 features organized across 7 implementation phases:

- **Phase 1 (MVP)**: 12 core features for basic operations
- **Phase 2 (Operations & Financial)**: 18 features for advanced operations and financial management
- **Phase 3 (Customer Engagement & Marketing)**: 14 features for marketing and customer retention
- **Phase 4 (Integrations & Compliance)**: 13 features for third-party integrations and compliance
- **Phase 5 (Advanced Features)**: 11 features for AI and advanced capabilities
- **Phase 6 (Public Booking)**: 1 feature for customer-facing booking interface via subdomain
- **Phase 7 (Point of Sale)**: 11 features for transaction processing and payment management

Each feature includes detailed acceptance criteria, business value, dependencies, data entities, and user roles to guide implementation.
