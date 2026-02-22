from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo import DESCENDING
from app.database import db


class DocumentManagementService:
    """Service for managing staff documents with version history and expiration tracking."""

    ALLOWED_FORMATS = {"pdf", "jpg", "jpeg", "png", "docx"}
    EXPIRATION_ALERT_DAYS = 30

    @staticmethod
    async def upload_document(
        staff_id: str,
        document_type: str,
        document_name: str,
        file_url: str,
        file_type: str,
        file_size_bytes: int,
        salon_id: str,
        uploaded_by: str,
        expiration_date: Optional[datetime] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a new document for a staff member."""
        # Validate file format
        file_ext = file_type.lower().split(".")[-1] if "." in file_type else file_type.lower()
        if file_ext not in DocumentManagementService.ALLOWED_FORMATS:
            raise ValueError(f"File format {file_ext} not allowed")

        # Check if document exists to handle versioning
        existing_doc = await db.staff_documents.find_one(
            {
                "staff_id": ObjectId(staff_id),
                "document_type": document_type,
                "salon_id": ObjectId(salon_id),
            },
            sort=[("created_at", DESCENDING)],
        )

        document = {
            "staff_id": ObjectId(staff_id),
            "document_type": document_type,
            "document_name": document_name,
            "file_url": file_url,
            "file_type": file_type,
            "file_size_bytes": file_size_bytes,
            "expiration_date": expiration_date,
            "is_expired": expiration_date and expiration_date < datetime.utcnow(),
            "uploaded_by": ObjectId(uploaded_by),
            "uploaded_at": datetime.utcnow(),
            "version": (existing_doc.get("version", 0) + 1) if existing_doc else 1,
            "previous_version_id": existing_doc.get("_id") if existing_doc else None,
            "notes": notes,
            "salon_id": ObjectId(salon_id),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await db.staff_documents.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    @staticmethod
    async def get_staff_documents(
        staff_id: str,
        salon_id: str,
        document_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all documents for a staff member."""
        query = {
            "staff_id": ObjectId(staff_id),
            "salon_id": ObjectId(salon_id),
            "previous_version_id": None,  # Only get latest versions
        }

        if document_type:
            query["document_type"] = document_type

        documents = await db.staff_documents.find(query).sort(
            "created_at", DESCENDING
        ).to_list(None)
        return documents

    @staticmethod
    async def get_document(document_id: str, salon_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document."""
        document = await db.staff_documents.find_one(
            {
                "_id": ObjectId(document_id),
                "salon_id": ObjectId(salon_id),
            }
        )
        return document

    @staticmethod
    async def get_document_versions(
        staff_id: str,
        document_type: str,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all versions of a document."""
        # Get the latest version first
        latest = await db.staff_documents.find_one(
            {
                "staff_id": ObjectId(staff_id),
                "document_type": document_type,
                "salon_id": ObjectId(salon_id),
                "previous_version_id": None,
            },
            sort=[("created_at", DESCENDING)],
        )

        if not latest:
            return []

        # Traverse version history
        versions = [latest]
        current_id = latest.get("_id")

        while current_id:
            prev_version = await db.staff_documents.find_one(
                {"_id": current_id}
            )
            if prev_version and prev_version.get("previous_version_id"):
                versions.append(prev_version)
                current_id = prev_version.get("previous_version_id")
            else:
                break

        return versions

    @staticmethod
    async def delete_document(document_id: str, salon_id: str) -> bool:
        """Delete a document."""
        result = await db.staff_documents.delete_one(
            {
                "_id": ObjectId(document_id),
                "salon_id": ObjectId(salon_id),
            }
        )
        return result.deleted_count > 0

    @staticmethod
    async def get_expiring_documents(
        salon_id: str,
        days_until_expiration: int = 30,
    ) -> List[Dict[str, Any]]:
        """Get documents expiring within specified days."""
        now = datetime.utcnow()
        expiration_threshold = now + timedelta(days=days_until_expiration)

        documents = await db.staff_documents.find(
            {
                "salon_id": ObjectId(salon_id),
                "expiration_date": {
                    "$gte": now,
                    "$lte": expiration_threshold,
                },
                "previous_version_id": None,  # Only latest versions
            }
        ).sort("expiration_date", 1).to_list(None)

        return documents

    @staticmethod
    async def get_expired_documents(salon_id: str) -> List[Dict[str, Any]]:
        """Get all expired documents."""
        documents = await db.staff_documents.find(
            {
                "salon_id": ObjectId(salon_id),
                "expiration_date": {"$lt": datetime.utcnow()},
                "previous_version_id": None,  # Only latest versions
            }
        ).sort("expiration_date", DESCENDING).to_list(None)

        return documents

    @staticmethod
    async def update_document_notes(
        document_id: str,
        notes: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Update notes for a document."""
        document = await db.staff_documents.find_one_and_update(
            {
                "_id": ObjectId(document_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$set": {
                    "notes": notes,
                    "updated_at": datetime.utcnow(),
                }
            },
            return_document=True,
        )
        return document

    @staticmethod
    async def check_missing_required_documents(
        staff_id: str,
        salon_id: str,
        required_types: List[str],
    ) -> Dict[str, bool]:
        """Check which required documents are missing."""
        documents = await db.staff_documents.find(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
                "previous_version_id": None,
            }
        ).to_list(None)

        document_types = {doc["document_type"] for doc in documents}
        missing = {}

        for doc_type in required_types:
            missing[doc_type] = doc_type not in document_types

        return missing

    @staticmethod
    async def get_staff_document_summary(
        staff_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Get a summary of staff documents."""
        documents = await db.staff_documents.find(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
                "previous_version_id": None,
            }
        ).to_list(None)

        now = datetime.utcnow()
        expiration_threshold = now + timedelta(days=DocumentManagementService.EXPIRATION_ALERT_DAYS)

        summary = {
            "total_documents": len(documents),
            "by_type": {},
            "expired_count": 0,
            "expiring_soon_count": 0,
            "total_size_bytes": 0,
        }

        for doc in documents:
            doc_type = doc.get("document_type", "other")
            if doc_type not in summary["by_type"]:
                summary["by_type"][doc_type] = 0
            summary["by_type"][doc_type] += 1

            if doc.get("expiration_date"):
                if doc["expiration_date"] < now:
                    summary["expired_count"] += 1
                elif doc["expiration_date"] <= expiration_threshold:
                    summary["expiring_soon_count"] += 1

            summary["total_size_bytes"] += doc.get("file_size_bytes", 0)

        return summary
