"""Verification workflow models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class VerificationRequest(Base):
    """Verification request for project advancement."""

    __tablename__ = "verification_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    project_id = Column(Integer, ForeignKey("aip_projects.id", ondelete="CASCADE"), nullable=False)

    # Request details
    from_level = Column(String(10), nullable=False)  # V0, V1, V2, V3, V4
    to_level = Column(String(10), nullable=False)  # V1, V2, V3, V4, V5
    status = Column(String(50), default="pending", nullable=False)  # pending, in_review, approved, rejected

    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    assigned_org_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))

    # Results
    decision = Column(String(50))  # approved, rejected, needs_revision
    decision_notes = Column(Text)
    decided_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    decided_at = Column(DateTime)

    # Metadata
    requested_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="verification_requests")
    checks = relationship("VerificationCheck", back_populates="request", cascade="all, delete-orphan")
    events = relationship("VerificationEvent", back_populates="request", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<VerificationRequest {self.from_level}->{self.to_level} ({self.status})>"


class VerificationCheck(Base):
    """Individual verification check within a request."""

    __tablename__ = "verification_checks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("verification_requests.id", ondelete="CASCADE"), nullable=False)

    # Check details
    check_type = Column(String(100), nullable=False)  # identity, document, financial, technical, legal, esg
    check_name = Column(String(255), nullable=False)
    description = Column(Text)

    # Result
    status = Column(String(50), default="pending", nullable=False)  # pending, passed, failed, skipped
    score = Column(Integer)  # 0-100 if applicable
    notes = Column(Text)
    evidence_json = Column(JSON)  # Supporting evidence/data

    # Performer
    checked_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    checked_at = Column(DateTime)

    # Auto vs manual
    is_automated = Column(Boolean, default=False, nullable=False)
    automation_source = Column(String(100))  # api_name, model_version

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    request = relationship("VerificationRequest", back_populates="checks")

    def __repr__(self):
        return f"<VerificationCheck {self.check_type}: {self.status}>"


class VerificationEvent(Base):
    """Audit trail for verification workflow."""

    __tablename__ = "verification_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("verification_requests.id", ondelete="CASCADE"), nullable=False)

    event_type = Column(String(100), nullable=False)  # created, assigned, check_completed, approved, rejected
    description = Column(Text)
    metadata_json = Column(JSON)

    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    request = relationship("VerificationRequest", back_populates="events")

    def __repr__(self):
        return f"<VerificationEvent {self.event_type}>"
