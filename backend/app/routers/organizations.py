"""Organizations router."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization, OrgMember
from app.schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    OrgMemberCreate, OrgMemberResponse
)
from .auth import require_auth

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new organization."""
    org = Organization(
        name=org_data.name,
        org_type=org_data.org_type,
        country_code=org_data.country_code,
        registration_no=org_data.registration_no,
        website=org_data.website,
        address=org_data.address,
        created_by=current_user.id,
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    # Add creator as owner
    member = OrgMember(
        org_id=org.id,
        user_id=current_user.id,
        role=org_data.org_type,
        is_owner=True,
    )
    db.add(member)
    db.commit()

    return org


@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    org_type: str = None,
    db: Session = Depends(get_db)
):
    """List all organizations."""
    query = db.query(Organization)
    if org_type:
        query = query.filter(Organization.org_type == org_type)
    return query.offset(skip).limit(limit).all()


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    """Get organization by ID."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.put("/{org_id}", response_model=OrganizationResponse)
def update_organization(
    org_id: int,
    org_data: OrganizationUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update organization."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    for field, value in org_data.model_dump(exclude_unset=True).items():
        setattr(org, field, value)

    db.commit()
    db.refresh(org)
    return org


@router.post("/{org_id}/members", response_model=OrgMemberResponse)
def add_member(
    org_id: int,
    member_data: OrgMemberCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Add member to organization."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    member = OrgMember(
        org_id=org_id,
        user_id=member_data.user_id,
        role=member_data.role,
        title=member_data.title,
        is_owner=member_data.is_owner,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/{org_id}/members", response_model=List[OrgMemberResponse])
def list_members(org_id: int, db: Session = Depends(get_db)):
    """List organization members."""
    return db.query(OrgMember).filter(OrgMember.org_id == org_id).all()
