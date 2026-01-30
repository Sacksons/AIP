"""Document and data room models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.core.database import Base


class Document(Base):
    """Document metadata and storage reference."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    project_id = Column(Integer, ForeignKey("aip_projects.id", ondelete="CASCADE"), nullable=False)

    # Document info
    name = Column(String(255), nullable=False)
    doc_type = Column(String(100), nullable=False)  # feasibility_study, ppa, license, financial_model, etc.
    description = Column(Text)

    # Storage
    s3_key = Column(String(500), nullable=False)
    mime_type = Column(String(100))
    file_size = Column(BigInteger)  # bytes
    sha256_hash = Column(String(64))  # For integrity verification

    # Access control
    is_public = Column(Boolean, default=False, nullable=False)
    requires_nda = Column(Boolean, default=True, nullable=False)

    # Verification
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    verified_at = Column(DateTime)

    # Metadata
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    access_logs = relationship("DocumentAccessLog", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document {self.name} ({self.doc_type})>"


class DocumentVersion(Base):
    """Document version history."""

    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    version_number = Column(Integer, nullable=False)
    s3_key = Column(String(500), nullable=False)
    file_size = Column(BigInteger)
    sha256_hash = Column(String(64))
    change_notes = Column(Text)

    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="versions")

    def __repr__(self):
        return f"<DocumentVersion {self.document_id} v{self.version_number}>"


class DataRoomAccess(Base):
    """Data room access grants for investors."""

    __tablename__ = "data_room_access"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("aip_projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"))

    # Access control
    access_level = Column(String(50), default="view", nullable=False)  # view, download, edit
    nda_signed = Column(Boolean, default=False, nullable=False)
    nda_signed_at = Column(DateTime)

    # Status
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, rejected, revoked
    granted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    granted_at = Column(DateTime)
    expires_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<DataRoomAccess user={self.user_id} project={self.project_id} ({self.status})>"


class DocumentAccessLog(Base):
    """Audit log for document access."""

    __tablename__ = "document_access_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)

    action = Column(String(50), nullable=False)  # view, download, preview
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="access_logs")

    def __repr__(self):
        return f"<DocumentAccessLog {self.action} doc={self.document_id} user={self.user_id}>"
