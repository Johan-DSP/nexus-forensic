from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.chrono import EventCreate, EventUpdate, EventResponse, OverlapReport
from app.repositories import chrono_repo, case_repo
from app.services import chrono_service

router = APIRouter(tags=["chrono"])


def verify_case_exists(db: Session, case_id: int):
    if not case_repo.get_case(db, case_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "CASE_NOT_FOUND", "message": "Case not found"},
        )


@router.post(
    "/api/cases/{case_id}/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(case_id: int, event_in: EventCreate, db: Session = Depends(get_db)):
    verify_case_exists(db, case_id)
    if event_in.end_datetime and event_in.end_datetime <= event_in.start_datetime:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_DATES",
                "message": "End datetime must be after start datetime",
            },
        )
    return chrono_repo.create_event(db, case_id=case_id, event_in=event_in)


@router.get("/api/cases/{case_id}/events", response_model=List[EventResponse])
def read_case_events(case_id: int, db: Session = Depends(get_db)):
    verify_case_exists(db, case_id)
    return chrono_repo.get_events_by_case(db, case_id)


@router.get("/api/events/{event_id}", response_model=EventResponse)
def read_event(event_id: int, db: Session = Depends(get_db)):
    event = chrono_repo.get_event(db, event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail={"error": "EVENT_NOT_FOUND", "message": "Event not found"},
        )
    return event


@router.put("/api/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_in: EventUpdate, db: Session = Depends(get_db)):
    event = chrono_repo.get_event(db, event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail={"error": "EVENT_NOT_FOUND", "message": "Event not found"},
        )
    return chrono_repo.update_event(db, db_event=event, event_in=event_in)


@router.delete("/api/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = chrono_repo.get_event(db, event_id)
    if not event:
        raise HTTPException(
            status_code=404,
            detail={"error": "EVENT_NOT_FOUND", "message": "Event not found"},
        )
    chrono_repo.delete_event(db, db_event=event)
    return None


@router.get("/api/cases/{case_id}/events/overlaps", response_model=List[OverlapReport])
def check_case_overlaps(case_id: int, db: Session = Depends(get_db)):
    verify_case_exists(db, case_id)
    events = chrono_repo.get_events_by_case(db, case_id)
    return chrono_service.detect_overlaps(events)
