# Phase 7 - Point of Sale (POS) Implementation Plan

## Overview

This implementation plan breaks down the Phase 7 POS system into actionable coding tasks organized by component. The plan follows a layered approach, starting with data models, then services, then API routes, and finally frontend components. Each task builds on previous tasks, ensuring incremental progress and early validation of core functionality.

**Technology Stack:**
- Backend: Python 3.11+ with FastAPI
- Database: MongoDB Atlas
- Cache: Redis 7+
- Payment Gateway: Paystack
- Frontend: React 19+ with TypeScript, Vite, Zustand, @tanstack/react-query
- Testing: pytest for unit tests, Hypothesis for property-based tests

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

- [x]* 2.1.1 Write property test for transaction immutability
  - **Property 1: Transaction Immutability**
  - **Validates: Requirements 70.4**

- [x]* 2.1.2 Write property test for transaction total calculation
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

- [x]* 2.3.1 Write property test for inventory deduction accuracy
  - **Property 2: Inventory Deduction Accuracy**
  - **Validates: Requirements 72.1**

- [x]* 2.3.2 Write property test for refund inventory restoration
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

- [x]* 2.4.1 Write property test for receipt generation completeness
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

- [x]* 2.5.1 Write property test for discount calculation accuracy
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

- [x]* 2.7.1 Write property test for commission calculation accuracy
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

- [x]* 2.8.1 Write property test for audit trail completeness
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

- [ ] 4.1 Write unit tests for POS services
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

- [ ] 4.2 Write integration tests for POS API
  - Test complete transaction flow from creation to receipt
  - Test payment processing with Paystack
  - Test inventory deduction and restoration
  - Test refund processing
  - Test commission calculation and payout
  - Test discount application
  - Test offline mode and sync
  - _Requirements: 70.1-80.5_

#### 4.3 Checkpoint - Ensure all POS backend tests pass

- [ ] 4.3 Checkpoint - Ensure all POS backend tests pass
  - Run all unit tests: `pytest backend/tests/unit/`
  - Run all property-based tests: `pytest backend/tests/unit/ -k property`
  - Run all integration tests: `pytest backend/tests/integration/`
  - Verify code coverage >90%
  - Ensure all tests pass, ask the user if questions arise.

---

### 5. Frontend: POS Dashboard and Components

#### 5.1 Create POS dashboard page

- [ ] 5.1 Create POS dashboard page
  - Create pages/pos/POSDashboard.tsx as main entry point
  - Display transaction summary (today's sales, transaction count, average transaction)
  - Display quick action buttons (New Transaction, View Receipts, Refunds, Reports)
  - Display recent transactions list
  - Display payment method breakdown
  - Display low-stock alerts
  - _Requirements: 70.1, 73.1_

#### 5.2 Create transaction entry component

- [ ] 5.2 Create transaction entry component
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

- [ ] 5.3 Create discount application component
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

- [ ] 5.4 Create payment processing component
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

- [ ] 5.5 Create receipt display and printing component
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

- [ ] 5.6 Create refund processing component
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

- [ ] 5.7 Create POS reporting component
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

- [ ] 7.3 Implement offline UI indicators
  - Create components/pos/OfflineIndicator.tsx component
  - Display offline status
  - Display sync progress
  - Display pending transaction count
  - _Requirements: 75.1_

---

### 8. Frontend: POS Testing

#### 8.1 Write unit tests for POS components

- [ ] 8.1 Write unit tests for POS components
  - Test transaction entry component
  - Test discount application component
  - Test payment processing component
  - Test receipt display component
  - Test refund processing component
  - Test POS reporting component
  - _Requirements: 70.1-80.5_

#### 8.2 Write integration tests for POS flow

- [ ] 8.2 Write integration tests for POS flow
  - Test complete transaction flow from entry to receipt
  - Test payment processing
  - Test refund processing
  - Test offline mode and sync
  - Test discount application
  - _Requirements: 70.1-80.5_

#### 8.3 Checkpoint - Ensure all POS frontend tests pass

- [ ] 8.3 Checkpoint - Ensure all POS frontend tests pass
  - Run all unit tests: `npm run test` (frontend)
  - Run all integration tests
  - Verify code coverage >90%
  - Ensure all tests pass, ask the user if questions arise.

---

### 9. Integration: POS with Existing Systems

#### 9.1 Link POS transactions to appointments

- [ ] 9.1 Link POS transactions to appointments
  - Update appointment model to include transaction_id reference
  - When appointment is completed, create transaction automatically
  - Link transaction to appointment for audit trail
  - _Requirements: 70.1_

#### 9.2 Link POS transactions to invoices

- [ ] 9.2 Link POS transactions to invoices
  - Update invoice model to include transaction_id reference
  - When transaction is completed, create invoice automatically
  - Link transaction to invoice for financial tracking
  - _Requirements: 70.1_

#### 9.3 Link POS transactions to inventory

- [ ] 9.3 Link POS transactions to inventory
  - When transaction is completed, deduct inventory automatically
  - When refund is processed, restore inventory automatically
  - Track inventory movements for audit trail
  - _Requirements: 72.1, 72.2, 72.3_

#### 9.4 Link POS transactions to customers

- [ ] 9.4 Link POS transactions to customers
  - Update customer model to include transaction history
  - Calculate customer lifetime value from transactions
  - Track customer purchase patterns
  - _Requirements: 70.1_

#### 9.5 Link POS transactions to staff

- [ ] 9.5 Link POS transactions to staff
  - Track which staff member processed each transaction
  - Calculate staff commission from transactions
  - Track staff performance metrics
  - _Requirements: 79.1, 79.2, 79.3_

#### 9.6 Link POS transactions to audit logs

- [ ] 9.6 Link POS transactions to audit logs
  - Log all transaction creation and modifications
  - Log all payment processing
  - Log all refunds
  - Log all discounts applied
  - _Requirements: 80.1, 80.2, 80.3_

---

### 10. Final Integration and Testing

#### 10.1 Write end-to-end tests for POS system

- [ ] 10.1 Write end-to-end tests for POS system
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

- [ ] 10.4 Checkpoint - Ensure all POS tests pass
  - Run all unit tests: `npm run test` (frontend) and `pytest` (backend)
  - Run all property-based tests
  - Run all integration tests
  - Run all end-to-end tests
  - Verify code coverage >90%
  - Ensure all tests pass, ask the user if questions arise.

---

## Summary

Phase 7 POS implementation includes:

1. **Backend Data Models**: Transaction, Cart, Receipt, Refund, Discount, Commission models
2. **Backend Services**: Transaction, Payment, Inventory, Receipt, Discount, Refund, Commission, Audit services
3. **Backend API Routes**: Transaction, Payment, Receipt, Discount, Refund, Commission, Reporting routes
4. **Frontend Components**: POS Dashboard, Transaction Entry, Payment Processing, Receipt Display, Refund Processing, Reporting
5. **Frontend Hooks**: useCart, useCheckout, useReceipt, useRefund, useDiscount, usePayment, usePOSReports
6. **Offline Mode**: IndexedDB storage, sync queue, conflict resolution
7. **Integration**: Link POS with appointments, invoices, inventory, customers, staff, audit logs
8. **Testing**: Unit tests, property-based tests, integration tests, end-to-end tests

All tasks include comprehensive testing with property-based tests validating correctness properties and unit/integration tests validating specific examples and edge cases.

