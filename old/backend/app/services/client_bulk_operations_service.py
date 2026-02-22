"""
Client Bulk Operations Service

Handles bulk operations on multiple clients:
- Bulk message sending (SMS/Email/WhatsApp)
- Bulk tag addition
- Bulk segment updates
- Bulk export

Requirements: REQ-CM-011
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from decimal import Decimal
import csv
import io
from bson import ObjectId

from app.database import Database
from app.services.communication_service import CommunicationService
from app.services.client_segmentation_service import client_segmentation_service

logger = logging.getLogger(__name__)


class ClientBulkOperationsService:
    """Service for bulk operations on clients"""

    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = Database.get_db()
        return self._db

    def send_bulk_message(
        self,
        tenant_id: str,
        client_ids: List[str],
        channel: str,
        content: str,
        subject: Optional[str] = None,
        message_type: str = "bulk"
    ) -> Dict[str, Any]:
        """
        Send message to multiple clients
        
        Args:
            tenant_id: Tenant ID
            client_ids: List of client IDs
            channel: Channel (sms, email, whatsapp)
            content: Message content
            subject: Email subject (for email channel)
            message_type: Type of message
            
        Returns:
            Dict with success/failure counts and details
            
        Requirements: REQ-CM-011
        """
        results = {
            "total": len(client_ids),
            "successful": 0,
            "failed": 0,
            "errors": [],
            "operation_id": str(ObjectId()),
            "started_at": datetime.now(),
            "completed_at": None
        }

        for client_id in client_ids:
            try:
                # Get client
                client = self.db.clients.find_one({
                    "_id": ObjectId(client_id),
                    "tenant_id": tenant_id
                })

                if not client:
                    results["failed"] += 1
                    results["errors"].append({
                        "client_id": client_id,
                        "error": "Client not found"
                    })
                    continue

                # Determine recipient
                if channel == "email":
                    if not client.get("email"):
                        results["failed"] += 1
                        results["errors"].append({
                            "client_id": client_id,
                            "error": "No email address"
                        })
                        continue
                    recipient = client["email"]
                else:  # sms or whatsapp
                    recipient = client.get("phone")
                    if not recipient:
                        results["failed"] += 1
                        results["errors"].append({
                            "client_id": client_id,
                            "error": "No phone number"
                        })
                        continue

                # Log communication
                communication = CommunicationService.log_communication(
                    client_id=client_id,
                    tenant_id=tenant_id,
                    channel=channel,
                    message_type=message_type,
                    content=content,
                    recipient=recipient,
                    subject=subject,
                    direction="outbound"
                )

                # Send message (integrate with existing services)
                try:
                    if channel == "sms":
                        from app.services.termii_service import send_sms
                        success = send_sms(recipient, content)
                        status = "sent" if success else "failed"
                    elif channel == "whatsapp":
                        from app.services.termii_service import send_whatsapp
                        success = send_whatsapp(recipient, content)
                        status = "sent" if success else "failed"
                    elif channel == "email":
                        from app.services.email_service import email_service
                        success = email_service.send_email(
                            to=recipient,
                            subject=subject or "Message from Salon",
                            html=f"<p>{content}</p>",
                            text=content
                        )
                        status = "sent" if success else "failed"
                    else:
                        status = "failed"
                        success = False

                    # Update communication status
                    CommunicationService.update_communication_status(
                        communication_id=str(communication["_id"]),
                        status=status,
                        error_message=None if success else "Failed to send"
                    )

                    if success:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append({
                            "client_id": client_id,
                            "error": "Failed to send message"
                        })

                except Exception as e:
                    logger.error(f"Error sending message to {client_id}: {e}")
                    results["failed"] += 1
                    results["errors"].append({
                        "client_id": client_id,
                        "error": str(e)
                    })
                    CommunicationService.update_communication_status(
                        communication_id=str(communication["_id"]),
                        status="failed",
                        error_message=str(e)
                    )

            except Exception as e:
                logger.error(f"Error processing client {client_id}: {e}")
                results["failed"] += 1
                results["errors"].append({
                    "client_id": client_id,
                    "error": str(e)
                })

        results["completed_at"] = datetime.now()
        return results

    def add_bulk_tags(
        self,
        tenant_id: str,
        client_ids: List[str],
        tags: List[str]
    ) -> Dict[str, Any]:
        """
        Add tags to multiple clients
        
        Args:
            tenant_id: Tenant ID
            client_ids: List of client IDs
            tags: Tags to add
            
        Returns:
            Dict with success/failure counts
            
        Requirements: REQ-CM-011
        """
        results = {
            "total": len(client_ids),
            "successful": 0,
            "failed": 0,
            "errors": [],
            "operation_id": str(ObjectId()),
            "started_at": datetime.now(),
            "completed_at": None
        }

        for client_id in client_ids:
            try:
                # Get client
                client = self.db.clients.find_one({
                    "_id": ObjectId(client_id),
                    "tenant_id": tenant_id
                })

                if not client:
                    results["failed"] += 1
                    results["errors"].append({
                        "client_id": client_id,
                        "error": "Client not found"
                    })
                    continue

                # Get existing tags
                existing_tags = client.get("tags", [])

                # Add new tags (avoid duplicates)
                updated_tags = list(set(existing_tags + tags))

                # Update client
                self.db.clients.update_one(
                    {"_id": ObjectId(client_id)},
                    {
                        "$set": {
                            "tags": updated_tags,
                            "updated_at": datetime.now()
                        }
                    }
                )

                results["successful"] += 1

            except Exception as e:
                logger.error(f"Error adding tags to {client_id}: {e}")
                results["failed"] += 1
                results["errors"].append({
                    "client_id": client_id,
                    "error": str(e)
                })

        results["completed_at"] = datetime.now()
        return results

    def update_bulk_segments(
        self,
        tenant_id: str,
        client_ids: List[str],
        segment: str
    ) -> Dict[str, Any]:
        """
        Update segment for multiple clients
        
        Args:
            tenant_id: Tenant ID
            client_ids: List of client IDs
            segment: Segment to assign (new, regular, vip, inactive)
            
        Returns:
            Dict with success/failure counts
            
        Requirements: REQ-CM-011
        """
        # Validate segment
        valid_segments = ["new", "regular", "vip", "inactive"]
        if segment not in valid_segments:
            return {
                "error": f"Invalid segment. Must be one of: {', '.join(valid_segments)}"
            }

        results = {
            "total": len(client_ids),
            "successful": 0,
            "failed": 0,
            "errors": [],
            "operation_id": str(ObjectId()),
            "started_at": datetime.now(),
            "completed_at": None
        }

        for client_id in client_ids:
            try:
                # Get client
                client = self.db.clients.find_one({
                    "_id": ObjectId(client_id),
                    "tenant_id": tenant_id
                })

                if not client:
                    results["failed"] += 1
                    results["errors"].append({
                        "client_id": client_id,
                        "error": "Client not found"
                    })
                    continue

                # Update segment
                self.db.clients.update_one(
                    {"_id": ObjectId(client_id)},
                    {
                        "$set": {
                            "segment": segment,
                            "updated_at": datetime.now()
                        }
                    }
                )

                results["successful"] += 1

            except Exception as e:
                logger.error(f"Error updating segment for {client_id}: {e}")
                results["failed"] += 1
                results["errors"].append({
                    "client_id": client_id,
                    "error": str(e)
                })

        results["completed_at"] = datetime.now()
        return results

    def export_clients_to_csv(
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
        clients = list(self.db.clients.find(query))

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

    def get_bulk_operation_status(
        self,
        tenant_id: str,
        operation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get status of a bulk operation
        
        Args:
            tenant_id: Tenant ID
            operation_id: Operation ID
            
        Returns:
            Operation status or None if not found
        """
        operation = self.db.bulk_operations.find_one({
            "_id": ObjectId(operation_id),
            "tenant_id": tenant_id
        })

        if operation:
            operation["id"] = str(operation.pop("_id"))

        return operation


# Create singleton instance
client_bulk_operations_service = ClientBulkOperationsService()
