"""Verification schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class VerificationCheckCreate(BaseModel):
    """Schema for creating a verification check."""
    check_type: str = Field(..., min_length=1, max_length=100)
    check_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class VerificationCheckResponse(BaseModel):
    """Schema for verification check response."""
    id: int
    request_id: int
    check_type: str
    check_name: str
    description: Optional[str] = None
    status: str
    score: Optional[int] = None
    notes: Optional[str] = None
    evidence_json: Optional[Dict[str, Any]] = None
    checked_by: Optional[int] = None
    checked_at: Optional[datetime] = None
    is_automated: bool
    automation_source: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VerificationRequestCreate(BaseModel):
    """Schema for creating a verification request."""
    project_id: int
    to_level: str = Field(..., pattern="^V[1-5]$")


class VerificationRequestResponse(BaseModel):
    """Schema for verification request response."""
    id: int
    uuid: str
    project_id: int
    from_level: str
    to_level: str
    status: str
    assigned_to: Optional[int] = None
    assigned_org_id: Optional[int] = None
    decision: Optional[str] = None
    decision_notes: Optional[str] = None
    decided_by: Optional[int] = None
    decided_at: Optional[datetime] = None
    requested_by: int
    created_at: datetime
    updated_at: datetime
    checks: Optional[List[VerificationCheckResponse]] = None

    class Config:
        from_attributes = True


class VerificationDecision(BaseModel):
    """Schema for making a verification decision."""
    decision: str = Field(..., pattern="^(approved|rejected|needs_revision)$")
    decision_notes: Optional[str] = None


class VerificationCheckUpdate(BaseModel):
    """Schema for updating a verification check result."""
    status: str = Field(..., pattern="^(passed|failed|skipped)$")
    score: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    evidence_json: Optional[Dict[str, Any]] = None
