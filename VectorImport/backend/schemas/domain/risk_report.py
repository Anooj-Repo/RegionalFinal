"""
schemas/domain/risk_report.py
-----------------------------
Pydantic v2 domain schemas for Graph 2 output — RiskAssessmentReport & Evidence Provenance.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field

from schemas.domain.normalized_document import DocumentSource


class EvidenceReference(BaseModel):
    """
    Lightweight evidence reference storing document/chunk identifiers and retrieval score.
    Clean reference for backend fetching when user clicks 'View Evidence'.
    """

    model_config = ConfigDict(frozen=True)

    document_id: str = Field(..., description="Original document ID.")
    chunk_id: str = Field(..., description="Vector chunk ID.")
    source: DocumentSource = Field(..., description="Source type (email, chat_message, meeting_note, status_report, risk_entry, historical_project, project_task).")
    similarity_score: float = Field(default=0.8, ge=0.0, le=1.0)

    @property
    def evidence_id(self) -> str:
        """Helper property for unique reference keying."""
        return f"ref_{self.document_id}_{self.chunk_id}"


class EvidencePackage(BaseModel):
    """
    Container of all retrieved evidence, entity references, and relationship context for Graph 2.
    """

    model_config = ConfigDict(frozen=True)

    retrieved_documents: list[EvidenceReference] = Field(default_factory=list)
    supporting_documents: list[EvidenceReference] = Field(default_factory=list)
    entity_references: list[str] = Field(default_factory=list)
    relationship_references: list[str] = Field(default_factory=list)


class EvidenceTrace(BaseModel):
    """
    Audit trace mapping a specific risk to its supporting evidence references.
    """

    model_config = ConfigDict(frozen=True)

    trace_id: str = Field(default_factory=lambda: f"tr_{uuid4().hex[:8]}")
    risk_id: str = Field(..., description="ID of the risk supported by this trace.")
    supporting_evidence: list[EvidenceReference] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CategorizedRisk(BaseModel):
    """
    Extracted or identified risk category item with evidence provenance mapping.
    """

    model_config = ConfigDict(frozen=True)

    risk_id: str = Field(..., description="Unique risk identifier.")
    category: str = Field(..., description="Category (vendor, timeline, data_quality, compliance).")
    title: str = Field(..., description="Headline title of the risk.")
    description: str = Field(..., description="Detailed description of the risk scenario.")
    probability: str = Field(..., description="low, medium, high.")
    impact: str = Field(..., description="low, medium, high, critical.")
    risk_score: float = Field(default=50.0, ge=0.0, le=100.0)
    supporting_evidence_ids: list[str] = Field(default_factory=list, description="IDs/chunk_ids of evidence supporting this risk.")


class EvidenceItem(BaseModel):
    """
    Legacy evidence item representation (maintained for backwards compatibility).
    """

    model_config = ConfigDict(frozen=True)

    evidence_id: str = Field(..., description="Unique evidence ID.")
    source_doc_id: str = Field(..., description="ID of source document or chunk.")
    title: str = Field(..., description="Source title.")
    content_snippet: str = Field(..., description="Extracted text snippet.")
    relevance_score: float = Field(default=0.8, ge=0.0, le=1.0)


class MitigationPlan(BaseModel):
    """
    Actionable mitigation recommendation for an identified risk with evidence provenance.
    """

    model_config = ConfigDict(frozen=True)

    mitigation_id: str = Field(..., description="Unique mitigation ID.")
    target_risk_id: str = Field(..., description="ID of the risk this mitigation addresses.")
    action_title: str = Field(..., description="Title of proposed mitigation action.")
    action_description: str = Field(..., description="Detailed action plan.")
    owner: str = Field(default="Unassigned", description="Primary owner responsible for execution.")
    due_date: str = Field(default="TBD", description="Target completion date.")
    cost_estimate: str = Field(default="Low", description="Cost estimate (Low, Medium, High).")
    expected_impact: str = Field(default="High Risk Reduction", description="Anticipated outcome.")
    supporting_evidence_ids: list[str] = Field(default_factory=list, description="Evidence IDs/chunk_ids justifying this mitigation.")


class ReflectionFeedback(BaseModel):
    """
    Evaluation output from ReflectionNode checking grounding and consistency.
    """

    model_config = ConfigDict(frozen=True)

    passed: bool = Field(..., description="True if validation checks passed.")
    grounding_score: float = Field(default=1.0, ge=0.0, le=1.0)
    consistency_score: float = Field(default=1.0, ge=0.0, le=1.0)
    unsupported_claims: list[str] = Field(default_factory=list)
    reflection_notes: str = Field(default="")
    retry_count: int = Field(default=0, ge=0)


class RiskAssessmentReport(BaseModel):
    """
    The canonical output contract of Graph 2, handed off to Graph 3.
    """

    model_config = ConfigDict(frozen=True)

    report_id: UUID = Field(default_factory=uuid4)
    project_id: str = Field(..., description="Project ID.")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    executive_summary: str = Field(..., description="High-level executive summary.")
    categorized_risks: list[CategorizedRisk] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    evidence_traces: list[EvidenceTrace] = Field(default_factory=list, description="Full evidence provenance traces per risk.")
    mitigations: list[MitigationPlan] = Field(default_factory=list)

    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    priority: str = Field(default="HIGH", description="LOW, MEDIUM, HIGH, CRITICAL.")
    affected_stakeholders: list[str] = Field(default_factory=list)
    recommended_escalation_level: str = Field(
        default="STEERING_COMMITTEE",
        description="NONE, PROJECT_MANAGER, STEERING_COMMITTEE, EXECUTIVE_BOARD.",
    )
    reflection_feedback: Optional[ReflectionFeedback] = Field(default=None)

    def summary(self) -> dict:
        """Lightweight summary dictionary for logging."""
        return {
            "report_id": str(self.report_id),
            "project_id": self.project_id,
            "priority": self.priority,
            "confidence": self.confidence,
            "risks_count": len(self.categorized_risks),
            "mitigations_count": len(self.mitigations),
            "evidence_count": len(self.evidence),
            "evidence_traces_count": len(self.evidence_traces),
            "escalation_level": self.recommended_escalation_level,
            "generated_at": self.generated_at.isoformat(),
        }
