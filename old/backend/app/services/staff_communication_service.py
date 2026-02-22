from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo import DESCENDING
from app.database import db
from app.schemas.staff_management import StaffMessage, StaffAnnouncement, ShiftNote


class StaffCommunicationService:
    """Service for managing staff communication including messages, announcements, and shift notes."""

    @staticmethod
    async def send_message(
        sender_id: str,
        recipient_id: str,
        content: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Send a direct message between staff members."""
        message = {
            "sender_id": ObjectId(sender_id),
            "recipient_id": ObjectId(recipient_id),
            "content": content,
            "salon_id": ObjectId(salon_id),
            "read": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.staff_messages.insert_one(message)
        message["_id"] = result.inserted_id
        return message

    @staticmethod
    async def send_group_message(
        sender_id: str,
        recipient_ids: List[str],
        content: str,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Send a message to multiple staff members."""
        messages = []
        for recipient_id in recipient_ids:
            message = await StaffCommunicationService.send_message(
                sender_id, recipient_id, content, salon_id
            )
            messages.append(message)
        return messages

    @staticmethod
    async def mark_message_as_read(message_id: str) -> Dict[str, Any]:
        """Mark a message as read."""
        result = await db.staff_messages.find_one_and_update(
            {"_id": ObjectId(message_id)},
            {
                "$set": {
                    "read": True,
                    "updated_at": datetime.utcnow(),
                }
            },
            return_document=True,
        )
        return result

    @staticmethod
    async def get_messages(
        user_id: str,
        salon_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get messages for a user (sent and received)."""
        messages = await db.staff_messages.find(
            {
                "$or": [
                    {"sender_id": ObjectId(user_id)},
                    {"recipient_id": ObjectId(user_id)},
                ],
                "salon_id": ObjectId(salon_id),
                "created_at": {
                    "$gte": datetime.utcnow() - timedelta(days=90)
                },
            }
        ).sort("created_at", DESCENDING).skip(skip).limit(limit).to_list(None)
        return messages

    @staticmethod
    async def get_conversation(
        user_id: str,
        other_user_id: str,
        salon_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get conversation between two users."""
        messages = await db.staff_messages.find(
            {
                "$or": [
                    {
                        "sender_id": ObjectId(user_id),
                        "recipient_id": ObjectId(other_user_id),
                    },
                    {
                        "sender_id": ObjectId(other_user_id),
                        "recipient_id": ObjectId(user_id),
                    },
                ],
                "salon_id": ObjectId(salon_id),
                "created_at": {
                    "$gte": datetime.utcnow() - timedelta(days=90)
                },
            }
        ).sort("created_at", DESCENDING).skip(skip).limit(limit).to_list(None)
        return messages

    @staticmethod
    async def get_unread_count(user_id: str, salon_id: str) -> int:
        """Get count of unread messages for a user."""
        count = await db.staff_messages.count_documents(
            {
                "recipient_id": ObjectId(user_id),
                "salon_id": ObjectId(salon_id),
                "read": False,
            }
        )
        return count

    @staticmethod
    async def send_announcement(
        sender_id: str,
        title: str,
        content: str,
        salon_id: str,
        target_roles: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Send an announcement to all staff or specific roles."""
        announcement = {
            "sender_id": ObjectId(sender_id),
            "title": title,
            "content": content,
            "salon_id": ObjectId(salon_id),
            "target_roles": target_roles,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.staff_announcements.insert_one(announcement)
        announcement["_id"] = result.inserted_id
        return announcement

    @staticmethod
    async def get_announcements(
        salon_id: str,
        user_role: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get announcements for a salon."""
        query = {"salon_id": ObjectId(salon_id)}
        if user_role:
            query["$or"] = [
                {"target_roles": None},
                {"target_roles": user_role},
            ]

        announcements = await db.staff_announcements.find(query).sort(
            "created_at", DESCENDING
        ).skip(skip).limit(limit).to_list(None)
        return announcements

    @staticmethod
    async def create_shift_note(
        shift_id: str,
        author_id: str,
        content: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Create a shift handoff note."""
        note = {
            "shift_id": ObjectId(shift_id),
            "author_id": ObjectId(author_id),
            "content": content,
            "salon_id": ObjectId(salon_id),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.shift_notes.insert_one(note)
        note["_id"] = result.inserted_id
        return note

    @staticmethod
    async def get_shift_notes(
        shift_id: str,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all notes for a shift."""
        notes = await db.shift_notes.find(
            {
                "shift_id": ObjectId(shift_id),
                "salon_id": ObjectId(salon_id),
            }
        ).sort("created_at", DESCENDING).to_list(None)
        return notes

    @staticmethod
    async def cleanup_old_messages(days: int = 90) -> int:
        """Delete messages older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await db.staff_messages.delete_many(
            {"created_at": {"$lt": cutoff_date}}
        )
        return result.deleted_count
