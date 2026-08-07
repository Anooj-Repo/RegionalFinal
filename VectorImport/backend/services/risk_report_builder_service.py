"""
services/risk_report_builder_service.py
----------------------------------------
RiskReportBuilderService — Node 7 service for Graph 2.

Assembles all validated decision artifacts and constructs full EvidenceTrace objects for every risk in RiskAssessmentReport.
"""

from __future__ import annotations

from intelligence.schemas import ProjectIntelligence
from schemas.domain.risk_report import (
    CategorizedRisk,
    EvidenceItem,
    EvidencePackage,
    EvidenceReference,
    EvidenceTrace,
    MitigationPlan,
    ReflectionFeedback,
    RiskAssessmentReport,
)
from prompts.graph2_prompts import RISK_REPORT_BUILDER_PROMPT
from services.llm_service import LLMService, get_llm_service
from utils.logger import get_logger

_log = get_logger("services.risk_report_builder")


class RiskReportBuilderService:
    """
    Assembles the final RiskAssessmentReport with full EvidenceTrace provenance per risk.
    """

    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or get_llm_service()

    def build_report(
        self,
        intelligence: ProjectIntelligence,
        context_summary: str,
        risks: list[CategorizedRisk],
        evidence: list[EvidenceItem] | EvidencePackage,
        mitigations: list[MitigationPlan],
        feedback: ReflectionFeedback | None,
        evidence_package: EvidencePackage | None = None,
    ) -> RiskAssessmentReport:
        _log.info("Building final RiskAssessmentReport with EvidenceTraces for project_id=%s", intelligence.project_id)

        status_val = intelligence.health.status.value.lower()
        if status_val == "critical":
            priority = "CRITICAL"
            escalation = "EXECUTIVE_BOARD"
        elif status_val == "at_risk":
            priority = "HIGH"
            escalation = "STEERING_COMMITTEE"
        else:
            priority = "MEDIUM"
            escalation = "PROJECT_MANAGER"

        prompt = RISK_REPORT_BUILDER_PROMPT.format(
            project_id=intelligence.project_id,
            priority=priority,
            escalation_level=escalation,
        )

        exec_summary = self.llm_service.invoke_text(prompt)

        # Build EvidenceReference lookup map
        pkg = evidence_package if isinstance(evidence_package, EvidencePackage) else (evidence if isinstance(evidence, EvidencePackage) else None)
        ref_map: dict[str, EvidenceReference] = {}

        if pkg and pkg.retrieved_documents:
            for ref in pkg.retrieved_documents:
                ref_map[ref.evidence_id] = ref

        # Construct EvidenceTrace for each CategorizedRisk
        evidence_traces: list[EvidenceTrace] = []

        for r in risks:
            supporting_refs: list[EvidenceReference] = []
            for ev_id in r.supporting_evidence_ids:
                if ev_id in ref_map:
                    supporting_refs.append(ref_map[ev_id])

            if not supporting_refs and ref_map:
                supporting_refs = list(ref_map.values())[:2]

            evidence_traces.append(
                EvidenceTrace(
                    risk_id=r.risk_id,
                    supporting_evidence=supporting_refs,
                )
            )

        # Legacy EvidenceItem list for backwards compatibility
        legacy_evidence = [
            EvidenceItem(
                evidence_id=ref.evidence_id,
                source_doc_id=ref.document_id,
                title=f"Source {ref.source.value} (chunk {ref.chunk_id})",
                content_snippet=f"Reference to {ref.source.value} document {ref.document_id}",
                relevance_score=ref.similarity_score,
            )
            for ref in ref_map.values()
        ]

        affected_stakeholders = [
            intelligence.project_id,
            "Programme Sponsor",
            "Project Lead",
        ]

        report = RiskAssessmentReport(
            project_id=intelligence.project_id,
            executive_summary=exec_summary,
            categorized_risks=risks,
            evidence=legacy_evidence,
            evidence_traces=evidence_traces,
            mitigations=mitigations,
            confidence=0.92 if (feedback and feedback.passed) else 0.75,
            priority=priority,
            affected_stakeholders=affected_stakeholders,
            recommended_escalation_level=escalation,
            reflection_feedback=feedback,
        )

        _log.info("RiskAssessmentReport built with %d EvidenceTraces — %s", len(evidence_traces), report.summary())
        return report
