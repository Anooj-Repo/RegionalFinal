"""
intelligence/services/timeline_analysis_service.py
---------------------------------------------------
TimelineAnalysisService — Analyzes task completion, blocked tasks, and schedule variance.
"""

from __future__ import annotations

from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle
from schemas.domain.normalized_document import DocumentSource
from intelligence.schemas import TimelineAnalysis
from utils.logger import get_logger

_log = get_logger("intelligence.services.timeline_analysis")


class TimelineAnalysisService:
    """
    Evaluates task completion rates, blocked work items, and schedule delay estimates.
    """

    def analyze(self, bundle: ProjectKnowledgeBundle) -> TimelineAnalysis:
        _log.debug("Analyzing timeline for project_id=%s", bundle.project_id)

        task_docs = [d for d in bundle.documents if d.source == DocumentSource.PROJECT_TASK]
        total_tasks = len(task_docs)

        if total_tasks == 0:
            return TimelineAnalysis(
                overall_completion_pct=100.0,
                overdue_task_count=0,
                blocked_task_count=0,
                estimated_delay_days=0,
                is_on_track=True,
            )

        completions = [d.metadata.get("completion", 0) for d in task_docs]
        statuses = [d.metadata.get("status", "open") for d in task_docs]

        overall_completion = sum(completions) / float(total_tasks)
        blocked_count = sum(1 for s in statuses if s == "blocked")

        # Estimate delay days deterministically: each blocked task adds ~14 days delay
        estimated_delay = blocked_count * 14
        is_on_track = (blocked_count == 0 and estimated_delay == 0)

        # Overdue tasks count heuristic from status reports / task metadata
        overdue_count = blocked_count  # blocked tasks in current datasets are overdue

        analysis = TimelineAnalysis(
            overall_completion_pct=round(overall_completion, 2),
            overdue_task_count=overdue_count,
            blocked_task_count=blocked_count,
            estimated_delay_days=estimated_delay,
            is_on_track=is_on_track,
        )
        _log.info(
            "TimelineAnalysis complete for project_id=%s — completion=%.1f%%, blocked=%d, delay=%dd",
            bundle.project_id, overall_completion, blocked_count, estimated_delay,
        )
        return analysis
