"""
Accounting schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AccountType(str, Enum):
    """Account types for chart of accounts"""
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class AccountSubType(str, Enum):
    """Account sub-types"""
    # Assets
    CASH = "cash"
    BANK = "bank"
    ACCOUNTS_RECEIVABLE = "accounts_receivable"
    INVENTORY = "inventory"
    FIXED_ASSETS = "fixed_assets"
    
    # Liabilities
    ACCOUNTS_PAYABLE = "accounts_payable"
    CREDIT_CARD = "credit_card"
    LOANS = "loans"
    
    # Equity
    OWNERS_EQUITY = "owners_equity"
    RETAINED_EARNINGS = "retained_earnings"
    
    # Revenue
    SERVICE_REVENUE = "service_revenue"
    PRODUCT_REVENUE = "product_revenue"
    OTHER_REVENUE = "other_revenue"
    
    # Expenses
    COST_OF_GOODS = "cost_of_goods"
    OPERATING_EXPENSES = "operating_expenses"
    PAYROLL = "payroll"
    RENT = "rent"
    UTILITIES = "utilities"
    MARKETING = "marketing"


class AccountCreate(BaseModel):
    """Account creation request"""
    code: str = Field(..., min_length=1, max_length=20, description="Account code (e.g., 1000)")
    name: str = Field(..., min_length=2, max_length=100)
    account_type: AccountType
    sub_type: AccountSubType
    description: Optional[str] = Field(None, max_length=500)
    parent_account_id: Optional[str] = None


class AccountUpdate(BaseModel):
    """Account update request"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    active: Optional[bool] = None


class AccountResponse(BaseModel):
    """Account response"""
    id: str
    tenant_id: str
    code: str
    name: str
    account_type: AccountType
    sub_type: AccountSubType
    description: Optional[str] = None
    parent_account_id: Optional[str] = None
    balance: float = 0.0
    active: bool = True
    created_at: datetime
    updated_at: datetime


class JournalEntryLineItem(BaseModel):
    """Journal entry line item"""
    account_id: str
    debit: float = Field(0.0, ge=0)
    credit: float = Field(0.0, ge=0)
    description: Optional[str] = None


class JournalEntryCreate(BaseModel):
    """Journal entry creation request"""
    date: str = Field(..., description="Entry date (YYYY-MM-DD)")
    reference: Optional[str] = Field(None, max_length=50)
    description: str = Field(..., min_length=2, max_length=500)
    line_items: List[JournalEntryLineItem] = Field(..., min_items=2)


class JournalEntryResponse(BaseModel):
    """Journal entry response"""
    id: str
    tenant_id: str
    entry_number: int
    date: str
    reference: Optional[str] = None
    description: str
    line_items: List[dict]
    total_debit: float
    total_credit: float
    balanced: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


class FinancialReportType(str, Enum):
    """Financial report types"""
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    TRIAL_BALANCE = "trial_balance"


class FinancialReportRequest(BaseModel):
    """Financial report request"""
    report_type: FinancialReportType
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")


class InvoiceStatus(str, Enum):
    """Invoice status"""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceCreate(BaseModel):
    """Invoice creation request"""
    client_id: str
    invoice_date: str = Field(..., description="Invoice date (YYYY-MM-DD)")
    due_date: str = Field(..., description="Due date (YYYY-MM-DD)")
    line_items: List[dict]
    tax_rate_id: Optional[str] = None
    tax_exempt: bool = False
    notes: Optional[str] = None
    currency_code: Optional[str] = Field("USD", description="Currency code")
    exchange_rate: Optional[float] = Field(1.0, description="Exchange rate to base currency")


class InvoiceUpdate(BaseModel):
    """Invoice update request"""
    client_id: Optional[str] = None
    invoice_date: Optional[str] = Field(None, description="Invoice date (YYYY-MM-DD)")
    due_date: Optional[str] = Field(None, description="Due date (YYYY-MM-DD)")
    line_items: Optional[List[dict]] = None
    tax_rate_id: Optional[str] = None
    tax_exempt: Optional[bool] = None
    notes: Optional[str] = None
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None


class InvoiceResponse(BaseModel):
    """Invoice response"""
    id: str
    tenant_id: str
    invoice_number: str
    client_id: str
    client_name: str
    invoice_date: str
    due_date: str
    line_items: List[dict]
    subtotal: float
    tax_rate_id: Optional[str] = None
    tax_rate_name: Optional[str] = None
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    tax_exempt: bool = False
    total: float
    amount_paid: float
    amount_due: float
    status: InvoiceStatus
    notes: Optional[str] = None
    currency_code: str = "USD"
    exchange_rate: float = 1.0
    base_currency_total: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class PaymentCreate(BaseModel):
    """Payment creation request"""
    invoice_id: str
    amount: float = Field(..., gt=0)
    payment_date: str = Field(..., description="Payment date (YYYY-MM-DD)")
    payment_method: str
    reference: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment response"""
    id: str
    tenant_id: str
    invoice_id: str
    amount: float
    payment_date: str
    payment_method: str
    reference: Optional[str] = None
    created_at: datetime


class TaxRateCreate(BaseModel):
    """Tax rate creation request"""
    name: str = Field(..., min_length=2, max_length=100)
    rate: float = Field(..., ge=0, le=100, description="Tax rate as percentage (0-100)")
    description: Optional[str] = Field(None, max_length=500)
    active: bool = True


class TaxRateUpdate(BaseModel):
    """Tax rate update request"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    rate: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = Field(None, max_length=500)
    active: Optional[bool] = None


