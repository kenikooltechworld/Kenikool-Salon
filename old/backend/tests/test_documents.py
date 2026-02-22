"""
Tests for document management service
"""
import pytest
from datetime import datetime
from bson import ObjectId
from app.services.document_service import DocumentService
from app.database import Database


@pytest.fixture
def db():
    """Get database instance"""
    return Database.get_db()


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "test-tenant-123"


@pytest.fixture
def sample_client(db, tenant_id):
    """Create sample client for testing"""
    client = {
        "tenant_id": tenant_id,
        "name": "John Smith",
        "phone": "+1-555-0101",
        "email": "john.smith@example.com",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = db.clients.insert_one(client)
    return str(result.inserted_id)


class TestDocumentService:
    """Test document management functionality"""
    
    def test_validate_file_valid_pdf(self):
        """Test validating valid PDF file"""
        ext, mime_type = DocumentService._validate_file("document.pdf", 1000)
        
        assert ext == "pdf"
        assert mime_type == "application/pdf"
    
    def test_validate_file_valid_image(self):
        """Test validating valid image file"""
        ext, mime_type = DocumentService._validate_file("photo.jpg", 1000)
        
        assert ext == "jpg"
        assert mime_type == "image/jpeg"
    
    def test_validate_file_no_extension(self):
        """Test validating file without extension"""
        with pytest.raises(Exception):
            DocumentService._validate_file("document", 1000)
    
    def test_validate_file_unsupported_type(self):
        """Test validating unsupported file type"""
        with pytest.raises(Exception):
            DocumentService._validate_file("document.exe", 1000)
    
    def test_validate_file_too_large(self):
        """Test validating file that's too large"""
        with pytest.raises(Exception):
            DocumentService._validate_file("document.pdf", 30 * 1024 * 1024)
    
    def test_upload_document(self, db, tenant_id, sample_client):
        """Test uploading document"""
        content = b"PDF content here"
        
        doc = DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="contract.pdf",
            file_content=content,
            document_type="contract",
            category="legal",
            description="Service contract"
        )
        
        assert doc["client_id"] == sample_client
        assert doc["filename"] == "contract.pdf"
        assert doc["file_type"] == "pdf"
        assert doc["document_type"] == "contract"
        assert doc["category"] == "legal"
        assert doc["size"] == len(content)
    
    def test_upload_document_invalid_client(self, db, tenant_id):
        """Test uploading document for non-existent client"""
        with pytest.raises(Exception):
            DocumentService.upload_document(
                client_id="invalid-id",
                tenant_id=tenant_id,
                filename="contract.pdf",
                file_content=b"content",
                document_type="contract"
            )
    
    def test_get_documents(self, db, tenant_id, sample_client):
        """Test getting documents for client"""
        # Upload multiple documents
        DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="contract.pdf",
            file_content=b"content1",
            document_type="contract"
        )
        
        DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="consent.pdf",
            file_content=b"content2",
            document_type="consent"
        )
        
        # Get documents
        docs = DocumentService.get_documents(
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        assert len(docs) == 2
        assert docs[0]["filename"] in ["contract.pdf", "consent.pdf"]
    
    def test_get_documents_filtered_by_type(self, db, tenant_id, sample_client):
        """Test getting documents filtered by type"""
        # Upload multiple documents
        DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="contract.pdf",
            file_content=b"content1",
            document_type="contract"
        )
        
        DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="consent.pdf",
            file_content=b"content2",
            document_type="consent"
        )
        
        # Get documents filtered by type
        docs = DocumentService.get_documents(
            client_id=sample_client,
            tenant_id=tenant_id,
            document_type="contract"
        )
        
        assert len(docs) == 1
        assert docs[0]["document_type"] == "contract"
    
    def test_get_documents_filtered_by_category(self, db, tenant_id, sample_client):
        """Test getting documents filtered by category"""
        # Upload documents with different categories
        DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="contract.pdf",
            file_content=b"content1",
            document_type="contract",
            category="legal"
        )
        
        DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="receipt.pdf",
            file_content=b"content2",
            document_type="receipt",
            category="financial"
        )
        
        # Get documents filtered by category
        docs = DocumentService.get_documents(
            client_id=sample_client,
            tenant_id=tenant_id,
            category="legal"
        )
        
        assert len(docs) == 1
        assert docs[0]["category"] == "legal"
    
    def test_get_document(self, db, tenant_id, sample_client):
        """Test getting single document"""
        # Upload document
        uploaded = DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="contract.pdf",
            file_content=b"content",
            document_type="contract"
        )
        
        # Get document
        doc = DocumentService.get_document(
            document_id=uploaded["_id"],
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        assert doc["_id"] == uploaded["_id"]
        assert doc["filename"] == "contract.pdf"
    
    def test_get_document_not_found(self, db, tenant_id, sample_client):
        """Test getting non-existent document"""
        with pytest.raises(Exception):
            DocumentService.get_document(
                document_id="invalid-id",
                client_id=sample_client,
                tenant_id=tenant_id
            )
    
    def test_download_document(self, db, tenant_id, sample_client):
        """Test downloading document"""
        content = b"PDF content here"
        
        # Upload document
        uploaded = DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="contract.pdf",
            file_content=content,
            document_type="contract"
        )
        
        # Download document
        filename, file_content, mime_type = DocumentService.download_document(
            document_id=uploaded["_id"],
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        assert filename == "contract.pdf"
        assert file_content == content
        assert mime_type == "application/pdf"
    
    def test_delete_document(self, db, tenant_id, sample_client):
        """Test deleting document"""
        # Upload document
        uploaded = DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="contract.pdf",
            file_content=b"content",
            document_type="contract"
        )
        
        # Delete document
        result = DocumentService.delete_document(
            document_id=uploaded["_id"],
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        assert result["id"] == uploaded["_id"]
        
        # Verify document is deleted
        with pytest.raises(Exception):
            DocumentService.get_document(
                document_id=uploaded["_id"],
                client_id=sample_client,
                tenant_id=tenant_id
            )
    
    def test_update_document(self, db, tenant_id, sample_client):
        """Test updating document metadata"""
        # Upload document
        uploaded = DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="contract.pdf",
            file_content=b"content",
            document_type="contract"
        )
        
        # Update document
        updated = DocumentService.update_document(
            document_id=uploaded["_id"],
            client_id=sample_client,
            tenant_id=tenant_id,
            category="legal",
            description="Updated description"
        )
        
        assert updated["category"] == "legal"
        assert updated["description"] == "Updated description"
    
    def test_document_file_content_not_in_list(self, db, tenant_id, sample_client):
        """Test that file content is not returned in list"""
        # Upload document
        DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="contract.pdf",
            file_content=b"content",
            document_type="contract"
        )
        
        # Get documents
        docs = DocumentService.get_documents(
            client_id=sample_client,
            tenant_id=tenant_id
        )
        
        # Check file content is not included
        assert "file_content" not in docs[0]


