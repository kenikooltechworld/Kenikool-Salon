"""
Tests for review photo upload functionality
"""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image
from bson import ObjectId
from datetime import datetime

from app.main import app
from app.database import get_database

client = TestClient(app)


@pytest.fixture
def mock_db(mocker):
    """Mock database"""
    db = mocker.MagicMock()
    mocker.patch("app.api.dependencies.get_database", return_value=db)
    return db


@pytest.fixture
def mock_current_user(mocker):
    """Mock current user"""
    user = {
        "id": "user-123",
        "tenant_id": "tenant-123",
        "name": "Test User",
        "email": "test@example.com"
    }
    mocker.patch("app.api.dependencies.get_current_user", return_value=user)
    return user


@pytest.fixture
def sample_review():
    """Sample review data"""
    return {
        "_id": ObjectId(),
        "tenant_id": "tenant-123",
        "booking_id": "booking-123",
        "client_id": "client-123",
        "client_name": "John Doe",
        "rating": 5,
        "comment": "Great service!",
        "status": "approved",
        "photos": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


def create_test_image(filename="test.jpg", size=(100, 100)):
    """Create a test image file"""
    image = Image.new('RGB', size, color='red')
    image_bytes = BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)
    return ("file", (filename, image_bytes, "image/jpeg"))


