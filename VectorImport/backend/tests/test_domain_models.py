"""
tests/test_domain_models.py
----------------------------
Structural tests for domain ORM models and Pydantic schemas.

Tests:
    1. All 10 domain tables exist in DB
    2. Column presence for each table
    3. ORM relationships work (insert + FK)
    4. Pydantic schema validation (valid + invalid input)
    5. Enum values
"""

import pytest
from datetime import date, datetime, timezone


# ===========================================================================
# 1 — Table existence
# ===========================================================================

EXPECTED_TABLES = {
    "projects", "project_tasks", "stakeholders",
    "email_documents", "chat_messages", "meeting_notes",
    "status_reports", "risk_entries", "historical_projects",
    "audit_logs",
}

def test_all_domain_tables_exist(db):
    from extensions import db as _db
    existing = set(_db.metadata.tables.keys())
    missing = EXPECTED_TABLES - existing
    assert not missing, f"Missing tables: {missing}"


# ===========================================================================
# 2 — Column checks
# ===========================================================================

class TestTableColumns:

    def _cols(self, table_name, db):
        from extensions import db as _db
        return {c.name for c in _db.metadata.tables[table_name].columns}

    def test_projects_columns(self, db):
        cols = self._cols("projects", db)
        for c in ("id","project_id","name","description","start_date","end_date",
                   "status","sponsor","program_manager","created_at","updated_at"):
            assert c in cols, f"Missing column '{c}' in projects"

    def test_project_tasks_columns(self, db):
        cols = self._cols("project_tasks", db)
        for c in ("id","project_id","title","owner","priority","status",
                   "due_date","completion","dependencies","blockers"):
            assert c in cols

    def test_stakeholders_columns(self, db):
        cols = self._cols("stakeholders", db)
        for c in ("id","project_id","name","role","department","communication_preference"):
            assert c in cols

    def test_email_documents_columns(self, db):
        cols = self._cols("email_documents", db)
        for c in ("id","project_id","sender","recipients","subject",
                   "timestamp","body","attachments","labels"):
            assert c in cols

    def test_chat_messages_columns(self, db):
        cols = self._cols("chat_messages", db)
        for c in ("id","project_id","channel","sender","timestamp",
                   "message","thread_id","reactions"):
            assert c in cols

    def test_meeting_notes_columns(self, db):
        cols = self._cols("meeting_notes", db)
        for c in ("id","project_id","meeting_title","attendees",
                   "decisions","action_items","transcript"):
            assert c in cols

    def test_status_reports_columns(self, db):
        cols = self._cols("status_reports", db)
        for c in ("id","project_id","reporting_period","accomplishments",
                   "blockers","risks","next_steps"):
            assert c in cols

    def test_risk_entries_columns(self, db):
        cols = self._cols("risk_entries", db)
        for c in ("id","project_id","title","probability","impact",
                   "owner","mitigation","status"):
            assert c in cols

    def test_historical_projects_columns(self, db):
        cols = self._cols("historical_projects", db)
        for c in ("id","project_name","lessons_learned",
                   "historical_risks","successful_mitigations"):
            assert c in cols

    def test_audit_logs_no_updated_at(self, db):
        cols = self._cols("audit_logs", db)
        assert "updated_at" not in cols, "audit_logs must be immutable (no updated_at)"


# ===========================================================================
# 3 — ORM insert + relationships
# ===========================================================================

class TestORMInserts:

    def test_create_project(self, db):
        from database.models import Project, ProjectStatus
        p = Project(name="Test Project", status=ProjectStatus.ACTIVE,
                    sponsor="Alice", program_manager="Bob")
        db.session.add(p)
        db.session.commit()
        assert p.id is not None
        assert p.project_id is not None   # UUID auto-generated
        db.session.delete(p)
        db.session.commit()

    def test_create_task_with_project_fk(self, db):
        from database.models import Project, ProjectTask, ProjectStatus, TaskPriority, TaskStatus
        p = Project(name="FK Test Project", status=ProjectStatus.ACTIVE)
        db.session.add(p)
        db.session.commit()

        t = ProjectTask(project_id=p.id, title="Task 1",
                        priority=TaskPriority.HIGH, status=TaskStatus.OPEN,
                        completion=0, dependencies=[], blockers=[])
        db.session.add(t)
        db.session.commit()
        assert t.id is not None
        assert t.project_id == p.id

        db.session.delete(p)   # cascade deletes task
        db.session.commit()

    def test_create_risk_entry(self, db):
        from database.models import Project, RiskEntry, ProjectStatus, RiskProbability, RiskImpact, RiskStatus
        p = Project(name="Risk Project", status=ProjectStatus.ACTIVE)
        db.session.add(p)
        db.session.commit()

        r = RiskEntry(project_id=p.id, title="Data breach",
                      probability=RiskProbability.HIGH,
                      impact=RiskImpact.CRITICAL,
                      status=RiskStatus.OPEN)
        db.session.add(r)
        db.session.commit()
        assert r.id is not None

        db.session.delete(p)
        db.session.commit()

    def test_create_historical_project(self, db):
        from database.models import HistoricalProject
        h = HistoricalProject(
            project_name="Legacy ERP Migration",
            lessons_learned=["Start testing earlier", "Involve users sooner"],
            historical_risks=[{"title": "Data loss", "outcome": "mitigated"}],
            successful_mitigations=["Weekly backups"],
        )
        db.session.add(h)
        db.session.commit()
        assert h.id is not None
        db.session.delete(h)
        db.session.commit()

    def test_meeting_note_json_fields(self, db):
        from database.models import Project, MeetingNote, ProjectStatus
        p = Project(name="Meeting Project", status=ProjectStatus.ACTIVE)
        db.session.add(p)
        db.session.commit()

        m = MeetingNote(
            project_id=p.id,
            meeting_title="Sprint Review",
            attendees=["Alice", "Bob"],
            decisions=["Go live next week"],
            action_items=[{"description": "Deploy", "owner": "Bob"}],
        )
        db.session.add(m)
        db.session.commit()
        assert m.attendees == ["Alice", "Bob"]
        assert m.decisions == ["Go live next week"]

        db.session.delete(p)
        db.session.commit()


