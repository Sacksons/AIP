"""Projects router."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectFinancials
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    ProjectFinancialsCreate, ProjectFinancialsResponse
)
from .auth import require_auth

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new project."""
    project = Project(
        sponsor_org_id=project_data.sponsor_org_id,
        name=project_data.name,
        sector=project_data.sector,
        sub_sector=project_data.sub_sector,
        country=project_data.country,
        city=project_data.city,
        latitude=project_data.latitude,
        longitude=project_data.longitude,
        summary=project_data.summary,
        description=project_data.description,
        sdg_tags=project_data.sdg_tags,
        capacity_value=project_data.capacity_value,
        capacity_unit=project_data.capacity_unit,
        impact_statement=project_data.impact_statement,
        investment_usd=project_data.investment_usd,
        expected_roi_pct=project_data.expected_roi_pct,
        payback_years=project_data.payback_years,
        created_by=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/", response_model=ProjectListResponse)
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sector: Optional[str] = None,
    country: Optional[str] = None,
    verification_level: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
):
    """List projects with pagination and filters."""
    query = db.query(Project)

    if sector:
        query = query.filter(Project.sector == sector)
    if country:
        query = query.filter(Project.country == country)
    if verification_level:
        query = query.filter(Project.verification_level == verification_level)
    if status_filter:
        query = query.filter(Project.status == status_filter)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return ProjectListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get project by ID."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Delete project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()


@router.post("/{project_id}/financials", response_model=ProjectFinancialsResponse)
def create_or_update_financials(
    project_id: int,
    financials_data: ProjectFinancialsCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create or update project financials."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    financials = db.query(ProjectFinancials).filter(
        ProjectFinancials.project_id == project_id
    ).first()

    if financials:
        for field, value in financials_data.model_dump(exclude_unset=True).items():
            setattr(financials, field, value)
    else:
        financials = ProjectFinancials(
            project_id=project_id,
            **financials_data.model_dump()
        )
        db.add(financials)

    db.commit()
    db.refresh(financials)
    return financials


@router.get("/{project_id}/financials", response_model=ProjectFinancialsResponse)
def get_financials(project_id: int, db: Session = Depends(get_db)):
    """Get project financials."""
    financials = db.query(ProjectFinancials).filter(
        ProjectFinancials.project_id == project_id
    ).first()
    if not financials:
        raise HTTPException(status_code=404, detail="Financials not found")
    return financials
