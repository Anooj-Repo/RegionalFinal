"""
rag/rag_retrieval_service.py
----------------------------
RAGRetrievalService — Performs similarity search against FAISS vector indices on disk.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import numpy as np
import faiss

from config import Config
from schemas.domain.normalized_document import DocumentSource
from schemas.domain.risk_report import EvidenceItem, EvidenceReference
from utils.logger import get_logger

_log = get_logger("rag.retrieval_service")

EMBEDDING_DIM = 384


class RAGRetrievalService:
    """
    RAG similarity search service against project FAISS indices.
    """

    def __init__(self, storage_dir: Path | str | None = None) -> None:
        if storage_dir is None:
            self._storage_dir = Path(Config.VECTOR_DB_PATH)
        else:
            self._storage_dir = Path(storage_dir)

    def _compute_embedding(self, text: str) -> np.ndarray:
        """Generate normalized 384-dim dense float32 vector matching EmbeddingService."""
        vec = np.zeros(EMBEDDING_DIM, dtype=np.float32)
        words = text.lower().split()
        for idx, word in enumerate(words):
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            bucket = h % EMBEDDING_DIM
            val = ((h >> 8) % 200 - 100) / 100.0
            vec[bucket] += val
            if idx > 0:
                bigram = f"{words[idx-1]}_{word}"
                h_bi = int(hashlib.md5(bigram.encode("utf-8")).hexdigest(), 16)
                bucket_bi = h_bi % EMBEDDING_DIM
                vec[bucket_bi] += ((h_bi >> 8) % 200 - 100) / 100.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def search_references(
        self,
        project_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[EvidenceReference]:
        """
        Query FAISS vector store for project_id and return top_k EvidenceReference objects.
        """
        pid_map = {"1": "PROG-ALPHA-2026", "2": "PROG-BETA-2026", "3": "PROG-GAMMA-2026"}
        resolved_pid = pid_map.get(str(project_id), str(project_id))

        safe_proj_id = resolved_pid.replace("-", "_").lower()
        faiss_file = self._storage_dir / f"project_{safe_proj_id}_index.faiss"
        meta_file = self._storage_dir / f"project_{safe_proj_id}_metadata.json"

        if not faiss_file.exists() or not meta_file.exists():
            _log.warning("FAISS index or metadata file not found at %s — returning empty evidence", faiss_file)
            return []

        try:
            index = faiss.read_index(str(faiss_file))
            with meta_file.open(encoding="utf-8") as fh:
                chunk_meta = json.load(fh)

            if index.ntotal == 0:
                return []

            q_vec = np.array([self._compute_embedding(query)], dtype=np.float32)
            k = min(top_k, index.ntotal)
            distances, indices = index.search(q_vec, k)

            results: list[EvidenceReference] = []
            for rank, idx_pos in enumerate(indices[0]):
                if 0 <= idx_pos < len(chunk_meta):
                    meta = chunk_meta[idx_pos]
                    dist = float(distances[0][rank])
                    relevance = max(0.0, min(1.0, 1.0 / (1.0 + dist)))

                    source_str = str(meta.get("source_type", meta.get("source", "status_report"))).lower()
                    try:
                        src_enum = DocumentSource(source_str)
                    except ValueError:
                        src_enum = DocumentSource.STATUS_REPORT

                    results.append(
                        EvidenceReference(
                            document_id=str(meta.get("doc_id", "unknown")),
                            chunk_id=str(meta.get("chunk_id", idx_pos)),
                            source=src_enum,
                            similarity_score=round(relevance, 2),
                        )
                    )

            _log.info("RAG search_references returned %d evidence references for project_id=%s", len(results), project_id)
            return results

        except Exception as exc:
            _log.error("RAG search_references failed for project_id=%s — error: %s", project_id, exc)
            return []

    def search(
        self,
        project_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[EvidenceItem]:
        """
        Legacy query method returning EvidenceItem objects for backwards compatibility.
        """
        refs = self.search_references(project_id, query, top_k)
        return [
            EvidenceItem(
                evidence_id=ref.evidence_id,
                source_doc_id=ref.document_id,
                title=f"Source {ref.source.value} (chunk {ref.chunk_id})",
                content_snippet=f"Reference to {ref.source.value} document {ref.document_id}",
                relevance_score=ref.similarity_score,
            )
            for ref in refs
        ]
