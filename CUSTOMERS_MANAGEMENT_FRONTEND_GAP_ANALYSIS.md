# Customers Management - Frontend Gap Analysis

## Overview
The frontend Customers page is currently using **mock data** and is missing critical integration with the backend API. The backend has a fully functional customer management system, but the frontend is not utilizing it.

## Current Frontend Status

### What's Implemented
- ✅ Basic UI layout with table display
- ✅ Search functionality (client-side only)
- ✅ Delete button (non-functional)
- ✅ Edit button (non-functional)
- ✅ Add Customer button (non-functional)
- ✅ Responsive design

### What's Missing
- ❌ API integration with backend
- ❌ Real data fetching
- ❌ Create customer modal/form
- ❌ Edit customer modal/form
- ❌ Customer detail view
- ❌ Customer history display
- ❌ Customer preferences management
- ❌ Outstanding balance display
- ❌ Pagination
- ❌ Status filtering
- ❌ Loading states
- ❌ Error handling
- ❌ Empty state handling

---

## Backend API Endpoints Available

### 1. List Customers
**Endpoint**: `GET /customers`
**Query Parameters**:
- `search` - Search by name or phone
- `status` - Filter by status (active/inactive)
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10, max: 100)

**Response**:
```json
{
  "customers": [
    {
      "id": "string",
      "first_name": "string",
      "last_name": "string",
      "email": "string",
      "phone": "string",
      "address": "string",
      "date_of_birth": "ISO date",
      "preferred_staff_id": "string",
      "preferred_services": ["string"],
      "communication_preference": "email|sms|phone|none",
      "status": "active|inactive",
      "created_at": "ISO datetime",
      "updated_at": "ISO datetime"
    }
  ],
  "total": "number",
  "page": "number",
  "page_size": "number"
}
```

### 2. Get Single Customer
**Endpoint**: `GET /customers/{customer_id}`

**Response**: Single customer object (same structure as above)

### 3. Create Customer
**Endpoint**: `POST /customers`
**Required Fields**:
- `first_name` - string
- `last_name` - string
- `email` - string (unique per tenant)
- `phone` - string

**Optional Fields**:
- `address` - string
- `date_of_birth` - ISO date
- `preferred_staff_id` - string (Staff ID)
- `preferred_services` - array of Service IDs
- `communication_preference` - "email" | "sms" | "phone" | "none"
- `status` - "active" | "inactive"

### 4. Update Customer
**Endpoint**: `PUT /customers/{customer_id}`
**Fields**: Any of the fields from Create (all optional)

### 5. Delete Customer
**Endpoint**: `DELETE /customers/{customer_id}`

---

## Related Backend Features

### Customer History
**Endpoint**: `GET /customers/{customer_id}/history`
- Tracks all appointments for a customer
- Includes service, staff, ratings, and feedback

### Customer Preferences
**Endpoint**: `GET /customers/{customer_id}/preferences`
**PUT** `/customers/{customer_id}/preferences`
- Preferred staff members
- Preferred services
- Communication methods
- Preferred time slots
- Language preference
- Notes

### Customer Model Fields
```python
- first_name (required)
- last_name (required)
- email (required, unique per tenant)
- phone (required)
- address (optional)
- date_of_birth (optional)
- preferred_staff_id (optional)
- preferred_services (optional, array)
- communication_preference (default: "email")
- status (default: "active")
- outstanding_balance (tracks customer balance)
- created_at
- updated_at
```

---

## Missing Frontend Components & Features

### 1. **Customer List Page** (Customers.tsx)
**Current Issues**:
- Using mock data instead of API
- No pagination
- No status filtering
- No loading states
- No error handling
- Search is client-side only

**What Needs to be Added**:
```typescript
// Use useCustomers hook with filters
const { data, isLoading, error } = useCustomers({
  search: searchTerm,
  status: selectedStatus,
  page: currentPage,
  page_size: 10
});

// Display loading state
// Display error state
// Display pagination controls
// Display status filter dropdown
// Handle real delete/edit actions
```

### 2. **Create Customer Modal/Form**
**Missing Component**: `CustomerForm.tsx` or `CreateCustomerModal.tsx`

**Should Include**:
- Form fields:
  - First Name (required)
  - Last Name (required)
  - Email (required, unique validation)
  - Phone (required)
  - Address (optional)
  - Date of Birth (optional)
  - Preferred Staff (optional, dropdown)
  - Preferred Services (optional, multi-select)
  - Communication Preference (dropdown)
  - Status (dropdown)
- Form validation
- Submit handler using `useCreateCustomer()`
- Error handling
- Success notification

### 3. **Edit Customer Modal/Form**
**Missing Component**: Reuse `CustomerForm.tsx` with edit mode

**Should Include**:
- Pre-populate form with existing customer data
- Submit handler using `useUpdateCustomer()`
- Validation for email uniqueness (excluding current customer)
- Error handling
- Success notification

