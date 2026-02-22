# Implementation Plan: Multi-Tenant SaaS Platform for Salon, Spa & Gym Management

## Overview

This implementation plan breaks down the comprehensive design into actionable coding tasks organized by feature area. The plan follows a layered approach, starting with foundational infrastructure, then building core features, and finally integrating advanced capabilities. Each task builds on previous tasks, ensuring incremental progress and early validation of core functionality.

**Technology Stack:**
- Backend: Python 3.11+ with FastAPI
- Database: MongoDB Atlas (managed cloud service)
- Cache: Redis 7+
- Message Queue: Celery with RabbitMQ
- Frontend: React 19+ with TypeScript, Vite, Zustand, @tanstack/react-query, Socket.io, Tailwind CSS
- Payments: Paystack (Africa-focused)
- Containerization: Docker & Docker Compose (all services except MongoDB)
- Testing: pytest for unit tests, Hypothesis for property-based tests
- AI/ML: TensorFlow/PyTorch for recommendations and predictive analytics

## Phase 1 - MVP Foundation (Weeks 1-4)

### 0. Frontend Setup and Dependencies (Existing + New)

**Status: ✅ 100% COMPLETE**

#### 0.1 React 19.2.0 + TypeScript 5.9.3 + Vite 7.3.1 setup

**Status:** ✅ COMPLETED

**Description:**
The frontend foundation has been established with React 19.2.0, TypeScript 5.9.3, and Vite 7.3.1. This provides a modern, type-safe development environment with fast build times and hot module replacement (HMR). The project is configured with ESLint for code quality and Tailwind CSS for styling. This task ensures the development environment is properly configured and ready for feature development.

**Technical Specifications:**
- React 19.2.0 with TypeScript strict mode enabled
- Vite 7.3.1 configured with HMR for development
- TypeScript 5.9.3 with strict type checking (noImplicitAny, strictNullChecks, etc.)
- ESLint configured with React and TypeScript plugins
- Tailwind CSS 3.4+ with @tailwindcss/vite plugin for optimized builds
- Source maps enabled for debugging
- Environment variable support (.env files)

**Acceptance Criteria:**
1. WHEN running `npm run dev`, THE development server SHALL start on port 3000 with HMR enabled
2. WHEN running `npm run build`, THE production build SHALL complete without errors and output to dist/ directory
3. WHEN importing React components, THE TypeScript compiler SHALL enforce strict type checking
4. WHEN running `npm run lint`, THE ESLint checker SHALL report no errors or warnings
5. WHEN using Tailwind CSS classes, THE build SHALL include only used styles in production

**Deliverables:**
- vite.config.ts (configured with React plugin and Tailwind CSS)
- tsconfig.json (strict mode enabled)
- eslint.config.js (configured for React and TypeScript)
- package.json (dependencies and scripts)
- .env.example (environment variable template)

---

#### 0.2 UI Component Library (35+ components)

**Status:** ✅ COMPLETED

**Description:**
A comprehensive production-ready UI component library has been built with 35+ components covering form inputs, display elements, dialogs, navigation, and advanced components. All components are built with Tailwind CSS, support light/dark modes, and follow accessibility best practices. Components include proper TypeScript types, prop validation, and comprehensive styling variants.

**Technical Specifications:**
- Form Components (10): Button, Input, Textarea, Select, Checkbox, Radio, RadioGroup, Switch, Label, Slider
- Display Components (10): Card, Badge, Avatar, Spinner, Skeleton, Progress, Alert, Toast, Divider, Separator
- Dialog Components (4): Modal, Dialog, ConfirmationModal, MobileModal
- Navigation Components (3): Dropdown, Tabs, Tooltip
- Advanced Components (8): Calendar, Table, ScrollArea, ErrorBoundary, LazyLoad, ImageLightbox, ServiceDetailsSkeleton, ThemeSelector
- All components support TypeScript with full type definitions
- All components support light/dark mode through CSS variables
- All components are fully responsive and mobile-optimized

**Acceptance Criteria:**
1. WHEN rendering any component, THE component SHALL display correctly in both light and dark modes
2. WHEN using form components, THE components SHALL support disabled state, error states, and loading states
3. WHEN using dialog components, THE components SHALL support keyboard navigation (Escape to close, Tab to navigate)
4. WHEN rendering components on mobile, THE components SHALL be touch-friendly with 44px minimum tap targets
5. WHEN using advanced components like Calendar or Table, THE components SHALL support filtering, sorting, and pagination

**Deliverables:**
- src/components/ui/ directory with all 35+ components
- Each component with TypeScript types and prop interfaces
- Storybook stories for each component (optional)
- Component documentation with usage examples

---

#### 0.3 Icon System (100+ SVG icons)

**Status:** ✅ COMPLETED

**Description:**
A comprehensive icon system with 100+ custom SVG icons organized by category (navigation, UI, business, services, status, finance, analytics, media, communication, settings, salon-specific, theme, file, loading). Icons are optimized for performance, support sizing variants, and integrate seamlessly with the component library.

**Technical Specifications:**
- 100+ custom SVG icons organized in categories
- Icons support multiple sizes (16px, 20px, 24px, 32px)
- Icons support color customization through CSS classes
- Icons are optimized for web (minified, no unnecessary attributes)
- Icon categories: Navigation, UI, Business, Services, Status, Finance, Analytics, Media, Communication, Settings, Salon-specific, Theme, File, Loading
- TypeScript icon component with proper prop types

**Acceptance Criteria:**
1. WHEN importing an icon, THE icon SHALL render correctly at all supported sizes
2. WHEN using icons in components, THE icons SHALL inherit color from parent element or accept custom color prop
3. WHEN rendering icons, THE SVG SHALL be optimized and not impact performance
4. WHEN viewing icons in light/dark mode, THE icons SHALL be visible and properly contrasted

**Deliverables:**
- src/components/icons/index.tsx (icon component with all 100+ icons)
- Icon assets organized by category
- Icon documentation with usage examples

---

#### 0.4 Theme System (3 themes × 2 modes)

**Status:** ✅ COMPLETED

**Description:**
A sophisticated theme system supporting 3 complete themes (Default, Elegant, Vibrant) with light and dark modes (6 total variations). The system uses CSS variables for dynamic theme switching without page reload. Each theme includes a complete color palette, typography, spacing, shadows, and border radius definitions.

**Technical Specifications:**
- 3 themes: Default (professional), Elegant (premium), Vibrant (energetic)
- 2 modes per theme: Light and Dark
- CSS variable-based system for dynamic switching
- Color palette: primary, secondary, accent, destructive, success, warning, info, muted
- Typography: font families, sizes (xs, sm, base, lg, xl, 2xl), weights (400, 500, 600, 700)
- Spacing: 8px base unit (0, 1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 32)
- Shadows: sm, md, lg, xl definitions
- Border radius: sm, md, lg, xl, full definitions
- Automatic dark mode detection via prefers-color-scheme media query
- Smooth theme transitions (0.3s)

**Acceptance Criteria:**
1. WHEN switching themes, THE entire application SHALL update colors without page reload
2. WHEN switching between light and dark modes, THE colors SHALL adjust appropriately
3. WHEN using CSS variables in components, THE variables SHALL be properly scoped to theme
4. WHEN system prefers dark mode, THE application SHALL automatically use dark theme
5. WHEN theme preference is saved, THE application SHALL restore theme on page reload

**Deliverables:**
- src/lib/themes/ directory with theme definitions
- CSS variable definitions in index.css
- Theme provider component
- useTheme hook for accessing and switching themes
- Theme persistence in localStorage

---

#### 0.5 Mobile Optimization & Accessibility

**Status:** ✅ COMPLETED

**Description:**
The frontend is fully optimized for mobile devices with touch-friendly interfaces, responsive layouts, and safe area insets for notched devices. Accessibility features ensure WCAG 2.1 AA compliance with focus states, ARIA labels, keyboard navigation, and reduced motion support.

**Technical Specifications:**
- Touch-friendly tap targets: 44px minimum for all interactive elements
- Mobile-optimized modals: Bottom sheet style for mobile, centered for desktop
- Responsive grids: Mobile-first approach with breakpoints at 768px (tablet) and 1024px (desktop)
- Safe area insets: Support for notched devices (iPhone X+, Android)
- Smooth scrolling: -webkit-overflow-scrolling for iOS
- GPU acceleration: transform and will-change for animations
- Reduced motion support: @prefers-reduced-motion media query
- Focus visible states: Keyboard navigation support
- ARIA labels and roles: Semantic HTML with proper ARIA attributes
- Color contrast: WCAG AA compliant (4.5:1 for text, 3:1 for graphics)
- Screen reader support: Proper heading hierarchy, alt text for images

**Acceptance Criteria:**
1. WHEN using the application on mobile, THE tap targets SHALL be at least 44px
2. WHEN navigating with keyboard, THE focus states SHALL be clearly visible
3. WHEN using a screen reader, THE application SHALL announce all interactive elements
4. WHEN system prefers reduced motion, THE animations SHALL be disabled or simplified
5. WHEN viewing on notched devices, THE content SHALL not be hidden behind notches

**Deliverables:**
- Responsive CSS with mobile-first approach
- Touch-friendly component variants
- ARIA labels and semantic HTML
- Keyboard navigation support
- Reduced motion CSS
- Safe area inset support

---

#### 0.6 Install missing frontend dependencies

**Status:** ✅ COMPLETED

**Description:**
Install the remaining frontend dependencies required for state management, data fetching, real-time communication, and HTTP requests. These libraries are essential for building the application features and will be used throughout the project.

**Technical Specifications:**
- Zustand 4.4+ (state management): Lightweight, simple, performant state management
- @tanstack/react-query 5.28+ (data fetching): Powerful data synchronization and caching
- socket.io-client 4.7+ (real-time): Real-time communication for notifications and updates
- Axios 1.6+ (HTTP client): Promise-based HTTP client with interceptors
- class-variance-authority 0.7+ (component variants): Type-safe component variant system
- clsx 2.0+ (class name utility): Utility for conditional class names
- tailwind-merge 2.2+ (Tailwind CSS merge): Merge Tailwind CSS classes without conflicts

**Acceptance Criteria:**
1. WHEN running `npm install`, THE dependencies SHALL install without errors
2. WHEN importing from installed packages, THE TypeScript compiler SHALL recognize types
3. WHEN running the development server, THE application SHALL start without dependency errors
4. WHEN checking package.json, THE versions SHALL match or exceed specified minimums

**Implementation Details:**
1. Run `npm install zustand @tanstack/react-query socket.io-client axios`
2. Run `npm install -D class-variance-authority clsx tailwind-merge`
3. Verify installation: `npm list zustand @tanstack/react-query socket.io-client axios`
4. Update package.json with exact versions for reproducibility

**Dependencies:**
- Node.js 18+ and npm 9+
- Existing React 19.2.0 and TypeScript 5.9.3 setup

**Testing Requirements:**
- Verify all packages are installed: `npm list`
- Check for peer dependency warnings: `npm audit`
- Verify TypeScript types are available: `npm run build`

**Deliverables:**
- Updated package.json with new dependencies
- Updated package-lock.json
- No breaking changes to existing code

---

#### 0.7 Create utility functions

**Status:** ✅ COMPLETED

**Description:**
Create a comprehensive set of utility functions for common operations including class name merging, formatting (currency, phone, dates), date calculations, validation, and API client setup. These utilities will be used throughout the application for consistent behavior and reduced code duplication.

**Technical Specifications:**

**lib/utils/cn.ts:**
- Merge Tailwind CSS classes without conflicts
- Use clsx and tailwind-merge for proper merging
- Support conditional classes
- Export as default function

**lib/utils/format.ts:**
- formatCurrency(amount, currency): Format number as currency (NGN, USD, etc.)
- formatPhone(phone): Format phone number (e.g., +234 123 456 7890)
- formatDate(date, format): Format date (e.g., "Jan 15, 2024")
- formatTime(date): Format time (e.g., "2:30 PM")
- formatDateTime(date): Format date and time
- formatDuration(minutes): Format duration (e.g., "1h 30m")

**lib/utils/date.ts:**
- addDays(date, days): Add days to date
- addHours(date, hours): Add hours to date
- addMinutes(date, minutes): Add minutes to date
- isSameDay(date1, date2): Check if dates are same day
- isToday(date): Check if date is today
- isTomorrow(date): Check if date is tomorrow
- getWeekStart(date): Get start of week
- getWeekEnd(date): Get end of week
- getMonthStart(date): Get start of month
- getMonthEnd(date): Get end of month
- getDayName(date): Get day name (Monday, Tuesday, etc.)
- getMonthName(date): Get month name (January, February, etc.)

**lib/utils/validation.ts:**
- isValidEmail(email): Validate email format
- isValidPhone(phone): Validate phone format
- isValidURL(url): Validate URL format
- isValidCurrency(amount): Validate currency amount
- isValidDate(date): Validate date format
- isStrongPassword(password): Validate password strength

**lib/utils/api.ts:**
- Create Axios instance with base URL
- Add request interceptor for JWT token
- Add response interceptor for error handling
- Add retry logic for failed requests
- Export configured Axios instance

**Acceptance Criteria:**
1. WHEN using cn() function, THE Tailwind CSS classes SHALL merge without conflicts
2. WHEN using format functions, THE output SHALL match expected format
3. WHEN using date functions, THE calculations SHALL be accurate
4. WHEN using validation functions, THE validation SHALL correctly identify valid/invalid inputs
5. WHEN using API client, THE JWT token SHALL be automatically added to requests

**Implementation Details:**
1. Create lib/utils/ directory
2. Create cn.ts with clsx and tailwind-merge integration
3. Create format.ts with all formatting functions
4. Create date.ts with all date utility functions
5. Create validation.ts with all validation functions
6. Create api.ts with Axios configuration
7. Export all utilities from lib/utils/index.ts
8. Add TypeScript types for all functions

**Dependencies:**
- clsx 2.0+
- tailwind-merge 2.2+
- Axios 1.6+
- date-fns 2.30+ (optional, for advanced date operations)

**Testing Requirements:**
- Unit tests for each utility function
- Test edge cases (empty strings, null values, invalid inputs)
- Test formatting with different locales
- Test date calculations across month/year boundaries

**Deliverables:**
- src/lib/utils/cn.ts
- src/lib/utils/format.ts
- src/lib/utils/date.ts
- src/lib/utils/validation.ts
- src/lib/utils/api.ts
- src/lib/utils/index.ts (barrel export)
- Unit tests for all utilities

---

#### 0.8 Set up Zustand stores

**Status:** ✅ COMPLETED

**Description:**
Create Zustand stores for global state management including authentication (user, token, permissions), tenant context (current tenant, settings), UI state (theme, modals, notifications), and user preferences (language, timezone). Zustand provides a lightweight, simple alternative to Redux with minimal boilerplate.

**Technical Specifications:**

**stores/auth.ts:**
- State: user (User | null), token (string | null), permissions (string[]), isLoading (boolean)
- Actions: setUser(user), setToken(token), setPermissions(permissions), logout(), updateUser(user)
- Selectors: isAuthenticated, hasPermission(permission), user, token
- Persistence: Save token to localStorage, restore on app load

**stores/tenant.ts:**
- State: currentTenant (Tenant | null), settings (TenantSettings | null), isLoading (boolean)
- Actions: setTenant(tenant), setSettings(settings), updateSettings(settings)
- Selectors: tenantId, tenantName, isFeatureEnabled(feature)
- Persistence: Save current tenant to localStorage

**stores/ui.ts:**
- State: theme (string), isDarkMode (boolean), modals (Record<string, boolean>), notifications (Notification[])
- Actions: setTheme(theme), toggleDarkMode(), openModal(name), closeModal(name), addNotification(notification), removeNotification(id)
- Selectors: currentTheme, isDarkMode, isModalOpen(name), notifications
- Persistence: Save theme preference to localStorage

**stores/preferences.ts:**
- State: language (string), timezone (string), dateFormat (string), timeFormat (string)
- Actions: setLanguage(language), setTimezone(timezone), setDateFormat(format), setTimeFormat(format)
- Selectors: language, timezone, dateFormat, timeFormat
- Persistence: Save preferences to localStorage

**Acceptance Criteria:**
1. WHEN setting user in auth store, THE user SHALL be persisted to localStorage
2. WHEN logging out, THE auth store SHALL clear user, token, and permissions
3. WHEN changing theme, THE theme SHALL update in UI store and persist to localStorage
4. WHEN opening modal, THE modal state SHALL update in UI store
5. WHEN accessing store selectors, THE values SHALL be correctly computed

**Implementation Details:**
1. Create stores/ directory
2. Create auth.ts with authentication store
3. Create tenant.ts with tenant context store
4. Create ui.ts with UI state store
5. Create preferences.ts with user preferences store
6. Create stores/index.ts for barrel exports
7. Add TypeScript types for all stores
8. Implement localStorage persistence
9. Add devtools middleware for debugging

**Dependencies:**
- Zustand 4.4+
- TypeScript 5.9.3+

**Testing Requirements:**
- Unit tests for store actions
- Test state updates
- Test localStorage persistence
- Test selectors
- Test concurrent updates

**Deliverables:**
- src/stores/auth.ts
- src/stores/tenant.ts
- src/stores/ui.ts
- src/stores/preferences.ts
- src/stores/index.ts
- Unit tests for all stores

---

#### 0.9 Configure React Query

**Status:** ✅ COMPLETED

