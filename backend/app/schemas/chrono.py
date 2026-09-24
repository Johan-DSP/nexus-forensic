from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List
from app.db.models.chrono import EventType, Certainty


class EventBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    event_type: EventType
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    source: Optional[str] = Field(None, max_length=200)
    certainty: Certainty = Certainty.UNKNOWN


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    source: Optional[str] = Field(None, max_length=200)
    certainty: Optional[Certainty] = None


class EventResponse(EventBase):
    id: int
    case_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class OverlapReport(BaseModel):
    event_1_id: int
    event_2_id: int
    message: str = "POSIBLE SOLAPAMIENTO TEMPORAL"
    overlap_minutes: float
