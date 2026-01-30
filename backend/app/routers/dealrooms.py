"""Deal rooms router."""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.dealroom import DealRoom, Message, Meeting
from app.schemas.dealroom import (
    DealRoomCreate, DealRoomResponse, DealRoomUpdate,
    MessageCreate, MessageResponse,
    MeetingCreate, MeetingResponse, MeetingUpdate
)
from .auth import require_auth

router = APIRouter(prefix="/dealrooms", tags=["Deal Rooms"])


@router.post("/", response_model=DealRoomResponse, status_code=status.HTTP_201_CREATED)
def create_deal_room(
    room_data: DealRoomCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new deal room."""
    project = db.query(Project).filter(Project.id == room_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    deal_room = DealRoom(
        project_id=room_data.project_id,
        investor_org_id=room_data.investor_org_id,
        sponsor_org_id=project.sponsor_org_id,
        name=room_data.name or f"Deal Room - {project.name}",
        created_by=current_user.id,
    )
    db.add(deal_room)
    db.commit()
    db.refresh(deal_room)
    return deal_room


@router.get("/", response_model=List[DealRoomResponse])
def list_my_deal_rooms(
    status_filter: str = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """List deal rooms for current user."""
    # This would need to filter by user's organizations
    query = db.query(DealRoom)
    if status_filter:
        query = query.filter(DealRoom.status == status_filter)
    return query.order_by(DealRoom.updated_at.desc()).all()


@router.get("/{room_id}", response_model=DealRoomResponse)
def get_deal_room(
    room_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get deal room by ID."""
    room = db.query(DealRoom).filter(DealRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Deal room not found")
    return room


@router.put("/{room_id}", response_model=DealRoomResponse)
def update_deal_room(
    room_id: int,
    room_data: DealRoomUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update deal room."""
    room = db.query(DealRoom).filter(DealRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Deal room not found")

    for field, value in room_data.model_dump(exclude_unset=True).items():
        setattr(room, field, value)

    if room_data.status == "closed":
        room.closed_at = datetime.utcnow()

    db.commit()
    db.refresh(room)
    return room


# Messages
@router.post("/{room_id}/messages", response_model=MessageResponse)
def send_message(
    room_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Send a message in deal room."""
    room = db.query(DealRoom).filter(DealRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Deal room not found")

    message = Message(
        deal_room_id=room_id,
        sender_id=current_user.id,
        content=message_data.content,
        message_type=message_data.message_type,
    )
    db.add(message)

    # Update room timestamp
    room.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)
    return message


@router.get("/{room_id}/messages", response_model=List[MessageResponse])
def get_messages(
    room_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get messages in deal room."""
    return db.query(Message).filter(
        Message.deal_room_id == room_id
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()


# Meetings
@router.post("/{room_id}/meetings", response_model=MeetingResponse)
def schedule_meeting(
    room_id: int,
    meeting_data: MeetingCreate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Schedule a meeting in deal room."""
    room = db.query(DealRoom).filter(DealRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Deal room not found")

    meeting = Meeting(
        deal_room_id=room_id,
        title=meeting_data.title,
        description=meeting_data.description,
        meeting_type=meeting_data.meeting_type,
        scheduled_at=meeting_data.scheduled_at,
        duration_minutes=meeting_data.duration_minutes,
        timezone=meeting_data.timezone,
        location=meeting_data.location,
        video_link=meeting_data.video_link,
        attendees=meeting_data.attendees or [],
        agenda=meeting_data.agenda,
        created_by=current_user.id,
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


@router.get("/{room_id}/meetings", response_model=List[MeetingResponse])
def get_meetings(
    room_id: int,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get meetings in deal room."""
    return db.query(Meeting).filter(
        Meeting.deal_room_id == room_id
    ).order_by(Meeting.scheduled_at).all()


@router.put("/{room_id}/meetings/{meeting_id}", response_model=MeetingResponse)
def update_meeting(
    room_id: int,
    meeting_id: int,
    meeting_data: MeetingUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update a meeting."""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.deal_room_id == room_id
    ).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    for field, value in meeting_data.model_dump(exclude_unset=True).items():
        setattr(meeting, field, value)

    db.commit()
    db.refresh(meeting)
    return meeting
