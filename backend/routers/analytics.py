# routers/analytics.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas import AnalyticReport, AnalyticReportCreate
from backend.crud import create_analytic_report, get_analytic_report
from backend.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/", response_model=AnalyticReport)
def create(report: AnalyticReportCreate, db: Session = Depends(get_db)):
    return create_analytic_report(db, report)

@router.get("/{report_id}", response_model=AnalyticReport)
def read(report_id: int, db: Session = Depends(get_db)):
    db_report = get_analytic_report(db, report_id)
    if db_report is None:
        raise HTTPException(status_code=404, detail="Analytic report not found")
    return db_report