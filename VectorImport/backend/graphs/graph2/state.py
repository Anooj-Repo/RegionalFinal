"""
graphs/graph2/state.py
----------------------
State definition for Graph 2: Decision Intelligence & Risk Assessment Pipeline.
"""

from __future__ import annotations

from typing import TypedDict, Optional, Any
from intelligence.schemas import ProjectIntelligence
from schemas.domain.risk_report import (
    CategorizedRisk,
    EvidenceItem,
    EvidenceReference,
    EvidencePackage,
    EvidenceTrace,
    MitigationPlan,
    ReflectionFeedback,
    RiskAssessmentReport,
)


class Graph2State(TypedDict, total=False):
    """
    State container passed through Graph 2 nodes.
    """

    intelligence: ProjectIntelligence
    llm_service: Any
    context_summary: str
    retrieved_evidence: list[EvidenceItem]
    evidence_package: Optional[EvidencePackage]
    evidence_traces: list[EvidenceTrace]
    decision_plan: list[str]
    categorized_risks: list[CategorizedRisk]
    mitigations: list[MitigationPlan]
    reflection_feedback: Optional[ReflectionFeedback]
    retry_count: int
    max_retries: int
    final_report: Optional[RiskAssessmentReport]
