import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    Float,
    JSON,
)
from sqlalchemy.sql import func
from app.db.base import Base


class EntityType(str, enum.Enum):
    PERSON = "PERSON"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    VEHICLE = "VEHICLE"
    ADDRESS = "ADDRESS"
    ORGANIZATION = "ORGANIZATION"
    ACCOUNT = "ACCOUNT"
    LOCATION = "LOCATION"
    DOCUMENT = "DOCUMENT"
    DEVICE = "DEVICE"
    OTHER = "OTHER"


class RelationshipType(str, enum.Enum):
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    OWNS = "OWNS"
    USES = "USES"
    CONTACTED = "CONTACTED"
    LOCATED_AT = "LOCATED_AT"
    EMPLOYED_BY = "EMPLOYED_BY"
    REGISTERED_TO = "REGISTERED_TO"
    CONNECTED_TO = "CONNECTED_TO"
    RELATED_TO = "RELATED_TO"
    OTHER = "OTHER"


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(
        Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    type = Column(Enum(EntityType), nullable=False)
    name = Column(String(200), nullable=False)
    identifier = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(
        Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False
    )
    source_entity_id = Column(
        Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False
    )
    target_entity_id = Column(
        Integer, ForeignKey("entities.id", ondelete="CASCADE"), nullable=False
    )
    relationship_type = Column(Enum(RelationshipType), nullable=False)
    description = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
