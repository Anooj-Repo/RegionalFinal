"""
intelligence/services/metrics_service.py
-----------------------------------------
MetricsService — Computes quantitative operational health KPIs.
"""

from __future__ import annotations

from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle
from schemas.domain.normalized_document import DocumentSource
from intelligence.schemas import ProjectMetrics
from utils.logger import get_logger

_log = get_logger("intelligence.services.metrics")


class MetricsService:
    """
    Calculates operational health KPIs from bundle contents.
    """

    def analyze(self, bundle: ProjectKnowledgeBundle) -> ProjectMetrics:
        _log.debug("Calculating metrics for project_id=%s", bundle.project_id)

        task_docs = [d for d in bundle.documents if d.source == DocumentSource.PROJECT_TASK]
        risk_docs = [d for d in bundle.documents if d.source == DocumentSource.RISK_ENTRY]

        total_tasks = len(task_docs)
        if total_tasks > 0:
            completions = [d.metadata.get("completion", 0) for d in task_docs]
            completion_rate = sum(completions) / float(total_tasks)
            blocked_tasks = sum(1 for d in task_docs if d.metadata.get("status") == "blocked")
            blocker_density = blocked_tasks / float(total_tasks)
        else:
            completion_rate = 0.0
            blocker_density = 0.0

        open_risks = sum(1 for d in risk_docs if d.metadata.get("status") == "open")
        critical_risks = sum(
            1 for d in risk_docs
            if d.metadata.get("status") == "open" and d.metadata.get("impact") in ("critical", "high")
        )

        doc_velocity = len(bundle.documents) / 30.0  # documents per day baseline

        metrics = ProjectMetrics(
            task_completion_rate=round(completion_rate, 2),
            blocker_density=round(blocker_density, 2),
            open_risk_count=open_risks,
            critical_risk_count=critical_risks,
            document_velocity=round(doc_velocity, 2),
        )
        _log.info(
            "MetricsService complete for project_id=%s — completion=%.1f%%, density=%.2f, open_risks=%d",
            bundle.project_id, completion_rate, blocker_density, open_risks,
        )
        return metrics
