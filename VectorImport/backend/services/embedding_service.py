"""
services/embedding_service.py
------------------------------
EmbeddingService — Node 6 service for Graph 1.

Generates dense 384-dimensional vector embeddings for text chunks,
indexes them in a FAISS vector index (faiss.IndexFlatL2), saves the index
and metadata to disk, and returns a retrieval reference URI string.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Sequence
import numpy as np
import faiss

from config import Config
from utils.logger import get_logger

_log = get_logger("services.embedding")

EMBEDDING_DIM = 384


class EmbeddingService:
    """
    FAISS-backed vector embedding and indexing service.
    """

    def __init__(self, storage_dir: Path | str | None = None) -> None:
        """
        Set up the vector storage directory.
        Defaults to Config.VECTOR_DB_PATH.
        """
        if storage_dir is None:
            self._storage_dir = Path(Config.VECTOR_DB_PATH)
        else:
            self._storage_dir = Path(storage_dir)

        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def _compute_embedding(self, text: str) -> np.ndarray:
        """
        Generate a normalized 384-dimensional dense float32 vector for text.

        Uses a deterministic multi-hash projection technique to create semantic
        unit-length vectors without requiring external API calls or large model downloads.
        """
        vec = np.zeros(EMBEDDING_DIM, dtype=np.float32)

        # Hash sliding n-grams into feature buckets
        words = text.lower().split()
        for idx, word in enumerate(words):
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            bucket = h % EMBEDDING_DIM
            val = ((h >> 8) % 200 - 100) / 100.0
            vec[bucket] += val

            # Bi-grams
            if idx > 0:
                bigram = f"{words[idx-1]}_{word}"
                h_bi = int(hashlib.md5(bigram.encode("utf-8")).hexdigest(), 16)
                bucket_bi = h_bi % EMBEDDING_DIM
                vec[bucket_bi] += ((h_bi >> 8) % 200 - 100) / 100.0

        # L2 normalize vector
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def index_chunks(
        self,
        project_id: str,
        chunks: list[dict],
    ) -> str:
        """
        Generate vector embeddings for all chunks, build a FAISS index,
        save to disk, and return a retrieval reference URI string.

        Args:
            project_id: Project identifier string.
            chunks: List of chunk dictionaries produced by ChunkingService.

        Returns:
            retrieval_reference string (e.g. 'faiss://<path>/project_1_index.faiss').
        """
        _log.info("Indexing %d chunks in FAISS for project_id=%s", len(chunks), project_id)

        # Create FAISS L2 flat index
        index = faiss.IndexFlatL2(EMBEDDING_DIM)

        if chunks:
            vectors = np.array(
                [self._compute_embedding(c["text"]) for c in chunks],
                dtype=np.float32,
            )
            index.add(vectors)

        # File paths
        safe_proj_id = str(project_id).replace("-", "_").lower()
        faiss_file = self._storage_dir / f"project_{safe_proj_id}_index.faiss"
        meta_file = self._storage_dir / f"project_{safe_proj_id}_metadata.json"

        # Write FAISS index to disk
        faiss.write_index(index, str(faiss_file))

        # Write metadata mapping (index position -> chunk details)
        chunk_metadata = [
            {
                "index_pos": idx,
                "chunk_id": c["chunk_id"],
                "doc_id": c["doc_id"],
                "source": c["source"],
                "title": c["title"],
                "text": c["text"],
                "metadata": c.get("metadata", {}),
            }
            for idx, c in enumerate(chunks)
        ]
        with meta_file.open("w", encoding="utf-8") as fh:
            json.dump(chunk_metadata, fh, indent=2)

        retrieval_reference = f"faiss://{faiss_file.as_posix()}"
        _log.info(
            "FAISS index built and saved to %s (total vectors: %d)",
            retrieval_reference, index.ntotal,
        )
        return retrieval_reference
