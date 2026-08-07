"""
schemas/domain/knowledge_entity.py
-----------------------------------
KnowledgeEntity schema and EntityType enum.

Extracted enterprise entities across documents and project state.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class EntityType(str, Enum):
    TASK        = "task"
    VENDOR      = "vendor"
    TEAM        = "team"
    MILESTONE   = "milestone"
    DELIVERABLE = "deliverable"
    APPLICATION = "application"
    SERVICE     = "service"
    DEPENDENCY  = "dependency"
    PERSON      = "person"


class KnowledgeEntity(BaseModel):
    """
    Extracted business entity representing a key domain concept.
    """

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    entity_id: str = Field(..., description="Unique entity identifier (e.g. ent_vendor_cloudsphere).")
    entity_type: EntityType = Field(..., description="Category of the entity.")
    name: str = Field(..., description="Human-readable entity name.")
    description: str = Field(default="", description="Detailed description or context.")
    source_document_ids: list[str] = Field(
        default_factory=list,
        description="IDs of NormalizedDocuments referencing this entity.",
    )