**Description:**
Set up React Query (TanStack Query) for powerful data fetching, caching, and synchronization. Create custom hooks for all major resources (appointments, customers, staff, services, invoices) to provide a consistent interface for data fetching throughout the application.

**Technical Specifications:**

**Query Client Configuration:**
- Default staleTime: 5 minutes
- Default cacheTime: 10 minutes
- Default retry: 3 attempts with exponential backoff
- Default refetchOnWindowFocus: true
- Default refetchOnReconnect: true
- Devtools enabled for debugging

**Custom Hooks:**
- useAppointments(filters): Fetch appointments with filtering
- useAppointment(id): Fetch single appointment
- useCreateAppointment(): Mutation for creating appointment
- useUpdateAppointment(): Mutation for updating appointment
- useDeleteAppointment(): Mutation for deleting appointment
- useCustomers(filters): Fetch customers with filtering
- useCustomer(id): Fetch single customer
- useStaff(filters): Fetch staff with filtering
- useServices(filters): Fetch services with filtering
- useInvoices(filters): Fetch invoices with filtering
- usePayments(filters): Fetch payments with filtering

**Acceptance Criteria:**
1. WHEN fetching data, THE data SHALL be cached and reused on subsequent requests
2. WHEN data becomes stale, THE data SHALL be automatically refetched in background
3. WHEN mutation succeeds, THE related queries SHALL be automatically invalidated
4. WHEN network is offline, THE cached data SHALL be returned
5. WHEN using React Query devtools, THE query state SHALL be visible for debugging

**Implementation Details:**
1. Create lib/react-query.ts with QueryClient configuration
2. Create hooks/useAppointments.ts with appointment hooks
3. Create hooks/useCustomers.ts with customer hooks
4. Create hooks/useStaff.ts with staff hooks
5. Create hooks/useServices.ts with service hooks
6. Create hooks/useInvoices.ts with invoice hooks
7. Create hooks/usePayments.ts with payment hooks
8. Wrap app with QueryClientProvider
9. Add React Query devtools for development

**Dependencies:**
- @tanstack/react-query 5.28+
- @tanstack/react-query-devtools 5.28+ (dev dependency)

**Testing Requirements:**
- Unit tests for custom hooks
- Test data fetching and caching
- Test mutations and invalidation
- Test error handling
- Test loading states

**Deliverables:**
- src/lib/react-query.ts
- src/hooks/useAppointments.ts
- src/hooks/useCustomers.ts
- src/hooks/useStaff.ts
- src/hooks/useServices.ts
- src/hooks/useInvoices.ts
- src/hooks/usePayments.ts
- Updated App.tsx with QueryClientProvider
- Unit tests for all hooks

---

#### 0.10 Set up Socket.io client

**Status:** ✅ COMPLETED

**Description:**
Configure Socket.io client for real-time communication with the backend. Create a Socket.io service and custom hook for managing real-time events including appointment updates, notifications, and presence tracking.

**Technical Specifications:**

**services/socket.ts:**
- Initialize Socket.io connection with JWT authentication
- Reconnection strategy: exponential backoff, max 10 attempts
- Automatic reconnection on network change
- Event handlers for common events
- Emit methods for sending events to server

**hooks/useSocket.ts:**
- Hook for accessing Socket.io instance
- Hook for listening to specific events
- Hook for emitting events
- Hook for connection status
- Automatic cleanup on unmount

**Real-time Events:**
- appointment:created - New appointment created
- appointment:updated - Appointment updated
- appointment:cancelled - Appointment cancelled
- notification:new - New notification
- presence:online - User came online
- presence:offline - User went offline
- queue:updated - Waiting room queue updated

**Acceptance Criteria:**
1. WHEN connecting to Socket.io, THE connection SHALL authenticate with JWT token
2. WHEN receiving real-time event, THE event handler SHALL be called immediately
3. WHEN network disconnects, THE Socket.io client SHALL automatically reconnect
4. WHEN component unmounts, THE event listeners SHALL be cleaned up
5. WHEN emitting event, THE event SHALL be sent to server

**Implementation Details:**
1. Create services/socket.ts with Socket.io configuration
2. Create hooks/useSocket.ts with Socket.io hook
3. Create hooks/useSocketEvent.ts for listening to events
4. Create hooks/useSocketEmit.ts for emitting events
5. Add Socket.io connection initialization in App.tsx
6. Add error handling and logging

**Dependencies:**
- socket.io-client 4.7+

**Testing Requirements:**
- Unit tests for Socket.io service
- Test connection and authentication
- Test event emission and reception
- Test reconnection logic
- Test cleanup on unmount

**Deliverables:**
- src/services/socket.ts
- src/hooks/useSocket.ts
- src/hooks/useSocketEvent.ts
- src/hooks/useSocketEmit.ts
- Unit tests for Socket.io integration

---

#### 0.11 Create project structure

**Status:** ✅ COMPLETED

**Description:**
Create the complete project directory structure for organizing components, pages, layouts, services, and utilities. This structure follows best practices for scalability and maintainability.

**Technical Specifications:**

**Directory Structure:**
```
src/
├── components/
│   ├── ui/              (35+ UI components)
│   ├── icons/           (100+ SVG icons)
│   ├── layout/          (Layout components)
│   └── common/          (Reusable components)
├── pages/
│   ├── auth/            (Login, signup, password reset)
│   ├── dashboard/       (Dashboard pages)
│   ├── appointments/    (Appointment pages)
│   ├── customers/       (Customer pages)
│   ├── staff/           (Staff pages)
│   ├── services/        (Service pages)
│   ├── invoices/        (Invoice pages)
│   ├── reports/         (Report pages)
│   └── settings/        (Settings pages)
├── layouts/
│   ├── MainLayout.tsx   (Main app layout)
│   ├── AuthLayout.tsx   (Auth pages layout)
│   └── AdminLayout.tsx  (Admin pages layout)
├── stores/              (Zustand stores)
├── hooks/               (Custom React hooks)
├── services/            (API client and Socket.io)
├── lib/
│   ├── utils/           (Utility functions)
│   ├── themes/          (Theme definitions)
│   └── react-query.ts   (React Query config)
├── types/               (TypeScript types)
├── App.tsx              (Main app component)
├── main.tsx             (Entry point)
└── index.css            (Global styles)
```

**Acceptance Criteria:**
1. WHEN importing from pages, components, or hooks, THE imports SHALL work correctly
2. WHEN running the development server, THE project structure SHALL not cause errors
3. WHEN adding new features, THE structure SHALL accommodate new pages and components
4. WHEN organizing code, THE structure SHALL follow the defined conventions

**Implementation Details:**
1. Create all directories listed above
2. Create index.ts files for barrel exports in each directory
3. Create placeholder components for each page
4. Create layout components
5. Update App.tsx with routing structure
6. Add TypeScript path aliases in tsconfig.json for easier imports

**Dependencies:**
- React Router v7+ (for routing)

**Testing Requirements:**
- Verify all directories are created
- Verify imports work correctly
- Verify no circular dependencies

**Deliverables:**
- Complete project directory structure
- Placeholder components for all pages
- Layout components
- Updated tsconfig.json with path aliases
- Updated App.tsx with routing

---

#### 0.12 Write unit tests for utility functions

**Status:** ✅ COMPLETED

**Description:**
Write comprehensive unit tests for all utility functions created in task 0.7. Tests should cover normal cases, edge cases, and error conditions to ensure utilities work correctly across the application.

**Technical Specifications:**

**Test Framework:** Jest with React Testing Library

**Test Coverage:**
- cn() function: Test class merging, conditional classes, Tailwind CSS conflicts
- format.ts: Test currency, phone, date, time, duration formatting
- date.ts: Test date calculations, day/month names, week/month boundaries
- validation.ts: Test email, phone, URL, currency, date, password validation
- api.ts: Test Axios configuration, interceptors, error handling

**Acceptance Criteria:**
1. WHEN running tests, THE test suite SHALL pass with >90% coverage
2. WHEN testing edge cases, THE utilities SHALL handle null, undefined, empty strings
3. WHEN testing formatting, THE output SHALL match expected format
4. WHEN testing validation, THE validation SHALL correctly identify valid/invalid inputs
5. WHEN testing API client, THE interceptors SHALL work correctly

**Implementation Details:**
1. Create src/lib/utils/__tests__/ directory
2. Create test files for each utility module
3. Write tests for all functions
4. Test edge cases and error conditions
5. Aim for >90% code coverage
6. Run tests with `npm run test`

**Dependencies:**
- Jest 29+
- @testing-library/react 14+

**Testing Requirements:**
- Run `npm run test` to execute tests
- Run `npm run test:coverage` to check coverage
- All tests should pass
- Coverage should be >90%

**Deliverables:**
- src/lib/utils/__tests__/cn.test.ts
- src/lib/utils/__tests__/format.test.ts
- src/lib/utils/__tests__/date.test.ts
- src/lib/utils/__tests__/validation.test.ts
- src/lib/utils/__tests__/api.test.ts
- Updated package.json with test scripts

### 1. Project Setup and Infrastructure

**Status: ✅ 100% COMPLETE**

#### 1.1 Initialize Python project with FastAPI and Docker

**Status:** ✅ COMPLETED

**Description:**
Set up the backend project structure with FastAPI, Python 3.11+, and Docker containerization. This task establishes the foundation for the entire backend application including project organization, dependency management, Docker configuration, and FastAPI middleware setup. The project will be containerized for consistent development and production environments.

**Technical Specifications:**

**Project Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              (FastAPI app initialization)
│   ├── config.py            (Configuration management)
│   ├── middleware.py        (CORS, logging, error handling)
│   ├── models/              (Mongoengine models)
│   ├── routes/              (API endpoints)
│   ├── services/            (Business logic)
│   ├── schemas/             (Pydantic schemas)
│   ├── utils/               (Utility functions)
│   └── tasks/               (Celery tasks)
├── tests/
│   ├── __init__.py
│   ├── conftest.py          (Pytest fixtures)
│   ├── unit/                (Unit tests)
│   └── integration/         (Integration tests)
├── migrations/              (Database migrations)
├── docker/
│   ├── Dockerfile           (Python application)
│   └── docker-compose.yml   (All services)
├── config/
│   ├── development.py       (Dev configuration)
│   ├── staging.py           (Staging configuration)
│   └── production.py        (Prod configuration)
├── requirements.txt         (Python dependencies)
├── .env.example             (Environment variables template)
├── .dockerignore            (Docker ignore file)
└── README.md                (Project documentation)
```

**Dependencies (requirements.txt):**
- fastapi==0.104.1
- uvicorn==0.24.0
- mongoengine==0.27.0
- celery==5.3.4
- redis==5.0.1
- pydantic==2.5.0
- pydantic-settings==2.1.0
- python-dotenv==1.0.0
- python-jose==3.3.0
- passlib==1.7.4
- bcrypt==4.1.1
- pytest==7.4.3
- pytest-asyncio==0.21.1
- httpx==0.25.2
- hypothesis==6.92.1

**FastAPI Configuration:**
- CORS middleware for frontend communication
- Request logging middleware
- Error handling middleware with custom exception handlers
- Request ID tracking for debugging
- Environment-based configuration (dev, staging, prod)
- API versioning (/v1/)
- OpenAPI/Swagger documentation

**Acceptance Criteria:**
1. WHEN running `python -m uvicorn app.main:app --reload`, THE FastAPI server SHALL start on port 8000
2. WHEN accessing http://localhost:8000/docs, THE Swagger documentation SHALL be available
3. WHEN making a request, THE request ID SHALL be logged for tracing
4. WHEN an error occurs, THE error response SHALL follow standard format with error code and message
5. WHEN running tests, THE test suite SHALL execute without errors

**Implementation Details:**
1. Create backend/ directory structure as specified
2. Create requirements.txt with all dependencies
3. Create app/main.py with FastAPI initialization
4. Create app/config.py with environment-based configuration
5. Create app/middleware.py with CORS, logging, error handling
6. Create Dockerfile for Python application
7. Create .env.example with required environment variables
8. Create README.md with setup instructions
9. Verify project structure with `tree` command
10. Test FastAPI startup with `uvicorn app.main:app --reload`

**Dependencies:**
- Python 3.11+
- pip package manager
- Docker and Docker Compose

**Testing Requirements:**
- Verify FastAPI server starts without errors
- Verify Swagger documentation is accessible
- Verify CORS middleware works correctly
- Verify error handling middleware works correctly
- Verify logging middleware logs requests

**Deliverables:**
- Backend project directory structure
- requirements.txt with all dependencies
- app/main.py with FastAPI initialization
- app/config.py with configuration management
- app/middleware.py with middleware setup
- Dockerfile for Python application
- .env.example with environment variables
- README.md with setup instructions

---

#### 1.2 Write property test for project initialization

**Status:** ✅ COMPLETED

**Description:**
Write property-based tests to verify that the FastAPI project initializes correctly with consistent configuration across different environments. These tests ensure that configuration is properly loaded and applied regardless of environment variables.

**Technical Specifications:**

**Property: Project Configuration Consistency**
- **Validates: Requirements 1.1**
- **Test Framework:** Hypothesis (Python property-based testing)
- **Hypothesis Strategy:** Generate random environment configurations and verify FastAPI initializes correctly

**Test Cases:**
1. Configuration loads correctly from environment variables
2. Default values are applied when environment variables are missing
3. Configuration is consistent across multiple initialization attempts
4. Invalid configuration values are rejected with appropriate errors
5. Configuration values are properly typed and validated

**Acceptance Criteria:**
1. WHEN running property tests, THE tests SHALL pass with >100 examples
2. WHEN configuration is invalid, THE tests SHALL detect the error
3. WHEN environment variables change, THE configuration SHALL update correctly
4. WHEN running tests multiple times, THE results SHALL be consistent

**Implementation Details:**
1. Create tests/unit/test_config.py
2. Use Hypothesis to generate random environment configurations
3. Test configuration loading from environment
4. Test default values
5. Test configuration validation
6. Test configuration consistency

**Dependencies:**
- pytest 7.4.3+
- hypothesis 6.92.1+

**Testing Requirements:**
- Run `pytest tests/unit/test_config.py -v`
- All tests should pass
- Coverage should be >90%

**Deliverables:**
- tests/unit/test_config.py with property-based tests

---

#### 1.3 Set up MongoDB Atlas connection and Mongoengine ODM

**Status:** ✅ COMPLETED

**Description:**
Configure MongoDB Atlas connection and set up Mongoengine as the Object Document Mapper (ODM). This task establishes the database layer with proper connection pooling, tenant context middleware, and base document class for all entities. MongoDB Atlas is a managed cloud service requiring no local setup.

**Technical Specifications:**

**MongoDB Atlas Setup:**
- Create MongoDB Atlas account and cluster
- Configure IP whitelist for application servers
- Create database user with appropriate permissions
- Generate connection string (mongodb+srv://...)
- Enable automatic backups and point-in-time recovery

**Mongoengine Configuration:**
- Connection pooling: max_pool_size=50, min_pool_size=10
- Connection timeout: 5 seconds
- Server selection timeout: 5 seconds
- Retry writes: enabled
- Replica set: enabled for high availability

**Base Document Class:**
```python
class BaseDocument(Document):
    tenant_id: ObjectIdField = ObjectIdField(required=True)
    created_at: DateTimeField = DateTimeField(default=datetime.utcnow)
    updated_at: DateTimeField = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'abstract': True,
        'indexes': [
            ('tenant_id', '_id'),
            ('tenant_id', 'created_at'),
        ]
    }