# ===========================================================================
# 4 — Pydantic schema validation
# ===========================================================================

class TestPydanticSchemas:

    # Project schemas
    def test_project_create_valid(self):
        from schemas.domain import ProjectCreateSchema, ProjectStatus
        s = ProjectCreateSchema(
            name="Alpha",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            status=ProjectStatus.ACTIVE,
        )
        assert s.name == "Alpha"

    def test_project_create_date_validation(self):
        from schemas.domain import ProjectCreateSchema
        with pytest.raises(Exception):
            ProjectCreateSchema(
                name="Bad",
                start_date=date(2026, 12, 31),
                end_date=date(2026, 1, 1),   # end before start → invalid
            )

    def test_project_create_name_required(self):
        from schemas.domain import ProjectCreateSchema
        with pytest.raises(Exception):
            ProjectCreateSchema()    # missing required 'name'

    # Task schemas
    def test_task_completion_bounds(self):
        from schemas.domain import ProjectTaskCreateSchema
        with pytest.raises(Exception):
            ProjectTaskCreateSchema(project_id=1, title="t", completion=101)  # > 100

    def test_task_defaults(self):
        from schemas.domain import ProjectTaskCreateSchema, TaskPriority, TaskStatus
        t = ProjectTaskCreateSchema(project_id=1, title="Deploy")
        assert t.priority == TaskPriority.MEDIUM
        assert t.status == TaskStatus.OPEN
        assert t.completion == 0
        assert t.dependencies == []
        assert t.blockers == []

    # Risk schemas
    def test_risk_score_critical(self):
        from schemas.domain import RiskEntrySchema, RiskProbability, RiskImpact, RiskStatus
        r = RiskEntrySchema(
            id=1, project_id=1, title="T",
            probability=RiskProbability.HIGH,
            impact=RiskImpact.CRITICAL,
            status=RiskStatus.OPEN,
        )
        assert r.risk_score == "CRITICAL"

    def test_risk_score_low(self):
        from schemas.domain import RiskEntrySchema, RiskProbability, RiskImpact, RiskStatus
        r = RiskEntrySchema(
            id=1, project_id=1, title="T",
            probability=RiskProbability.LOW,
            impact=RiskImpact.LOW,
            status=RiskStatus.OPEN,
        )
        assert r.risk_score == "LOW"

    # Status report
    def test_status_report_has_blockers(self):
        from schemas.domain import StatusReportSchema
        s = StatusReportSchema(id=1, project_id=1,
                               reporting_period="2026-W32",
                               blockers=["Server down"])
        assert s.has_blockers is True

    def test_status_report_no_blockers(self):
        from schemas.domain import StatusReportSchema
        s = StatusReportSchema(id=1, project_id=1,
                               reporting_period="2026-W32")
        assert s.has_blockers is False

    # Historical project
    def test_historical_project_counts(self):
        from schemas.domain import HistoricalProjectSchema, HistoricalRisk
        h = HistoricalProjectSchema(
            id=1,
            project_name="Legacy",
            lessons_learned=["L1", "L2"],
            historical_risks=[
                HistoricalRisk(title="R1", probability="high", impact="critical")
            ],
        )
        assert h.lesson_count == 2
        assert h.risk_count == 1

    # Communications
    def test_email_document_create(self):
        from schemas.domain import EmailDocumentCreateSchema
        e = EmailDocumentCreateSchema(
            project_id=1,
            sender="alice@example.com",
            recipients=["bob@example.com"],
            subject="Status update",
            labels=["important"],
        )
        assert e.labels == ["important"]

    def test_chat_message_reactions(self):
        from schemas.domain import ChatMessageCreateSchema
        c = ChatMessageCreateSchema(
            project_id=1,
            sender="alice",
            reactions={"👍": 3, "🎉": 1},
        )
        assert c.reactions["👍"] == 3

    def test_meeting_note_action_items(self):
        from schemas.domain import MeetingNoteCreateSchema, MeetingActionItem
        m = MeetingNoteCreateSchema(
            project_id=1,
            meeting_title="Kickoff",
            attendees=["Alice", "Bob"],
            action_items=[
                MeetingActionItem(description="Send agenda", owner="Alice")
            ],
        )
        assert len(m.action_items) == 1
        assert m.action_items[0].owner == "Alice"


# ===========================================================================
# 5 — All tables empty after fresh init
# ===========================================================================

def test_all_domain_tables_empty(db):
    from database.models import (Project, ProjectTask, Stakeholder,
                                  EmailDocument, ChatMessage, MeetingNote,
                                  StatusReport, RiskEntry, HistoricalProject)
    from extensions import db as _db
    for model in (Project, ProjectTask, Stakeholder, EmailDocument,
                  ChatMessage, MeetingNote, StatusReport, RiskEntry, HistoricalProject):
        assert _db.session.query(model).count() == 0, f"{model.__name__} table not empty"
