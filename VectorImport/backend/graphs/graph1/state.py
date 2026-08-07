"""
graphs/graph1/state.py
----------------------
State definition for Graph 1: Knowledge Intelligence Pipeline.
"""

from __future__ import annotations

from typing import TypedDict, Optional
from schemas.domain.snapshot import ProjectSnapshot
from schemas.domain.normalized_document import NormalizedDocument
from schemas.domain.knowledge_entity import KnowledgeEntity
from schemas.domain.relationship import Relationship
from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle


class Graph1State(TypedDict, total=False):
    """
    State container passed through Graph 1 nodes.
    """

    snapshot: ProjectSnapshot
    normalized_documents: list[NormalizedDocument]
    entities: list[KnowledgeEntity]
    relationships: list[Relationship]
    chunks: list[dict]
    retrieval_reference: str
    knowledge_bundle: Optional[ProjectKnowledgeBundle]
