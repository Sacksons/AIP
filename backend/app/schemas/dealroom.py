"""Deal room schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DealRoomCreate(BaseModel):
    """Schema for creating a deal room."""
    project_id: int
    investor_org_id: int
    name: Optional[str] = Field(None, max_length=255)


class DealRoomResponse(BaseModel):
    """Schema for deal room response."""
    id: int
    uuid: str
    project_id: int
    investor_org_id: int
    sponsor_org_id: int
    name: Optional[str] = None
    status: str
    deal_stage: str
    deal_value_usd: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    content: str = Field(..., min_length=1)
    message_type: str = "text"


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    deal_room_id: int
    sender_id: int
    content: str
    message_type: str
    attachment_name: Optional[str] = None
    attachment_s3_key: Optional[str] = None
    attachment_size: Optional[int] = None
    read_by: Optional[List[int]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingCreate(BaseModel):
    """Schema for creating a meeting."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    meeting_type: str = "video_call"
    scheduled_at: datetime
    duration_minutes: int = 60
    timezone: str = "UTC"
    location: Optional[str] = Field(None, max_length=500)
    video_link: Optional[str] = Field(None, max_length=500)
    attendees: Optional[List[int]] = None
    agenda: Optional[str] = None


class MeetingResponse(BaseModel):
    """Schema for meeting response."""
    id: int
    uuid: str
    deal_room_id: int
    title: str
    description: Optional[str] = None
    meeting_type: str
    scheduled_at: datetime
    duration_minutes: int
    timezone: str
    location: Optional[str] = None
    video_link: Optional[str] = None
    attendees: Optional[List[int]] = None
    confirmed_attendees: Optional[List[int]] = None
    status: str
    agenda: Optional[str] = None
    meeting_notes: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DealRoomUpdate(BaseModel):
    """Schema for updating a deal room."""
    name: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, pattern="^(active|archived|closed)$")
    deal_stage: Optional[str] = None
    deal_value_usd: Optional[str] = None


class MeetingUpdate(BaseModel):
    """Schema for updating a meeting."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    location: Optional[str] = Field(None, max_length=500)
    video_link: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(scheduled|cancelled|completed)$")
    agenda: Optional[str] = None
    meeting_notes: Optional[str] = None
