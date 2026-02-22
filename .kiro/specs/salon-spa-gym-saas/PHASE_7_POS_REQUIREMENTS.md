# Phase 7 - Point of Sale (POS) System Requirements

## Overview

Phase 7 introduces a comprehensive Point of Sale (POS) system enabling salons, spas, and gyms to process transactions, manage payments, track inventory, and generate receipts. The POS system integrates with existing appointment, invoice, and inventory systems to provide a unified transaction management experience.

---

## Requirement 70: POS Transaction Recording and Processing

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

## Requirement 71: Payment Processing Integration with Paystack

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

## Requirement 72: Inventory Deduction on Transaction

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

## Requirement 73: POS Reporting and Analytics

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

## Requirement 74: Receipt Generation and Printing

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

## Requirement 75: Offline Mode for POS

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

## Requirement 76: Quick Checkout and Split Payments

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

## Requirement 77: Discounts, Taxes, and Promotions

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

## Requirement 78: Refund Processing

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

## Requirement 79: Staff Tracking and Commission

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

## Requirement 80: Audit Trail and Compliance

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

