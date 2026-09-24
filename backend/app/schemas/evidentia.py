from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Dict, Any


# --- EVIDENCE ---
class EvidenceBase(BaseModel):
    description: Optional[str] = None
    source: Optional[str] = Field(None, max_length=200)
    acquired_at: Optional[datetime] = None


class EvidenceResponse(EvidenceBase):
    id: int
    case_id: int
    original_filename: str
    stored_filename: str
    mime_type: str
    file_size: int
    sha256: str
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class VerifyResponse(BaseModel):
    match: bool
    stored_hash: str
    current_hash: str
    message: str


# --- AUDIT LOG ---
class AuditLogBase(BaseModel):
    case_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    metadata_: Optional[Dict[str, Any]] = Field(
    default_factory=dict,
    validation_alias="metadata_",
    serialization_alias="metadata",
)


class AuditLogResponse(AuditLogBase):
    id: int
    user_id: str
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
