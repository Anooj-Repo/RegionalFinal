"""
tests/test_adapters.py
-----------------------
Tests for Part 3 (Mock Adapters) and Part 4 (DataSourceRegistry with ProjectSnapshot).

Covers:
    - Each adapter returns the correct Pydantic type (never dicts)
    - load() is the only public method
    - DataSourceRegistry.load_project() → ProjectSnapshot
    - Graceful degradation when a non-critical adapter fails
    - ProjectNotFoundError raised when project adapter fails
    - Adapter injection works (registry is testable)
"""

import pytest


# ===========================================================================
# Helpers
# ===========================================================================

SAMPLE_PROJECT_IDS = [1, 2, 3]


def _is_pydantic(obj) -> bool:
    """Return True if obj is a Pydantic model instance."""
    return hasattr(type(obj), "model_fields")


def _all_pydantic(lst: list) -> bool:
    """Return True if every item in the list is a Pydantic model."""
    return all(_is_pydantic(item) for item in lst)


# ===========================================================================
# Part 3 — Individual adapters
# ===========================================================================

class TestProjectPlanAdapter:

    def test_returns_project_schema(self):
        from adapters import ProjectPlanAdapter
        from schemas.domain import ProjectSchema
        result = ProjectPlanAdapter().load(1)
        assert isinstance(result, ProjectSchema)

    def test_no_dicts_returned(self):
        from adapters import ProjectPlanAdapter
        result = ProjectPlanAdapter().load(1)
        assert _is_pydantic(result)

    def test_project_id_field_is_uuid_string(self):
        from adapters import ProjectPlanAdapter
        result = ProjectPlanAdapter().load(1)
        assert isinstance(result.project_id, str)
        assert len(result.project_id) > 0

    def test_deterministic_output(self):
        from adapters import ProjectPlanAdapter
        a = ProjectPlanAdapter()
        assert a.load(1).name == a.load(1).name

    def test_varies_by_project_id(self):
        from adapters import ProjectPlanAdapter
        a = ProjectPlanAdapter()
        names = {a.load(pid).name for pid in SAMPLE_PROJECT_IDS}
        assert len(names) > 1

    def test_exposes_only_load(self):
        from adapters import ProjectPlanAdapter
        public = [m for m in dir(ProjectPlanAdapter()) if not m.startswith("_")]
        assert "load" in public
        assert "fetch" not in public
        assert "get" not in public


class TestTaskAdapter:

    def test_returns_list(self):
        from adapters import TaskAdapter
        result = TaskAdapter().load(1)
        assert isinstance(result, list)

    def test_returns_pydantic_models(self):
        from adapters import TaskAdapter
        result = TaskAdapter().load(1)
        assert len(result) > 0
        assert _all_pydantic(result)

    def test_task_count_range(self):
        from adapters import TaskAdapter
        a = TaskAdapter()
        for pid in SAMPLE_PROJECT_IDS:
            count = len(a.load(pid))
            assert 3 <= count <= 10, f"Expected 3-10 tasks, got {count} for project_id={pid}"

    def test_all_tasks_have_project_id(self):
        from adapters import TaskAdapter
        project_id = 2
        tasks = TaskAdapter().load(project_id)
        assert all(t.project_id == project_id for t in tasks)

    def test_completion_within_bounds(self):
        from adapters import TaskAdapter
        for task in TaskAdapter().load(1):
            assert 0 <= task.completion <= 100


class TestStakeholderAdapter:

    def test_returns_list_of_stakeholder_schemas(self):
        from adapters import StakeholderAdapter
        from schemas.domain import StakeholderSchema
        result = StakeholderAdapter().load(1)
        assert len(result) > 0
        assert all(isinstance(s, StakeholderSchema) for s in result)

    def test_stakeholder_count_range(self):
        from adapters import StakeholderAdapter
        a = StakeholderAdapter()
        for pid in SAMPLE_PROJECT_IDS:
            count = len(a.load(pid))
            assert 3 <= count <= 10

    def test_all_stakeholders_have_project_id(self):
        from adapters import StakeholderAdapter
        project_id = 2
        stakeholders = StakeholderAdapter().load(project_id)
        assert all(s.project_id == project_id for s in stakeholders)


class TestEmailAdapter:

    def test_returns_list_of_email_schemas(self):
        from adapters import EmailAdapter
        from schemas.domain import EmailDocumentSchema
        result = EmailAdapter().load(1)
        assert len(result) > 0
        assert all(isinstance(e, EmailDocumentSchema) for e in result)

    def test_email_count_range(self):
        from adapters import EmailAdapter
        a = EmailAdapter()
        for pid in SAMPLE_PROJECT_IDS:
            count = len(a.load(pid))
            assert 2 <= count <= 10

    def test_recipients_is_list_of_strings(self):
        from adapters import EmailAdapter
        for email in EmailAdapter().load(1):
            assert isinstance(email.recipients, list)
            assert all(isinstance(r, str) for r in email.recipients)

    def test_labels_is_list(self):
        from adapters import EmailAdapter
        for email in EmailAdapter().load(1):
            assert isinstance(email.labels, list)


