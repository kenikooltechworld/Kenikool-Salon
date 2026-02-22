# PHASE 1 POS CRITICAL GAPS - COMPLETE WIRING DIAGRAM

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  POSDashboard.tsx                                                │
│  ├─ Renders RefundProcessor when activeTab === "refunds"        │
│  └─ Renders TransactionEntry when activeTab === "transaction"   │
│                                                                   │
│  RefundProcessor.tsx                                             │
│  ├─ Imports: useCreateRefund from useRefund.ts                  │
│  ├─ Calls: createRefund() mutation                              │
│  └─ Endpoint: POST /pos/refunds                                 │
│                                                                   │
│  TransactionEntry.tsx                                            │
│  ├─ Uses: usePOSStore for cart management                       │
│  ├─ Calls: useCheckout() for transaction creation               │
│  └─ Endpoint: POST /pos/transactions                            │
│                                                                   │
│  Hooks:                                                          │
│  ├─ useCart.ts (6 functions)                                    │
│  │  ├─ useCreateCart() → POST /pos/carts                        │
│  │  ├─ useCart() → GET /pos/carts/{id}                          │
│  │  ├─ useAddToCart() → POST /pos/carts/{id}/items              │
│  │  ├─ useRemoveFromCart() → DELETE /pos/carts/{id}/items/{id}  │
│  │  ├─ useUpdateCartItem() → PUT /pos/carts/{id}/items/{id}     │
│  │  └─ useClearCart() → DELETE /pos/carts/{id}                  │
│  │                                                                │
│  └─ useRefund.ts (6 functions)                                  │
│     ├─ useCreateRefund() → POST /pos/refunds                    │
│     ├─ useRefund() → GET /pos/refunds/{id}                      │
│     ├─ useRefunds() → GET /pos/refunds                          │
│     ├─ useApproveRefund() → PUT /pos/refunds/{id}/approve       │
│     ├─ useProcessRefund() → PUT /pos/refunds/{id}/process       │
│     └─ useReverseRefund() → PUT /pos/refunds/{id}/reverse       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  main.py                                                         │
│  ├─ Imports: pos_carts, pos_refunds from routes                 │
│  └─ Registers: app.include_router(pos_carts.router)             │
│               app.include_router(pos_refunds.router)             │
│                                                                   │
│  routes/__init__.py                                              │
│  ├─ Imports: pos_carts, pos_refunds modules                     │
│  └─ Exports: Both modules in __all__                            │
│                                                                   │
│  routes/pos_carts.py (7 endpoints)                              │
│  ├─ POST /api/pos/carts → create_cart()                         │
│  ├─ GET /api/pos/carts/{id} → get_cart()                        │
│  ├─ PUT /api/pos/carts/{id} → update_cart()                     │
│  ├─ DELETE /api/pos/carts/{id} → delete_cart()                  │
│  ├─ POST /api/pos/carts/{id}/items → add_item_to_cart()         │
│  ├─ DELETE /api/pos/carts/{id}/items/{id} → remove_item()       │
│  └─ PUT /api/pos/carts/{id}/items/{id} → update_quantity()      │
│                                                                   │
│  routes/pos_refunds.py (6 endpoints)                            │
│  ├─ POST /api/pos/refunds → create_refund()                     │
│  ├─ GET /api/pos/refunds → list_refunds()                       │
│  ├─ GET /api/pos/refunds/{id} → get_refund()                    │
│  ├─ PUT /api/pos/refunds/{id}/approve → approve_refund()        │
│  ├─ PUT /api/pos/refunds/{id}/process → process_refund()        │
│  └─ PUT /api/pos/refunds/{id}/reverse → reverse_refund()        │
│                                                                   │
│  routes/pos_transactions.py                                      │
│  └─ POST /api/pos/transactions → create_transaction()           │
│     └─ Calls: TransactionService.create_transaction()           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  TransactionService.create_transaction()                         │
│  │                                                                │
│  ├─ Step 1: Validate items                                      │
│  │                                                                │
│  ├─ Step 2: Create TransactionItem objects                      │
│  │                                                                │
│  ├─ Step 3: ✅ CHECK INVENTORY                                  │
│  │   └─ InventoryDeductionService.check_inventory_availability()│
│  │      └─ Validates: quantity <= available stock               │
│  │      └─ Raises: ValueError if insufficient                   │
│  │                                                                │
│  ├─ Step 4: ✅ APPLY DISCOUNT (if discount_code)                │
│  │   └─ DiscountService.apply_discount()                        │
│  │      ├─ Validates: code exists, active, not expired          │
│  │      ├─ Checks: usage limit not exceeded                     │
│  │      ├─ Calculates: discount amount (%, fixed, etc)          │
│  │      └─ Returns: discount_amount or raises ValueError         │
│  │                                                                │
│  ├─ Step 5: Calculate totals                                    │
│  │   └─ total = subtotal - discount + tax                       │
│  │                                                                │
│  ├─ Step 6: Create and save Transaction                         │
│  │                                                                │
│  ├─ Step 7: ✅ DEDUCT INVENTORY                                 │
│  │   └─ InventoryDeductionService.deduct_inventory()            │
│  │      ├─ Reduces: inventory.quantity -= item.quantity         │
│  │      ├─ Creates: InventoryTransaction record                 │
│  │      └─ Generates: Low stock alerts if needed                │
│  │                                                                │
│  └─ Step 8: ✅ CALCULATE COMMISSION                             │
│      └─ CommissionService.calculate_commission()                │
│         ├─ Gets: commission_rate from staff or parameter        │
│         ├─ Calculates: amount based on type (%, fixed)          │
│         └─ Creates: StaffCommission record                      │
│                                                                   │
│  RefundService.create_refund()                                   │
│  ├─ Validates: payment exists and is success status             │
│  ├─ Validates: refund amount <= original amount                 │
│  ├─ Checks: no duplicate refund exists                          │
│  ├─ Calls: Paystack API to process refund                       │
│  └─ Creates: Refund document with pending status                │
│                                                                   │
│  InventoryDeductionService                                       │
│  ├─ check_inventory_availability() - Pre-transaction check      │
│  ├─ deduct_inventory() - Reduces stock after transaction        │
│  ├─ restore_inventory() - Restores stock on cancellation        │
│  └─ generate_low_stock_alert() - Creates alerts                 │
│                                                                   │
│  DiscountService                                                 │
│  ├─ apply_discount() - Validates and applies discount           │
│  ├─ validate_discount_code() - Checks validity                  │
│  ├─ calculate_discount_amount() - Calculates amount             │
│  └─ check_discount_conditions() - Validates conditions          │
│                                                                   │
│  CommissionService                                               │
│  ├─ calculate_commission() - Creates commission record          │
│  ├─ calculate_total_commission() - Sums for period              │
│  ├─ get_commission_structure() - Gets staff settings            │
│  └─ calculate_payout() - Calculates payout                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER (MongoDB)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Models:                                                         │
│  ├─ Cart                                                         │
│  │  ├─ customer_id, staff_id                                    │
│  │  ├─ items (CartItem[])                                       │
│  │  ├─ subtotal, tax_amount, discount_amount, total             │
│  │  └─ status (active, completed, abandoned)                    │
│  │                                                                │
│  ├─ Refund                                                       │
│  │  ├─ payment_id, amount, reason                               │
│  │  ├─ status (pending, success, failed)                        │
│  │  ├─ reference (Paystack reference)                           │
│  │  └─ metadata (additional data)                               │
│  │                                                                │
│  ├─ Transaction                                                  │
│  │  ├─ customer_id, staff_id                                    │
│  │  ├─ items (TransactionItem[])                                │
│  │  ├─ subtotal, tax_amount, discount_amount, total             │
│  │  ├─ payment_method, payment_status                           │
│  │  └─ reference_number                                         │
│  │                                                                │
│  ├─ Inventory                                                    │
│  │  ├─ name, sku, quantity                                      │
│  │  ├─ reorder_level, unit_cost                                 │
│  │  └─ category                                                 │
│  │                                                                │
│  ├─ Discount                                                     │
│  │  ├─ discount_code, discount_type, discount_value             │
│  │  ├─ applicable_to, conditions                                │
│  │  ├─ valid_from, valid_until, usage_limit                     │
│  │  └─ active, usage_count                                      │
│  │                                                                │
│  └─ StaffCommission                                              │
│     ├─ staff_id, transaction_id                                 │
│     ├─ commission_amount, commission_rate, commission_type      │
│     └─ calculated_at                                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Examples