class TaxRateResponse(BaseModel):
    """Tax rate response"""
    id: str
    tenant_id: str
    name: str
    rate: float
    description: Optional[str] = None
    active: bool = True
    created_at: datetime
    updated_at: datetime


class TaxReportRequest(BaseModel):
    """Tax report request"""
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    tax_rate_id: Optional[str] = None


class TaxReportResponse(BaseModel):
    """Tax report response"""
    period_start: str
    period_end: str
    tax_rate_name: Optional[str] = None
    total_taxable_amount: float
    total_tax_collected: float
    invoice_count: int
    breakdown: List[dict]


# Vendor Types
class VendorStatus(str, Enum):
    """Vendor status"""
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


class VendorCreate(BaseModel):
    """Vendor creation request"""
    name: str = Field(..., min_length=2, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    tax_id: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)


class VendorUpdate(BaseModel):
    """Vendor update request"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    contact_person: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    tax_id: Optional[str] = Field(None, max_length=50)
    payment_terms: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)
    status: Optional[VendorStatus] = None


class VendorResponse(BaseModel):
    """Vendor response"""
    id: str
    tenant_id: str
    vendor_number: str
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    status: VendorStatus
    total_outstanding: float = 0.0
    created_at: datetime
    updated_at: datetime


# Bill Types
class BillStatus(str, Enum):
    """Bill status"""
    draft = "draft"
    pending = "pending"
    approved = "approved"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"


class BillCreate(BaseModel):
    """Bill creation request"""
    vendor_id: str
    bill_date: str = Field(..., description="Bill date (YYYY-MM-DD)")
    due_date: str = Field(..., description="Due date (YYYY-MM-DD)")
    reference_number: Optional[str] = Field(None, max_length=100)
    line_items: List[dict]
    tax_rate_id: Optional[str] = None
    tax_exempt: bool = False
    notes: Optional[str] = None
    currency_code: Optional[str] = Field("USD", description="Currency code")
    exchange_rate: Optional[float] = Field(1.0, description="Exchange rate to base currency")


class BillUpdate(BaseModel):
    """Bill update request"""
    vendor_id: Optional[str] = None
    bill_date: Optional[str] = Field(None, description="Bill date (YYYY-MM-DD)")
    due_date: Optional[str] = Field(None, description="Due date (YYYY-MM-DD)")
    reference_number: Optional[str] = Field(None, max_length=100)
    line_items: Optional[List[dict]] = None
    tax_rate_id: Optional[str] = None
    tax_exempt: Optional[bool] = None
    notes: Optional[str] = None
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None


class BillResponse(BaseModel):
    """Bill response"""
    id: str
    tenant_id: str
    bill_number: str
    vendor_id: str
    vendor_name: str
    bill_date: str
    due_date: str
    reference_number: Optional[str] = None
    line_items: List[dict]
    subtotal: float
    tax_rate_id: Optional[str] = None
    tax_rate_name: Optional[str] = None
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    tax_exempt: bool = False
    total: float
    amount_paid: float = 0.0
    amount_due: float
    status: BillStatus
    notes: Optional[str] = None
    currency_code: str = "USD"
    exchange_rate: float = 1.0
    base_currency_total: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class BillPaymentCreate(BaseModel):
    """Bill payment creation request"""
    bill_id: str
    amount: float = Field(..., gt=0)
    payment_date: str = Field(..., description="Payment date (YYYY-MM-DD)")
    payment_method: str
    reference: Optional[str] = None


class BillPaymentResponse(BaseModel):
    """Bill payment response"""
    id: str
    tenant_id: str
    bill_id: str
    amount: float
    payment_date: str
    payment_method: str
    reference: Optional[str] = None
    created_at: datetime


# Enhanced Payment Types
class PaymentMethodType(str, Enum):
    """Payment method types"""
    cash = "cash"
    card = "card"
    bank_transfer = "bank_transfer"
    check = "check"
    mobile_money = "mobile_money"
    crypto = "crypto"
    other = "other"


class PaymentStatus(str, Enum):
    """Payment status"""
    pending = "pending"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"
    refunded = "refunded"


class EnhancedPaymentCreate(BaseModel):
    """Enhanced payment creation request"""
    invoice_id: Optional[str] = None
    bill_id: Optional[str] = None
    amount: float = Field(..., gt=0)
    payment_date: str = Field(..., description="Payment date (YYYY-MM-DD)")
    payment_method: PaymentMethodType
    reference_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)
    bank_account: Optional[str] = Field(None, max_length=100)
    check_number: Optional[str] = Field(None, max_length=50)


class EnhancedPaymentResponse(BaseModel):
    """Enhanced payment response"""
    id: str
    tenant_id: str
    invoice_id: Optional[str] = None
    bill_id: Optional[str] = None
    amount: float
    payment_date: str
    payment_method: PaymentMethodType
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    bank_account: Optional[str] = None
    check_number: Optional[str] = None
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime


class RefundCreate(BaseModel):
    """Refund creation request"""
    payment_id: str
    amount: float = Field(..., gt=0)
    reason: str = Field(..., min_length=5, max_length=500)
    refund_date: str = Field(..., description="Refund date (YYYY-MM-DD)")
    refund_method: Optional[PaymentMethodType] = None


class RefundResponse(BaseModel):
    """Refund response"""
    id: str
    tenant_id: str
    payment_id: str
    invoice_id: Optional[str] = None
    bill_id: Optional[str] = None
    amount: float
    reason: str
    refund_date: str
    refund_method: PaymentMethodType
    status: PaymentStatus
    created_at: datetime


# Enhanced Financial Report Types
class ReportFormat(str, Enum):
    """Report export formats"""
    json = "json"
    pdf = "pdf"
    excel = "excel"
    csv = "csv"


class DateRangePreset(str, Enum):
    """Date range presets"""
    today = "today"
    yesterday = "yesterday"
    this_week = "this_week"
    last_week = "last_week"
    this_month = "this_month"
    last_month = "last_month"
    this_quarter = "this_quarter"
    last_quarter = "last_quarter"
    this_year = "this_year"
    last_year = "last_year"
    ytd = "ytd"
    qtd = "qtd"
    custom = "custom"


class CashFlowCategory(str, Enum):
    """Cash flow categories"""
    operating = "operating"
    investing = "investing"
    financing = "financing"


class EnhancedReportRequest(BaseModel):
    """Enhanced financial report request"""
    report_type: str = Field(..., description="Type of report (balance_sheet, income_statement, cash_flow, etc.)")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    date_preset: Optional[DateRangePreset] = None
    comparison_period: Optional[bool] = False
    comparison_start_date: Optional[str] = Field(None, description="Comparison start date (YYYY-MM-DD)")
    comparison_end_date: Optional[str] = Field(None, description="Comparison end date (YYYY-MM-DD)")
    format: ReportFormat = ReportFormat.json
    include_zero_balances: bool = False
    account_ids: Optional[List[str]] = None


class CashFlowRequest(BaseModel):
    """Cash flow statement request"""
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    method: str = Field("indirect", description="Cash flow method (direct or indirect)")
    format: ReportFormat = ReportFormat.json


class ComparisonReportRequest(BaseModel):
    """Period comparison report request"""
    report_type: str = Field(..., description="Type of report to compare")
    current_start_date: str = Field(..., description="Current period start date (YYYY-MM-DD)")
    current_end_date: str = Field(..., description="Current period end date (YYYY-MM-DD)")
    comparison_start_date: str = Field(..., description="Comparison period start date (YYYY-MM-DD)")
    comparison_end_date: str = Field(..., description="Comparison period end date (YYYY-MM-DD)")
    format: ReportFormat = ReportFormat.json


class DrillDownRequest(BaseModel):
    """Report drill-down request"""
    report_type: str
    account_id: str
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    transaction_type: Optional[str] = None


class ReportVisualizationRequest(BaseModel):
    """Report visualization request"""
    report_type: str
    chart_type: str = Field(..., description="Chart type (line, bar, pie, area)")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    group_by: str = Field("month", description="Grouping period (day, week, month, quarter, year)")
    account_ids: Optional[List[str]] = None

# Bank Reconciliation Schemas
class ReconciliationStatus(str, Enum):
    """Reconciliation status options"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReconciliationTransactionCreate(BaseModel):
    """Schema for creating reconciliation transaction"""
    transaction_id: str
    reconciled: bool = False
    cleared_date: Optional[str] = None


