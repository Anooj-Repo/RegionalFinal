"""
intelligence/services/delta_service.py
---------------------------------------
DeltaService — Evaluates state deltas and new escalations across documents.
"""

from __future__ import annotations

from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle
from schemas.domain.normalized_document import DocumentSource
from intelligence.schemas import DeltaSummary
from utils.logger import get_logger

_log = get_logger("intelligence.services.delta")


class DeltaService:
    """
    Detects state changes, newly blocked items, and new escalations from bundle data.
    """

    def analyze(self, bundle: ProjectKnowledgeBundle) -> DeltaSummary:
        _log.debug("Analyzing state deltas for project_id=%s", bundle.project_id)

        blocked_tasks: list[str] = []
        new_escalations: list[str] = []

        for doc in bundle.documents:
            if doc.source == DocumentSource.PROJECT_TASK and doc.metadata.get("status") == "blocked":
                blocked_tasks.append(doc.title)
            elif doc.source == DocumentSource.EMAIL and "escalat" in (doc.title + " " + doc.text).lower():
                new_escalations.append(doc.title)

        has_critical = len(blocked_tasks) > 0 or len(new_escalations) > 0

        delta = DeltaSummary(
            newly_blocked_tasks=blocked_tasks,
            new_escalations=new_escalations,
            progress_delta_pct=-5.0 if has_critical else 0.0,
            has_critical_changes=has_critical,
        )
        _log.info(
            "DeltaService complete for project_id=%s — %d blocked, %d escalations",
            bundle.project_id, len(blocked_tasks), len(new_escalations),
        )
        return delta
