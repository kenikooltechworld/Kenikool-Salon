"""
Media upload endpoints
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.media_service import upload_media, MediaUploadError
from app.decorators.tenant_isolated import tenant_isolated

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/media", tags=["media"])


class MediaUploadRequest(BaseModel):
    """Request model for media upload"""
    base64_data: str = Field(..., description="Base64 encoded file data")
    media_type: str = Field(default="image", description="Type of media (image, video, etc.)")
    folder: str = Field(default="salon-media", description="Cloudinary folder path")


class MediaUploadResponse(BaseModel):
    """Response model for media upload"""
    url: str = Field(..., description="Secure URL of uploaded media")
    message: str = Field(default="Media uploaded successfully")


@router.post("/upload", response_model=MediaUploadResponse)
@tenant_isolated
async def upload_media_endpoint(
    request: MediaUploadRequest,
):
    """
    Upload media to Cloudinary
    
    Validates file size based on media type:
    - image: 5 MB max
    - document: 10 MB max
    """
    try:
        url = upload_media(
            base64_data=request.base64_data,
            media_type=request.media_type,
            folder=request.folder,
        )
        logger.info(f"Media uploaded successfully: {url}")
        return MediaUploadResponse(url=url)
    except MediaUploadError as e:
        logger.error(f"Media upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during media upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Media upload failed")
