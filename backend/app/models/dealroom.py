"""Deal room models for investor-sponsor negotiations."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class DealRoom(Base):
    """Private deal room for investor-sponsor negotiations."""

    __tablename__ = "deal_rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    project_id = Column(Integer, ForeignKey("aip_projects.id", ondelete="CASCADE"), nullable=False)
    investor_org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    sponsor_org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Room details
    name = Column(String(255))
    status = Column(String(50), default="active", nullable=False)  # active, archived, closed

    # Deal status
    deal_stage = Column(String(100), default="initial_contact")  # initial_contact, due_diligence, negotiation, term_sheet, closing
    deal_value_usd = Column(String(50))  # Estimated deal size

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime)

    # Relationships
    project = relationship("Project", back_populates="dealrooms")
    messages = relationship("Message", back_populates="deal_room", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="deal_room", cascade="all, delete-orphan")
    term_sheets = relationship("TermSheet", back_populates="deal_room", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DealRoom {self.uuid[:8]} ({self.deal_stage})>"


class Message(Base):
    """Message within a deal room."""

    __tablename__ = "deal_room_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deal_room_id = Column(Integer, ForeignKey("deal_rooms.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)

    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, file, system

    # File attachment (if message_type == 'file')
    attachment_name = Column(String(255))
    attachment_s3_key = Column(String(500))
    attachment_size = Column(Integer)

    # Read status tracking (JSON array of user IDs who have read)
    read_by = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    deal_room = relationship("DealRoom", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.id} in room {self.deal_room_id}>"


class Meeting(Base):
    """Scheduled meeting within a deal room."""

    __tablename__ = "deal_room_meetings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    deal_room_id = Column(Integer, ForeignKey("deal_rooms.id", ondelete="CASCADE"), nullable=False)

    # Meeting details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    meeting_type = Column(String(50), default="video_call")  # video_call, in_person, phone

    # Scheduling
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50), default="UTC")

    # Location/link
    location = Column(String(500))  # Physical address or video link
    video_link = Column(String(500))

    # Attendees (JSON array of user IDs)
    attendees = Column(JSON, default=list)
    confirmed_attendees = Column(JSON, default=list)

    # Status
    status = Column(String(50), default="scheduled")  # scheduled, cancelled, completed

    # Notes
    agenda = Column(Text)
    meeting_notes = Column(Text)

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    deal_room = relationship("DealRoom", back_populates="meetings")

    def __repr__(self):
        return f"<Meeting {self.title} at {self.scheduled_at}>"


class TermSheet(Base):
    """Term sheet document and signatures."""

    __tablename__ = "term_sheets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    deal_room_id = Column(Integer, ForeignKey("deal_rooms.id", ondelete="CASCADE"), nullable=False)

    # Document
    version = Column(Integer, default=1, nullable=False)
    title = Column(String(255), nullable=False)
    s3_key = Column(String(500))
    content_json = Column(JSON)  # Structured term sheet data

    # Key terms
    investment_amount_usd = Column(String(100))
    equity_percentage = Column(String(50))
    valuation_usd = Column(String(100))
    key_conditions = Column(Text)

    # Status
    status = Column(String(50), default="draft")  # draft, pending_signature, partially_signed, fully_signed, expired

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime)

    # Relationships
    deal_room = relationship("DealRoom", back_populates="term_sheets")
    signatures = relationship("Signature", back_populates="term_sheet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TermSheet v{self.version} ({self.status})>"


class Signature(Base):
    """Electronic signature on a term sheet."""

    __tablename__ = "term_sheet_signatures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    term_sheet_id = Column(Integer, ForeignKey("term_sheets.id", ondelete="CASCADE"), nullable=False)
    signer_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))

    # Signature details
    signer_name = Column(String(255), nullable=False)
    signer_title = Column(String(100))
    signer_email = Column(String(255))

    # Signature data
    signature_data = Column(Text)  # Base64 encoded signature image or digital signature
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Status
    status = Column(String(50), default="pending")  # pending, signed, declined
    signed_at = Column(DateTime)
    declined_at = Column(DateTime)
    decline_reason = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    term_sheet = relationship("TermSheet", back_populates="signatures")

    def __repr__(self):
        return f"<Signature {self.signer_name} ({self.status})>"
