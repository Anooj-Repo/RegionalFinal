"""
services/mitigation_planning_service.py
----------------------------------------
MitigationPlanningService — Node 5 service for Graph 2.

Drafts actionable mitigation plans with supporting_evidence_ids justifying each action.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from schemas.domain.risk_report import CategorizedRisk, MitigationPlan, ReflectionFeedback, EvidencePackage
from prompts.graph2_prompts import MITIGATION_PLANNING_PROMPT
from services.llm_service import LLMService, get_llm_service
from utils.logger import get_logger

_log = get_logger("services.mitigation_planning")


class MitigationPlanningOutput(BaseModel):
    mitigations: list[MitigationPlan] = Field(..., description="Actionable mitigation plans with supporting_evidence_ids.")


class MitigationPlanningService:
    """
    Drafts mitigation plans for categorized risks via LLM with supporting_evidence_ids.
    """

    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or get_llm_service()

    def plan_mitigations(
        self,
        risks: list[CategorizedRisk],
        feedback: ReflectionFeedback | None = None,
        evidence_package: EvidencePackage | None = None,
    ) -> list[MitigationPlan]:
        _log.info("Planning mitigations via LLM for %d risks with evidence tracing", len(risks))

        risks_summary = "; ".join(f"{r.risk_id} ({r.category}): {r.title} [Evidence: {', '.join(r.supporting_evidence_ids)}]" for r in risks)
        fb_str = feedback.reflection_notes if feedback else "None"

        prompt = MITIGATION_PLANNING_PROMPT.format(
            risks_summary=risks_summary,
            reflection_feedback=fb_str,
        )
        prompt += "\nInstruction: Every mitigation plan MUST include supporting_evidence_ids justifying the action."

        output: MitigationPlanningOutput = self.llm_service.invoke_structured(
            prompt, MitigationPlanningOutput
        )

        risk_ev_map = {r.risk_id: r.supporting_evidence_ids for r in risks}
        fallback_ids = list(risk_ev_map.values())[0] if risk_ev_map else []

        enriched_mitigations: list[MitigationPlan] = []
        for m in output.mitigations:
            valid_ids = risk_ev_map.get(m.target_risk_id, fallback_ids)
            target_ids = m.supporting_evidence_ids if m.supporting_evidence_ids and any(e in risk_ev_map.get(m.target_risk_id, []) for e in m.supporting_evidence_ids) else valid_ids

            enriched_mitigations.append(
                MitigationPlan(
                    mitigation_id=m.mitigation_id,
                    target_risk_id=m.target_risk_id if m.target_risk_id in risk_ev_map else (risks[0].risk_id if risks else "risk_1"),
                    action_title=m.action_title,
                    action_description=m.action_description,
                    owner=m.owner,
                    due_date=m.due_date,
                    cost_estimate=m.cost_estimate,
                    expected_impact=m.expected_impact,
                    supporting_evidence_ids=target_ids,
                )
            )

        _log.info("Drafted %d mitigation plans with evidence tracing via LLM", len(enriched_mitigations))
        return enriched_mitigations
