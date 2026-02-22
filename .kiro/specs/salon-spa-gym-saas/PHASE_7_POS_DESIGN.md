# Phase 7 - Point of Sale (POS) System Design

## Overview

The Phase 7 POS system provides a comprehensive point-of-sale solution for processing transactions, managing payments, tracking inventory, and generating receipts. The system integrates with existing appointment, invoice, and inventory systems to create a unified transaction management experience.

---

## 1. POS Architecture

### High-Level Architecture

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

### Component Responsibilities

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

---

## 2. Data Models

### Transaction Model

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

### Transaction Item Model

```python
class TransactionItem(EmbeddedDocument):
    item_type = StringField(
        choices=['service', 'product', 'package'],
        required=True
    )
    item_id = ObjectIdField(required=True)
    item_name = StringField(required=True)
    
    quantity = IntField(required=True)
    unit_price = DecimalField(required=True)
    line_total = DecimalField(required=True)  # quantity * unit_price
    
    tax_rate = DecimalField(default=0)  # Tax percentage
    tax_amount = DecimalField(default=0)
    
    discount_rate = DecimalField(default=0)  # Discount percentage
    discount_amount = DecimalField(default=0)
```

### Cart Model (for offline mode)

```python
class Cart(Document):
    tenant_id = ObjectIdField(required=True)
    customer_id = ObjectIdField()  # Optional for guest checkout
    staff_id = ObjectIdField(required=True)
    
    items = ListField(EmbeddedDocumentField('CartItem'))
    
    subtotal = DecimalField(default=0)
    tax_amount = DecimalField(default=0)
    discount_amount = DecimalField(default=0)
    total = DecimalField(default=0)
    
    status = StringField(
        choices=['active', 'completed', 'abandoned'],
        default='active'
    )
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'indexes': [
            ('tenant_id', 'status'),
            ('tenant_id', 'created_at')
        ]
    }
```

### Receipt Model

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

### Refund Model

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

### Discount Model

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

---

## 3. Payment Integration with Paystack

### Payment Flow

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

### Paystack Integration

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

### Webhook Handling

```python
@app.post("/webhooks/paystack")
async def handle_paystack_webhook(request: Request):
    # Verify webhook signature
    signature = request.headers.get("x-paystack-signature")
    body = await request.body()
    
    if not verify_signature(body, signature):
        return {"status": "invalid"}
    
    payload = await request.json()
    event = payload.get("event")
    
    if event == "charge.success":
        # Update transaction status to completed
        # Send confirmation email
        # Deduct inventory
        # Calculate commission
    
    elif event == "charge.failed":
        # Update transaction status to failed
        # Send failure notification
    
    return {"status": "ok"}
```

---

## 4. Inventory Deduction Workflow

### Deduction Process

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

### Inventory Service

```python
class InventoryService:
    def deduct_inventory(self, tenant_id, transaction_id, items):
        """Deduct inventory for transaction items"""
        for item in items:
            if item.item_type == 'product':
                # Check availability
                inventory = Inventory.objects(
                    tenant_id=tenant_id,
                    product_id=item.item_id
                ).first()
                
                if not inventory or inventory.quantity_available < item.quantity:
                    raise InsufficientInventoryError()
                
                # Deduct inventory
                inventory.quantity_on_hand -= item.quantity
                inventory.save()
                
                # Create movement record
                InventoryMovement.objects.create(
                    tenant_id=tenant_id,
                    product_id=item.item_id,
                    movement_type='sale',
                    quantity=-item.quantity,
                    reference_id=transaction_id
                )
                
                # Check for low stock
                if inventory.quantity_on_hand <= inventory.reorder_point:
                    self.generate_low_stock_alert(tenant_id, item.item_id)
    
    def restore_inventory(self, tenant_id, transaction_id):
        """Restore inventory when transaction is refunded"""
        # Find all inventory movements for transaction
        # Reverse each movement
        # Update inventory quantities
```

---

## 5. Receipt Generation System

