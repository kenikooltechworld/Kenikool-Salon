"""
Location image service for handling image uploads, processing, and optimization.
Handles image validation, resizing, format conversion, and storage.
"""

import io
import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from PIL import Image
except ImportError:
    Image = None

logger = logging.getLogger(__name__)


class LocationImageException(Exception):
    """Exception raised for image processing errors"""
    pass


class LocationImageService:
    """Service for managing location images"""

    # Configuration constants
    MAX_IMAGES_PER_LOCATION = 10
    ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
    ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1080
    THUMBNAIL_WIDTH = 400
    THUMBNAIL_HEIGHT = 300
    WEBP_QUALITY = 85

    def __init__(self):
        """Initialize image service"""
        if Image is None:
            raise LocationImageException(
                "Pillow library is required for image processing. "
                "Install it with: pip install Pillow"
            )

    async def validate_image_file(
        self, file_content: bytes, content_type: str
    ) -> Dict[str, Any]:
        """
        Validate image file for size, type, and format.

        Args:
            file_content: Raw file bytes
            content_type: MIME type of the file

        Returns:
            Dictionary with validation results

        Raises:
            LocationImageException: If validation fails
        """
        # Check MIME type
        if content_type not in self.ALLOWED_MIME_TYPES:
            raise LocationImageException(
                f"Invalid image format. Allowed formats: JPEG, PNG, WebP"
            )

        # Check file size
        if len(file_content) > self.MAX_FILE_SIZE:
            raise LocationImageException(
                f"File size exceeds maximum of {self.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
            )

        # Validate image can be opened
        try:
            image = Image.open(io.BytesIO(file_content))
            image.verify()
            
            # Reopen after verify (verify closes the file)
            image = Image.open(io.BytesIO(file_content))
            
            # Check image format
            if image.format not in self.ALLOWED_FORMATS:
                raise LocationImageException(
                    f"Invalid image format: {image.format}. "
                    f"Allowed formats: {', '.join(self.ALLOWED_FORMATS)}"
                )

            return {
                "valid": True,
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "size": len(file_content),
            }
        except Image.UnidentifiedImageError:
            raise LocationImageException("File is not a valid image")
        except Exception as e:
            logger.error(f"Image validation error: {e}")
            raise LocationImageException(f"Image validation failed: {str(e)}")

    async def process_image(
        self, file_content: bytes, content_type: str
    ) -> Dict[str, Any]:
        """
        Process image: resize, optimize, and convert to WebP.

        Args:
            file_content: Raw file bytes
            content_type: MIME type of the file

        Returns:
            Dictionary with processed image data

        Raises:
            LocationImageException: If processing fails
        """
        try:
            # Validate first
            validation = await self.validate_image_file(file_content, content_type)
            if not validation["valid"]:
                raise LocationImageException("Image validation failed")

            # Open image
            image = Image.open(io.BytesIO(file_content))

            # Convert RGBA to RGB if necessary (for JPEG compatibility)
            if image.mode in ("RGBA", "LA", "P"):
                # Create white background
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
                image = background

            # Resize if necessary
            if image.width > self.MAX_WIDTH or image.height > self.MAX_HEIGHT:
                image.thumbnail(
                    (self.MAX_WIDTH, self.MAX_HEIGHT),
                    Image.Resampling.LANCZOS
                )
                logger.info(f"Resized image to {image.width}x{image.height}")

            # Convert to WebP for optimization
            output = io.BytesIO()
            image.save(
                output,
                format="WEBP",
                quality=self.WEBP_QUALITY,
                method=6  # Slower but better compression
            )
            output.seek(0)
            processed_content = output.getvalue()

            # Generate thumbnail
            thumbnail = image.copy()
            thumbnail.thumbnail(
                (self.THUMBNAIL_WIDTH, self.THUMBNAIL_HEIGHT),
                Image.Resampling.LANCZOS
            )
            thumbnail_output = io.BytesIO()
            thumbnail.save(
                thumbnail_output,
                format="WEBP",
                quality=self.WEBP_QUALITY,
                method=6
            )
            thumbnail_output.seek(0)
            thumbnail_content = thumbnail_output.getvalue()

            logger.info(
                f"Processed image: {len(file_content)} bytes -> "
                f"{len(processed_content)} bytes (WebP), "
                f"thumbnail: {len(thumbnail_content)} bytes"
            )

            return {
                "original_size": len(file_content),
                "processed_size": len(processed_content),
                "thumbnail_size": len(thumbnail_content),
                "width": image.width,
                "height": image.height,
                "format": "WEBP",
                "content": processed_content,
                "thumbnail_content": thumbnail_content,
                "compression_ratio": len(processed_content) / len(file_content),
            }

        except LocationImageException:
            raise
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise LocationImageException(f"Image processing failed: {str(e)}")

    async def generate_image_id(self) -> str:
        """
        Generate unique image ID.

        Returns:
            Unique image ID
        """
        return str(uuid.uuid4())

    async def create_image_metadata(
        self,
        image_id: str,
        url: str,
        thumbnail_url: Optional[str] = None,
        is_primary: bool = False,
    ) -> Dict[str, Any]:
        """
        Create image metadata document.

        Args:
            image_id: Unique image ID
            url: Image URL
            thumbnail_url: Thumbnail URL
            is_primary: Whether this is the primary image

        Returns:
            Image metadata dictionary
        """
        return {
            "id": image_id,
            "url": url,
            "thumbnail_url": thumbnail_url,
            "is_primary": is_primary,
            "uploaded_at": datetime.utcnow(),
        }

    def get_image_stats(self) -> Dict[str, Any]:
        """
        Get image service statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "max_images_per_location": self.MAX_IMAGES_PER_LOCATION,
            "allowed_formats": list(self.ALLOWED_FORMATS),
            "max_file_size_mb": self.MAX_FILE_SIZE / 1024 / 1024,
            "max_dimensions": f"{self.MAX_WIDTH}x{self.MAX_HEIGHT}",
            "thumbnail_dimensions": f"{self.THUMBNAIL_WIDTH}x{self.THUMBNAIL_HEIGHT}",
            "webp_quality": self.WEBP_QUALITY,
        }