```

**Tenant Context Middleware:**
- Extract tenant_id from JWT token
- Store tenant_id in request context
- Automatically filter queries by tenant_id
- Prevent cross-tenant data access

**Acceptance Criteria:**
1. WHEN connecting to MongoDB Atlas, THE connection SHALL succeed within 5 seconds
2. WHEN creating a document, THE tenant_id SHALL be automatically set from context
3. WHEN querying documents, THE results SHALL be automatically filtered by tenant_id
4. WHEN accessing data from different tenant, THE query SHALL return empty results
5. WHEN connection fails, THE application SHALL retry with exponential backoff

**Implementation Details:**
1. Create MongoDB Atlas cluster and configure connection
2. Create app/db.py with Mongoengine configuration
3. Create app/models/base.py with BaseDocument class
4. Create app/middleware/tenant.py with tenant context middleware
5. Create app/models/__init__.py with model imports
6. Update app/main.py to initialize database connection
7. Add connection pooling configuration
8. Add error handling for connection failures
9. Test connection with sample query

**Dependencies:**
- mongoengine 0.27.0+
- pymongo 4.6+
- MongoDB Atlas account

**Testing Requirements:**
- Verify connection to MongoDB Atlas succeeds
- Verify documents are created with tenant_id
- Verify queries are filtered by tenant_id
- Verify cross-tenant queries return empty results
- Verify connection pooling works correctly

**Deliverables:**
- app/db.py with Mongoengine configuration
- app/models/base.py with BaseDocument class
- app/middleware/tenant.py with tenant context middleware
- Updated app/main.py with database initialization
- MongoDB Atlas cluster configuration

---

#### 1.4 Write property test for database connection

**Status:** ✅ COMPLETED

**Description:**
Write property-based tests to verify database connection reliability and consistency. These tests ensure that the database connection handles various scenarios including connection failures, timeouts, and recovery.

**Technical Specifications:**

**Property: Database Connection Reliability**
- **Validates: Requirements 1.1**
- **Test Framework:** Hypothesis with pytest
- **Hypothesis Strategy:** Generate random connection scenarios and verify proper handling

**Test Cases:**
1. Connection succeeds with valid credentials
2. Connection fails gracefully with invalid credentials
3. Connection retries on temporary failure
4. Connection timeout is handled properly
5. Connection pool is properly managed
6. Multiple concurrent connections work correctly

**Acceptance Criteria:**
1. WHEN running property tests, THE tests SHALL pass with >100 examples
2. WHEN connection fails, THE application SHALL retry with exponential backoff
3. WHEN connection succeeds, THE connection pool SHALL be properly initialized
4. WHEN multiple connections are made, THE pool SHALL manage them efficiently

**Implementation Details:**
1. Create tests/unit/test_database.py
2. Use Hypothesis to generate connection scenarios
3. Test successful connections
4. Test connection failures and retries
5. Test connection pooling
6. Test concurrent connections

**Dependencies:**
- pytest 7.4.3+
- hypothesis 6.92.1+
- mongoengine 0.27.0+

**Testing Requirements:**
- Run `pytest tests/unit/test_database.py -v`
- All tests should pass
- Coverage should be >90%

**Deliverables:**
- tests/unit/test_database.py with property-based tests

---

#### 1.5 Configure Redis cache and session management

**Status:** ✅ COMPLETED

**Description:**
Set up Redis for caching and session management. Redis will store user sessions, cached data, and temporary reservations. This task configures Redis connection, implements session storage, and sets up cache key patterns with appropriate TTLs.

**Technical Specifications:**

**Redis Configuration:**
- Host: redis (Docker service name)
- Port: 6379
- Database: 0 (sessions), 1 (cache), 2 (locks)
- Connection pooling: max_connections=50
- Timeout: 5 seconds
- Retry on connection failure: 3 attempts

**Session Storage:**
- Session key format: `session:{session_id}`
- Session TTL: 24 hours
- Session data: user_id, tenant_id, permissions, created_at
- Session invalidation on logout

**Cache Key Patterns:**
- Services: `cache:services:{tenant_id}` (TTL: 1 hour)
- Staff: `cache:staff:{tenant_id}` (TTL: 10 minutes)
- Availability: `cache:availability:{staff_id}:{date}` (TTL: 1 minute)
- Permissions: `cache:permissions:{user_id}` (TTL: 5 minutes)
- Customers: `cache:customers:{tenant_id}` (TTL: 10 minutes)

**Cache Invalidation:**
- Time-based: TTL expiration
- Event-based: Invalidate on data changes
- Manual: Invalidate specific keys on demand

**Acceptance Criteria:**
1. WHEN storing session in Redis, THE session SHALL be retrievable within 100ms
2. WHEN session expires, THE session SHALL be automatically removed
3. WHEN caching data, THE cache hit rate SHALL be >80%
4. WHEN data changes, THE cache SHALL be invalidated
5. WHEN Redis is unavailable, THE application SHALL gracefully degrade

**Implementation Details:**
1. Create app/cache.py with Redis configuration
2. Create app/services/session.py with session management
3. Create app/services/cache.py with cache operations
4. Create Redis service in docker-compose.yml
5. Add Redis connection pooling
6. Implement cache invalidation logic
7. Add error handling for Redis failures
8. Test cache operations

**Dependencies:**
- redis 5.0.1+
- Docker and Docker Compose

**Testing Requirements:**
- Verify Redis connection succeeds
- Verify session storage and retrieval
- Verify cache operations
- Verify cache invalidation
- Verify graceful degradation when Redis is unavailable

**Deliverables:**
- app/cache.py with Redis configuration
- app/services/session.py with session management
- app/services/cache.py with cache operations
- Updated docker-compose.yml with Redis service
- Unit tests for cache operations

---

#### 1.6 Set up RabbitMQ and Celery for async task processing

**Status:** ✅ COMPLETED

**Description:**
Configure RabbitMQ as the message broker and Celery for asynchronous task processing. This enables the application to handle long-running tasks (email sending, notifications, report generation) without blocking API requests.

**Technical Specifications:**

**RabbitMQ Configuration:**
- Host: rabbitmq (Docker service name)
- Port: 5672 (AMQP), 15672 (Management UI)
- Default user: guest / guest
- Virtual host: /
- Queues: notifications, emails, reports, webhooks

**Celery Configuration:**
- Broker: amqp://guest:guest@rabbitmq:5672//
- Result backend: redis://redis:6379/1
- Task serialization: JSON
- Task time limit: 30 minutes
- Task soft time limit: 25 minutes
- Task retry: 3 attempts with exponential backoff

**Task Queues:**
- notifications: High priority, real-time notifications
- emails: Medium priority, email sending
- reports: Low priority, report generation
- webhooks: Medium priority, webhook delivery

**Celery Tasks:**
- send_email(to, subject, template, context)
- send_sms(phone, message)
- send_notification(user_id, title, message)
- generate_report(report_type, filters)
- process_webhook(event, data)

**Acceptance Criteria:**
1. WHEN submitting a task, THE task SHALL be queued in RabbitMQ
2. WHEN Celery worker starts, THE worker SHALL process tasks from queue
3. WHEN task fails, THE task SHALL be retried with exponential backoff
4. WHEN task completes, THE result SHALL be stored in Redis
5. WHEN accessing RabbitMQ management UI, THE queues and tasks SHALL be visible

**Implementation Details:**
1. Create app/tasks.py with Celery configuration
2. Create app/tasks/notifications.py with notification tasks
3. Create app/tasks/emails.py with email tasks
4. Create app/tasks/reports.py with report tasks
5. Create app/tasks/webhooks.py with webhook tasks
6. Add RabbitMQ service to docker-compose.yml
7. Add Celery worker service to docker-compose.yml
8. Implement task retry logic
9. Add error handling and logging
10. Test task submission and processing

**Dependencies:**
- celery 5.3.4+
- redis 5.0.1+
- Docker and Docker Compose

**Testing Requirements:**
- Verify RabbitMQ connection succeeds
- Verify Celery worker starts and processes tasks
- Verify task retry logic works
- Verify task results are stored in Redis
- Verify error handling works correctly

**Deliverables:**
- app/tasks.py with Celery configuration
- app/tasks/notifications.py with notification tasks
- app/tasks/emails.py with email tasks
- app/tasks/reports.py with report tasks
- app/tasks/webhooks.py with webhook tasks
- Updated docker-compose.yml with RabbitMQ and Celery worker
- Unit tests for task processing

---

#### 1.7 Create Docker Compose configuration for local development

**Status:** ✅ COMPLETED

**Description:**
Create a comprehensive Docker Compose configuration that orchestrates all services for local development. This includes FastAPI backend, React frontend, MongoDB Atlas connection, Redis cache, RabbitMQ message broker, and Celery worker. The configuration enables developers to run the entire stack with a single command.

**Technical Specifications:**

**docker-compose.yml Services:**

**FastAPI Backend:**
- Image: salon-api:latest (built from Dockerfile)
- Port: 8000:8000
- Environment: Development configuration
- Volumes: Source code for hot reload
- Depends on: redis, rabbitmq
- Health check: HTTP GET /health

**React Frontend:**
- Image: salon-frontend:latest (built from Dockerfile)
- Port: 3000:3000
- Environment: API_URL=http://localhost:8000
- Volumes: Source code for hot reload
- Depends on: api

**Redis:**
- Image: redis:7-alpine
- Port: 6379:6379
- Volumes: redis-data (persistence)
- Health check: redis-cli ping

**RabbitMQ:**
- Image: rabbitmq:3.13-management-alpine
- Port: 5672:5672 (AMQP), 15672:15672 (Management UI)
- Environment: RABBITMQ_DEFAULT_USER=guest, RABBITMQ_DEFAULT_PASS=guest
- Volumes: rabbitmq-data (persistence)
- Health check: rabbitmq-diagnostics -q ping

**Celery Worker:**
- Image: salon-api:latest (same as backend)
- Command: celery -A app.tasks worker --loglevel=info
- Environment: Development configuration
- Depends on: redis, rabbitmq
- Volumes: Source code for hot reload

**Environment Variables:**
- ENVIRONMENT=development
- DATABASE_URL=mongodb+srv://...
- REDIS_URL=redis://redis:6379/0
- RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//
- JWT_SECRET_KEY=dev-secret-key
- API_URL=http://localhost:8000
- FRONTEND_URL=http://localhost:3000

**Volumes:**
- redis-data: Redis persistence
- rabbitmq-data: RabbitMQ persistence

**Networks:**
- salon-network: Internal network for service communication

**Acceptance Criteria:**
1. WHEN running `docker-compose up`, ALL services SHALL start successfully
2. WHEN accessing http://localhost:3000, THE frontend SHALL load
3. WHEN accessing http://localhost:8000/docs, THE API documentation SHALL be available
4. WHEN accessing http://localhost:15672, THE RabbitMQ management UI SHALL be available
5. WHEN stopping services, ALL containers SHALL stop gracefully

**Implementation Details:**
1. Create docker-compose.yml with all services
2. Create Dockerfile for FastAPI backend
3. Create Dockerfile for React frontend (optional, can use npm run dev)
4. Create .env.development with development environment variables
5. Create .dockerignore to exclude unnecessary files
6. Add health checks for all services
7. Configure volume mounts for hot reload
8. Set up service dependencies
9. Test docker-compose up and verify all services start
10. Document setup instructions in README.md

**Dependencies:**
- Docker 20.10+
- Docker Compose 2.0+

**Testing Requirements:**
- Run `docker-compose up` and verify all services start
- Verify frontend loads at http://localhost:3000
- Verify API is accessible at http://localhost:8000
- Verify RabbitMQ management UI is accessible at http://localhost:15672
- Verify Redis is accessible at localhost:6379
- Verify Celery worker processes tasks
- Run `docker-compose down` and verify graceful shutdown

**Deliverables:**
- docker-compose.yml with all services
- Dockerfile for FastAPI backend
- .env.development with development environment variables
- .dockerignore file
- Updated README.md with Docker setup instructions
- docker-compose.override.yml for local development overrides (optional)

### 2. Multi-Tenant Architecture and Data Isolation

#### 2.1 Implement tenant context and isolation layer

**Status:** ✅ COMPLETED

**Description:**
Implement the core multi-tenant architecture with automatic data isolation. This task creates the Tenant document model, tenant context middleware that extracts tenant_id from JWT tokens, and a base Document class that all entities inherit from. The isolation layer ensures that all queries automatically filter by tenant_id, preventing accidental cross-tenant data access.

**Technical Specifications:**

**Tenant Document Model:**
```python
class Tenant(Document):
    name: StringField(required=True, max_length=255)
    subscription_tier: StringField(choices=['starter', 'professional', 'enterprise'], default='starter')
    status: StringField(choices=['active', 'suspended', 'deleted'], default='active')
    region: StringField(default='us-east-1')
    created_at: DateTimeField(default=datetime.utcnow)
    updated_at: DateTimeField(default=datetime.utcnow)
    deleted_at: DateTimeField(null=True)
    
    meta = {
        'collection': 'tenants',
        'indexes': ['created_at', 'status']
    }
```

**Tenant Context Middleware:**
- Extract tenant_id from JWT token claims
- Store tenant_id in request context (g object or context var)
- Make tenant_id available to all route handlers
- Validate tenant_id on every request
- Handle missing or invalid tenant_id with 401 Unauthorized

**Base Document Class:**
- All entities inherit from BaseDocument
- BaseDocument includes tenant_id field (required)
- BaseDocument includes created_at and updated_at timestamps
- BaseDocument includes compound indexes for tenant_id + _id

**Query Filtering Decorator:**
- Create @tenant_isolated decorator for route handlers
- Decorator automatically filters queries by tenant_id
- Decorator validates user belongs to tenant
- Decorator prevents cross-tenant data access

**Acceptance Criteria:**
1. WHEN creating a document, THE tenant_id SHALL be automatically set from request context
2. WHEN querying documents, THE results SHALL be automatically filtered by tenant_id
3. WHEN accessing data from different tenant, THE query SHALL return empty results
4. WHEN tenant_id is missing from JWT, THE request SHALL return 401 Unauthorized
5. WHEN tenant_id is invalid, THE request SHALL return 403 Forbidden

**Implementation Details:**
1. Create app/models/tenant.py with Tenant model
2. Create app/middleware/tenant_context.py with tenant context middleware
3. Update app/models/base.py with tenant_id field
4. Create app/decorators/tenant_isolated.py with isolation decorator
5. Create app/context.py with context management (g object or context vars)
6. Update app/main.py to register tenant context middleware
7. Add tenant_id extraction from JWT token
8. Add error handling for missing/invalid tenant_id
9. Test tenant isolation with multiple tenants

**Dependencies:**
- mongoengine 0.27.0+
- fastapi 0.104.1+
- python-jose 3.3.0+

**Testing Requirements:**
- Verify tenant_id is extracted from JWT token
- Verify documents are created with tenant_id
- Verify queries are filtered by tenant_id
- Verify cross-tenant queries return empty results
- Verify missing tenant_id returns 401
- Verify invalid tenant_id returns 403

**Deliverables:**
- app/models/tenant.py with Tenant model
- app/middleware/tenant_context.py with tenant context middleware
- Updated app/models/base.py with tenant_id field
- app/decorators/tenant_isolated.py with isolation decorator
- app/context.py with context management
- Updated app/main.py with middleware registration
- Unit tests for tenant isolation

---

#### 2.2 Write property test for tenant isolation

**Status:** ✅ COMPLETED

**Description:**
Write comprehensive property-based tests to verify that tenant isolation works correctly across all scenarios. These tests ensure that no cross-tenant data leakage occurs and that the isolation layer is robust against various attack vectors.

**Technical Specifications:**

**Property 1: No Cross-Tenant Data Leakage**
- **Validates: Requirements 1.1, 1.2, 1.3**
- **Test Framework:** Hypothesis with pytest
- **Hypothesis Strategy:** Generate random tenants, users, and queries; verify isolation

**Test Cases:**
1. User from Tenant A cannot access data from Tenant B
2. Queries automatically filter by tenant_id
3. Cross-tenant queries return empty results
4. Tenant context is properly isolated between requests
5. Concurrent requests from different tenants don't interfere
6. Deleted tenant data is not accessible

**Acceptance Criteria:**
1. WHEN running property tests, THE tests SHALL pass with >100 examples
2. WHEN user from Tenant A queries Tenant B data, THE query SHALL return empty results
3. WHEN multiple concurrent requests occur, THE isolation SHALL be maintained
4. WHEN tenant is deleted, THE data SHALL not be accessible

**Implementation Details:**
1. Create tests/unit/test_tenant_isolation.py
2. Use Hypothesis to generate random tenants and users
3. Test cross-tenant query prevention
4. Test concurrent request isolation
5. Test deleted tenant data access
6. Test tenant context middleware

**Dependencies:**
- pytest 7.4.3+
- hypothesis 6.92.1+
- mongoengine 0.27.0+

**Testing Requirements:**
- Run `pytest tests/unit/test_tenant_isolation.py -v`
- All tests should pass
- Coverage should be >90%

**Deliverables:**
- tests/unit/test_tenant_isolation.py with property-based tests

---

#### 2.3 Implement MongoDB indexes for tenant isolation

**Status:** ✅ COMPLETED

**Description:**
Create MongoDB indexes to optimize query performance for tenant-isolated queries. Proper indexing is critical for performance as every query includes a tenant_id filter. This task creates compound indexes on all collections to ensure fast lookups.

**Technical Specifications:**

**Index Strategy:**
- Compound indexes on all collections: {tenant_id: 1, _id: 1}
- Time-series indexes: {tenant_id: 1, created_at: -1}
- Status filtering indexes: {tenant_id: 1, status: 1}
- User-specific indexes: {tenant_id: 1, user_id: 1}
- Text search indexes: {tenant_id: 1, field: "text"}

**Indexes by Collection:**

**Appointments:**
- {tenant_id: 1, _id: 1}
- {tenant_id: 1, created_at: -1}
- {tenant_id: 1, status: 1}
- {tenant_id: 1, customer_id: 1}
- {tenant_id: 1, staff_id: 1}
- {tenant_id: 1, start_time: 1, end_time: 1}

**Customers:**
- {tenant_id: 1, _id: 1}
- {tenant_id: 1, created_at: -1}
- {tenant_id: 1, email: 1}
- {tenant_id: 1, phone: 1}
- {tenant_id: 1, name: "text"}

**Staff:**
- {tenant_id: 1, _id: 1}
- {tenant_id: 1, created_at: -1}
- {tenant_id: 1, status: 1}
- {tenant_id: 1, specialty: 1}

**Services:**
- {tenant_id: 1, _id: 1}
- {tenant_id: 1, category: 1}
- {tenant_id: 1, is_active: 1}

**Invoices:**
- {tenant_id: 1, _id: 1}
- {tenant_id: 1, created_at: -1}
- {tenant_id: 1, status: 1}
- {tenant_id: 1, customer_id: 1}

**Acceptance Criteria:**
1. WHEN querying with tenant_id filter, THE query SHALL use index
2. WHEN checking index usage, THE explain() output SHALL show index usage
3. WHEN querying with multiple filters, THE compound index SHALL be used
4. WHEN adding new collection, THE indexes SHALL be automatically created

**Implementation Details:**
1. Create app/models/indexes.py with index definitions
2. Create migration script to create indexes
3. Add index creation to Mongoengine models
4. Verify index creation with MongoDB Compass
5. Test query performance with and without indexes
6. Document index strategy

**Dependencies:**
- mongoengine 0.27.0+
- MongoDB Atlas

**Testing Requirements:**
- Verify indexes are created in MongoDB
- Verify queries use indexes (explain() output)
- Verify query performance is acceptable
- Verify no duplicate indexes

**Deliverables:**
- app/models/indexes.py with index definitions
- Migration script for index creation
- Updated Mongoengine models with indexes
- Index documentation

---

#### 2.4 Write property test for query filtering

**Status:** ✅ COMPLETED

**Description:**
Write property-based tests to verify that query filtering works correctly and that tenant deletion properly removes all associated data. These tests ensure data consistency and proper cleanup.

**Technical Specifications:**

**Property 2: Tenant Deletion Completeness**
- **Validates: Requirements 1.4**
- **Test Framework:** Hypothesis with pytest
- **Hypothesis Strategy:** Generate random tenants with data; delete tenant; verify all data is removed

**Test Cases:**
1. When tenant is deleted, all associated documents are removed
2. Deletion is complete and no orphaned data remains
3. Deletion is idempotent (can be run multiple times safely)
4. Deletion respects soft delete (deleted_at timestamp)
5. Deletion cascades to all related collections

**Acceptance Criteria:**
1. WHEN running property tests, THE tests SHALL pass with >100 examples
2. WHEN tenant is deleted, ALL associated data SHALL be removed
3. WHEN querying deleted tenant, THE results SHALL be empty
4. WHEN running deletion multiple times, THE operation SHALL be idempotent

**Implementation Details:**
1. Create tests/unit/test_tenant_deletion.py
2. Use Hypothesis to generate random tenants with data
3. Test tenant deletion
4. Test cascade deletion to related collections
5. Test soft delete functionality
6. Test idempotency of deletion

**Dependencies:**
- pytest 7.4.3+
- hypothesis 6.92.1+
- mongoengine 0.27.0+

**Testing Requirements:**
- Run `pytest tests/unit/test_tenant_deletion.py -v`
- All tests should pass
- Coverage should be >90%

**Deliverables:**
- tests/unit/test_tenant_deletion.py with property-based tests

---

#### 2.5 Implement tenant provisioning workflow

**Status:** ✅ COMPLETED

**Description:**
Implement the complete tenant provisioning workflow that enables rapid onboarding of new businesses. This includes creating tenant records, provisioning database collections, generating API keys, and sending onboarding emails.

**Technical Specifications:**

**Tenant Provisioning Workflow:**
1. Receive tenant signup request with business information
2. Validate business information (name, email, phone)
3. Create Tenant document in MongoDB
4. Create TenantSettings document with default settings
5. Generate API keys for tenant
6. Create initial admin user for tenant
7. Send onboarding email with login credentials
8. Return tenant_id and credentials to client

**Tenant Provisioning Endpoint:**
```
POST /api/v1/tenants
{
  "name": "Salon ABC",
  "email": "owner@salon.com",
  "phone": "+234 123 456 7890",
  "subscription_tier": "tier"
}