class ReconciliationTransactionResponse(BaseModel):
    """Schema for reconciliation transaction response"""
    id: str
    date: str
    description: str
    reference: Optional[str] = None
    amount: float
    type: str
    reconciled: bool = False
    cleared_date: Optional[str] = None
    journal_entry_id: str
    line_item_id: str


class ReconciliationAdjustmentCreate(BaseModel):
    """Schema for creating reconciliation adjustment"""
    description: str
    amount: float
    account_id: Optional[str] = None
    reference: Optional[str] = None


class ReconciliationAdjustmentResponse(BaseModel):
    """Schema for reconciliation adjustment response"""
    id: str
    reconciliation_id: str
    description: str
    amount: float
    account_id: Optional[str] = None
    reference: Optional[str] = None
    created_at: datetime


class ReconciliationCreate(BaseModel):
    """Schema for creating bank reconciliation"""
    account_id: str
    reconciliation_date: str
    statement_date: str
    statement_balance: float
    created_by: Optional[str] = None


class ReconciliationUpdate(BaseModel):
    """Schema for updating bank reconciliation"""
    matched_transactions: Optional[List[ReconciliationTransactionCreate]] = None
    adjustments: Optional[List[ReconciliationAdjustmentCreate]] = None
    notes: Optional[str] = None


class ReconciliationResponse(BaseModel):
    """Schema for bank reconciliation response"""
    id: str
    tenant_id: str
    account_id: str
    account_name: str
    reconciliation_date: str
    statement_date: str
    beginning_balance: float
    ending_balance: float
    statement_balance: float
    reconciled_balance: float
    difference: float
    status: ReconciliationStatus
    created_by: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    transaction_count: int = 0
    matched_count: int = 0
    unmatched_count: int = 0
    transactions: Optional[List[ReconciliationTransactionResponse]] = None
    adjustments: Optional[List[ReconciliationAdjustmentResponse]] = None
    notes: Optional[str] = None


class ReconciliationSummaryResponse(BaseModel):
    """Schema for reconciliation summary"""
    account_id: str
    last_reconciled_date: Optional[str] = None
    last_reconciled_balance: float = 0.0
    current_book_balance: float = 0.0
    unreconciled_transactions: int = 0
    unreconciled_amount: float = 0.0
    days_since_last_reconciliation: Optional[int] = None
    reconciliation_frequency: str = "monthly"


