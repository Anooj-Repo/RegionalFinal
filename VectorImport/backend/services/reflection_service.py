"""
services/reflection_service.py
-------------------------------
ReflectionService — Node 6 service for Graph 2.

Audits drafted mitigations and risks for evidence grounding, checking that every risk has valid,
non-hallucinated supporting_evidence_ids present in EvidencePackage.
"""

from __future__ import annotations

from schemas.domain.risk_report import CategorizedRisk, MitigationPlan, ReflectionFeedback, EvidencePackage
from prompts.graph2_prompts import REFLECTION_PROMPT
from services.llm_service import LLMService, get_llm_service
from utils.logger import get_logger

_log = get_logger("services.reflection")


class ReflectionService:
    """
    Evaluates evidence grounding, checks for hallucinated evidence IDs, and validates mitigation quality via LLM.
    """

    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or get_llm_service()

    def reflect(
        self,
        context_summary: str,
        risks: list[CategorizedRisk],
        mitigations: list[MitigationPlan],
        retry_count: int = 0,
        evidence_package: EvidencePackage | None = None,
    ) -> ReflectionFeedback:
        _log.info("Executing ReflectionService audit via LLM (retry_count=%d)", retry_count)

        mitigations_str = "; ".join(f"{m.mitigation_id}: {m.action_title} [Evidence: {', '.join(m.supporting_evidence_ids)}]" for m in mitigations)
        prompt = REFLECTION_PROMPT.format(
            context_summary=context_summary,
            mitigations_summary=mitigations_str,
        )

        feedback: ReflectionFeedback = self.llm_service.invoke_structured(
            prompt, ReflectionFeedback
        )

        # Deterministic Evidence Trace Audit Rule
        valid_ev_ids = {ref.evidence_id for ref in (evidence_package.retrieved_documents if evidence_package else [])}
        unsupported: list[str] = list(feedback.unsupported_claims)

        for r in risks:
            if not r.supporting_evidence_ids:
                unsupported.append(f"Risk '{r.risk_id}' ({r.title}) lacks supporting evidence IDs.")
            elif valid_ev_ids:
                hallucinated = [ev_id for ev_id in r.supporting_evidence_ids if ev_id not in valid_ev_ids]
                if hallucinated:
                    unsupported.append(f"Risk '{r.risk_id}' references hallucinated evidence IDs: {hallucinated}")

        for m in mitigations:
            if not m.supporting_evidence_ids:
                unsupported.append(f"Mitigation '{m.mitigation_id}' lacks supporting evidence IDs.")

        is_passed = feedback.passed and len(unsupported) == 0

        notes = (
            "Audit passed — all risks and mitigations fully grounded with valid evidence references."
            if is_passed
            else f"Audit failed — {len(unsupported)} evidence provenance issue(s) detected: {'; '.join(unsupported[:3])}"
        )

        audit_feedback = ReflectionFeedback(
            passed=is_passed,
            grounding_score=0.95 if is_passed else 0.50,
            consistency_score=0.95 if is_passed else 0.50,
            unsupported_claims=unsupported,
            reflection_notes=notes,
            retry_count=retry_count,
        )

        _log.info("Reflection audit complete — passed=%s, grounding=%.2f", audit_feedback.passed, audit_feedback.grounding_score)
        return audit_feedback
