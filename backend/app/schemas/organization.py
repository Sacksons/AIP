"""Organization schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    """Schema for creating an organization."""
    name: str = Field(..., min_length=1, max_length=255)
    org_type: str = Field(..., pattern="^(investor|sponsor|government|epc|verifier)$")
    country_code: Optional[str] = Field(None, max_length=10)
    registration_no: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    country_code: Optional[str] = Field(None, max_length=10)
    registration_no: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)


class OrgMemberCreate(BaseModel):
    """Schema for adding a member to organization."""
    user_id: int
    role: str = Field(..., pattern="^(admin|verifier|partner_verifier|sponsor|investor|government|epc)$")
    title: Optional[str] = Field(None, max_length=100)
    is_owner: bool = False


class OrgMemberResponse(BaseModel):
    """Schema for organization member response."""
    id: int
    org_id: int
    user_id: int
    role: str
    title: Optional[str] = None
    is_owner: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationResponse(BaseModel):
    """Schema for organization response."""
    id: int
    uuid: str
    name: str
    org_type: str
    country_code: Optional[str] = None
    registration_no: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    members: Optional[List[OrgMemberResponse]] = None

    class Config:
        from_attributes = True
