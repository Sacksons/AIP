# routers/verifications.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.schemas import Verification, VerificationCreate
from backend.database import get_db
from backend import models

router = APIRouter(prefix="/verifications", tags=["verifications"])


@router.get("/ping")
def ping():
    """Health check for verifications service."""
    return {"ok": True}


@router.post("/", response_model=Verification)
def create(verification: VerificationCreate, db: Session = Depends(get_db)):
    """Create a new verification record for a project."""
    # Check if project exists
    project = db.query(models.Project).filter(models.Project.id == verification.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create verification record
    db_verification = models.Verification(
        project_id=verification.project_id,
        level=verification.level,
        technical_readiness=verification.bankability.technical_readiness if verification.bankability else None,
        financial_robustness=verification.bankability.financial_robustness if verification.bankability else None,
        legal_clarity=verification.bankability.legal_clarity if verification.bankability else None,
        esg_compliance=verification.bankability.esg_compliance if verification.bankability else None,
        overall_score=verification.bankability.overall_score if verification.bankability else None,
        risk_flags=",".join(verification.bankability.risk_flags) if verification.bankability and verification.bankability.risk_flags else None,
        last_verified=verification.bankability.last_verified if verification.bankability else None
    )
    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)
    return db_verification


@router.get("/{verification_id}", response_model=Verification)
def read(verification_id: int, db: Session = Depends(get_db)):
    """Get a verification record by ID."""
    db_verification = db.query(models.Verification).filter(
        models.Verification.id == verification_id
    ).first()
    if db_verification is None:
        raise HTTPException(status_code=404, detail="Verification not found")
    return db_verification


@router.get("/project/{project_id}", response_model=List[Verification])
def list_by_project(project_id: int, db: Session = Depends(get_db)):
    """Get all verification records for a project."""
    # Check if project exists
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return db.query(models.Verification).filter(
        models.Verification.project_id == project_id
    ).all()


@router.get("/project/{project_id}/latest", response_model=Verification)
def get_latest(project_id: int, db: Session = Depends(get_db)):
    """Get the latest verification record for a project."""
    verification = db.query(models.Verification).filter(
        models.Verification.project_id == project_id
    ).order_by(models.Verification.id.desc()).first()

    if verification is None:
        raise HTTPException(status_code=404, detail="No verification found for project")
    return verification
