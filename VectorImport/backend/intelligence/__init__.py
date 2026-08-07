"""
intelligence/__init__.py
------------------------
Public surface of the intelligence package.
"""

from intelligence.config import IntelligenceConfig
from intelligence.schemas import (
    SignalSeverity,
    ProjectHealthStatus,
    DeterministicSignal,
    DependencyAnalysis,
    TimelineAnalysis,
    CommunicationAnalysis,
    SentimentAnalysis,
    ProjectMetrics,
    ProjectHealth,
    DeltaSummary,
    ProjectIntelligence,
)
from intelligence.engine import IntelligenceEngine, get_intelligence_engine

__all__ = [
    "IntelligenceConfig",
    "SignalSeverity",
    "ProjectHealthStatus",
    "DeterministicSignal",
    "DependencyAnalysis",
    "TimelineAnalysis",
    "CommunicationAnalysis",
    "SentimentAnalysis",
    "ProjectMetrics",
    "ProjectHealth",
    "DeltaSummary",
    "ProjectIntelligence",
    "IntelligenceEngine",
    "get_intelligence_engine",
]
