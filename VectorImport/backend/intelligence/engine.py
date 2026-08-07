"""
intelligence/engine.py
----------------------
IntelligenceEngine — Central orchestrator for deterministic project intelligence analysis.

Accepts a ProjectKnowledgeBundle (from Graph 1) and returns a ProjectIntelligence object
(to be handed off as sole input to Graph 2).
"""

from __future__ import annotations

from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle
from intelligence.config import IntelligenceConfig
from intelligence.schemas import ProjectIntelligence
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
from utils.logger import get_logger

_log = get_logger("intelligence.engine")


class IntelligenceEngine:
    """
    Orchestrates deterministic analysis services to construct ProjectIntelligence.

    Usage:
        engine = IntelligenceEngine()
        intelligence = engine.analyze(bundle)
    """

    def __init__(
        self,
        config: IntelligenceConfig | None = None,
        dependency_service:     DependencyAnalysisService    | None = None,
        timeline_service:       TimelineAnalysisService      | None = None,
        communication_service:  CommunicationAnalysisService | None = None,
        sentiment_service:      SentimentAnalysisService     | None = None,
        metrics_service:        MetricsService               | None = None,
        health_service:         HealthAnalysisService        | None = None,
        delta_service:          DeltaService                 | None = None,
        scoring_service:        ScoringService               | None = None,
    ) -> None:
        """
        All services are injectable for unit testing.
        Default to standard instances when omitted.
        """
        self.config = config or IntelligenceConfig()
        self._dep_service = dependency_service or DependencyAnalysisService()
        self._timeline_service = timeline_service or TimelineAnalysisService()
        self._comm_service = communication_service or CommunicationAnalysisService()
        self._sent_service = sentiment_service or SentimentAnalysisService()
        self._metrics_service = metrics_service or MetricsService()
        self._health_service = health_service or HealthAnalysisService(self.config)
        self._delta_service = delta_service or DeltaService()
        self._scoring_service = scoring_service or ScoringService()

    def analyze(self, bundle: ProjectKnowledgeBundle) -> ProjectIntelligence:
        """
        Transform a ProjectKnowledgeBundle into a ProjectIntelligence object.

        Args:
            bundle: The structured knowledge bundle produced by Graph 1.

        Returns:
            A fully-populated, strongly-typed ProjectIntelligence object.
        """
        _log.info("Starting IntelligenceEngine analysis for project_id=%s", bundle.project_id)

        # 1. Execute individual analysis services
        dep_analysis  = self._dep_service.analyze(bundle)
        time_analysis = self._timeline_service.analyze(bundle)
        comm_analysis = self._comm_service.analyze(bundle)
        sent_analysis = self._sent_service.analyze(bundle)
        metrics       = self._metrics_service.analyze(bundle)

        # 2. Composite health evaluation
        health = self._health_service.analyze(metrics, time_analysis, sent_analysis)

        # 3. Delta detection and scoring signals
        delta   = self._delta_service.analyze(bundle)
        signals = self._scoring_service.analyze(bundle)

        # 4. Assemble ProjectIntelligence
        intelligence = ProjectIntelligence(
            project_id=bundle.project_id,
            health=health,
            metrics=metrics,
            dependency_analysis=dep_analysis,
            timeline_analysis=time_analysis,
            communication_analysis=comm_analysis,
            sentiment_analysis=sent_analysis,
            signals=signals,
            delta=delta,
        )

        _log.info(
            "IntelligenceEngine analysis complete for project_id=%s — %s",
            bundle.project_id, intelligence.summary(),
        )
        return intelligence


# Singleton instance helper
_engine: IntelligenceEngine | None = None


def get_intelligence_engine() -> IntelligenceEngine:
    """
    Return the module-level IntelligenceEngine singleton.
    """
    global _engine
    if _engine is None:
        _engine = IntelligenceEngine()
    return _engine
