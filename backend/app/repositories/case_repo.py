from sqlalchemy.orm import Session
from app.db.models.case import Case
from app.schemas.case import CaseCreate, CaseUpdate
from typing import List, Optional


def get_case(db: Session, case_id: int) -> Optional[Case]:
    return db.query(Case).filter(Case.id == case_id).first()


def get_case_by_number(db: Session, case_number: str) -> Optional[Case]:
    return db.query(Case).filter(Case.case_number == case_number).first()


def get_cases(db: Session, skip: int = 0, limit: int = 100) -> List[Case]:
    return db.query(Case).offset(skip).limit(limit).all()


def create_case(db: Session, case_in: CaseCreate) -> Case:
    db_case = Case(**case_in.model_dump())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


def update_case(db: Session, db_case: Case, case_in: CaseUpdate) -> Case:
    update_data = case_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_case, field, value)
    db.commit()
    db.refresh(db_case)
    return db_case


def delete_case(db: Session, db_case: Case) -> Case:
    db.delete(db_case)
    db.commit()
    return db_case
