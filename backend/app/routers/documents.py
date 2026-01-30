"""Documents router."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.document import Document, DataRoomAccess
from app.schemas.document import (
    DocumentCreate, DocumentResponse,
    DataRoomAccessRequest, DataRoomAccessResponse
)
from .auth import require_auth

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    doc_data: DocumentCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a document record (file upload handled separately)."""
    document = Document(
        project_id=doc_data.project_id,
        name=doc_data.name,
        doc_type=doc_data.doc_type,
        description=doc_data.description,
        is_public=doc_data.is_public,
        requires_nda=doc_data.requires_nda,
        s3_key="pending",  # Set after upload
        uploaded_by=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/project/{project_id}", response_model=List[DocumentResponse])
def list_project_documents(
    project_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """List documents for a project."""
    return db.query(Document).filter(Document.project_id == project_id).all()


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get document by ID."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Delete document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()


# Data Room Access endpoints
@router.post("/access/request", response_model=DataRoomAccessResponse)
def request_data_room_access(
    request_data: DataRoomAccessRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Request access to project data room."""
    access = DataRoomAccess(
        project_id=request_data.project_id,
        user_id=current_user.id,
        access_level=request_data.access_level,
        status="pending",
    )
    db.add(access)
    db.commit()
    db.refresh(access)
    return access


@router.get("/access/project/{project_id}", response_model=List[DataRoomAccessResponse])
def list_access_requests(
    project_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """List data room access requests for a project."""
    return db.query(DataRoomAccess).filter(
        DataRoomAccess.project_id == project_id
    ).all()


@router.put("/access/{access_id}/approve", response_model=DataRoomAccessResponse)
def approve_access(
    access_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Approve data room access request."""
    from datetime import datetime

    access = db.query(DataRoomAccess).filter(DataRoomAccess.id == access_id).first()
    if not access:
        raise HTTPException(status_code=404, detail="Access request not found")

    access.status = "approved"
    access.granted_by = current_user.id
    access.granted_at = datetime.utcnow()
    db.commit()
    db.refresh(access)
    return access


@router.put("/access/{access_id}/reject", response_model=DataRoomAccessResponse)
def reject_access(
    access_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Reject data room access request."""
    access = db.query(DataRoomAccess).filter(DataRoomAccess.id == access_id).first()
    if not access:
        raise HTTPException(status_code=404, detail="Access request not found")

    access.status = "rejected"
    db.commit()
    db.refresh(access)
    return access
