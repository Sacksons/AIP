# routers/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.schemas import Project, ProjectCreate
from backend.crud import create_project, get_project
from backend.database import get_db
from backend import models

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=Project)
def create(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project."""
    return create_project(db, project)


@router.get("/{project_id}", response_model=Project)
def read(project_id: int, db: Session = Depends(get_db)):
    """Get a project by ID."""
    db_project = get_project(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project


@router.get("/", response_model=List[Project])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    sector: str = None,
    country: str = None,
    stage: str = None,
    db: Session = Depends(get_db)
):
    """List projects with optional filtering."""
    query = db.query(models.Project)

    if sector:
        query = query.filter(models.Project.sector == sector)
    if country:
        query = query.filter(models.Project.country == country)
    if stage:
        query = query.filter(models.Project.stage == stage)

    return query.offset(skip).limit(limit).all()
