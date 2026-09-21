# POS & Related Issues Audit

Date: 2026-09-19
Scope: Backend (`backend/app`) + Frontend (`salon/src`) POS, receipt, inventory, report, and websocket flows

---

## 1. Critical Bugs

### 1.1 POS Receipt Shows "Invalid Date"
**Severity:** Critical  
**Files involved:**
- Backend: `backend/app/schemas/receipt.py`, `backend/app/schemas/transaction.py`
- Frontend: `salon/src/hooks/useReceipt.ts`, `salon/src/components/pos/ReceiptDisplay.tsx`, `salon/src/pages/pos/ReceiptHistory.tsx`, `salon/src/pages/pos/POSDashboard.tsx`, `salon/src/components/pos/RefundProcessor.tsx`

**Problem:** Backend Pydantic response schemas serialize JSON keys in `snake_case`, but the frontend TypeScript interfaces and components expect `camelCase`.

When the frontend reads `receipt.receiptDate`, it is `undefined` because the actual JSON key is `receipt_date`. `new Date(undefined)` produces `Invalid Date`.

**Mismatched fields:**
| Backend JSON key | Frontend expected | Used in |
|---|---|---|
| `receipt_date` | `receiptDate` | `ReceiptDisplay.tsx:108`, `ReceiptHistory.tsx:215,287` |
| `created_at` | `createdAt` | `POSDashboard.tsx:311`, `RefundProcessor.tsx:116` |
| `payment_method` | `paymentMethod` | `ReceiptHistory.tsx:225` |
| `payment_reference` | `paymentReference` | `useReceipt.ts:30` |
| `receipt_format` | `receiptFormat` | `useReceipt.ts:31` |
| `printed_at` | `printedAt` | `ReceiptHistory.tsx:227` |
| `emailed_at` | `emailedAt` | `ReceiptHistory.tsx:232` |
| `tax_amount` | `taxAmount` | `useReceipt.ts:26`, POSDashboard totals |
| `discount_amount` | `discountAmount` | `useReceipt.ts:27`, POSDashboard totals |
| `transaction_id` | `transactionId` | `useReceipt.ts:17` |
| `customer_id` | `customerId` | `POSDashboard.tsx:308`, `RefundProcessor.tsx:113` |
| `staff_id` | `staffId` | various |
| `transaction_type` | `transactionType` | `useCheckout.ts:21` |
| `payment_status` | `paymentStatus` | `POSDashboard.tsx:332` |
| `reference_number` | `referenceNumber` | `useCheckout.ts:29` |

**Report endpoints also affected:**
- Backend returns: `total_sales`, `total_transactions`, `average_transaction`, `period.start_date`, `period.end_date`, `total_revenue`, `total_tax`, `total_discount`, `net_revenue`
- Frontend expects: `totalSales`, `totalTransactions`, `averageTransaction`, `period.startDate`, `period.endDate`, `totalRevenue`, `totalTax`, `totalDiscount`, `netRevenue`

---

### 1.2 PDF Receipt Download Returns 404
**Severity:** Critical  
**Files involved:**
- Frontend: `salon/src/components/pos/ReceiptDisplay.tsx:232-236`, `salon/src/hooks/useReceipt.ts:128-136`
- Backend: `backend/app/routes/pos_receipts.py`

**Problem A:** `ReceiptDisplay.tsx` uses an `<a href>` link pointing to `/receipts/${receipt.id}/pdf`. This path is **not** proxied by Vite’s `/api` proxy, so it hits the Vite dev server and 404s.

**Problem B:** Backend `pos_receipts.py` **does not define** `GET /{receipt_id}/pdf`. Even the API hook `useDownloadReceiptPDF` would 404.

---

### 1.3 Inventory Report Server Error (500)
**Severity:** Critical  
**Files involved:**
- Backend: `backend/app/routes/pos_reports.py:86-115`, `backend/app/models/inventory.py`

**Problem:** `pos_reports.py:99-106` references non-existent fields on the `Inventory` model:
- `inv.product_id`
- `inv.quantity_on_hand`
- `inv.reorder_point`

The actual `Inventory` model has:
- `name`, `sku`, `quantity`, `reorder_level`, `unit_cost`, `unit`, `category`, `supplier_id`, `last_restocked_at`, `expiry_date`, `is_active`, `notes`

This endpoint throws `AttributeError` and returns 500.

---

## 2. Broken Functionality

### 2.1 `useGenerateReceipt` Cache Pollution
**Severity:** High  
**Files involved:**
- Backend: `backend/app/routes/pos_transactions.py:523-584`
- Frontend: `salon/src/hooks/useReceipt.ts:142-158`

**Problem:** Frontend calls `POST /transactions/{id}/generate-receipt` and expects the response to be a full `Receipt` object with `transactionId`. Backend returns only:
```json
{ "success": true, "message": "...", "transaction_id": "..." }
```
Not a receipt object.

