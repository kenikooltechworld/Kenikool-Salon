"""
Payment schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema


class PaymentInitRequest(BaseModel):
    """Payment initialization request"""
    booking_id: str = Field(..., description="Booking ID")
    email: EmailStr = Field(..., description="Customer email")
    amount: float = Field(..., gt=0, description="Payment amount")
    gateway: str = Field(..., description="Payment gateway: paystack or flutterwave")


class PaymentInitResponse(BaseModel):
    """Payment initialization response"""
    payment_id: str
    authorization_url: str
    reference: str


class DepositPaymentRequest(BaseModel):
    """Deposit payment request"""
    booking_id: str = Field(..., description="Booking ID")
    email: EmailStr = Field(..., description="Customer email")
    amount: float = Field(..., gt=0, description="Deposit amount")
    gateway: str = Field(..., description="Payment gateway: paystack or flutterwave")


class PaymentMethodInput(BaseModel):
    """Payment method input"""
    method: str = Field(..., description="cash, card, transfer, or gift_card")
    amount: float = Field(..., gt=0)
    reference: Optional[str] = None
    gift_card_code: Optional[str] = None


class CheckoutRequest(BaseModel):
    """Checkout request for split payments"""
    booking_id: str = Field(..., description="Booking ID")
    payment_methods: List[PaymentMethodInput] = Field(..., description="List of payment methods")


class PaymentResponse(BaseSchema):
    """Payment response"""
    id: str
    tenant_id: str
    booking_id: str
    amount: float
    gateway: str
    reference: str
    status: str
    payment_type: str  # full, deposit, checkout
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    verified_at: Optional[datetime] = None
    
    # Refund fields
    refund_amount: Optional[float] = None
    refund_reason: Optional[str] = None
    refunded_at: Optional[datetime] = None
    refund_type: Optional[str] = None  # full, partial
    refunded_by: Optional[str] = None  # user_id who processed refund
    
    # Receipt fields
    receipt_generated_at: Optional[datetime] = None
    receipt_url: Optional[str] = None
    receipt_emailed_at: Optional[datetime] = None
    
    # Manual payment fields
    recorded_by: Optional[str] = None  # for manual payments
    is_manual: bool = False
    
    # Gateway sync fields
    gateway_sync_status: str = "synced"  # synced, pending, failed
    last_synced_at: Optional[datetime] = None


class PaymentDetailResponse(PaymentResponse):
    """Extended payment response with related data"""
    booking_data: Optional[dict] = None
    client_data: Optional[dict] = None
    refund_history: Optional[List[dict]] = None


class RefundRequest(BaseModel):
    """Refund request"""
    payment_id: str = Field(..., description="Payment ID to refund")
    refund_amount: float = Field(..., gt=0, description="Amount to refund")
    reason: str = Field(..., min_length=10, description="Reason for refund")
    refund_type: str = Field(..., description="full or partial")


class RefundResponse(BaseModel):
    """Refund response"""
    refund_id: str
    payment_id: str
    refund_amount: float
    refund_type: str
    status: str
    processed_at: datetime
    message: str


class ManualPaymentRequest(BaseModel):
    """Manual payment recording request"""
    booking_id: str = Field(..., description="Booking ID")
    amount: float = Field(..., gt=0, description="Payment amount")
    payment_method: str = Field(..., description="cash, bank_transfer, check, or other")
    reference: Optional[str] = Field(None, description="Optional reference number")
    notes: Optional[str] = Field(None, description="Optional notes")


class PaymentRefund(BaseModel):
    """Payment refund record"""
    id: str
    tenant_id: str
    payment_id: str
    refund_amount: float
    refund_type: str  # full, partial
    reason: str
    status: str  # pending, completed, failed
    gateway_refund_id: Optional[str] = None
    processed_by: str  # user_id
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class PaymentReceipt(BaseModel):
    """Payment receipt record"""
    id: str
    tenant_id: str
    payment_id: str
    receipt_number: str
    receipt_url: str
    generated_at: datetime
    generated_by: str  # user_id
    emailed_to: Optional[str] = None
    emailed_at: Optional[datetime] = None


class EmailReceiptRequest(BaseModel):
    """Email receipt request"""
    email: Optional[EmailStr] = Field(None, description="Email address (uses payment metadata if not provided)")


class PaymentAnalyticsResponse(BaseModel):
    """Payment analytics data"""
    date_range: dict
    
    # Revenue metrics
    total_revenue: float
    total_transactions: int
    average_payment: float
    
    # Trends
    revenue_trends: List[dict]  # [{date, amount, count}]
    
    # Breakdowns
    payment_method_breakdown: List[dict]  # [{method, amount, count, percentage}]
    gateway_breakdown: List[dict]  # [{gateway, amount, count, success_rate}]
    payment_type_breakdown: List[dict]  # [{type, amount, count}]
    
    # Status analysis
    status_breakdown: dict  # {completed: 100, pending: 5, failed: 2}
    
    # Refund metrics
    total_refunded: float
    refund_count: int
    refund_rate: float  # percentage
    
    # Failed payments
    failed_payment_count: int
    failed_payment_amount: float
    common_failure_reasons: List[dict]


class ReconciliationResponse(BaseModel):
    """Payment reconciliation data"""
    unmatched_payments: List[dict]
    mismatched_amounts: List[dict]
    duplicate_payments: List[dict]
    sync_pending: List[dict]
    total_unmatched: int
    total_mismatched: int
    total_duplicates: int


class PaymentFilter(BaseModel):
    """Payment filter parameters"""
    booking_id: Optional[str] = None
    status: Optional[str] = None
    gateway: Optional[str] = None
    payment_type: Optional[str] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    customer_email: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
