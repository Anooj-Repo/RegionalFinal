"""
tests/test_graph_execution_service.py
--------------------------------------
Unit and integration tests for GraphExecutionService orchestrator.
"""

import pytest
from exceptions import ProjectNotFoundError
from services.graph_execution_service import GraphExecutionService, get_graph_execution_service
from tests.test_graph2_services import MockLLMService


class TestGraphExecutionService:

    @pytest.fixture
    def execution_service(self):
        return GraphExecutionService(llm_service=MockLLMService())

    def test_singleton_accessor(self):
        svc1 = get_graph_execution_service()
        svc2 = get_graph_execution_service()
        assert svc1 is svc2

    def test_invalid_project_id_raises_not_found(self, execution_service):
        with pytest.raises(ProjectNotFoundError):
            execution_service.execute_graph1("invalid_9999")

    def test_execute_graph1_alpha(self, execution_service):
        result = execution_service.execute_graph1("PROG-ALPHA-2026")
        assert result["status"] == "success"
        assert result["project_id"] == "PROG-ALPHA-2026"
        assert result["documents"] > 0
        assert result["entities"] > 0
        assert result["relationships"] > 0
        assert result["execution_time_ms"] >= 0

    def test_execute_intelligence_alpha(self, execution_service):
        result = execution_service.execute_intelligence("1")
        assert result["status"] == "success"
        assert result["project_id"] == "PROG-ALPHA-2026"
        assert "overall_health" in result
        assert "metrics" in result
        assert "blocked_tasks" in result
        assert "execution_time_ms" in result

    def test_execute_graph2_alpha(self, execution_service):
        result = execution_service.execute_graph2("PROG-ALPHA-2026")
        assert result["status"] == "success"
        assert "overall_risk" in result
        assert "confidence" in result
        assert "report" in result
        assert result["execution_time_ms"] >= 0

    def test_execute_full_analysis_alpha(self, execution_service):
        result = execution_service.execute_full_analysis("1")
        assert result["status"] == "success"
        assert "knowledge_summary" in result
        assert "project_intelligence" in result
        assert "risk_report" in result
        assert "execution_summary" in result
        assert result["execution_summary"]["total_ms"] >= 0