### Receipt Template

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: monospace; width: 80mm; }
        .header { text-align: center; margin-bottom: 10px; }
        .items { margin: 10px 0; }
        .item { display: flex; justify-content: space-between; }
        .total { border-top: 1px solid #000; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>{{ salon_name }}</h2>
        <p>{{ salon_address }}</p>
        <p>{{ salon_phone }}</p>
    </div>
    
    <div class="receipt-info">
        <p>Receipt #: {{ receipt_number }}</p>
        <p>Date: {{ receipt_date }}</p>
        <p>Staff: {{ staff_name }}</p>
    </div>
    
    <div class="customer-info">
        <p>Customer: {{ customer_name }}</p>
        <p>Phone: {{ customer_phone }}</p>
    </div>
    
    <div class="items">
        {% for item in items %}
        <div class="item">
            <span>{{ item.name }} x{{ item.quantity }}</span>
            <span>{{ item.line_total | currency }}</span>
        </div>
        {% endfor %}
    </div>
    
    <div class="totals">
        <div class="item">
            <span>Subtotal:</span>
            <span>{{ subtotal | currency }}</span>
        </div>
        <div class="item">
            <span>Tax:</span>
            <span>{{ tax_amount | currency }}</span>
        </div>
        <div class="item">
            <span>Discount:</span>
            <span>-{{ discount_amount | currency }}</span>
        </div>
        <div class="item total">
            <span>Total:</span>
            <span>{{ total | currency }}</span>
        </div>
    </div>
    
    <div class="payment-info">
        <p>Payment Method: {{ payment_method }}</p>
        <p>Reference: {{ payment_reference }}</p>
    </div>
    
    <div class="qr-code">
        <img src="{{ qr_code_url }}" alt="Receipt QR Code">
    </div>
    
    <div class="footer">
        <p>Thank you for your business!</p>
        <p>{{ salon_website }}</p>
    </div>
</body>
</html>
```

### Receipt Service

```python
class ReceiptService:
    def generate_receipt(self, transaction_id):
        """Generate receipt for transaction"""
        transaction = Transaction.objects.get(id=transaction_id)
        
        # Prepare receipt data
        receipt_data = {
            'receipt_number': self.generate_receipt_number(),
            'receipt_date': datetime.utcnow(),
            'customer_name': transaction.customer.name,
            'customer_phone': transaction.customer.phone,
            'items': transaction.items,
            'subtotal': transaction.subtotal,
            'tax_amount': transaction.tax_amount,
            'discount_amount': transaction.discount_amount,
            'total': transaction.total,
            'payment_method': transaction.payment_method,
            'payment_reference': transaction.paystack_reference,
            'qr_code_url': self.generate_qr_code(transaction_id)
        }
        
        # Render template
        html = self.render_template('receipt.html', receipt_data)
        
        # Generate PDF
        pdf = self.html_to_pdf(html)
        
        # Create receipt record
        receipt = Receipt.objects.create(
            tenant_id=transaction.tenant_id,
            transaction_id=transaction_id,
            **receipt_data
        )
        
        return receipt, pdf
    
    def print_receipt(self, receipt_id, printer_name):
        """Print receipt to printer"""
        receipt = Receipt.objects.get(id=receipt_id)
        pdf = self.generate_receipt_pdf(receipt)
        
        # Send to printer
        self.send_to_printer(pdf, printer_name)
        
        receipt.printed_at = datetime.utcnow()
        receipt.save()
    
    def email_receipt(self, receipt_id, email):
        """Email receipt to customer"""
        receipt = Receipt.objects.get(id=receipt_id)
        pdf = self.generate_receipt_pdf(receipt)
        
        # Send email with PDF attachment
        self.send_email(
            to=email,
            subject=f"Receipt #{receipt.receipt_number}",
            body="Your receipt is attached",
            attachments=[pdf]
        )
        
        receipt.emailed_at = datetime.utcnow()
        receipt.save()
```

---

## 6. Offline Sync Mechanism

### Offline Storage

```javascript
// IndexedDB schema for offline storage
const dbSchema = {
    stores: {
        transactions: {
            keyPath: 'id',
            indexes: [
                { name: 'status', keyPath: 'status' },
                { name: 'created_at', keyPath: 'created_at' }
            ]
        },
        carts: {
            keyPath: 'id',
            indexes: [
                { name: 'status', keyPath: 'status' }
            ]
        },
        inventory: {
            keyPath: 'id',
            indexes: [
                { name: 'product_id', keyPath: 'product_id' }
            ]
        }
    }
};
```

### Sync Process

```javascript
class OfflineSyncManager {
    async syncTransactions() {
        // Get all pending transactions from IndexedDB
        const pendingTransactions = await this.db.transactions
            .where('status').equals('pending')
            .toArray();
        
        for (const transaction of pendingTransactions) {
            try {
                // Send to server
                const response = await fetch('/api/transactions', {
                    method: 'POST',
                    body: JSON.stringify(transaction)
                });
                
                if (response.ok) {
                    // Update status to synced
                    transaction.status = 'synced';
                    await this.db.transactions.put(transaction);
                }
            } catch (error) {
                // Retry on next sync
                console.error('Sync failed:', error);
            }
        }
    }
    
    async handleConflict(localTransaction, serverTransaction) {
        // Compare timestamps
        if (localTransaction.updated_at > serverTransaction.updated_at) {
            // Local is newer, use local version
            return localTransaction;
        } else {
            // Server is newer, use server version
            return serverTransaction;
        }
    }
}
```

---

## 7. Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Transaction Immutability
*For any* completed transaction, the transaction record SHALL NOT be modified; only refunds are allowed for corrections.
**Validates: Requirements 70.4**

### Property 2: Inventory Deduction Accuracy
*For any* transaction with product items, the inventory quantity SHALL be reduced by the exact quantity sold.
**Validates: Requirements 72.1**

### Property 3: Payment Status Consistency
*For any* transaction, the payment status SHALL match the Paystack payment status after webhook processing.
**Validates: Requirements 71.3**

### Property 4: Receipt Generation Completeness
*For any* completed transaction, a receipt SHALL be generated automatically with all transaction details.
**Validates: Requirements 74.1**

### Property 5: Refund Inventory Restoration
*For any* refunded transaction, the inventory quantities SHALL be restored to pre-transaction levels.
**Validates: Requirements 78.3**

### Property 6: Discount Calculation Accuracy
*For any* transaction with applied discount, the discount amount SHALL be calculated correctly based on discount type and value.
**Validates: Requirements 77.1**

### Property 7: Tax Calculation Accuracy
*For any* transaction, the tax amount SHALL be calculated correctly based on the discounted subtotal and applicable tax rate.
**Validates: Requirements 77.5**

### Property 8: Commission Calculation Accuracy
*For any* completed transaction, the staff commission SHALL be calculated correctly based on the commission structure.
**Validates: Requirements 79.2**

### Property 9: Offline Sync Idempotence
*For any* transaction synced multiple times from offline mode, the final state SHALL be identical to syncing once.
**Validates: Requirements 75.3**

### Property 10: Audit Trail Completeness
*For any* transaction modification, an audit log entry SHALL be created with user, timestamp, and old/new values.
**Validates: Requirements 80.1**

---

## 8. Error Handling

### Transaction Errors

- **InsufficientInventoryError**: Raised when product inventory is insufficient
- **PaymentFailedError**: Raised when payment processing fails
- **InvalidDiscountError**: Raised when discount code is invalid or expired
- **DuplicateTransactionError**: Raised when duplicate transaction is detected
- **RefundNotAllowedError**: Raised when refund is not allowed for transaction

### Error Responses

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

---

## 9. Testing Strategy

### Unit Tests

- Transaction creation and validation
- Inventory deduction logic
- Discount calculation
- Tax calculation
- Commission calculation
- Receipt generation
- Refund processing

### Property-Based Tests

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

### Integration Tests

- Complete transaction flow from cart to receipt
- Payment processing with Paystack
- Inventory deduction and restoration
- Offline mode and sync
- Refund processing
- Commission calculation and payout

