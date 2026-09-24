import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class EventType(str, enum.Enum):
    CALL = "CALL"
    MESSAGE = "MESSAGE"
    MEETING = "MEETING"
    MOVEMENT = "MOVEMENT"
    OBSERVATION = "OBSERVATION"
    TRANSACTION = "TRANSACTION"
    INCIDENT = "INCIDENT"
    DOCUMENT = "DOCUMENT"
    OTHER = "OTHER"


class Certainty(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    REPORTED = "REPORTED"
    ESTIMATED = "ESTIMATED"
    UNKNOWN = "UNKNOWN"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(
        Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(Enum(EventType), nullable=False)
    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=True), nullable=True)
    location = Column(String(200), nullable=True)
    source = Column(String(200), nullable=True)
    certainty = Column(Enum(Certainty), default=Certainty.UNKNOWN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
