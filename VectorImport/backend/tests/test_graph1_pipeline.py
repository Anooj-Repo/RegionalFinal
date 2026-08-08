"""
tests/test_graph1_pipeline.py
------------------------------
End-to-end integration tests for Graph 1: Knowledge Intelligence Pipeline.
"""

import pytest
from graphs.graph1 import graph1
from services import get_registry
from workflow.workflow_service import WorkflowService
from schemas.domain import ProjectKnowledgeBundle, ProjectSnapshot


class TestGraph1Pipeline:

    def test_graph1_execution_alpha(self):
        snapshot: ProjectSnapshot = get_registry().load_project(1)
        initial_state = {"snapshot": snapshot}

        final_state = graph1.invoke(initial_state)

        assert "knowledge_bundle" in final_state
        bundle: ProjectKnowledgeBundle = final_state["knowledge_bundle"]
        assert isinstance(bundle, ProjectKnowledgeBundle)
        assert bundle.project_id == "PROG-ALPHA-2026"
        assert len(bundle.documents) > 0
        assert len(bundle.entities) > 0
        assert len(bundle.relationships) > 0
        assert bundle.retrieval_reference.startswith("faiss://")

        # Summary check
        summary = bundle.summary()
        assert summary["documents"] > 0
        assert summary["entities"] > 0
        assert summary["relationships"] > 0

    def test_graph1_execution_beta(self):
        snapshot: ProjectSnapshot = get_registry().load_project(2)
        initial_state = {"snapshot": snapshot}

        final_state = graph1.invoke(initial_state)

        bundle: ProjectKnowledgeBundle = final_state["knowledge_bundle"]
        assert bundle.project_id == "PROG-BETA-2026"
        assert len(bundle.documents) > 0
        assert len(bundle.entities) > 0

    def test_graph1_execution_gamma(self):
        snapshot: ProjectSnapshot = get_registry().load_project(3)
        initial_state = {"snapshot": snapshot}

        final_state = graph1.invoke(initial_state)

        bundle: ProjectKnowledgeBundle = final_state["knowledge_bundle"]
        assert bundle.project_id == "PROG-GAMMA-2026"
        assert len(bundle.documents) > 0
        assert len(bundle.entities) > 0

    def test_workflow_service_run_graph1(self):
        service = WorkflowService()
        bundle = service.run_graph1(1)
        assert isinstance(bundle, ProjectKnowledgeBundle)
        assert bundle.project_id == "PROG-ALPHA-2026"
        assert bundle.retrieval_reference.startswith("faiss://")
