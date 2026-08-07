"""
tests/test_snapshot.py
-----------------------
Tests for ProjectSnapshot — the canonical enterprise domain snapshot passed into Graph 1.
"""

import pytest
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers — minimal valid schema instances
# ---------------------------------------------------------------------------

def _make_project():
    from schemas.domain import ProjectSchema, ProjectStatus
    return ProjectSchema(
        id=1,
        project_id="PROG-TEST-2026",
        name="Alpha Programme",
        status=ProjectStatus.ACTIVE,
        sponsor="Sarah Mitchell",
        program_manager="James Okonkwo",
    )

def _make_task(task_id: int = 1, blocked: bool = False):
    from schemas.domain import ProjectTaskSchema, TaskPriority, TaskStatus
    return ProjectTaskSchema(
        id=task_id,
        project_id=1,
        title=f"Task {task_id}",
        priority=TaskPriority.HIGH,
        status=TaskStatus.BLOCKED if blocked else TaskStatus.OPEN,
        completion=0,
    )

def _make_stakeholder(stakeholder_id: int = 1):
    from schemas.domain import StakeholderSchema, CommunicationPreference
    return StakeholderSchema(
        id=stakeholder_id,
        project_id=1,
        name="Sarah Mitchell",
        role="Sponsor",
        department="Executive",
        communication_preference=CommunicationPreference.EMAIL,
    )

def _make_risk(risk_id: int = 1, open_: bool = True):
    from schemas.domain import RiskEntrySchema, RiskProbability, RiskImpact, RiskStatus
    return RiskEntrySchema(
        id=risk_id,
        project_id=1,
        title=f"Risk {risk_id}",
        probability=RiskProbability.HIGH,
        impact=RiskImpact.CRITICAL,
        status=RiskStatus.OPEN if open_ else RiskStatus.MITIGATED,
    )

def _make_email(email_id: int = 1):
    from schemas.domain import EmailDocumentSchema
    return EmailDocumentSchema(
        id=email_id, project_id=1,
        sender="alice@corp.com", recipients=["bob@corp.com"],
        subject="Weekly update",
    )

def _make_chat(chat_id: int = 1):
    from schemas.domain import ChatMessageSchema
    return ChatMessageSchema(
        id=chat_id, project_id=1,
        sender="alice", message="Let's sync tomorrow.",
    )

def _make_meeting(meeting_id: int = 1):
    from schemas.domain import MeetingNoteSchema
    return MeetingNoteSchema(
        id=meeting_id, project_id=1,
        meeting_title="Sprint Review",
        attendees=["Alice", "Bob"],
    )

def _make_report(report_id: int = 1):
    from schemas.domain import StatusReportSchema
    return StatusReportSchema(
        id=report_id, project_id=1,
        reporting_period="2026-W32",
        accomplishments=["Launched v1"],
        blockers=[],
    )

def _make_historical(hist_id: int = 1):
    from schemas.domain import HistoricalProjectSchema
    return HistoricalProjectSchema(
        id=hist_id,
        project_name="Legacy ERP",
        lessons_learned=["Test early"],
    )


# ---------------------------------------------------------------------------
# Structure tests
# ---------------------------------------------------------------------------