Response:
{
  "tenant_id": "...",
  "admin_user_id": "...",
  "api_key": "...",
  "message": "Tenant provisioned successfully"
}
```

**API Key Generation:**
- Generate random 32-character API key
- Store hashed API key in database
- Return unhashed key only once to client
- Support API key rotation

**Default Settings:**
- Subscription tier: starter
- Status: active
- Region: us-east-1
- Features enabled: basic features only
- Timezone: UTC
- Language: English

**Acceptance Criteria:**
1. WHEN provisioning new tenant, THE Tenant document SHALL be created
2. WHEN provisioning new tenant, THE admin user SHALL be created
3. WHEN provisioning new tenant, THE API key SHALL be generated
4. WHEN provisioning new tenant, THE onboarding email SHALL be sent
5. WHEN provisioning new tenant, THE process SHALL complete within 5 minutes

**Implementation Details:**
1. Create app/routes/tenants.py with tenant endpoints
2. Create app/services/tenant_service.py with provisioning logic
3. Create app/schemas/tenant.py with request/response schemas
4. Implement tenant creation endpoint
5. Implement API key generation
6. Implement admin user creation
7. Implement onboarding email sending
8. Add error handling and validation
9. Test provisioning workflow end-to-end

**Dependencies:**
- fastapi 0.104.1+
- mongoengine 0.27.0+
- pydantic 2.5.0+

**Testing Requirements:**
- Test tenant creation with valid data
- Test tenant creation with invalid data
- Test API key generation
- Test admin user creation
- Test onboarding email sending
- Test error handling

**Deliverables:**
- app/routes/tenants.py with tenant endpoints
- app/services/tenant_service.py with provisioning logic
- app/schemas/tenant.py with request/response schemas
- Unit tests for tenant provisioning

---

#### 2.6 Write unit tests for tenant provisioning

**Status:** ✅ COMPLETED

**Description:**
Write comprehensive unit tests for the tenant provisioning workflow to ensure it works correctly and handles edge cases properly.

**Technical Specifications:**

**Test Cases:**
1. Successful tenant provisioning with valid data
2. Duplicate tenant prevention (same email)
3. API key generation and validation
4. Admin user creation with correct permissions
5. Onboarding email sending
6. Error handling for invalid data
7. Error handling for database failures
8. Concurrent provisioning requests

**Acceptance Criteria:**
1. WHEN running tests, THE test suite SHALL pass with >90% coverage
2. WHEN provisioning with duplicate email, THE system SHALL reject with error
3. WHEN provisioning fails, THE system SHALL rollback changes
4. WHEN provisioning succeeds, ALL components SHALL be created

**Implementation Details:**
1. Create tests/unit/test_tenant_provisioning.py
2. Write tests for successful provisioning
3. Write tests for error cases
4. Write tests for edge cases
5. Mock external services (email)
6. Test database transactions

**Dependencies:**
- pytest 7.4.3+
- pytest-mock 3.12+
- mongoengine 0.27.0+

**Testing Requirements:**
- Run `pytest tests/unit/test_tenant_provisioning.py -v`
- All tests should pass
- Coverage should be >90%

**Deliverables:**
- tests/unit/test_tenant_provisioning.py with unit tests

### 3. User Authentication and Authorization

**Status: ✅ 100% COMPLETE**

#### 3.1 Implement user authentication system

**Status:** ✅ COMPLETED

**Description:**
Implement the core user authentication system with email/password login, JWT token generation, and token refresh mechanism. This task creates the User model with secure password hashing, login endpoint, and token management.

**Technical Specifications:**

**User Document Model:**
```python
class User(BaseDocument):
    email: EmailField(required=True, unique=True)
    password_hash: StringField(required=True)
    first_name: StringField(required=True, max_length=100)
    last_name: StringField(required=True, max_length=100)
    phone: StringField(max_length=20)
    role_id: ObjectIdField(required=True)
    status: StringField(choices=['active', 'inactive', 'suspended'], default='active')
    mfa_enabled: BooleanField(default=False)
    mfa_method: StringField(choices=['totp', 'sms'], null=True)
    created_at: DateTimeField(default=datetime.utcnow)
    updated_at: DateTimeField(default=datetime.utcnow)
    last_login: DateTimeField(null=True)
    
    meta = {
        'collection': 'users',
        'indexes': [
            ('tenant_id', 'email'),
            ('tenant_id', 'status'),
            ('tenant_id', 'created_at')
        ]
    }
```

**Password Security:**
- Hash passwords with bcrypt (salt rounds ≥12)
- Never store plain text passwords
- Minimum 12 characters with complexity requirements
- Password reset via email link (valid for 1 hour)

**JWT Token Structure:**
```json
{
  "sub": "user_id",
  "tenant_id": "tenant_id",
  "email": "user@example.com",
  "role": "manager",
  "permissions": ["appointments:read", "appointments:write"],
  "iat": 1234567890,
  "exp": 1234571490
}
```

**Token Management:**
- Access token: 24-hour expiration
- Refresh token: 30-day expiration
- Token signing: RS256 algorithm
- Token validation: Verify signature and expiration

**Login Endpoint:**
```
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Acceptance Criteria:**
1. WHEN user logs in with valid credentials, THE system SHALL return access and refresh tokens
2. WHEN user logs in with invalid credentials, THE system SHALL return 401 Unauthorized
3. WHEN access token expires, THE user SHALL use refresh token to get new access token
4. WHEN refresh token expires, THE user SHALL log in again
5. WHEN password is changed, ALL existing tokens SHALL be invalidated

**Implementation Details:**
1. Create app/models/user.py with User model
2. Create app/services/auth_service.py with authentication logic
3. Create app/routes/auth.py with authentication endpoints
4. Create app/schemas/auth.py with request/response schemas
5. Implement password hashing with bcrypt
6. Implement JWT token generation and validation
7. Implement token refresh mechanism
8. Add error handling and validation
9. Test authentication flow end-to-end

**Dependencies:**
- fastapi 0.104.1+
- mongoengine 0.27.0+
- pydantic 2.5.0+
- python-jose 3.3.0+
- passlib 1.7.4+
- bcrypt 4.1.1+

**Testing Requirements:**
- Test login with valid credentials
- Test login with invalid credentials
- Test token generation and validation
- Test token refresh
- Test password hashing
- Test error handling

**Deliverables:**
- app/models/user.py with User model
- app/services/auth_service.py with authentication logic
- app/routes/auth.py with authentication endpoints
- app/schemas/auth.py with request/response schemas
- Unit tests for authentication

---

#### 3.2 Write property test for authentication

**Status:** ✅ COMPLETED

**Description:**
Write property-based tests to verify that authentication works correctly across various scenarios including token generation, validation, and expiration.

**Technical Specifications:**

**Property 7: Authentication Token Validity**
- **Validates: Requirements 2.1**
- **Test Framework:** Hypothesis with pytest
- **Hypothesis Strategy:** Generate random users and credentials; verify token generation and validation

**Test Cases:**
1. Valid credentials generate valid tokens
2. Invalid credentials are rejected
3. Tokens are properly signed and can be verified
4. Tokens contain correct claims (user_id, tenant_id, permissions)
5. Expired tokens are rejected
6. Token refresh generates new valid token
7. Concurrent authentication requests work correctly

**Acceptance Criteria:**
1. WHEN running property tests, THE tests SHALL pass with >100 examples
2. WHEN token is valid, THE verification SHALL succeed
3. WHEN token is expired, THE verification SHALL fail
4. WHEN token is tampered with, THE verification SHALL fail

**Implementation Details:**
1. Create tests/unit/test_authentication.py
2. Use Hypothesis to generate random users and credentials
3. Test token generation
4. Test token validation
5. Test token expiration
6. Test token refresh

**Dependencies:**
- pytest 7.4.3+
- hypothesis 6.92.1+
- python-jose 3.3.0+

**Testing Requirements:**
- Run `pytest tests/unit/test_authentication.py -v`
- All tests should pass
- Coverage should be >90%

**Deliverables:**
- tests/unit/test_authentication.py with property-based tests

---

#### 3.3 Implement Role-Based Access Control (RBAC)

**Status:** ✅ COMPLETED

**Description:**
Implement a comprehensive Role-Based Access Control (RBAC) system with predefined roles (Owner, Manager, Staff, Customer) and customizable permissions. This task creates the Role and Permission models, permission checking decorator, and permission caching.

**Technical Specifications:**

**Role Document Model:**
```python
class Role(BaseDocument):
    name: StringField(required=True, max_length=100)
    description: StringField(max_length=500)
    is_custom: BooleanField(default=False)
    permissions: ListField(ObjectIdField(), default=[])
    created_at: DateTimeField(default=datetime.utcnow)
    updated_at: DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'roles',
        'indexes': [
            ('tenant_id', 'name'),
            ('tenant_id', 'is_custom')
        ]
    }
```

**Permission Document Model:**
```python
class Permission(BaseDocument):
    resource: StringField(required=True, max_length=100)
    action: StringField(choices=['view', 'create', 'edit', 'delete', 'export'], required=True)
    description: StringField(max_length=500)
    created_at: DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'permissions',
        'indexes': [
            ('tenant_id', 'resource', 'action')
        ]
    }
```

**Predefined Roles:**
- Owner: Full platform access (all permissions)
- Manager: Staff and operational management
- Staff: Limited to assigned services and schedule
- Customer: Self-service appointment booking and profile

**Permission Checking:**
- Create @require_permission(resource, action) decorator
- Decorator checks user has required permission
- Permissions cached in Redis with 5-minute TTL
- Cache invalidated on permission changes

**Acceptance Criteria:**
1. WHEN user with Owner role accesses settings, THE system SHALL grant full access
2. WHEN user with Manager role accesses staff management, THE system SHALL allow viewing and editing
3. WHEN user with Staff role attempts to access billing, THE system SHALL deny access
4. WHEN user's role changes, THE permissions SHALL be immediately updated
5. WHEN permission is checked, THE check SHALL complete within 10ms (cached)

**Implementation Details:**
1. Create app/models/role.py with Role model
2. Create app/models/permission.py with Permission model
3. Create app/services/rbac_service.py with RBAC logic
4. Create app/decorators/require_permission.py with permission decorator
5. Implement permission caching in Redis
6. Create default roles and permissions
7. Add permission checking to endpoints
8. Test RBAC end-to-end

**Dependencies:**
- fastapi 0.104.1+
- mongoengine 0.27.0+
- redis 5.0.1+

**Testing Requirements:**
- Test role creation and assignment
- Test permission checking
- Test permission caching
- Test permission invalidation
- Test RBAC enforcement

**Deliverables:**
- app/models/role.py with Role model
- app/models/permission.py with Permission model
- app/services/rbac_service.py with RBAC logic
- app/decorators/require_permission.py with permission decorator
- Unit tests for RBAC

---

#### 3.4 Write property test for RBAC

**Status:** ✅ COMPLETED

**Description:**
Write property-based tests to verify that RBAC works correctly and prevents unauthorized access across various scenarios.

**Technical Specifications:**

**Property 4: Role-Based Access Control**
- **Validates: Requirements 2.2, 2.3, 2.4, 2.5**
- **Test Framework:** Hypothesis with pytest
- **Hypothesis Strategy:** Generate random roles, permissions, and users; verify access control

**Test Cases:**
1. Users with correct permissions can access resources
2. Users without permissions are denied access
3. Permission inheritance works correctly
4. Permission caching is consistent
5. Permission changes are immediately reflected
6. Concurrent permission checks work correctly

**Acceptance Criteria:**
1. WHEN running property tests, THE tests SHALL pass with >100 examples
2. WHEN user lacks permission, THE access SHALL be denied
3. WHEN user has permission, THE access SHALL be granted
4. WHEN permission changes, THE new permission SHALL be enforced

**Implementation Details:**
1. Create tests/unit/test_rbac.py
2. Use Hypothesis to generate random roles and permissions
3. Test permission checking
4. Test permission inheritance
5. Test permission caching
6. Test concurrent access

**Dependencies:**
- pytest 7.4.3+
- hypothesis 6.92.1+
- mongoengine 0.27.0+

**Testing Requirements:**
- Run `pytest tests/unit/test_rbac.py -v`
- All tests should pass
- Coverage should be >90%

**Deliverables:**
- tests/unit/test_rbac.py with property-based tests

---

#### 3.5 Implement Multi-Factor Authentication (MFA)

**Status:** ✅ COMPLETED

**Description:**
Implement Multi-Factor Authentication (MFA) support with TOTP (Time-based One-Time Password) and SMS-based OTP. This task adds MFA fields to the User model and creates MFA setup and verification endpoints.

**Technical Specifications:**

**MFA Methods:**
- TOTP: Time-based One-Time Password via authenticator apps (Google Authenticator, Authy)
- SMS: One-Time Password sent via SMS (Twilio integration)

**MFA Setup Endpoint:**
```
POST /api/v1/auth/mfa/setup
{
  "method": "totp"
}

Response:
{
  "secret": "JBSWY3DPEBLW64TMMQ======",
  "qr_code": "data:image/png;base64,..."
}
```

**MFA Verification Endpoint:**
```
POST /api/v1/auth/mfa/verify
{
  "code": "123456"
}

Response:
{
  "verified": true,
  "backup_codes": ["code1", "code2", ...]
}
```

**MFA Login Flow:**
1. User submits email and password
2. System validates credentials
3. If MFA enabled, system returns temporary token requiring MFA
4. User submits MFA code
5. System validates code and returns full JWT token

**Acceptance Criteria:**
1. WHEN setting up MFA, THE system SHALL generate secret and QR code
2. WHEN verifying MFA code, THE system SHALL validate code is correct
3. WHEN MFA is enabled, THE login flow SHALL require MFA code
4. WHEN MFA code is invalid, THE login SHALL fail
5. WHEN backup codes are used, THE system SHALL track usage

**Implementation Details:**
1. Create app/services/mfa_service.py with MFA logic
2. Create app/routes/mfa.py with MFA endpoints
3. Create app/schemas/mfa.py with request/response schemas
4. Implement TOTP generation and verification
5. Implement SMS OTP sending (Twilio)
6. Add MFA fields to User model
7. Update login flow to support MFA
8. Test MFA setup and verification

**Dependencies:**
- fastapi 0.104.1+
- pyotp 2.9.0+ (TOTP)
- twilio 8.10.0+ (SMS)
- qrcode 7.4.2+ (QR code generation)

