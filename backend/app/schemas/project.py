"""Project schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from decimal import Decimal


class ProjectFinancialsCreate(BaseModel):
    """Schema for creating/updating project financials."""
    currency: str = "USD"
    revenue_model: Optional[str] = None
    capex_usd: Optional[Decimal] = None
    opex_usd_annual: Optional[Decimal] = None
    irr_pct: Optional[Decimal] = None
    roi_pct: Optional[Decimal] = None
    payback_years: Optional[Decimal] = None
    timeline_json: Optional[Dict[str, Any]] = None
    assumptions_json: Optional[Dict[str, Any]] = None


class ProjectFinancialsResponse(BaseModel):
    """Schema for project financials response."""
    id: int
    project_id: int
    currency: str
    revenue_model: Optional[str] = None
    capex_usd: Optional[Decimal] = None
    opex_usd_annual: Optional[Decimal] = None
    irr_pct: Optional[Decimal] = None
    roi_pct: Optional[Decimal] = None
    payback_years: Optional[Decimal] = None
    timeline_json: Optional[Dict[str, Any]] = None
    assumptions_json: Optional[Dict[str, Any]] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectRiskAssessmentResponse(BaseModel):
    """Schema for project risk assessment response."""
    id: int
    uuid: str
    project_id: int
    overall_score: int
    category_scores: Dict[str, Any]
    model_version: str
    narrative: Optional[str] = None
    mitigations_json: Optional[Dict[str, Any]] = None
    is_human_override: bool
    override_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    """Schema for creating a project."""
    sponsor_org_id: int
    name: str = Field(..., min_length=1, max_length=255)
    sector: str = Field(..., min_length=1, max_length=100)
    sub_sector: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    sdg_tags: Optional[str] = None  # Comma-separated
    capacity_value: Optional[Decimal] = None
    capacity_unit: Optional[str] = Field(None, max_length=50)
    impact_statement: Optional[str] = None
    investment_usd: Optional[Decimal] = None
    expected_roi_pct: Optional[Decimal] = None
    payback_years: Optional[Decimal] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sector: Optional[str] = Field(None, min_length=1, max_length=100)
    sub_sector: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    sdg_tags: Optional[str] = None
    capacity_value: Optional[Decimal] = None
    capacity_unit: Optional[str] = Field(None, max_length=50)
    impact_statement: Optional[str] = None
    investment_usd: Optional[Decimal] = None
    expected_roi_pct: Optional[Decimal] = None
    payback_years: Optional[Decimal] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: int
    uuid: str
    sponsor_org_id: int
    name: str
    sector: str
    sub_sector: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    sdg_tags: Optional[str] = None
    capacity_value: Optional[Decimal] = None
    capacity_unit: Optional[str] = None
    impact_statement: Optional[str] = None
    investment_usd: Optional[Decimal] = None
    expected_roi_pct: Optional[Decimal] = None
    payback_years: Optional[Decimal] = None
    verification_level: str
    risk_score: Optional[int] = None
    status: str
    is_featured: bool
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    financials: Optional[ProjectFinancialsResponse] = None
    risk_assessments: Optional[List[ProjectRiskAssessmentResponse]] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for paginated project list."""
    items: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    pages: int
