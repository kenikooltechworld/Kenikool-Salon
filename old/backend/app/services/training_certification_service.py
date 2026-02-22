"""
Training & Certification Service - Manage staff training and certifications
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class TrainingCertificationService:
    """Service for managing staff training and certifications"""

    @staticmethod
    def create_training_record(
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
        """Create a training record"""
        db = Database.get_db()
        
        # Get staff
        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })
        
        if not staff:
            raise NotFoundException("Staff member not found")
        
        training = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name"),
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
    def get_training_records(
        tenant_id: str,
        staff_id: Optional[str] = None,
        training_type: Optional[str] = None
    ) -> List[Dict]:
        """Get training records"""
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if staff_id:
            query["staff_id"] = staff_id
        
        if training_type:
            query["training_type"] = training_type
        
        records = list(db.training_records.find(query).sort("training_date", -1))
        return records

    @staticmethod
    def create_certification(
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
        """Create a certification record"""
        db = Database.get_db()
        
        # Get staff
        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })
        
        if not staff:
            raise NotFoundException("Staff member not found")
        
        is_expired = expiration_date < datetime.utcnow()
        
        certification = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name"),
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
    def get_certifications(
        tenant_id: str,
        staff_id: Optional[str] = None,
        is_required: Optional[bool] = None
    ) -> List[Dict]:
        """Get certifications"""
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if staff_id:
            query["staff_id"] = staff_id
        
        if is_required is not None:
            query["is_required"] = is_required
        
        certs = list(db.certifications.find(query).sort("expiration_date", 1))
        return certs

    @staticmethod
    def get_expiring_certifications(
        tenant_id: str,
        days_until_expiry: int = 30
    ) -> List[Dict]:
        """Get certifications expiring soon"""
        db = Database.get_db()
        
        now = datetime.utcnow()
        expiry_date = now + timedelta(days=days_until_expiry)
        
        certs = list(db.certifications.find({
            "tenant_id": tenant_id,
            "expiration_date": {
                "$gte": now,
                "$lte": expiry_date
            },
            "is_expired": False
        }).sort("expiration_date", 1))
        
        return certs

    @staticmethod
    def update_certification(
        tenant_id: str,
        certification_id: str,
        expiration_date: Optional[datetime] = None,
        document_url: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """Update a certification"""
        db = Database.get_db()
        
        cert = db.certifications.find_one({
            "_id": ObjectId(certification_id),
            "tenant_id": tenant_id
        })
        
        if not cert:
            raise NotFoundException("Certification not found")
        
        update_data = {"updated_at": datetime.utcnow()}
        
        if expiration_date:
            update_data["expiration_date"] = expiration_date
            update_data["is_expired"] = expiration_date < datetime.utcnow()
        
        if document_url:
            update_data["document_url"] = document_url
        
        if notes is not None:
            update_data["notes"] = notes
        
        db.certifications.update_one(
            {"_id": ObjectId(certification_id)},
            {"$set": update_data}
        )
        
        return db.certifications.find_one({"_id": ObjectId(certification_id)})

    @staticmethod
    def get_training_report(
        tenant_id: str,
        staff_id: Optional[str] = None
    ) -> Dict:
        """Generate training report"""
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        if staff_id:
            query["staff_id"] = staff_id
        
        training_records = list(db.training_records.find(query))
        certifications = list(db.certifications.find(query))
        
        # Calculate statistics
        total_training_hours = sum(r.get("duration_hours", 0) for r in training_records)
        total_ce_hours = sum(c.get("continuing_education_hours", 0) for c in certifications)
        
        # Group by staff if not filtered
        by_staff = {}
        if not staff_id:
            for record in training_records:
                sid = record.get("staff_id")
                if sid not in by_staff:
                    by_staff[sid] = {
                        "staff_name": record.get("staff_name"),
                        "training_count": 0,
                        "training_hours": 0,
                        "certification_count": 0,
                        "ce_hours": 0
                    }
                by_staff[sid]["training_count"] += 1
                by_staff[sid]["training_hours"] += record.get("duration_hours", 0)
            
            for cert in certifications:
                sid = cert.get("staff_id")
                if sid not in by_staff:
                    by_staff[sid] = {
                        "staff_name": cert.get("staff_name"),
                        "training_count": 0,
                        "training_hours": 0,
                        "certification_count": 0,
                        "ce_hours": 0
                    }
                by_staff[sid]["certification_count"] += 1
                by_staff[sid]["ce_hours"] += cert.get("continuing_education_hours", 0)
        
        return {
            "total_training_records": len(training_records),
            "total_training_hours": round(total_training_hours, 2),
            "total_certifications": len(certifications),
            "total_ce_hours": round(total_ce_hours, 2),
            "expired_certifications": len([c for c in certifications if c.get("is_expired")]),
            "expiring_soon": len(TrainingCertificationService.get_expiring_certifications(tenant_id)),
            "by_staff": by_staff
        }

    @staticmethod
    def get_staff_skill_levels(
        tenant_id: str,
        staff_id: str
    ) -> Dict:
        """Get current skill levels for a staff member"""
        db = Database.get_db()
        
        # Get latest training records
        training_records = list(db.training_records.find({
            "tenant_id": tenant_id,
            "staff_id": staff_id
        }).sort("training_date", -1))
        
        # Group by topic and get latest skill level
        skill_levels = {}
        for record in training_records:
            topic = record.get("training_topic")
            if topic not in skill_levels:
                skill_levels[topic] = {
                    "current_level": record.get("skill_level_after"),
                    "last_training": record.get("training_date"),
                    "training_count": 0
                }
            skill_levels[topic]["training_count"] += 1
        
        return skill_levels

    @staticmethod
    def check_required_certifications(
        tenant_id: str,
        staff_id: str
    ) -> Dict:
        """Check if staff has all required certifications"""
        db = Database.get_db()
        
        # Get all required certifications
        required_certs = list(db.certifications.find({
            "tenant_id": tenant_id,
            "is_required": True
        }))
        
        # Get staff certifications
        staff_certs = list(db.certifications.find({
            "tenant_id": tenant_id,
            "staff_id": staff_id
        }))
        
        staff_cert_names = set(c.get("certification_name") for c in staff_certs)
        
        missing = []
        expired = []
        
        for req_cert in required_certs:
            cert_name = req_cert.get("certification_name")
            if cert_name not in staff_cert_names:
                missing.append(cert_name)
            else:
                # Check if expired
                staff_cert = next((c for c in staff_certs if c.get("certification_name") == cert_name), None)
                if staff_cert and staff_cert.get("is_expired"):
                    expired.append(cert_name)
        
        return {
            "staff_id": staff_id,
            "all_required_current": len(missing) == 0 and len(expired) == 0,
            "missing_certifications": missing,
            "expired_certifications": expired,
            "total_required": len(required_certs),
            "current_certifications": len(staff_certs)
        }


# Singleton instance
training_certification_service = TrainingCertificationService()
