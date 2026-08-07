"""
intelligence/schemas.py
-----------------------
Strongly typed Pydantic v2 schemas for the Project Intelligence Engine.

Every model is frozen and strictly typed. No plain dicts allowed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field


class SignalSeverity(str, Enum):
    INFO     = "info"
    WARNING  = "warning"
    CRITICAL = "critical"


class ProjectHealthStatus(str, Enum):
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    CRITICAL = "critical"


class DeterministicSignal(BaseModel):
    """
    Structured warning/alert signal produced by deterministic analysis rules.
    """

    model_config = ConfigDict(frozen=True)

    signal_id: str = Field(..., description="Unique signal identifier.")
    severity: SignalSeverity = Field(..., description="Severity level.")
    category: str = Field(..., description="Domain category (e.g. vendor, data_quality, compliance, timeline).")
    title: str = Field(..., description="Short summary title.")
    description: str = Field(..., description="Detailed explanation of the rule trigger.")
    source_entity_ids: list[str] = Field(default_factory=list, description="IDs of entities/documents triggering this signal.")


class DependencyAnalysis(BaseModel):
    """
    Analysis of dependency chains, bottlenecks, and structural constraints.
    """

    model_config = ConfigDict(frozen=True)

    total_dependencies: int = Field(default=0, ge=0)
    blocked_dependency_count: int = Field(default=0, ge=0)
    critical_path_length: int = Field(default=0, ge=0)
    bottleneck_entity_ids: list[str] = Field(default_factory=list)


class TimelineAnalysis(BaseModel):
    """
    Analysis of project schedule, progress, and task due dates.
    """

    model_config = ConfigDict(frozen=True)

    overall_completion_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    overdue_task_count: int = Field(default=0, ge=0)
    blocked_task_count: int = Field(default=0, ge=0)
    estimated_delay_days: int = Field(default=0, ge=0)
    is_on_track: bool = Field(default=True)


class CommunicationAnalysis(BaseModel):
    """
    Analysis of communication volume, participant activity, and escalations.
    """

    model_config = ConfigDict(frozen=True)

    total_documents: int = Field(default=0, ge=0)
    escalation_count: int = Field(default=0, ge=0)
    active_authors_count: int = Field(default=0, ge=0)
    channel_distribution_summary: str = Field(default="")


class SentimentAnalysis(BaseModel):
    """
    Sentiment distribution and trend across communication channels.
    """

    model_config = ConfigDict(frozen=True)

    net_sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    urgent_count: int = Field(default=0, ge=0)
    negative_count: int = Field(default=0, ge=0)
    positive_count: int = Field(default=0, ge=0)
    neutral_count: int = Field(default=0, ge=0)
    sentiment_trend: str = Field(default="stable")


class ProjectMetrics(BaseModel):
    """
    Quantitative operational health KPIs.
    """

    model_config = ConfigDict(frozen=True)

    task_completion_rate: float = Field(default=0.0, ge=0.0, le=100.0)
    blocker_density: float = Field(default=0.0, ge=0.0)
    open_risk_count: int = Field(default=0, ge=0)
    critical_risk_count: int = Field(default=0, ge=0)
    document_velocity: float = Field(default=0.0, ge=0.0)


class ProjectHealth(BaseModel):
    """
    Overall health score and status assessment.
    """

    model_config = ConfigDict(frozen=True)

    health_score: float = Field(default=100.0, ge=0.0, le=100.0)
    status: ProjectHealthStatus = Field(default=ProjectHealthStatus.HEALTHY)
    primary_drivers: list[str] = Field(default_factory=list)
    risk_exposure_score: float = Field(default=0.0, ge=0.0, le=100.0)


class DeltaSummary(BaseModel):
    """
    Summary of recent state changes and new escalations.
    """

    model_config = ConfigDict(frozen=True)

    newly_blocked_tasks: list[str] = Field(default_factory=list)
    new_escalations: list[str] = Field(default_factory=list)
    progress_delta_pct: float = Field(default=0.0)
    has_critical_changes: bool = Field(default=False)


class ProjectIntelligence(BaseModel):
    """
    Canonical output of the Intelligence Engine, handed off as the sole input to Graph 2.
    """

    model_config = ConfigDict(frozen=True)

    intelligence_id: UUID = Field(default_factory=uuid4)
    project_id: str = Field(...)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    health: ProjectHealth
    metrics: ProjectMetrics
    dependency_analysis: DependencyAnalysis
    timeline_analysis: TimelineAnalysis
    communication_analysis: CommunicationAnalysis
    sentiment_analysis: SentimentAnalysis
    signals: list[DeterministicSignal] = Field(default_factory=list)
    delta: DeltaSummary

    def summary(self) -> dict:
        """Lightweight summary dictionary for logging."""
        return {
            "intelligence_id": str(self.intelligence_id),
            "project_id": self.project_id,
            "health_status": self.health.status.value,
            "health_score": self.health.health_score,
            "signals_count": len(self.signals),
            "blocked_tasks": self.timeline_analysis.blocked_task_count,
            "generated_at": self.generated_at.isoformat(),
        }
