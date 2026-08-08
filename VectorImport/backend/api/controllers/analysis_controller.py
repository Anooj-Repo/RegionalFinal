"""
api/controllers/analysis_controller.py
---------------------------------------
AnalysisController — Handles analysis graph execution requests.

Delegates execution to GraphExecutionService and formats HTTP responses.
"""

from __future__ import annotations

from flask import jsonify, Response
from services.graph_execution_service import GraphExecutionService, get_graph_execution_service
from utils.logger import get_logger

_log = get_logger("api.controllers.analysis")


class AnalysisController:
    """
    Controller for Graph 1, Intelligence Engine, Graph 2, and Full Analysis execution endpoints.
    Accepts an injectable GraphExecutionService instance for clean unit-testing.
    """

    def __init__(self, execution_service: GraphExecutionService | None = None) -> None:
        self._execution_service = execution_service

    @property
    def service(self) -> GraphExecutionService:
        return self._execution_service or get_graph_execution_service()

    def execute_knowledge(self, project_id: str) -> Response:
        """
        POST /api/projects/<project_id>/knowledge
        Executes Graph 1 Knowledge Intelligence Pipeline.
        """
        _log.info("[AnalysisController] POST /knowledge requested for project_id=%s", project_id)
        result = self.service.execute_graph1(project_id)
        return jsonify(result), 200

    def execute_intelligence(self, project_id: str) -> Response:
        """
        POST /api/projects/<project_id>/intelligence
        Executes Project Intelligence Engine.
        """
        _log.info("[AnalysisController] POST /intelligence requested for project_id=%s", project_id)
        result = self.service.execute_intelligence(project_id)
        return jsonify(result), 200

    def execute_analysis(self, project_id: str) -> Response:
        """
        POST /api/projects/<project_id>/analysis
        Executes Graph 2 Decision Intelligence Pipeline.
        """
        _log.info("[AnalysisController] POST /analysis requested for project_id=%s", project_id)
        result = self.service.execute_graph2(project_id)
        return jsonify(result), 200

    def execute_full_analysis(self, project_id: str) -> Response:
        """
        POST /api/projects/<project_id>/analyze
        Executes full end-to-end analysis pipeline (Graph 1 -> Intelligence Engine -> Graph 2).
        """
        _log.info("[AnalysisController] POST /analyze requested for project_id=%s", project_id)
        result = self.service.execute_full_analysis(project_id)
        return jsonify(result), 200
