"""
Staff Management Service - Core business logic for staff management enhancements
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bson import ObjectId
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class StaffManagementService:
    """Service for managing staff-related operations"""

    @staticmethod
    def create_schedule_template(
        tenant_id: str,
        staff_id: str,
        name: str,
        schedule: Dict[str, List[Dict[str, str]]],
        is_default: bool = False
    ) -> Dict:
        """Create a new schedule template for a staff member"""
        db = Database.get_db()
        
        template = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "name": name,
            "is_default": is_default,
            "schedule": schedule,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.schedule_templates.insert_one(template)
        template["_id"] = result.inserted_id
        return template

    @staticmethod
    def apply_schedule_template(
        tenant_id: str,
        template_id: str,
        staff_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Apply a schedule template to a date range"""
        db = Database.get_db()
        
        template = db.schedule_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id
        })
        
        if not template:
            raise NotFoundException("Schedule template not found")
        
        # Update staff schedule with template
        db.stylists.update_one(
            {"_id": ObjectId(staff_id), "tenant_id": tenant_id},
            {
                "$set": {
                    "schedule": template["schedule"],
                    "schedule_template_id": ObjectId(template_id),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"status": "success", "message": "Schedule template applied"}

    @staticmethod
    def create_time_off_request(
        tenant_id: str,
        staff_id: str,
        request_type: str,
        start_date: datetime,
        end_date: datetime,
        reason: str,
        notes: Optional[str] = None
    ) -> Dict:
        """Create a time-off request"""
        db = Database.get_db()
        
        # Get staff name
        staff = db.stylists.find_one({"_id": ObjectId(staff_id), "tenant_id": tenant_id})
        if not staff:
            raise NotFoundException("Staff member not found")
        
        # Calculate total days
        total_days = (end_date - start_date).days + 1
        
        request = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name", ""),
            "request_type": request_type,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "reason": reason,
            "notes": notes,
            "status": "pending",
            "reviewed_by": None,
            "reviewed_at": None,
            "review_notes": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.time_off_requests.insert_one(request)
        request["_id"] = result.inserted_id
        return request

    @staticmethod
    def approve_time_off_request(
        tenant_id: str,
        request_id: str,
        reviewed_by: str,
        review_notes: Optional[str] = None
    ) -> Dict:
        """Approve a time-off request"""
        db = Database.get_db()
        
        request = db.time_off_requests.find_one({
            "_id": ObjectId(request_id),
            "tenant_id": tenant_id
        })
        
        if not request:
            raise NotFoundException("Time-off request not found")
        
        if request["status"] != "pending":
            raise BadRequestException("Only pending requests can be approved")
        
        db.time_off_requests.update_one(
            {"_id": ObjectId(request_id)},
            {
                "$set": {
                    "status": "approved",
                    "reviewed_by": reviewed_by,
                    "reviewed_at": datetime.utcnow(),
                    "review_notes": review_notes,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        updated_request = db.time_off_requests.find_one({"_id": ObjectId(request_id)})
        return updated_request

    @staticmethod
    def deny_time_off_request(
        tenant_id: str,
        request_id: str,
        reviewed_by: str,
        review_notes: Optional[str] = None
    ) -> Dict:
        """Deny a time-off request"""
        db = Database.get_db()
        
        request = db.time_off_requests.find_one({
            "_id": ObjectId(request_id),
            "tenant_id": tenant_id
        })
        
        if not request:
            raise NotFoundException("Time-off request not found")
        
        if request["status"] != "pending":
            raise BadRequestException("Only pending requests can be denied")
        
        db.time_off_requests.update_one(
            {"_id": ObjectId(request_id)},
            {
                "$set": {
                    "status": "denied",
                    "reviewed_by": reviewed_by,
                    "reviewed_at": datetime.utcnow(),
                    "review_notes": review_notes,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        updated_request = db.time_off_requests.find_one({"_id": ObjectId(request_id)})
        return updated_request

    @staticmethod
    def create_shift_swap_request(
        tenant_id: str,
        requesting_staff_id: str,
        target_staff_id: str,
        shift_date: datetime,
        shift_start: str,
        shift_end: str,
        reason: str
    ) -> Dict:
        """Create a shift swap request"""
        db = Database.get_db()
        
        # Get staff names
        requesting_staff = db.stylists.find_one({
            "_id": ObjectId(requesting_staff_id),
            "tenant_id": tenant_id
        })
        target_staff = db.stylists.find_one({
            "_id": ObjectId(target_staff_id),
            "tenant_id": tenant_id
        })
        
        if not requesting_staff or not target_staff:
            raise NotFoundException("Staff member not found")
        
        swap = {
            "tenant_id": tenant_id,
            "requesting_staff_id": requesting_staff_id,
            "requesting_staff_name": requesting_staff.get("name", ""),
            "target_staff_id": target_staff_id,
            "target_staff_name": target_staff.get("name", ""),
            "shift_date": shift_date,
            "shift_start": shift_start,
            "shift_end": shift_end,
            "reason": reason,
            "status": "pending",
            "target_response_at": datetime.utcnow() + timedelta(days=2),
            "manager_approved_by": None,
            "manager_approved_at": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.shift_swaps.insert_one(swap)
        swap["_id"] = result.inserted_id
        return swap

    @staticmethod
    def create_performance_goal(
        tenant_id: str,
        staff_id: str,
        goal_type: str,
        target_value: float,
        period_start: datetime,
        period_end: datetime,
        created_by: str,
        notes: Optional[str] = None
    ) -> Dict:
        """Create a performance goal for a staff member"""
        db = Database.get_db()
        
        # Get staff name
        staff = db.stylists.find_one({"_id": ObjectId(staff_id), "tenant_id": tenant_id})
        if not staff:
            raise NotFoundException("Staff member not found")
        
        goal = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name", ""),
            "goal_type": goal_type,
            "target_value": target_value,
            "current_value": 0,
            "period_start": period_start,
            "period_end": period_end,
            "status": "active",
            "achieved_at": None,
            "notes": notes,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.performance_goals.insert_one(goal)
        goal["_id"] = result.inserted_id
        return goal

    @staticmethod
    def record_commission(
        tenant_id: str,
        staff_id: str,
        source_type: str,
        source_id: str,
        source_reference: str,
        base_amount: float,
        commission_rate: float,
        pay_period_start: datetime,
        pay_period_end: datetime,
        tier_applied: Optional[int] = None,
        adjustment_amount: Optional[float] = None,
        adjustment_reason: Optional[str] = None
    ) -> Dict:
        """Record a commission entry"""
        db = Database.get_db()
        
        # Get staff name
        staff = db.stylists.find_one({"_id": ObjectId(staff_id), "tenant_id": tenant_id})
        if not staff:
            raise NotFoundException("Staff member not found")
        
        # Calculate commission amount
        commission_amount = base_amount * (commission_rate / 100)
        if adjustment_amount:
            commission_amount += adjustment_amount
        
        commission = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name", ""),
            "source_type": source_type,
            "source_id": source_id,
            "source_reference": source_reference,
            "base_amount": base_amount,
            "commission_rate": commission_rate,
            "commission_amount": commission_amount,
            "tier_applied": tier_applied,
            "payout_status": "pending",
            "payout_date": None,
            "payout_method": None,
            "adjustment_amount": adjustment_amount,
            "adjustment_reason": adjustment_reason,
            "pay_period_start": pay_period_start,
            "pay_period_end": pay_period_end,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.commission_history.insert_one(commission)
        commission["_id"] = result.inserted_id
        return commission

    @staticmethod
    def record_attendance(
        tenant_id: str,
        staff_id: str,
        date: datetime,
        location_id: Optional[str] = None
    ) -> Dict:
        """Record clock-in for attendance"""
        db = Database.get_db()
        
        # Get staff name
        staff = db.stylists.find_one({"_id": ObjectId(staff_id), "tenant_id": tenant_id})
        if not staff:
            raise NotFoundException("Staff member not found")
        
        # Check if already clocked in today
        existing = db.attendance_records.find_one({
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "date": {"$gte": date.replace(hour=0, minute=0, second=0),
                    "$lt": date.replace(hour=23, minute=59, second=59)},
            "clock_out": None
        })
        
        if existing:
            raise BadRequestException("Staff member already clocked in")
        
        # Determine if late
        now = datetime.utcnow()
        scheduled_start = staff.get("schedule", {}).get(date.strftime("%A").lower(), [{}])[0].get("start")
        late_minutes = 0
        status = "present"
        
        if scheduled_start:
            scheduled_time = datetime.strptime(scheduled_start, "%H:%M").time()
            if now.time() > scheduled_time:
                late_minutes = int((now - datetime.combine(now.date(), scheduled_time)).total_seconds() / 60)
                status = "late" if late_minutes > 0 else "present"
        
        attendance = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name", ""),
            "date": date,
            "clock_in": now,
            "clock_out": None,
            "scheduled_start": None,
            "scheduled_end": None,
            "total_hours": 0,
            "regular_hours": 0,
            "overtime_hours": 0,
            "breaks": [],
            "total_break_minutes": 0,
            "status": status,
            "late_minutes": late_minutes,
            "notes": None,
            "approved_by": None,
            "approved_at": None,
            "location_id": location_id,
            "created_at": now,
            "updated_at": now
        }
        
        result = db.attendance_records.insert_one(attendance)
        attendance["_id"] = result.inserted_id
        return attendance

    @staticmethod
    def record_training(
        tenant_id: str,
        staff_id: str,
        training_topic: str,
        training_type: str,
        instructor: str,
        training_date: datetime,
        duration_hours: float,
        skill_level_before: str,
        skill_level_after: str,
        notes: Optional[str] = None,
        certificate_url: Optional[str] = None
    ) -> Dict:
        """Record a training session"""
        db = Database.get_db()
        
        # Get staff name
        staff = db.stylists.find_one({"_id": ObjectId(staff_id), "tenant_id": tenant_id})
        if not staff:
            raise NotFoundException("Staff member not found")
        
        training = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name", ""),
            "training_topic": training_topic,
            "training_type": training_type,
            "instructor": instructor,
            "training_date": training_date,
            "duration_hours": duration_hours,
            "completion_status": "completed",
            "skill_level_before": skill_level_before,
            "skill_level_after": skill_level_after,
            "notes": notes,
            "certificate_url": certificate_url,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.training_records.insert_one(training)
        training["_id"] = result.inserted_id
        return training

    @staticmethod
    def add_certification(
        tenant_id: str,
        staff_id: str,
        certification_name: str,
        issuing_body: str,
        certification_number: str,
        issue_date: datetime,
        expiration_date: datetime,
        is_required: bool = False,
        document_url: Optional[str] = None,
        continuing_education_hours: float = 0,
        notes: Optional[str] = None
    ) -> Dict:
        """Add a certification for a staff member"""
        db = Database.get_db()
        
        # Get staff name
        staff = db.stylists.find_one({"_id": ObjectId(staff_id), "tenant_id": tenant_id})
        if not staff:
            raise NotFoundException("Staff member not found")
        
        is_expired = expiration_date < datetime.utcnow()
        
        certification = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name", ""),
            "certification_name": certification_name,
            "issuing_body": issuing_body,
            "certification_number": certification_number,
            "issue_date": issue_date,
            "expiration_date": expiration_date,
            "is_expired": is_expired,
            "is_required": is_required,
            "document_url": document_url,
            "continuing_education_hours": continuing_education_hours,
            "notes": notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.certifications.insert_one(certification)
        certification["_id"] = result.inserted_id
        return certification

    @staticmethod
    def send_staff_message(
        tenant_id: str,
        sender_id: str,
        message_type: str,
        subject: str,
        content: str,
        recipient_ids: Optional[List[str]] = None,
        group_id: Optional[str] = None,
        is_broadcast: bool = False,
        is_shift_note: bool = False,
        shift_date: Optional[datetime] = None,
        priority: str = "normal"
    ) -> Dict:
        """Send a message to staff"""
        db = Database.get_db()
        
        # Get sender name
        sender = db.users.find_one({"_id": ObjectId(sender_id)})
        sender_name = sender.get("full_name", "") if sender else ""
        
        message = {
            "tenant_id": tenant_id,
            "message_type": message_type,
            "sender_id": sender_id,
            "sender_name": sender_name,
            "recipient_ids": recipient_ids or [],
            "group_id": group_id,
            "subject": subject,
            "content": content,
            "is_broadcast": is_broadcast,
            "is_shift_note": is_shift_note,
            "shift_date": shift_date,
            "read_by": [],
            "priority": priority,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.staff_messages.insert_one(message)
        message["_id"] = result.inserted_id
        return message

    @staticmethod
    def upload_staff_document(
        tenant_id: str,
        staff_id: str,
        document_type: str,
        document_name: str,
        file_url: str,
        file_type: str,
        file_size_bytes: int,
        uploaded_by: str,
        expiration_date: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """Upload a document for a staff member"""
        db = Database.get_db()
        
        # Get staff name
        staff = db.stylists.find_one({"_id": ObjectId(staff_id), "tenant_id": tenant_id})
        if not staff:
            raise NotFoundException("Staff member not found")
        
        is_expired = False
        if expiration_date:
            is_expired = expiration_date < datetime.utcnow()
        
        document = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name", ""),
            "document_type": document_type,
            "document_name": document_name,
            "file_url": file_url,
            "file_type": file_type,
            "file_size_bytes": file_size_bytes,
            "expiration_date": expiration_date,
            "is_expired": is_expired,
            "uploaded_by": uploaded_by,
            "uploaded_at": datetime.utcnow(),
            "version": 1,
            "previous_version_id": None,
            "notes": notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.staff_documents.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    @staticmethod
    def create_onboarding_checklist(
        tenant_id: str,
        staff_id: str,
        template_id: str,
        items: List[Dict[str, Any]]
    ) -> Dict:
        """Create an onboarding checklist for a new staff member"""
        db = Database.get_db()
        
        # Get staff name
        staff = db.stylists.find_one({"_id": ObjectId(staff_id), "tenant_id": tenant_id})
        if not staff:
            raise NotFoundException("Staff member not found")
        
        checklist = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name", ""),
            "template_id": template_id,
            "items": items,
            "progress_percentage": 0,
            "status": "not_started",
            "started_at": None,
            "completed_at": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.onboarding_checklists.insert_one(checklist)
        checklist["_id"] = result.inserted_id
        return checklist

    @staticmethod
    def calculate_payroll(
        tenant_id: str,
        staff_id: str,
        pay_period_start: datetime,
        pay_period_end: datetime
    ) -> Dict:
        """Calculate payroll for a staff member for a pay period"""
        db = Database.get_db()
        
        # Get staff
        staff = db.stylists.find_one({"_id": ObjectId(staff_id), "tenant_id": tenant_id})
        if not staff:
            raise NotFoundException("Staff member not found")
        
        # Get attendance records for period
        attendance_records = list(db.attendance_records.find({
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "date": {"$gte": pay_period_start, "$lte": pay_period_end}
        }))
        
        # Calculate hours
        regular_hours = sum(r.get("regular_hours", 0) for r in attendance_records)
        overtime_hours = sum(r.get("overtime_hours", 0) for r in attendance_records)
        
        # Get commission for period
        commissions = list(db.commission_history.find({
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "pay_period_start": pay_period_start,
            "pay_period_end": pay_period_end,
            "payout_status": "pending"
        }))
        
        commission_earnings = sum(c.get("commission_amount", 0) for c in commissions)
        
        # Calculate payroll
        hourly_rate = staff.get("hourly_rate", 0)
        gross_pay_hours = regular_hours * hourly_rate
        gross_pay_total = gross_pay_hours + commission_earnings
        
        payroll_info = staff.get("payroll_info", {})
        tax_withholding_percentage = payroll_info.get("tax_withholding_percentage", 0)
        tax_withholding = gross_pay_total * (tax_withholding_percentage / 100)
        
        net_pay = gross_pay_total - tax_withholding
        
        payroll = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name", ""),
            "pay_period_start": pay_period_start,
            "pay_period_end": pay_period_end,
            "regular_hours": regular_hours,
            "overtime_hours": overtime_hours,
            "hourly_rate": hourly_rate,
            "gross_pay_hours": gross_pay_hours,
            "commission_earnings": commission_earnings,
            "bonuses": 0,
            "gross_pay_total": gross_pay_total,
            "tax_withholding": tax_withholding,
            "other_deductions": 0,
            "net_pay": net_pay,
            "payment_date": None,
            "payment_method": None,
            "payment_status": "pending",
            "notes": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.payroll_records.insert_one(payroll)
        payroll["_id"] = result.inserted_id
        return payroll

    @staticmethod
    def create_performance_review(
        tenant_id: str,
        staff_id: str,
        review_date: datetime,
        review_period_start: datetime,
        review_period_end: datetime,
        reviewer_id: str,
        ratings: Dict[str, int],
        strengths: str,
        areas_for_improvement: str,
        goals: List[Dict[str, Any]],
        follow_up_date: Optional[datetime] = None
    ) -> Dict:
        """Create a performance review"""
        db = Database.get_db()
        
        # Get staff name
        staff = db.stylists.find_one({"_id": ObjectId(staff_id), "tenant_id": tenant_id})
        if not staff:
            raise NotFoundException("Staff member not found")
        
        # Get reviewer name
        reviewer = db.users.find_one({"_id": ObjectId(reviewer_id)})
        reviewer_name = reviewer.get("full_name", "") if reviewer else ""
        
        review = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name", ""),
            "review_date": review_date,
            "review_period_start": review_period_start,
            "review_period_end": review_period_end,
            "reviewer_id": reviewer_id,
            "reviewer_name": reviewer_name,
            "ratings": ratings,
            "strengths": strengths,
            "areas_for_improvement": areas_for_improvement,
            "goals": goals,
            "staff_self_review": None,
            "follow_up_date": follow_up_date,
            "status": "completed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.performance_reviews.insert_one(review)
        review["_id"] = result.inserted_id
        return review

    @staticmethod
    def record_staff_referral(
        tenant_id: str,
        referring_staff_id: str,
        referral_type: str,
        referred_name: str,
        referral_date: datetime,
        referred_client_id: Optional[str] = None,
        referred_staff_id: Optional[str] = None
    ) -> Dict:
        """Record a staff referral"""
        db = Database.get_db()
        
        # Get referring staff name
        staff = db.stylists.find_one({"_id": ObjectId(referring_staff_id), "tenant_id": tenant_id})
        if not staff:
            raise NotFoundException("Staff member not found")
        
        referral = {
            "tenant_id": tenant_id,
            "referring_staff_id": referring_staff_id,
            "referring_staff_name": staff.get("name", ""),
            "referral_type": referral_type,
            "referred_client_id": referred_client_id,
            "referred_staff_id": referred_staff_id,
            "referred_name": referred_name,
            "referral_date": referral_date,
            "status": "pending",
            "conversion_date": None,
            "total_revenue_generated": 0,
            "bonus_earned": 0,
            "bonus_paid": False,
            "bonus_paid_date": None,
            "notes": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.staff_referrals.insert_one(referral)
        referral["_id"] = result.inserted_id
        return referral


# Singleton instance
staff_management_service = StaffManagementService()
