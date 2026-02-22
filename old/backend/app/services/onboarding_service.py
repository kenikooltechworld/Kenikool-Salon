from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo import DESCENDING
from app.database import db


class OnboardingService:
    """Service for managing staff onboarding checklists and templates."""

    @staticmethod
    async def create_onboarding_template(
        salon_id: str,
        template_name: str,
        items: List[Dict[str, Any]],
        created_by: str,
    ) -> Dict[str, Any]:
        """Create an onboarding template."""
        template = {
            "salon_id": ObjectId(salon_id),
            "template_name": template_name,
            "items": items,
            "created_by": ObjectId(created_by),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.onboarding_templates.insert_one(template)
        template["_id"] = result.inserted_id
        return template

    @staticmethod
    async def get_onboarding_templates(salon_id: str) -> List[Dict[str, Any]]:
        """Get all onboarding templates for a salon."""
        templates = await db.onboarding_templates.find(
            {
                "salon_id": ObjectId(salon_id),
                "is_active": True,
            }
        ).sort("created_at", DESCENDING).to_list(None)
        return templates

    @staticmethod
    async def create_checklist_from_template(
        staff_id: str,
        template_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Create an onboarding checklist from a template."""
        template = await db.onboarding_templates.find_one(
            {
                "_id": ObjectId(template_id),
                "salon_id": ObjectId(salon_id),
            }
        )

        if not template:
            raise ValueError("Template not found")

        # Create checklist items from template
        checklist_items = []
        for item in template.get("items", []):
            checklist_items.append({
                "title": item.get("title"),
                "description": item.get("description"),
                "assigned_to": item.get("assigned_to", "manager"),
                "order": item.get("order", 0),
                "status": "pending",
                "completed_at": None,
                "completed_by": None,
                "notes": None,
            })

        checklist = {
            "staff_id": ObjectId(staff_id),
            "template_id": ObjectId(template_id),
            "salon_id": ObjectId(salon_id),
            "items": checklist_items,
            "progress_percentage": 0,
            "status": "in_progress",
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = await db.onboarding_checklists.insert_one(checklist)
        checklist["_id"] = result.inserted_id
        return checklist

    @staticmethod
    async def get_staff_checklist(
        staff_id: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get onboarding checklist for a staff member."""
        checklist = await db.onboarding_checklists.find_one(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        )
        return checklist

    @staticmethod
    async def update_checklist_item(
        checklist_id: str,
        item_index: int,
        status: str,
        notes: Optional[str] = None,
        completed_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a checklist item status."""
        checklist = await db.onboarding_checklists.find_one(
            {"_id": ObjectId(checklist_id)}
        )

        if not checklist:
            raise ValueError("Checklist not found")

        if item_index >= len(checklist["items"]):
            raise ValueError("Item index out of range")

        # Update item
        checklist["items"][item_index]["status"] = status
        if status == "completed":
            checklist["items"][item_index]["completed_at"] = datetime.utcnow()
            checklist["items"][item_index]["completed_by"] = completed_by
        checklist["items"][item_index]["notes"] = notes

        # Calculate progress
        completed_count = sum(
            1 for item in checklist["items"] if item["status"] == "completed"
        )
        total_count = len(checklist["items"])
        progress_percentage = int((completed_count / total_count) * 100) if total_count > 0 else 0

        # Update checklist
        update_data = {
            "items": checklist["items"],
            "progress_percentage": progress_percentage,
            "updated_at": datetime.utcnow(),
        }

        # Mark as completed if all items done
        if progress_percentage == 100:
            update_data["status"] = "completed"
            update_data["completed_at"] = datetime.utcnow()

        result = await db.onboarding_checklists.find_one_and_update(
            {"_id": ObjectId(checklist_id)},
            {"$set": update_data},
            return_document=True,
        )
        return result

    @staticmethod
    async def get_checklist_progress(
        staff_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Get progress summary for a staff member's onboarding."""
        checklist = await db.onboarding_checklists.find_one(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        )

        if not checklist:
            return {
                "has_checklist": False,
                "progress_percentage": 0,
                "status": "not_started",
            }

        items = checklist.get("items", [])
        completed = sum(1 for item in items if item["status"] == "completed")
        pending = sum(1 for item in items if item["status"] == "pending")
        in_progress = sum(1 for item in items if item["status"] == "in_progress")

        return {
            "has_checklist": True,
            "progress_percentage": checklist.get("progress_percentage", 0),
            "status": checklist.get("status", "in_progress"),
            "total_items": len(items),
            "completed_items": completed,
            "pending_items": pending,
            "in_progress_items": in_progress,
            "started_at": checklist.get("started_at"),
            "completed_at": checklist.get("completed_at"),
        }

    @staticmethod
    async def get_pending_items_by_assignee(
        salon_id: str,
        assigned_to: str,
    ) -> List[Dict[str, Any]]:
        """Get all pending onboarding items assigned to a person."""
        checklists = await db.onboarding_checklists.find(
            {
                "salon_id": ObjectId(salon_id),
                "status": {"$ne": "completed"},
            }
        ).to_list(None)

        pending_items = []
        for checklist in checklists:
            for idx, item in enumerate(checklist.get("items", [])):
                if (
                    item.get("assigned_to") == assigned_to
                    and item.get("status") != "completed"
                ):
                    pending_items.append({
                        "checklist_id": str(checklist["_id"]),
                        "staff_id": str(checklist["staff_id"]),
                        "item_index": idx,
                        "item": item,
                    })

        return pending_items

    @staticmethod
    async def get_onboarding_stats(salon_id: str) -> Dict[str, Any]:
        """Get onboarding statistics for a salon."""
        checklists = await db.onboarding_checklists.find(
            {"salon_id": ObjectId(salon_id)}
        ).to_list(None)

        total = len(checklists)
        completed = sum(1 for c in checklists if c.get("status") == "completed")
        in_progress = sum(1 for c in checklists if c.get("status") == "in_progress")
        not_started = sum(1 for c in checklists if c.get("status") == "not_started")

        avg_progress = (
            sum(c.get("progress_percentage", 0) for c in checklists) / total
            if total > 0
            else 0
        )

        return {
            "total_checklists": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "average_progress_percentage": int(avg_progress),
            "completion_rate": int((completed / total) * 100) if total > 0 else 0,
        }
