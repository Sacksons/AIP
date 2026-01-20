# routers/investors.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas import Investor, InvestorCreate
from backend.crud import create_investor, get_investor
from backend.database import get_db
from backend.models import Instrument, Sector

router = APIRouter(prefix="/investors", tags=["investors"])

@router.post("/", response_model=Investor)
def create(investor: InvestorCreate, db: Session = Depends(get_db)):
    return create_investor(db, investor)

@router.get("/{investor_id}", response_model=Investor)
def read(investor_id: int, db: Session = Depends(get_db)):
    db_inv = get_investor(db, investor_id)
    if db_inv is None:
        raise HTTPException(status_code=404, detail="Investor not found")
    # Map strings back to lists/enums
    return Investor(
        id=db_inv.id,
        fund_name=db_inv.fund_name,
        aum=db_inv.aum,
        ticket_size_min=db_inv.ticket_size_min,
        ticket_size_max=db_inv.ticket_size_max,
        instruments=[Instrument(i) for i in db_inv.instruments.split(",")],
        target_irr=db_inv.target_irr,
        country_focus=db_inv.country_focus.split(","),
        sector_focus=[Sector(s) for s in db_inv.sector_focus.split(",")],
        esg_constraints=db_inv.esg_constraints
    )