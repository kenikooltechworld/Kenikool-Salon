---
inclusion: always
---

# Project Coding Standards and Rules

## CRITICAL: Always Follow These Rules

### 1. ASK BEFORE ACTING
- **NEVER make changes without user consent**
- **ALWAYS ask questions when requirements are unclear**
- **ALWAYS present findings and get approval before implementing**
- **NEVER use modals (userInput tool) to ask questions** - ask directly in chat
- When user says "investigate", show findings first - don't implement

### 2. USE MODERN 2026 LIBRARIES AND PATTERNS
- We're in 2026 - use current best practices
- React 19.2.0 with modern patterns (no legacy code)
- TypeScript 5.9 with strict typing
- Use specified libraries - don't substitute alternatives

### 3. FOLLOW EXISTING CODE PATTERNS
- Read existing code before writing new code
- Match the project's style and structure
- Don't introduce new patterns without discussion

## Technology Stack (2026)

### Frontend
- **React**: 19.2.0 (latest features, no legacy patterns)
- **TypeScript**: 5.9 (strict mode enabled)
- **Build Tool**: Vite 7.3
- **State Management**: 
  - Zustand 5.0 for global state
  - @tanstack/react-query 5.89.0 for server state
- **Styling**: Tailwind CSS 4.0
- **UI Components**: Custom components in `salon/src/components/ui/`

### Backend
- **Python**: 3.11+
- **Framework**: FastAPI
- **Database**: MongoDB Atlas with Mongoengine ODM
- **Task Queue**: Celery with Redis/RabbitMQ
- **Real-time**: Socket.io
- **Payments**: Paystack (Africa-focused)

### Testing
- **Backend**: pytest with Hypothesis (property-based testing)
- **Frontend**: vitest

## Frontend Patterns

### User Interaction Rules

**CRITICAL**: When asking questions or gathering requirements:
- Ask questions directly in chat responses
- NEVER use modals or popup dialogs to ask questions
- Present options and information inline in your responses
- Let users respond naturally in the conversation

### React Query Usage (MANDATORY)

**CRITICAL**: Use @tanstack/react-query for ALL server state management
- **NEVER use useEffect for data fetching** - use React Query hooks
- **NEVER use useState for server data** - use React Query cache

#### Hook Pattern (Custom Hooks in `salon/src/hooks/`)
```typescript
// ✅ CORRECT: Use React Query hooks
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/utils/api";

export function useBookings(filters?: BookingFilters) {
  return useQuery({
    queryKey: ["bookings", filters],
    queryFn: async () => {
      const { data } = await apiClient.get("/appointments", { params: filters });
      return transformData(data); // Transform snake_case to camelCase
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateBooking() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (input: CreateBookingInput) => {
      const { data } = await apiClient.post("/appointments", input);
      return transformData(data);
    },
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ["bookings"], exact: false });
    },
  });
}
```

#### Query Key Conventions
- Use array format: `["resource", filters]`
- Include filters in query key for proper caching
- Use `exact: false` when invalidating to clear all related queries

**Query Key Naming Convention**:

```typescript
// Define constants for base keys
const BOOKINGS_QUERY_KEY = "bookings";

// Use array format with filters
queryKey: [BOOKINGS_QUERY_KEY, { status, startDate, endDate }]

// Use kebab-case for multi-word keys
queryKey: ["available-slots", staffId, serviceId, date]

// Include all filter parameters in key for proper cache invalidation
queryKey: [BOOKINGS_QUERY_KEY, filters]
```

#### Stale Time Guidelines
- List queries: 5 minutes (`5 * 60 * 1000`)
- Detail queries: 5 minutes
- Real-time data: 1-2 minutes
- Static data: 10+ minutes

### Zustand Store Pattern (Global UI State Only)

**Use Zustand ONLY for**:
- Authentication state (`salon/src/stores/auth.ts`)
- UI state (modals, sidebars, theme)
- Client-side preferences

**DO NOT use Zustand for**:
- Server data (use React Query)
- Form state (use local state)

#### Store Pattern with Persistence

All Zustand stores MUST use `persist` middleware:

```typescript
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  user: User | null;
  permissions: string[];
  setUser: (user: User | null) => void;
  logout: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      permissions: [],
      setUser: (user) => set({ user }),
      logout: async () => {
        await apiClient.post("/auth/logout");
        queryClient.clear(); // Clear React Query cache
        set({ user: null, permissions: [] });
      },
    }),
    {
      name: "auth-store",  // localStorage key
      partialize: (state) => ({
        // Only persist specific fields
        user: state.user,
        permissions: state.permissions,
      }),
    },
  ),
);
```

- Use `persist` middleware for localStorage
- Set `name` to unique store identifier
- Use `partialize` to exclude sensitive data
- Don't persist auth tokens (use httpOnly cookies)

### Component Structure

#### File Organization
```
salon/src/
├── components/
│   ├── ui/              # Reusable UI components (Button, Card, Input)
│   ├── bookings/        # Feature-specific components
│   ├── services/
│   └── ...
├── hooks/               # Custom React Query hooks
├── pages/               # Route components
├── stores/              # Zustand stores (minimal)
├── lib/
│   └── utils/           # Utility functions
└── types/               # TypeScript types
```

#### Component Pattern

All components MUST define explicit Props interface:

```typescript
// ✅ CORRECT: Functional component with TypeScript
interface BookingCardProps {
  booking: Booking;
  onView?: (id: string) => void;
  onConfirm?: (id: string) => void;
  isLoading?: boolean;
}

export function BookingCard({
  booking,
  onView,
  onConfirm,
  isLoading = false,
}: BookingCardProps) {
  return (
    <Card className="p-4">
      {/* Component content */}
    </Card>
  );
}
```

**Component Props Interface Convention**:
1. Define interface with all props
2. Mark optional props with `?`
3. Provide default values in destructuring
4. Use interface name as `ComponentNameProps`

### Data Transformation (snake_case ↔ camelCase)

**Backend uses snake_case, Frontend uses camelCase**

#### Transform in React Query Hooks

All React Query hooks MUST transform snake_case to camelCase:

```typescript
// ✅ CORRECT: Transform in the hook
export function useBookings() {
  return useQuery({
    queryKey: ["bookings"],
    queryFn: async () => {
      const { data } = await apiClient.get("/appointments");
      // Transform snake_case to camelCase
      return (data.appointments || []).map((appt: any) => ({
        id: appt.id,
        customerId: appt.customer_id,
        staffId: appt.staff_id,
        startTime: appt.start_time,
        endTime: appt.end_time,
        // Transform all fields
      }));
    },
  });
}
```

This ensures frontend uses camelCase consistently.

### API Client Usage

#### Import Pattern
```typescript
import { apiClient } from "@/lib/utils/api";
```

#### HTTP Methods
```typescript
// GET
const { data } = await apiClient.get("/appointments");

// POST (with idempotency for retries)
const { data } = await apiClient.post("/appointments", payload, {
  headers: { "Idempotency-Key": crypto.randomUUID() }
});

// PUT
const { data } = await apiClient.put(`/appointments/${id}`, payload);

// DELETE
const { data } = await apiClient.delete(`/appointments/${id}`);
```

#### API Client Retry Logic

The API client automatically retries transient errors with exponential backoff:

- **Retries**: 3 attempts maximum
- **Backoff**: 500ms, 1000ms, 2000ms (exponential)
- **Jitter**: Random 0-200ms added to prevent thundering herd
- **Safe methods**: GET, HEAD, OPTIONS, PUT, DELETE (always retried)
- **POST**: Only retried if `Idempotency-Key` header present

**Transient errors that trigger retry**:
- Network errors (ERR_NETWORK, ECONNABORTED, ETIMEDOUT)
- HTTP 408, 425, 429, 500, 502, 503, 504

**Non-transient errors (not retried)**:
- 400, 401, 403, 404, 422 (client errors)

#### Error Handling
```typescript
import { getErrorMessage } from "@/lib/utils/api";

try {
  await apiClient.post("/appointments", data);
} catch (error) {
  const message = getErrorMessage(error);
  showToast({ variant: "error", title: "Error", description: message });
}
```

## Backend Patterns

### Service Layer Pattern (MANDATORY)

**CRITICAL**: All service methods MUST be static methods (@staticmethod)

Services are utility classes that are never instantiated. All methods are called as `ServiceClass.method_name(tenant_id, ...)`.