# Budget and Forecasting Schemas
class BudgetPeriod(str, Enum):
    """Budget period options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class BudgetStatus(str, Enum):
    """Budget status options"""
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class BudgetLineItemCreate(BaseModel):
    """Schema for creating budget line item"""
    account_id: str
    period_start: str
    period_end: str
    budgeted_amount: float
    notes: Optional[str] = None


class BudgetLineItemUpdate(BaseModel):
    """Schema for updating budget line item"""
    budgeted_amount: Optional[float] = None
    notes: Optional[str] = None


class BudgetLineItemResponse(BaseModel):
    """Schema for budget line item response"""
    id: str
    account_id: str
    account_code: str
    account_name: str
    period_start: str
    period_end: str
    budgeted_amount: float
    actual_amount: float = 0.0
    variance_amount: float = 0.0
    variance_percent: float = 0.0
    notes: Optional[str] = None


class BudgetCreate(BaseModel):
    """Schema for creating budget"""
    name: str
    description: Optional[str] = None
    budget_year: int
    budget_period: BudgetPeriod
    status: BudgetStatus = BudgetStatus.DRAFT
    line_items: List[BudgetLineItemCreate] = []


class BudgetUpdate(BaseModel):
    """Schema for updating budget"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[BudgetStatus] = None
    line_items: Optional[List[BudgetLineItemCreate]] = None


class BudgetResponse(BaseModel):
    """Schema for budget response"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    budget_year: int
    budget_period: BudgetPeriod
    status: BudgetStatus
    total_budgeted: float = 0.0
    total_actual: float = 0.0
    total_variance: float = 0.0
    variance_percent: float = 0.0
    created_by: str
    created_at: datetime
    updated_at: datetime
    line_items: List[BudgetLineItemResponse] = []


class BudgetVarian

# Bank Reconciliation Schemas
class ReconciliationStatus(str, Enum):
    """Reconciliation status options"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReconciliationCreate(BaseModel):
    """Schema for creating a new reconciliation"""
    account_id: str = Field(..., description="ID of the bank account to reconcile")
    reconciliation_date: str = Field(..., description="Date of reconciliation (YYYY-MM-DD)")
    statement_date: str = Field(..., description="Bank statement date (YYYY-MM-DD)")
    statement_balance: float = Field(..., description="Ending balance on bank statement")
    created_by: Optional[str] = Field(None, description="User who created the reconciliation")


class ReconciliationUpdate(BaseModel):
    """Schema for updating a reconciliation"""
    matched_transactions: Optional[List[dict]] = Field(None, description="List of matched transaction IDs")
    adjustments: Optional[List[dict]] = Field(None, description="List of adjustment entries")


class ReconciliationAdjustmentCreate(BaseModel):
    """Schema for creating reconciliation adjustments"""
    description: str = Field(..., description="Description of the adjustment")
    amount: float = Field(..., description="Adjustment amount (positive or negative)")
    account_id: Optional[str] = Field(None, description="Account to offset the adjustment")
    reference: Optional[str] = Field(None, description="Reference number or note")


class ReconciliationTransactionResponse(BaseModel):
    """Schema for reconciliation transaction response"""
    id: str
    date: str
    description: str
    reference: Optional[str]
    amount: float
    type: str  # "debit" or "credit"
    reconciled: bool
    journal_entry_id: str
    line_item_id: str


class ReconciliationResponse(BaseModel):
    """Schema for reconciliation response"""
    id: str
    tenant_id: str
    account_id: str
    account_name: str
    reconciliation_date: str
    statement_date: str
    beginning_balance: float
    ending_balance: float
    statement_balance: float
    reconciled_balance: float
    difference: float
    status: ReconciliationStatus
    created_by: str
    created_at: datetime
    completed_at: Optional[datetime]
    transaction_count: int
    matched_count: int
    unmatched_count: int
    transactions: Optional[List[ReconciliationTransactionResponse]] = None
    adjustments: Optional[List[dict]] = None


class ReconciliationSummaryResponse(BaseModel):
    """Schema for reconciliation summary response"""
    account_id: str
    last_reconciled_date: Optional[str]
    last_reconciled_balance: float
    current_book_balance: float
    unreconciled_transactions: int
    unreconciled_amount: float
    days_since_last_reconciliation: Optional[int]
    reconciliation_frequency: str


# Budget and Forecasting Schemas
class BudgetPeriod(str, Enum):
    """Budget period options"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class BudgetStatus(str, Enum):
    """Budget status options"""
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class BudgetLineItemCreate(BaseModel):
    """Schema for creating budget line items"""
    account_id: str = Field(..., description="Account ID")
    account_code: Optional[str] = Field(None, description="Account code")
    account_name: Optional[str] = Field(None, description="Account name")
    budgeted_amount: float = Field(..., description="Budgeted amount for the period")
    notes: Optional[str] = Field(None, description="Notes about this budget line")


class BudgetLineItemResponse(BaseModel):
    """Schema for budget line item response"""
    id: str
    account_id: str
    account_code: str
    account_name: str
    budgeted_amount: float
    actual_amount: float
    variance_amount: float
    variance_percentage: float
    notes: Optional[str]


class BudgetCreate(BaseModel):
    """Schema for creating a new budget"""
    name: str = Field(..., description="Budget name")
    description: Optional[str] = Field(None, description="Budget description")
    budget_year: int = Field(..., description="Budget year (e.g., 2024)")
    period_type: BudgetPeriod = Field(..., description="Budget period type")
    start_date: str = Field(..., description="Budget start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Budget end date (YYYY-MM-DD)")
    line_items: List[BudgetLineItemCreate] = Field(..., description="Budget line items")


class BudgetUpdate(BaseModel):
    """Schema for updating a budget"""
    name: Optional[str] = Field(None, description="Budget name")
    description: Optional[str] = Field(None, description="Budget description")
    status: Optional[BudgetStatus] = Field(None, description="Budget status")
    line_items: Optional[List[BudgetLineItemCreate]] = Field(None, description="Budget line items")


class BudgetResponse(BaseModel):
    """Schema for budget response"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    budget_year: int
    period_type: BudgetPeriod
    start_date: str
    end_date: str
    status: BudgetStatus
    total_budgeted: float
    total_actual: float
    total_variance: float
    variance_percentage: float
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]
    line_items: List[BudgetLineItemResponse]


