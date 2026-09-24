from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.nexus import Entity, Relationship
from app.schemas.nexus import (
    EntityCreate,
    EntityUpdate,
    RelationshipCreate,
    RelationshipUpdate,
)


# ============================================================
# ENTITIES
# ============================================================
def get_entity(db: Session, entity_id: int) -> Optional[Entity]:
    return db.query(Entity).filter(Entity.id == entity_id).first()


def get_entities_by_case(db: Session, case_id: int) -> List[Entity]:
    return (
        db.query(Entity)
        .filter(Entity.case_id == case_id)
        .order_by(Entity.id.asc())
        .all()
    )


def create_entity(db: Session, case_id: int, entity_in: EntityCreate) -> Entity:
    # by_alias=False -> devuelve 'metadata_' que es el nombre del atributo ORM
    data = entity_in.model_dump(by_alias=False)
    db_entity = Entity(**data, case_id=case_id)
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def update_entity(db: Session, db_entity: Entity, entity_in: EntityUpdate) -> Entity:
    update_data = entity_in.model_dump(exclude_unset=True, by_alias=False)
    for field, value in update_data.items():
        setattr(db_entity, field, value)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def delete_entity(db: Session, db_entity: Entity) -> Entity:
    """
    Elimina la entidad y todas las relaciones que la referencian.
    SQLite no aplica ON DELETE CASCADE por defecto, por eso se
    hace explícito en el repositorio.
    """
    db.query(Relationship).filter(
        (Relationship.source_entity_id == db_entity.id)
        | (Relationship.target_entity_id == db_entity.id)
    ).delete(synchronize_session=False)
    db.delete(db_entity)
    db.commit()
    return db_entity


# ============================================================
# RELATIONSHIPS
# ============================================================
def get_relationship(db: Session, relationship_id: int) -> Optional[Relationship]:
    return db.query(Relationship).filter(Relationship.id == relationship_id).first()


def get_relationships_by_case(db: Session, case_id: int) -> List[Relationship]:
    return (
        db.query(Relationship)
        .filter(Relationship.case_id == case_id)
        .order_by(Relationship.id.asc())
        .all()
    )


def create_relationship(
    db: Session, case_id: int, rel_in: RelationshipCreate
) -> Relationship:
    db_rel = Relationship(**rel_in.model_dump(), case_id=case_id)
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    return db_rel


def update_relationship(
    db: Session, db_rel: Relationship, rel_in: RelationshipUpdate
) -> Relationship:
    update_data = rel_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_rel, field, value)
    db.commit()
    db.refresh(db_rel)
    return db_rel


def delete_relationship(db: Session, db_rel: Relationship) -> Relationship:
    db.delete(db_rel)
    db.commit()
    return db_rel
