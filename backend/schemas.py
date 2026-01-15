from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=200)
    role: str = Field(default="user", max_length=20)


class UserRead(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sector: Optional[str] = None
    country: Optional[str] = None
    gps_location: Optional[str] = None
    stage: Optional[str] = None
    capex: Optional[Decimal] = None
    funding_gap: Optional[Decimal] = None
    timeline_fid: Optional[date] = None
    timeline_cod: Optional[date] = None
    revenue_model: Optional[str] = None
    offtaker: Optional[str] = None
    tariff: Optional[str] = None
    concession_length: Optional[int] = None
    fx_exposure: Optional[str] = None
    political_risk: Optional[str] = None
    sovereign_support: Optional[str] = None
    technology: Optional[str] = None
    epc_status: Optional[str] = None
    land_acquisition_status: Optional[str] = None
    esg_category: Optional[str] = None
    permits_status: Optional[str] = None
    teaser_url: Optional[str] = None
    feasibility_study_url: Optional[str] = None
    financial_model_url: Optional[str] = None
    concession_summary_url: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = None
    gps_location: Optional[str] = None
    stage: Optional[str] = None
    capex: Optional[Decimal] = None
    funding_gap: Optional[Decimal] = None
    timeline_fid: Optional[date] = None
    timeline_cod: Optional[date] = None
    revenue_model: Optional[str] = None
    offtaker: Optional[str] = None
    tariff: Optional[str] = None
    concession_length: Optional[int] = None
    fx_exposure: Optional[str] = None
    political_risk: Optional[str] = None
    sovereign_support: Optional[str] = None
    technology: Optional[str] = None
    epc_status: Optional[str] = None
    land_acquisition_status: Optional[str] = None
    esg_category: Optional[str] = None
    permits_status: Optional[str] = None
    teaser_url: Optional[str] = None
    feasibility_study_url: Optional[str] = None
    financial_model_url: Optional[str] = None
    concession_summary_url: Optional[str] = None


class ProjectRead(BaseModel):
    id: int
    name: str
    sector: Optional[str] = None
    country: Optional[str] = None
    verification_level: int
    bankability_score: float
    last_verified: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedProjects(BaseModel):
    projects: list[ProjectRead]
    total: int
    page: int
    limit: int
    pages: int