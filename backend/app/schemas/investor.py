"""Investor schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from decimal import Decimal


class InvestorPreferencesCreate(BaseModel):
    """Schema for creating/updating investor preferences."""
    min_ticket_usd: Optional[Decimal] = None
    max_ticket_usd: Optional[Decimal] = None
    target_irr_min: Optional[Decimal] = None
    target_irr_max: Optional[Decimal] = None
    sectors: Optional[str] = None  # Comma-separated
    countries: Optional[str] = None  # Comma-separated
    instruments: Optional[str] = None  # Comma-separated
    stages: Optional[str] = None  # Comma-separated
    max_risk_score: Optional[int] = Field(None, ge=0, le=100)
    min_verification_level: Optional[str] = Field(None, pattern="^V[0-5]$")
    esg_minimum_score: Optional[int] = Field(None, ge=0, le=100)
    excluded_sectors: Optional[str] = None  # Comma-separated
    aum_usd: Optional[Decimal] = None


class InvestorPreferencesResponse(BaseModel):
    """Schema for investor preferences response."""
    id: int
    org_id: int
    min_ticket_usd: Optional[Decimal] = None
    max_ticket_usd: Optional[Decimal] = None
    target_irr_min: Optional[Decimal] = None
    target_irr_max: Optional[Decimal] = None
    sectors: Optional[str] = None
    countries: Optional[str] = None
    instruments: Optional[str] = None
    stages: Optional[str] = None
    max_risk_score: Optional[int] = None
    min_verification_level: Optional[str] = None
    esg_minimum_score: Optional[int] = None
    excluded_sectors: Optional[str] = None
    aum_usd: Optional[Decimal] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    """Schema for match response."""
    id: int
    uuid: str
    project_id: int
    investor_org_id: int
    match_score: int
    score_breakdown: Optional[Dict[str, Any]] = None
    match_reasons: Optional[List[str]] = None
    status: str
    investor_interest: Optional[str] = None
    sponsor_interest: Optional[str] = None
    viewed_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    introduced_at: Optional[datetime] = None
    model_version: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MatchInterest(BaseModel):
    """Schema for expressing interest in a match."""
    interest: str = Field(..., pattern="^(interested|not_interested|later)$")
