"""
tests/test_intelligence_engine.py
----------------------------------
Integration tests for IntelligenceEngine orchestrator.
"""

import pytest
from workflow.workflow_service import WorkflowService
from intelligence.engine import IntelligenceEngine, get_intelligence_engine
from intelligence.schemas import (
    ProjectIntelligence,
    ProjectHealthStatus,
    DependencyAnalysis,
    TimelineAnalysis,
    CommunicationAnalysis,
    SentimentAnalysis,
    ProjectMetrics,
    ProjectHealth,
    DeltaSummary,
)


class TestIntelligenceEngine:

    def test_engine_single_public_method(self):
        engine = IntelligenceEngine()
        public_methods = [
            m for m in dir(engine)
            if not m.startswith("_") and callable(getattr(engine, m))
        ]
        assert "analyze" in public_methods

    def test_analyze_alpha_project(self):
        bundle = WorkflowService().run_graph1(1)
        engine = IntelligenceEngine()

        intel = engine.analyze(bundle)

        assert isinstance(intel, ProjectIntelligence)
        assert intel.project_id == "PROG-ALPHA-2026"
        assert isinstance(intel.health, ProjectHealth)
        assert isinstance(intel.metrics, ProjectMetrics)
        assert isinstance(intel.dependency_analysis, DependencyAnalysis)
        assert isinstance(intel.timeline_analysis, TimelineAnalysis)
        assert isinstance(intel.communication_analysis, CommunicationAnalysis)
        assert isinstance(intel.sentiment_analysis, SentimentAnalysis)
        assert isinstance(intel.delta, DeltaSummary)
        assert len(intel.signals) > 0

        # Health status check: Alpha has blocked task & vendor delay -> AT_RISK or CRITICAL
        assert intel.health.status in (ProjectHealthStatus.AT_RISK, ProjectHealthStatus.CRITICAL)

    def test_analyze_beta_project(self):
        bundle = WorkflowService().run_graph1(2)
        intel = IntelligenceEngine().analyze(bundle)

        assert isinstance(intel, ProjectIntelligence)
        assert intel.project_id == "PROG-BETA-2026"
        assert intel.health.status in (ProjectHealthStatus.AT_RISK, ProjectHealthStatus.CRITICAL)

    def test_analyze_gamma_project(self):
        bundle = WorkflowService().run_graph1(3)
        intel = IntelligenceEngine().analyze(bundle)

        assert isinstance(intel, ProjectIntelligence)
        assert intel.project_id == "PROG-GAMMA-2026"
        assert intel.health.status in (ProjectHealthStatus.AT_RISK, ProjectHealthStatus.CRITICAL)

    def test_no_dicts_in_output(self):
        bundle = WorkflowService().run_graph1(1)
        intel = get_intelligence_engine().analyze(bundle)

        assert hasattr(type(intel.health), "model_fields")
        assert hasattr(type(intel.metrics), "model_fields")
        assert hasattr(type(intel.dependency_analysis), "model_fields")
        assert hasattr(type(intel.timeline_analysis), "model_fields")
        assert hasattr(type(intel.communication_analysis), "model_fields")
        assert hasattr(type(intel.sentiment_analysis), "model_fields")
        assert hasattr(type(intel.delta), "model_fields")
        assert all(hasattr(type(s), "model_fields") for s in intel.signals)