class BudgetVarianceResponse(BaseModel):
    """Schema for budget variance analysis"""
    budget_id: str
    budget_name: str
    period_start: str
    period_end: str
    total_budgeted: float
    total_actual: float
    total_variance: float
    variance_percentage: float
    line_items: List[BudgetLineItemResponse]
    over_budget_accounts: List[BudgetLineItemResponse]
    under_budget_accounts: List[BudgetLineItemResponse]


class ForecastCreate(BaseModel):
    """Schema for creating forecasts"""
    account_id: str = Field(..., description="Account ID to forecast")
    forecast_periods: int = Field(..., description="Number of periods to forecast")
    forecast_method: str = Field(default="trend", description="Forecasting method")
    manual_adjustments: Optional[List[dict]] = Field(None, description="Manual forecast adjustments")


class ForecastResponse(BaseModel):
    """Schema for forecast response"""
    account_id: str
    account_name: str
    forecast_method: str
    historical_data: List[dict]
    forecast_data: List[dict]
    confidence_level: float
    generated_at: datetime


class BudgetCopyRequest(BaseModel):
    """Schema for copying budgets"""
    source_budget_id: str = Field(..., description="ID of budget to copy from")
    new_budget_name: str = Field(..., description="Name for the new budget")
    new_budget_year: int = Field(..., description="Year for the new budget")
    adjustment_percentage: Optional[float] = Field(0.0, description="Percentage adjustment to apply")
    start_date: str = Field(..., description="Start date for new budget")
    end_date: str = Field(..., description="End date for new budget")


# Multi-Currency Support Schemas
class CurrencyCreate(BaseModel):
    """Schema for creating a new currency"""
    code: str = Field(..., min_length=3, max_length=3, description="Currency code (e.g., USD, EUR)")
    name: str = Field(..., min_length=2, max_length=100, description="Currency name")
    symbol: Optional[str] = Field(None, max_length=10, description="Currency symbol")
    decimal_places: Optional[int] = Field(2, ge=0, le=6, description="Number of decimal places")
    is_base_currency: Optional[bool] = Field(False, description="Whether this is the base currency")
    active: Optional[bool] = Field(True, description="Whether the currency is active")


class CurrencyUpdate(BaseModel):
    """Schema for updating a currency"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    symbol: Optional[str] = Field(None, max_length=10)
    decimal_places: Optional[int] = Field(None, ge=0, le=6)
    is_base_currency: Optional[bool] = None
    active: Optional[bool] = None


class CurrencyResponse(BaseModel):
    """Schema for currency response"""
    id: str
    tenant_id: str
    code: str
    name: str
    symbol: str
    decimal_places: int
    is_base_currency: bool
    active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


class ExchangeRateCreate(BaseModel):
    """Schema for creating exchange rates"""
    from_currency: str = Field(..., min_length=3, max_length=3, description="Source currency code")
    to_currency: str = Field(..., min_length=3, max_length=3, description="Target currency code")
    rate: float = Field(..., gt=0, description="Exchange rate")
    rate_date: str = Field(..., description="Rate date (YYYY-MM-DD)")
    source: Optional[str] = Field("manual", description="Rate source (manual, api, etc.)")


class ExchangeRateResponse(BaseModel):
    """Schema for exchange rate response"""
    id: str
    tenant_id: str
    from_currency: str
    to_currency: str
    rate: float
    rate_date: str
    source: str
    created_by: str
    created_at: datetime
    updated_at: datetime


class CurrencyConversionRequest(BaseModel):
    """Schema for currency conversion request"""
    amount: float = Field(..., gt=0, description="Amount to convert")
    from_currency: str = Field(..., min_length=3, max_length=3, description="Source currency")
    to_currency: str = Field(..., min_length=3, max_length=3, description="Target currency")
    rate_date: Optional[str] = Field(None, description="Rate date (YYYY-MM-DD)")


class CurrencyConversionResponse(BaseModel):
    """Schema for currency conversion response"""
    original_amount: float
    converted_amount: float
    exchange_rate: float
    from_currency: str
    to_currency: str
    rate_date: str


class ExchangeGainLossResponse(BaseModel):
    """Schema for exchange gain/loss response"""
    original_amount: float
    original_currency: str
    original_rate: float
    current_rate: float
    base_currency: str
    original_base_amount: float
    current_base_amount: float
    gain_loss_amount: float
    is_gain: bool


class CurrencySummaryResponse(BaseModel):
    """Schema for currency configuration summary"""
    total_currencies: int
    active_currencies: int
    base_currency: CurrencyResponse
    recent_exchange_rates: List[ExchangeRateResponse]
    multi_currency_enabled: bool


# Fixed Assets Management Schemas
class DepreciationMethod(str, Enum):
    """Depreciation method options"""
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    DOUBLE_DECLINING_BALANCE = "double_declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"


class AssetStatus(str, Enum):
    """Asset status options"""
    ACTIVE = "active"
    DISPOSED = "disposed"
    FULLY_DEPRECIATED = "fully_depreciated"
    INACTIVE = "inactive"


class FixedAssetCreate(BaseModel):
    """Schema for creating fixed assets"""
    name: str = Field(..., min_length=2, max_length=200, description="Asset name")
    description: Optional[str] = Field(None, max_length=500, description="Asset description")
    category: str = Field(..., max_length=100, description="Asset category")
    purchase_date: str = Field(..., description="Purchase date (YYYY-MM-DD)")
    purchase_price: float = Field(..., gt=0, description="Purchase price")
    salvage_value: Optional[float] = Field(0.0, ge=0, description="Salvage value")
    useful_life_years: int = Field(..., gt=0, description="Useful life in years")
    useful_life_units: Optional[int] = Field(None, gt=0, description="Useful life in units (for units of production)")
    depreciation_method: DepreciationMethod = Field(..., description="Depreciation method")
    location: Optional[str] = Field(None, max_length=200, description="Asset location")
    serial_number: Optional[str] = Field(None, max_length=100, description="Serial number")
    vendor_id: Optional[str] = Field(None, description="Vendor ID")
    currency_code: Optional[str] = Field("USD", description="Currency code")


class FixedAssetUpdate(BaseModel):
    """Schema for updating fixed assets"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    serial_number: Optional[str] = Field(None, max_length=100)
    status: Optional[AssetStatus] = None


