"""
Tests for White Label Asset Manager Service
"""
import pytest
import io
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from PIL import Image
from fastapi import UploadFile

# Mock minio before importing AssetManagerService
import sys
from unittest.mock import MagicMock
sys.modules['minio'] = MagicMock()
sys.modules['minio.error'] = MagicMock()

from app.services.white_label_asset_manager import AssetManagerService


@pytest.fixture
def asset_manager():
    """Create asset manager instance with mocked MinIO client"""
    with patch('app.services.white_label_asset_manager.minio.Minio'):
        manager = AssetManagerService()
        manager.client = Mock()
        return manager


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "test-tenant-123"


@pytest.fixture
def sample_png_image():
    """Create a sample PNG image"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


@pytest.fixture
def sample_favicon_image():
    """Create a sample favicon image (32x32)"""
    img = Image.new('RGB', (32, 32), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


@pytest.fixture
def sample_large_image():
    """Create a large image that exceeds size limit"""
    img = Image.new('RGB', (5000, 5000), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG', quality=95)
    img_bytes.seek(0)
    return img_bytes.getvalue()


def create_upload_file(filename: str, content: bytes, content_type: str) -> UploadFile:
    """Helper to create UploadFile for testing"""
    file_obj = io.BytesIO(content)
    file = UploadFile(
        file=file_obj,
        size=len(content),
        filename=filename
    )
    file.content_type = content_type
    return file


class TestAssetValidation:
    """Test asset validation functionality"""

    @pytest.mark.asyncio
    async def test_validate_image_valid_png(self, asset_manager, sample_png_image):
        """Test validating valid PNG image"""
        file = create_upload_file("logo.png", sample_png_image, "image/png")
        
        result = await asset_manager.validate_image(file, "logo")
        
        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_image_invalid_extension(self, asset_manager, sample_png_image):
        """Test validating image with invalid extension"""
        file = create_upload_file("logo.gif", sample_png_image, "image/gif")
        
        result = await asset_manager.validate_image(file, "logo")
        
        assert result["valid"] is False
        assert "Invalid file type" in result["error"]

    @pytest.mark.asyncio
    async def test_validate_image_invalid_content_type(self, asset_manager, sample_png_image):
        """Test validating image with invalid content type"""
        file = create_upload_file("logo.png", sample_png_image, "text/plain")
        
        result = await asset_manager.validate_image(file, "logo")
        
        assert result["valid"] is False
        assert "Invalid content type" in result["error"]

    @pytest.mark.asyncio
    async def test_validate_image_file_too_large(self, asset_manager, sample_large_image):
        """Test validating image that exceeds size limit"""
        file = create_upload_file("logo.png", sample_large_image, "image/png")
        
        result = await asset_manager.validate_image(file, "logo")
        
        assert result["valid"] is False
        assert "File too large" in result["error"]

    @pytest.mark.asyncio
    async def test_validate_favicon_invalid_dimensions(self, asset_manager, sample_png_image):
        """Test validating favicon with invalid dimensions"""
        file = create_upload_file("favicon.png", sample_png_image, "image/png")
        
        result = await asset_manager.validate_image(file, "favicon")
        
        assert result["valid"] is False
        assert "Favicon dimensions" in result["error"]

    @pytest.mark.asyncio
    async def test_validate_favicon_valid_dimensions(self, asset_manager, sample_favicon_image):
        """Test validating favicon with valid dimensions"""
        file = create_upload_file("favicon.png", sample_favicon_image, "image/png")
        
        result = await asset_manager.validate_image(file, "favicon")
        
        assert result["valid"] is True


class TestAssetOptimization:
    """Test asset optimization functionality"""

    @pytest.mark.asyncio
    async def test_optimize_image_png(self, asset_manager, sample_png_image):
        """Test optimizing PNG image"""
        optimized = await asset_manager.optimize_image(sample_png_image, "logo")
        
        assert optimized is not None
        assert len(optimized) > 0
        # Verify it's still a valid image
        img = Image.open(io.BytesIO(optimized))
        assert img.format in ['PNG', 'JPEG']

    @pytest.mark.asyncio
    async def test_optimize_image_preserves_svg(self, asset_manager):
        """Test that SVG images are preserved as-is"""
        svg_content = b'<svg></svg>'
        
        optimized = await asset_manager.optimize_image(svg_content, "logo")
        
        assert optimized == svg_content

    @pytest.mark.asyncio
    async def test_optimize_image_resizes_large_logo(self, asset_manager):
        """Test that large logos are resized"""
        # Create a large image (1000x1000)
        img = Image.new('RGB', (1000, 1000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        large_image = img_bytes.getvalue()
        
        optimized = await asset_manager.optimize_image(large_image, "logo")
        
        # Verify the optimized image is smaller
        optimized_img = Image.open(io.BytesIO(optimized))
        assert optimized_img.width <= 500


class TestAssetUpload:
    """Test asset upload functionality"""

    @pytest.mark.asyncio
    async def test_upload_asset_logo_success(self, asset_manager, tenant_id, sample_png_image):
        """Test successful logo upload"""
        file = create_upload_file("logo.png", sample_png_image, "image/png")
        asset_manager.client.put_object = Mock()
        asset_manager.client.get_presigned_download_link = Mock(
            return_value="https://minio.example.com/bucket/logo.png"
        )
        
        result = await asset_manager.upload_asset(tenant_id, file, "logo")
        
        assert result["asset_type"] == "logo"
        assert result["asset_url"] == "https://minio.example.com/bucket/logo.png"
        assert result["file_size"] > 0
        assert "dimensions" in result
        assert result["dimensions"]["width"] > 0
        assert result["dimensions"]["height"] > 0
        assert "uploaded_at" in result

    @pytest.mark.asyncio
    async def test_upload_asset_favicon_success(self, asset_manager, tenant_id, sample_favicon_image):
        """Test successful favicon upload"""
        file = create_upload_file("favicon.png", sample_favicon_image, "image/png")
        asset_manager.client.put_object = Mock()
        asset_manager.client.get_presigned_download_link = Mock(
            return_value="https://minio.example.com/bucket/favicon.png"
        )
        
        result = await asset_manager.upload_asset(tenant_id, file, "favicon")
        
        assert result["asset_type"] == "favicon"
        assert result["asset_url"] == "https://minio.example.com/bucket/favicon.png"

    @pytest.mark.asyncio
    async def test_upload_asset_invalid_type(self, asset_manager, tenant_id, sample_png_image):
        """Test upload with invalid asset type"""
        file = create_upload_file("image.png", sample_png_image, "image/png")
        
        with pytest.raises(ValueError, match="asset_type must be"):
            await asset_manager.upload_asset(tenant_id, file, "invalid")

    @pytest.mark.asyncio
    async def test_upload_asset_validation_fails(self, asset_manager, tenant_id):
        """Test upload when validation fails"""
        file = create_upload_file("image.gif", b"not an image", "image/gif")
        
        with pytest.raises(ValueError, match="Invalid file type"):
            await asset_manager.upload_asset(tenant_id, file, "logo")

    @pytest.mark.asyncio
    async def test_upload_asset_storage_fails(self, asset_manager, tenant_id, sample_png_image):
        """Test upload when storage fails"""
        from minio.error import S3Error
        
        file = create_upload_file("logo.png", sample_png_image, "image/png")
        asset_manager.client.put_object = Mock(side_effect=S3Error("Storage error"))
        
        with pytest.raises(RuntimeError, match="Failed to upload asset"):
            await asset_manager.upload_asset(tenant_id, file, "logo")


class TestAssetDeletion:
    """Test asset deletion functionality"""

    @pytest.mark.asyncio
    async def test_delete_asset_success(self, asset_manager, tenant_id):
        """Test successful asset deletion"""
        asset_url = "https://minio.example.com/bucket/logo.png"
        asset_manager.client.remove_object = Mock()
        
        result = await asset_manager.delete_asset(tenant_id, asset_url)
        
        assert result is True
        asset_manager.client.remove_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_asset_storage_fails(self, asset_manager, tenant_id):
        """Test deletion when storage fails"""
        from minio.error import S3Error
        
        asset_url = "https://minio.example.com/bucket/logo.png"
        asset_manager.client.remove_object = Mock(side_effect=S3Error("Storage error"))
        
        with pytest.raises(RuntimeError, match="Failed to delete asset"):
            await asset_manager.delete_asset(tenant_id, asset_url)


class TestAssetRetrieval:
    """Test asset retrieval functionality"""

    @pytest.mark.asyncio
    async def test_get_asset_url_found(self, asset_manager, tenant_id):
        """Test retrieving asset URL when asset exists"""
        mock_obj = Mock()
        mock_obj.object_name = "white-label/test-tenant-123/logo/logo_abc123.png"
        
        asset_manager.client.list_objects = Mock(return_value=[mock_obj])
        asset_manager.client.get_presigned_download_link = Mock(
            return_value="https://minio.example.com/bucket/logo.png"
        )
        
        result = await asset_manager.get_asset_url(tenant_id, "logo")
        
        assert result == "https://minio.example.com/bucket/logo.png"

    @pytest.mark.asyncio
    async def test_get_asset_url_not_found(self, asset_manager, tenant_id):
        """Test retrieving asset URL when asset doesn't exist"""
        asset_manager.client.list_objects = Mock(return_value=[])
        
        result = await asset_manager.get_asset_url(tenant_id, "logo")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_asset_url_storage_error(self, asset_manager, tenant_id):
        """Test retrieving asset URL when storage fails"""
        from minio.error import S3Error
        
        asset_manager.client.list_objects = Mock(side_effect=S3Error("Storage error"))
        
        result = await asset_manager.get_asset_url(tenant_id, "logo")
        
        assert result is None


class TestAssetURLGeneration:
    """Test secure URL generation"""

    def test_generate_asset_url_success(self, asset_manager):
        """Test generating presigned URL"""
        object_name = "white-label/tenant-123/logo/logo_abc123.png"
        asset_manager.client.get_presigned_download_link = Mock(
            return_value="https://minio.example.com/presigned-url"
        )
        
        url = asset_manager._generate_asset_url(object_name)
        
        assert url == "https://minio.example.com/presigned-url"
        asset_manager.client.get_presigned_download_link.assert_called_once()

    def test_generate_asset_url_fallback(self, asset_manager):
        """Test URL generation fallback when presigned fails"""
        from minio.error import S3Error
        
        object_name = "white-label/tenant-123/logo/logo_abc123.png"
        asset_manager.client.get_presigned_download_link = Mock(side_effect=S3Error("Error"))
        
        url = asset_manager._generate_asset_url(object_name)
        
        assert object_name in url
