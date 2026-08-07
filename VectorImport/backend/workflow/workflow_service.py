"""
workflow/workflow_service.py
----------------------------
Orchestrates multi-step AI workflows by routing requests
to the appropriate LangGraph graphs or agent pipelines.
"""

from __future__ import annotations

import logging
from typing import Any

from services.data_source_registry import get_registry
from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle
from schemas.domain.risk_report import RiskAssessmentReport
from intelligence.engine import get_intelligence_engine
from graphs.graph1 import graph1
from graphs.graph2 import graph2

logger = logging.getLogger("workflow.service")


class WorkflowService:
    """
    Central orchestrator for AI workflows.

    Usage:
        service = WorkflowService()
        bundle  = service.run_graph1(project_id=1)
        report  = service.run_graph2(project_id=1)
    """

    def __init__(self):
        self._build_registry()

    def _build_registry(self) -> None:
        """Populate the workflow registry."""
        self._registry = {
            "graph1": self._run_graph1_handler,
            "graph2": self._run_graph2_handler,
        }

    def run_graph1(self, project_id: int) -> ProjectKnowledgeBundle:
        """
        Execute Graph 1 pipeline for a given project_id:
            DataSourceRegistry -> ProjectSnapshot -> Graph 1 -> ProjectKnowledgeBundle
        """
        logger.info("Executing Graph 1 workflow for project_id=%s", project_id)
        registry = get_registry()
        snapshot = registry.load_project(project_id)
        initial_state = {"snapshot": snapshot}

        final_state = graph1.invoke(initial_state)
        bundle: ProjectKnowledgeBundle = final_state["knowledge_bundle"]
        logger.info(
            "Graph 1 workflow finished for project_id=%s — %s",
            project_id, bundle.summary(),
        )
        return bundle

    def run_graph2(self, project_id: int) -> RiskAssessmentReport:
        """
        Execute Graph 2 pipeline for a given project_id:
            Graph 1 (Bundle) -> IntelligenceEngine (Intelligence) -> Graph 2 -> RiskAssessmentReport
        """
        logger.info("Executing Graph 2 workflow for project_id=%s", project_id)
        bundle = self.run_graph1(project_id)

        engine = get_intelligence_engine()
        intelligence = engine.analyze(bundle)

        initial_state = {
            "intelligence": intelligence,
            "retry_count": 0,
            "max_retries": 2,
        }

        final_state = graph2.invoke(initial_state)
        report: RiskAssessmentReport = final_state["final_report"]
        logger.info(
            "Graph 2 workflow finished for project_id=%s — %s",
            project_id, report.summary(),
        )
        return report

    def run(self, workflow_name: str, payload: dict) -> Any:
        """
        Dispatch a payload to the named workflow.

        Args:
            workflow_name: Key registered in _registry.
            payload:       Input data containing 'project_id'.

        Returns:
            The workflow's output.

        Raises:
            ValueError: If the workflow name is not registered.
        """
        handler = self._registry.get(workflow_name)
        if not handler:
            raise ValueError(
                f"Unknown workflow '{workflow_name}'. "
                f"Available: {list(self._registry.keys())}"
            )
        logger.info("Running workflow '%s'", workflow_name)
        return handler(payload)

    # ------------------------------------------------------------------
    # Private workflow handlers
    # ------------------------------------------------------------------

    def _run_graph1_handler(self, payload: dict) -> ProjectKnowledgeBundle:
        project_id = payload.get("project_id")
        if not project_id:
            raise ValueError("Payload must contain 'project_id'.")
        return self.run_graph1(int(project_id))

    def _run_graph2_handler(self, payload: dict) -> RiskAssessmentReport:
        project_id = payload.get("project_id")
        if not project_id:
            raise ValueError("Payload must contain 'project_id'.")
        return self.run_graph2(int(project_id))