class TestProjectSnapshotStructure:

    def test_import(self):
        from schemas.domain import ProjectSnapshot
        assert ProjectSnapshot is not None

    def test_requires_project(self):
        from schemas.domain import ProjectSnapshot
        with pytest.raises(Exception):
            ProjectSnapshot()   # missing required project

    def test_minimal_snapshot(self):
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(project=_make_project())
        assert snapshot.project.name == "Alpha Programme"
        assert isinstance(snapshot.snapshot_timestamp, datetime)
        assert snapshot.project_version == "1.0.0"

    def test_all_fields_optional_except_project(self):
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(project=_make_project())
        assert snapshot.tasks == []
        assert snapshot.stakeholders == []
        assert snapshot.emails == []
        assert snapshot.chat_messages == []
        assert snapshot.meeting_notes == []
        assert snapshot.status_reports == []
        assert snapshot.risk_register == []
        assert snapshot.historical_projects == []

    def test_full_snapshot(self):
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(
            project=_make_project(),
            tasks=[_make_task(1), _make_task(2)],
            stakeholders=[_make_stakeholder(1)],
            emails=[_make_email(1), _make_email(2)],
            chat_messages=[_make_chat()],
            meeting_notes=[_make_meeting()],
            status_reports=[_make_report()],
            risk_register=[_make_risk(1), _make_risk(2)],
            historical_projects=[_make_historical()],
            project_version="2.1.0",
        )
        assert len(snapshot.tasks) == 2
        assert len(snapshot.stakeholders) == 1
        assert len(snapshot.emails) == 2
        assert len(snapshot.chat_messages) == 1
        assert len(snapshot.risk_register) == 2
        assert len(snapshot.historical_projects) == 1
        assert snapshot.project_version == "2.1.0"


# ---------------------------------------------------------------------------
# Immutability test
# ---------------------------------------------------------------------------

class TestProjectSnapshotImmutability:

    def test_is_frozen(self):
        """ProjectSnapshot must be immutable — workflows cannot mutate snapshot state."""
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(project=_make_project())
        with pytest.raises(Exception):
            snapshot.tasks = []    # frozen model → should raise


# ---------------------------------------------------------------------------
# Convenience property tests
# ---------------------------------------------------------------------------

class TestProjectSnapshotProperties:

    def test_is_empty_true(self):
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(project=_make_project())
        assert snapshot.is_empty is True

    def test_is_empty_false(self):
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(project=_make_project(), tasks=[_make_task()])
        assert snapshot.is_empty is False

    def test_open_risks_filter(self):
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(
            project=_make_project(),
            risk_register=[
                _make_risk(1, open_=True),
                _make_risk(2, open_=False),   # mitigated
                _make_risk(3, open_=True),
            ],
        )
        assert len(snapshot.open_risks) == 2

    def test_blocked_tasks_filter(self):
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(
            project=_make_project(),
            tasks=[
                _make_task(1, blocked=False),
                _make_task(2, blocked=True),
                _make_task(3, blocked=True),
            ],
        )
        assert len(snapshot.blocked_tasks) == 2

    def test_total_documents(self):
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(
            project=_make_project(),
            emails=[_make_email(1), _make_email(2)],
            chat_messages=[_make_chat()],
            meeting_notes=[_make_meeting()],
        )
        assert snapshot.total_documents == 4   # 2 emails + 1 chat + 1 meeting

    def test_snapshot_id_uuid(self):
        from uuid import UUID
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(project=_make_project())
        assert isinstance(snapshot.snapshot_id, UUID)

    def test_summary_keys(self):
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(
            project=_make_project(),
            tasks=[_make_task()],
            risk_register=[_make_risk()],
        )
        s = snapshot.summary()
        expected_keys = {
            "snapshot_id", "project_id", "project_name", "tasks", "stakeholders", "emails",
            "chat_messages", "meeting_notes", "status_reports", "risk_register",
            "open_risks", "blocked_tasks", "historical_projects", "total_documents",
            "snapshot_timestamp", "project_version",
        }
        assert expected_keys == set(s.keys())

    def test_summary_counts_correct(self):
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(
            project=_make_project(),
            tasks=[_make_task(1), _make_task(2, blocked=True)],
            stakeholders=[_make_stakeholder()],
            emails=[_make_email()],
            risk_register=[_make_risk(1), _make_risk(2, open_=False)],
        )
        s = snapshot.summary()
        assert s["tasks"]         == 2
        assert s["stakeholders"]  == 1
        assert s["emails"]        == 1
        assert s["open_risks"]    == 1
        assert s["blocked_tasks"] == 1

    def test_summary_project_info(self):
        from schemas.domain import ProjectSnapshot
        snapshot = ProjectSnapshot(project=_make_project())
        s = snapshot.summary()
        assert s["project_name"] == "Alpha Programme"
        assert s["project_id"]   == "PROG-TEST-2026"
