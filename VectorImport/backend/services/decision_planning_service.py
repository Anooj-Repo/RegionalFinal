"""
services/decision_planning_service.py
--------------------------------------
DecisionPlanningService — Node 3 service for Graph 2.

Formulates strategic decision priorities and maps reasoning to EvidencePackage IDs.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from intelligence.schemas import ProjectIntelligence
from schemas.domain.risk_report import EvidenceItem, EvidencePackage
from prompts.graph2_prompts import DECISION_PLANNER_PROMPT
from services.llm_service import LLMService, get_llm_service
from utils.logger import get_logger

_log = get_logger("services.decision_planning")


class DecisionPriorityItem(BaseModel):
    priority_text: str = Field(..., description="Strategic decision priority description.")
    reasoning: str = Field(..., description="Logical reasoning supporting this decision.")
    referenced_evidence_ids: list[str] = Field(default_factory=list, description="IDs of evidence supporting this conclusion.")


class DecisionPlanOutput(BaseModel):
    priorities: list[str] = Field(..., description="Top strategic decision priorities.")
    decision_items: list[DecisionPriorityItem] = Field(default_factory=list, description="Detailed priorities with reasoning and evidence IDs.")


class DecisionPlanningService:
    """
    Formulates strategic decision priorities via LLM with evidence ID tracing.
    """

    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or get_llm_service()

    def plan_decisions(
        self,
        intelligence: ProjectIntelligence,
        context_summary: str,
        evidence: list[EvidenceItem] | EvidencePackage,
    ) -> list[str]:
        _log.info("Formulating decision priorities via LLM with evidence tracing for project_id=%s", intelligence.project_id)

        if isinstance(evidence, EvidencePackage):
            evidence_refs = evidence.retrieved_documents
        else:
            evidence_refs = evidence

        evidence_summary_lines = [
            f"- [{getattr(e, 'evidence_id', 'ref_doc')}] Source: {getattr(e, 'source', 'document')}, Doc ID: {getattr(e, 'document_id', getattr(e, 'source_doc_id', 'unknown'))}"
            for e in evidence_refs
        ]
        evidence_str = "\n".join(evidence_summary_lines) if evidence_summary_lines else "None"

        prompt = DECISION_PLANNER_PROMPT.format(
            context_summary=context_summary,
            evidence_count=len(evidence_refs),
            evidence_titles=evidence_str,
        )

        prompt += "\nInstruction: Every identified decision priority must explicitly reference the evidence_ids that support the reasoning."

        output: DecisionPlanOutput = self.llm_service.invoke_structured(
            prompt, DecisionPlanOutput
        )

        _log.info("Formulated %d decision priorities via LLM for project_id=%s", len(output.priorities), intelligence.project_id)
        return output.priorities
