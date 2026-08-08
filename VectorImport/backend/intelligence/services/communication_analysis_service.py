"""
intelligence/services/communication_analysis_service.py
--------------------------------------------------------
CommunicationAnalysisService — Analyzes document volume, escalation tags, and channels.
"""

from __future__ import annotations

from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle
from schemas.domain.normalized_document import DocumentSource
from intelligence.schemas import CommunicationAnalysis
from utils.logger import get_logger

_log = get_logger("intelligence.services.communication_analysis")


class CommunicationAnalysisService:
    """
    Evaluates message density, active authors, escalation frequency, and channel breakdown.
    """

    def analyze(self, bundle: ProjectKnowledgeBundle) -> CommunicationAnalysis:
        _log.debug("Analyzing communications for project_id=%s", bundle.project_id)

        docs = bundle.documents
        total_docs = len(docs)

        authors = {d.author for d in docs if d.author and d.author != "Unknown"}
        active_authors_count = len(authors)

        escalation_count = 0
        channel_counts: dict[str, int] = {}

        for d in docs:
            channel = d.source.value
            channel_counts[channel] = channel_counts.get(channel, 0) + 1

            title_lower = (d.title + " " + d.text).lower()
            if "escalation" in title_lower or "escalat" in title_lower or "formal escalation" in title_lower:
                escalation_count += 1

        dist_parts = [f"{k}:{v}" for k, v in sorted(channel_counts.items())]
        dist_summary = ", ".join(dist_parts)

        analysis = CommunicationAnalysis(
            total_documents=total_docs,
            escalation_count=escalation_count,
            active_authors_count=active_authors_count,
            channel_distribution_summary=dist_summary,
        )
        _log.info(
            "CommunicationAnalysis complete for project_id=%s — %d docs, %d escalations, %d authors",
            bundle.project_id, total_docs, escalation_count, active_authors_count,
        )
        return analysis
