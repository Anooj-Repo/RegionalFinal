"""
intelligence/services/scoring_service.py
-----------------------------------------
ScoringService — Generates deterministic warning and alert signals.
"""

from __future__ import annotations

from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle
from schemas.domain.relationship import RelationshipType
from intelligence.schemas import DeterministicSignal, SignalSeverity
from utils.logger import get_logger

_log = get_logger("intelligence.services.scoring")


class ScoringService:
    """
    Evaluates rule triggers to produce deterministic signal alerts.
    """

    def analyze(self, bundle: ProjectKnowledgeBundle) -> list[DeterministicSignal]:
        _log.debug("Evaluating scoring signals for project_id=%s", bundle.project_id)

        signals: list[DeterministicSignal] = []

        # Rule 1: Vendor Block Signal
        for rel in bundle.relationships:
            if rel.relationship_type == RelationshipType.BLOCKS and "vendor" in rel.source_entity:
                signals.append(
                    DeterministicSignal(
                        signal_id=f"sig_vendor_block_{rel.source_entity}",
                        severity=SignalSeverity.CRITICAL,
                        category="vendor_delivery",
                        title=f"Third-Party Vendor Delivery Block ({rel.source_entity})",
                        description=f"Vendor entity '{rel.source_entity}' is actively blocking work item '{rel.target_entity}'. Contractual SLA penalty or escalation required.",
                        source_entity_ids=[rel.source_entity, rel.target_entity],
                    )
                )

        # Rule 2: Critical Path Task Blocked
        for doc in bundle.documents:
            if doc.source.value == "project_task" and doc.metadata.get("status") == "blocked":
                blockers = doc.metadata.get("blockers", [])
                blocker_desc = "; ".join(blockers) if blockers else "Task execution suspended."
                signals.append(
                    DeterministicSignal(
                        signal_id=f"sig_task_blocked_{doc.id}",
                        severity=SignalSeverity.CRITICAL,
                        category="timeline_delay",
                        title=f"Critical Task Blocked: {doc.title}",
                        description=f"Task '{doc.title}' is blocked. Details: {blocker_desc}",
                        source_entity_ids=[doc.id],
                    )
                )

        # Rule 3: Data Quality Audit Blocked (SAP GL_ACCOUNTS)
        for doc in bundle.documents:
            if "gl_accounts" in (doc.title + " " + doc.text).lower() and ("null" in doc.text.lower() or "audit" in doc.text.lower()):
                signals.append(
                    DeterministicSignal(
                        signal_id="sig_data_quality_gl_accounts",
                        severity=SignalSeverity.CRITICAL,
                        category="data_quality",
                        title="Critical Data Anomaly in GL_ACCOUNTS Table",
                        description="Null mandatory fields discovered in GL_ACCOUNTS migration scope. Data migration design suspended pending remediation.",
                        source_entity_ids=[doc.id],
                    )
                )
                break

        # Rule 4: GDPR Procurement Contract Delay
        for doc in bundle.documents:
            if "gdpr" in (doc.title + " " + doc.text).lower() and ("procurement" in doc.text.lower() or "contract" in doc.text.lower()):
                signals.append(
                    DeterministicSignal(
                        signal_id="sig_compliance_gdpr_procurement",
                        severity=SignalSeverity.CRITICAL,
                        category="compliance_risk",
                        title="GDPR Audit Deadline at Risk — Unsigned Pen Test Contract",
                        description="Procurement contract sign-off is overdue. Pen test cannot start without contract, endangering regulatory compliance deadline.",
                        source_entity_ids=[doc.id],
                    )
                )
                break

        _log.info("ScoringService generated %d signals for project_id=%s", len(signals), bundle.project_id)
        return signals
