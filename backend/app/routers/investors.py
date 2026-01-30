"""Investors router."""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.organization import OrgMember
from app.models.investor import InvestorPreferences, Match
from app.schemas.investor import (
    InvestorPreferencesCreate, InvestorPreferencesResponse,
    MatchResponse, MatchInterest
)
from .auth import require_auth

router = APIRouter(prefix="/investors", tags=["Investors"])


@router.post("/preferences", response_model=InvestorPreferencesResponse)
def create_or_update_preferences(
    prefs_data: InvestorPreferencesCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create or update investor preferences."""
    # Get user's investor org
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.role == "investor"
    ).first()
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="User is not associated with an investor organization"
        )

    org_id = membership.org_id

    prefs = db.query(InvestorPreferences).filter(
        InvestorPreferences.org_id == org_id
    ).first()

    if prefs:
        for field, value in prefs_data.model_dump(exclude_unset=True).items():
            setattr(prefs, field, value)
    else:
        prefs = InvestorPreferences(
            org_id=org_id,
            **prefs_data.model_dump()
        )
        db.add(prefs)

    db.commit()
    db.refresh(prefs)
    return prefs


@router.get("/preferences", response_model=InvestorPreferencesResponse)
def get_my_preferences(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get current user's investor preferences."""
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.role == "investor"
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Investor preferences not found")

    prefs = db.query(InvestorPreferences).filter(
        InvestorPreferences.org_id == membership.org_id
    ).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")

    return prefs


@router.get("/preferences/{org_id}", response_model=InvestorPreferencesResponse)
def get_org_preferences(
    org_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get investor preferences by organization ID."""
    prefs = db.query(InvestorPreferences).filter(
        InvestorPreferences.org_id == org_id
    ).first()
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return prefs


# Match endpoints
@router.get("/matches", response_model=List[MatchResponse])
def get_my_matches(
    status_filter: str = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get matches for current investor."""
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.role == "investor"
    ).first()
    if not membership:
        return []

    query = db.query(Match).filter(Match.investor_org_id == membership.org_id)
    if status_filter:
        query = query.filter(Match.status == status_filter)

    return query.order_by(Match.match_score.desc()).all()


@router.get("/matches/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get match by ID."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Mark as viewed
    if not match.viewed_at:
        match.viewed_at = datetime.utcnow()
        match.status = "viewed"
        db.commit()
        db.refresh(match)

    return match


@router.post("/matches/{match_id}/interest", response_model=MatchResponse)
def express_interest(
    match_id: int,
    interest_data: MatchInterest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Express interest in a match."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match.investor_interest = interest_data.interest
    match.responded_at = datetime.utcnow()

    if interest_data.interest == "interested":
        match.status = "interested"

    db.commit()
    db.refresh(match)
    return match
