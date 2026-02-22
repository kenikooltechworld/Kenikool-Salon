"""
Attendance Service - Time tracking and attendance management
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class AttendanceService:
    """Service for managing staff attendance and time tracking"""

    @staticmethod
    def clock_in(
        tenant_id: str,
        staff_id: str,
        location_id: Optional[str] = None
    ) -> Dict:
        """Record clock-in for a staff member"""
        db = Database.get_db()
        
        # Get staff
        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })
        
        if not staff:
            raise NotFoundException("Staff member not found")
        
        # Check if already clocked in
        today = datetime.utcnow().date()
        existing = db.attendance_records.find_one({
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "date": {"$gte": datetime.combine(today, datetime.min.time()),
                    "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())},
            "clock_out": None
        })
        
        if existing:
            raise BadRequestException("Staff member already clocked in")
        
        # Determine if late
        now = datetime.utcnow()
        late_minutes = 0
        status = "present"
        
        # Get scheduled start time
        day_name = now.strftime("%A").lower()
        schedule = staff.get("schedule", {})
        day_schedule = schedule.get(day_name, [])
        
        if day_schedule and len(day_schedule) > 0:
            scheduled_start_str = day_schedule[0].get("start")
            if scheduled_start_str:
                try:
                    scheduled_hour, scheduled_minute = map(int, scheduled_start_str.split(":"))
                    scheduled_time = now.replace(hour=scheduled_hour, minute=scheduled_minute, second=0, microsecond=0)
                    if now > scheduled_time:
                        late_minutes = int((now - scheduled_time).total_seconds() / 60)
                        status = "late" if late_minutes > 0 else "present"
                except:
                    pass
        
        attendance = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name"),
            "date": datetime.combine(today, datetime.min.time()),
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
    def clock_out(
        tenant_id: str,
        staff_id: str
    ) -> Dict:
        """Record clock-out for a staff member"""
        db = Database.get_db()
        
        today = datetime.utcnow().date()
        now = datetime.utcnow()
        
        # Find active clock-in
        attendance = db.attendance_records.find_one({
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "date": {"$gte": datetime.combine(today, datetime.min.time()),
                    "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())},
            "clock_out": None
        })
        
        if not attendance:
            raise BadRequestException("No active clock-in found")
        
        # Calculate hours
        clock_in = attendance.get("clock_in")
        total_minutes = int((now - clock_in).total_seconds() / 60)
        break_minutes = attendance.get("total_break_minutes", 0)
        worked_minutes = total_minutes - break_minutes
        worked_hours = worked_minutes / 60
        
        # Calculate regular and overtime
        regular_hours = min(worked_hours, 8)
        overtime_hours = max(0, worked_hours - 8)
        
        db.attendance_records.update_one(
            {"_id": attendance["_id"]},
            {
                "$set": {
                    "clock_out": now,
                    "total_hours": round(worked_hours, 2),
                    "regular_hours": round(regular_hours, 2),
                    "overtime_hours": round(overtime_hours, 2),
                    "updated_at": now
                }
            }
        )
        
        return db.attendance_records.find_one({"_id": attendance["_id"]})

    @staticmethod
    def start_break(
        tenant_id: str,
        staff_id: str
    ) -> Dict:
        """Start a break"""
        db = Database.get_db()
        
        today = datetime.utcnow().date()
        now = datetime.utcnow()
        
        # Find active clock-in
        attendance = db.attendance_records.find_one({
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "date": {"$gte": datetime.combine(today, datetime.min.time()),
                    "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())},
            "clock_out": None
        })
        
        if not attendance:
            raise BadRequestException("No active clock-in found")
        
        # Check if already on break
        breaks = attendance.get("breaks", [])
        if breaks and breaks[-1].get("end") is None:
            raise BadRequestException("Already on break")
        
        # Add break
        new_break = {
            "start": now,
            "end": None,
            "duration_minutes": 0
        }
        breaks.append(new_break)
        
        db.attendance_records.update_one(
            {"_id": attendance["_id"]},
            {
                "$set": {
                    "breaks": breaks,
                    "updated_at": now
                }
            }
        )
        
        return db.attendance_records.find_one({"_id": attendance["_id"]})

    @staticmethod
    def end_break(
        tenant_id: str,
        staff_id: str
    ) -> Dict:
        """End a break"""
        db = Database.get_db()
        
        today = datetime.utcnow().date()
        now = datetime.utcnow()
        
        # Find active clock-in
        attendance = db.attendance_records.find_one({
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "date": {"$gte": datetime.combine(today, datetime.min.time()),
                    "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())},
            "clock_out": None
        })
        
        if not attendance:
            raise BadRequestException("No active clock-in found")
        
        breaks = attendance.get("breaks", [])
        if not breaks or breaks[-1].get("end") is not None:
            raise BadRequestException("Not on break")
        
        # End break
        break_start = breaks[-1]["start"]
        duration_minutes = int((now - break_start).total_seconds() / 60)
        breaks[-1]["end"] = now
        breaks[-1]["duration_minutes"] = duration_minutes
        
        # Calculate total break time
        total_break_minutes = sum(b.get("duration_minutes", 0) for b in breaks)
        
        db.attendance_records.update_one(
            {"_id": attendance["_id"]},
            {
                "$set": {
                    "breaks": breaks,
                    "total_break_minutes": total_break_minutes,
                    "updated_at": now
                }
            }
        )
        
        return db.attendance_records.find_one({"_id": attendance["_id"]})

    @staticmethod
    def get_attendance_records(
        tenant_id: str,
        staff_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get attendance records"""
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if staff_id:
            query["staff_id"] = staff_id
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            if date_query:
                query["date"] = date_query
        
        if status:
            query["status"] = status
        
        records = list(db.attendance_records.find(query).sort("date", -1))
        return records

    @staticmethod
    def update_attendance(
        tenant_id: str,
        attendance_id: str,
        status: Optional[str] = None,
        notes: Optional[str] = None,
        clock_in: Optional[datetime] = None,
        clock_out: Optional[datetime] = None
    ) -> Dict:
        """Update attendance record"""
        db = Database.get_db()
        
        attendance = db.attendance_records.find_one({
            "_id": ObjectId(attendance_id),
            "tenant_id": tenant_id
        })
        
        if not attendance:
            raise NotFoundException("Attendance record not found")
        
        update_data = {"updated_at": datetime.utcnow()}
        
        if status:
            update_data["status"] = status
        if notes is not None:
            update_data["notes"] = notes
        if clock_in:
            update_data["clock_in"] = clock_in
        if clock_out:
            update_data["clock_out"] = clock_out
        
        db.attendance_records.update_one(
            {"_id": ObjectId(attendance_id)},
            {"$set": update_data}
        )
        
        return db.attendance_records.find_one({"_id": ObjectId(attendance_id)})

    @staticmethod
    def get_attendance_report(
        tenant_id: str,
        staff_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Generate attendance report"""
        db = Database.get_db()
        
        # Default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        query = {
            "tenant_id": tenant_id,
            "date": {"$gte": start_date, "$lte": end_date}
        }
        
        if staff_id:
            query["staff_id"] = staff_id
        
        records = list(db.attendance_records.find(query))
        
        # Calculate statistics
        total_days = len(records)
        present_days = len([r for r in records if r.get("status") == "present"])
        late_days = len([r for r in records if r.get("status") == "late"])
        absent_days = len([r for r in records if r.get("status") == "absent"])
        
        total_hours = sum(r.get("total_hours", 0) for r in records)
        total_overtime = sum(r.get("overtime_hours", 0) for r in records)
        
        punctuality_rate = (present_days / total_days * 100) if total_days > 0 else 0
        absence_rate = (absent_days / total_days * 100) if total_days > 0 else 0
        
        # Group by staff if not filtered
        by_staff = {}
        if not staff_id:
            for record in records:
                sid = record.get("staff_id")
                if sid not in by_staff:
                    by_staff[sid] = {
                        "staff_name": record.get("staff_name"),
                        "total_days": 0,
                        "present_days": 0,
                        "late_days": 0,
                        "absent_days": 0,
                        "total_hours": 0,
                        "total_overtime": 0
                    }
                
                by_staff[sid]["total_days"] += 1
                by_staff[sid]["total_hours"] += record.get("total_hours", 0)
                by_staff[sid]["total_overtime"] += record.get("overtime_hours", 0)
                
                status = record.get("status")
                if status == "present":
                    by_staff[sid]["present_days"] += 1
                elif status == "late":
                    by_staff[sid]["late_days"] += 1
                elif status == "absent":
                    by_staff[sid]["absent_days"] += 1
        
        return {
            "period_start": start_date,
            "period_end": end_date,
            "total_days": total_days,
            "present_days": present_days,
            "late_days": late_days,
            "absent_days": absent_days,
            "total_hours": round(total_hours, 2),
            "total_overtime": round(total_overtime, 2),
            "punctuality_rate": round(punctuality_rate, 2),
            "absence_rate": round(absence_rate, 2),
            "by_staff": by_staff
        }

    @staticmethod
    def export_attendance_data(
        tenant_id: str,
        staff_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """Export attendance data for payroll"""
        db = Database.get_db()
        
        # Default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        query = {
            "tenant_id": tenant_id,
            "date": {"$gte": start_date, "$lte": end_date}
        }
        
        if staff_id:
            query["staff_id"] = staff_id
        
        records = list(db.attendance_records.find(query).sort("date", 1))
        
        # Format for export
        export_data = []
        for record in records:
            export_data.append({
                "staff_id": record.get("staff_id"),
                "staff_name": record.get("staff_name"),
                "date": record.get("date"),
                "clock_in": record.get("clock_in"),
                "clock_out": record.get("clock_out"),
                "total_hours": record.get("total_hours"),
                "regular_hours": record.get("regular_hours"),
                "overtime_hours": record.get("overtime_hours"),
                "status": record.get("status"),
                "late_minutes": record.get("late_minutes")
            })
        
        return export_data


# Singleton instance
attendance_service = AttendanceService()