```python
class AppointmentService:
    """Service for appointment management."""
    
    @staticmethod
    def create_appointment(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        service_id: ObjectId,
        start_time: datetime,
        end_time: datetime,
        customer_id: Optional[ObjectId] = None,
    ) -> Appointment:
        """
        Create a new appointment.
        
        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            
        Returns:
            Created Appointment document
            
        Raises:
            ValueError: If appointment overlaps or validation fails
        """
        # Business logic
        appointment = Appointment(tenant_id=tenant_id, staff_id=staff_id)
        appointment.save()
        return appointment
```

### Logging with Contextual Prefixes

Use contextual prefixes in log messages to identify the operation context:

```python
logger.info(f"[DoubleBookingCheck] Checking for overlaps")
logger.warning(f"[BalanceCheck] Insufficient balance for customer {customer_id}")
logger.error(f"[TenantContext] Failed to extract tenant from JWT")
```

This helps with debugging and log analysis.

### Middleware Architecture Pattern

All middleware MUST extend `BaseHTTPMiddleware` and implement `dispatch` method:

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Pre-processing
        logger.info(f"[CustomMiddleware] Processing {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Post-processing
        return response
```

Middleware registration order in `main.py` matters - register in correct sequence.

### Tenant Context Extraction Pattern

Tenant context is extracted from JWT tokens in cookies:

```python
# Middleware extracts tenant_id from JWT token in access_token cookie
# Tenant soft-deletion checking happens automatically
# Use get_tenant_id() dependency to access in routes

from app.middleware.tenant_context import get_tenant_id

@router.get("/resource")
async def get_resource(tenant_id: ObjectId = Depends(get_tenant_id)):
    # tenant_id is automatically extracted and validated
    pass
```

### Database Indexing Convention

All models MUST define indexes in `meta` dict:

1. Always include `tenant_id` as first field (multi-tenancy)
2. Include `_id` for identity lookups
3. Include frequently queried fields
4. Use compound indexes for complex queries
5. Add comments explaining compound indexes

```python
meta = {
    "collection": "appointments",
    "indexes": [
        ("tenant_id", "_id"),
        ("tenant_id", "customer_id"),
        ("tenant_id", "staff_id"),
        ("tenant_id", "start_time"),
        # Compound index for double-booking prevention
        ("tenant_id", "staff_id", "start_time", "end_time", "status"),
    ],
}
```

### Idempotency Key Pattern (Backend)

For operations that create resources, check idempotency key first:

```python
if idempotency_key:
    existing = Model.objects(
        tenant_id=tenant_id,
        idempotency_key=idempotency_key
    ).first()
    if existing:
        return existing  # Return existing instead of creating duplicate

# Create new resource
resource = Model(
    tenant_id=tenant_id,
    idempotency_key=idempotency_key,
)
resource.save()
return resource
```

### Non-Critical Operation Error Handling

For operations that shouldn't fail the main operation:

```python
try:
    NonCriticalService.operation(...)
except Exception as e:
    logger.warning(f"Non-critical operation failed: {str(e)}")
    # Continue - operation is not critical to main flow
```

Examples of non-critical operations:
- Creating appointment history
- Sending notifications
- Emitting WebSocket updates
- Creating booking activity for social proof

Always log the failure for debugging.

### Real-Time Updates Pattern

Services emit WebSocket updates for real-time client updates:

```python
try:
    from app.socketio_handler import emit_availability_update
    loop = asyncio.get_event_loop()
    loop.create_task(emit_availability_update(
        tenant_id=str(tenant_id),
        service_id=str(service_id),
        date=date_str,
        event_data={
            "event_type": "slot_taken",
            "time_slot": time_str,
        }
    ))
except Exception as e:
    logger.error(f"Error emitting update: {str(e)}")
```

- Wrap in try-except (non-critical)
- Use `asyncio.create_task()` for async emission
- Include `tenant_id` for multi-tenancy
- Log errors but don't fail main operation

### Guest Booking Pattern

Appointments support two booking types:

1. **Internal Booking**: `customer_id` provided
   - Requires existing customer
   - Checks customer balance
   - Uses customer contact info

2. **Public Booking**: `guest_*` fields provided
   - `guest_name`, `guest_email`, `guest_phone`
   - Auto-creates guest customer if not exists
   - Skips balance check
   - Marks appointment as `is_guest=True`

```python
is_guest = bool(guest_name)

if is_guest and guest_email:
    customer_id = AppointmentService._get_or_create_guest_customer(
        tenant_id, guest_name, guest_email, guest_phone
    )
```

### Soft Delete Pattern

Tenants support soft deletion with grace period:

1. `deletion_status` field: "active", "soft_deleted", "permanently_deleted"
2. `deleted_at` timestamp
3. `grace_period_days` (default 30)
4. Soft-deleted tenants can recover within grace period
5. After grace period, permanent deletion occurs

```python
if tenant.deletion_status == "soft_deleted":
    logger.warning(f"Tenant is soft deleted: {tenant_id}")
    # Skip tenant context for deleted tenants
```

### Celery Task Pattern

All Celery tasks MUST follow this pattern:

```python
from app.tasks import celery_app

@celery_app.task(bind=True, max_retries=3)
def task_name(self, param1: str, param2: dict):
    try:
        # Task implementation
        logger.info(f"[TaskName] Task completed: {param1}")
        return {"status": "success"}
    except Exception as exc:
        logger.error(f"[TaskName] Task failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
```

- Use `bind=True` to access self for retry
- Set `max_retries=3` for resilience
- Always log success and errors
- Use `self.retry()` for exponential backoff

### Pydantic Schema Configuration

All request schemas MUST use `ConfigDict`:

```python
from pydantic import BaseModel, ConfigDict

class AppointmentCreateRequest(BaseModel):
    customer_id: str
    staff_id: str
    
    model_config = ConfigDict(
        populate_by_name=True,      # Accept both snake_case and camelCase
        str_strip_whitespace=True   # Auto-strip whitespace from strings
    )
```

This enables frontend to send camelCase while backend uses snake_case.

### FastAPI Route Structure

#### File Organization
```
backend/app/
├── routes/              # API endpoints
├── services/            # Business logic
├── models/              # Mongoengine models
├── schemas/             # Pydantic schemas
├── middleware/          # Middleware
└── tasks/               # Celery tasks
```

#### Route Pattern
```python
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.middleware.tenant_context import get_tenant_id
from app.schemas.appointment import AppointmentCreateRequest, AppointmentResponse
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("", response_model=AppointmentResponse)
async def create_appointment(
    request: AppointmentCreateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Create a new appointment."""
    try:
        appointment = AppointmentService.create_appointment(
            tenant_id=tenant_id,
            customer_id=ObjectId(request.customer_id),
            # ... other fields
        )
        return AppointmentResponse(
            id=str(appointment.id),
            customer_id=str(appointment.customer_id),
            # ... transform to response
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### Service Layer Pattern

**All business logic goes in service classes**

```python
class AppointmentService:
    """Service for appointment management."""
    
    @staticmethod
    def create_appointment(
        tenant_id: ObjectId,
        staff_id: ObjectId,
        service_id: ObjectId,
        start_time: datetime,
        end_time: datetime,
        customer_id: Optional[ObjectId] = None,
        # ... other params
    ) -> Appointment:
        """
        Create a new appointment.
        
        Args:
            tenant_id: Tenant ID
            staff_id: Staff member ID
            # ... document all parameters
            
        Returns:
            Created Appointment document
            
        Raises:
            ValueError: If appointment overlaps or validation fails
        """
        # Validation
        AppointmentService._check_double_booking(tenant_id, staff_id, start_time, end_time)
        
        # Business logic
        appointment = Appointment(
            tenant_id=tenant_id,
            staff_id=staff_id,
            # ... fields
        )
        appointment.save()
        
        # Side effects (notifications, etc.)
        AppointmentService._send_confirmation(appointment)
        
        return appointment
    
    @staticmethod
    def _check_double_booking(...):
        """Private helper method."""
        # Validation logic
```

### Mongoengine Model Pattern

```python
from datetime import datetime
from mongoengine import StringField, ObjectIdField, DateTimeField, DecimalField
from app.models.base import BaseDocument

class Appointment(BaseDocument):
    """Appointment document representing a booked appointment."""
    
    # Required fields
    customer_id = ObjectIdField(required=True)
    staff_id = ObjectIdField(required=True)
    service_id = ObjectIdField(required=True)
    start_time = DateTimeField(required=True)
    end_time = DateTimeField(required=True)
    
    # Status with choices
    status = StringField(
        required=True,
        choices=["scheduled", "confirmed", "completed", "cancelled", "no_show"],
        default="scheduled"
    )
    
    # Optional fields
    notes = StringField(null=True, max_length=1000)
    price = DecimalField(null=True, min_value=0)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        "collection": "appointments",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "customer_id"),
            ("tenant_id", "staff_id"),
            ("tenant_id", "start_time"),
        ],
    }
    
    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
```

### Pydantic Schema Pattern

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal

class AppointmentCreateRequest(BaseModel):
    """Request schema for creating an appointment."""
    
    customer_id: str = Field(..., alias="customerId")
    staff_id: str = Field(..., alias="staffId")
    service_id: str = Field(..., alias="serviceId")
    start_time: str = Field(..., alias="startTime")
    notes: Optional[str] = Field(None, max_length=1000)
    
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True
    )

class AppointmentResponse(BaseModel):
    """Response schema for an appointment."""
    
    id: str
    customer_id: str
    staff_id: str
    start_time: str
    status: str
    
    class Config:
        from_attributes = True
```

## Testing Patterns

### Property-Based Testing (Backend)

**Use Hypothesis for property-based testing**

All property-based tests MUST follow this pattern:

```python
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime, timedelta
from bson import ObjectId

@pytest.fixture
def test_tenant():
    """Create a test tenant."""
    tenant = Tenant(name="Test Salon", subdomain="test-salon")
    tenant.save()
    yield tenant
    tenant.delete()

class TestAppointmentProperties:
    """Property-based tests for appointments."""
    
    @given(
        initial_status=st.sampled_from(["scheduled", "confirmed"]),
    )
    @settings(
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        max_examples=10,
        deadline=None
    )
    def test_mark_appointment_completed_updates_status(
        self,
        test_tenant,
        initial_status,
    ):
        """
        Property: For any appointment with initial status,
        marking it as completed SHALL update the status persistently.
        """
        # Create appointment
        appointment = Appointment(
            tenant_id=test_tenant.id,
            status=initial_status,
            # ... other fields
        )
        appointment.save()
        
        # Mark as completed
        appointment.status = "completed"
        appointment.save()
        
        # Verify persistence
        retrieved = Appointment.objects(id=appointment.id).first()
        assert retrieved.status == "completed"
        
        # Cleanup
        appointment.delete()
```

**Property-Based Testing Conventions**:
1. Use `@given` decorator with strategy generators
2. Suppress health checks for fixture-based tests
3. Set `max_examples=10` for reasonable test time
4. Set `deadline=None` to avoid timeout issues
5. Document the property being tested in docstring

## Naming Conventions

### Files and Folders
- **Frontend**: camelCase for files (`BookingCard.tsx`, `useBookings.ts`)
- **Backend**: snake_case for files (`appointment_service.py`, `booking_routes.py`)
- **Folders**: kebab-case (`salon/src/components/booking-card/`)

### Variables and Functions
- **Frontend**: camelCase (`customerId`, `handleSubmit`)
- **Backend**: snake_case (`customer_id`, `create_appointment`)

### Components
- **React Components**: PascalCase (`BookingCard`, `ServiceForm`)
- **Hooks**: camelCase with `use` prefix (`useBookings`, `useCreateService`)

### Constants
- **All caps with underscores**: `MAX_RETRIES`, `BASE_DELAY_MS`

## Import Patterns

### Frontend
```typescript
// External libraries first
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

// Internal utilities
import { apiClient } from "@/lib/utils/api";
import { formatDate } from "@/lib/utils/format";

// Components
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

// Types
import type { Booking } from "@/types";

// Hooks (last)
import { useBookings } from "@/hooks/useBookings";
```

### Backend
```python
# Standard library
import logging
from datetime import datetime
from typing import Optional, List

# Third-party
from fastapi import APIRouter, Depends
from bson import ObjectId
from mongoengine import Q

# Local
from app.models.appointment import Appointment
from app.services.appointment_service import AppointmentService
from app.schemas.appointment import AppointmentResponse
```

## Error Handling

### Frontend
```typescript
// ✅ CORRECT: Handle errors in mutations
const { mutate: createBooking } = useCreateBooking();

const handleSubmit = async (data: BookingInput) => {
  createBooking(data, {
    onSuccess: (booking) => {
      showToast({ variant: "success", title: "Booking created" });
      navigate(`/bookings/${booking.id}`);
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      showToast({ variant: "error", title: "Error", description: message });
    },
  });
};
```

### Backend
```python
# ✅ CORRECT: Raise specific exceptions
@router.post("/appointments")
async def create_appointment(request: AppointmentCreateRequest):
    try:
        appointment = AppointmentService.create_appointment(...)
        return AppointmentResponse(...)
    except ValueError as e:
        # Business logic errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Security Rules

### Authentication
- **All routes require authentication** (except public endpoints)
- **Use httpOnly cookies** for tokens (no localStorage)
- **Tenant isolation** enforced at middleware level

### Input Validation
- **Frontend**: Validate in forms before submission
- **Backend**: Validate with Pydantic schemas
- **Never trust client input**

### SQL/NoSQL Injection Prevention
- **Always use ObjectId()** for MongoDB IDs
- **Never concatenate user input** into queries
- **Use parameterized queries**

## Performance Rules

### Frontend
- **Lazy load routes** with React.lazy()
- **Memoize expensive computations** with useMemo
- **Debounce search inputs**
- **Use React Query staleTime** to reduce requests

### Backend
- **Add database indexes** for frequently queried fields
- **Use pagination** for list endpoints
- **Cache expensive operations** with Redis
- **Batch database operations** when possible

## Code Quality Rules

### TypeScript
- **Enable strict mode** in tsconfig.json
- **Define explicit types** for all props and returns
- **Use interfaces** for object shapes
- **Avoid `any`** - use `unknown` if type is truly unknown

### Python
- **Type hints** for all function parameters and returns
- **Docstrings** for all public functions and classes
- **Follow PEP 8** style guide
- **Use f-strings** for string formatting

## Git Commit Messages

```
feat: add booking cancellation feature
fix: resolve double-booking issue
refactor: extract appointment validation logic
docs: update API documentation
test: add property tests for appointments
chore: update dependencies
```

## When in Doubt

1. **Look at existing code** - match the pattern
2. **Ask the user** - don't guess
3. **Read the tech stack** - use specified libraries
4. **Check this file** - follow these standards

## Anti-Patterns to Avoid

### Frontend Anti-Patterns

#### ❌ NEVER: Promise Chains in Components
```typescript
// ❌ WRONG: Using .then() promise chains in components
fetch(`/api/v1/transactions/${id}/generate-receipt`, { method: "POST" })
  .then(() => {
    setSuccess(true);
    showToast({ title: "Success" });
  })
  .catch((err) => {
    console.error("Failed:", err);
  });
```

```typescript
// ✅ CORRECT: Use React Query mutations
const { mutate: generateReceipt } = useMutation({
  mutationFn: async (id: string) => {
    const { data } = await apiClient.post(`/transactions/${id}/generate-receipt`);
    return data;
  },
  onSuccess: () => {
    showToast({ variant: "success", title: "Receipt generated" });
  },
  onError: (error) => {
    const message = getErrorMessage(error);
    showToast({ variant: "error", title: "Error", description: message });
  },
});

// Use it
generateReceipt(transactionId);
```

#### ❌ NEVER: Missing Idempotency Keys
```typescript
// ❌ WRONG: POST without idempotency key
await apiClient.post("/appointments", data);
```

```typescript
// ✅ CORRECT: Always include idempotency key for POST requests
await apiClient.post("/appointments", data, {
  headers: { "Idempotency-Key": crypto.randomUUID() }
});
```

### Backend Anti-Patterns

#### ❌ NEVER: Duplicate Decorators
```python
# ❌ WRONG: Duplicate @staticmethod decorator
@staticmethod
@staticmethod  # Duplicate!
def method():
    pass
```

```python
# ✅ CORRECT: Single decorator
@staticmethod
def method():
    pass
```

#### ❌ NEVER: Missing Error Context in Logs
```python
# ❌ WRONG: Vague error messages
logger.error(f"Error: {e}")
```

```python
# ✅ CORRECT: Include context
logger.error(f"[OperationName] Failed to create appointment: {e}")
```

#### ❌ NEVER: Bare Exception Handlers
```python
# ❌ WRONG: Catching exceptions without logging
try:
    result = some_operation()
except Exception as e:
    pass  # Silent failure
```

```python
# ✅ CORRECT: Always log exceptions
try:
    result = some_operation()
except ValueError as e:
    # Log business logic errors
    logger.warning(f"Validation failed: {str(e)}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    # Log unexpected errors
    logger.error(f"Unexpected error in operation: {str(e)}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

#### ❌ NEVER: Silent Exception Swallowing
```python
# ❌ WRONG: Swallowing exceptions without action
try:
    AppointmentHistoryService.create_history(tenant_id, appt_id)
except ValueError as e:
    pass  # No logging, no action
```

```python
# ✅ CORRECT: Log and handle appropriately
try:
    AppointmentHistoryService.create_history(tenant_id, appt_id)
except ValueError as e:
    # Log the issue but don't fail the main operation
    logger.warning(f"Failed to create appointment history: {str(e)}")
    # Continue - history creation is not critical
```

## Idempotency Pattern

### When to Use Idempotency Keys

Use idempotency keys for ALL operations that:
- Create resources (POST requests)
- Process payments
- Send notifications
- Trigger side effects

### Implementation Pattern

```typescript
// Frontend: Generate idempotency key
const idempotencyKey = crypto.randomUUID();

const { mutate: createBooking } = useMutation({
  mutationFn: async (input: CreateBookingInput) => {
    const { data } = await apiClient.post("/appointments", input, {
      headers: { "Idempotency-Key": idempotencyKey }
    });
    return data;
  },
});
```

```python
# Backend: Check idempotency key
@router.post("/appointments")
async def create_appointment(
    request: AppointmentCreateRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    # Check if this request was already processed
    if idempotency_key:
        existing = Appointment.objects(
            tenant_id=tenant_id,
            idempotency_key=idempotency_key
        ).first()
        if existing:
            return AppointmentResponse.from_orm(existing)
    
    # Process new request
    appointment = AppointmentService.create_appointment(
        tenant_id=tenant_id,
        idempotency_key=idempotency_key,
        # ... other params
    )
    return AppointmentResponse.from_orm(appointment)
```

## Error Handling Best Practices

### Frontend Error Handling

```typescript
// Always use getErrorMessage utility
import { getErrorMessage } from "@/lib/utils/api";

const { mutate: createBooking } = useMutation({
  mutationFn: async (input) => {
    const { data } = await apiClient.post("/appointments", input);
    return data;
  },
  onError: (error) => {
    const message = getErrorMessage(error);
    showToast({ 
      variant: "error", 
      title: "Booking Failed", 
      description: message 
    });
  },
});
```

### Backend Error Handling

```python
# Use specific exception types
@router.post("/appointments")
async def create_appointment(request: AppointmentCreateRequest):
    try:
        appointment = AppointmentService.create_appointment(...)
        return AppointmentResponse(...)
    except ValueError as e:
        # Business logic errors (400)
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        # Authorization errors (403)
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        # Unexpected errors (500)
        logger.error(f"Error creating appointment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Code Review Checklist

Before committing code, verify:

### Frontend Checklist
- [ ] No promise chains (`.then()`) in components - use React Query
- [ ] All POST requests include idempotency keys
- [ ] All mutations have `onError` handlers
- [ ] Error messages use `getErrorMessage()` utility
- [ ] No `useState` for server data - use React Query
- [ ] Data transformation (snake_case → camelCase) in hooks

### Backend Checklist
- [ ] All exceptions are logged before raising
- [ ] No bare `except Exception` without logging
- [ ] No silent exception swallowing (`except: pass`)
- [ ] Idempotency keys checked for POST endpoints
- [ ] Type hints on all function parameters
- [ ] Docstrings on all public functions
- [ ] Specific exception types (ValueError, PermissionError, etc.)

## REMEMBER

- ✅ Ask before making changes
- ✅ NEVER use modals to ask questions - ask directly in chat
- ✅ Use modern 2026 libraries
- ✅ Follow existing patterns
- ✅ Use React Query for server state (NO promise chains)
- ✅ Transform snake_case ↔ camelCase
- ✅ Write property-based tests
- ✅ Document your code
- ✅ Handle errors properly (always log)
- ✅ Include idempotency keys on POST requests
- ✅ Never swallow exceptions silently
- ✅ All service methods must be @staticmethod
- ✅ Use contextual prefixes in log messages
- ✅ Define database indexes for all models
- ✅ Check idempotency keys before creating resources

---

**Last Updated**: 2026-03-30
**Version**: 1.2.0
