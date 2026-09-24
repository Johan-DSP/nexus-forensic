from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.db.models.nexus import EntityType, RelationshipType


# ============================================================
# ENTITY
# ============================================================
class EntityBase(BaseModel):
    type: EntityType
    name: str = Field(..., max_length=200)
    identifier: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class EntityCreate(EntityBase):
    # El cliente envía la clave "metadata" en JSON.
    metadata_: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        validation_alias="metadata",
    )
    model_config = ConfigDict(populate_by_name=True)


class EntityUpdate(BaseModel):
    type: Optional[EntityType] = None
    name: Optional[str] = Field(None, max_length=200)
    identifier: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = Field(
        None,
        validation_alias="metadata",
    )
    model_config = ConfigDict(populate_by_name=True)


class EntityResponse(EntityBase):
    id: int
    case_id: int
    # Lee del ORM (metadata_), exporta al cliente como "metadata".
    metadata_: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        validation_alias="metadata_",
        serialization_alias="metadata",
    )
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ============================================================
# RELATIONSHIP
# ============================================================
class RelationshipBase(BaseModel):
    source_entity_id: int
    target_entity_id: int
    relationship_type: RelationshipType
    description: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class RelationshipCreate(RelationshipBase):
    pass


class RelationshipUpdate(BaseModel):
    relationship_type: Optional[RelationshipType] = None
    description: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class RelationshipResponse(RelationshipBase):
    id: int
    case_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# GRAPH (Cytoscape.js)
# ============================================================
class GraphNode(BaseModel):
    data: Dict[str, Any]


class GraphEdge(BaseModel):
    data: Dict[str, Any]


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