class TestPhotoUpload:
    """Test photo upload functionality"""

    def test_upload_photo_success(self, mock_db, mock_current_user, sample_review):
        """Test successful photo upload"""
        review_id = str(sample_review["_id"])
        
        # Mock database responses
        mock_db.reviews.find_one.return_value = sample_review
        mock_db.reviews.update_one.return_value = None
        mock_db.review_photos.insert_one.return_value = None

        # Create test image
        image_file = create_test_image()

        # Upload photo
        response = client.post(
            f"/api/reviews/{review_id}/photos",
            files=[image_file],
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "url" in data
        assert data["filename"] == "test.jpg"
        assert data["content_type"] == "image/jpeg"

    def test_upload_photo_review_not_found(self, mock_db, mock_current_user):
        """Test upload when review doesn't exist"""
        review_id = str(ObjectId())
        
        # Mock database response
        mock_db.reviews.find_one.return_value = None

        # Create test image
        image_file = create_test_image()

        # Upload photo
        response = client.post(
            f"/api/reviews/{review_id}/photos",
            files=[image_file],
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 400
        assert "Review not found" in response.json()["detail"]

    def test_upload_photo_max_limit(self, mock_db, mock_current_user, sample_review):
        """Test upload when max photos reached"""
        review_id = str(sample_review["_id"])
        
        # Add 5 photos to review
        sample_review["photos"] = [
            {"id": f"photo-{i}", "url": f"/api/reviews/{review_id}/photos/photo-{i}"}
            for i in range(5)
        ]
        
        # Mock database responses
        mock_db.reviews.find_one.return_value = sample_review

        # Create test image
        image_file = create_test_image()

        # Upload photo
        response = client.post(
            f"/api/reviews/{review_id}/photos",
            files=[image_file],
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 400
        assert "Maximum 5 photos" in response.json()["detail"]

    def test_upload_photo_invalid_file_type(self, mock_db, mock_current_user, sample_review):
        """Test upload with invalid file type"""
        review_id = str(sample_review["_id"])
        
        # Mock database response
        mock_db.reviews.find_one.return_value = sample_review

        # Create invalid file (PDF)
        pdf_file = ("file", ("test.pdf", BytesIO(b"PDF content"), "application/pdf"))

        # Upload photo
        response = client.post(
            f"/api/reviews/{review_id}/photos",
            files=[pdf_file],
            headers={"Authorization": "Bearer test-token"}
        )

        # Should fail validation
        assert response.status_code in [400, 422]

    def test_upload_multiple_photos(self, mock_db, mock_current_user, sample_review):
        """Test uploading multiple photos"""
        review_id = str(sample_review["_id"])
        
        # Mock database responses
        mock_db.reviews.find_one.return_value = sample_review
        mock_db.reviews.update_one.return_value = None
        mock_db.review_photos.insert_one.return_value = None

        # Create multiple test images
        files = [
            create_test_image(f"test{i}.jpg")
            for i in range(3)
        ]

        # Upload photos
        for image_file in files:
            response = client.post(
                f"/api/reviews/{review_id}/photos",
                files=[image_file],
                headers={"Authorization": "Bearer test-token"}
            )
            assert response.status_code == 200

        # Verify all photos were uploaded
        assert mock_db.review_photos.insert_one.call_count == 3

    def test_upload_photo_requires_auth(self, sample_review):
        """Test that photo upload requires authentication"""
        review_id = str(sample_review["_id"])
        
        # Create test image
        image_file = create_test_image()

        # Upload photo without auth
        response = client.post(
            f"/api/reviews/{review_id}/photos",
            files=[image_file]
        )

        assert response.status_code == 401


class TestPhotoDelete:
    """Test photo deletion functionality"""

    def test_delete_photo_success(self, mock_db, mock_current_user, sample_review):
        """Test successful photo deletion"""
        review_id = str(sample_review["_id"])
        photo_id = "photo-123"
        
        # Add photo to review
        sample_review["photos"] = [
            {"id": photo_id, "url": f"/api/reviews/{review_id}/photos/{photo_id}"}
        ]
        
        # Mock database responses
        mock_db.reviews.find_one.return_value = sample_review
        mock_db.reviews.update_one.return_value = None
        mock_db.review_photos.delete_one.return_value = None

        # Delete photo
        response = client.delete(
            f"/api/reviews/{review_id}/photos/{photo_id}",
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        
        # Verify deletion calls
        mock_db.reviews.update_one.assert_called_once()
        mock_db.review_photos.delete_one.assert_called_once()

    def test_delete_photo_review_not_found(self, mock_db, mock_current_user):
        """Test delete when review doesn't exist"""
        review_id = str(ObjectId())
        photo_id = "photo-123"
        
        # Mock database response
        mock_db.reviews.find_one.return_value = None

        # Delete photo
        response = client.delete(
            f"/api/reviews/{review_id}/photos/{photo_id}",
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 400
        assert "Review not found" in response.json()["detail"]

    def test_delete_photo_requires_auth(self, sample_review):
        """Test that photo deletion requires authentication"""
        review_id = str(sample_review["_id"])
        photo_id = "photo-123"

        # Delete photo without auth
        response = client.delete(
            f"/api/reviews/{review_id}/photos/{photo_id}"
        )

        assert response.status_code == 401


class TestPhotoGallery:
    """Test photo gallery display"""

    def test_review_with_photos_in_list(self, mock_db, mock_current_user, sample_review):
        """Test that reviews with photos are returned correctly"""
        review_id = str(sample_review["_id"])
        
        # Add photos to review
        sample_review["photos"] = [
            {
                "id": f"photo-{i}",
                "url": f"/api/reviews/{review_id}/photos/photo-{i}",
                "uploaded_at": datetime.utcnow()
            }
            for i in range(3)
        ]
        
        # Mock database responses
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = [sample_review]
        mock_db.reviews.count_documents.return_value = 1

        # Get reviews
        response = client.get(
            "/api/reviews",
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["reviews"]) == 1
        assert len(data["reviews"][0]["photos"]) == 3

    def test_photo_count_in_aggregation(self, mock_db, mock_current_user):
        """Test that photo count is included in aggregation"""
        # Mock database response
        mock_db.reviews.aggregate.return_value = [
            {
                "_id": None,
                "average_rating": 4.5,
                "total_reviews": 10,
                "reviews_with_photos": 5
            }
        ]

        # Get aggregation
        response = client.get(
            "/api/reviews/aggregation",
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200


class TestPhotoValidation:
    """Test photo validation"""

    def test_validate_image_format_jpeg(self, mock_db, mock_current_user, sample_review):
        """Test JPEG format validation"""
        review_id = str(sample_review["_id"])
        
        mock_db.reviews.find_one.return_value = sample_review
        mock_db.reviews.update_one.return_value = None
        mock_db.review_photos.insert_one.return_value = None

        image_file = create_test_image("test.jpg")
        response = client.post(
            f"/api/reviews/{review_id}/photos",
            files=[image_file],
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200

    def test_validate_image_format_png(self, mock_db, mock_current_user, sample_review):
        """Test PNG format validation"""
        review_id = str(sample_review["_id"])
        
        mock_db.reviews.find_one.return_value = sample_review
        mock_db.reviews.update_one.return_value = None
        mock_db.review_photos.insert_one.return_value = None

        # Create PNG image
        image = Image.new('RGB', (100, 100), color='blue')
        image_bytes = BytesIO()
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        image_file = ("file", ("test.png", image_bytes, "image/png"))

        response = client.post(
            f"/api/reviews/{review_id}/photos",
            files=[image_file],
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200

    def test_validate_image_format_webp(self, mock_db, mock_current_user, sample_review):
        """Test WebP format validation"""
        review_id = str(sample_review["_id"])
        
        mock_db.reviews.find_one.return_value = sample_review
        mock_db.reviews.update_one.return_value = None
        mock_db.review_photos.insert_one.return_value = None

        # Create WebP image
        image = Image.new('RGB', (100, 100), color='green')
        image_bytes = BytesIO()
        image.save(image_bytes, format='WEBP')
        image_bytes.seek(0)
        image_file = ("file", ("test.webp", image_bytes, "image/webp"))

        response = client.post(
            f"/api/reviews/{review_id}/photos",
            files=[image_file],
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200

    def test_validate_file_size_limit(self, mock_db, mock_current_user, sample_review):
        """Test file size validation"""
        review_id = str(sample_review["_id"])
        
        mock_db.reviews.find_one.return_value = sample_review

        # Create large file (simulated)
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        large_file = ("file", ("large.jpg", BytesIO(large_content), "image/jpeg"))

        response = client.post(
            f"/api/reviews/{review_id}/photos",
            files=[large_file],
            headers={"Authorization": "Bearer test-token"}
        )

        # Should fail validation
        assert response.status_code in [400, 422]
