"""
services/chunking_service.py
-----------------------------
ChunkingService — Node 5 service for Graph 1.

Splits long text documents (meeting notes, status reports, long emails,
historical projects) into semantic text chunks while preserving tasks, risks,
and chat messages as unchunked atomic units.
"""

from __future__ import annotations

from schemas.domain.normalized_document import NormalizedDocument, DocumentSource
from utils.logger import get_logger

_log = get_logger("services.chunking")

# Document sources that should be chunked if text exceeds threshold
_CHUNKING_SOURCES = {
    DocumentSource.MEETING_NOTE,
    DocumentSource.STATUS_REPORT,
    DocumentSource.HISTORICAL_PROJECT,
}

# Maximum character size per chunk
DEFAULT_CHUNK_SIZE = 400
DEFAULT_CHUNK_OVERLAP = 50


class ChunkingService:
    """
    Semantic text chunker for normalized documents.
    """

    def chunk_documents(
        self,
        documents: list[NormalizedDocument],
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> list[dict]:
        """
        Produce a list of text chunk dictionaries.

        Chunk dict shape:
        {
            "chunk_id": "email_1001_chk_0",
            "doc_id": "email_1001",
            "source": "email",
            "title": "Email Title",
            "text": "Chunk text content...",
            "metadata": {...}
        }
        """
        _log.info("Chunking documents (size=%d, overlap=%d)", chunk_size, chunk_overlap)
        chunks: list[dict] = []

        for doc in documents:
            text = doc.text.strip()

            # Determine whether this document type should be chunked
            should_chunk = (
                doc.source in _CHUNKING_SOURCES
                or (doc.source == DocumentSource.EMAIL and len(text) > chunk_size)
            )

            if not should_chunk or len(text) <= chunk_size:
                # Keep atomic (1 chunk per doc)
                chunks.append(
                    {
                        "chunk_id": f"{doc.id}_chk_0",
                        "doc_id": doc.id,
                        "source": doc.source.value,
                        "title": doc.title,
                        "text": text,
                        "metadata": doc.metadata,
                    }
                )
            else:
                # Split into overlapping chunks by line/sentence boundaries
                lines = text.split("\n")
                current_chunk = ""
                chunk_index = 0

                for line in lines:
                    if len(current_chunk) + len(line) + 1 <= chunk_size:
                        current_chunk += (line + "\n")
                    else:
                        if current_chunk.strip():
                            chunks.append(
                                {
                                    "chunk_id": f"{doc.id}_chk_{chunk_index}",
                                    "doc_id": doc.id,
                                    "source": doc.source.value,
                                    "title": f"{doc.title} (Part {chunk_index + 1})",
                                    "text": current_chunk.strip(),
                                    "metadata": doc.metadata,
                                }
                            )
                            chunk_index += 1
                        # Start next chunk with overlap from end of current_chunk
                        overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                        current_chunk = overlap_text + line + "\n"

                if current_chunk.strip():
                    chunks.append(
                        {
                            "chunk_id": f"{doc.id}_chk_{chunk_index}",
                            "doc_id": doc.id,
                            "source": doc.source.value,
                            "title": f"{doc.title} (Part {chunk_index + 1})" if chunk_index > 0 else doc.title,
                            "text": current_chunk.strip(),
                            "metadata": doc.metadata,
                        }
                    )

        _log.info("Produced %d total text chunks from %d documents", len(chunks), len(documents))
        return chunks
