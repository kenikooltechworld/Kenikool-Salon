# Customer Feature Integration Test Plan

This document outlines the test plan to verify that all customer features are fully integrated and working end-to-end.

## Backend Tests

### 1. Customer Balance Management
```bash
# Test customer balance endpoints
curl -X GET "http://localhost:8000/customers/{customer_id}/balance" \
  -H "Authorization: Bearer {token}"

curl -X PUT "http://localhost:8000/customers/{customer_id}/balance" \
  -H "Authorization: Bearer {token}"

curl -X GET "http://localhost:8000/customers/{customer_id}/booking-eligibility" \
  -H "Authorization: Bearer {token}"
```

### 2. Customer Preferences
```bash
# Test customer preferences endpoints
curl -X GET "http://localhost:8000/customers/{customer_id}/preferences" \
  -H "Authorization: Bearer {token}"

curl -X PUT "http://localhost:8000/customers/{customer_id}/preferences" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_staff_ids": ["staff_id_1"],
    "preferred_service_ids": ["service_id_1"],
    "communication_methods": ["email", "sms"],
    "preferred_time_slots": ["morning"],
    "language": "en",
    "notes": "Test preferences"
  }'
```

### 3. Portal Invitations
```bash
# Test portal invitation resend
curl -X POST "http://localhost:8000/customers/{customer_id}/resend-portal-invitation" \
  -H "Authorization: Bearer {token}"
```

## Frontend Tests

### 1. Customer List Page (`/customers`)
- [ ] Displays all customers with pagination
- [ ] Shows customer status badges (Active/Inactive, Guest, Outstanding Balance)
- [ ] Search functionality works
- [ ] Status filtering works
- [ ] Create customer button opens modal
- [ ] Edit/Delete actions work
- [ ] Click on customer navigates to detail page

### 2. Customer Detail Page (`/customers/{id}`)
- [ ] Shows customer information in tabs layout
- [ ] **Profile Tab**: Displays contact information
- [ ] **Balance Tab**: Shows balance widget with:
  - [ ] Outstanding balance amount
  - [ ] Booking eligibility status
  - [ ] List of unpaid invoices
  - [ ] Recalculate balance button works
- [ ] **Preferences Tab**: Shows preferences panel with:
  - [ ] Preferred staff selection
  - [ ] Preferred services selection
  - [ ] Time slots preferences
  - [ ] Communication methods
  - [ ] Language selection
  - [ ] Notes field
  - [ ] Edit/Save functionality
- [ ] **History Tab**: Shows appointment history
- [ ] Portal invitation button works
- [ ] Edit customer button opens modal
- [ ] Delete customer with confirmation

### 3. Customer Balance Component
- [ ] Loads balance data correctly
- [ ] Shows eligibility status with appropriate badges
- [ ] Displays unpaid invoices with details
- [ ] Recalculate button updates balance
- [ ] Shows "no balance" message when balance is 0
- [ ] Error states handled properly

### 4. Customer Preferences Panel
- [ ] Loads current preferences
- [ ] Edit mode enables form fields
- [ ] Staff selection with checkboxes
- [ ] Service selection with checkboxes
- [ ] Time slot selection
- [ ] Communication method selection
- [ ] Language dropdown
- [ ] Notes textarea
- [ ] Save/Cancel buttons work
- [ ] Form validation

## Integration Tests

### 1. Customer Creation Flow
1. Owner creates customer via form
2. Customer receives welcome email with portal setup link
3. Customer can set up password and access portal
4. Customer appears in customer list
5. Customer preferences can be set by owner
6. Customer balance is tracked

### 2. Customer Balance Flow
1. Customer has unpaid invoices
2. Balance is calculated automatically
3. Owner can see balance in customer detail
4. Booking eligibility is checked
5. Balance can be recalculated manually
6. Customer cannot book if balance > 0

### 3. Customer Preferences Flow
1. Owner sets customer preferences
2. Preferences are saved to backend
3. Preferences display correctly in UI
4. Preferences can be edited and updated
5. Empty preferences show appropriate messages

