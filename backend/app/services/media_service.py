"""
Media upload service for handling Cloudinary uploads
"""
import base64
import io
import logging
from typing import Optional

try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False

from app.context import get_tenant_id
from app.config import settings

logger = logging.getLogger(__name__)

_cloudinary_configured = False


class MediaUploadError(Exception):
    """Raised when media upload fails"""
    pass


def configure_cloudinary():
    """Configure Cloudinary with credentials from settings"""
    global _cloudinary_configured
    
    if _cloudinary_configured:
        return
    
    if not CLOUDINARY_AVAILABLE:
        raise MediaUploadError("Cloudinary is not installed. Install it with: pip install cloudinary")
    
    cloud_name = settings.cloudinary_cloud_name
    api_key = settings.cloudinary_api_key
    api_secret = settings.cloudinary_api_secret
    
    if not all([cloud_name, api_key, api_secret]):
        raise MediaUploadError(
            f"Missing Cloudinary credentials. "
            f"cloud_name={bool(cloud_name)}, api_key={bool(api_key)}, api_secret={bool(api_secret)}"
        )
    
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
    )
    
    _cloudinary_configured = True
    logger.info("Cloudinary configured successfully")


def upload_media(
    base64_data: str,
    media_type: str = "image",
    folder: str = "salon-media",
) -> str:
    """
    Upload media to Cloudinary
    
    Args:
        base64_data: Base64 encoded file data
        media_type: Type of media (image, video, etc.)
        folder: Cloudinary folder path
        
    Returns:
        Secure URL of uploaded media
        
    Raises:
        MediaUploadError: If upload fails
    """
    try:
        if not CLOUDINARY_AVAILABLE:
            raise MediaUploadError("Cloudinary is not installed")
        
        # Configure Cloudinary on first use
        configure_cloudinary()
        
        # Get tenant ID for folder organization
        tenant_id = get_tenant_id()
        if tenant_id:
            folder = f"{folder}/{tenant_id}"
        
        # Decode base64 data
        try:
            # Handle data URI format (data:image/png;base64,...)
            if "," in base64_data:
                base64_data = base64_data.split(",")[1]
            
            file_data = base64.b64decode(base64_data)
        except Exception as e:
            raise MediaUploadError(f"Invalid base64 data: {str(e)}")
        
        # Create file-like object
        file_obj = io.BytesIO(file_data)
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_obj,
            folder=folder,
            resource_type="auto",
            quality="auto",
            fetch_format="auto",
        )
        
        return result.get("secure_url")
        
    except cloudinary.exceptions.Error as e:
        raise MediaUploadError(f"Cloudinary upload failed: {str(e)}")
    except Exception as e:
        raise MediaUploadError(f"Media upload error: {str(e)}")
