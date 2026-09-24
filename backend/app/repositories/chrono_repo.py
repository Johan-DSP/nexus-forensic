from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.chrono import Event
from app.schemas.chrono import EventCreate, EventUpdate


def get_event(db: Session, event_id: int) -> Optional[Event]:
    return db.query(Event).filter(Event.id == event_id).first()


def get_events_by_case(db: Session, case_id: int) -> List[Event]:
    return (
        db.query(Event)
        .filter(Event.case_id == case_id)
        .order_by(Event.start_datetime.asc())
        .all()
    )


def create_event(db: Session, case_id: int, event_in: EventCreate) -> Event:
    db_event = Event(**event_in.model_dump(), case_id=case_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def update_event(db: Session, db_event: Event, event_in: EventUpdate) -> Event:
    update_data = event_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)
    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, db_event: Event) -> Event:
    db.delete(db_event)
    db.commit()
    return db_event