**Testing Requirements:**
- Test TOTP generation and verification
- Test SMS OTP sending
- Test MFA setup
- Test MFA login flow
- Test backup codes

**Deliverables:**
- app/services/mfa_service.py with MFA logic
- app/routes/mfa.py with MFA endpoints
- app/schemas/mfa.py with request/response schemas
- Unit tests for MFA

---

#### 3.6 Write unit tests for MFA

**Status:** ✅ COMPLETED

**Description:**
Write comprehensive unit tests for MFA functionality to ensure it works correctly and handles edge cases.

**Technical Specifications:**

**Test Cases:**
1. TOTP secret generation
2. TOTP code verification
3. TOTP code expiration
4. SMS OTP sending
5. SMS OTP verification
6. Backup code generation and usage
7. MFA setup and verification
8. MFA login flow

**Acceptance Criteria:**
1. WHEN running tests, THE test suite SHALL pass with >90% coverage
2. WHEN TOTP code is valid, THE verification SHALL succeed
3. WHEN TOTP code is expired, THE verification SHALL fail
4. WHEN SMS OTP is sent, THE code SHALL be deliverable

**Implementation Details:**
1. Create tests/unit/test_mfa.py
2. Write tests for TOTP generation and verification
3. Write tests for SMS OTP
4. Write tests for backup codes
5. Mock Twilio for SMS testing
6. Test MFA login flow

**Dependencies:**
- pytest 7.4.3+
- pytest-mock 3.12+
- pyotp 2.9.0+

**Testing Requirements:**
- Run `pytest tests/unit/test_mfa.py -v`
- All tests should pass
- Coverage should be >90%

**Deliverables:**
- tests/unit/test_mfa.py with unit tests

---

#### 3.7 Implement session management

**Status:** ✅ COMPLETED

**Description:**
Implement session management to track active user sessions, enable session invalidation on logout, and enforce concurrent session limits. Sessions are stored in Redis for fast access and automatic expiration.

**Technical Specifications:**

**Session Model:**
```python
class Session(BaseDocument):
    user_id: ObjectIdField(required=True)
    token: StringField(required=True)
    refresh_token: StringField(required=True)
    created_at: DateTimeField(default=datetime.utcnow)
    expires_at: DateTimeField(required=True)
    ip_address: StringField(required=True)
    user_agent: StringField(required=True)
    status: StringField(choices=['active', 'revoked'], default='active')
    
    meta = {
        'collection': 'sessions',
        'indexes': [
            ('tenant_id', 'user_id'),
            ('tenant_id', 'status'),
            ('expires_at',)
        ]
    }
```

**Session Management:**
- Store sessions in Redis with 24-hour TTL
- Track active sessions per user
- Limit concurrent sessions to 5 per user
- Invalidate sessions on logout
- Invalidate all sessions on password change
- Track IP address and user agent for security

**Logout Endpoint:**
```
POST /api/v1/auth/logout
Authorization: Bearer {token}

Response:
{
  "message": "Logged out successfully"
}
```

**Acceptance Criteria:**
1. WHEN user logs in, THE session SHALL be created and stored
2. WHEN user logs out, THE session SHALL be invalidated
3. WHEN user has >5 concurrent sessions, THE oldest session SHALL be invalidated
4. WHEN session expires, THE session SHALL be automatically removed
5. WHEN password changes, ALL sessions SHALL be invalidated

**Implementation Details:**
1. Create app/models/session.py with Session model
2. Create app/services/session_service.py with session logic
3. Create logout endpoint in app/routes/auth.py
4. Implement session creation on login
5. Implement session invalidation on logout
6. Implement concurrent session limits
7. Implement session expiration
8. Test session management end-to-end

**Dependencies:**
- fastapi 0.104.1+
- mongoengine 0.27.0+
- redis 5.0.1+

**Testing Requirements:**
- Test session creation
- Test session invalidation
- Test concurrent session limits
- Test session expiration
- Test logout

**Deliverables:**
- app/models/session.py with Session model
- app/services/session_service.py with session logic
- Updated app/routes/auth.py with logout endpoint
- Unit tests for session management

---

#### 3.8 Write property test for session management

**Status:** ✅ COMPLETED

**Description:**
Write property-based tests to verify that session management works correctly including session creation, invalidation, and expiration.

**Technical Specifications:**

**Property 6: Session Invalidation on Logout**
- **Validates: Requirements 2.7**
- **Test Framework:** Hypothesis with pytest
- **Hypothesis Strategy:** Generate random sessions and operations; verify session state

**Test Cases:**
1. Sessions are created correctly on login
2. Sessions are invalidated on logout
3. Expired sessions are removed
4. Concurrent session limits are enforced
5. Session state is consistent across operations

**Acceptance Criteria:**
1. WHEN running property tests, THE tests SHALL pass with >100 examples
2. WHEN session is invalidated, THE session SHALL not be accessible
3. WHEN session expires, THE session SHALL be removed
4. WHEN concurrent sessions exceed limit, THE oldest SHALL be removed

**Implementation Details:**
1. Create tests/unit/test_session_management.py
2. Use Hypothesis to generate random sessions
3. Test session creation and invalidation
4. Test session expiration
5. Test concurrent session limits

**Dependencies:**
- pytest 7.4.3+
- hypothesis 6.92.1+
- redis 5.0.1+

**Testing Requirements:**
- Run `pytest tests/unit/test_session_management.py -v`
- All tests should pass
- Coverage should be >90%

**Deliverables:**
- tests/unit/test_session_management.py with property-based tests

### 4. Checkpoint - Core Infrastructure

**Status: ✅ 100% COMPLETE**

#### 4.1 Ensure all tests pass and core infrastructure is stable

**Status:** ✅ COMPLETED

**Description:**
This checkpoint validates that all core infrastructure components are working correctly before proceeding to feature development. This includes running the full test suite, verifying database isolation, testing authentication flow, and ensuring no cross-tenant data leakage.

**Technical Specifications:**

**Validation Checklist:**
1. All unit tests pass (>90% coverage)
2. All property-based tests pass (>100 examples each)
3. Database isolation verified with manual queries
4. Authentication flow works end-to-end
5. No cross-tenant data leakage detected
6. All services start correctly with docker-compose
7. API documentation is accessible
8. Performance targets are met

**Test Execution:**
```bash
# Run all tests
pytest tests/ -v --cov=app --cov-report=html

# Run specific test suites
pytest tests/unit/ -v
pytest tests/integration/ -v

# Run property-based tests
pytest tests/unit/test_*.py -v

# Check coverage
pytest tests/ --cov=app --cov-report=term-missing
```

**Manual Verification:**
1. Start docker-compose: `docker-compose up -d`
2. Verify FastAPI server: `curl http://localhost:8000/health`
3. Verify Swagger docs: `curl http://localhost:8000/docs`
4. Verify Redis connection: `redis-cli ping`
5. Verify RabbitMQ: `curl http://localhost:15672` (guest/guest)
6. Verify MongoDB connection: Test query in app
7. Test authentication flow manually
8. Test tenant isolation with multiple tenants

**Performance Verification:**
- API response time: <500ms (p95)
- Database query time: <100ms (p95)
- Cache hit rate: >80%
- Concurrent requests: 1000+ without errors

**Acceptance Criteria:**
1. WHEN running full test suite, ALL tests SHALL pass
2. WHEN checking coverage, THE coverage SHALL be >90%
3. WHEN verifying isolation, NO cross-tenant data leakage SHALL be detected
4. WHEN testing authentication, THE flow SHALL work end-to-end
5. WHEN checking performance, ALL targets SHALL be met
6. WHEN starting services, ALL services SHALL start without errors

**Implementation Details:**
1. Run full test suite: `pytest tests/ -v --cov=app`
2. Review test coverage report
3. Fix any failing tests
4. Verify database isolation with manual queries
5. Test authentication flow end-to-end
6. Test tenant provisioning
7. Verify performance with load testing
8. Document any issues or limitations
9. Ask user for approval to proceed

**Dependencies:**
- All Phase 1 tasks completed
- pytest 7.4.3+
- All services running in docker-compose

**Testing Requirements:**
- All unit tests pass
- All property-based tests pass
- Coverage >90%
- No cross-tenant data leakage
- Authentication flow works
- Performance targets met

**Deliverables:**
- Test coverage report (HTML)
- Manual verification checklist (completed)
- Performance test results
- Any bug fixes or improvements
- Documentation of any issues

## Phase 2 - Appointment Booking System (Weeks 5-8)

### 5. Service and Availability Management

- [x] 5.1 Implement Service model and management
  - Create Service model (name, duration, price, category)
  - Create service endpoints (list, get, create, update, delete)
  - Implement service filtering by category
  - _Requirements: 3.1, 51.1_

- [ ]* 5.2 Write unit tests for service management
  - Test service creation with valid data
  - Test service validation
  - Test service filtering

- [x] 5.3 Implement Staff availability scheduling
  - Create Availability model (recurring patterns, date ranges)
  - Implement availability endpoints
  - Support recurring weekly schedules and custom date ranges
  - _Requirements: 4.2_

- [ ]* 5.4 Write property test for availability
  - **Property 9: Availability Calculation Accuracy**
  - **Validates: Requirements 3.1, 3.4**

### 6. Appointment Booking Core

- [x] 6.1 Implement appointment booking logic
  - Create Appointment model with status tracking
  - Implement appointment creation endpoint
  - Implement double-booking prevention (database constraints)
  - Calculate available slots based on staff availability and service duration
  - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [ ]* 6.2 Write property test for double-booking prevention
  - **Property 8: Double-Booking Prevention**
  - **Validates: Requirements 3.5, 8.2**

- [x] 6.3 Implement time slot reservation system
  - Create TimeSlot model for temporary reservations
  - Implement 10-minute reservation window
  - Implement automatic reservation expiration
  - _Requirements: 3.2_

- [ ]* 6.4 Write property test for slot reservation
  - **Property 10: Slot Reservation Consistency**
  - **Validates: Requirements 3.2**

- [x] 6.5 Implement appointment confirmation and notifications
  - Create appointment confirmation endpoint
  - Queue confirmation notification
  - Update appointment status to confirmed
  - _Requirements: 3.3, 7.1_

- [ ]* 6.6 Write property test for appointment confirmation
  - **Property 11: Appointment Confirmation Notification**
  - **Validates: Requirements 3.3, 7.1**

- [x] 6.7 Implement appointment cancellation
  - Create cancellation endpoint with reason tracking
  - Release time slot on cancellation
  - Queue cancellation notifications
  - _Requirements: 3.7_

- [ ]* 6.8 Write property test for cancellation
  - **Property 12: Appointment Cancellation Slot Release**
  - **Validates: Requirements 3.7**

### 7. Calendar Views and Availability Display

- [x] 7.1 Implement calendar availability endpoint
  - Create endpoint to get available slots for date range
  - Filter by staff, service, location
  - Return slots in customer's timezone
  - _Requirements: 3.1, 3.4_

- [ ]* 7.2 Write unit tests for calendar availability
  - Test availability calculation with various schedules
  - Test timezone conversion
  - Test filtering by staff/service

- [x] 7.3 Implement appointment listing endpoints
  - Create endpoints for day/week/month views
  - Implement pagination and filtering
  - Support filtering by status, staff, customer
  - _Requirements: 3.6_

- [ ]* 7.4 Write unit tests for appointment listing
  - Test pagination
  - Test filtering
  - Test sorting

### 8. Checkpoint - Appointment Booking

- [ ] 8.1 Ensure appointment booking system is fully functional
  - Run full test suite
  - Test booking flow end-to-end
  - Verify double-booking prevention
  - Verify availability calculations
  - Ask the user if questions arise.

## Phase 3 - Staff and Customer Management (Weeks 9-12)

### 9. Staff Management

- [ ] 9.1 Implement Staff model and profiles
  - Create Staff model (specialties, certifications, hourly_rate)
  - Create staff endpoints (list, get, create, update)
  - Implement staff filtering by specialty
  - _Requirements: 4.1, 26.1_

- [ ]* 9.2 Write property test for staff profiles
  - **Property 13: Staff Profile Data Completeness**
  - **Validates: Requirements 4.1**

- [x] 9.3 Implement shift management
  - Create Shift model with status tracking
  - Implement shift creation with conflict detection
  - Calculate labor costs based on hourly rate
  - _Requirements: 4.3, 4.6_

- [ ]* 9.4 Write property test for shift management
  - **Property 14: Shift Conflict Detection**
  - **Validates: Requirements 4.3**

- [ ]* 9.5 Write property test for labor cost calculation
  - **Property 15: Labor Cost Calculation Accuracy**
  - **Validates: Requirements 4.6**

- [x] 9.6 Implement time-off request workflow
  - Create TimeOffRequest model
  - Implement request creation endpoint
  - Implement approval/denial endpoints
  - Queue notifications for manager
  - _Requirements: 10.2, 10.3_

- [ ]* 9.7 Write unit tests for time-off requests
  - Test request creation
  - Test approval workflow
  - Test availability blocking

### 10. Customer Management

- [x] 10.1 Implement Customer model and profiles
  - Create Customer model with contact info and preferences
  - Create customer endpoints (list, get, create, update)
  - Implement customer search by name/phone
  - _Requirements: 5.1, 5.3_

- [ ]* 10.2 Write property test for customer profiles
  - **Property 17: Customer History Completeness**
  - **Validates: Requirements 5.2**

- [x] 10.3 Implement customer history tracking
  - Create AppointmentHistory model
  - Track all customer appointments with services and staff
  - Implement history retrieval endpoint
  - _Requirements: 5.2_

- [ ]* 10.4 Write unit tests for customer history
  - Test history creation on appointment completion
  - Test history retrieval
  - Test history filtering

- [x] 10.5 Implement customer preferences
  - Create CustomerPreference model
  - Implement preference update endpoint
  - Store preferred staff, services, communication methods
  - _Requirements: 5.3_

- [ ]* 10.6 Write property test for preferences
  - **Property 18: Preference Storage and Retrieval**
  - **Validates: Requirements 5.3**

### 11. Checkpoint - Staff and Customer Management

- [x] 11.1 Ensure staff and customer management is fully functional
  - Run full test suite
  - Test staff scheduling end-to-end
  - Test customer profile management
  - Verify data isolation for staff and customer data
  - Ask the user if questions arise.

## Phase 4 - Billing and Payments (Weeks 13-16)

### 12. Invoice Generation

- [x] 12.1 Implement Invoice model and generation
  - Create Invoice model with line items
  - Implement invoice creation on appointment completion
  - Calculate total = amount - discount + tax
  - _Requirements: 6.1, 20.1_

- [ ]* 12.2 Write property test for invoice accuracy
  - **Property 21: Invoice Generation Accuracy**
  - **Validates: Requirements 6.1, 20.1**

- [x] 12.3 Implement invoice endpoints
  - Create endpoints for listing and retrieving invoices
  - Implement invoice status tracking
  - Support invoice filtering by status and date
  - _Requirements: 6.1_

- [ ]* 12.4 Write unit tests for invoice endpoints
  - Test invoice creation
  - Test invoice retrieval
  - Test invoice filtering

### 13. Paystack Integration Setup

- [x] 13.1 Configure Paystack API client
  - Create Paystack service with API key from .env
  - Implement Paystack API wrapper for transactions
  - Add error handling and logging
  - _Requirements: 6.2, 45.1_

- [x] 13.2 Implement Payment model
  - Create Payment model with fields: amount, status, reference, customer_id, invoice_id, gateway, metadata
  - Add payment status enum: pending, success, failed, cancelled
  - Add indexes for reference and customer_id
  - _Requirements: 6.2_

- [x] 13.3 Implement payment initialization endpoint
  - Create POST /payments/initialize endpoint
  - Accept amount, customer_id, invoice_id
  - Call Paystack to initialize transaction
  - Return authorization_url for frontend redirect
  - Store payment record with pending status
  - _Requirements: 6.2, 45.1_

- [ ]* 13.4 Write unit tests for payment initialization
  - Test successful initialization
  - Test validation of required fields
  - Test Paystack API error handling

### 14. Paystack Webhook Integration

- [x] 14.1 Implement webhook endpoint for Paystack
  - Create POST /webhooks/paystack endpoint
  - Verify webhook signature using Paystack secret key
  - Handle charge.success event
  - Handle charge.failed event
  - Log all webhook events for audit trail
  - _Requirements: 6.2_

- [x] 14.2 Implement webhook signature verification
  - Extract signature from X-Paystack-Signature header
  - Compute HMAC-SHA512 hash of request body
  - Compare with provided signature
  - Reject if signature doesn't match
  - _Requirements: 6.2_

- [x] 14.3 Implement payment status update from webhook
  - Update Payment record status based on webhook event
  - On charge.success: update status to success, mark invoice as paid
  - On charge.failed: update status to failed, log reason
  - Queue notification task for customer
  - _Requirements: 6.2_

- [ ]* 14.4 Write unit tests for webhook handling
  - Test valid webhook signature verification
  - Test invalid signature rejection
  - Test payment status updates
  - Test event logging

### 15. Payment Processing & Verification

- [x] 15.1 Implement payment verification endpoint
  - Create GET /payments/{reference}/verify endpoint
  - Call Paystack to verify transaction status
  - Update local payment record if status changed
  - Return current payment status
  - _Requirements: 6.2_

