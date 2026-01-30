"""Investor preferences and matching models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Numeric, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class InvestorPreferences(Base):
    """Investor organization preferences for project matching."""

    __tablename__ = "investor_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Investment criteria
    min_ticket_usd = Column(Numeric(18, 2))
    max_ticket_usd = Column(Numeric(18, 2))
    target_irr_min = Column(Numeric(6, 2))
    target_irr_max = Column(Numeric(6, 2))

    # Preferences (comma-separated or JSON)
    sectors = Column(String(500))  # Energy,Transport,Water
    countries = Column(String(500))  # NG,KE,ZA
    instruments = Column(String(200))  # equity,debt,mezzanine
    stages = Column(String(200))  # feasibility,construction,operation

    # Risk tolerance
    max_risk_score = Column(Integer)  # 0-100
    min_verification_level = Column(String(10), default="V2")  # V0-V5

    # ESG requirements
    esg_minimum_score = Column(Integer)
    excluded_sectors = Column(String(500))  # coal,tobacco,weapons

    # Metadata
    aum_usd = Column(Numeric(18, 2))  # Assets under management
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    investor_org = relationship("Organization", back_populates="preferences")

    def __repr__(self):
        return f"<InvestorPreferences org={self.org_id}>"


class Match(Base):
    """AI-generated match between investor and project."""

    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    project_id = Column(Integer, ForeignKey("aip_projects.id", ondelete="CASCADE"), nullable=False)
    investor_org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Match quality
    match_score = Column(Integer, nullable=False)  # 0-100
    score_breakdown = Column(JSON)  # {"sector": 90, "geography": 85, "ticket": 70, ...}
    match_reasons = Column(JSON)  # ["Sector alignment", "Geographic focus", ...]

    # Status
    status = Column(String(50), default="suggested", nullable=False)  # suggested, viewed, interested, dismissed
    investor_interest = Column(String(50))  # interested, not_interested, later
    sponsor_interest = Column(String(50))  # interested, not_interested, later

    # Interaction tracking
    viewed_at = Column(DateTime)
    responded_at = Column(DateTime)
    introduced_at = Column(DateTime)  # When formal introduction was made

    # Metadata
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="matches")

    def __repr__(self):
        return f"<Match project={self.project_id} investor={self.investor_org_id} score={self.match_score}>"