class DepreciationEntryResponse(BaseModel):
    """Schema for depreciation entry response"""
    id: str
    asset_id: str
    depreciation_date: str
    depreciation_amount: float
    accumulated_depreciation: float
    book_value: float
    journal_entry_id: Optional[str]
    created_at: datetime


class FixedAssetResponse(BaseModel):
    """Schema for fixed asset response"""
    id: str
    tenant_id: str
    asset_number: str
    name: str
    description: Optional[str]
    category: str
    purchase_date: str
    purchase_price: float
    salvage_value: float
    useful_life_years: int
    useful_life_units: Optional[int]
    depreciation_method: DepreciationMethod
    location: Optional[str]
    serial_number: Optional[str]
    vendor_id: Optional[str]
    currency_code: str
    status: AssetStatus
    accumulated_depreciation: float
    book_value: float
    monthly_depreciation: float
    created_by: str
    created_at: datetime
    updated_at: datetime
    depreciation_entries: Optional[List[DepreciationEntryResponse]] = None


class AssetDisposalCreate(BaseModel):
    """Schema for asset disposal"""
    disposal_date: str = Field(..., description="Disposal date (YYYY-MM-DD)")
    disposal_price: float = Field(..., ge=0, description="Disposal price")
    disposal_method: str = Field(..., description="Disposal method (sale, scrap, trade, etc.)")
    notes: Optional[str] = Field(None, max_length=500, description="Disposal notes")


class AssetDisposalResponse(BaseModel):
    """Schema for asset disposal response"""
    id: str
    asset_id: str
    disposal_date: str
    disposal_price: float
    disposal_method: str
    book_value_at_disposal: float
    gain_loss_amount: float
    is_gain: bool
    notes: Optional[str]
    journal_entry_id: Optional[str]
    created_at: datetime


class DepreciationScheduleResponse(BaseModel):
    """Schema for depreciation schedule response"""
    asset_id: str
    asset_name: str
    schedule: List[Dict[str, Any]]
    total_depreciation: float
    remaining_book_value: float


class DepreciationPostingRequest(BaseModel):
    """Schema for depreciation posting request"""
    asset_ids: Optional[List[str]] = Field(None, description="Specific asset IDs to depreciate")
    depreciation_date: str = Field(..., description="Depreciation date (YYYY-MM-DD)")
    period_type: str = Field("monthly", description="Period type (monthly, quarterly, yearly)")


class DepreciationPostingResponse(BaseModel):
    """Schema for depreciation posting response"""
    posted_count: int
    total_depreciation_amount: float
    journal_entry_ids: List[str]
    failed_assets: List[Dict[str, str]]
    posting_date: str



