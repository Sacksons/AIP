"""Verifications router."""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.verification import VerificationRequest, VerificationCheck, VerificationEvent
from app.schemas.verification import (
    VerificationRequestCreate, VerificationRequestResponse,
    VerificationCheckCreate, VerificationCheckResponse,
    VerificationDecision, VerificationCheckUpdate
)
from .auth import require_auth

router = APIRouter(prefix="/verifications", tags=["Verifications"])


@router.post("/", response_model=VerificationRequestResponse, status_code=status.HTTP_201_CREATED)
def create_verification_request(
    request_data: VerificationRequestCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a verification request for project advancement."""
    project = db.query(Project).filter(Project.id == request_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    verification = VerificationRequest(
        project_id=request_data.project_id,
        from_level=project.verification_level,
        to_level=request_data.to_level,
        requested_by=current_user.id,
    )
    db.add(verification)
    db.commit()
    db.refresh(verification)

    # Log event
    event = VerificationEvent(
        request_id=verification.id,
        event_type="created",
        description=f"Verification request created: {verification.from_level} -> {verification.to_level}",
        created_by=current_user.id,
    )
    db.add(event)
    db.commit()

    return verification


@router.get("/", response_model=List[VerificationRequestResponse])
def list_verification_requests(
    status_filter: str = None,
    project_id: int = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """List verification requests."""
    query = db.query(VerificationRequest)

    if status_filter:
        query = query.filter(VerificationRequest.status == status_filter)
    if project_id:
        query = query.filter(VerificationRequest.project_id == project_id)

    return query.order_by(VerificationRequest.created_at.desc()).all()


@router.get("/{request_id}", response_model=VerificationRequestResponse)
def get_verification_request(
    request_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get verification request by ID."""
    verification = db.query(VerificationRequest).filter(
        VerificationRequest.id == request_id
    ).first()
    if not verification:
        raise HTTPException(status_code=404, detail="Verification request not found")
    return verification


@router.post("/{request_id}/checks", response_model=VerificationCheckResponse)
def add_verification_check(
    request_id: int,
    check_data: VerificationCheckCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Add a verification check to request."""
    verification = db.query(VerificationRequest).filter(
        VerificationRequest.id == request_id
    ).first()
    if not verification:
        raise HTTPException(status_code=404, detail="Verification request not found")

    check = VerificationCheck(
        request_id=request_id,
        check_type=check_data.check_type,
        check_name=check_data.check_name,
        description=check_data.description,
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


@router.put("/{request_id}/checks/{check_id}", response_model=VerificationCheckResponse)
def update_verification_check(
    request_id: int,
    check_id: int,
    check_update: VerificationCheckUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update verification check result."""
    check = db.query(VerificationCheck).filter(
        VerificationCheck.id == check_id,
        VerificationCheck.request_id == request_id
    ).first()
    if not check:
        raise HTTPException(status_code=404, detail="Check not found")

    check.status = check_update.status
    if check_update.score is not None:
        check.score = check_update.score
    if check_update.notes is not None:
        check.notes = check_update.notes
    if check_update.evidence_json is not None:
        check.evidence_json = check_update.evidence_json
    check.checked_by = current_user.id
    check.checked_at = datetime.utcnow()

    db.commit()
    db.refresh(check)
    return check


@router.post("/{request_id}/decision", response_model=VerificationRequestResponse)
def make_decision(
    request_id: int,
    decision_data: VerificationDecision,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Make a decision on verification request."""
    verification = db.query(VerificationRequest).filter(
        VerificationRequest.id == request_id
    ).first()
    if not verification:
        raise HTTPException(status_code=404, detail="Verification request not found")

    verification.decision = decision_data.decision
    verification.decision_notes = decision_data.decision_notes
    verification.decided_by = current_user.id
    verification.decided_at = datetime.utcnow()
    verification.status = "approved" if decision_data.decision == "approved" else "rejected"

    # Update project level if approved
    if decision_data.decision == "approved":
        project = db.query(Project).filter(Project.id == verification.project_id).first()
        if project:
            project.verification_level = verification.to_level

    # Log event
    event = VerificationEvent(
        request_id=verification.id,
        event_type=decision_data.decision,
        description=f"Verification {decision_data.decision}: {decision_data.decision_notes}",
        created_by=current_user.id,
    )
    db.add(event)

    db.commit()
    db.refresh(verification)
    return verification
