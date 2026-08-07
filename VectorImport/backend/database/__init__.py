"""
database/__init__.py
--------------------
Public surface of the database package.

    from database import init_db, Project, ProjectRepository
"""

from database.db import drop_db, health_check, init_db
from database.models import (
    # Enums
    AuditAction,
    CommunicationPreference,
    ProjectStatus,
    RiskImpact,
    RiskProbability,
    RiskStatus,
    TaskPriority,
    TaskStatus,
    # Models
    AuditLog,
    ChatMessage,
    EmailDocument,
    HistoricalProject,
    MeetingNote,
    Project,
    ProjectTask,
    RiskEntry,
    Stakeholder,
    StatusReport,
)
from database.repositories import (
    AuditLogRepository,
    ChatMessageRepository,
    EmailDocumentRepository,
    HistoricalProjectRepository,
    MeetingNoteRepository,
    ProjectRepository,
    ProjectTaskRepository,
    RiskEntryRepository,
    StakeholderRepository,
    StatusReportRepository,
)

__all__ = [
    # Lifecycle
    "init_db", "drop_db", "health_check",
    # Models
    "Project", "ProjectTask", "Stakeholder",
    "EmailDocument", "ChatMessage", "MeetingNote",
    "StatusReport", "RiskEntry", "HistoricalProject", "AuditLog",
    # Enums
    "ProjectStatus", "TaskPriority", "TaskStatus", "CommunicationPreference",
    "RiskProbability", "RiskImpact", "RiskStatus", "AuditAction",
    # Repositories
    "ProjectRepository", "ProjectTaskRepository", "StakeholderRepository",
    "EmailDocumentRepository", "ChatMessageRepository", "MeetingNoteRepository",
    "StatusReportRepository", "RiskEntryRepository",
    "HistoricalProjectRepository", "AuditLogRepository",
]