- [x] 15.2 Implement payment retry logic
  - Create retry mechanism for failed payments
  - Allow customer to retry payment up to 3 times
  - Implement exponential backoff between retries
  - Queue notification on final failure
  - _Requirements: 6.3_

- [x]* 15.3 Write property test for payment retry
  - **Property 22: Payment Retry Logic**
  - **Validates: Requirements 6.3**

- [x] 15.4 Implement idempotency for payment processing
  - Add idempotency_key to Payment model
  - Check for duplicate payments before processing
  - Return existing payment if duplicate detected
  - _Requirements: 6.2_

- [x]* 15.5 Write property test for payment idempotence
  - **Property 23: Payment Processing Idempotence**
  - **Validates: Requirements 6.2**

### 16. Refund Processing

- [x] 16.1 Implement Refund model
  - Create Refund model with fields: amount, reason, status, payment_id, reference
  - Add refund status enum: pending, success, failed
  - Validate refund amount <= original payment amount
  - _Requirements: 6.4_

- [x] 16.2 Implement refund endpoint
  - Create POST /payments/{payment_id}/refund endpoint
  - Validate payment is in success status
  - Call Paystack to process refund
  - Create Refund record with pending status
  - _Requirements: 6.4_

- [x] 16.3 Implement refund webhook handling
  - Handle refund.success event from Paystack
  - Update Refund record status to success
  - Update Payment record to reflect refund
  - Queue notification for customer
  - _Requirements: 6.4_

- [x]* 16.4 Write property test for refund validation
  - **Property 24: Refund Amount Validation**
  - **Validates: Requirements 6.4**

### 17. Financial Reporting

- [x] 17.1 Implement financial report generation
  - Create report endpoints for revenue, payments, refunds
  - Calculate total revenue, outstanding payments, success rates
  - Support date range filtering
  - Implement caching for performance
  - _Requirements: 6.5, 19.1_

- [x]* 17.2 Write property test for financial accuracy
  - **Property 25: Financial Report Accuracy**
  - **Validates: Requirements 6.5, 19.1**

- [x] 17.3 Implement outstanding balance enforcement
  - Check customer balance before allowing new bookings
  - Prevent booking if balance > 0
  - Return balance information in booking response
  - _Requirements: 6.6_

- [x]* 17.4 Write property test for balance enforcement
  - **Property 26: Outstanding Balance Enforcement**
  - **Validates: Requirements 6.6**

### 18. Frontend Payment Integration

- [x] 18.1 Create payment initialization hook
  - Implement useInitializePayment hook
  - Call backend to initialize payment
  - Redirect to Paystack payment page
  - Handle errors gracefully
  - _Requirements: 6.2_

- [x] 18.2 Implement payment verification page
  - Create payment verification component
  - Poll backend for payment status after redirect
  - Show success/failure message
  - Redirect to invoice on success
  - _Requirements: 6.2_

- [x] 18.3 Implement payment history UI
  - Display payment history in customer dashboard
  - Show payment status, amount, date
  - Allow payment retry for failed payments
  - Show refund status if applicable
  - _Requirements: 6.2_

- [x]* 18.4 Write unit tests for payment UI
  - Test payment initialization flow
  - Test payment verification
  - Test error handling

### 19. Checkpoint - Billing System

- [x] 19.1 Ensure billing system is fully functional
  - Run full test suite
  - Test invoice generation end-to-end
  - Test payment processing with Paystack
  - Test webhook handling and payment updates
  - Test refund processing
  - Test financial reporting accuracy
  - Ask the user if questions arise.

## Phase 5 - Notifications and Integrations (Weeks 17-20)

### 16. Notification System

- [x] 16.1 Implement notification infrastructure
  - Create Notification model with status tracking
  - Implement notification queue processing
  - Create notification worker for async delivery
  - _Requirements: 7.1, 7.2, 7.3_

- [ ]* 16.2 Write property test for notification delivery
  - **Property 28: Appointment Reminder Timing**
  - **Validates: Requirements 7.2, 13.1**

- [x] 16.3 Implement email notifications
  - Integrate with SendGrid for email delivery
  - Create email templates for different notification types
  - Implement template rendering with variables
  - _Requirements: 7.1, 49.1_

- [ ]* 16.4 Write unit tests for email notifications
  - Test email template rendering
  - Test email delivery queuing
  - Test delivery tracking

- [x] 16.5 Implement SMS notifications
  - Integrate with Termii for SMS delivery
  - Create SMS templates
  - Implement SMS delivery tracking
  - _Requirements: 7.1, 46.1_

- [ ]* 16.6 Write unit tests for SMS notifications
  - Test SMS template rendering
  - Test SMS delivery queuing
  - Test delivery tracking

- [x] 16.7 Implement notification preferences
  - Create NotificationPreference model
  - Allow customers to opt out of specific notification types
  - Respect preferences in notification delivery
  - _Requirements: 7.1_

- [ ]* 16.8 Write unit tests for notification preferences
  - Test preference storage
  - Test preference enforcement

### 17. Resource Management

- [x] 17.1 Implement Resource model and management
  - Create Resource model (name, type, location, capacity)
  - Create resource endpoints (list, get, create, update)
  - Implement resource availability scheduling
  - _Requirements: 8.1, 8.3_

- [ ]* 17.2 Write property test for resource conflicts
  - **Property 31: Resource Conflict Prevention**
  - **Validates: Requirements 8.2**

- [x] 17.3 Implement resource assignment to appointments
  - Add resource_id to Appointment model
  - Validate resource availability before booking
  - Prevent double-booking of resources
  - _Requirements: 8.2_

- [ ]* 17.4 Write unit tests for resource assignment
  - Test resource availability validation
  - Test resource conflict detection

### 18. Waiting Room Management

- [x] 18.1 Implement Waiting Room queue system
  - Create WaitingRoom model for queue tracking
  - Implement check-in endpoint
  - Implement queue ordering by check-in time
  - _Requirements: 9.1, 9.2_

- [ ]* 18.2 Write property test for queue management
  - **Property 33: Queue Order Consistency**
  - **Validates: Requirements 9.1, 9.2**

- [x] 18.3 Implement queue status endpoint
  - Create endpoint to get current queue
  - Display wait times
  - Show customer position in queue
  - _Requirements: 9.3_

- [ ]* 18.4 Write unit tests for queue status
  - Test queue retrieval
  - Test wait time calculation

### 19. Checkpoint - Notifications and Resources

- [x] 19.1 Ensure notifications and resources are fully functional
  - Run full test suite
  - Test notification delivery end-to-end
  - Test resource management
  - Test waiting room queue
  - Ask the user if questions arise.

## Phase 6 - Advanced Features (Weeks 21-24)

### 20. Inventory Management

- [x] 20.1 Implement Inventory model and tracking
  - Create Inventory model (name, SKU, quantity, reorder_level)
  - Create inventory endpoints (list, get, create, update)
  - Implement stock level alerts
  - _Requirements: 27.1, 28.1_

- [x]* 20.2 Write property test for inventory deduction
  - **Property 41: Inventory Deduction Accuracy**
  - **Validates: Requirements 27.1**

- [x] 20.3 Implement inventory deduction on service
  - Track products used in services
  - Deduct inventory when service is completed
  - Alert when stock falls below reorder level
  - _Requirements: 27.1, 28.1_

- [x]* 20.4 Write property test for stock alerts
  - **Property 42: Stock Alert Triggering**
  - **Validates: Requirements 28.1**

- [x] 20.5 Implement inventory reconciliation
  - Create reconciliation endpoint
  - Compare physical count with system records
  - Identify and log discrepancies
  - _Requirements: 30.1_

- [x]* 20.6 Write property test for reconciliation
  - **Property 43: Inventory Reconciliation Accuracy**
  - **Validates: Requirements 30.1**

### 21. Audit Logging and Compliance

- [x] 21.1 Implement comprehensive audit logging
  - Create AuditLog model for all data access
  - Log all create, read, update, delete operations
  - Include user, timestamp, and action in logs
  - _Requirements: 41.1, 64.1_

- [x]* 21.2 Write property test for audit logging
  - **Property 48: Audit Trail Completeness**
  - **Validates: Requirements 41.1, 64.1**

- [x] 21.3 Implement data access logging
  - Log all customer profile access
  - Log all sensitive data access
  - Implement audit log retrieval endpoint
  - _Requirements: 5.6, 41.1_

- [x]* 21.4 Write unit tests for audit logging
  - Test audit log creation
  - Test audit log retrieval
  - Test audit log filtering

### 22. Backup and Disaster Recovery

- [x] 22.1 Implement backup system
  - Create automated daily backups to S3
  - Implement point-in-time recovery capability
  - Encrypt backups with AES-256
  - _Requirements: 42.1_

- [x]* 22.2 Write property test for backup encryption
  - **Property 49: Backup Encryption**
  - **Validates: Requirements 42.1**

- [x] 22.3 Implement backup verification
  - Verify backup integrity
  - Test restore procedures
  - Document recovery procedures
  - _Requirements: 42.1_

- [x]* 22.4 Write unit tests for backup system
  - Test backup creation
  - Test backup verification
  - Test restore procedures

### 23. Performance Optimization

- [x] 23.1 Implement caching layer
  - Cache frequently accessed data (services, staff, availability)
  - Implement cache invalidation on data changes
  - Monitor cache hit rates
  - _Requirements: 1.1_

- [x]* 23.2 Write unit tests for caching
  - Test cache hit/miss
  - Test cache invalidation
  - Test cache expiration

- [x] 23.3 Implement database query optimization
  - Add indexes for common queries
  - Optimize N+1 queries with eager loading
  - Monitor slow queries
  - _Requirements: 1.1_

- [x]* 23.4 Write unit tests for query performance
  - Test query execution time
  - Test index usage

### 24. Final Checkpoint - MVP Complete

- [x] 24.1 Ensure entire MVP is fully functional and tested
  - Run full test suite (unit + property tests)
  - Verify all 68 features are implemented
  - Test end-to-end workflows
  - Verify data isolation and security
  - Verify performance targets met
  - Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional property-based tests and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples and edge cases
- Checkpoints ensure incremental validation and early error detection
- All code should follow Python best practices and PEP 8 style guide
- All endpoints should include proper error handling and validation
- All database operations should use SQLAlchemy ORM with proper transaction management

### 0.13 Implement Salon Registration Frontend (Registration & Verification Pages)

**Status:** ⏳ NOT STARTED

**Description:**
Build the frontend registration and verification pages for salon owners. This includes the registration form with validation, verification code input page, and success page. The pages will use React components, form validation, and API integration to guide users through the three-phase registration process.

**Technical Specifications:**

**Registration Page (pages/auth/Register.tsx):**
- Form fields: salon_name, owner_name, email, phone, password, address, bank_account (optional), referral_code (optional)
- Real-time validation feedback for each field
- Password strength indicator
- Submit button with loading state
- Error messages displayed inline
- Link to login page for existing users
- Responsive design for mobile and desktop

**Verification Page (pages/auth/Verify.tsx):**
- 6-digit code input field (auto-focus, auto-advance between digits)
- Resend code button (disabled for 60 seconds after sending)
- Countdown timer showing code expiration
- Error messages for invalid/expired codes
- Loading state during verification
- Success message before redirect

**Success Page (pages/auth/RegisterSuccess.tsx):**
- Congratulations message
- Display salon name and subdomain
- Show trial period end date
- Quick start guide (create staff, add services, etc.)
- Button to go to dashboard
- Auto-redirect to dashboard after 5 seconds

**Form Validation:**
- Email: RFC 5322 format, required
- Phone: E.164 format, required
- Salon name: 3-255 characters, required
- Owner name: 2-100 characters, required
- Password: Min 12 chars, uppercase, lowercase, number, special char
- Address: 5-500 characters, required
- Bank account: Optional, 10-50 characters if provided
- Referral code: Optional, alphanumeric

**API Integration:**
- POST /auth/register - Submit registration
- POST /auth/verify-code - Verify code and create account
- POST /auth/resend-code - Request new verification code

**Acceptance Criteria:**
1. WHEN user enters valid registration data, THE form SHALL submit without errors
2. WHEN user enters invalid email, THE form SHALL show error "Invalid email format"
3. WHEN user enters duplicate email, THE API SHALL return error "Email already registered"
4. WHEN verification code is sent, THE user SHALL receive email with 6-digit code
5. WHEN user enters correct code, THE account SHALL be created and user logged in
6. WHEN user enters incorrect code 5 times, THE form SHALL lock for 15 minutes
7. WHEN verification code expires, THE user SHALL be able to request new code
8. WHEN registration succeeds, THE user SHALL be redirected to dashboard

**Deliverables:**
- src/pages/auth/Register.tsx
- src/pages/auth/Verify.tsx
- src/pages/auth/RegisterSuccess.tsx
- src/components/RegistrationForm.tsx
- src/components/VerificationCodeInput.tsx
- Unit tests for form validation
- Integration tests for registration flow

---

### 0.14 Implement Salon Registration Backend (API Endpoints & Services)

**Status:** ⏳ NOT STARTED

**Description:**
Build the backend registration API endpoints and services. This includes the three-phase registration process: validation, temporary storage with verification code, and account creation. The implementation will use FastAPI, MongoDB, and email services to handle the complete registration flow.

**Technical Specifications:**

**API Endpoints:**

**POST /auth/register**
- Request body: salon_name, owner_name, email, phone, password, address, bank_account (optional), referral_code (optional)
- Response: 200 OK with message "Verification code sent to email"
- Response: 409 Conflict if email/phone/salon_name already exists
- Response: 400 Bad Request if validation fails
- Rate limiting: 5 requests per minute per IP

**POST /auth/verify-code**
- Request body: email, verification_code
- Response: 200 OK with JWT token and user data
- Response: 400 Bad Request if code invalid/expired
- Response: 429 Too Many Requests if too many failed attempts
- Rate limiting: 10 requests per minute per email

**POST /auth/resend-code**
- Request body: email
- Response: 200 OK with message "New code sent to email"
- Response: 404 Not Found if email not in temp_registrations
- Response: 429 Too Many Requests if too many resend attempts
- Rate limiting: 3 requests per minute per email

**Services:**

**RegistrationService:**
- validate_registration_data(data) - Validate all inputs
- generate_subdomain(salon_name) - Generate unique subdomain
- generate_verification_code() - Generate 6-digit code
- create_temp_registration(data) - Store temporary registration
- verify_code(email, code) - Verify code and create account
- send_verification_email(email, code) - Send email with code
- track_referral(referral_code, new_tenant_id) - Track referral

**Database Models:**

**TempRegistration:**
```python
class TempRegistration(Document):
    email = StringField(required=True, unique=True)
    phone = StringField(required=True)
    salon_name = StringField(required=True)
    owner_name = StringField(required=True)
    address = StringField(required=True)
    bank_account = StringField()
    password_hash = StringField(required=True)
    subdomain = StringField(required=True)
    verification_code = StringField(required=True)
    verification_code_expires = DateTimeField(required=True)
    referral_code = StringField()
    referral_tenant_id = ObjectIdField()
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)  # TTL index
    attempt_count = IntField(default=0)
    locked_until = DateTimeField()
    
    meta = {
        'indexes': [
            ('expires_at', 1),  # TTL index
            ('email', 1),
            ('phone', 1),
            ('subdomain', 1)
        ]
    }
```

**Tenant:**
```python
class Tenant(Document):
    name = StringField(required=True)
    subdomain = StringField(required=True, unique=True)
    owner_name = StringField(required=True)
    phone = StringField(required=True)
    email = StringField(required=True)
    address = StringField(required=True)
    subscription_plan = StringField(default='trial')
    subscription_tier = StringField(default='enterprise')
    is_active = BooleanField(default=True)
    is_published = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    settings = DictField(default={})
```

**Acceptance Criteria:**
1. WHEN POST /auth/register is called with valid data, THE System SHALL validate and create temp registration
2. WHEN email already exists, THE System SHALL return 409 Conflict
3. WHEN verification code is sent, THE System SHALL send email within 1 second
4. WHEN POST /auth/verify-code is called with correct code, THE System SHALL create tenant, user, subscription
5. WHEN code is incorrect, THE System SHALL increment attempt_count
6. WHEN attempt_count >= 5, THE System SHALL lock account for 15 minutes
7. WHEN code expires, THE System SHALL allow requesting new code
8. WHEN account is created, THE System SHALL auto-publish salon to marketplace
9. WHEN referral_code is provided, THE System SHALL track referral

**Deliverables:**
- app/routes/auth.py (API endpoints)
- app/services/registration_service.py (Registration logic)
- app/models/temp_registration.py (Temporary registration model)
- app/schemas/registration.py (Pydantic schemas)
- app/tasks/emails.py (Email sending tasks)
- Unit tests for registration service
- Integration tests for API endpoints
- Property-based tests for validation logic

---

### 0.15 Implement Subdomain Routing & Tenant Context

**Status:** ⏳ NOT STARTED

**Description:**
Implement subdomain-based routing to automatically extract tenant context from request hostname and inject it into all subsequent queries. This ensures multi-tenant isolation and enables customers to access salons via unique subdomains.

**Technical Specifications:**

**Middleware (middleware/subdomain_context.py):**
- Extract subdomain from request hostname
- Query MongoDB for matching tenant
- Set tenant_id in request context
- Validate tenant is active
- Handle wildcard domain routing

