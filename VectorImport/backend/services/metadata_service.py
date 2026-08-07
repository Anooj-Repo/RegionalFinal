"""
services/metadata_service.py
-----------------------------
MetadataService — Node 4 service for Graph 1.

Enriches NormalizedDocument instances with calculated metadata attributes:
    - sentiment (positive, neutral, negative, urgent)
    - keywords
    - teams
    - sprint / period
    - owner / author
    - priority
    - source system
    - document type
"""

from __future__ import annotations

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from schemas.domain.normalized_document import NormalizedDocument
from utils.logger import get_logger

_log = get_logger("services.metadata")

_URGENT_KEYWORDS = {"urgent", "formal escalation", "critical", "blocked", "failure", "at risk"}
_vader = SentimentIntensityAnalyzer()

_KEYWORD_RULES = {
    "escalation": ["escalat", "urgent", "delay", "missed", "blocked", "issue"],
    "vendor": ["vendor", "cloudsphere", "securecheck", "contract", "supplier"],
    "data_quality": ["gl_accounts", "null", "etl", "migration", "audit", "corrupt"],
    "compliance": ["gdpr", "pen test", "penetration", "fine", "regulatory", "audit"],
    "architecture": ["azure", "sap", "s/4hana", "zero-trust", "iam", "siem", "api"],
}


class MetadataService:
    """
    Metadata enrichment service for NormalizedDocument items.
    """

    def enrich_documents(
        self,
        documents: list[NormalizedDocument],
    ) -> list[NormalizedDocument]:
        """
        Enrich a list of NormalizedDocument instances with metadata tags.
        Returns a new list of enriched NormalizedDocument instances.
        """
        _log.info("Enriching metadata for %d documents", len(documents))
        enriched: list[NormalizedDocument] = []

        for doc in documents:
            text_lower = (doc.title + " " + doc.text).lower()

            # 1. Sentiment analysis — VADER NLP, with urgent keyword override
            raw_text = doc.title + " " + doc.text
            if any(kw in text_lower for kw in _URGENT_KEYWORDS):
                sentiment = "urgent"
            else:
                scores = _vader.polarity_scores(raw_text)
                compound = scores["compound"]
                if compound >= 0.05:
                    sentiment = "positive"
                elif compound <= -0.05:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"

            # 2. Keyword extraction
            found_keywords: set[str] = set()
            for category, patterns in _KEYWORD_RULES.items():
                if any(p in text_lower for p in patterns):
                    found_keywords.add(category)

            # 3. Build enriched metadata dict
            updated_meta = dict(doc.metadata)
            updated_meta.update(
                {
                    "sentiment": sentiment,
                    "keywords": sorted(list(found_keywords)),
                    "source_system": doc.source.value,
                    "document_type": doc.source.value.upper(),
                    "author": doc.author or "Unknown",
                    "priority": updated_meta.get("priority", "medium" if sentiment in ("negative", "urgent") else "low"),
                }
            )

            enriched_doc = NormalizedDocument(
                id=doc.id,
                source=doc.source,
                title=doc.title,
                text=doc.text,
                author=doc.author,
                created_at=doc.created_at,
                metadata=updated_meta,
            )
            enriched.append(enriched_doc)

        return enriched
