from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse
from app.repositories import case_repo

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(case_in: CaseCreate, db: Session = Depends(get_db)):
    db_case = case_repo.get_case_by_number(db, case_number=case_in.case_number)
    if db_case:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "CASE_ALREADY_EXISTS",
                "message": "A case with this number already exists",
            },
        )
    return case_repo.create_case(db, case_in=case_in)


@router.get("/", response_model=List[CaseResponse])
def read_cases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return case_repo.get_cases(db, skip=skip, limit=limit)


@router.get("/{case_id}", response_model=CaseResponse)
def read_case(case_id: int, db: Session = Depends(get_db)):
    db_case = case_repo.get_case(db, case_id=case_id)
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "CASE_NOT_FOUND", "message": "Case not found"},
        )
    return db_case


@router.put("/{case_id}", response_model=CaseResponse)
def update_case(case_id: int, case_in: CaseUpdate, db: Session = Depends(get_db)):
    db_case = case_repo.get_case(db, case_id=case_id)
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "CASE_NOT_FOUND", "message": "Case not found"},
        )
    return case_repo.update_case(db, db_case=db_case, case_in=case_in)


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(case_id: int, db: Session = Depends(get_db)):
    db_case = case_repo.get_case(db, case_id=case_id)
    if not db_case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "CASE_NOT_FOUND", "message": "Case not found"},
        )
    case_repo.delete_case(db, db_case=db_case)
    return None