class TestDocumentServiceProperties:
    """Property-based tests for document service"""
    
    def test_uploaded_document_has_required_fields(self, db, tenant_id, sample_client):
        """Property: Uploaded document should have all required fields"""
        doc = DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="contract.pdf",
            file_content=b"content",
            document_type="contract"
        )
        
        assert "client_id" in doc
        assert "filename" in doc
        assert "file_type" in doc
        assert "size" in doc
        assert "document_type" in doc
        assert "uploaded_at" in doc
    
    def test_document_size_matches_content(self, db, tenant_id, sample_client):
        """Property: Document size should match file content size"""
        content = b"This is test content"
        
        doc = DocumentService.upload_document(
            client_id=sample_client,
            tenant_id=tenant_id,
            filename="test.txt",
            file_content=content,
            document_type="test"
        )
        
        assert doc["size"] == len(content)
    
    def test_file_type_extracted_correctly(self, db, tenant_id, sample_client):
        """Property: File type should be extracted correctly from filename"""
        test_files = [
            ("document.pdf", "pdf"),
            ("image.jpg", "jpg"),
            ("spreadsheet.xlsx", "xlsx"),
            ("text.txt", "txt")
        ]
        
        for filename, expected_ext in test_files:
            doc = DocumentService.upload_document(
                client_id=sample_client,
                tenant_id=tenant_id,
                filename=filename,
                file_content=b"content",
                document_type="test"
            )
            
            assert doc["file_type"] == expected_ext
