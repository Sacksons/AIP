"""Organization and membership models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


class Organization(Base):
    """Organization/company model."""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    name = Column(String(255), nullable=False)
    org_type = Column(String(50), nullable=False)  # investor, sponsor, government, epc
    country_code = Column(String(10))  # ISO 3166-1 alpha-2
    registration_no = Column(String(100))
    website = Column(String(255))
    address = Column(String(500))

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    members = relationship("OrgMember", back_populates="organization", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="sponsor_org")
    preferences = relationship("InvestorPreferences", back_populates="investor_org", uselist=False)

    def __repr__(self):
        return f"<Organization {self.name} ({self.org_type})>"


class OrgMember(Base):
    """Organization membership with role assignment."""

    __tablename__ = "org_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    role = Column(String(50), nullable=False)  # From UserRole enum
    title = Column(String(100))  # Job title
    is_owner = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default="active", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="org_memberships")

    def __repr__(self):
        return f"<OrgMember {self.user_id} in {self.org_id} as {self.role}>"
