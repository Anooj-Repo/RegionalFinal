"""
graphs/graph2/nodes.py
----------------------
Nodes for Graph 2: Decision Intelligence & Risk Assessment Pipeline with Evidence Trace System.

Thin orchestration wrappers delegating logic to modular services.
"""

from __future__ import annotations

from typing import Any
from graphs.graph2.state import Graph2State
from services import (
    ContextBuilderService,
    EvidenceCollectorService,
    DecisionPlanningService,
    RiskAssessmentService,
    MitigationPlanningService,
    ReflectionService,
    RiskReportBuilderService,
)
from utils.logger import get_logger

_log = get_logger("graphs.graph2.nodes")


def context_builder_node(state: Graph2State) -> dict[str, Any]:
    """Node 1: Synthesize ProjectIntelligence into context summary via LLM."""
    _log.info("[Node 1] Running ContextBuilderNode")
    intel = state["intelligence"]
    llm_svc = state.get("llm_service")
    service = ContextBuilderService(llm_service=llm_svc)
    summary = service.build_context(intel)
    return {"context_summary": summary}


def evidence_collector_node(state: Graph2State) -> dict[str, Any]:
    """Node 2: Retrieve grounding evidence and build EvidencePackage."""
    _log.info("[Node 2] Running EvidenceCollectorNode (RAG EvidencePackage)")
    intel = state["intelligence"]
    service = EvidenceCollectorService()
    pkg = service.collect_evidence_package(intel)
    legacy_evidence = service.collect_evidence(intel)
    return {
        "evidence_package": pkg,
        "retrieved_evidence": legacy_evidence,
    }


def decision_planner_node(state: Graph2State) -> dict[str, Any]:
    """Node 3: Formulate strategic decision priorities via LLM."""
    _log.info("[Node 3] Running DecisionPlannerNode")
    intel = state["intelligence"]
    summary = state.get("context_summary", "")
    pkg = state.get("evidence_package") or state.get("retrieved_evidence", [])
    llm_svc = state.get("llm_service")
    service = DecisionPlanningService(llm_service=llm_svc)
    plan = service.plan_decisions(intel, summary, pkg)
    return {"decision_plan": plan}


def risk_assessment_node(state: Graph2State) -> dict[str, Any]:
    """Node 4: Categorize and score project risks with evidence ID mapping via LLM."""
    _log.info("[Node 4] Running RiskAssessmentNode")
    intel = state["intelligence"]
    pkg = state.get("evidence_package")
    llm_svc = state.get("llm_service")
    service = RiskAssessmentService(llm_service=llm_svc)
    risks = service.assess_risks(intel, evidence_package=pkg)
    return {"categorized_risks": risks}


def mitigation_planning_node(state: Graph2State) -> dict[str, Any]:
    """Node 5: Draft actionable mitigation plans with supporting evidence IDs via LLM."""
    _log.info("[Node 5] Running MitigationPlanningNode")
    risks = state.get("categorized_risks", [])
    feedback = state.get("reflection_feedback")
    pkg = state.get("evidence_package")
    llm_svc = state.get("llm_service")
    service = MitigationPlanningService(llm_service=llm_svc)
    mitigations = service.plan_mitigations(risks, feedback, evidence_package=pkg)
    return {"mitigations": mitigations}


def reflection_node(state: Graph2State) -> dict[str, Any]:
    """Node 6: Reflection audit for evidence grounding, consistency, and non-hallucinated evidence references via LLM."""
    _log.info("[Node 6] Running ReflectionNode")
    summary = state.get("context_summary", "")
    risks = state.get("categorized_risks", [])
    mitigations = state.get("mitigations", [])
    retry_cnt = state.get("retry_count", 0)
    pkg = state.get("evidence_package")
    llm_svc = state.get("llm_service")
    service = ReflectionService(llm_service=llm_svc)

    feedback = service.reflect(summary, risks, mitigations, retry_cnt, evidence_package=pkg)
    next_retry = retry_cnt + (0 if feedback.passed else 1)

    return {
        "reflection_feedback": feedback,
        "retry_count": next_retry,
    }


def risk_report_builder_node(state: Graph2State) -> dict[str, Any]:
    """Node 7: Assemble final RiskAssessmentReport with complete EvidenceTraces via LLM."""
    _log.info("[Node 7] Running RiskReportBuilderNode")
    intel = state["intelligence"]
    summary = state.get("context_summary", "")
    risks = state.get("categorized_risks", [])
    evidence = state.get("retrieved_evidence", [])
    mitigations = state.get("mitigations", [])
    feedback = state.get("reflection_feedback")
    pkg = state.get("evidence_package")
    llm_svc = state.get("llm_service")
    service = RiskReportBuilderService(llm_service=llm_svc)

    report = service.build_report(
        intel, summary, risks, evidence, mitigations, feedback, evidence_package=pkg
    )
    return {
        "final_report": report,
        "evidence_traces": report.evidence_traces,
    }
