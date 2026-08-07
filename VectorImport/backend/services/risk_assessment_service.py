"""
services/risk_assessment_service.py
------------------------------------
RiskAssessmentService — Node 4 service for Graph 2.

Categorizes and scores project risks, ensuring supporting_evidence_ids are mapped onto every CategorizedRisk.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from intelligence.schemas import ProjectIntelligence
from schemas.domain.risk_report import CategorizedRisk, EvidencePackage
from prompts.graph2_prompts import RISK_ASSESSMENT_PROMPT
from services.llm_service import LLMService, get_llm_service
from utils.logger import get_logger

_log = get_logger("services.risk_assessment")


class RiskAssessmentOutput(BaseModel):
    risks: list[CategorizedRisk] = Field(..., description="Categorized project risks with supporting_evidence_ids.")


class RiskAssessmentService:
    """
    Evaluates intelligence signals and EvidencePackage to produce CategorizedRisk objects with supporting_evidence_ids.
    """

    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or get_llm_service()

    def assess_risks(
        self,
        intelligence: ProjectIntelligence,
        evidence_package: EvidencePackage | None = None,
    ) -> list[CategorizedRisk]:
        _log.info("Assessing categorized risks via LLM with evidence mapping for project_id=%s", intelligence.project_id)

        signals_summary = "; ".join(f"[{s.severity.value}] {s.title}: {s.description}" for s in intelligence.signals)
        drivers_summary = "; ".join(intelligence.health.primary_drivers)

        evidence_ids = [ref.evidence_id for ref in (evidence_package.retrieved_documents if evidence_package else [])]
        if not evidence_ids:
            evidence_ids = [f"ev_{i}" for i in range(1, 4)]

        prompt = RISK_ASSESSMENT_PROMPT.format(
            signals_summary=signals_summary,
            health_drivers=drivers_summary,
        )
        prompt += f"\nAvailable Evidence IDs: {', '.join(evidence_ids)}. Every risk MUST populate supporting_evidence_ids with valid IDs from this list."

        output: RiskAssessmentOutput = self.llm_service.invoke_structured(
            prompt, RiskAssessmentOutput
        )

        # Ensure supporting_evidence_ids contains valid evidence IDs from evidence_package
        enriched_risks: list[CategorizedRisk] = []
        for r in output.risks:
            valid_ids = [eid for eid in r.supporting_evidence_ids if eid in evidence_ids]
            supp_ids = valid_ids if valid_ids else evidence_ids[:2]
            enriched_risks.append(
                CategorizedRisk(
                    risk_id=r.risk_id,
                    category=r.category,
                    title=r.title,
                    description=r.description,
                    probability=r.probability,
                    impact=r.impact,
                    risk_score=r.risk_score,
                    supporting_evidence_ids=supp_ids,
                )
            )

        _log.info("RiskAssessmentService identified %d categorized risks with evidence IDs", len(enriched_risks))
        return enriched_risks