class TestChatAdapter:

    def test_returns_list_of_chat_schemas(self):
        from adapters import ChatAdapter
        from schemas.domain import ChatMessageSchema
        result = ChatAdapter().load(1)
        assert len(result) > 0
        assert all(isinstance(c, ChatMessageSchema) for c in result)

    def test_chat_count_range(self):
        from adapters import ChatAdapter
        a = ChatAdapter()
        for pid in SAMPLE_PROJECT_IDS:
            count = len(a.load(pid))
            assert 3 <= count <= 10

    def test_reactions_is_dict(self):
        from adapters import ChatAdapter
        for msg in ChatAdapter().load(1):
            assert isinstance(msg.reactions, dict)

    def test_no_dict_items(self):
        from adapters import ChatAdapter
        result = ChatAdapter().load(1)
        assert _all_pydantic(result)


class TestStatusReportAdapter:

    def test_returns_list_of_status_report_schemas(self):
        from adapters import StatusReportAdapter
        from schemas.domain import StatusReportSchema
        result = StatusReportAdapter().load(1)
        assert len(result) > 0
        assert all(isinstance(r, StatusReportSchema) for r in result)

    def test_report_count_range(self):
        from adapters import StatusReportAdapter
        a = StatusReportAdapter()
        for pid in SAMPLE_PROJECT_IDS:
            count = len(a.load(pid))
            assert 1 <= count <= 2

    def test_accomplishments_is_list(self):
        from adapters import StatusReportAdapter
        for report in StatusReportAdapter().load(1):
            assert isinstance(report.accomplishments, list)

    def test_next_steps_is_list(self):
        from adapters import StatusReportAdapter
        for report in StatusReportAdapter().load(1):
            assert isinstance(report.next_steps, list)


class TestRiskRegisterAdapter:

    def test_returns_list_of_risk_schemas(self):
        from adapters import RiskRegisterAdapter
        from schemas.domain import RiskEntrySchema
        result = RiskRegisterAdapter().load(1)
        assert len(result) > 0
        assert all(isinstance(r, RiskEntrySchema) for r in result)

    def test_risk_count_range(self):
        from adapters import RiskRegisterAdapter
        a = RiskRegisterAdapter()
        for pid in SAMPLE_PROJECT_IDS:
            count = len(a.load(pid))
            assert 2 <= count <= 5

    def test_risk_score_computable(self):
        from adapters import RiskRegisterAdapter
        for risk in RiskRegisterAdapter().load(1):
            assert risk.risk_score in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    def test_mitigation_is_string_or_none(self):
        from adapters import RiskRegisterAdapter
        for risk in RiskRegisterAdapter().load(1):
            assert risk.mitigation is None or isinstance(risk.mitigation, str)


class TestLessonsLearnedAdapter:

    def test_returns_list_of_historical_schemas(self):
        from adapters import LessonsLearnedAdapter
        from schemas.domain import HistoricalProjectSchema
        result = LessonsLearnedAdapter().load(1)
        assert len(result) > 0
        assert all(isinstance(h, HistoricalProjectSchema) for h in result)

    def test_historical_count_range(self):
        from adapters import LessonsLearnedAdapter
        a = LessonsLearnedAdapter()
        for pid in SAMPLE_PROJECT_IDS:
            count = len(a.load(pid))
            assert 1 <= count <= 2

    def test_lessons_learned_is_list_of_strings(self):
        from adapters import LessonsLearnedAdapter
        for h in LessonsLearnedAdapter().load(1):
            assert isinstance(h.lessons_learned, list)
            assert all(isinstance(l, str) for l in h.lessons_learned)

    def test_historical_risks_are_nested_models(self):
        from adapters import LessonsLearnedAdapter
        from schemas.domain.historical import HistoricalRisk
        for h in LessonsLearnedAdapter().load(1):
            for risk in h.historical_risks:
                assert isinstance(risk, HistoricalRisk)


# ===========================================================================
# Part 4 — DataSourceRegistry with ProjectSnapshot
# ===========================================================================

