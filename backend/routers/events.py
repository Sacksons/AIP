# routers/events.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.schemas import Event, EventCreate
from backend.crud import create_event, get_event
from backend.database import get_db
from backend import models

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=Event)
def create(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new event."""
    return create_event(db, event)


@router.get("/{event_id}", response_model=Event)
def read(event_id: int, db: Session = Depends(get_db)):
    """Get an event by ID."""
    db_event = get_event(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    # Parse strings back to lists
    projects_involved = [int(p) for p in db_event.projects_involved.split(",")] if db_event.projects_involved else []
    return Event(
        id=db_event.id,
        name=db_event.name,
        description=db_event.description,
        event_date=db_event.event_date,
        type=db_event.type,
        projects_involved=projects_involved
    )


@router.get("/", response_model=List[Event])
def list_events(
    skip: int = 0,
    limit: int = 100,
    event_type: str = None,
    db: Session = Depends(get_db)
):
    """List events with optional filtering."""
    query = db.query(models.Event)
    if event_type:
        query = query.filter(models.Event.type == event_type)
    return query.offset(skip).limit(limit).all()
