"""
intelligence/services/health_analysis_service.py
-------------------------------------------------
HealthAnalysisService — Calculates project health score and status.
"""

from __future__ import annotations

from intelligence.config import IntelligenceConfig
from intelligence.schemas import (
    ProjectHealth,
    ProjectHealthStatus,
    ProjectMetrics,
    TimelineAnalysis,
    SentimentAnalysis,
)
from utils.logger import get_logger

_log = get_logger("intelligence.services.health_analysis")


class HealthAnalysisService:
    """
    Evaluates composite project health score (0-100) and status using IntelligenceConfig thresholds.
    """

    def __init__(self, config: IntelligenceConfig | None = None) -> None:
        self.config = config or IntelligenceConfig()

    def analyze(
        self,
        metrics: ProjectMetrics,
        timeline: TimelineAnalysis,
        sentiment: SentimentAnalysis,
    ) -> ProjectHealth:
        _log.debug("Calculating health score")

        score = 100.0
        drivers: list[str] = []

        # Deductions
        if timeline.blocked_task_count > 0:
            ded = timeline.blocked_task_count * self.config.blocked_task_deduction
            score -= ded
            drivers.append(f"{timeline.blocked_task_count} task(s) currently blocked (-{ded:.0f} pts)")

        if metrics.critical_risk_count > 0:
            ded = metrics.critical_risk_count * self.config.critical_risk_deduction
            score -= ded
            drivers.append(f"{metrics.critical_risk_count} critical/high risk(s) open (-{ded:.0f} pts)")

        if sentiment.urgent_count > 0:
            ded = sentiment.urgent_count * self.config.urgent_sentiment_deduction
            score -= ded
            drivers.append(f"{sentiment.urgent_count} urgent communication(s) logged (-{ded:.0f} pts)")

        final_score = max(0.0, min(100.0, score))

        if final_score >= self.config.healthy_min_score:
            status = ProjectHealthStatus.HEALTHY
        elif final_score >= self.config.at_risk_min_score:
            status = ProjectHealthStatus.AT_RISK
        else:
            status = ProjectHealthStatus.CRITICAL

        if not drivers:
            drivers.append("Project operating within healthy baseline parameters.")

        risk_exposure = min(100.0, (100.0 - final_score) * 1.1)

        health = ProjectHealth(
            health_score=round(final_score, 1),
            status=status,
            primary_drivers=drivers,
            risk_exposure_score=round(risk_exposure, 1),
        )
        _log.info("HealthAnalysis complete — score=%.1f, status=%s", final_score, status.value)
        return health
