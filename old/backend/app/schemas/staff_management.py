"""
Pydantic schemas for staff management enhancements
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class StaffRole(str, Enum):
    OWNER = "owner"
    MANAGER = "manager"
    STYLIST = "stylist"
    RECEPTIONIST = "receptionist"


class TimeOffType(str, Enum):
    VACATION = "vacation"
    SICK = "sick"
    PERSONAL = "personal"
    UNPAID = "unpaid"


class TimeOffStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class ShiftSwapStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    APPROVED = "approved"
    CANCELLED = "cancelled"


class PerformanceGoalType(str, Enum):
    REVENUE = "revenue"
    BOOKINGS = "bookings"
    RATING = "rating"
    REBOOKING_RATE = "rebooking_rate"


class PerformanceGoalStatus(str, Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    MISSED = "missed"
    CANCELLED = "cancelled"


class CommissionPayoutStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    DISPUTED = "disputed"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    LATE = "late"
    ABSENT = "absent"
    EXCUSED = "excused"


class TrainingType(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"
    ONLINE = "online"
    CERTIFICATION = "certification"


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER = "master"


class DocumentType(str, Enum):
    CONTRACT = "contract"
    ID = "id"
    LICENSE = "license"
    TAX_FORM = "tax_form"
    OTHER = "other"


class OnboardingItemStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class OnboardingStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class PayPeriod(str, Enum):
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CHECK = "check"
    DIRECT_DEPOSIT = "direct_deposit"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class ReviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    FOLLOW_UP_NEEDED = "follow_up_needed"


class ReferralType(str, Enum):
    CLIENT = "client"
    STAFF = "staff"


class ReferralStatus(str, Enum):
    PENDING = "pending"
    CONVERTED = "converted"
    ACTIVE = "active"
    INACTIVE = "inactive"


# Schedule Template Schemas
class ScheduleTemplateCreate(BaseModel):
    name: str
    is_default: bool = False
    schedule: Dict[str, List[Dict[str, str]]]


class ScheduleTemplateUpdate(BaseModel):
    name: Optional[str] = None
    is_default: Optional[bool] = None
    schedule: Optional[Dict[str, List[Dict[str, str]]]] = None


class ScheduleTemplateResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    name: str
    is_default: bool
    schedule: Dict[str, List[Dict[str, str]]]
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Time-Off Request Schemas
class TimeOffRequestCreate(BaseModel):
    request_type: TimeOffType
    start_date: datetime
    end_date: datetime
    reason: str
    notes: Optional[str] = None


class TimeOffRequestUpdate(BaseModel):
    status: TimeOffStatus
    review_notes: Optional[str] = None


class TimeOffRequestResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    staff_name: str
    request_type: TimeOffType
    start_date: datetime
    end_date: datetime
    total_days: int
    reason: str
    notes: Optional[str]
    status: TimeOffStatus
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Shift Swap Schemas
class ShiftSwapCreate(BaseModel):
    target_staff_id: str
    shift_date: datetime
    shift_start: str
    shift_end: str
    reason: str


class ShiftSwapResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    requesting_staff_id: str
    requesting_staff_name: str
    target_staff_id: str
    target_staff_name: str
    shift_date: datetime
    shift_start: str
    shift_end: str
    reason: str
    status: ShiftSwapStatus
    target_response_at: Optional[datetime] = None
    manager_approved_by: Optional[str] = None
    manager_approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Performance Goal Schemas
class PerformanceGoalCreate(BaseModel):
    goal_type: PerformanceGoalType
    target_value: float
    period_start: datetime
    period_end: datetime
    notes: Optional[str] = None


class PerformanceGoalUpdate(BaseModel):
    target_value: Optional[float] = None
    status: Optional[PerformanceGoalStatus] = None
    notes: Optional[str] = None


class PerformanceGoalResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    staff_name: str
    goal_type: PerformanceGoalType
    target_value: float
    current_value: float
    period_start: datetime
    period_end: datetime
    status: PerformanceGoalStatus
    achieved_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Commission History Schemas
class CommissionHistoryResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    staff_name: str
    source_type: str
    source_id: str
    source_reference: str
    base_amount: float
    commission_rate: float
    commission_amount: float
    tier_applied: Optional[int] = None
    payout_status: CommissionPayoutStatus
    payout_date: Optional[datetime] = None
    payout_method: Optional[PaymentMethod] = None
    adjustment_amount: Optional[float] = None
    adjustment_reason: Optional[str] = None
    pay_period_start: datetime
    pay_period_end: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class CommissionAdjustmentCreate(BaseModel):
    staff_id: str
    amount: float
    reason: str


# Attendance Record Schemas
class BreakRecord(BaseModel):
    start: datetime
    end: datetime
    duration_minutes: int


class AttendanceRecordCreate(BaseModel):
    staff_id: str
    location_id: Optional[str] = None


class AttendanceRecordUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None
    clock_in: Optional[datetime] = None
    clock_out: Optional[datetime] = None


class AttendanceRecordResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    staff_name: str
    date: datetime
    clock_in: Optional[datetime] = None
    clock_out: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    total_hours: float
    regular_hours: float
    overtime_hours: float
    breaks: List[BreakRecord]
    total_break_minutes: int
    status: AttendanceStatus
    late_minutes: int
    notes: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    location_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Training Record Schemas
class TrainingRecordCreate(BaseModel):
    training_topic: str
    training_type: TrainingType
    instructor: str
    training_date: datetime
    duration_hours: float
    completion_status: str = "completed"
    skill_level_before: SkillLevel
    skill_level_after: SkillLevel
    notes: Optional[str] = None
    certificate_url: Optional[str] = None


class TrainingRecordResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    staff_name: str
    training_topic: str
    training_type: TrainingType
    instructor: str
    training_date: datetime
    duration_hours: float
    completion_status: str
    skill_level_before: SkillLevel
    skill_level_after: SkillLevel
    notes: Optional[str] = None
    certificate_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Certification Schemas
class CertificationCreate(BaseModel):
    certification_name: str
    issuing_body: str
    certification_number: str
    issue_date: datetime
    expiration_date: datetime
    is_required: bool = False
    document_url: Optional[str] = None
    continuing_education_hours: float = 0
    notes: Optional[str] = None


class CertificationUpdate(BaseModel):
    certification_name: Optional[str] = None
    issuing_body: Optional[str] = None
    certification_number: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    is_required: Optional[bool] = None
    document_url: Optional[str] = None
    continuing_education_hours: Optional[float] = None
    notes: Optional[str] = None


class CertificationResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    staff_name: str
    certification_name: str
    issuing_body: str
    certification_number: str
    issue_date: datetime
    expiration_date: datetime
    is_expired: bool
    is_required: bool
    document_url: Optional[str] = None
    continuing_education_hours: float
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Staff Message Schemas
class StaffMessage(BaseModel):
    sender_id: str
    recipient_id: str
    content: str
    read: bool = False
    created_at: datetime
    updated_at: datetime


class StaffMessageCreate(BaseModel):
    message_type: str  # announcement, direct, group, shift_note
    recipient_ids: Optional[List[str]] = None
    group_id: Optional[str] = None
    subject: str
    content: str
    is_broadcast: bool = False
    is_shift_note: bool = False
    shift_date: Optional[datetime] = None
    priority: str = "normal"


class StaffMessageResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    message_type: str
    sender_id: str
    sender_name: str
    recipient_ids: List[str]
    group_id: Optional[str] = None
    subject: str
    content: str
    is_broadcast: bool
    is_shift_note: bool
    shift_date: Optional[datetime] = None
    read_by: List[Dict[str, Any]]
    priority: str
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Staff Announcement Schemas
class StaffAnnouncement(BaseModel):
    sender_id: str
    title: str
    content: str
    target_roles: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


# Shift Note Schemas
class ShiftNote(BaseModel):
    shift_id: str
    author_id: str
    content: str
    created_at: datetime
    updated_at: datetime


# Staff Document Schemas
class StaffDocumentCreate(BaseModel):
    document_type: DocumentType
    document_name: str
    file_url: str
    file_type: str
    file_size_bytes: int
    expiration_date: Optional[datetime] = None
    notes: Optional[str] = None


class StaffDocumentResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    staff_name: str
    document_type: DocumentType
    document_name: str
    file_url: str
    file_type: str
    file_size_bytes: int
    expiration_date: Optional[datetime] = None
    is_expired: bool
    uploaded_by: str
    uploaded_at: datetime
    version: int
    previous_version_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Onboarding Checklist Schemas
class OnboardingChecklistItemCreate(BaseModel):
    title: str
    description: str
    assigned_to: str  # manager, staff, owner
    order: int


class OnboardingChecklistItemUpdate(BaseModel):
    status: OnboardingItemStatus
    notes: Optional[str] = None


class OnboardingChecklistResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    staff_name: str
    template_id: str
    items: List[Dict[str, Any]]
    progress_percentage: int
    status: OnboardingStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Payroll Record Schemas
class PayrollRecordCreate(BaseModel):
    staff_id: str
    pay_period_start: datetime
    pay_period_end: datetime
    regular_hours: float
    overtime_hours: float
    hourly_rate: float
    commission_earnings: float = 0
    bonuses: float = 0


class PayrollRecordResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    staff_name: str
    pay_period_start: datetime
    pay_period_end: datetime
    regular_hours: float
    overtime_hours: float
    hourly_rate: float
    gross_pay_hours: float
    commission_earnings: float
    bonuses: float
    gross_pay_total: float
    tax_withholding: float
    other_deductions: float
    net_pay: float
    payment_date: Optional[datetime] = None
    payment_method: Optional[PaymentMethod] = None
    payment_status: PaymentStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Performance Review Schemas
class PerformanceReviewGoal(BaseModel):
    goal: str
    target_date: datetime
    status: str = "pending"


class PerformanceReviewCreate(BaseModel):
    staff_id: str
    review_date: datetime
    review_period_start: datetime
    review_period_end: datetime
    ratings: Dict[str, int]
    strengths: str
    areas_for_improvement: str
    goals: List[PerformanceReviewGoal]
    follow_up_date: Optional[datetime] = None


class PerformanceReviewResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    staff_id: str
    staff_name: str
    review_date: datetime
    review_period_start: datetime
    review_period_end: datetime
    reviewer_id: str
    reviewer_name: str
    ratings: Dict[str, int]
    strengths: str
    areas_for_improvement: str
    goals: List[PerformanceReviewGoal]
    staff_self_review: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Staff Referral Schemas
class StaffReferralCreate(BaseModel):
    referral_type: ReferralType
    referred_client_id: Optional[str] = None
    referred_staff_id: Optional[str] = None
    referred_name: str
    referral_date: datetime


class StaffReferralResponse(BaseModel):
    id: str = Field(alias="_id")
    tenant_id: str
    referring_staff_id: str
    referring_staff_name: str
    referral_type: ReferralType
    referred_client_id: Optional[str] = None
    referred_staff_id: Optional[str] = None
    referred_name: str
    referral_date: datetime
    status: ReferralStatus
    conversion_date: Optional[datetime] = None
    total_revenue_generated: float
    bonus_earned: float
    bonus_paid: bool
    bonus_paid_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


# Emergency Contact Schemas
class EmergencyContact(BaseModel):
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None
    is_primary: bool = False


class MedicalInfo(BaseModel):
    allergies: Optional[str] = None
    conditions: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None


class PayrollInfo(BaseModel):
    pay_period: PayPeriod
    tax_withholding_percentage: float
    direct_deposit_account: Optional[str] = None
    direct_deposit_routing: Optional[str] = None


# Enhanced Stylist/Staff Schemas
class StylistEnhancedCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    role: StaffRole = StaffRole.STYLIST
    specialty: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: float
    commission_rate: float
    commission_tiers: Optional[List[Dict[str, float]]] = None
    services: Optional[List[str]] = None
    schedule: Optional[Dict[str, List[Dict[str, str]]]] = None
    locations: Optional[List[str]] = None
    primary_location_id: Optional[str] = None
    online_booking_enabled: bool = True
    max_bookings_per_day: Optional[int] = None
    buffer_time_minutes: int = 0
    emergency_contacts: Optional[List[EmergencyContact]] = None
    medical_info: Optional[MedicalInfo] = None
    payroll_info: Optional[PayrollInfo] = None


class StylistEnhancedUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[StaffRole] = None
    specialty: Optional[str] = None
    bio: Optional[str] = None
    hourly_rate: Optional[float] = None
    commission_rate: Optional[float] = None
    commission_tiers: Optional[List[Dict[str, float]]] = None
    services: Optional[List[str]] = None
    schedule: Optional[Dict[str, List[Dict[str, str]]]] = None
    locations: Optional[List[str]] = None
    primary_location_id: Optional[str] = None
    online_booking_enabled: Optional[bool] = None
    max_bookings_per_day: Optional[int] = None
    buffer_time_minutes: Optional[int] = None
    emergency_contacts: Optional[List[EmergencyContact]] = None
    medical_info: Optional[MedicalInfo] = None
    payroll_info: Optional[PayrollInfo] = None
    is_active: Optional[bool] = None
