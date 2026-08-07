"""
schemas/domain/project_knowledge_bundle.py
-------------------------------------------
ProjectKnowledgeBundle schema.

The single output contract of Graph 1, handed off to Graph 2.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field

from schemas.domain.normalized_document import NormalizedDocument
from schemas.domain.knowledge_entity import KnowledgeEntity
from schemas.domain.relationship import Relationship


class ProjectKnowledgeBundle(BaseModel):
    """
    Structured knowledge intelligence bundle for a project.

    Aggregates normalized documents, extracted entities, discovered relationships,
    and a FAISS vector DB retrieval reference.
    """

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    project_id: str = Field(..., description="Project UUID or business ID.")
    documents: list[NormalizedDocument] = Field(default_factory=list, description="Normalized documents.")
    entities: list[KnowledgeEntity] = Field(default_factory=list, description="Extracted business entities.")
    relationships: list[Relationship] = Field(default_factory=list, description="Extracted entity relationships.")
    retrieval_reference: str = Field(..., description="FAISS vector store index reference URI or path.")
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when this bundle was constructed.",
    )

    def summary(self) -> dict:
        """Lightweight summary dictionary for telemetry/logging."""
        return {
            "project_id":          self.project_id,
            "documents":           len(self.documents),
            "entities":            len(self.entities),
            "relationships":       len(self.relationships),
            "retrieval_reference": self.retrieval_reference,
            "generated_at":        self.generated_at.isoformat(),
        }
