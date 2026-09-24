from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.nexus import (
    EntityCreate,
    EntityUpdate,
    EntityResponse,
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipResponse,
    GraphResponse,
)
from app.repositories import nexus_repo, case_repo

router = APIRouter(tags=["nexus"])


# ============================================================
# HELPERS
# ============================================================
def verify_case_exists(db: Session, case_id: int) -> None:
    if not case_repo.get_case(db, case_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "CASE_NOT_FOUND", "message": "Case not found"},
        )


def get_entity_or_404(db: Session, entity_id: int):
    entity = nexus_repo.get_entity(db, entity_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "ENTITY_NOT_FOUND", "message": "Entity not found"},
        )
    return entity


def get_relationship_or_404(db: Session, relationship_id: int):
    rel = nexus_repo.get_relationship(db, relationship_id)
    if not rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "RELATIONSHIP_NOT_FOUND",
                "message": "Relationship not found",
            },
        )
    return rel


def verify_entity_belongs_to_case(db: Session, entity_id: int, case_id: int) -> None:
    entity = get_entity_or_404(db, entity_id)
    if entity.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ENTITY_NOT_IN_CASE",
                "message": "Entity does not belong to the specified case",
            },
        )


# ============================================================
# ENTITIES
# ============================================================
@router.post(
    "/api/cases/{case_id}/entities",
    response_model=EntityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_entity(case_id: int, entity_in: EntityCreate, db: Session = Depends(get_db)):
    verify_case_exists(db, case_id)
    return nexus_repo.create_entity(db, case_id=case_id, entity_in=entity_in)


@router.get("/api/cases/{case_id}/entities", response_model=List[EntityResponse])
def read_case_entities(case_id: int, db: Session = Depends(get_db)):
    verify_case_exists(db, case_id)
    return nexus_repo.get_entities_by_case(db, case_id)


@router.get("/api/entities/{entity_id}", response_model=EntityResponse)
def read_entity(entity_id: int, db: Session = Depends(get_db)):
    return get_entity_or_404(db, entity_id)


@router.put("/api/entities/{entity_id}", response_model=EntityResponse)
def update_entity(
    entity_id: int, entity_in: EntityUpdate, db: Session = Depends(get_db)
):
    entity = get_entity_or_404(db, entity_id)
    return nexus_repo.update_entity(db, db_entity=entity, entity_in=entity_in)


@router.delete("/api/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entity(entity_id: int, db: Session = Depends(get_db)):
    entity = get_entity_or_404(db, entity_id)
    nexus_repo.delete_entity(db, db_entity=entity)
    return None


# ============================================================
# RELATIONSHIPS
# ============================================================
@router.post(
    "/api/cases/{case_id}/relationships",
    response_model=RelationshipResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_relationship(
    case_id: int, rel_in: RelationshipCreate, db: Session = Depends(get_db)
):
    verify_case_exists(db, case_id)

    if rel_in.source_entity_id == rel_in.target_entity_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "SELF_RELATIONSHIP_NOT_ALLOWED",
                "message": "Source and target entities must be different",
            },
        )

    verify_entity_belongs_to_case(db, rel_in.source_entity_id, case_id)
    verify_entity_belongs_to_case(db, rel_in.target_entity_id, case_id)

    return nexus_repo.create_relationship(db, case_id=case_id, rel_in=rel_in)


@router.get(
    "/api/cases/{case_id}/relationships",
    response_model=List[RelationshipResponse],
)
def read_case_relationships(case_id: int, db: Session = Depends(get_db)):
    verify_case_exists(db, case_id)
    return nexus_repo.get_relationships_by_case(db, case_id)


@router.get("/api/relationships/{relationship_id}", response_model=RelationshipResponse)
def read_relationship(relationship_id: int, db: Session = Depends(get_db)):
    return get_relationship_or_404(db, relationship_id)


@router.put("/api/relationships/{relationship_id}", response_model=RelationshipResponse)
def update_relationship(
    relationship_id: int,
    rel_in: RelationshipUpdate,
    db: Session = Depends(get_db),
):
    rel = get_relationship_or_404(db, relationship_id)
    return nexus_repo.update_relationship(db, db_rel=rel, rel_in=rel_in)


@router.delete(
    "/api/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_relationship(relationship_id: int, db: Session = Depends(get_db)):
    rel = get_relationship_or_404(db, relationship_id)
    nexus_repo.delete_relationship(db, db_rel=rel)
    return None


# ============================================================
# GRAPH (Cytoscape.js)
# ============================================================
@router.get("/api/cases/{case_id}/graph", response_model=GraphResponse)
def read_case_graph(case_id: int, db: Session = Depends(get_db)):
    verify_case_exists(db, case_id)

    entities = nexus_repo.get_entities_by_case(db, case_id)
    relationships = nexus_repo.get_relationships_by_case(db, case_id)

    nodes = [
        {
            "data": {
                "id": f"e{e.id}",
                "entity_id": e.id,
                "label": e.name,
                "type": e.type.value if hasattr(e.type, "value") else str(e.type),
                "identifier": e.identifier,
                "description": e.description,
            }
        }
        for e in entities
    ]

    edges = [
        {
            "data": {
                "id": f"r{r.id}",
                "relationship_id": r.id,
                "source": f"e{r.source_entity_id}",
                "target": f"e{r.target_entity_id}",
                "label": (
                    r.relationship_type.value
                    if hasattr(r.relationship_type, "value")
                    else str(r.relationship_type)
                ),
                "type": (
                    r.relationship_type.value
                    if hasattr(r.relationship_type, "value")
                    else str(r.relationship_type)
                ),
                "description": r.description,
                "confidence": r.confidence,
            }
        }
        for r in relationships
    ]

    return {"nodes": nodes, "edges": edges}

