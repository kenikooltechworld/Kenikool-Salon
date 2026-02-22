"""
Document Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Dict, Optional
from app.services.document_service import DocumentService
from app.middleware.tenant_isolation import get_current_tenant_id
import os
import tempfile

router = APIRouter()


@router.post("/api/clients/{client_id}/documents")
async def upload_document(
    client_id: str,
    file: UploadFile = File(...),
    category: str = Form("general"),
    tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Upload a document for a client.
    
    Args:
        client_id: Client ID
        file: File to upload
        category: Document category
        tenant_id: Current tenant ID
    
    Returns:
        Upload confirmation with document ID
    """
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        result = DocumentService.upload_document(
            tenant_id=tenant_id,
            client_id=client_id,
            file_path=tmp_path,
            file_name=file.filename,
            category=category
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/clients/{client_id}/documents")
async def get_client_documents(
    client_id: str,
    tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Get all documents for a client.
    
    Args:
        client_id: Client ID
        tenant_id: Current tenant ID
    
    Returns:
        List of client documents
    """
    try:
        documents = DocumentService.get_client_documents(
            tenant_id=tenant_id,
            client_id=client_id
        )
        return {
            "status": "success",
            "count": len(documents),
            "documents": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/documents/{document_id}")
async def delete_document(
    document_id: str,
    tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Delete a document.
    
    Args:
        document_id: Document ID
        tenant_id: Current tenant ID
    
    Returns:
        Deletion confirmation
    """
    try:
        result = DocumentService.delete_document(
            tenant_id=tenant_id,
            document_id=document_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
