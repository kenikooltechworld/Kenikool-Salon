from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo import DESCENDING
from app.database import db


class PayrollService:
    """Service for managing payroll calculations and pay stub generation."""

    @staticmethod
    async def calculate_payroll(
        staff_id: str,
        pay_period_start: datetime,
        pay_period_end: datetime,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Calculate payroll for a staff member for a pay period."""
        # Get staff info
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        )

        if not staff:
            raise ValueError("Staff member not found")

        hourly_rate = staff.get("hourly_rate", 0)

        # Get attendance records for the period
        attendance_records = await db.attendance_records.find(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
                "date": {
                    "$gte": pay_period_start,
                    "$lte": pay_period_end,
                },
            }
        ).to_list(None)

        # Calculate hours
        regular_hours = 0
        overtime_hours = 0
        total_hours = 0

        for record in attendance_records:
            hours = record.get("total_hours", 0)
            total_hours += hours
            if total_hours <= 40:
                regular_hours += hours
            else:
                if regular_hours < 40:
                    regular_hours += hours
                    if total_hours > 40:
                        overtime_hours = total_hours - 40
                        regular_hours = 40
                else:
                    overtime_hours += hours

        # Get commission earnings
        commission_records = await db.commission_history.find(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
                "pay_period_start": pay_period_start,
                "pay_period_end": pay_period_end,
            }
        ).to_list(None)

        commission_earnings = sum(
            record.get("commission_amount", 0) for record in commission_records
        )

        # Calculate gross pay
        gross_pay_hours = (regular_hours * hourly_rate) + (overtime_hours * hourly_rate * 1.5)
        gross_pay_total = gross_pay_hours + commission_earnings

        # Get payroll info for tax calculation
        payroll_info = staff.get("payroll_info", {})
        tax_withholding_percentage = payroll_info.get("tax_withholding_percentage", 0.15)

        # Calculate deductions
        tax_withholding = gross_pay_total * tax_withholding_percentage
        other_deductions = 0  # Can be extended for other deductions

        # Calculate net pay
        net_pay = gross_pay_total - tax_withholding - other_deductions

        payroll_record = {
            "staff_id": ObjectId(staff_id),
            "salon_id": ObjectId(salon_id),
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
            "other_deductions": other_deductions,
            "net_pay": net_pay,
            "payment_date": None,
            "payment_method": None,
            "payment_status": "pending",
            "notes": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await db.payroll_records.insert_one(payroll_record)
        payroll_record["_id"] = result.inserted_id
        return payroll_record

    @staticmethod
    async def get_payroll_record(
        payroll_id: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get a specific payroll record."""
        record = await db.payroll_records.find_one(
            {
                "_id": ObjectId(payroll_id),
                "salon_id": ObjectId(salon_id),
            }
        )
        return record

    @staticmethod
    async def get_staff_payroll_history(
        staff_id: str,
        salon_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get payroll history for a staff member."""
        records = await db.payroll_records.find(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        ).sort("pay_period_end", DESCENDING).skip(skip).limit(limit).to_list(None)
        return records

    @staticmethod
    async def update_payment_info(
        payroll_id: str,
        payment_date: datetime,
        payment_method: str,
        payment_status: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Update payment information for a payroll record."""
        record = await db.payroll_records.find_one_and_update(
            {
                "_id": ObjectId(payroll_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$set": {
                    "payment_date": payment_date,
                    "payment_method": payment_method,
                    "payment_status": payment_status,
                    "updated_at": datetime.utcnow(),
                }
            },
            return_document=True,
        )
        return record

    @staticmethod
    async def add_bonus(
        payroll_id: str,
        bonus_amount: float,
        reason: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Add a bonus to a payroll record."""
        record = await db.payroll_records.find_one(
            {
                "_id": ObjectId(payroll_id),
                "salon_id": ObjectId(salon_id),
            }
        )

        if not record:
            raise ValueError("Payroll record not found")

        # Update bonuses and recalculate net pay
        new_bonuses = record.get("bonuses", 0) + bonus_amount
        new_gross_total = (
            record.get("gross_pay_hours", 0)
            + record.get("commission_earnings", 0)
            + new_bonuses
        )
        new_net_pay = (
            new_gross_total
            - record.get("tax_withholding", 0)
            - record.get("other_deductions", 0)
        )

        updated_record = await db.payroll_records.find_one_and_update(
            {
                "_id": ObjectId(payroll_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$set": {
                    "bonuses": new_bonuses,
                    "gross_pay_total": new_gross_total,
                    "net_pay": new_net_pay,
                    "updated_at": datetime.utcnow(),
                }
            },
            return_document=True,
        )
        return updated_record

    @staticmethod
    async def get_pending_payroll(salon_id: str) -> List[Dict[str, Any]]:
        """Get all pending payroll records for a salon."""
        records = await db.payroll_records.find(
            {
                "salon_id": ObjectId(salon_id),
                "payment_status": "pending",
            }
        ).sort("pay_period_end", 1).to_list(None)
        return records

    @staticmethod
    async def get_payroll_summary(
        salon_id: str,
        pay_period_start: datetime,
        pay_period_end: datetime,
    ) -> Dict[str, Any]:
        """Get payroll summary for a pay period."""
        records = await db.payroll_records.find(
            {
                "salon_id": ObjectId(salon_id),
                "pay_period_start": pay_period_start,
                "pay_period_end": pay_period_end,
            }
        ).to_list(None)

        total_gross = sum(r.get("gross_pay_total", 0) for r in records)
        total_net = sum(r.get("net_pay", 0) for r in records)
        total_tax = sum(r.get("tax_withholding", 0) for r in records)
        total_commission = sum(r.get("commission_earnings", 0) for r in records)
        total_bonuses = sum(r.get("bonuses", 0) for r in records)

        paid_count = sum(1 for r in records if r.get("payment_status") == "paid")
        pending_count = sum(1 for r in records if r.get("payment_status") == "pending")

        return {
            "pay_period_start": pay_period_start,
            "pay_period_end": pay_period_end,
            "total_staff": len(records),
            "total_gross_pay": total_gross,
            "total_net_pay": total_net,
            "total_tax_withholding": total_tax,
            "total_commission_earnings": total_commission,
            "total_bonuses": total_bonuses,
            "paid_count": paid_count,
            "pending_count": pending_count,
        }

    @staticmethod
    async def export_payroll_csv(
        salon_id: str,
        pay_period_start: datetime,
        pay_period_end: datetime,
    ) -> str:
        """Generate CSV export of payroll data."""
        records = await db.payroll_records.find(
            {
                "salon_id": ObjectId(salon_id),
                "pay_period_start": pay_period_start,
                "pay_period_end": pay_period_end,
            }
        ).to_list(None)

        # Build CSV content
        csv_lines = [
            "Staff ID,Regular Hours,Overtime Hours,Hourly Rate,Gross Pay (Hours),Commission,Bonuses,Gross Total,Tax Withholding,Deductions,Net Pay,Payment Status,Payment Date,Payment Method"
        ]

        for record in records:
            csv_lines.append(
                f"{record.get('staff_id')},"
                f"{record.get('regular_hours', 0)},"
                f"{record.get('overtime_hours', 0)},"
                f"{record.get('hourly_rate', 0)},"
                f"{record.get('gross_pay_hours', 0)},"
                f"{record.get('commission_earnings', 0)},"
                f"{record.get('bonuses', 0)},"
                f"{record.get('gross_pay_total', 0)},"
                f"{record.get('tax_withholding', 0)},"
                f"{record.get('other_deductions', 0)},"
                f"{record.get('net_pay', 0)},"
                f"{record.get('payment_status', 'pending')},"
                f"{record.get('payment_date', '')},"
                f"{record.get('payment_method', '')}"
            )

        return "\n".join(csv_lines)
