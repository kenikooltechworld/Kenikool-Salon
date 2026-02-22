"""
Pydantic schemas for request/response validation
"""
from app.schemas.base import ErrorResponse, SuccessResponse, PaginationParams, PaginatedResponse
from app.schemas.auth import (
    RegisterRequest, LoginRequest, AuthResponse, UserResponse,
    VerifyEmailRequest, ResendVerificationRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from app.schemas.tenant import (
    TenantResponse, UpdateTenantRequest, BankAccountInput, SalonNameAvailability, PublicSalonResponse
)
from app.schemas.service import (
    ServiceResponse, ServiceCreate, ServiceUpdate, ServiceFilter
)
from app.schemas.stylist import (
    StylistResponse, StylistCreate, StylistUpdate, WorkingHoursInput, StylistScheduleInput
)
from app.schemas.booking import (
    BookingResponse, BookingCreate, BookingStatusUpdate, BookingFilter, TimeSlotResponse
)
from app.schemas.client import (
    ClientResponse, ClientCreate, ClientUpdate, ClientFilter, ClientPhotoInput
)
from app.schemas.payment import (
    PaymentResponse, PaymentInitRequest, PaymentInitResponse, DepositPaymentRequest, CheckoutRequest
)
from app.schemas.inventory import (
    InventoryProductResponse, InventoryProductCreate, InventoryProductUpdate,
    InventoryAdjustmentRequest, LowStockAlertResponse
)
from app.schemas.waitlist import (
    WaitlistResponse, WaitlistCreate, WaitlistUpdate
)
from app.schemas.review import (
    ReviewResponse, ReviewCreate, ReviewModerate, RatingAggregation
)
from app.schemas.package import (
    PackageResponse, PackageCreate
)
from app.schemas.promo_code import (
    PromoCodeResponse, PromoCodeCreate, PromoCodeValidationResponse
)
from app.schemas.expense import (
    ExpenseResponse, ExpenseCreate, ExpenseUpdate
)
from app.schemas.membership import (
    MembershipPlanResponse, MembershipPlanCreate,
    MembershipSubscriptionResponse, MembershipSubscriptionCreate,
    CancelSubscriptionRequest
)
from app.schemas.subscription import (
    SubscriptionPlanResponse, SubscriptionUpgradeRequest, SubscriptionResponse,
    PaymentMethodCreate, PaymentMethodResponse, BillingHistoryResponse
)
from app.schemas.group_booking import (
    GroupBookingResponse, GroupBookingCreate, GroupBookingMemberInput
)
from app.schemas.gift_card import (
    GiftCardResponse, GiftCardCreate, GiftCardValidationResponse,
    GiftCardRedemptionResponse, GiftCardBalanceResponse
)
from app.schemas.referral import (
    ReferralResponse, ReferralDashboardResponse
)
from app.schemas.location import (
    LocationResponse, LocationCreate, LocationUpdate
)
from app.schemas.dashboard import (
    DashboardMetricsResponse
)
# Analytics schemas are defined but not exported here

__all__ = [
    # Base
    "ErrorResponse", "SuccessResponse", "PaginationParams", "PaginatedResponse",
    # Auth
    "RegisterRequest", "LoginRequest", "AuthResponse", "UserResponse",
    "VerifyEmailRequest", "ResendVerificationRequest", "ForgotPasswordRequest", "ResetPasswordRequest",
    # Tenant
    "TenantResponse", "UpdateTenantRequest", "BankAccountInput", "SalonNameAvailability", "PublicSalonResponse",
    # Service
    "ServiceResponse", "ServiceCreate", "ServiceUpdate", "ServiceFilter",
    # Stylist
    "StylistResponse", "StylistCreate", "StylistUpdate", "WorkingHoursInput", "StylistScheduleInput",
    # Booking
    "BookingResponse", "BookingCreate", "BookingStatusUpdate", "BookingFilter", "TimeSlotResponse",
    # Client
    "ClientResponse", "ClientCreate", "ClientUpdate", "ClientFilter", "ClientPhotoInput",
    # Payment
    "PaymentResponse", "PaymentInitRequest", "PaymentInitResponse", "DepositPaymentRequest", "CheckoutRequest",
    # Inventory
    "InventoryProductResponse", "InventoryProductCreate", "InventoryProductUpdate",
    "InventoryAdjustmentRequest", "LowStockAlertResponse",
    # Waitlist
    "WaitlistResponse", "WaitlistCreate", "WaitlistUpdate",
    # Review
    "ReviewResponse", "ReviewCreate", "ReviewModerate", "RatingAggregation",
    # Package
    "PackageResponse", "PackageCreate",
    # Promo Code
    "PromoCodeResponse", "PromoCodeCreate", "PromoCodeValidationResponse",
    # Expense
    "ExpenseResponse", "ExpenseCreate", "ExpenseUpdate",
    # Membership
    "MembershipPlanResponse", "MembershipPlanCreate",
    "MembershipSubscriptionResponse", "MembershipSubscriptionCreate",
    "CancelSubscriptionRequest",
    # Group Booking
    "GroupBookingResponse", "GroupBookingCreate", "GroupBookingMemberInput",
    # Gift Card
    "GiftCardResponse", "GiftCardCreate", "GiftCardValidationResponse",
    "GiftCardRedemptionResponse", "GiftCardBalanceResponse",
    # Referral
    "ReferralResponse", "ReferralDashboardResponse",
    # Location
    "LocationResponse", "LocationCreate", "LocationUpdate",
    # Dashboard
    "DashboardMetricsResponse",
]
