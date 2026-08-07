"""
database/models.py
------------------
SQLAlchemy ORM — full business domain models.

Tables:
    projects            — core project entity
    project_tasks       — tasks within a project
    stakeholders        — project stakeholders
    email_documents     — ingested email communications
    chat_messages       — ingested chat/Slack messages
    meeting_notes       — meeting records with transcripts
    status_reports      — periodic status reports
    risk_entries        — identified project risks
    historical_projects — completed projects + lessons learned
    audit_logs          — immutable system-wide audit trail (kept from M3)
"""

from __future__ import annotations

import enum
import uuid

from extensions import db


# ===========================================================================
# Shared mixins
# ===========================================================================

class TimestampMixin:
    """Adds created_at / updated_at to any model."""

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )


# ===========================================================================
# Enums
# ===========================================================================

class ProjectStatus(str, enum.Enum):
    PLANNING   = "planning"
    ACTIVE     = "active"
    ON_HOLD    = "on_hold"
    COMPLETED  = "completed"
    CANCELLED  = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class TaskStatus(str, enum.Enum):
    OPEN        = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED     = "blocked"
    COMPLETED   = "completed"
    CANCELLED   = "cancelled"


class RiskProbability(str, enum.Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


class RiskImpact(str, enum.Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class RiskStatus(str, enum.Enum):
    OPEN      = "open"
    MITIGATED = "mitigated"
    ACCEPTED  = "accepted"
    CLOSED    = "closed"


class CommunicationPreference(str, enum.Enum):
    EMAIL   = "email"
    CHAT    = "chat"
    MEETING = "meeting"
    PHONE   = "phone"


class AuditAction(str, enum.Enum):
    CREATE = "create"
    READ   = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    LOGIN  = "login"
    LOGOUT = "logout"
    ERROR  = "error"


# ===========================================================================
# Table 1 — Project
# ===========================================================================

class Project(db.Model):
    """
    Lightweight project registry — stores only id, project_id, and name.
    All other project data is loaded on-demand from JSON via DataSourceRegistry.
    """

    __tablename__ = "projects"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(            # business key e.g. "PROG-ALPHA-2026"
        db.String(64),
        unique=True,
        nullable=False,
        index=True,
    )
    name       = db.Column(db.String(255), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Project id={self.id} project_id={self.project_id!r} name={self.name!r}>"


# ===========================================================================
# Table 2 — ProjectTask
# ===========================================================================

class ProjectTask(TimestampMixin, db.Model):
    """A single task / work item within a project."""

    __tablename__ = "project_tasks"

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id   = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title        = db.Column(db.String(255), nullable=False)
    description  = db.Column(db.Text,        nullable=True)
    owner        = db.Column(db.String(128), nullable=True)
    priority     = db.Column(db.Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM, index=True)
    status       = db.Column(db.Enum(TaskStatus),   nullable=False, default=TaskStatus.OPEN,     index=True)
    due_date     = db.Column(db.Date,    nullable=True)
    completion   = db.Column(db.Integer, nullable=False, default=0)      # 0–100 %
    dependencies = db.Column(db.JSON,    nullable=True, default=list)    # list of task ids
    blockers     = db.Column(db.JSON,    nullable=True, default=list)    # list of blocker strings

    project = db.relationship("Project", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<ProjectTask id={self.id} title={self.title!r} status={self.status}>"


# ===========================================================================
# Table 3 — Stakeholder
# ===========================================================================

class Stakeholder(TimestampMixin, db.Model):
    """A project stakeholder with role and contact preference."""

    __tablename__ = "stakeholders"

    id                       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id               = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name                     = db.Column(db.String(128), nullable=False)
    role                     = db.Column(db.String(128), nullable=True)
    department               = db.Column(db.String(128), nullable=True)
    communication_preference = db.Column(
        db.Enum(CommunicationPreference),
        nullable=False,
        default=CommunicationPreference.EMAIL,
    )

    project = db.relationship("Project", back_populates="stakeholders")

    def __repr__(self) -> str:
        return f"<Stakeholder id={self.id} name={self.name!r} role={self.role!r}>"


# ===========================================================================
# Table 4 — EmailDocument
# ===========================================================================

class EmailDocument(TimestampMixin, db.Model):
    """An ingested email communication associated with a project."""

    __tablename__ = "email_documents"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id  = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    sender      = db.Column(db.String(255),          nullable=False)
    recipients  = db.Column(db.JSON,                 nullable=False, default=list)   # list[str]
    subject     = db.Column(db.String(512),          nullable=True)
    timestamp   = db.Column(db.DateTime(timezone=True), nullable=True)
    body        = db.Column(db.Text,                 nullable=True)
    attachments = db.Column(db.JSON,                 nullable=True, default=list)   # list[str] (filenames)
    labels      = db.Column(db.JSON,                 nullable=True, default=list)   # list[str]

    project = db.relationship("Project", back_populates="emails")

    def __repr__(self) -> str:
        return f"<EmailDocument id={self.id} subject={self.subject!r}>"


# ===========================================================================
# Table 5 — ChatMessage
# ===========================================================================

class ChatMessage(TimestampMixin, db.Model):
    """A single message from a chat platform (Slack, Teams, etc.)."""

    __tablename__ = "chat_messages"

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    channel    = db.Column(db.String(128),              nullable=True,  index=True)
    sender     = db.Column(db.String(128),              nullable=False)
    timestamp  = db.Column(db.DateTime(timezone=True),  nullable=True)
    message    = db.Column(db.Text,                     nullable=True)
    thread_id  = db.Column(db.String(128),              nullable=True,  index=True)
    reactions  = db.Column(db.JSON,                     nullable=True, default=dict)  # {emoji: count}

    project = db.relationship("Project", back_populates="chat_messages")

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} channel={self.channel!r} sender={self.sender!r}>"


# ===========================================================================
# Table 6 — MeetingNote
# ===========================================================================

class MeetingNote(TimestampMixin, db.Model):
    """Structured meeting notes including decisions, actions, and transcript."""

    __tablename__ = "meeting_notes"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id    = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    meeting_title = db.Column(db.String(255), nullable=False)
    attendees     = db.Column(db.JSON,        nullable=True, default=list)   # list[str]
    decisions     = db.Column(db.JSON,        nullable=True, default=list)   # list[str]
    action_items  = db.Column(db.JSON,        nullable=True, default=list)   # list[dict]
    transcript    = db.Column(db.Text,        nullable=True)

    project = db.relationship("Project", back_populates="meeting_notes")

    def __repr__(self) -> str:
        return f"<MeetingNote id={self.id} title={self.meeting_title!r}>"


# ===========================================================================
# Table 7 — StatusReport
# ===========================================================================

class StatusReport(TimestampMixin, db.Model):
    """A periodic project status report."""

    __tablename__ = "status_reports"

    id               = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id       = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    reporting_period = db.Column(db.String(64),  nullable=False)           # e.g. "2026-W32"
    accomplishments  = db.Column(db.JSON,        nullable=True, default=list)  # list[str]
    blockers         = db.Column(db.JSON,        nullable=True, default=list)  # list[str]
    risks            = db.Column(db.JSON,        nullable=True, default=list)  # list[str]
    next_steps       = db.Column(db.JSON,        nullable=True, default=list)  # list[str]

    project = db.relationship("Project", back_populates="status_reports")

    def __repr__(self) -> str:
        return f"<StatusReport id={self.id} period={self.reporting_period!r}>"


# ===========================================================================
# Table 8 — RiskEntry
# ===========================================================================

class RiskEntry(TimestampMixin, db.Model):
    """An identified risk with probability, impact, and mitigation plan."""

    __tablename__ = "risk_entries"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id  = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title       = db.Column(db.String(255),            nullable=False)
    probability = db.Column(db.Enum(RiskProbability),  nullable=False, default=RiskProbability.MEDIUM, index=True)
    impact      = db.Column(db.Enum(RiskImpact),       nullable=False, default=RiskImpact.MEDIUM,      index=True)
    owner       = db.Column(db.String(128),            nullable=True)
    mitigation  = db.Column(db.Text,                   nullable=True)
    status      = db.Column(db.Enum(RiskStatus),       nullable=False, default=RiskStatus.OPEN,        index=True)

    project = db.relationship("Project", back_populates="risk_entries")

    def __repr__(self) -> str:
        return f"<RiskEntry id={self.id} title={self.title!r} status={self.status}>"


# ===========================================================================
# Table 9 — HistoricalProject
# ===========================================================================

class HistoricalProject(TimestampMixin, db.Model):
    """
    A completed project archived for institutional knowledge.
    Not linked to live projects — standalone reference data.
    """

    __tablename__ = "historical_projects"

    id                     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name           = db.Column(db.String(255), nullable=False, index=True)
    lessons_learned        = db.Column(db.JSON,        nullable=True, default=list)  # list[str]
    historical_risks       = db.Column(db.JSON,        nullable=True, default=list)  # list[dict]
    successful_mitigations = db.Column(db.JSON,        nullable=True, default=list)  # list[str]

    def __repr__(self) -> str:
        return f"<HistoricalProject id={self.id} name={self.project_name!r}>"


# ===========================================================================
# Table 10 — AuditLog  (kept from Milestone 3 — system-wide, immutable)
# ===========================================================================

class AuditLog(db.Model):
    """Immutable system-wide audit trail — must never be updated."""

    __tablename__ = "audit_logs"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action      = db.Column(db.Enum(AuditAction), nullable=False, index=True)
    entity_type = db.Column(db.String(64),        nullable=True,  index=True)
    entity_id   = db.Column(db.Integer,           nullable=True,  index=True)
    actor       = db.Column(db.String(128),       nullable=True)
    ip_address  = db.Column(db.String(45),        nullable=True)
    details     = db.Column(db.JSON,              nullable=True, default=dict)
    created_at  = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action} entity={self.entity_type}:{self.entity_id}>"