# Audit Trail and Compliance Schemas
class AuditLogAction(str, Enum):
    """Audit log action types"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"
    APPROVE = "approve"
    REJECT = "reject"
    POST = "post"
    REVERSE = "reverse"


class AuditLogCreate(BaseModel):
    """Schema for creating audit logs"""
    entity_type: str = Field(..., description="Type of entity (account, invoice, bill, etc.)")
    entity_id: str = Field(..., description="ID of the entity")
    action: AuditLogAction = Field(..., description="Action performed")
    old_values: Optional[Dict[str, Any]] = Field(None, description="Previous values")
    new_values: Optional[Dict[str, Any]] = Field(None, description="New values")
    user_id: str = Field(..., description="User who performed the action")
    ip_address: Optional[str] = Field(None, description="IP address of the user")
    description: Optional[str] = Field(None, description="Description of the change")


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: str
    tenant_id: str
    entity_type: str
    entity_id: str
    action: AuditLogAction
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    user_id: str
    ip_address: Optional[str]
    description: Optional[str]
    timestamp: datetime
    created_at: datetime


class AccessLogCreate(BaseModel):
    """Schema for creating access logs"""
    entity_type: str = Field(..., description="Type of entity accessed")
    entity_id: str = Field(..., description="ID of the entity")
    user_id: str = Field(..., description="User who accessed the data")
    access_type: str = Field(..., description="Type of access (read, export, etc.)")
    ip_address: Optional[str] = Field(None, description="IP address of the user")
    description: Optional[str] = Field(None, description="Description of the access")


class AccessLogResponse(BaseModel):
    """Schema for access log response"""
    id: str
    tenant_id: str
    entity_type: str
    entity_id: str
    user_id: str
    access_type: str
    ip_address: Optional[str]
    description: Optional[str]
    timestamp: datetime
    created_at: datetime


class AuditTrailFilterRequest(BaseModel):
    """Schema for filtering audit logs"""
    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    entity_id: Optional[str] = Field(None, description="Filter by entity ID")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    action: Optional[AuditLogAction] = Field(None, description="Filter by action")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    limit: int = Field(100, ge=1, le=1000, description="Number of records to return")
    offset: int = Field(0, ge=0, description="Number of records to skip")


class UserActivityResponse(BaseModel):
    """Schema for user activity summary"""
    user_id: str
    period_days: int
    total_changes: int
    total_accesses: int
    action_breakdown: Dict[str, int]
    entity_breakdown: Dict[str, int]
    recent_changes: List[Dict[str, Any]]


class ComplianceReportResponse(BaseModel):
    """Schema for compliance report"""
    period_start: str
    period_end: str
    total_changes: int
    total_accesses: int
    entity_changes: Dict[str, Dict[str, Any]]
    access_by_user: Dict[str, int]
    sensitive_data_accesses: int
    unique_users: int
    generated_at: str


class AuditSummaryResponse(BaseModel):
    """Schema for audit trail summary"""
    total_audit_logs: int
    total_access_logs: int
    recent_changes: List[Dict[str, Any]]
    active_users: List[Dict[str, Any]]


# Period Close and Year-End Schemas
class PeriodCloseStatus(str, Enum):
    """Period close status options"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    YEAR_END_CLOSED = "year_end_closed"
    REOPENED = "reopened"


class PeriodCloseCreate(BaseModel):
    """Schema for creating period close"""
    period_start: str = Field(..., description="Period start date (YYYY-MM-DD)")
    period_end: str = Field(..., description="Period end date (YYYY-MM-DD)")
    period_type: str = Field(..., description="Period type (monthly, quarterly, yearly)")
    description: Optional[str] = Field(None, description="Description of the period")
    created_by: Optional[str] = Field(None, description="User creating the period close")


class PeriodCloseUpdate(BaseModel):
    """Schema for updating period close"""
    status: Optional[PeriodCloseStatus] = Field(None, description="New status")
    notes: Optional[str] = Field(None, description="Notes about the period close")


class PeriodCloseResponse(BaseModel):
    """Schema for period close response"""
    id: str
    tenant_id: str
    period_start: str
    period_end: str
    period_type: str
    description: Optional[str]
    status: PeriodCloseStatus
    locked: bool
    notes: Optional[str]
    created_by: str
    created_at: datetime
    closed_at: Optional[datetime]
    reopened_at: Optional[datetime]
    reopened_by: Optional[str]


class YearEndCloseRequest(BaseModel):
    """Schema for year-end close request"""
    fiscal_year: int = Field(..., description="Fiscal year to close")
    close_date: str = Field(..., description="Close date (YYYY-MM-DD)")
    retained_earnings_account_id: str = Field(..., description="Retained earnings account ID")
    create_closing_entries: bool = Field(True, description="Whether to create closing entries")
    notes: Optional[str] = Field(None, description="Notes about the year-end close")


class YearEndCloseResponse(BaseModel):
    """Schema for year-end close response"""
    id: str
    tenant_id: str
    fiscal_year: int
    close_date: str
    status: PeriodCloseStatus
    net_income: float
    closing_entries_created: int
    journal_entry_ids: List[str]
    created_by: str
    created_at: datetime
    completed_at: Optional[datetime]


class PeriodLockResponse(BaseModel):
    """Schema for period lock status"""
    period_id: str
    period_start: str
    period_end: str
    is_locked: bool
    locked_by: Optional[str]
    locked_at: Optional[datetime]
    can_reopen: bool
    reopen_reason: Optional[str]


class ClosingEntryResponse(BaseModel):
    """Schema for closing entry response"""
    id: str
    journal_entry_id: str
    account_id: str
    account_name: str
    account_type: str
    debit: float
    credit: float
    closing_type: str  # "revenue", "expense", "income_summary", "retained_earnings"
    fiscal_year: int
    created_at: datetime


class YearEndReportResponse(BaseModel):
    """Schema for year-end report"""
    fiscal_year: int
    close_date: str
    net_income: float
    retained_earnings_beginning: float
    retained_earnings_ending: float
    closing_entries: List[ClosingEntryResponse]
    final_balance_sheet: Dict[str, Any]
    final_income_statement: Dict[str, Any]
    generated_at: datetime



# POS Integration Schemas
class POSTransactionCreate(BaseModel):
    """Schema for creating POS transaction"""
    pos_transaction_id: str = Field(..., description="POS transaction ID")
    transaction_date: str = Field(..., description="Transaction date (YYYY-MM-DD)")
    transaction_type: str = Field(..., description="Transaction type (sale, refund, etc.)")
    amount: float = Field(..., gt=0, description="Transaction amount")
    items: List[Dict[str, Any]] = Field(..., description="Line items")
    payment_method: str = Field(..., description="Payment method")
    reference: Optional[str] = Field(None, description="Reference number")
    notes: Optional[str] = Field(None, description="Notes")


