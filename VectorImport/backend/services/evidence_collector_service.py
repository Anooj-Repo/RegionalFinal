"""
services/evidence_collector_service.py
---------------------------------------
EvidenceCollectorService — Node 2 service for Graph 2.

Retrieves relevant historical knowledge and evidence references from the FAISS vector index,
assembling a structured EvidencePackage.
"""

from __future__ import annotations

from intelligence.schemas import ProjectIntelligence
from rag.rag_retrieval_service import RAGRetrievalService
from schemas.domain.risk_report import EvidenceItem, EvidencePackage, EvidenceReference
from utils.logger import get_logger

_log = get_logger("services.evidence_collector")


class EvidenceCollectorService:
    """
    Evidence collector delegating similarity queries to RAGRetrievalService and building EvidencePackage.
    """

    def __init__(self, rag_service: RAGRetrievalService | None = None) -> None:
        self.rag_service = rag_service or RAGRetrievalService()

    def collect_evidence_package(
        self,
        intelligence: ProjectIntelligence,
        top_k: int = 5,
    ) -> EvidencePackage:
        _log.info("Collecting EvidencePackage for project_id=%s", intelligence.project_id)

        query_terms = [s.title for s in intelligence.signals]
        query_terms.extend(intelligence.health.primary_drivers)
        query = " ".join(query_terms) if query_terms else "project risk delay blocker vendor compliance"

        retrieved_refs = self.rag_service.search_references(
            project_id=intelligence.project_id,
            query=query,
            top_k=top_k,
        )

        entity_ids: list[str] = []
        for s in intelligence.signals:
            entity_ids.extend(s.source_entity_ids)

        if intelligence.dependency_analysis.bottleneck_entity_ids:
            entity_ids.extend(intelligence.dependency_analysis.bottleneck_entity_ids)

        package = EvidencePackage(
            retrieved_documents=retrieved_refs,
            supporting_documents=retrieved_refs,
            entity_references=sorted(list(set(entity_ids))),
            relationship_references=[f"rel_blocker_{i}" for i in range(len(intelligence.signals))],
        )

        _log.info("Assembled EvidencePackage with %d references for project_id=%s", len(retrieved_refs), intelligence.project_id)
        return package

    def collect_evidence(
        self,
        intelligence: ProjectIntelligence,
        top_k: int = 5,
    ) -> list[EvidenceItem]:
        """Backwards compatible legacy helper."""
        pkg = self.collect_evidence_package(intelligence, top_k)
        return [
            EvidenceItem(
                evidence_id=ref.evidence_id,
                source_doc_id=ref.document_id,
                title=f"Source {ref.source.value} (chunk {ref.chunk_id})",
                content_snippet=f"Reference to {ref.source.value} document {ref.document_id}",
                relevance_score=ref.similarity_score,
            )
            for ref in pkg.retrieved_documents
        ]