### Example 1: Create Transaction with All Integrations

```
Frontend: RefundProcessor.tsx
  ↓
POST /pos/transactions
  {
    customerId: "123",
    staffId: "456",
    items: [
      { itemType: "product", itemId: "789", quantity: 2, unitPrice: 100 }
    ],
    discountCode: "SAVE10"
  }
  ↓
Backend: pos_transactions.py → create_transaction()
  ↓
TransactionService.create_transaction()
  ├─ Validate items
  ├─ Create TransactionItem objects
  ├─ ✅ Check inventory: 2 units available? YES
  ├─ ✅ Apply discount: SAVE10 = 10% = $20
  ├─ Calculate: total = 200 - 20 + 18 (tax) = $198
  ├─ Save Transaction
  ├─ ✅ Deduct inventory: quantity = 98 (100 - 2)
  ├─ ✅ Calculate commission: 5% of $198 = $9.90
  └─ Return Transaction
  ↓
Frontend: Success message displayed
```

### Example 2: Create Refund

```
Frontend: RefundProcessor.tsx
  ↓
POST /pos/refunds
  {
    paymentId: "payment_123",
    amount: 100,
    reason: "Customer request"
  }
  ↓
Backend: pos_refunds.py → create_refund()
  ↓
RefundService.create_refund()
  ├─ Validate: payment exists? YES
  ├─ Validate: payment status = success? YES
  ├─ Validate: amount <= original? YES
  ├─ Check: no duplicate refund? YES
  ├─ Call Paystack API
  ├─ Create Refund document (status: pending)
  └─ Return Refund
  ↓
Frontend: Refund created, awaiting processing
```

## Verification Checklist

### Backend ✅
- [x] Routes imported and registered
- [x] All endpoints have decorators
- [x] All endpoints have response models
- [x] All endpoints have error handling
- [x] Services imported in transaction_service
- [x] Services called in correct order
- [x] Models have all required fields
- [x] Schemas validate request/response
- [x] Audit logging integrated
- [x] No syntax errors

### Frontend ✅
- [x] Hooks created with correct endpoints
- [x] Hooks use /pos/ prefix
- [x] Components import hooks
- [x] Components rendered in POSDashboard
- [x] Tab navigation working
- [x] Query invalidation on mutations
- [x] Error handling implemented
- [x] Loading states implemented
- [x] No syntax errors

### Integration ✅
- [x] Inventory check before transaction
- [x] Inventory deduction after transaction
- [x] Discount validation and application
- [x] Commission calculation
- [x] Error handling and rollback
- [x] Audit logging
- [x] Proper HTTP status codes
- [x] Proper error messages

## Status: ✅ COMPLETE AND FULLY WIRED

All Phase 1 critical gaps are implemented, integrated, and ready for testing.
