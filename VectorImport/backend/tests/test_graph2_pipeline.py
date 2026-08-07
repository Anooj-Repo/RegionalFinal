"""
tests/test_graph2_pipeline.py
------------------------------
End-to-end integration tests for Graph 2: Decision Intelligence & Risk Assessment Pipeline.
"""

import pytest
from graphs.graph2 import graph2, route_after_reflection
from intelligence.engine import get_intelligence_engine
from workflow.workflow_service import WorkflowService
from schemas.domain import RiskAssessmentReport, ReflectionFeedback
from tests.test_graph2_services import MockLLMService


@pytest.fixture
def mock_llm():
    return MockLLMService()


class TestGraph2Pipeline:

    def test_graph2_execution_alpha(self, mock_llm):
        bundle = WorkflowService().run_graph1(1)
        intel = get_intelligence_engine().analyze(bundle)
        initial_state = {
            "intelligence": intel,
            "llm_service": mock_llm,
            "retry_count": 0,
            "max_retries": 2,
        }

        final_state = graph2.invoke(initial_state)

        assert "final_report" in final_state
        report: RiskAssessmentReport = final_state["final_report"]
        assert isinstance(report, RiskAssessmentReport)
        assert report.project_id == "PROG-ALPHA-2026"
        assert len(report.executive_summary) > 0
        assert len(report.categorized_risks) > 0
        assert len(report.evidence) > 0
        assert len(report.mitigations) > 0
        assert report.confidence >= 0.7
        assert report.priority in ("MEDIUM", "HIGH", "CRITICAL")

    def test_graph2_execution_beta(self, mock_llm):
        bundle = WorkflowService().run_graph1(2)
        intel = get_intelligence_engine().analyze(bundle)

        final_state = graph2.invoke({"intelligence": intel, "llm_service": mock_llm})
        report: RiskAssessmentReport = final_state["final_report"]
        assert report.project_id == "PROG-BETA-2026"
        assert len(report.categorized_risks) > 0

    def test_graph2_execution_gamma(self, mock_llm):
        bundle = WorkflowService().run_graph1(3)
        intel = get_intelligence_engine().analyze(bundle)

        final_state = graph2.invoke({"intelligence": intel, "llm_service": mock_llm})
        report: RiskAssessmentReport = final_state["final_report"]
        assert report.project_id == "PROG-GAMMA-2026"
        assert len(report.categorized_risks) > 0

    def test_reflection_loop_conditional_routing(self):
        state_retry = {
            "reflection_feedback": ReflectionFeedback(
                passed=False,
                grounding_score=0.5,
                consistency_score=0.5,
                unsupported_claims=["Claim failed"],
            ),
            "retry_count": 1,
            "max_retries": 2,
        }
        target = route_after_reflection(state_retry)
        assert target == "mitigation_planning"

        state_passed = {
            "reflection_feedback": ReflectionFeedback(
                passed=True,
                grounding_score=0.9,
                consistency_score=0.9,
            ),
            "retry_count": 1,
            "max_retries": 2,
        }
        target_passed = route_after_reflection(state_passed)
        assert target_passed == "risk_report_builder"

    def test_workflow_service_run_graph2(self, mock_llm):
        service = WorkflowService()
        bundle = service.run_graph1(1)
        intel = get_intelligence_engine().analyze(bundle)

        final_state = graph2.invoke({"intelligence": intel, "llm_service": mock_llm})
        report: RiskAssessmentReport = final_state["final_report"]

        assert isinstance(report, RiskAssessmentReport)
        assert report.project_id == "PROG-ALPHA-2026"
        assert len(report.mitigations) > 0
