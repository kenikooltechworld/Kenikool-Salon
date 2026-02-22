"""Gift card bulk operations service for creating multiple cards from CSV."""
import csv
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from bson import ObjectId
from app.database import db
from app.services.gift_card_service import GiftCardService
from app.services.email_service import EmailService
from app.tasks.gift_card_tasks import send_gift_card_email_task


class GiftCardBulkOperationsService:
    """Service for bulk gift card operations."""

    @staticmethod
    def parse_csv(csv_content: str) -> Tuple[List[Dict], List[str]]:
        """Parse CSV content and return cards data and errors."""
        errors = []
        cards_data = []
        
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            if not reader.fieldnames:
                errors.append("CSV file is empty")
                return [], errors
            
            required_fields = {"amount", "recipient_email", "recipient_name"}
            missing_fields = required_fields - set(reader.fieldnames or [])
            if missing_fields:
                errors.append(f"Missing required fields: {', '.join(missing_fields)}")
                return [], errors
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    amount = float(row.get("amount", "").strip())
                    if amount <= 0:
                        errors.append(f"Row {row_num}: Amount must be positive")
                        continue
                    
                    recipient_email = row.get("recipient_email", "").strip()
                    if not recipient_email or "@" not in recipient_email:
                        errors.append(f"Row {row_num}: Invalid email address")
                        continue
                    
                    recipient_name = row.get("recipient_name", "").strip()
                    if not recipient_name:
                        errors.append(f"Row {row_num}: Recipient name is required")
                        continue
                    
                    cards_data.append({
                        "amount": amount,
                        "recipient_email": recipient_email,
                        "recipient_name": recipient_name,
                        "message": row.get("message", "").strip() or None,
                        "card_type": "digital"
                    })
                except ValueError as e:
                    errors.append(f"Row {row_num}: Invalid amount format")
                    continue
        
        except Exception as e:
            errors.append(f"CSV parsing error: {str(e)}")
        
        return cards_data, errors

    @staticmethod
    async def bulk_create(
        tenant_id: str,
        csv_content: str,
        created_by: str,
        design_theme: str = "default",
        expiration_months: int = 12
    ) -> Dict:
        """Create multiple gift cards from CSV data."""
        cards_data, parse_errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        if parse_errors:
            return {
                "success": False,
                "errors": parse_errors,
                "created_count": 0,
                "failed_count": 0
            }
        
        if not cards_data:
            return {
                "success": False,
                "errors": ["No valid cards found in CSV"],
                "created_count": 0,
                "failed_count": 0
            }
        
        # Limit to 100 cards per batch
        if len(cards_data) > 100:
            return {
                "success": False,
                "errors": ["Maximum 100 cards per batch allowed"],
                "created_count": 0,
                "failed_count": len(cards_data)
            }
        
        created_count = 0
        failed_count = 0
        created_cards = []
        
        for card_data in cards_data:
            try:
                card = await GiftCardService.create_gift_card(
                    tenant_id=tenant_id,
                    amount=card_data["amount"],
                    card_type=card_data["card_type"],
                    recipient_email=card_data["recipient_email"],
                    recipient_name=card_data["recipient_name"],
                    message=card_data.get("message"),
                    design_theme=design_theme,
                    created_by=created_by,
                    expiration_months=expiration_months
                )
                created_cards.append(card)
                created_count += 1
                
                # Queue email delivery
                send_gift_card_email_task.delay(str(card["_id"]))
            
            except Exception as e:
                failed_count += 1
        
        return {
            "success": created_count > 0,
            "created_count": created_count,
            "failed_count": failed_count,
            "total": len(cards_data),
            "cards": created_cards
        }

    @staticmethod
    def get_bulk_progress(tenant_id: str, batch_id: str) -> Dict:
        """Get progress of a bulk operation."""
        batch = db.gift_card_batches.find_one({
            "_id": ObjectId(batch_id),
            "tenant_id": tenant_id
        })
        
        if not batch:
            return {"error": "Batch not found"}
        
        return {
            "batch_id": str(batch["_id"]),
            "status": batch.get("status"),
            "total": batch.get("total", 0),
            "processed": batch.get("processed", 0),
            "created": batch.get("created", 0),
            "failed": batch.get("failed", 0),
            "progress_percent": int((batch.get("processed", 0) / batch.get("total", 1)) * 100),
            "created_at": batch.get("created_at"),
            "completed_at": batch.get("completed_at")
        }
