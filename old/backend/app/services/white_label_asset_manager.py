"""Asset Manager Service for White Label System"""
import os
import io
from typing import Optional, Dict, Tuple
from datetime import datetime
from pathlib import Path
import hashlib

from fastapi import UploadFile
from PIL import Image
import minio
from minio.error import S3Error

from app.config import settings


class AssetManagerService:
    """Handles logo and favicon uploads with validation and optimization"""

    ALLOWED_TYPES = {"image/png", "image/jpeg", "image/svg+xml"}
    ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg"}
    LOGO_MAX_SIZE = 5 * 1024 * 1024  # 5MB
    FAVICON_MAX_SIZE = 1 * 1024 * 1024  # 1MB
    FAVICON_SIZES = {(16, 16), (32, 32), (64, 64)}

    def __init__(self):
        """Initialize MinIO client"""
        self.client = minio.Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    async def upload_asset(
        self,
        tenant_id: str,
        file: UploadFile,
        asset_type: str,
    ) -> Dict:
        """
        Upload and validate an asset (logo or favicon)

        Args:
            tenant_id: Tenant identifier
            file: Uploaded file
            asset_type: "logo" or "favicon"

        Returns:
            Dict with asset metadata and URL
        """
        # Validate asset type
        if asset_type not in ["logo", "favicon"]:
            raise ValueError("asset_type must be 'logo' or 'favicon'")

        # Read file content
        content = await file.read()

        # Validate file
        validation_result = await self.validate_image(file, asset_type)
        if not validation_result["valid"]:
            raise ValueError(validation_result["error"])

        # Optimize image
        optimized_content = await self.optimize_image(content, asset_type)

        # Generate filename
        file_hash = hashlib.md5(optimized_content).hexdigest()
        ext = Path(file.filename).suffix.lower()
        filename = f"{asset_type}_{file_hash}{ext}"

        # Store in MinIO
        object_name = f"white-label/{tenant_id}/{asset_type}/{filename}"

        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(optimized_content),
                len(optimized_content),
                content_type=file.content_type,
            )
        except S3Error as e:
            raise RuntimeError(f"Failed to upload asset: {str(e)}")

        # Generate secure URL
        asset_url = self._generate_asset_url(object_name)

        # Get image dimensions
        img = Image.open(io.BytesIO(optimized_content))
        dimensions = {"width": img.width, "height": img.height}

        return {
            "asset_url": asset_url,
            "asset_type": asset_type,
            "file_size": len(optimized_content),
            "dimensions": dimensions,
            "uploaded_at": datetime.utcnow().isoformat(),
            "object_name": object_name,
        }

    async def validate_image(
        self,
        file: UploadFile,
        asset_type: str,
    ) -> Dict:
        """
        Validate image file

        Args:
            file: Uploaded file
            asset_type: "logo" or "favicon"

        Returns:
            Dict with validation result
        """
        # Check file extension
        ext = Path(file.filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            return {
                "valid": False,
                "error": f"Invalid file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}",
            }

        # Check content type
        if file.content_type not in self.ALLOWED_TYPES:
            return {
                "valid": False,
                "error": f"Invalid content type. Allowed: {', '.join(self.ALLOWED_TYPES)}",
            }

        # Read and validate image
        content = await file.read()
        await file.seek(0)  # Reset file pointer

        # Check file size
        max_size = self.FAVICON_MAX_SIZE if asset_type == "favicon" else self.LOGO_MAX_SIZE
        if len(content) > max_size:
            return {
                "valid": False,
                "error": f"File too large. Maximum size: {max_size / 1024 / 1024}MB",
            }

        # Validate image format
        try:
            img = Image.open(io.BytesIO(content))
            img.verify()
        except Exception as e:
            return {"valid": False, "error": f"Invalid image file: {str(e)}"}

        # For favicon, validate dimensions
        if asset_type == "favicon":
            img = Image.open(io.BytesIO(content))
            if (img.width, img.height) not in self.FAVICON_SIZES:
                return {
                    "valid": False,
                    "error": f"Favicon dimensions must be one of: {self.FAVICON_SIZES}",
                }

        return {"valid": True}

    async def optimize_image(
        self,
        content: bytes,
        asset_type: str,
    ) -> bytes:
        """
        Optimize image for web display

        Args:
            content: Image file content
            asset_type: "logo" or "favicon"

        Returns:
            Optimized image content
        """
        try:
            img = Image.open(io.BytesIO(content))

            # Convert RGBA to RGB if needed
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background

            # Resize if needed
            if asset_type == "logo":
                # Max width 500px for logos
                if img.width > 500:
                    ratio = 500 / img.width
                    new_size = (500, int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Save optimized image
            output = io.BytesIO()
            format_map = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".svg": "SVG"}
            file_ext = Path(content).suffix.lower() if isinstance(content, str) else ".png"

            # For SVG, return as-is
            if file_ext == ".svg":
                return content

            img.save(output, format="PNG" if file_ext == ".png" else "JPEG", quality=85)
            return output.getvalue()

        except Exception as e:
            # If optimization fails, return original
            return content

    async def delete_asset(
        self,
        tenant_id: str,
        asset_url: str,
    ) -> bool:
        """
        Delete an asset

        Args:
            tenant_id: Tenant identifier
            asset_url: Asset URL

        Returns:
            True if deleted successfully
        """
        try:
            # Extract object name from URL
            object_name = f"white-label/{tenant_id}/{asset_url.split('/')[-1]}"
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            raise RuntimeError(f"Failed to delete asset: {str(e)}")

    async def get_asset_url(
        self,
        tenant_id: str,
        asset_type: str,
    ) -> Optional[str]:
        """
        Get URL for an asset type

        Args:
            tenant_id: Tenant identifier
            asset_type: "logo" or "favicon"

        Returns:
            Asset URL or None if not found
        """
        try:
            prefix = f"white-label/{tenant_id}/{asset_type}/"
            objects = self.client.list_objects(self.bucket_name, prefix=prefix)

            for obj in objects:
                return self._generate_asset_url(obj.object_name)

            return None
        except S3Error:
            return None

    def _generate_asset_url(self, object_name: str) -> str:
        """Generate secure URL for asset"""
        try:
            url = self.client.get_presigned_download_link(
                self.bucket_name,
                object_name,
                expires=3600 * 24 * 7,  # 7 days
            )
            return url
        except S3Error:
            # Fallback to direct URL
            return f"{settings.MINIO_ENDPOINT}/{self.bucket_name}/{object_name}"
