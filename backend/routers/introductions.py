# routers/introductions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas import Introduction, IntroductionCreate
from backend.crud import create_introduction, get_introduction
from backend.database import get_db

router = APIRouter(prefix="/introductions", tags=["introductions"])

@router.post("/", response_model=Introduction)
def create(intro: IntroductionCreate, db: Session = Depends(get_db)):
    return create_introduction(db, intro)

@router.get("/{intro_id}", response_model=Introduction)
def read(intro_id: int, db: Session = Depends(get_db)):
    db_intro = get_introduction(db, intro_id)
    if db_intro is None:
        raise HTTPException(status_code=404, detail="Introduction not found")
    return Introduction(
        id=db_intro.id,
        investor_id=db_intro.investor_id,
        project_id=db_intro.project_id,
        message=db_intro.message,
        nda_executed=bool(db_intro.nda_executed),
        sponsor_approved=bool(db_intro.sponsor_approved),
        status=db_intro.status
    )