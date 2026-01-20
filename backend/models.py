# models.py
from sqlalchemy import Column, Integer, String, Float, Date, Enum as SQLEnum, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base  # Import once
from enum import Enum as PyEnum
import datetime  # Change to this to avoid shadowing

class Sector(PyEnum):
    ENERGY = "Energy"
    MINING = "Mining"
    WATER = "Water"
    TRANSPORT = "Transport"
    PORTS = "Ports"
    RAIL = "Rail"
    ROADS = "Roads"
    AGRICULTURE = "Agriculture"
    HEALTH = "Health"

class ProjectStage(PyEnum):
    CONCEPT = "Concept"
    FEASIBILITY = "Feasibility"
    PROCUREMENT = "Procurement"
    CONSTRUCTION = "Construction"
    OPERATION = "Operation"

class VerificationLevel(PyEnum):
    V0_SUBMITTED = "V0: Submitted"
    V1_SPONSOR_VERIFIED = "V1: Sponsor Identity Verified"
    V2_DOCUMENTS_VERIFIED = "V2: Documents Verified"
    V3_BANKABILITY_SCREENED = "V3: Bankability Screened"

class Instrument(PyEnum):
    EQUITY = "Equity"
    DEBT = "Debt"
    MEZZANINE = "Mezzanine"

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    sector = Column(SQLEnum(Sector))
    country = Column(String)
    region = Column(String, nullable=True)
    gps_location = Column(String, nullable=True)
    stage = Column(SQLEnum(ProjectStage))
    estimated_capex = Column(Float)
    funding_gap = Column(Float, nullable=True)
    timeline_fid = Column(Date, nullable=True)
    timeline_cod = Column(Date, nullable=True)
    revenue_model = Column(String)
    offtaker = Column(String, nullable=True)
    tariff_mechanism = Column(String, nullable=True)
    concession_length = Column(Integer, nullable=True)
    fx_exposure = Column(String, nullable=True)
    political_risk_mitigation = Column(String, nullable=True)
    sovereign_support = Column(String, nullable=True)
    technology = Column(String, nullable=True)
    epc_status = Column(String, nullable=True)
    land_acquisition_status = Column(String, nullable=True)
    esg_category = Column(String, nullable=True)
    permits_status = Column(String, nullable=True)
    attachments = Column(String, nullable=True)  # JSON string for dict
    created_at = Column(Date, default=datetime.date.today)
    updated_at = Column(Date, default=datetime.date.today)
    timeline_fid = Column(Date, nullable=True)
    timeline_cod = Column(Date, nullable=True)
    created_at = Column(Date, default=datetime.date.today)
    updated_at = Column(Date, default=datetime.date.today)

class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    level = Column(SQLEnum(VerificationLevel))
    technical_readiness = Column(Integer, nullable=True)
    financial_robustness = Column(Integer, nullable=True)
    legal_clarity = Column(Integer, nullable=True)
    esg_compliance = Column(Integer, nullable=True)
    overall_score = Column(Float, nullable=True)
    risk_flags = Column(String, nullable=True)  # Comma-separated
    last_verified = Column(Date)

    project = relationship("Project")
    last_verified = Column(Date)

class Investor(Base):
    __tablename__ = "investors"

    id = Column(Integer, primary_key=True)
    fund_name = Column(String)
    aum = Column(Float, nullable=True)
    ticket_size_min = Column(Float)
    ticket_size_max = Column(Float)
    instruments = Column(String)  # Comma-separated enums
    target_irr = Column(Float, nullable=True)
    country_focus = Column(String)  # Comma-separated
    sector_focus = Column(String)  # Comma-separated
    esg_constraints = Column(String, nullable=True)

class Introduction(Base):
    __tablename__ = "introductions"

    id = Column(Integer, primary_key=True)
    investor_id = Column(Integer, ForeignKey("investors.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    message = Column(String, nullable=True)
    nda_executed = Column(Integer, default=0)  # Boolean as int
    sponsor_approved = Column(Integer, default=0)
    status = Column(String, default="Pending")

    investor = relationship("Investor")
    project = relationship("Project")

# models.py (add after existing classes)
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

class DataRoom(Base):
    __tablename__ = "data_rooms"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    nda_required = Column(Boolean, default=True)
    access_users = Column(String, nullable=True)  # Comma-separated user IDs
    documents = Column(String, nullable=True)  # JSON of {"name": "S3_key"}
    created_at = Column(DateTime, default=datetime.datetime.now)

    project = relationship("Project")

class AnalyticReport(Base):
    __tablename__ = "analytic_reports"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    sector = Column(SQLEnum(Sector), nullable=True)
    country = Column(String, nullable=True)
    content = Column(String)  # JSON or markdown for dashboards/league tables
    created_at = Column(DateTime, default=datetime.datetime.now)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    date = Column(Date)
    type = Column(String)  # e.g., "Roundtable", "Forum"
    projects_involved = Column(String, nullable=True)  # Comma-separated project IDs
    event_date = Column(Date)
# models.py (add)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # e.g., "admin", "investor", "sponsor"

# models.py (update Event class)
class Event(Base):
    __tablename__ = 'events'  # Ensure unique tablename if needed
    __table_args__ = {'extend_existing': True}  # This line fixes the redefinition error

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    event_date = Column(Date)
    type = Column(String)
    projects_involved = Column(String, nullable=True)