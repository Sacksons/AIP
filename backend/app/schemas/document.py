"""Document schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    """Schema for creating a document record."""
    project_id: int
    name: str = Field(..., min_length=1, max_length=255)
    doc_type: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_public: bool = False
    requires_nda: bool = True


class DocumentResponse(BaseModel):
    """Schema for document response."""
    id: int
    uuid: str
    project_id: int
    name: str
    doc_type: str
    description: Optional[str] = None
    s3_key: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    sha256_hash: Optional[str] = None
    is_public: bool
    requires_nda: bool
    is_verified: bool
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    uploaded_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataRoomAccessRequest(BaseModel):
    """Schema for requesting data room access."""
    project_id: int
    access_level: str = "view"  # view, download
    message: Optional[str] = None


class DataRoomAccessResponse(BaseModel):
    """Schema for data room access response."""
    id: int
    project_id: int
    user_id: int
    org_id: Optional[int] = None
    access_level: str
    nda_signed: bool
    nda_signed_at: Optional[datetime] = None
    status: str
    granted_by: Optional[int] = None
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
