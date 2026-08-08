"""
services/context_builder_service.py
------------------------------------
ContextBuilderService — Node 1 service for Graph 2.

Synthesizes ProjectIntelligence signals and health metrics into a unified context summary using LLMService.
"""

from __future__ import annotations

from intelligence.schemas import ProjectIntelligence
from prompts.graph2_prompts import CONTEXT_BUILDER_PROMPT
from services.llm_service import LLMService, get_llm_service
from utils.logger import get_logger

_log = get_logger("services.context_builder")


class ContextBuilderService:
    """
    Synthesizes ProjectIntelligence into a structured context summary using LLM.
    """

    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or get_llm_service()

    def build_context(self, intelligence: ProjectIntelligence) -> str:
        _log.info("Building context summary via LLM for project_id=%s", intelligence.project_id)

        prompt = CONTEXT_BUILDER_PROMPT.format(
            project_id=intelligence.project_id,
            health_score=intelligence.health.health_score,
            health_status=intelligence.health.status.value,
            blocked_tasks=intelligence.timeline_analysis.blocked_task_count,
            signal_count=len(intelligence.signals),
        )

        # Call mandatory LLM
        summary = self.llm_service.invoke_text(prompt)
        _log.info("Context summary built via LLM for project_id=%s", intelligence.project_id)
        return summary
