"""
tests/test_api_endpoints.py
----------------------------
Integration tests for Flask REST API endpoints and Controllers.
"""

import pytest
from factory import create_app
import services.graph_execution_service as ges_module
from services.graph_execution_service import GraphExecutionService
from tests.test_graph2_services import MockLLMService


@pytest.fixture
def client(monkeypatch):
    app = create_app("testing")
    app.config["TESTING"] = True

    mock_svc = GraphExecutionService(llm_service=MockLLMService())
    monkeypatch.setattr(ges_module, "_execution_service_instance", mock_svc)

    with app.test_client() as client:
        yield client


class TestApiEndpoints:

    def test_health_endpoint(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "healthy"

    def test_get_projects_endpoint(self, client):
        res = client.get("/api/projects")
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["project_id"] == "PROG-ALPHA-2026"

    def test_knowledge_endpoint(self, client):
        res = client.post("/api/projects/1/knowledge")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert data["project_id"] == "PROG-ALPHA-2026"

    def test_intelligence_endpoint(self, client):
        res = client.post("/api/projects/PROG-ALPHA-2026/intelligence")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "overall_health" in data

    def test_analysis_endpoint(self, client):
        res = client.post("/api/projects/1/analysis")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "overall_risk" in data

    def test_analyze_full_endpoint(self, client):
        res = client.post("/api/projects/PROG-ALPHA-2026/analyze")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "knowledge_summary" in data
        assert "project_intelligence" in data
        assert "risk_report" in data
        assert "execution_summary" in data

    def test_project_not_found_returns_404(self, client):
        res = client.post("/api/projects/unknown_proj_999/analyze")
        assert res.status_code == 404
        data = res.get_json()
        assert data["status"] == "error"
        assert data["code"] == "PROJECT_NOT_FOUND"
