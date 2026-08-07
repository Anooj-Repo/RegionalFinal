"""
services/graph_execution_service.py
------------------------------------
GraphExecutionService — Application service orchestrating DataSourceRegistry,
Graph 1 (Knowledge Intelligence), Project Intelligence Engine, and Graph 2 (Decision Intelligence).
"""

from __future__ import annotations

import time
from typing import Any
from exceptions import ProjectNotFoundError, GraphExecutionError
from services.data_source_registry import get_registry
from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle
from intelligence.engine import get_intelligence_engine
from intelligence.schemas import ProjectIntelligence
from schemas.domain.risk_report import RiskAssessmentReport
from services.llm_service import LLMService
from utils.logger import get_logger

_log = get_logger("services.graph_execution")


class GraphExecutionService:
    """
    Application service that orchestrates intermediate states and LangGraph graph executions.
    """

    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service
        self._bundle_cache: dict[str, ProjectKnowledgeBundle] = {}
        self._intelligence_cache: dict[str, ProjectIntelligence] = {}

    def _resolve_project(self, project_id: str) -> int:
        """Resolve numeric or string project ID to internal integer ID, verifying existence."""
        pid_map = {
            "1": 1, "PROG-ALPHA-2026": 1,
            "2": 2, "PROG-BETA-2026": 2,
            "3": 3, "PROG-GAMMA-2026": 3,
        }
        str_pid = str(project_id).strip()
        if str_pid in pid_map:
            return pid_map[str_pid]
        try:
            val = int(str_pid)
            if val in (1, 2, 3):
                return val
        except ValueError:
            pass

        try:
            from database.repositories import ProjectRepository
            if str_pid.isdigit():
                p = ProjectRepository.get_by_id(int(str_pid))
            else:
                p = ProjectRepository.get_by_project_id(str_pid)
            if p:
                return p.id
        except Exception:
            pass

        raise ProjectNotFoundError(project_id=project_id)

    def execute_graph1(self, project_id: str) -> dict[str, Any]:
        """
        Execute Graph 1 ETL pipeline:
            Registry -> ProjectSnapshot -> Graph1 -> ProjectKnowledgeBundle
        """
        start_time = time.perf_counter()
        _log.info("[Graph1 Execution] Started for project_id=%s", project_id)

        int_pid = self._resolve_project(project_id)
        registry = get_registry()
        snapshot = registry.load_project(int_pid)

        try:
            from graphs.graph1 import graph1
            initial_state = {"snapshot": snapshot}
            final_state = graph1.invoke(initial_state)
            bundle: ProjectKnowledgeBundle = final_state["knowledge_bundle"]
            self._bundle_cache[bundle.project_id] = bundle
            self._bundle_cache[str(int_pid)] = bundle

            elapsed_ms = round((time.perf_counter() - start_time) * 1000)
            _log.info("[Graph1 Execution] Finished for project_id=%s in %dms", project_id, elapsed_ms)

            return {
                "status": "success",
                "project_id": bundle.project_id,
                "documents": len(bundle.documents),
                "entities": len(bundle.entities),
                "relationships": len(bundle.relationships),
                "execution_time_ms": elapsed_ms,
            }
        except Exception as exc:
            _log.error("[Graph1 Execution] Failed for project_id=%s — error: %s", project_id, exc)
            if isinstance(exc, ProjectNotFoundError):
                raise
            raise GraphExecutionError(message=f"Graph 1 execution failed for project '{project_id}': {exc}", graph_name="Graph1")

    def execute_intelligence(self, project_id: str) -> dict[str, Any]:
        """
        Execute Project Intelligence Engine:
            ProjectKnowledgeBundle -> IntelligenceEngine -> ProjectIntelligence
        """
        start_time = time.perf_counter()
        _log.info("[Intelligence Engine Execution] Started for project_id=%s", project_id)

        int_pid = self._resolve_project(project_id)
        str_pid = str(int_pid)

        bundle = self._bundle_cache.get(str_pid) or self._bundle_cache.get("PROG-ALPHA-2026" if int_pid == 1 else ("PROG-BETA-2026" if int_pid == 2 else "PROG-GAMMA-2026"))
        if not bundle:
            _log.info("KnowledgeBundle missing in cache for project_id=%s — running Graph 1 automatically", project_id)
            self.execute_graph1(project_id)
            bundle = self._bundle_cache[str_pid]

        try:
            engine = get_intelligence_engine()
            intel: ProjectIntelligence = engine.analyze(bundle)
            self._intelligence_cache[intel.project_id] = intel
            self._intelligence_cache[str_pid] = intel

            elapsed_ms = round((time.perf_counter() - start_time) * 1000)
            _log.info("[Intelligence Engine Execution] Finished for project_id=%s in %dms", project_id, elapsed_ms)

            return {
                "status": "success",
                "project_id": intel.project_id,
                "overall_health": intel.health.status.value,
                "health_score": intel.health.health_score,
                "metrics": intel.metrics.model_dump(),
                "blocked_tasks": intel.timeline_analysis.blocked_task_count,
                "overdue_tasks": intel.timeline_analysis.overdue_task_count,
                "timeline_variance": intel.timeline_analysis.estimated_delay_days,
                "communication_score": intel.sentiment_analysis.net_sentiment_score,
                "deterministic_signals": [s.model_dump() for s in intel.signals],
                "execution_time_ms": elapsed_ms,
            }
        except Exception as exc:
            _log.error("[Intelligence Engine Execution] Failed for project_id=%s — error: %s", project_id, exc)
            if isinstance(exc, ProjectNotFoundError):
                raise
            raise GraphExecutionError(message=f"Intelligence Engine execution failed for project '{project_id}': {exc}", graph_name="IntelligenceEngine")

    def execute_graph2(self, project_id: str) -> dict[str, Any]:
        """
        Execute Graph 2 Decision Intelligence pipeline:
            ProjectIntelligence -> Graph2 -> RiskAssessmentReport
        """
        start_time = time.perf_counter()
        _log.info("[Graph2 Execution] Started for project_id=%s", project_id)

        int_pid = self._resolve_project(project_id)
        str_pid = str(int_pid)

        intel = self._intelligence_cache.get(str_pid) or self._intelligence_cache.get("PROG-ALPHA-2026" if int_pid == 1 else ("PROG-BETA-2026" if int_pid == 2 else "PROG-GAMMA-2026"))
        if not intel:
            _log.info("ProjectIntelligence missing in cache for project_id=%s — running Intelligence Engine automatically", project_id)
            self.execute_intelligence(project_id)
            intel = self._intelligence_cache[str_pid]

        try:
            from graphs.graph2 import graph2
            initial_state: dict[str, Any] = {
                "intelligence": intel,
                "retry_count": 0,
                "max_retries": 2,
            }
            if self.llm_service:
                initial_state["llm_service"] = self.llm_service

            final_state = graph2.invoke(initial_state)
            report: RiskAssessmentReport = final_state["final_report"]

            elapsed_ms = round((time.perf_counter() - start_time) * 1000)
            _log.info("[Graph2 Execution] Finished for project_id=%s in %dms", project_id, elapsed_ms)

            return {
                "status": "success",
                "overall_risk": report.priority,
                "risk_count": len(report.categorized_risks),
                "confidence": report.confidence,
                "report": report.model_dump(mode="json"),
                "execution_time_ms": elapsed_ms,
            }
        except Exception as exc:
            _log.error("[Graph2 Execution] Failed for project_id=%s — error: %s", project_id, exc)
            if isinstance(exc, ProjectNotFoundError):
                raise
            raise GraphExecutionError(message=f"Graph 2 execution failed for project '{project_id}': {exc}", graph_name="Graph2")

    def execute_full_analysis(self, project_id: str) -> dict[str, Any]:
        """
        Primary orchestration endpoint:
            Registry -> ProjectSnapshot -> Graph1 -> KnowledgeBundle -> Intelligence Engine -> ProjectIntelligence -> Graph2 -> RiskAssessmentReport
        """
        total_start = time.perf_counter()
        _log.info("[Full Analysis Execution] Started for project_id=%s", project_id)

        int_pid = self._resolve_project(project_id)

        g1_res = self.execute_graph1(project_id)
        g1_ms = g1_res["execution_time_ms"]

        intel_res = self.execute_intelligence(project_id)
        intel_ms = intel_res["execution_time_ms"]

        g2_res = self.execute_graph2(project_id)
        g2_ms = g2_res["execution_time_ms"]

        total_ms = round((time.perf_counter() - total_start) * 1000)
        _log.info("[Full Analysis Execution] Finished for project_id=%s in %dms (g1=%dms, intel=%dms, g2=%dms)", project_id, total_ms, g1_ms, intel_ms, g2_ms)

        return {
            "status": "success",
            "knowledge_summary": g1_res,
            "project_intelligence": intel_res,
            "risk_report": g2_res["report"],
            "execution_summary": {
                "graph1_ms": g1_ms,
                "intelligence_ms": intel_ms,
                "graph2_ms": g2_ms,
                "total_ms": total_ms,
            },
        }


# Global singleton instance
_execution_service_instance: GraphExecutionService | None = None


def get_graph_execution_service() -> GraphExecutionService:
    """Retrieve global singleton GraphExecutionService."""
    global _execution_service_instance
    if _execution_service_instance is None:
        _execution_service_instance = GraphExecutionService()
    return _execution_service_instance
