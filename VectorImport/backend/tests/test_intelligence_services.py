"""
tests/test_intelligence_services.py
------------------------------------
Unit tests for the 8 deterministic intelligence services.
"""

import pytest
from workflow.workflow_service import WorkflowService
from intelligence.services import (
    DependencyAnalysisService,
    TimelineAnalysisService,
    CommunicationAnalysisService,
    SentimentAnalysisService,
    MetricsService,
    HealthAnalysisService,
    DeltaService,
    ScoringService,
)
from intelligence.schemas import (
    DependencyAnalysis,
    TimelineAnalysis,
    CommunicationAnalysis,
    SentimentAnalysis,
    ProjectMetrics,
    ProjectHealth,
    DeltaSummary,
    DeterministicSignal,
    ProjectHealthStatus,
)


@pytest.fixture
def bundle_alpha():
    """Generate ProjectKnowledgeBundle for Project 1 (Alpha)."""
    return WorkflowService().run_graph1(1)


class TestDependencyAnalysisService:

    def test_returns_dependency_analysis(self, bundle_alpha):
        service = DependencyAnalysisService()
        result = service.analyze(bundle_alpha)
        assert isinstance(result, DependencyAnalysis)
        assert result.total_dependencies >= 0


class TestTimelineAnalysisService:

    def test_returns_timeline_analysis(self, bundle_alpha):
        service = TimelineAnalysisService()
        result = service.analyze(bundle_alpha)
        assert isinstance(result, TimelineAnalysis)
        assert 0.0 <= result.overall_completion_pct <= 100.0
        assert result.blocked_task_count >= 1  # Task 102 is blocked in Alpha


class TestCommunicationAnalysisService:

    def test_returns_communication_analysis(self, bundle_alpha):
        service = CommunicationAnalysisService()
        result = service.analyze(bundle_alpha)
        assert isinstance(result, CommunicationAnalysis)
        assert result.total_documents > 0
        assert result.escalation_count >= 1


class TestSentimentAnalysisService:

    def test_returns_sentiment_analysis(self, bundle_alpha):
        service = SentimentAnalysisService()
        result = service.analyze(bundle_alpha)
        assert isinstance(result, SentimentAnalysis)
        assert -1.0 <= result.net_sentiment_score <= 1.0


class TestMetricsService:

    def test_returns_project_metrics(self, bundle_alpha):
        service = MetricsService()
        result = service.analyze(bundle_alpha)
        assert isinstance(result, ProjectMetrics)
        assert result.blocker_density > 0.0


class TestHealthAnalysisService:

    def test_returns_project_health(self, bundle_alpha):
        metrics = MetricsService().analyze(bundle_alpha)
        timeline = TimelineAnalysisService().analyze(bundle_alpha)
        sentiment = SentimentAnalysisService().analyze(bundle_alpha)

        health_service = HealthAnalysisService()
        result = health_service.analyze(metrics, timeline, sentiment)

        assert isinstance(result, ProjectHealth)
        assert 0.0 <= result.health_score <= 100.0
        assert result.status in (ProjectHealthStatus.AT_RISK, ProjectHealthStatus.CRITICAL)


class TestDeltaService:

    def test_returns_delta_summary(self, bundle_alpha):
        service = DeltaService()
        result = service.analyze(bundle_alpha)
        assert isinstance(result, DeltaSummary)
        assert result.has_critical_changes is True


class TestScoringService:

    def test_returns_list_of_signals(self, bundle_alpha):
        service = ScoringService()
        signals = service.analyze(bundle_alpha)
        assert isinstance(signals, list)
        assert len(signals) > 0
        assert all(isinstance(s, DeterministicSignal) for s in signals)
