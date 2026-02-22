from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import json

from app.schemas.branding_version import (
    BrandingVersion,
    BrandingVersionSnapshot,
    BrandingVersionDiff,
    BrandingVersionCreate,
)
from app.schemas.white_label import WhiteLabelConfig


class BrandingVersionService:
    """Service for managing branding configuration versions"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.branding_versions
        self.max_versions = 10  # Store last 10 versions per tenant

    async def create_version(
        self,
        tenant_id: str,
        config: WhiteLabelConfig,
        change_description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> BrandingVersion:
        """Create a new version snapshot of the current branding configuration"""
        
        # Create snapshot from current config
        snapshot = BrandingVersionSnapshot(
            branding=config.branding.model_dump(),
            domain=config.domain.model_dump(),
            features=config.features.model_dump(),
            is_active=config.is_active,
        )

        # Get next version number
        version_number = await self._get_next_version_number(tenant_id)

        # Create version document
        version_doc = {
            "tenant_id": tenant_id,
            "version_number": version_number,
            "snapshot": snapshot.model_dump(),
            "created_at": datetime.utcnow(),
            "created_by": created_by,
            "change_description": change_description,
            "is_current": True,  # Mark as current
        }

        # Insert version
        result = await self.collection.insert_one(version_doc)
        version_doc["_id"] = str(result.inserted_id)

        # Mark previous version as not current
        await self.collection.update_many(
            {
                "tenant_id": tenant_id,
                "_id": {"$ne": result.inserted_id},
            },
            {"$set": {"is_current": False}},
        )

        # Clean up old versions (keep only last 10)
        await self._cleanup_old_versions(tenant_id)

        return BrandingVersion(**version_doc)

    async def get_version(
        self, tenant_id: str, version_number: int
    ) -> Optional[BrandingVersion]:
        """Get a specific version by version number"""
        version_doc = await self.collection.find_one(
            {"tenant_id": tenant_id, "version_number": version_number}
        )
        if version_doc:
            version_doc["_id"] = str(version_doc["_id"])
            return BrandingVersion(**version_doc)
        return None

    async def get_current_version(self, tenant_id: str) -> Optional[BrandingVersion]:
        """Get the current active version"""
        version_doc = await self.collection.find_one(
            {"tenant_id": tenant_id, "is_current": True},
            sort=[("version_number", -1)],
        )
        if version_doc:
            version_doc["_id"] = str(version_doc["_id"])
            return BrandingVersion(**version_doc)
        return None

    async def list_versions(
        self, tenant_id: str, skip: int = 0, limit: int = 100
    ) -> tuple[List[BrandingVersion], int]:
        """List all versions for a tenant"""
        # Get total count
        total = await self.collection.count_documents({"tenant_id": tenant_id})

        # Get versions sorted by version number descending
        cursor = self.collection.find({"tenant_id": tenant_id}).sort(
            "version_number", -1
        ).skip(skip).limit(limit)

        versions = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            versions.append(BrandingVersion(**doc))

        return versions, total

    async def get_version_diff(
        self, tenant_id: str, from_version: int, to_version: int
    ) -> Optional[BrandingVersionDiff]:
        """Get differences between two versions"""
        from_v = await self.get_version(tenant_id, from_version)
        to_v = await self.get_version(tenant_id, to_version)

        if not from_v or not to_v:
            return None

        # Compare snapshots
        from_snapshot = from_v.snapshot
        to_snapshot = to_v.snapshot

        changes = {}
        added_fields = {}
        removed_fields = {}
        modified_fields = {}

        # Compare each section
        for section in ["branding", "domain", "features"]:
            from_section = getattr(from_snapshot, section)
            to_section = getattr(to_snapshot, section)

            section_changes = {}

            # Check for added and modified fields
            for key, to_value in to_section.items():
                if key not in from_section:
                    added_fields[f"{section}.{key}"] = to_value
                elif from_section[key] != to_value:
                    modified_fields[f"{section}.{key}"] = {
                        "old": from_section[key],
                        "new": to_value,
                    }
                    section_changes[key] = to_value

            # Check for removed fields
            for key, from_value in from_section.items():
                if key not in to_section:
                    removed_fields[f"{section}.{key}"] = from_value

            if section_changes:
                changes[section] = section_changes

        return BrandingVersionDiff(
            from_version=from_version,
            to_version=to_version,
            changes=changes,
            added_fields=added_fields,
            removed_fields=removed_fields,
            modified_fields=modified_fields,
        )

    async def rollback_to_version(
        self,
        tenant_id: str,
        version_number: int,
        created_by: Optional[str] = None,
    ) -> Optional[BrandingVersion]:
        """Rollback to a previous version"""
        version = await self.get_version(tenant_id, version_number)
        if not version:
            return None

        # Create a new version with the rolled-back configuration
        new_version = await self.create_version(
            tenant_id=tenant_id,
            config=self._snapshot_to_config(tenant_id, version.snapshot),
            change_description=f"Rolled back to version {version_number}",
            created_by=created_by,
        )

        return new_version

    async def delete_version(self, tenant_id: str, version_number: int) -> bool:
        """Delete a specific version (cannot delete current version)"""
        version = await self.get_version(tenant_id, version_number)
        if not version:
            return False

        # Cannot delete current version
        if version.is_current:
            raise ValueError("Cannot delete the current active version")

        result = await self.collection.delete_one(
            {"tenant_id": tenant_id, "version_number": version_number}
        )
        return result.deleted_count > 0

    async def _get_next_version_number(self, tenant_id: str) -> int:
        """Get the next version number for a tenant"""
        latest = await self.collection.find_one(
            {"tenant_id": tenant_id},
            sort=[("version_number", -1)],
        )
        if latest:
            return latest["version_number"] + 1
        return 1

    async def _cleanup_old_versions(self, tenant_id: str) -> None:
        """Keep only the last max_versions versions"""
        # Get all versions sorted by version number
        versions = await self.collection.find(
            {"tenant_id": tenant_id}
        ).sort("version_number", -1).to_list(None)

        # If we have more than max_versions, delete the oldest ones
        if len(versions) > self.max_versions:
            versions_to_delete = versions[self.max_versions :]
            version_numbers_to_delete = [v["version_number"] for v in versions_to_delete]

            await self.collection.delete_many(
                {
                    "tenant_id": tenant_id,
                    "version_number": {"$in": version_numbers_to_delete},
                }
            )

    def _snapshot_to_config(
        self, tenant_id: str, snapshot: BrandingVersionSnapshot
    ) -> WhiteLabelConfig:
        """Convert a snapshot back to a WhiteLabelConfig object"""
        from app.schemas.white_label import (
            WhiteLabelBranding,
            WhiteLabelDomain,
            WhiteLabelFeatures,
        )

        return WhiteLabelConfig(
            id="temp",  # Temporary ID
            tenant_id=tenant_id,
            branding=WhiteLabelBranding(**snapshot.branding),
            domain=WhiteLabelDomain(**snapshot.domain),
            features=WhiteLabelFeatures(**snapshot.features),
            is_active=snapshot.is_active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    async def get_version_count(self, tenant_id: str) -> int:
        """Get total number of versions for a tenant"""
        return await self.collection.count_documents({"tenant_id": tenant_id})

    async def export_version(self, tenant_id: str, version_number: int) -> Optional[Dict[str, Any]]:
        """Export a version as JSON"""
        version = await self.get_version(tenant_id, version_number)
        if not version:
            return None

        return {
            "version_number": version.version_number,
            "created_at": version.created_at.isoformat(),
            "created_by": version.created_by,
            "change_description": version.change_description,
            "snapshot": version.snapshot.model_dump(),
        }

    async def import_version(
        self,
        tenant_id: str,
        version_data: Dict[str, Any],
        created_by: Optional[str] = None,
    ) -> Optional[BrandingVersion]:
        """Import a version from JSON"""
        try:
            snapshot = BrandingVersionSnapshot(**version_data.get("snapshot", {}))
            
            # Create a temporary config from snapshot
            config = self._snapshot_to_config(tenant_id, snapshot)
            
            # Create new version
            new_version = await self.create_version(
                tenant_id=tenant_id,
                config=config,
                change_description=f"Imported from external version: {version_data.get('change_description', '')}",
                created_by=created_by,
            )
            
            return new_version
        except Exception as e:
            raise ValueError(f"Failed to import version: {str(e)}")