Result: `onSuccess` reads `receipt.transactionId` which is `undefined`, then caches under `["receipts", undefined]`. The actual receipt display won’t populate from this cache entry.

---

### 2.2 `useCheckout` / `TransactionEntry` Cart Totals Not Synced
**Severity:** Medium  
**Files involved:**
- Frontend: `salon/src/components/pos/TransactionEntry.tsx:80-83`, `salon/src/stores/pos.ts:151-162`

**Problem:** After successful checkout, `TransactionEntry` calls `calculateCartTotals()` which reads from `state.cartItems`. However, the cart is **not cleared** at this point — `clearCart()` is only called inside `PaymentProcessor.tsx` after receipt generation. So `calculateCartTotals()` runs on stale data, potentially showing incorrect totals briefly.

---

### 2.3 POS Dashboard Transaction Date Rendering
**Severity:** Medium  
**Files involved:**
- Frontend: `salon/src/pages/pos/POSDashboard.tsx:311`, `salon/src/components/pos/RefundProcessor.tsx:116`

**Problem:** Both call `new Date(transaction.createdAt)`, but `createdAt` is `undefined` due to the snake_case mismatch. Every transaction date renders as `Invalid Date`.

---

## 3. Code Quality / Inconsistency Issues

### 3.1 Duplicate `@staticmethod` Decorators
**Severity:** Low  
**File:** `backend/app/services/transaction_service.py:338-339, 364-365`

**Problem:** `validate_transaction_data` and `calculate_totals` have `@staticmethod` applied twice. Python tolerates this, but it indicates sloppy editing and could confuse linters or future maintainers.

---

### 3.2 Duplicate Socket.IO Handler Code Block
**Severity:** Low  
**File:** `backend/app/socketio_handler.py:1-121` and `124-272`

**Problem:** The file contains two near-identical code blocks defining `sio`, event handlers (`connect`, `disconnect`, `dashboard_update`, `join_availability_room`, `leave_availability_room`), and helper functions. Functionally harmless but a maintenance hazard.

---

### 3.3 Frontend `TransactionItem.lineTota` Typo
**Severity:** Low  
**File:** `salon/src/hooks/useCheckout.ts:11`

**Problem:** The interface defines `lineTota: number` instead of `lineTotal`. This is a TypeScript type-only issue (doesn’t break runtime), but it’s inconsistent with the backend field name and with the `CartItem` interface in `salon/src/stores/pos.ts:9`.

---

## 4. Previously Fixed (Context)

### 4.1 Inventory API 404s — FIXED
**Files modified:**
- `backend/app/main.py` — added `inventory` to routes import and `app.include_router(inventory.router, ...)`
- `backend/app/routes/__init__.py` — added `inventory` to package imports and `__all__`

**Status:** Backend now exposes `/api/v1/inventory`, `/api/v1/inventory/{id}`, `/api/v1/inventory/transactions/list`, `/api/v1/inventory/alerts/list`, `/api/v1/inventory/low-stock/list`, `/api/v1/inventory/value/summary`, etc.

---

### 4.2 WebSocket Disconnect Logs — NOT A BUG
**Files:** `salon/src/services/socket.ts`, `salon/src/hooks/useWebSocket.ts`, `salon/src/pages/dashboard/Dashboard.tsx`

**Problem observed:** Console logs showed `Socket.io disconnected` and `Dashboard WebSocket disconnected`.

**Finding:** These are expected debug logs emitted by the client’s disconnect handler. The Socket.IO client is configured with `reconnection: true` and will auto-reconnect. No actual error.

---

## 5. Summary

| # | Issue | Severity | Status |
|---|---|---|---|
| 1.1 | Receipt/Transaction snake_case vs camelCase mismatch causing Invalid Date | Critical | Open |
| 1.2 | PDF receipt download endpoint missing + frontend link wrong | Critical | Open |
| 1.3 | Inventory report references non-existent model fields | Critical | Open |
| 2.1 | `useGenerateReceipt` expects Receipt but backend returns status dict | High | Open |
| 2.2 | Cart totals briefly stale after checkout before clear | Medium | Open |
| 2.3 | POS dashboard/refund dates render Invalid Date | Medium | Open |
| 3.1 | Duplicate `@staticmethod` decorators | Low | Open |
| 3.2 | Duplicate Socket.IO code block in handler file | Low | Open |
| 3.3 | `lineTota` typo in `useCheckout.ts` interface | Low | Open |

**Recommended fix order:**
1. Fix backend schema serialization to use camelCase aliases globally for all POS/receipt/transaction/report schemas
2. Fix or align `POST /transactions/{id}/generate-receipt` response shape
3. Add `GET /receipts/{id}/pdf` backend endpoint
4. Fix `ReceiptDisplay.tsx` download link to use `/api/v1/receipts/${id}/pdf`
5. Fix inventory report to use actual `Inventory` model fields
6. Fix frontend date rendering by using correct camelCase keys
7. Clean up duplicate decorators and duplicate Socket.IO block
8. Fix `lineTota` typo