### 4. Portal Invitation Flow
1. Owner creates customer
2. Welcome email sent automatically
3. Owner can resend invitation manually
4. Customer receives setup link
5. Customer can set up password
6. Customer can access portal

## Data Transformation Tests

### 1. Snake Case to Camel Case
- [ ] Backend `first_name` → Frontend `firstName`
- [ ] Backend `outstanding_balance` → Frontend `outstandingBalance`
- [ ] Backend `preferred_staff_ids` → Frontend `preferredStaffIds`
- [ ] Backend `communication_methods` → Frontend `communicationMethods`

### 2. API Response Structure
- [ ] Customer list returns proper pagination
- [ ] Customer detail returns all fields
- [ ] Balance API returns proper structure
- [ ] Preferences API returns proper structure

## Error Handling Tests

### 1. Backend Errors
- [ ] Customer not found returns 404
- [ ] Invalid data returns 400 with details
- [ ] Authorization errors return 401/403
- [ ] Server errors return 500

### 2. Frontend Error Handling
- [ ] Network errors show toast messages
- [ ] Loading states display properly
- [ ] Retry mechanisms work
- [ ] Fallback UI for missing data

## Performance Tests

### 1. Customer List Performance
- [ ] Pagination handles large datasets
- [ ] Search is responsive
- [ ] Filters don't block UI

### 2. Customer Detail Performance
- [ ] Tabs switch instantly
- [ ] Balance calculation is fast
- [ ] Preferences load quickly

## Security Tests

### 1. Authentication
- [ ] All endpoints require proper authentication
- [ ] Tenant isolation is enforced
- [ ] Customer data is protected

### 2. Authorization
- [ ] Owners can manage all customers
- [ ] Customers can only access own data
- [ ] Staff permissions are proper

## Browser Compatibility Tests
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile responsiveness

## Accessibility Tests
- [ ] Keyboard navigation works
- [ ] Screen reader compatibility
- [ ] ARIA labels present
- [ ] Color contrast adequate
- [ ] Focus indicators visible

## Regression Tests
- [ ] Existing customer functionality unchanged
- [ ] Other features still work
- [ ] No performance degradation
- [ ] No memory leaks

## Success Criteria

All customer features are considered fully integrated when:

1. **✅ Backend APIs** work correctly with proper error handling
2. **✅ Frontend Components** render and function properly
3. **✅ Data Flow** works end-to-end with proper transformations
4. **✅ User Experience** is smooth and intuitive
5. **✅ Error Handling** is comprehensive and user-friendly
6. **✅ Performance** meets acceptable standards
7. **✅ Security** requirements are met
8. **✅ Accessibility** standards are followed

## Test Environment Setup

### Backend
```bash
cd backend
python -m pytest tests/test_customer_integration.py -v
```

### Frontend
```bash
cd salon
npm run test -- --watch=false --testPathPattern=customer
```

### End-to-End
```bash
cd salon
npm run test:e2e -- --spec="customers/**/*"
```

## Manual Testing Checklist

### Owner Workflow
1. [ ] Login as salon owner
2. [ ] Navigate to customers page
3. [ ] Create new customer
4. [ ] Verify customer appears in list
5. [ ] Click on customer to view details
6. [ ] Switch between all tabs
7. [ ] Edit customer preferences
8. [ ] Check customer balance
9. [ ] Send portal invitation
10. [ ] Delete customer (test account only)

### Customer Workflow
1. [ ] Receive welcome email
2. [ ] Click setup link
3. [ ] Set password
4. [ ] Login to customer portal
5. [ ] View booking history
6. [ ] Update profile information
7. [ ] Check outstanding balance

### Integration Verification
1. [ ] Owner changes → reflect in customer portal
2. [ ] Customer changes → visible to owner
3. [ ] Balance updates → affect booking eligibility
4. [ ] Preferences → properly stored and retrieved
5. [ ] Email notifications → sent successfully

This comprehensive test plan ensures that all customer features are working correctly and integrated properly across the entire application.