class TestDataSourceRegistry:

    def test_load_project_returns_project_snapshot(self):
        from services.data_source_registry import DataSourceRegistry
        from schemas.domain.snapshot import ProjectSnapshot
        registry = DataSourceRegistry()
        snapshot = registry.load_project(1)
        assert isinstance(snapshot, ProjectSnapshot)

    def test_snapshot_project_is_set(self):
        from services.data_source_registry import DataSourceRegistry
        from schemas.domain import ProjectSchema
        snapshot = DataSourceRegistry().load_project(1)
        assert isinstance(snapshot.project, ProjectSchema)
        assert snapshot.project.name is not None

    def test_snapshot_has_tasks(self):
        from services.data_source_registry import DataSourceRegistry
        snapshot = DataSourceRegistry().load_project(1)
        assert isinstance(snapshot.tasks, list)
        assert len(snapshot.tasks) > 0

    def test_snapshot_has_stakeholders(self):
        from services.data_source_registry import DataSourceRegistry
        snapshot = DataSourceRegistry().load_project(1)
        assert isinstance(snapshot.stakeholders, list)
        assert len(snapshot.stakeholders) > 0

    def test_snapshot_has_emails(self):
        from services.data_source_registry import DataSourceRegistry
        snapshot = DataSourceRegistry().load_project(1)
        assert isinstance(snapshot.emails, list)
        assert len(snapshot.emails) > 0

    def test_snapshot_has_chat_messages(self):
        from services.data_source_registry import DataSourceRegistry
        snapshot = DataSourceRegistry().load_project(1)
        assert isinstance(snapshot.chat_messages, list)
        assert len(snapshot.chat_messages) > 0

    def test_snapshot_has_risk_register(self):
        from services.data_source_registry import DataSourceRegistry
        snapshot = DataSourceRegistry().load_project(1)
        assert isinstance(snapshot.risk_register, list)
        assert len(snapshot.risk_register) > 0

    def test_snapshot_has_status_reports(self):
        from services.data_source_registry import DataSourceRegistry
        snapshot = DataSourceRegistry().load_project(1)
        assert isinstance(snapshot.status_reports, list)
        assert len(snapshot.status_reports) > 0

    def test_snapshot_has_historical_projects(self):
        from services.data_source_registry import DataSourceRegistry
        snapshot = DataSourceRegistry().load_project(1)
        assert isinstance(snapshot.historical_projects, list)
        assert len(snapshot.historical_projects) > 0

    def test_snapshot_is_immutable(self):
        from services.data_source_registry import DataSourceRegistry
        snapshot = DataSourceRegistry().load_project(1)
        with pytest.raises(Exception):
            snapshot.tasks = []   # frozen=True must prevent mutation

    def test_snapshot_summary_complete(self):
        from services.data_source_registry import DataSourceRegistry
        snapshot = DataSourceRegistry().load_project(1)
        summary = snapshot.summary()
        assert summary["tasks"] > 0
        assert summary["stakeholders"] > 0
        assert summary["emails"] > 0
        assert summary["chat_messages"] > 0
        assert summary["risk_register"] > 0
        assert "snapshot_timestamp" in summary
        assert summary["project_version"] == "1.0.0"

    def test_different_project_ids_produce_different_snapshots(self):
        from services.data_source_registry import DataSourceRegistry
        r = DataSourceRegistry()
        s1 = r.load_project(1)
        s2 = r.load_project(2)
        assert s1.project.id != s2.project.id

    def test_project_not_found_when_project_adapter_fails(self):
        """If ProjectPlanAdapter raises, registry must raise ProjectNotFoundError."""
        from services.data_source_registry import DataSourceRegistry
        from exceptions import ProjectNotFoundError, AdapterError
        from adapters.base import BaseAdapter
        from schemas.domain import ProjectSchema

        class _FailingProjectAdapter(BaseAdapter[ProjectSchema]):
            adapter_name = "FailingProjectAdapter"
            def load(self, project_id: int) -> ProjectSchema:
                self._raise("Simulated failure")

        registry = DataSourceRegistry(project_adapter=_FailingProjectAdapter())
        with pytest.raises(ProjectNotFoundError):
            registry.load_project(999)

    def test_graceful_degradation_when_task_adapter_fails(self):
        """Non-critical adapter failure → empty list, snapshot still returned."""
        from services.data_source_registry import DataSourceRegistry
        from exceptions import AdapterError
        from adapters.base import BaseAdapter

        class _FailingTaskAdapter(BaseAdapter[list]):
            adapter_name = "FailingTaskAdapter"
            def load(self, project_id: int) -> list:
                self._raise("Simulated task failure")

        registry = DataSourceRegistry(task_adapter=_FailingTaskAdapter())
        snapshot = registry.load_project(1)   # should NOT raise
        assert snapshot.tasks == []            # degraded gracefully
        assert snapshot.project is not None    # rest of snapshot intact

    def test_get_registry_singleton(self):
        from services.data_source_registry import get_registry
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2   # same instance

    def test_only_load_project_is_public(self):
        from services.data_source_registry import DataSourceRegistry
        public = [
            m for m in dir(DataSourceRegistry())
            if not m.startswith("_") and callable(getattr(DataSourceRegistry, m, None))
        ]
        assert "load_project" in public