**Subdomain Extraction Logic:**
- Request: `https://acme-salon.kenikool.com/api/appointments`
- Hostname: `acme-salon.kenikool.com`
- Subdomain: `acme-salon`
- Query: `db.tenants.find_one({subdomain: 'acme-salon'})`
- Set: `request.state.tenant_id = tenant._id`

**Tenant Context Injection:**
- All database queries automatically filtered by tenant_id
- All API responses include tenant context
- All audit logs include tenant_id
- All errors include tenant context for debugging

**DNS Configuration:**
- Wildcard DNS: `*.kenikool.com` → API Gateway IP
- All subdomains route to same application
- Reverse proxy (nginx/Caddy) handles SSL certificates

**Acceptance Criteria:**
1. WHEN request is made to subdomain URL, THE System SHALL extract subdomain correctly
2. WHEN subdomain matches tenant, THE System SHALL set tenant_id in context
3. WHEN subdomain doesn't match, THE System SHALL return 404 Not Found
4. WHEN tenant is inactive, THE System SHALL return 403 Forbidden
5. WHEN all queries include tenant_id filter, THE System SHALL prevent cross-tenant data access

**Deliverables:**
- app/middleware/subdomain_context.py
- app/utils/subdomain.py (Subdomain extraction utilities)
- Unit tests for subdomain extraction
- Integration tests for tenant context injection
- Nginx/Caddy configuration for wildcard routing

---



## Phase 5 - Salon Registration & Subdomain Routing

### 5. Implement Salon Owner Registration with Email Verification

#### 5.1 Create registration data models and schemas

- [ ] 5.1 Create registration data models and schemas
  - Create TempRegistration model in app/models/temp_registration.py with TTL index (24 hours)
  - Create SubdomainRouting model in app/models/subdomain_routing.py
  - Extend Tenant model with subdomain, is_published, is_active fields
  - Extend Service model with is_published, public_description, public_image_url, allow_public_booking fields
  - Extend Staff model with is_available_for_public_booking, public_bio, public_photo_url fields
  - Create Pydantic schemas for registration requests/responses in app/schemas/registration.py
  - Add database indexes for email, phone, subdomain uniqueness
  - _Requirements: 2.1, 2.2, 2.4_

#### 5.2 Implement registration service logic

- [ ] 5.2 Implement registration service logic
  - Create RegistrationService in app/services/registration_service.py
  - Implement validate_registration_data(data) - Validate without DB write
  - Implement generate_subdomain(salon_name) - Generate unique subdomain with auto-counter
  - Implement generate_verification_code() - Generate 6-digit code
  - Implement create_temp_registration(data) - Store temporary registration
  - Implement verify_email_code(email, code) - Verify and create permanent records
  - Implement resend_verification_code(email) - Generate and send new code
  - _Requirements: 2.1, 2.2, 2.3, 2.9_

- [ ]* 5.2.1 Write property test for registration validation
  - **Property 1: Registration Data Validation**
  - **Validates: Requirements 2.1, 2.14, 2.15**

- [ ]* 5.2.2 Write property test for subdomain uniqueness
  - **Property 2: Subdomain Uniqueness**
  - **Validates: Requirements 2.2**

- [ ]* 5.2.3 Write property test for verification code expiry
  - **Property 3: Verification Code Expiry**
  - **Validates: Requirements 2.9**

- [ ]* 5.2.4 Write property test for temporary registration cleanup
  - **Property 12: Temporary Registration Cleanup**
  - **Validates: Requirements 2.10**

#### 5.3 Create registration API routes

- [ ] 5.3 Create registration API routes
  - Create app/routes/registration.py with endpoints:
    - POST /auth/register - Submit registration form
    - POST /auth/verify-email - Verify email with code
    - POST /auth/resend-code - Resend verification code
    - GET /auth/check-availability - Check email/phone/salon name availability
  - Implement request validation and error handling
  - Add rate limiting for registration attempts (5 per minute per IP)
  - _Requirements: 2.1, 2.2, 2.3, 2.9_

#### 5.4 Create registration frontend pages

- [ ] 5.4 Create registration frontend pages
  - Create pages/auth/Register.tsx - Registration form with validation
  - Create pages/auth/Verify.tsx - Email verification code entry
  - Create pages/auth/RegisterSuccess.tsx - Success page with subdomain URL
  - Implement form validation (email, phone, password strength)
  - Implement error handling and user feedback
  - Add loading states and success messages
  - _Requirements: 2.1, 2.2, 2.3_

#### 5.5 Implement subdomain routing middleware

- [ ] 5.5 Implement subdomain routing middleware
  - Create middleware/subdomain_context.py for subdomain extraction
  - Extract subdomain from Host header
  - Query SubdomainRouting table for tenant_id
  - Validate tenant is_published and is_active
  - Inject tenant_id into request context
  - Set is_public flag for public routes
  - _Requirements: 2.16, 2.20_

- [ ]* 5.5.1 Write property test for subdomain routing
  - **Property 11: Subdomain Routing Accuracy**
  - **Validates: Requirements 2.16**

#### 5.6 Write unit tests for registration

- [ ] 5.6 Write unit tests for registration
  - Test registration validation (email, phone, salon name uniqueness)
  - Test subdomain generation and uniqueness
  - Test verification code generation and expiry
  - Test temporary registration cleanup
  - Test subdomain extraction from Host header
  - Test email/phone/salon name availability checks
  - _Requirements: 2.1-2.15_

#### 5.7 Write integration tests for registration

- [ ] 5.7 Write integration tests for registration
  - Test complete registration flow from form submission to dashboard access
  - Test subdomain routing to public booking interface
  - Test verification code resend functionality
  - Test registration expiry and cleanup
  - Test email sending with real email service
  - _Requirements: 2.1-2.15_

#### 5.8 Checkpoint - Ensure all registration tests pass

- [ ] 5.8 Checkpoint - Ensure all registration tests pass
  - Run all unit tests: `npm run test` (frontend) and `pytest` (backend)
  - Run all property-based tests
  - Run all integration tests
  - Verify code coverage >90%
  - Ensure all tests pass, ask the user if questions arise.

---



## Phase 6 - Public Booking Feature

### 6. Implement Public Booking via Subdomain

#### 6.1 Create public booking data models and schemas

- [x] 6.1 Create public booking data models and schemas
  - Create PublicBooking model in app/models/public_booking.py
  - Extend Service model with is_published, public_description, public_image_url, allow_public_booking fields (already done in 5.1)
  - Extend Staff model with is_available_for_public_booking, public_bio, public_photo_url fields (already done in 5.1)
  - Create Pydantic schemas for public booking requests/responses in app/schemas/public_booking.py
  - Add database indexes for tenant_id and created_at on PublicBooking collection
  - _Requirements: 2.17, 2.18, 2.19_

#### 6.2 Implement availability calculation engine

- [x] 6.2 Implement availability calculation engine
  - Create AvailabilityCalculator class in app/utils/availability.py
  - Implement get_available_slots(tenant_id, staff_id, service_id, date) method
  - Calculate slots based on staff schedule, existing appointments, service duration, buffer time
  - Handle timezone conversions for salon and customer
  - Implement caching with Redis (5-minute TTL)
  - _Requirements: 2.4_

- [-]* 6.2.1 Write property test for availability calculation
  - **Property 6: Availability Calculation Accuracy**
  - **Validates: Requirements 2.4**

#### 6.3 Create public booking API routes

- [x] 6.3 Create public booking API routes
  - Create app/routes/public_booking.py with endpoints:
    - GET /public/services - List published services for tenant
    - GET /public/staff - List available staff for service
    - GET /public/availability - Get available time slots
    - POST /public/bookings - Create booking
    - GET /public/bookings/{id} - Get booking details
  - Implement request validation and error handling
  - Add rate limiting middleware (10 bookings per minute per IP)
  - _Requirements: 2.17, 2.18, 2.19, 2.4_

- [ ]* 6.3.1 Write property test for tenant isolation
  - **Property 4: Tenant Isolation in Public Booking**
  - **Validates: Requirements 2.20**

- [ ]* 6.3.2 Write property test for rate limiting
  - **Property 8: Rate Limiting Enforcement**
  - **Validates: Requirements 2.21**

#### 6.4 Implement public booking service logic

- [x] 6.4 Implement public booking service logic
  - Create PublicBookingService in app/services/public_booking_service.py
  - Implement create_public_booking(tenant_id, booking_data) method
  - Implement double-booking prevention with database locking
  - Implement guest customer creation if email doesn't exist
  - Implement appointment creation from public booking
  - _Requirements: 2.18, 2.19, 2.5, 2.20_

- [ ]* 6.4.1 Write property test for no double-booking
  - **Property 5: No Double-Booking**
  - **Validates: Requirements 2.5**

- [ ]* 6.4.2 Write property test for guest booking account creation
  - **Property 9: Guest Booking Account Creation**
  - **Validates: Requirements 2.18**

#### 6.5 Implement booking confirmation email

- [x] 6.5 Implement booking confirmation email
  - Create email template for booking confirmation in app/templates/booking_confirmation.html
  - Implement send_booking_confirmation(booking) in PublicBookingService
  - Include appointment details, salon contact info, cancellation/rescheduling instructions
  - Send email asynchronously via Celery task
  - _Requirements: 2.19_

- [ ]* 6.5.1 Write property test for email delivery
  - **Property 7: Booking Confirmation Email Delivery**
  - **Validates: Requirements 2.19**

#### 6.6 Create public booking frontend - service selection

- [x] 6.6 Create public booking frontend - service selection
  - Create pages/public/PublicBookingApp.tsx as main entry point
  - Create components/public/ServiceSelector.tsx component
  - Display published services with descriptions, pricing, duration
  - Implement service filtering and search
  - Add service images and icons
  - _Requirements: 2.17, 2.2_

#### 6.7 Create public booking frontend - staff and time selection

- [x] 6.7 Create public booking frontend - staff and time selection
  - Create components/public/StaffSelector.tsx component
  - Create components/public/TimeSlotSelector.tsx component
  - Display available staff with photos and bios
  - Display calendar with available dates
  - Show available time slots for selected date
  - Implement real-time availability updates
  - _Requirements: 2.3, 2.4_

#### 6.8 Create public booking frontend - booking form and confirmation

- [x] 6.8 Create public booking frontend - booking form and confirmation
  - Create components/public/BookingForm.tsx component
  - Create components/public/BookingConfirmation.tsx component
  - Collect customer details (name, email, phone)
  - Implement form validation
  - Display booking confirmation with appointment details
  - Offer account creation option
  - _Requirements: 2.18, 2.19, 2.5_

#### 6.9 Implement public booking styling and branding

- [x] 6.9 Implement public booking styling and branding
  - Apply salon branding (logo, colors, fonts) to public interface
  - Implement responsive design for mobile and desktop
  - Add accessibility features (WCAG 2.1 AA compliance)
  - Implement dark mode support
  - _Requirements: 2.17_

#### 6.10 Implement public booking middleware and routing

- [-] 6.10 Implement public booking middleware and routing
  - Create middleware/public_booking.py for public booking validation
  - Validate tenant is active and allows public bookings
  - Set is_public flag in request context
  - Apply rate limiting
  - Log all public booking requests
  - _Requirements: 2.17, 2.21_

#### 6.11 Write unit tests for public booking

- [ ] 6.11 Write unit tests for public booking
  - Test availability calculation with various schedules
  - Test tenant isolation in queries
  - Test rate limiting logic
  - Test email validation and phone validation
  - Test booking creation with valid and invalid data
  - Test double-booking prevention
  - _Requirements: 2.1-2.23_

#### 6.12 Write integration tests for public booking

- [ ] 6.12 Write integration tests for public booking
  - Test complete booking flow from service selection to confirmation
  - Test subdomain routing to public booking interface
  - Test email sending with real email service
  - Test database transactions for booking creation
  - Test concurrent booking attempts for same time slot
  - _Requirements: 2.1-2.23_

#### 6.13 Checkpoint - Ensure all public booking tests pass

- [ ] 6.13 Checkpoint - Ensure all public booking tests pass
  - Run all unit tests: `npm run test` (frontend) and `pytest` (backend)
  - Run all property-based tests
  - Run all integration tests
  - Verify code coverage >90%
  - Ensure all tests pass, ask the user if questions arise.



---

## Phase 7 - Point of Sale (POS) System

### 1. Backend: POS Data Models and Schemas

#### 1.1 Create POS data models

- [x] 1.1 Create POS data models
  - Create app/models/transaction.py with Transaction and TransactionItem models
  - Create app/models/cart.py with Cart and CartItem models
  - Create app/models/receipt.py with Receipt and ReceiptItem models
  - Create app/models/refund.py with Refund model
  - Create app/models/discount.py with Discount model
  - Create app/models/staff_commission.py with StaffCommission and CommissionStructure models
  - Add database indexes for tenant_id, created_at, payment_status, customer_id, staff_id
  - Add TTL indexes for temporary records (carts, pending transactions)
  - _Requirements: 70.1, 71.1, 72.1, 73.1, 74.1, 75.1, 76.1, 77.1, 78.1, 79.1_

#### 1.2 Create POS Pydantic schemas

- [x] 1.2 Create POS Pydantic schemas
  - Create app/schemas/transaction.py with TransactionCreate, TransactionUpdate, TransactionResponse schemas
  - Create app/schemas/cart.py with CartCreate, CartUpdate, CartResponse schemas
  - Create app/schemas/receipt.py with ReceiptCreate, ReceiptResponse schemas
  - Create app/schemas/refund.py with RefundCreate, RefundResponse schemas
  - Create app/schemas/discount.py with DiscountCreate, DiscountResponse schemas
  - Create app/schemas/payment.py with PaymentInitiate, PaymentVerify schemas
  - Add validation for all schemas (amount > 0, valid payment methods, etc.)
  - _Requirements: 70.1, 71.1, 72.1, 73.1, 74.1, 75.1, 76.1, 77.1, 78.1, 79.1_

---

### 2. Backend: POS Services

#### 2.1 Implement transaction service

- [x] 2.1 Implement transaction service
  - Create app/services/transaction_service.py with TransactionService class
  - Implement create_transaction(tenant_id, transaction_data) method
  - Implement calculate_totals(items, discounts, tax_rate) method
  - Implement get_transaction(tenant_id, transaction_id) method
  - Implement list_transactions(tenant_id, filters) method
  - Implement update_transaction_status(transaction_id, status) method
  - Implement validate_transaction_data(data) method
  - _Requirements: 70.1, 70.2, 70.3_

- [ ]* 2.1.1 Write property test for transaction immutability
  - **Property 1: Transaction Immutability**
  - **Validates: Requirements 70.4**

- [ ]* 2.1.2 Write property test for transaction total calculation
  - **Property 7: Tax Calculation Accuracy**
  - **Validates: Requirements 77.5**

#### 2.2 Implement payment service with Paystack integration

- [x] 2.2 Implement payment service with Paystack integration
  - Create app/services/paystack_service.py with PaystackService class
  - Implement initialize_payment(amount, email, reference) method
  - Implement verify_payment(reference) method
  - Implement process_refund(reference, amount) method
  - Implement handle_webhook(payload, signature) method
  - Add error handling for payment failures
  - Add retry logic for failed payments
  - _Requirements: 71.1, 71.2, 71.3_

- [ ]* 2.2.1 Write property test for payment status consistency
  - **Property 3: Payment Status Consistency**
  - **Validates: Requirements 71.3**

#### 2.3 Implement inventory deduction service

- [x] 2.3 Implement inventory deduction service
  - Create app/services/inventory_deduction_service.py with InventoryDeductionService class
  - Implement deduct_inventory(tenant_id, transaction_id, items) method
  - Implement restore_inventory(tenant_id, transaction_id) method
  - Implement check_inventory_availability(tenant_id, product_id, quantity) method
  - Implement generate_low_stock_alert(tenant_id, product_id) method
  - Add transaction support for atomic inventory updates
  - _Requirements: 72.1, 72.2, 72.3_

- [ ]* 2.3.1 Write property test for inventory deduction accuracy
  - **Property 2: Inventory Deduction Accuracy**
  - **Validates: Requirements 72.1**

- [ ]* 2.3.2 Write property test for refund inventory restoration
  - **Property 5: Refund Inventory Restoration**
  - **Validates: Requirements 78.3**

#### 2.4 Implement receipt generation service

- [x] 2.4 Implement receipt generation service
  - Create app/services/receipt_service.py with ReceiptService class
  - Implement generate_receipt(transaction_id) method
  - Implement render_receipt_template(receipt_data) method
  - Implement generate_receipt_pdf(receipt) method
  - Implement print_receipt(receipt_id, printer_name) method
  - Implement email_receipt(receipt_id, email) method
  - Implement generate_qr_code(transaction_id) method
  - _Requirements: 74.1, 74.2, 74.3_

- [ ]* 2.4.1 Write property test for receipt generation completeness
  - **Property 4: Receipt Generation Completeness**
  - **Validates: Requirements 74.1**

#### 2.5 Implement discount service

- [x] 2.5 Implement discount service
  - Create app/services/discount_service.py with DiscountService class
  - Implement apply_discount(transaction, discount_code) method
  - Implement calculate_discount_amount(discount, subtotal) method
  - Implement validate_discount_code(discount_code) method
  - Implement check_discount_conditions(discount, transaction) method
  - Implement apply_loyalty_discount(customer_id, transaction) method
  - _Requirements: 77.1, 77.2, 77.3_

