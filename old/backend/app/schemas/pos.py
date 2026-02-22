"""
Point of Sale (POS) schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.base import BaseSchema


class POSCartItem(BaseModel):
    """POS cart item"""
    type: str = Field(..., description="Item type: service or product")
    item_id: str = Field(..., description="Service ID or Product ID")
    item_name: str = Field(..., description="Service or product name")
    quantity: int = Field(..., gt=0, description="Quantity")
    price: float = Field(..., gt=0, description="Unit price")
    discount: float = Field(default=0, ge=0, description="Discount amount")


class POSPaymentMethod(BaseModel):
    """POS payment method"""
    method: str = Field(..., description="Payment method: cash, card, transfer")
    amount: float = Field(..., gt=0, description="Payment amount")
    reference: Optional[str] = Field(None, description="Payment reference/transaction ID")


class POSTransactionCreate(BaseModel):
    """POS transaction creation request"""
    items: List[POSCartItem] = Field(..., min_length=1, description="Transaction items")
    client_id: Optional[str] = Field(None, description="Client ID (optional)")
    stylist_id: Optional[str] = Field(None, description="Stylist ID (optional)")
    discount_total: float = Field(default=0, ge=0, description="Total discount")
    tax: float = Field(default=0, ge=0, description="Tax amount")
    tip: float = Field(default=0, ge=0, description="Tip amount")
    notes: Optional[str] = Field(None, max_length=500, description="Transaction notes")


class POSPaymentRequest(BaseModel):
    """POS payment processing request"""
    transaction_id: str = Field(..., description="Transaction ID")
    payments: List[POSPaymentMethod] = Field(..., min_length=1, description="Payment methods")


class POSTransactionResponse(BaseSchema):
    """POS transaction response"""
    id: str
    tenant_id: str
    transaction_number: str
    items: List[Dict[str, Any]]
    subtotal: float
    discount_total: float
    tax: float
    tip: float
    total: float
    payments: List[Dict[str, Any]]
    client_id: Optional[str] = None
    stylist_id: Optional[str] = None
    created_by: str
    created_at: datetime
    status: str  # pending, completed, refunded, partially_refunded, voided
    refund_amount: Optional[float] = None
    refund_reason: Optional[str] = None
    refunded_at: Optional[datetime] = None
    refund_type: Optional[str] = None  # full or partial
    void_reason: Optional[str] = None
    voided_at: Optional[datetime] = None
    voided_by: Optional[str] = None


class CashDrawerOpen(BaseModel):
    """Cash drawer open request"""
    opening_balance: float = Field(..., ge=0, description="Opening cash balance")
    notes: Optional[str] = Field(None, max_length=500)


class CashDrawerDrop(BaseModel):
    """Cash drop request"""
    amount: float = Field(..., gt=0, description="Amount to drop")
    notes: Optional[str] = Field(None, max_length=500)


class CashDrawerClose(BaseModel):
    """Cash drawer close request"""
    actual_balance: float = Field(..., ge=0, description="Actual cash counted")
    notes: Optional[str] = Field(None, max_length=500)


class CashDrawerResponse(BaseSchema):
    """Cash drawer response"""
    id: str
    tenant_id: str
    opened_by: str
    opened_at: datetime
    opening_balance: float
    expected_balance: float
    actual_balance: Optional[float] = None
    variance: Optional[float] = None
    closed_at: Optional[datetime] = None
    transactions: List[Dict[str, Any]]
    status: str  # open, closed


class POSTransactionFilter(BaseModel):
    """POS transaction filter parameters"""
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    stylist_id: Optional[str] = None
    client_id: Optional[str] = None
    status: Optional[str] = None


class POSPaymentMethodSummary(BaseModel):
    """Payment method summary"""
    method: str
    total: float
    count: int


class POSDailySummary(BaseModel):
    """POS daily summary response"""
    date: str
    transaction_count: int
    total_sales: float
    average_transaction: float
    total_cash: float
    total_card: float
    total_tips: float
    total_discounts: float
    total_tax: float
    payment_methods: List[POSPaymentMethodSummary]
    services_revenue: float
    services_count: int
    products_revenue: float
    products_count: int
    cash_drawer_variance: Optional[float] = None


class POSReceiptRequest(BaseModel):
    """POS receipt generation request"""
    transaction_id: str = Field(..., description="Transaction ID")
    email: Optional[str] = Field(None, description="Email to send receipt (optional)")


class POSReceiptResponse(BaseModel):
    """POS receipt response"""
    transaction_id: str
    receipt_url: Optional[str] = None
    receipt_html: str
    sent_to_email: Optional[str] = None


class POSRefundRequest(BaseModel):
    """POS refund request"""
    refund_amount: float = Field(..., gt=0, description="Amount to refund")
    reason: str = Field(..., min_length=1, max_length=500, description="Refund reason")
    items: Optional[List[str]] = Field(None, description="Item IDs for partial refund (optional)")


class POSRefundResponse(BaseModel):
    """POS refund response"""
    status: str
    transaction_id: str
    refund_amount: float
    refund_type: str  # full or partial


class POSVoidRequest(BaseModel):
    """POS void request"""
    reason: str = Field(..., min_length=1, max_length=500, description="Void reason")


class POSVoidResponse(BaseModel):
    """POS void response"""
    status: str
    transaction_id: str
    void_reason: str


class POSDiscountApply(BaseModel):
    """POS discount application request"""
    discount_type: str = Field(..., pattern="^(promo_code|manual|member)$", description="Discount type")
    promo_code: Optional[str] = Field(None, description="Promo code (if type is promo_code)")
    discount_amount: Optional[float] = Field(None, gt=0, description="Manual discount amount")
    discount_percentage: Optional[float] = Field(None, gt=0, le=100, description="Manual discount percentage")
    reason: Optional[str] = Field(None, max_length=200, description="Discount reason (for manual discounts)")


class POSDiscountResponse(BaseModel):
    """POS discount validation response"""
    valid: bool
    discount_amount: float
    discount_type: str
    promo_code: Optional[str] = None
    reason: Optional[str] = None
    error: Optional[str] = None


class POSReturnRequest(BaseModel):
    """POS return/exchange request"""
    transaction_id: str = Field(..., description="Original transaction ID")
    return_items: List[Dict[str, Any]] = Field(..., min_length=1, description="Items to return")
    return_reason: str = Field(..., min_length=1, max_length=500, description="Return reason")
    restocking_fee: float = Field(default=0, ge=0, description="Restocking fee amount")
    exchange_items: Optional[List[Dict[str, Any]]] = Field(None, description="Items for exchange (optional)")


class POSReturnResponse(BaseModel):
    """POS return/exchange response"""
    status: str
    return_id: str
    transaction_id: str
    return_amount: float
    restocking_fee: float
    exchange_amount: float
    net_refund: float


# Feature 21: Gift Cards
class GiftCardCreate(BaseModel):
    """Gift card creation request"""
    amount: float = Field(..., gt=0, description="Gift card amount")
    card_type: str = Field(default="physical", pattern="^(physical|digital)$", description="Card type")
    recipient_name: Optional[str] = Field(None, max_length=200, description="Recipient name")
    recipient_email: Optional[str] = Field(None, description="Recipient email (for digital cards)")
    message: Optional[str] = Field(None, max_length=500, description="Gift message")
    expiration_months: int = Field(default=12, gt=0, le=60, description="Expiration in months")


class GiftCardResponse(BaseModel):
    """Gift card response"""
    id: str
    card_number: str
    amount: float
    balance: float
    card_type: str
    status: str  # active, redeemed, expired
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    redeemed_at: Optional[datetime] = None


class GiftCardRedeem(BaseModel):
    """Gift card redemption request"""
    card_number: str = Field(..., description="Gift card number")
    amount: float = Field(..., gt=0, description="Amount to redeem")


class GiftCardBalance(BaseModel):
    """Gift card balance response"""
    card_number: str
    balance: float
    status: str
    expires_at: datetime


# Feature 22: Multi-Currency
class CurrencyConversion(BaseModel):
    """Currency conversion request"""
    from_currency: str = Field(..., min_length=3, max_length=3, description="Source currency code (e.g., USD)")
    to_currency: str = Field(..., min_length=3, max_length=3, description="Target currency code")
    amount: float = Field(..., gt=0, description="Amount to convert")


class CurrencyConversionResponse(BaseModel):
    """Currency conversion response"""
    from_currency: str
    to_currency: str
    from_amount: float
    to_amount: float
    exchange_rate: float
    timestamp: datetime


class ExchangeRateUpdate(BaseModel):
    """Exchange rate update request"""
    currency_code: str = Field(..., min_length=3, max_length=3, description="Currency code")
    rate: float = Field(..., gt=0, description="Exchange rate to base currency")


# Feature 23: Customer Notes
class CustomerNotesResponse(BaseModel):
    """Customer notes and preferences response"""
    client_id: str
    preferences: Dict[str, Any]
    allergies: List[str]
    special_requirements: Optional[str] = None
    purchase_history: List[Dict[str, Any]]
    recommended_products: List[Dict[str, Any]]
    last_visit: Optional[datetime] = None
    total_spent: float
    visit_count: int


# Feature 24: Analytics Dashboard
class POSAnalyticsRequest(BaseModel):
    """POS analytics request"""
    date_from: str = Field(..., description="Start date (YYYY-MM-DD)")
    date_to: str = Field(..., description="End date (YYYY-MM-DD)")
    interval: str = Field(default="day", pattern="^(hour|day|week|month)$", description="Data interval")


class POSAnalyticsResponse(BaseModel):
    """POS analytics response"""
    date_from: str
    date_to: str
    total_sales: float
    total_transactions: int
    average_transaction: float
    best_selling_items: List[Dict[str, Any]]
    peak_hours: List[Dict[str, Any]]
    stylist_performance: List[Dict[str, Any]]
    revenue_trend: List[Dict[str, Any]]
    category_performance: List[Dict[str, Any]]
    payment_method_breakdown: Dict[str, float]


# Feature 25: Receipt Options
class ReceiptSendRequest(BaseModel):
    """Receipt send request"""
    transaction_id: str = Field(..., description="Transaction ID")
    method: str = Field(..., pattern="^(email|sms|print)$", description="Send method")
    recipient: Optional[str] = Field(None, description="Email address or phone number")
    save_preference: bool = Field(default=False, description="Save as client preference")


class ReceiptSendResponse(BaseModel):
    """Receipt send response"""
    status: str
    method: str
    recipient: Optional[str] = None
    message: str

