# routers/data_rooms.py
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.schemas import DataRoom, DataRoomCreate
from backend.crud import create_data_room, get_data_room
from backend.database import get_db

router = APIRouter(prefix="/data-rooms", tags=["data_rooms"])

@router.post("/", response_model=DataRoom)
def create(room: DataRoomCreate, db: Session = Depends(get_db)):
    return create_data_room(db, room)

@router.get("/{room_id}", response_model=DataRoom)
def read(room_id: int, db: Session = Depends(get_db)):
    db_room = get_data_room(db, room_id)
    if db_room is None:
        raise HTTPException(status_code=404, detail="Data room not found")
    # Parse strings back to lists/dicts
    access_users = [int(u) for u in db_room.access_users.split(",")] if db_room.access_users else []
    documents = json.loads(db_room.documents) if db_room.documents else {}
    return DataRoom(
        id=db_room.id,
        project_id=db_room.project_id,
        nda_required=db_room.nda_required,
        access_users=access_users,
        documents=documents,
        created_at=db_room.created_at
    )