### 4. **Customer Detail Page**
**Missing Component**: `CustomerDetail.tsx` or `CustomerProfile.tsx`

**Should Display**:
- Customer basic information
- Outstanding balance
- Appointment history (using `useCustomerHistory`)
- Customer preferences (using `useCustomerPreferences`)
- Edit button
- Delete button
- Tabs for:
  - Overview
  - Appointment History
  - Preferences
  - Balance/Invoices

### 5. **Customer History Component**
**Missing Component**: `CustomerHistory.tsx` (exists but not used)

**Should Display**:
- List of past appointments
- Service name
- Staff name
- Appointment date/time
- Rating and feedback
- Pagination

### 6. **Customer Preferences Component**
**Missing Component**: `CustomerPreferences.tsx` (exists but not used)

**Should Display**:
- Preferred staff members (multi-select)
- Preferred services (multi-select)
- Communication methods (checkboxes)
- Preferred time slots (checkboxes)
- Language preference
- Notes
- Edit/Save functionality

### 7. **Outstanding Balance Display**
**Missing Feature**: Show customer balance in:
- Customer list (as a column)
- Customer detail page
- Customer card

### 8. **Status Filtering**
**Missing Feature**: Filter dropdown for:
- Active
- Inactive
- All

### 9. **Pagination**
**Missing Feature**:
- Previous/Next buttons
- Page number display
- Items per page selector
- Total count display

### 10. **Loading & Error States**
**Missing**:
- Loading spinner while fetching
- Error message display
- Empty state message
- Retry button on error

---

## Implementation Priority

### Phase 1 (Critical)
1. Update `Customers.tsx` to use `useCustomers` hook
2. Create `CustomerForm.tsx` component
3. Create Create/Edit modals
4. Add loading, error, and empty states
5. Implement real delete functionality

### Phase 2 (Important)
1. Create `CustomerDetail.tsx` page
2. Implement customer history display
3. Implement customer preferences management
4. Add pagination
5. Add status filtering

### Phase 3 (Nice to Have)
1. Add outstanding balance display
2. Add advanced search/filtering
3. Add bulk actions
4. Add export functionality
5. Add customer notes/tags

---

## Code Examples

### Using useCustomers Hook
```typescript
import { useCustomers, useCreateCustomer, useUpdateCustomer, useDeleteCustomer } from "@/hooks/useCustomers";

function Customers() {
  const [filters, setFilters] = useState({ search: "", status: "", page: 1 });
  const { data, isLoading, error } = useCustomers(filters);
  const createMutation = useCreateCustomer();
  const updateMutation = useUpdateCustomer();
  const deleteMutation = useDeleteCustomer();

  const handleCreate = async (customerData) => {
    await createMutation.mutateAsync(customerData);
  };

  const handleDelete = async (id) => {
    await deleteMutation.mutateAsync(id);
  };

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      {/* Search and filters */}
      {/* Table with real data */}
      {/* Pagination */}
    </div>
  );
}
```

### Customer Form Component
```typescript
interface CustomerFormProps {
  customer?: Customer;
  onSubmit: (data: Partial<Customer>) => Promise<void>;
  isLoading?: boolean;
}

export function CustomerForm({ customer, onSubmit, isLoading }: CustomerFormProps) {
  const [formData, setFormData] = useState(customer || {});
  const [errors, setErrors] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Validate
    // Call onSubmit
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
}
```

---

## Files to Create/Modify

### Create
- `salon/src/components/customers/CustomerForm.tsx` - Form for create/edit
- `salon/src/components/customers/CreateCustomerModal.tsx` - Modal wrapper
- `salon/src/components/customers/EditCustomerModal.tsx` - Modal wrapper
- `salon/src/pages/customers/CustomerDetail.tsx` - Detail page
- `salon/src/components/customers/CustomerHistoryTab.tsx` - History display
- `salon/src/components/customers/CustomerPreferencesTab.tsx` - Preferences display

### Modify
- `salon/src/pages/customers/Customers.tsx` - Use real API data
- `salon/src/hooks/useCustomers.ts` - Already good, just needs to be used

### Already Exist (Need to be used)
- `salon/src/hooks/useCustomerHistory.ts`
- `salon/src/hooks/useCustomerPreferences.ts`
- `salon/src/hooks/useCustomerWithDetails.ts`
- `salon/src/components/customers/CustomerHistory.tsx`
- `salon/src/components/customers/CustomerPreferences.tsx`

---

## Summary

The backend has a **complete and robust customer management system** with:
- ✅ Full CRUD operations
- ✅ Search and filtering
- ✅ Pagination
- ✅ Customer history tracking
- ✅ Customer preferences management
- ✅ Outstanding balance tracking
- ✅ Tenant isolation

The frontend is **missing critical integration** and needs:
- ❌ API integration
- ❌ Create/Edit forms
- ❌ Detail page
- ❌ History and preferences display
- ❌ Proper state management
- ❌ Error handling
- ❌ Loading states

**Estimated effort**: 2-3 days to fully implement all missing features.
