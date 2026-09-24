from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.evidentia import Evidence, AuditLog, AuditAction


def create_audit_log(
    db: Session,
    action: AuditAction,
    entity_type: str,
    entity_id: int,
    case_id: int = None,
    meta: dict = None,
):
    log = AuditLog(
        case_id=case_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_=meta or {},
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_evidence(db: Session, evidence_id: int) -> Optional[Evidence]:
    return db.query(Evidence).filter(Evidence.id == evidence_id).first()


def get_evidence_by_case(db: Session, case_id: int) -> List[Evidence]:
    return db.query(Evidence).filter(Evidence.case_id == case_id).all()


def create_evidence(db: Session, evidence_data: dict) -> Evidence:
    db_ev = Evidence(**evidence_data)
    db.add(db_ev)
    db.commit()
    db.refresh(db_ev)
    return db_ev


def delete_evidence(db: Session, db_ev: Evidence) -> Evidence:
    db.delete(db_ev)
    db.commit()
    return db_ev
