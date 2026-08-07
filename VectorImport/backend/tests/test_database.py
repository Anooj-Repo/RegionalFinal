"""
tests/test_database.py
-----------------------
Database structural tests — updated for domain models (Milestone 6).
"""

import pytest
from extensions import db as _db


# ---------------------------------------------------------------------------
# Core domain tables that must exist
# ---------------------------------------------------------------------------

EXPECTED_TABLES = {
    "projects", "project_tasks", "stakeholders",
    "email_documents", "chat_messages", "meeting_notes",
    "status_reports", "risk_entries", "historical_projects",
    "audit_logs",
}


def test_all_tables_exist(db):
    existing = set(_db.metadata.tables.keys())
    missing = EXPECTED_TABLES - existing
    assert not missing, f"Missing tables: {missing}"


def test_tables_are_empty_on_init(db):
    """All domain tables start empty."""
    from database.models import (
        Project, ProjectTask, Stakeholder,
        EmailDocument, ChatMessage, MeetingNote,
        StatusReport, RiskEntry, HistoricalProject, AuditLog,
    )
    for model in (Project, ProjectTask, Stakeholder, EmailDocument,
                  ChatMessage, MeetingNote, StatusReport, RiskEntry,
                  HistoricalProject, AuditLog):
        assert _db.session.query(model).count() == 0


def test_audit_logs_no_updated_at(db):
    cols = {c.name for c in _db.metadata.tables["audit_logs"].columns}
    assert "updated_at" not in cols, "audit_logs must be immutable"


def test_db_health_check(app):
    from database.db import health_check
    with app.app_context():
        result = health_check()
    assert result["status"] == "ok"
