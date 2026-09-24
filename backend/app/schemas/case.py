from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from app.db.models.case import CaseStatus


class CaseBase(BaseModel):
    case_number: str = Field(
        ..., max_length=50, description="Identificador único del caso"
    )
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    status: CaseStatus = CaseStatus.OPEN


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[CaseStatus] = None


class CaseResponse(CaseBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
