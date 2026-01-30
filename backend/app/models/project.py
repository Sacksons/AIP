"""Project and related financial/risk models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class Project(Base):
    """Infrastructure project model."""

    __tablename__ = "aip_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    sponsor_org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Basic Information (Step 1 of wizard)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=False)  # Energy, Transport, Water, etc.
    sub_sector = Column(String(100))
    country = Column(String(100))
    city = Column(String(100))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    summary = Column(Text)
    description = Column(Text)
    sdg_tags = Column(String(500))  # Comma-separated SDG tags

    # Capacity & Impact
    capacity_value = Column(Numeric(18, 2))
    capacity_unit = Column(String(50))  # MW, km, m3/day, etc.
    impact_statement = Column(Text)

    # Financial Highlights (cached from ProjectFinancials)
    investment_usd = Column(Numeric(18, 2))
    expected_roi_pct = Column(Numeric(6, 2))
    payback_years = Column(Numeric(6, 2))

    # Verification & Risk
    verification_level = Column(String(10), default="V0", nullable=False)  # V0-V5
    risk_score = Column(Integer)  # 0-100
    status = Column(String(50), default="draft", nullable=False)  # draft, submitted, active, archived
    is_featured = Column(Boolean, default=False, nullable=False)

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    sponsor_org = relationship("Organization", back_populates="projects")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_projects")
    financials = relationship("ProjectFinancials", back_populates="project", uselist=False, cascade="all, delete-orphan")
    risk_assessments = relationship("ProjectRiskAssessment", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    verification_requests = relationship("VerificationRequest", back_populates="project", cascade="all, delete-orphan")
    blockchain_records = relationship("BlockchainRecord", back_populates="project", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="project", cascade="all, delete-orphan")
    dealrooms = relationship("DealRoom", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name} ({self.verification_level})>"


class ProjectFinancials(Base):
    """Detailed financial information for a project (Step 2 of wizard)."""

    __tablename__ = "project_financials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("aip_projects.id", ondelete="CASCADE"), unique=True, nullable=False)

    currency = Column(String(10), default="USD")
    revenue_model = Column(String(100))  # PPA, tariff, concession, etc.

    # Financial metrics
    capex_usd = Column(Numeric(18, 2))
    opex_usd_annual = Column(Numeric(18, 2))
    irr_pct = Column(Numeric(6, 2))
    roi_pct = Column(Numeric(6, 2))
    payback_years = Column(Numeric(6, 2))

    # Structured data
    timeline_json = Column(JSON)  # Development phases, milestones
    assumptions_json = Column(JSON)  # Key financial assumptions

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="financials")

    def __repr__(self):
        return f"<ProjectFinancials for project {self.project_id}>"


class ProjectRiskAssessment(Base):
    """AI-generated risk assessment for a project (Step 3 of wizard)."""

    __tablename__ = "project_risk_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    project_id = Column(Integer, ForeignKey("aip_projects.id", ondelete="CASCADE"), nullable=False)

    # Risk scores
    overall_score = Column(Integer, nullable=False)  # 0-100
    category_scores = Column(JSON, nullable=False)  # {"political": 75, "currency": 60, ...}

    # Metadata
    model_version = Column(String(50), nullable=False)
    inputs_json = Column(JSON, nullable=False)  # Input data used for scoring
    narrative = Column(Text)  # Human-readable explanation
    mitigations_json = Column(JSON)  # Suggested risk mitigations

    # Human override
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    is_human_override = Column(Boolean, default=False, nullable=False)
    override_reason = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="risk_assessments")

    def __repr__(self):
        return f"<RiskAssessment {self.overall_score} for project {self.project_id}>"
