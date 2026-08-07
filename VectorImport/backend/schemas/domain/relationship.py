"""
schemas/domain/relationship.py
-------------------------------
Relationship schema and RelationshipType enum.

Extracted causal or directional relationships between domain entities/documents.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class RelationshipType(str, Enum):
    BLOCKS      = "BLOCKS"
    DEPENDS_ON  = "DEPENDS_ON"
    OWNS        = "OWNS"
    DELIVERS    = "DELIVERS"
    IMPACTS     = "IMPACTS"
    ASSIGNED_TO = "ASSIGNED_TO"
    APPLIES_TO  = "APPLIES_TO"


class Relationship(BaseModel):
    """
    Directional relationship link between two entity IDs or document IDs.
    """

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    source_entity: str = Field(..., description="Source entity ID or document ID.")
    target_entity: str = Field(..., description="Target entity ID or document ID.")
    relationship_type: RelationshipType = Field(..., description="Semantic type of connection.")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0).")
