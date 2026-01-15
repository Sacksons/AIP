FastAPI app entrypoint (PythonAnywhere-friendly).

Run as: uvicorn main:app
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy import asc, desc, text
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Project as ProjectModel
from schemas import Project, ProjectCreate

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="AIPI API")


@app.on_event("startup")
def startup() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("DB tables ensured.")
    except Exception:
        logger.exception("DB init failed (site will still run; DB endpoints may fail).")


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
        return {"ok": True, "db": True}
    except Exception:
        return {"ok": True, "db": False}


@app.post("/projects", response_model=Project)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> ProjectModel:
    obj = ProjectModel(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/projects")
def list_projects(
    sector: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    verification_level: Optional[int] = Query(None),
    sort: str = Query("bankability_score desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    q = db.query(ProjectModel)

    if sector:
        q = q.filter(ProjectModel.sector.ilike(f"%{sector}%"))
    if country:
        q = q.filter(ProjectModel.country.ilike(f"%{country}%"))
    if verification_level is not None:
        q = q.filter(ProjectModel.verification_level >= verification_level)
    if min_score is not None:
        q = q.filter(ProjectModel.bankability_score >= min_score)

    field, direction = (sort.rsplit(" ", 1) if " " in sort else (sort, "asc"))
    col = getattr(ProjectModel, field, None)
    if not col:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {field}")
    q = q.order_by(desc(col) if direction.lower() == "desc" else asc(col))

    total = q.count()
    items = q.offset((page - 1) * limit).limit(limit).all()
    return {
        "projects": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
    }


# Serve static frontend if present (Next.js export copied into backend/static)
_static_dir = Path(__file__).resolve().parent / "static"
if _static_dir.exists():
    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="frontend")
PY

# Compile + import test (must pass)
set -a; source .env; set +a
python -m py_compile database.py models.py schemas.py main.py || exit 1
python -c "import main; print('IMPORT OK, app:', hasattr(main, 'app'))" || exit 1

# Reload website (do NOT run uvicorn manually on :8000)
 /home/sackson/.virtualenvs/api-venv/bin/pa website reload --domain api-sackson.pythonanywhere.com
tail -n 60 /var/log/api-sackson.pythonanywhere.com.error.log
