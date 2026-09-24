import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.database import get_db
from app.core.config import settings
from app.schemas.evidentia import EvidenceResponse, VerifyResponse
from app.repositories import evidentia_repo, case_repo
from app.db.models.evidentia import AuditAction
from app.services import hashing_service

router = APIRouter(tags=["evidentia"])


def verify_case_exists(db: Session, case_id: int):
    if not case_repo.get_case(db, case_id):
        raise HTTPException(
            status_code=404,
            detail={"error": "CASE_NOT_FOUND", "message": "Case not found"},
        )


@router.post(
    "/api/cases/{case_id}/evidence",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_evidence(
    case_id: int,
    file: UploadFile = File(...),
    description: str = Form(None),
    source: str = Form(None),
    acquired_at: datetime = Form(None),
    db: Session = Depends(get_db),
):
    verify_case_exists(db, case_id)

    # Crear carpeta de almacenamiento si no existe
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)

    # Generar nombre seguro e inmutable
    file_ext = os.path.splitext(file.filename)[1]
    stored_filename = f"{uuid.uuid4().hex}{file_ext}"
    storage_path = os.path.join(settings.STORAGE_PATH, stored_filename)

    # Validar tamaño y calcular hash
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    if file_size > (settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024):
        raise HTTPException(status_code=413, detail="File too large")

    file.file.seek(0)
    sha256_hash = hashing_service.calculate_sha256(file.file)

    # Guardar en disco
    with open(storage_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Guardar en base de datos
    evidence_data = {
        "case_id": case_id,
        "original_filename": file.filename,
        "stored_filename": stored_filename,
        "mime_type": file.content_type,
        "file_size": file_size,
        "sha256": sha256_hash,
        "storage_path": storage_path,
        "description": description,
        "source": source,
        "acquired_at": acquired_at,
    }

    db_evidence = evidentia_repo.create_evidence(db, evidence_data)
    evidentia_repo.create_audit_log(
        db,
        AuditAction.UPLOAD,
        "EVIDENCE",
        db_evidence.id,
        case_id,
        {"hash": sha256_hash},
    )

    return db_evidence


@router.get("/api/cases/{case_id}/evidence", response_model=List[EvidenceResponse])
def get_case_evidence(case_id: int, db: Session = Depends(get_db)):
    verify_case_exists(db, case_id)
    return evidentia_repo.get_evidence_by_case(db, case_id)


@router.get("/api/evidence/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(evidence_id: int, db: Session = Depends(get_db)):
    evidence = evidentia_repo.get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=404,
            detail={"error": "EVIDENCE_NOT_FOUND", "message": "Evidence not found"},
        )
    return evidence


@router.post("/api/evidence/{evidence_id}/verify", response_model=VerifyResponse)
def verify_evidence_integrity(evidence_id: int, db: Session = Depends(get_db)):
    evidence = evidentia_repo.get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    try:
        current_hash = hashing_service.calculate_sha256_from_path(evidence.storage_path)
    except FileNotFoundError:
        evidentia_repo.create_audit_log(
            db,
            AuditAction.VERIFY,
            "EVIDENCE",
            evidence.id,
            evidence.case_id,
            {"status": "FILE_MISSING"},
        )
        raise HTTPException(
            status_code=404, detail="Physical file missing from storage"
        )

    match = current_hash == evidence.sha256
    status_msg = (
        "INTEGRIDAD VERIFICADA - HASH COINCIDE" if match else "INTEGRITY_MISMATCH"
    )

    evidentia_repo.create_audit_log(
        db,
        AuditAction.VERIFY,
        "EVIDENCE",
        evidence.id,
        evidence.case_id,
        {"match": match, "stored_hash": evidence.sha256, "current_hash": current_hash},
    )

    return {
        "match": match,
        "stored_hash": evidence.sha256,
        "current_hash": current_hash,
        "message": status_msg,
    }


@router.delete("/api/evidence/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evidence(evidence_id: int, db: Session = Depends(get_db)):
    evidence = evidentia_repo.get_evidence(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    evidentia_repo.delete_evidence(db, evidence)
    evidentia_repo.create_audit_log(
        db, AuditAction.DELETE, "EVIDENCE", evidence_id, evidence.case_id
    )
    return None
