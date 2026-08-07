"""
tests/test_graph1_services.py
------------------------------
Unit tests for each modular service supporting Graph 1:
    - DocumentNormalizationService
    - EntityExtractionService
    - RelationshipService
    - MetadataService
    - ChunkingService
    - EmbeddingService (FAISS)
"""

import pytest
from services import (
    get_registry,
    DocumentNormalizationService,
    EntityExtractionService,
    RelationshipService,
    MetadataService,
    ChunkingService,
    EmbeddingService,
)
from schemas.domain import (
    NormalizedDocument,
    KnowledgeEntity,
    Relationship,
    DocumentSource,
    EntityType,
    RelationshipType,
)


@pytest.fixture
def snapshot_alpha():
    """Load ProjectSnapshot for Project 1 (Alpha)."""
    return get_registry().load_project(1)


class TestDocumentNormalizationService:

    def test_normalize_returns_list_of_normalized_documents(self, snapshot_alpha):
        service = DocumentNormalizationService()
        docs = service.normalize(snapshot_alpha)
        assert isinstance(docs, list)
        assert len(docs) > 0
        assert all(isinstance(d, NormalizedDocument) for d in docs)

    def test_all_document_sources_represented(self, snapshot_alpha):
        service = DocumentNormalizationService()
        docs = service.normalize(snapshot_alpha)
        sources = {d.source for d in docs}
        assert DocumentSource.EMAIL in sources
        assert DocumentSource.CHAT in sources
        assert DocumentSource.MEETING_NOTE in sources
        assert DocumentSource.STATUS_REPORT in sources
        assert DocumentSource.PROJECT_TASK in sources
        assert DocumentSource.RISK_ENTRY in sources
        assert DocumentSource.HISTORICAL_PROJECT in sources


class TestEntityExtractionService:

    def test_extract_entities_returns_knowledge_entities(self, snapshot_alpha):
        norm_service = DocumentNormalizationService()
        docs = norm_service.normalize(snapshot_alpha)

        service = EntityExtractionService()
        entities = service.extract_entities(snapshot_alpha, docs)
        assert isinstance(entities, list)
        assert len(entities) > 0
        assert all(isinstance(e, KnowledgeEntity) for e in entities)

    def test_extracts_cloudsphere_vendor_entity(self, snapshot_alpha):
        norm_service = DocumentNormalizationService()
        docs = norm_service.normalize(snapshot_alpha)

        entities = EntityExtractionService().extract_entities(snapshot_alpha, docs)
        vendor_names = [e.name for e in entities if e.entity_type == EntityType.VENDOR]
        assert any("cloudsphere" in v.lower() for v in vendor_names)


class TestRelationshipService:

    def test_extract_relationships_returns_relationship_objects(self, snapshot_alpha):
        norm_service = DocumentNormalizationService()
        docs = norm_service.normalize(snapshot_alpha)
        entity_service = EntityExtractionService()
        entities = entity_service.extract_entities(snapshot_alpha, docs)

        rel_service = RelationshipService()
        relationships = rel_service.extract_relationships(snapshot_alpha, docs, entities)
        assert isinstance(relationships, list)
        assert len(relationships) > 0
        assert all(isinstance(r, Relationship) for r in relationships)

    def test_cloudsphere_blocks_task_relationship_found(self, snapshot_alpha):
        norm_service = DocumentNormalizationService()
        docs = norm_service.normalize(snapshot_alpha)
        entities = EntityExtractionService().extract_entities(snapshot_alpha, docs)

        relationships = RelationshipService().extract_relationships(snapshot_alpha, docs, entities)
        block_rels = [r for r in relationships if r.relationship_type == RelationshipType.BLOCKS]
        assert len(block_rels) > 0


class TestMetadataService:

    def test_enrich_documents_adds_metadata_attributes(self, snapshot_alpha):
        docs = DocumentNormalizationService().normalize(snapshot_alpha)
        enriched = MetadataService().enrich_documents(docs)
        assert len(enriched) == len(docs)
        for doc in enriched:
            assert "sentiment" in doc.metadata
            assert "keywords" in doc.metadata
            assert "source_system" in doc.metadata


class TestChunkingService:

    def test_chunk_documents_chunks_long_documents(self, snapshot_alpha):
        docs = DocumentNormalizationService().normalize(snapshot_alpha)
        chunks = ChunkingService().chunk_documents(docs)
        assert isinstance(chunks, list)
        assert len(chunks) >= len(docs)
        for c in chunks:
            assert "chunk_id" in c
            assert "text" in c
            assert "doc_id" in c


class TestEmbeddingService:

    def test_index_chunks_faiss_creates_index(self, snapshot_alpha, tmp_path):
        docs = DocumentNormalizationService().normalize(snapshot_alpha)
        chunks = ChunkingService().chunk_documents(docs)

        embed_service = EmbeddingService(storage_dir=tmp_path)
        ref = embed_service.index_chunks("1", chunks)
        assert ref.startswith("faiss://")

        faiss_path = tmp_path / "project_1_index.faiss"
        meta_path = tmp_path / "project_1_metadata.json"
        assert faiss_path.exists()
        assert meta_path.exists()
