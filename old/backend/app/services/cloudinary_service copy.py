"""
Cloudinary service for file uploads
"""
import cloudinary
import cloudinary.uploader
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


async def upload_image(file_data: bytes, folder: str, public_id: str = None) -> str:
    """
    Upload image to Cloudinary
    Returns the secure URL of the uploaded image
    """
    try:
        result = cloudinary.uploader.upload(
            file_data,
            folder=folder,
            public_id=public_id,
            overwrite=True,
            resource_type="image"
        )
        return result.get("secure_url")
    except Exception as e:
        logger.error(f"Cloudinary upload error: {e}")
        raise Exception(f"Failed to upload image: {str(e)}")


async def delete_image(public_id: str) -> bool:
    """
    Delete image from Cloudinary
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        logger.error(f"Cloudinary delete error: {e}")
        return False
