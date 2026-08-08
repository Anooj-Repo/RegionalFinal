"""
tests/test_graph2_evidence_trace.py
------------------------------------
Unit and integration tests for Evidence Trace & Provenance System in Graph 2.
"""

import pytest
from workflow.workflow_service import WorkflowService
from intelligence.engine import get_intelligence_engine
from services import EvidenceCollectorService, ReflectionService, RiskReportBuilderService
from tests.test_graph2_services import MockLLMService
from schemas.domain import (
    DocumentSource,
    EvidenceReference,
    EvidencePackage,
    EvidenceTrace,
    CategorizedRisk,
    MitigationPlan,
    RiskAssessmentReport,
)


@pytest.fixture
def mock_llm():
    return MockLLMService()


@pytest.fixture
def intelligence_alpha():
    bundle = WorkflowService().run_graph1(1)
    return get_intelligence_engine().analyze(bundle)


class TestEvidenceTraceModels:

    def test_evidence_reference_fields(self):
        ref = EvidenceReference(
            document_id="doc_email_1001",
            chunk_id="chunk_42",
            source=DocumentSource.EMAIL,
            similarity_score=0.95,
        )
        assert ref.document_id == "doc_email_1001"
        assert ref.chunk_id == "chunk_42"
        assert ref.source == DocumentSource.EMAIL
        assert ref.similarity_score == 0.95
        assert ref.evidence_id == "ref_doc_email_1001_chunk_42"

    def test_evidence_package_assembly(self, intelligence_alpha):
        service = EvidenceCollectorService()
        package = service.collect_evidence_package(intelligence_alpha)
        assert isinstance(package, EvidencePackage)
        assert len(package.retrieved_documents) > 0
        assert all(isinstance(r, EvidenceReference) for r in package.retrieved_documents)
        assert len(package.entity_references) > 0

    def test_evidence_trace_mapping(self, intelligence_alpha):
        ref = EvidenceReference(
            document_id="doc_chat_1",
            chunk_id="chunk_1",
            source=DocumentSource.CHAT,
            similarity_score=0.9,
        )
        trace = EvidenceTrace(
            risk_id="risk_101",
            supporting_evidence=[ref],
        )
        assert trace.risk_id == "risk_101"
        assert len(trace.supporting_evidence) == 1
        assert trace.supporting_evidence[0].source == DocumentSource.CHAT

    def test_reflection_audits_missing_evidence(self, mock_llm):
        service = ReflectionService(llm_service=mock_llm)
        risk_without_evidence = CategorizedRisk(
            risk_id="risk_bad_1",
            category="vendor",
            title="Unsupported Risk",
            description="No evidence provided",
            probability="high",
            impact="critical",
            supporting_evidence_ids=[],  # Empty!
        )
        feedback = service.reflect(
            context_summary="Test summary",
            risks=[risk_without_evidence],
            mitigations=[],
            retry_count=0,
            evidence_package=EvidencePackage(),
        )
        assert feedback.passed is False
        assert any("lacks supporting evidence IDs" in c for c in feedback.unsupported_claims)

    def test_report_contains_evidence_traces(self, intelligence_alpha, mock_llm):
        collector = EvidenceCollectorService()
        pkg = collector.collect_evidence_package(intelligence_alpha)

        risk = CategorizedRisk(
            risk_id="risk_alpha_1",
            category="vendor_delivery",
            title="CloudSphere Vendor Delay",
            description="Missed API gateway deadline.",
            probability="high",
            impact="critical",
            supporting_evidence_ids=[pkg.retrieved_documents[0].evidence_id],
        )

        mitigation = MitigationPlan(
            mitigation_id="mit_alpha_1",
            target_risk_id="risk_alpha_1",
            action_title="Invoke Penalty",
            action_description="SLA penalty enforcement.",
            supporting_evidence_ids=[pkg.retrieved_documents[0].evidence_id],
        )

        builder = RiskReportBuilderService(llm_service=mock_llm)
        report = builder.build_report(
            intelligence_alpha,
            "Context summary",
            [risk],
            pkg,
            [mitigation],
            None,
            evidence_package=pkg,
        )

        assert isinstance(report, RiskAssessmentReport)
        assert len(report.evidence_traces) == 1
        assert report.evidence_traces[0].risk_id == "risk_alpha_1"
        assert len(report.evidence_traces[0].supporting_evidence) > 0
