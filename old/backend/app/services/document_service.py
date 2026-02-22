from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId
from app.database import db
import os

class DocumentService:
    """Service for managing client documents and files."""
    
    ALLOWED_TYPES = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif']
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
    
    @staticmethod
    def upload_document(tenant_id: str, client_id: str, file_path: str, 
                       file_name: str, category: str) -> Dict:
        """Upload and store client document."""
        file_ext = file_name.split('.')[-1].lower()
        
        if file_ext not in DocumentService.ALLOWED_TYPES:
            raise ValueError(f"File type {file_ext} not allowed")
        
        file_size = os.path.getsize(file_path)
        if file_size > DocumentService.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds {DocumentService.MAX_FILE_SIZE} bytes")
        
        document = {
            "client_id": ObjectId(client_id),
            "tenant_id": tenant_id,
            "file_name": file_name,
            "file_path": file_path,
            "file_type": file_ext,
            "file_size": file_size,
            "category": category,
            "uploaded_at": datetime.utcnow(),
            "thumbnail_path": None,
        }
        
        result = db.client_documents.insert_one(document)
        
        return {
            "status": "uploaded",
            "document_id": str(result.inserted_id),
            "file_name": file_name,
        }
    
    @staticmethod
    def get_client_documents(tenant_id: str, client_id: str) -> List[Dict]:
        """Get all documents for a client."""
        documents = list(db.client_documents.find({
            "client_id": ObjectId(client_id),
            "tenant_id": tenant_id
        }))
        
        return [{
            "id": str(doc["_id"]),
            "file_name": doc["file_name"],
            "file_type": doc["file_type"],
            "file_size": doc["file_size"],
            "category": doc["category"],
            "uploaded_at": doc["uploaded_at"].isoformat(),
        } for doc in documents]
    
    @staticmethod
    def delete_document(tenant_id: str, document_id: str) -> Dict:
        """Delete a document."""
        doc = db.client_documents.find_one({
            "_id": ObjectId(document_id),
            "tenant_id": tenant_id
        })
        
        if not doc:
            raise ValueError("Document not found")
        
        # Delete file from storage
        if os.path.exists(doc["file_path"]):
            os.remove(doc["file_path"])
        
        db.client_documents.delete_one({"_id": ObjectId(document_id)})
        
        return {"status": "deleted", "document_id": document_id}
    
    @staticmethod
    def generate_thumbnail(file_path: str, file_type: str) -> Optional[str]:
        """Generate thumbnail for document preview."""
        if file_type in ['jpg', 'jpeg', 'png', 'gif']:
            # Image thumbnail generation would go here
            return file_path
        elif file_type == 'pdf':
            # PDF thumbnail generation would go here
            return None
        return None
