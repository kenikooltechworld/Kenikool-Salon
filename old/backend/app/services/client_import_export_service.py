"""
Client Import/Export Service

Handles CSV import and export for clients:
- CSV export with field selection
- CSV import with validation
- Duplicate detection and handling
- Import preview and validation

Requirements: REQ-CM-012
"""
import logging
import csv
import io
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from bson import ObjectId
import re

from app.database import Database

logger = logging.getLogger(__name__)


class ClientImportExportService:
    """Service for importing and exporting client data"""

    # Required fields for import
    REQUIRED_FIELDS = ["name", "phone"]

    # Optional fields
    OPTIONAL_FIELDS = [
        "email", "address", "birthday", "notes", "segment", "tags",
        "preferred_stylist_id", "communication_preferences"
    ]
    
    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()

    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Simple validation - at least 10 digits
        digits = re.sub(r"\D", "", phone)
        return len(digits) >= 10

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def validate_row(self, row: Dict[str, str], row_number: int) -> Tuple[bool, Optional[str]]:
        """
        Validate a single CSV row
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        if not row.get("name", "").strip():
            return False, f"Row {row_number}: Name is required"

        if not row.get("phone", "").strip():
            return False, f"Row {row_number}: Phone is required"

        # Validate phone
        if not self.validate_phone(row["phone"]):
            return False, f"Row {row_number}: Invalid phone format"

        # Validate email if provided
        if row.get("email", "").strip():
            if not self.validate_email(row["email"]):
                return False, f"Row {row_number}: Invalid email format"

        # Validate birthday if provided
        if row.get("birthday", "").strip():
            try:
                datetime.fromisoformat(row["birthday"])
            except ValueError:
                return False, f"Row {row_number}: Invalid birthday format (use YYYY-MM-DD)"

        # Validate segment if provided
        if row.get("segment", "").strip():
            valid_segments = ["new", "regular", "vip", "inactive"]
            if row["segment"] not in valid_segments:
                return False, f"Row {row_number}: Invalid segment (must be one of: {', '.join(valid_segments)})"

        return True, None

    def check_duplicate(
        self,
        tenant_id: str,
        phone: str,
        email: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if client already exists (by phone or email)
        
        Returns:
            Existing client or None
        """
        db = ClientImportExportService._get_db()
        query = {"tenant_id": tenant_id}

        # Check by phone
        existing = db.clients.find_one({
            **query,
            "phone": phone
        })

        if existing:
            return existing

        # Check by email if provided
        if email:
            existing = db.clients.find_one({
                **query,
                "email": email
            })

            if existing:
                return existing

        return None

    def preview_import(
        self,
        tenant_id: str,
        csv_content: str,
        duplicate_handling: str = "skip"
    ) -> Dict[str, Any]:
        """
        Preview import data without actually importing
        
        Args:
            tenant_id: Tenant ID
            csv_content: CSV file content
            duplicate_handling: How to handle duplicates (skip, update, create)
            
        Returns:
            Preview data with validation results
            
        Requirements: REQ-CM-012
        """
        preview = {
            "total_rows": 0,
            "valid_rows": 0,
            "invalid_rows": 0,
            "duplicate_rows": 0,
            "rows": [],
            "errors": [],
            "duplicate_handling": duplicate_handling
        }

        try:
            # Parse CSV
            reader = csv.DictReader(io.StringIO(csv_content))

            if not reader.fieldnames:
                preview["errors"].append("CSV file is empty")
                return preview

            row_number = 1
            for row in reader:
                row_number += 1
                preview["total_rows"] += 1

                # Validate row
                is_valid, error = self.validate_row(row, row_number)

                if not is_valid:
                    preview["invalid_rows"] += 1
                    preview["errors"].append(error)
                    preview["rows"].append({
                        "row_number": row_number,
                        "data": row,
                        "status": "invalid",
                        "error": error
                    })
                    continue

                # Check for duplicates
                duplicate = self.check_duplicate(
                    tenant_id,
                    row["phone"],
                    row.get("email")
                )

                if duplicate:
                    preview["duplicate_rows"] += 1
                    preview["rows"].append({
                        "row_number": row_number,
                        "data": row,
                        "status": "duplicate",
                        "duplicate_id": str(duplicate["_id"]),
                        "duplicate_handling": duplicate_handling
                    })
                else:
                    preview["valid_rows"] += 1
                    preview["rows"].append({
                        "row_number": row_number,
                        "data": row,
                        "status": "valid"
                    })

        except Exception as e:
            logger.error(f"Error previewing import: {e}")
            preview["errors"].append(f"Error parsing CSV: {str(e)}")

        return preview

    def import_clients(
        self,
        tenant_id: str,
        csv_content: str,
        duplicate_handling: str = "skip",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Import clients from CSV
        
        Args:
            tenant_id: Tenant ID
            csv_content: CSV file content
            duplicate_handling: How to handle duplicates (skip, update, create)
            user_id: User performing import
            
        Returns:
            Import results with success/failure counts
            
        Requirements: REQ-CM-012
        """
        db = ClientImportExportService._get_db()
        results = {
            "total_rows": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "failed": 0,
            "errors": [],
            "operation_id": str(ObjectId()),
            "started_at": datetime.now(),
            "completed_at": None
        }

        try:
            # Parse CSV
            reader = csv.DictReader(io.StringIO(csv_content))

            if not reader.fieldnames:
                results["errors"].append("CSV file is empty")
                return results

            row_number = 1
            for row in reader:
                row_number += 1
                results["total_rows"] += 1

                try:
                    # Validate row
                    is_valid, error = self.validate_row(row, row_number)

                    if not is_valid:
                        results["failed"] += 1
                        results["errors"].append(error)
                        continue

                    # Check for duplicates
                    duplicate = self.check_duplicate(
                        tenant_id,
                        row["phone"],
                        row.get("email")
                    )

                    if duplicate:
                        if duplicate_handling == "skip":
                            results["skipped"] += 1
                            continue
                        elif duplicate_handling == "update":
                            # Update existing client
                            update_data = {
                                "name": row.get("name", duplicate.get("name")),
                                "phone": row.get("phone", duplicate.get("phone")),
                                "email": row.get("email", duplicate.get("email")),
                                "address": row.get("address", duplicate.get("address")),
                                "notes": row.get("notes", duplicate.get("notes")),
                                "updated_at": datetime.now()
                            }

                            # Parse optional fields
                            if row.get("birthday"):
                                update_data["birthday"] = datetime.fromisoformat(row["birthday"])

                            if row.get("segment"):
                                update_data["segment"] = row["segment"]

                            if row.get("tags"):
                                update_data["tags"] = [t.strip() for t in row["tags"].split(",")]

                            db.clients.update_one(
                                {"_id": duplicate["_id"]},
                                {"$set": update_data}
                            )

                            results["updated"] += 1
                            continue
                        # else: create_new - fall through to create

                    # Create new client
                    client_data = {
                        "tenant_id": tenant_id,
                        "name": row["name"],
                        "phone": row["phone"],
                        "email": row.get("email", ""),
                        "address": row.get("address", ""),
                        "notes": row.get("notes", ""),
                        "segment": row.get("segment", "new"),
                        "tags": [t.strip() for t in row.get("tags", "").split(",")] if row.get("tags") else [],
                        "total_visits": 0,
                        "total_spent": 0,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }

                    # Parse optional fields
                    if row.get("birthday"):
                        client_data["birthday"] = datetime.fromisoformat(row["birthday"])

                    if row.get("preferred_stylist_id"):
                        client_data["preferred_stylist_id"] = row["preferred_stylist_id"]

                    db.clients.insert_one(client_data)
                    results["created"] += 1

                except Exception as e:
                    logger.error(f"Error importing row {row_number}: {e}")
                    results["failed"] += 1
                    results["errors"].append(f"Row {row_number}: {str(e)}")

        except Exception as e:
            logger.error(f"Error importing clients: {e}")
            results["errors"].append(f"Import error: {str(e)}")

        results["completed_at"] = datetime.now()
        return results

    def export_clients(
        self,
        tenant_id: str,
        client_ids: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export clients to CSV format
        
        Args:
            tenant_id: Tenant ID
            client_ids: Specific client IDs to export (if None, use filters)
            fields: Fields to include in export
            filters: Query filters to apply
            
        Returns:
            CSV string
            
        Requirements: REQ-CM-012
        """
        db = ClientImportExportService._get_db()
        # Default fields
        if fields is None:
            fields = [
                "id", "name", "phone", "email", "address", "birthday",
                "segment", "tags", "total_visits", "total_spent",
                "last_visit_date", "preferred_stylist_id", "notes"
            ]

        # Build query
        query = {"tenant_id": tenant_id}

        if client_ids:
            query["_id"] = {"$in": [ObjectId(cid) for cid in client_ids]}

        if filters:
            query.update(filters)

        # Get clients
        clients = list(db.clients.find(query))

        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)

        # Write header
        writer.writeheader()

        # Write rows
        for client in clients:
            row = {}
            for field in fields:
                if field == "id":
                    row[field] = str(client.get("_id", ""))
                elif field == "tags":
                    row[field] = ",".join(client.get(field, []))
                elif field == "total_spent":
                    row[field] = str(client.get(field, 0))
                else:
                    value = client.get(field, "")
                    if isinstance(value, datetime):
                        row[field] = value.isoformat()
                    else:
                        row[field] = str(value) if value else ""

            writer.writerow(row)

        return output.getvalue()


# Create singleton instance
client_import_export_service = ClientImportExportService()