class POSTransactionResponse(BaseModel):
    """Schema for POS transaction response"""
    id: str
    tenant_id: str
    pos_transaction_id: str
    transaction_date: str
    transaction_type: str
    amount: float
    items: List[Dict[str, Any]]
    payment_method: str
    reference: Optional[str]
    notes: Optional[str]
    journal_entry_id: Optional[str]
    cogs_journal_entry_id: Optional[str]
    cogs_amount: Optional[float]
    status: str
    created_by: str
    created_at: datetime
    synced_at: Optional[datetime]


class POSReconciliationResponse(BaseModel):
    """Schema for POS reconciliation response"""
    period_start: str
    period_end: str
    pos_total: float
    pos_transaction_count: int
    accounting_total: float
    variance: float
    variance_percent: float
    reconciled: bool
    transactions: List[Dict[str, Any]]


class POSSyncStatusResponse(BaseModel):
    """Schema for POS sync status response"""
    total_synced: int
    total_failed: int
    last_sync_time: Optional[str]
    recent_logs: List[Dict[str, Any]]


# Expense Integration Schemas
class ExpenseMappingCreate(BaseModel):
    """Schema for creating expense mapping"""
    category: str = Field(..., description="Expense category")
    account_id: str = Field(..., description="GL account ID")
    description: Optional[str] = Field(None, description="Description")


class ExpenseMappingUpdate(BaseModel):
    """Schema for updating expense mapping"""
    account_id: Optional[str] = Field(None, description="GL account ID")
    description: Optional[str] = Field(None, description="Description")
    active: Optional[bool] = Field(None, description="Active status")


class ExpenseMappingResponse(BaseModel):
    """Schema for expense mapping response"""
    id: str
    tenant_id: str
    category: str
    account_id: str
    account_name: str
    account_code: str
    description: Optional[str]
    active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


class ExpenseCreate(BaseModel):
    """Schema for creating expense"""
    expense_id: str = Field(..., description="Expense ID")
    category: str = Field(..., description="Expense category")
    amount: float = Field(..., gt=0, description="Expense amount")
    expense_date: str = Field(..., description="Expense date (YYYY-MM-DD)")
    description: str = Field(..., description="Description")
    approval_status: Optional[str] = Field("pending", description="Approval status")


class ExpenseApprovalRequest(BaseModel):
    """Schema for expense approval request"""
    expense_id: str = Field(..., description="Expense ID")


class ExpenseRejectionRequest(BaseModel):
    """Schema for expense rejection request"""
    expense_id: str = Field(..., description="Expense ID")
    reason: str = Field(..., description="Rejection reason")


class ExpenseResponse(BaseModel):
    """Schema for expense response"""
    id: str
    tenant_id: str
    expense_id: str
    category: str
    amount: float
    expense_date: str
    description: str
    approval_status: str
    mapping_id: str
    account_id: str
    journal_entry_id: Optional[str]
    synced: bool
    created_by: str
    created_at: datetime
    synced_at: Optional[datetime]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    rejected_by: Optional[str]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]


class ExpenseReconciliationResponse(BaseModel):
    """Schema for expense reconciliation response"""
    period_start: str
    period_end: str
    approved_expenses: Dict[str, Any]
    pending_expenses: Dict[str, Any]
    rejected_expenses: Dict[str, Any]
    total_expenses: float


# Payroll Integration Schemas
class PayrollCreate(BaseModel):
    """Schema for creating payroll"""
    payroll_period: str = Field(..., description="Payroll period (e.g., 2024-01)")
    payroll_date: str = Field(..., description="Payroll date (YYYY-MM-DD)")
    employees: List[Dict[str, Any]] = Field(..., description="Employee payroll data")


class PayrollResponse(BaseModel):
    """Schema for payroll response"""
    id: str
    tenant_id: str
    payroll_period: str
    payroll_date: str
    employees: List[Dict[str, Any]]
    total_gross: float
    total_net: float
    total_taxes: float
    wage_journal_entry_id: str
    tax_journal_entry_id: str
    payment_journal_entry_id: Optional[str]
    synced: bool
    payment_posted: bool
    created_by: str
    created_at: datetime
    synced_at: Optional[datetime]


class PayrollExpenseReportResponse(BaseModel):
    """Schema for payroll expense report"""
    period_start: str
    period_end: str
    total_gross: float
    total_net: float
    total_taxes: float
    payroll_count: int
    employee_count: int
    employee_summary: List[Dict[str, Any]]


class TaxWithholdingReportResponse(BaseModel):
    """Schema for tax withholding report"""
    period_start: str
    period_end: str
    total_taxes: float
    tax_breakdown: Dict[str, float]
    payroll_count: int


# Accounting Dashboard Schemas
class DashboardKPIResponse(BaseModel):
    """Schema for dashboard KPIs"""
    cash_balance: float
    accounts_receivable: float
    accounts_payable: float
    current_revenue: float
    current_expenses: float
    current_profit: float
    profit_margin: float
    overdue_invoices_count: int
    overdue_invoices_amount: float
    overdue_bills_count: int
    overdue_bills_amount: float
    working_capital: float


class DashboardTrendResponse(BaseModel):
    """Schema for dashboard trends"""
    trends: List[Dict[str, Any]]


class FinancialRatiosResponse(BaseModel):
    """Schema for financial ratios"""
    current_ratio: float
    debt_to_equity: float
    return_on_assets: float
    total_assets: float
    total_liabilities: float
    total_equity: float


class DashboardAlertResponse(BaseModel):
    """Schema for dashboard alert"""
    type: str
    title: str
    message: str
    severity: str


class DashboardAlertsResponse(BaseModel):
    """Schema for dashboard alerts"""
    alerts: List[DashboardAlertResponse]
