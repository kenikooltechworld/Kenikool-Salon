from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.database import db


class EmergencyContactService:
    """Service for managing emergency contact information for staff."""

    @staticmethod
    async def add_emergency_contact(
        staff_id: str,
        salon_id: str,
        name: str,
        relationship: str,
        phone: str,
        email: Optional[str] = None,
        is_primary: bool = False,
    ) -> Dict[str, Any]:
        """Add an emergency contact for a staff member."""
        contact = {
            "name": name,
            "relationship": relationship,
            "phone": phone,
            "email": email,
            "is_primary": is_primary,
            "added_at": datetime.utcnow(),
        }

        # If this is primary, unset other primary contacts
        if is_primary:
            await db.stylists.update_one(
                {
                    "_id": ObjectId(staff_id),
                    "salon_id": ObjectId(salon_id),
                },
                {"$set": {"emergency_contacts.$[].is_primary": False}},
            )

        # Add the new contact
        result = await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$push": {"emergency_contacts": contact},
            },
        )

        if result.matched_count == 0:
            raise ValueError("Staff member not found")

        return contact

    @staticmethod
    async def get_emergency_contacts(
        staff_id: str,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all emergency contacts for a staff member."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"emergency_contacts": 1},
        )

        if not staff:
            raise ValueError("Staff member not found")

        return staff.get("emergency_contacts", [])

    @staticmethod
    async def update_emergency_contact(
        staff_id: str,
        salon_id: str,
        contact_index: int,
        name: Optional[str] = None,
        relationship: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        is_primary: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update an emergency contact."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        )

        if not staff:
            raise ValueError("Staff member not found")

        contacts = staff.get("emergency_contacts", [])
        if contact_index >= len(contacts):
            raise ValueError("Contact not found")

        # Update contact fields
        if name:
            contacts[contact_index]["name"] = name
        if relationship:
            contacts[contact_index]["relationship"] = relationship
        if phone:
            contacts[contact_index]["phone"] = phone
        if email is not None:
            contacts[contact_index]["email"] = email
        if is_primary is not None:
            if is_primary:
                # Unset other primary contacts
                for contact in contacts:
                    contact["is_primary"] = False
            contacts[contact_index]["is_primary"] = is_primary

        # Update in database
        await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"$set": {"emergency_contacts": contacts}},
        )

        return contacts[contact_index]

    @staticmethod
    async def delete_emergency_contact(
        staff_id: str,
        salon_id: str,
        contact_index: int,
    ) -> bool:
        """Delete an emergency contact."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        )

        if not staff:
            raise ValueError("Staff member not found")

        contacts = staff.get("emergency_contacts", [])
        if contact_index >= len(contacts):
            raise ValueError("Contact not found")

        contacts.pop(contact_index)

        await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"$set": {"emergency_contacts": contacts}},
        )

        return True

    @staticmethod
    async def add_medical_info(
        staff_id: str,
        salon_id: str,
        allergies: Optional[str] = None,
        conditions: Optional[str] = None,
        insurance_provider: Optional[str] = None,
        insurance_policy_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add or update medical information for a staff member."""
        medical_info = {
            "allergies": allergies,
            "conditions": conditions,
            "insurance_provider": insurance_provider,
            "insurance_policy_number": insurance_policy_number,
            "updated_at": datetime.utcnow(),
        }

        result = await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"$set": {"medical_info": medical_info}},
        )

        if result.matched_count == 0:
            raise ValueError("Staff member not found")

        return medical_info

    @staticmethod
    async def get_medical_info(
        staff_id: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get medical information for a staff member."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"medical_info": 1},
        )

        if not staff:
            raise ValueError("Staff member not found")

        return staff.get("medical_info")

    @staticmethod
    async def get_emergency_info_summary(
        staff_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Get complete emergency information summary."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "emergency_contacts": 1,
                "medical_info": 1,
                "name": 1,
            },
        )

        if not staff:
            raise ValueError("Staff member not found")

        primary_contact = None
        contacts = staff.get("emergency_contacts", [])
        for contact in contacts:
            if contact.get("is_primary"):
                primary_contact = contact
                break

        return {
            "staff_id": str(staff["_id"]),
            "staff_name": staff.get("name"),
            "primary_contact": primary_contact,
            "all_contacts": contacts,
            "medical_info": staff.get("medical_info"),
            "total_contacts": len(contacts),
        }
