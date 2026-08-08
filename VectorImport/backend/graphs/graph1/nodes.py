"""
graphs/graph1/nodes.py
----------------------
Nodes for Graph 1: Knowledge Intelligence Pipeline.

Thin orchestration wrappers delegating logic to modular services.
"""

from __future__ import annotations

from typing import Any
from graphs.graph1.state import Graph1State
from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle
from services import (
    DocumentNormalizationService,
    EntityExtractionService,
    RelationshipService,
    MetadataService,
    ChunkingService,
    EmbeddingService,
)
from utils.logger import get_logger

_log = get_logger("graphs.graph1.nodes")

# Default service instances
_norm_service = DocumentNormalizationService()
_entity_service = EntityExtractionService()
_rel_service = RelationshipService()
_meta_service = MetadataService()
_chunk_service = ChunkingService()
_embed_service = EmbeddingService()


def normalize_node(state: Graph1State) -> dict[str, Any]:
    """Node 1: Normalize heterogeneous snapshot items into NormalizedDocuments."""
    _log.info("[Node 1] Running NormalizeNode")
    snapshot = state["snapshot"]
    docs = _norm_service.normalize(snapshot)
    return {"normalized_documents": docs}


def entity_extraction_node(state: Graph1State) -> dict[str, Any]:
    """Node 2: Extract typed KnowledgeEntity instances."""
    _log.info("[Node 2] Running EntityExtractionNode")
    snapshot = state["snapshot"]
    docs = state.get("normalized_documents", [])
    entities = _entity_service.extract_entities(snapshot, docs)
    return {"entities": entities}


def relationship_extraction_node(state: Graph1State) -> dict[str, Any]:
    """Node 3: Discover Relationships between entities and documents."""
    _log.info("[Node 3] Running RelationshipExtractionNode")
    snapshot = state["snapshot"]
    docs = state.get("normalized_documents", [])
    entities = state.get("entities", [])
    relationships = _rel_service.extract_relationships(snapshot, docs, entities)
    return {"relationships": relationships}


def metadata_enrichment_node(state: Graph1State) -> dict[str, Any]:
    """Node 4: Enrich NormalizedDocuments with metadata tags."""
    _log.info("[Node 4] Running MetadataEnrichmentNode")
    docs = state.get("normalized_documents", [])
    enriched_docs = _meta_service.enrich_documents(docs)
    return {"normalized_documents": enriched_docs}


def chunking_node(state: Graph1State) -> dict[str, Any]:
    """Node 5: Chunk long text documents."""
    _log.info("[Node 5] Running ChunkingNode")
    docs = state.get("normalized_documents", [])
    chunks = _chunk_service.chunk_documents(docs)
    return {"chunks": chunks}


def embedding_node(state: Graph1State) -> dict[str, Any]:
    """Node 6: Generate embeddings and build FAISS vector index."""
    _log.info("[Node 6] Running EmbeddingNode")
    snapshot = state["snapshot"]
    chunks = state.get("chunks", [])
    project_id = snapshot.project.project_id
    ref = _embed_service.index_chunks(project_id, chunks)
    return {"retrieval_reference": ref}


def knowledge_bundle_node(state: Graph1State) -> dict[str, Any]:
    """Node 7: Package all outputs into a ProjectKnowledgeBundle."""
    _log.info("[Node 7] Running KnowledgeBundleNode")
    snapshot = state["snapshot"]
    docs = state.get("normalized_documents", [])
    entities = state.get("entities", [])
    relationships = state.get("relationships", [])
    ref = state.get("retrieval_reference", "")

    bundle = ProjectKnowledgeBundle(
        project_id=snapshot.project.project_id,
        documents=docs,
        entities=entities,
        relationships=relationships,
        retrieval_reference=ref,
    )
    _log.info(
        "Built ProjectKnowledgeBundle for project '%s' — %s",
        snapshot.project.name, bundle.summary(),
    )
    return {"knowledge_bundle": bundle}