- [ ]* 2.5.1 Write property test for discount calculation accuracy
  - **Property 6: Discount Calculation Accuracy**
  - **Validates: Requirements 77.1**

#### 2.6 Implement refund service

- [x] 2.6 Implement refund service
  - Create app/services/refund_service.py with RefundService class
  - Implement create_refund(transaction_id, refund_data) method
  - Implement approve_refund(refund_id, approver_id) method
  - Implement process_refund(refund_id) method
  - Implement reverse_refund(refund_id) method
  - Implement validate_refund_eligibility(transaction_id) method
  - _Requirements: 78.1, 78.2, 78.3_

#### 2.7 Implement staff commission service

- [x] 2.7 Implement staff commission service
  - Create app/services/commission_service.py with CommissionService class
  - Implement calculate_commission(transaction_id, staff_id) method
  - Implement get_commission_structure(tenant_id, staff_id) method
  - Implement calculate_payout(tenant_id, staff_id, period) method
  - Implement process_commission_payout(payout_id) method
  - Support percentage, fixed, and tiered commission structures
  - _Requirements: 79.1, 79.2, 79.3_

- [ ]* 2.7.1 Write property test for commission calculation accuracy
  - **Property 8: Commission Calculation Accuracy**
  - **Validates: Requirements 79.2**

#### 2.8 Implement audit logging service

- [x] 2.8 Implement audit logging service
  - Create app/services/pos_audit_service.py with POSAuditService class
  - Implement log_transaction_created(transaction_id, user_id) method
  - Implement log_transaction_modified(transaction_id, old_value, new_value, user_id) method
  - Implement log_payment_processed(transaction_id, payment_method, user_id) method
  - Implement log_refund_processed(refund_id, user_id) method
  - Implement log_discount_applied(transaction_id, discount_id, user_id) method
  - Implement log_inventory_deducted(transaction_id, items, user_id) method
  - _Requirements: 80.1, 80.2, 80.3_

- [ ]* 2.8.1 Write property test for audit trail completeness
  - **Property 10: Audit Trail Completeness**
  - **Validates: Requirements 80.1**

---

### 3. Backend: POS API Routes

#### 3.1 Create transaction API routes

- [x] 3.1 Create transaction API routes
  - Create app/routes/pos_transactions.py with endpoints:
    - POST /api/transactions - Create transaction
    - GET /api/transactions - List transactions with filtering
    - GET /api/transactions/{id} - Get transaction details
    - PUT /api/transactions/{id} - Update transaction
    - POST /api/transactions/{id}/refund - Create refund
  - Implement request validation and error handling
  - Add rate limiting for transaction creation
  - _Requirements: 70.1, 70.2, 70.3_

#### 3.2 Create payment API routes

- [x] 3.2 Create payment API routes
  - Create app/routes/pos_payments.py with endpoints:
    - POST /api/payments/initialize - Initialize payment
    - GET /api/payments/{reference}/verify - Verify payment
    - POST /api/payments/{reference}/refund - Process refund
    - POST /webhooks/paystack - Handle Paystack webhook
  - Implement Paystack webhook signature verification
  - Add error handling for payment failures
  - _Requirements: 71.1, 71.2, 71.3_

#### 3.3 Create receipt API routes

- [x] 3.3 Create receipt API routes
  - Create app/routes/pos_receipts.py with endpoints:
    - GET /api/receipts/{transaction_id} - Get receipt
    - POST /api/receipts/{id}/print - Print receipt
    - POST /api/receipts/{id}/email - Email receipt
    - GET /api/receipts/{id}/pdf - Download receipt PDF
  - Implement receipt generation on-demand
  - Add printer configuration support
  - _Requirements: 74.1, 74.2, 74.3_

#### 3.4 Create discount API routes

- [x] 3.4 Create discount API routes
  - Create app/routes/pos_discounts.py with endpoints:
    - POST /api/discounts - Create discount
    - GET /api/discounts - List discounts
    - POST /api/discounts/validate - Validate discount code
    - POST /api/discounts/{id}/apply - Apply discount to transaction
  - Implement discount validation and application
  - Add rate limiting for discount validation
  - _Requirements: 77.1, 77.2, 77.3_

#### 3.5 Create refund API routes

- [x] 3.5 Create refund API routes
  - Create app/routes/pos_refunds.py with endpoints:
    - POST /api/refunds - Create refund request
    - GET /api/refunds - List refunds
    - GET /api/refunds/{id} - Get refund details
    - PUT /api/refunds/{id}/approve - Approve refund
    - PUT /api/refunds/{id}/process - Process refund
    - PUT /api/refunds/{id}/reverse - Reverse refund
  - Implement refund approval workflow
  - Add authorization checks for refund approval
  - _Requirements: 78.1, 78.2, 78.3_

#### 3.6 Create commission API routes

- [x] 3.6 Create commission API routes
  - Create app/routes/pos_commissions.py with endpoints:
    - GET /api/commissions/staff/{staff_id} - Get staff commission
    - GET /api/commissions/payouts - List commission payouts
    - POST /api/commissions/payouts - Create commission payout
    - PUT /api/commissions/payouts/{id}/process - Process payout
  - Implement commission calculation and tracking
  - Add authorization checks for commission access
  - _Requirements: 79.1, 79.2, 79.3_

#### 3.7 Create POS reporting API routes

- [x] 3.7 Create POS reporting API routes
  - Create app/routes/pos_reports.py with endpoints:
    - GET /api/reports/sales - Get sales report
    - GET /api/reports/revenue - Get revenue report
    - GET /api/reports/inventory - Get inventory report
    - GET /api/reports/payments - Get payment report
    - GET /api/reports/export - Export report as PDF/CSV/Excel
  - Implement report generation and aggregation
  - Add caching for report data
  - _Requirements: 73.1, 73.2, 73.3_

---

### 4. Backend: POS Testing

#### 4.1 Write unit tests for POS services

- [x] 4.1 Write unit tests for POS services
  - Test transaction creation and validation
  - Test inventory deduction logic
  - Test discount calculation
  - Test tax calculation
  - Test commission calculation
  - Test receipt generation
  - Test refund processing
  - Test payment verification
  - _Requirements: 70.1-80.5_

#### 4.2 Write integration tests for POS API

- [x] 4.2 Write integration tests for POS API
  - Test complete transaction flow from creation to receipt
  - Test payment processing with Paystack
  - Test inventory deduction and restoration
  - Test refund processing
  - Test commission calculation and payout
  - Test discount application
  - Test offline mode and sync
  - _Requirements: 70.1-80.5_

#### 4.3 Checkpoint - Ensure all POS backend tests pass

- [x] 4.3 Checkpoint - Ensure all POS backend tests pass
  - Run all unit tests: `pytest backend/tests/unit/`
  - Run all property-based tests: `pytest backend/tests/unit/ -k property`
  - Run all integration tests: `pytest backend/tests/integration/`
  - Verify code coverage >90%
  - Ensure all tests pass, ask the user if questions arise.

---

### 5. Frontend: POS Dashboard and Components

#### 5.1 Create POS dashboard page

- [x] 5.1 Create POS dashboard page
  - Create pages/pos/POSDashboard.tsx as main entry point
  - Display transaction summary (today's sales, transaction count, average transaction)
  - Display quick action buttons (New Transaction, View Receipts, Refunds, Reports)
  - Display recent transactions list
  - Display payment method breakdown
  - Display low-stock alerts
  - _Requirements: 70.1, 73.1_

#### 5.2 Create transaction entry component

- [x] 5.2 Create transaction entry component
  - Create components/pos/TransactionEntry.tsx component
  - Create components/pos/CartItems.tsx component
  - Create components/pos/ItemSelector.tsx component
  - Implement adding items to cart (services, products, packages)
  - Implement quantity adjustment
  - Implement item removal
  - Display running total with tax and discount
  - _Requirements: 70.1, 76.1_

- [ ]* 5.2.1 Write unit tests for transaction entry
  - Test adding items to cart
  - Test quantity adjustment
  - Test total calculation
  - _Requirements: 70.1_

#### 5.3 Create discount application component

- [x] 5.3 Create discount application component
  - Create components/pos/DiscountApplier.tsx component
  - Implement discount code input
  - Implement discount validation
  - Implement discount application
  - Display discount amount and final total
  - _Requirements: 77.1, 77.2_

- [ ]* 5.3.1 Write unit tests for discount application
  - Test discount code validation
  - Test discount calculation
  - _Requirements: 77.1_

#### 5.4 Create payment processing component

- [x] 5.4 Create payment processing component
  - Create components/pos/PaymentProcessor.tsx component
  - Create components/pos/PaymentMethodSelector.tsx component
  - Implement payment method selection (cash, card, mobile money)
  - Implement split payment support
  - Implement tip handling
  - Implement payment status display
  - _Requirements: 71.1, 76.1_

- [ ]* 5.4.1 Write unit tests for payment processing
  - Test payment method selection
  - Test split payment calculation
  - _Requirements: 71.1, 76.1_

#### 5.5 Create receipt display and printing component

- [x] 5.5 Create receipt display and printing component
  - Create components/pos/ReceiptDisplay.tsx component
  - Create components/pos/ReceiptPrinter.tsx component
  - Display receipt with all transaction details
  - Implement print functionality
  - Implement email receipt functionality
  - Implement receipt preview
  - _Requirements: 74.1, 74.2, 74.3_

- [ ]* 5.5.1 Write unit tests for receipt display
  - Test receipt rendering
  - Test receipt data formatting
  - _Requirements: 74.1_

#### 5.6 Create refund processing component

- [x] 5.6 Create refund processing component
  - Create components/pos/RefundProcessor.tsx component
  - Implement transaction selection for refund
  - Implement refund amount input
  - Implement refund reason selection
  - Display refund status
  - _Requirements: 78.1, 78.2_

- [ ]* 5.6.1 Write unit tests for refund processing
  - Test refund creation
  - Test refund validation
  - _Requirements: 78.1_

#### 5.7 Create POS reporting component

- [x] 5.7 Create POS reporting component
  - Create pages/pos/POSReports.tsx page
  - Create components/pos/SalesReport.tsx component
  - Create components/pos/RevenueReport.tsx component
  - Create components/pos/InventoryReport.tsx component
  - Create components/pos/PaymentReport.tsx component
  - Implement report filtering by date range
  - Implement report export (PDF, CSV, Excel)
  - Display charts and graphs
  - _Requirements: 73.1, 73.2, 73.3_

- [ ]* 5.7.1 Write unit tests for POS reporting
  - Test report generation
  - Test report filtering
  - _Requirements: 73.1_

---

### 6. Frontend: POS Hooks and State Management

#### 6.1 Create POS hooks

- [x] 6.1 Create POS hooks
  - Create hooks/useCart.ts hook for cart management
  - Create hooks/useCheckout.ts hook for checkout process
  - Create hooks/useReceipt.ts hook for receipt generation
  - Create hooks/useRefund.ts hook for refund processing
  - Create hooks/useDiscount.ts hook for discount application
  - Create hooks/usePayment.ts hook for payment processing
  - Create hooks/usePOSReports.ts hook for report generation
  - _Requirements: 70.1-80.5_

#### 6.2 Create POS Zustand stores

- [x] 6.2 Create POS Zustand stores
  - Create stores/pos.ts store for POS state
  - Implement cart state (items, totals, discounts)
  - Implement transaction state (current transaction, history)
  - Implement payment state (payment method, status)
  - Implement offline state (sync status, pending transactions)
  - _Requirements: 70.1-80.5_

---

### 7. Frontend: Offline Mode Implementation

#### 7.1 Implement offline storage

- [x] 7.1 Implement offline storage
  - Create lib/offline/indexeddb.ts for IndexedDB management
  - Implement transaction storage
  - Implement cart storage
  - Implement inventory cache
  - Implement sync queue
  - _Requirements: 75.1, 75.2_

#### 7.2 Implement offline sync

- [x] 7.2 Implement offline sync
  - Create lib/offline/sync.ts for sync management
  - Implement sync queue processing
  - Implement conflict resolution
  - Implement retry logic
  - Implement sync status tracking
  - _Requirements: 75.3, 75.4_

- [ ]* 7.2.1 Write property test for offline sync idempotence
  - **Property 9: Offline Sync Idempotence**
  - **Validates: Requirements 75.3**

#### 7.3 Implement offline UI indicators

- [x] 7.3 Implement offline UI indicators
  - Create components/pos/OfflineIndicator.tsx component
  - Display offline status
  - Display sync progress
  - Display pending transaction count
  - _Requirements: 75.1_

---

### 8. Frontend: POS Testing

#### 8.1 Write unit tests for POS components

- [x] 8.1 Write unit tests for POS components
  - Test transaction entry component
  - Test discount application component
  - Test payment processing component
  - Test receipt display component
  - Test refund processing component
  - Test POS reporting component
  - _Requirements: 70.1-80.5_

#### 8.2 Write integration tests for POS flow

- [x] 8.2 Write integration tests for POS flow
  - Test complete transaction flow from entry to receipt
  - Test payment processing
  - Test refund processing
  - Test offline mode and sync
  - Test discount application
  - _Requirements: 70.1-80.5_

#### 8.3 Checkpoint - Ensure all POS frontend tests pass

- [x] 8.3 Checkpoint - Ensure all POS frontend tests pass
  - Run all unit tests: `npm run test` (frontend)
  - Run all integration tests
  - Verify code coverage >90%
  - Ensure all tests pass, ask the user if questions arise.

---

### 9. Integration: POS with Existing Systems

#### 9.1 Link POS transactions to appointments

- [x] 9.1 Link POS transactions to appointments
  - Update appointment model to include transaction_id reference
  - When appointment is completed, create transaction automatically
  - Link transaction to appointment for audit trail
  - _Requirements: 70.1_

#### 9.2 Link POS transactions to invoices

- [x] 9.2 Link POS transactions to invoices
  - Update invoice model to include transaction_id reference
  - When transaction is completed, create invoice automatically
  - Link transaction to invoice for financial tracking
  - _Requirements: 70.1_

#### 9.3 Link POS transactions to inventory

- [x] 9.3 Link POS transactions to inventory
  - When transaction is completed, deduct inventory automatically
  - When refund is processed, restore inventory automatically
  - Track inventory movements for audit trail
  - _Requirements: 72.1, 72.2, 72.3_

#### 9.4 Link POS transactions to customers

- [x] 9.4 Link POS transactions to customers
  - Update customer model to include transaction history
  - Calculate customer lifetime value from transactions
  - Track customer purchase patterns
  - _Requirements: 70.1_

#### 9.5 Link POS transactions to staff

- [x] 9.5 Link POS transactions to staff
  - Track which staff member processed each transaction
  - Calculate staff commission from transactions
  - Track staff performance metrics
  - _Requirements: 79.1, 79.2, 79.3_

#### 9.6 Link POS transactions to audit logs

- [x] 9.6 Link POS transactions to audit logs
  - Log all transaction creation and modifications
  - Log all payment processing
  - Log all refunds
  - Log all discounts applied
  - _Requirements: 80.1, 80.2, 80.3_

---

### 10. Final Integration and Testing

#### 10.1 Write end-to-end tests for POS system

- [x] 10.1 Write end-to-end tests for POS system
  - Test complete POS flow from transaction entry to receipt
  - Test payment processing with Paystack
  - Test inventory deduction and restoration
  - Test refund processing
  - Test commission calculation
  - Test offline mode and sync
  - Test integration with appointments, invoices, customers, staff
  - _Requirements: 70.1-80.5_

#### 10.2 Performance testing

- [ ] 10.2 Performance testing
  - Test transaction creation performance (target: <2 seconds)
  - Test payment processing performance (target: <5 seconds)
  - Test receipt generation performance (target: <2 seconds)
  - Test report generation performance (target: <5 seconds)
  - Test offline sync performance (target: <10 seconds for 100 transactions)
  - _Requirements: 70.1-80.5_

#### 10.3 Security testing

- [ ] 10.3 Security testing
  - Test transaction data isolation (no cross-tenant access)
  - Test payment data security (no sensitive data in logs)
  - Test refund authorization (only authorized users can approve)
  - Test audit trail integrity (audit logs cannot be modified)
  - _Requirements: 80.1, 80.2, 80.3_

#### 10.4 Checkpoint - Ensure all POS tests pass

- [x] 10.4 Checkpoint - Ensure all POS tests pass
  - Run all unit tests: `npm run test` (frontend) and `pytest` (backend)
  - Run all property-based tests
  - Run all integration tests
  - Run all end-to-end tests
  - Verify code coverage >90%
  - Ensure all tests pass, ask the user if questions arise.

---

## Summary

This comprehensive implementation plan specifies 80+ features organized across 7 implementation phases:

- **Phase 1 (MVP)**: 12 core features for basic operations
- **Phase 2 (Operations & Financial)**: 18 features for advanced operations and financial management
- **Phase 3 (Customer Engagement & Marketing)**: 14 features for marketing and customer retention
- **Phase 4 (Integrations & Compliance)**: 13 features for third-party integrations and compliance
- **Phase 5 (Advanced Features)**: 11 features for AI and advanced capabilities
- **Phase 6 (Operational Excellence)**: 11 features for optimization and advanced operations
- **Phase 7 (Point of Sale)**: 11 features for transaction processing and payment management
- **Public Booking**: 1 feature for customer-facing booking interface

Each phase includes detailed implementation tasks with acceptance criteria, technical specifications, and testing requirements to guide development.
