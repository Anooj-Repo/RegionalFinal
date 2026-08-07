"""
database/repositories.py
-------------------------
Repository pattern — typed CRUD for every domain model.

Rule: Services call repositories. Repositories call SQLAlchemy.
      No business logic lives here.
"""

from __future__ import annotations

from typing import Generic, Optional, Type, TypeVar

from extensions import db
from database.models import (
    AuditLog, AuditAction,
    Project, ProjectTask, Stakeholder,
    EmailDocument, ChatMessage, MeetingNote,
    StatusReport, RiskEntry, HistoricalProject,
)

T = TypeVar("T", bound=db.Model)


# ===========================================================================
# Generic base
# ===========================================================================

class BaseRepository(Generic[T]):
    """Generic CRUD — subclasses set `model` to a SQLAlchemy model class."""

    model: Type[T]

    @classmethod
    def get_by_id(cls, record_id: int) -> Optional[T]:
        return db.session.get(cls.model, record_id)

    @classmethod
    def get_all(cls) -> list[T]:
        return db.session.execute(db.select(cls.model)).scalars().all()

    @classmethod
    def save(cls, instance: T) -> T:
        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance

    @classmethod
    def delete(cls, instance: T) -> None:
        db.session.delete(instance)
        db.session.commit()


# ===========================================================================
# ProjectRepository
# ===========================================================================

class ProjectRepository(BaseRepository[Project]):
    model = Project

    @staticmethod
    def get_by_project_id(project_id: str) -> Optional[Project]:
        return db.session.execute(
            db.select(Project).where(Project.project_id == project_id)
        ).scalar_one_or_none()

    @staticmethod
    def get_by_name(name: str) -> Optional[Project]:
        return db.session.execute(
            db.select(Project).where(Project.name == name)
        ).scalar_one_or_none()

    @staticmethod
    def get_by_status(status) -> list[Project]:
        return db.session.execute(
            db.select(Project).where(Project.status == status)
        ).scalars().all()

    @staticmethod
    def create(**kwargs) -> Project:
        instance = Project(**kwargs)
        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance


# ===========================================================================
# ProjectTaskRepository
# ===========================================================================

class ProjectTaskRepository(BaseRepository[ProjectTask]):
    model = ProjectTask

    @staticmethod
    def get_by_project(project_id: int) -> list[ProjectTask]:
        return db.session.execute(
            db.select(ProjectTask).where(ProjectTask.project_id == project_id)
        ).scalars().all()

    @staticmethod
    def get_by_status(project_id: int, status) -> list[ProjectTask]:
        return db.session.execute(
            db.select(ProjectTask).where(
                ProjectTask.project_id == project_id,
                ProjectTask.status == status,
            )
        ).scalars().all()

    @staticmethod
    def create(**kwargs) -> ProjectTask:
        instance = ProjectTask(**kwargs)
        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance


# ===========================================================================
# StakeholderRepository
# ===========================================================================

class StakeholderRepository(BaseRepository[Stakeholder]):
    model = Stakeholder

    @staticmethod
    def get_by_project(project_id: int) -> list[Stakeholder]:
        return db.session.execute(
            db.select(Stakeholder).where(Stakeholder.project_id == project_id)
        ).scalars().all()

    @staticmethod
    def create(**kwargs) -> Stakeholder:
        instance = Stakeholder(**kwargs)
        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance


# ===========================================================================
# EmailDocumentRepository
# ===========================================================================

class EmailDocumentRepository(BaseRepository[EmailDocument]):
    model = EmailDocument

    @staticmethod
    def get_by_project(project_id: int) -> list[EmailDocument]:
        return db.session.execute(
            db.select(EmailDocument).where(EmailDocument.project_id == project_id)
        ).scalars().all()

    @staticmethod
    def get_by_sender(project_id: int, sender: str) -> list[EmailDocument]:
        return db.session.execute(
            db.select(EmailDocument).where(
                EmailDocument.project_id == project_id,
                EmailDocument.sender == sender,
            )
        ).scalars().all()

    @staticmethod
    def create(**kwargs) -> EmailDocument:
        instance = EmailDocument(**kwargs)
        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance


# ===========================================================================
# ChatMessageRepository
# ===========================================================================

class ChatMessageRepository(BaseRepository[ChatMessage]):
    model = ChatMessage

    @staticmethod
    def get_by_project(project_id: int) -> list[ChatMessage]:
        return db.session.execute(
            db.select(ChatMessage).where(ChatMessage.project_id == project_id)
        ).scalars().all()

    @staticmethod
    def get_by_thread(thread_id: str) -> list[ChatMessage]:
        return db.session.execute(
            db.select(ChatMessage)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.timestamp)
        ).scalars().all()

    @staticmethod
    def create(**kwargs) -> ChatMessage:
        instance = ChatMessage(**kwargs)
        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance


# ===========================================================================
# MeetingNoteRepository
# ===========================================================================

class MeetingNoteRepository(BaseRepository[MeetingNote]):
    model = MeetingNote

    @staticmethod
    def get_by_project(project_id: int) -> list[MeetingNote]:
        return db.session.execute(
            db.select(MeetingNote).where(MeetingNote.project_id == project_id)
        ).scalars().all()

    @staticmethod
    def create(**kwargs) -> MeetingNote:
        instance = MeetingNote(**kwargs)
        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance


# ===========================================================================
# StatusReportRepository
# ===========================================================================

class StatusReportRepository(BaseRepository[StatusReport]):
    model = StatusReport

    @staticmethod
    def get_by_project(project_id: int) -> list[StatusReport]:
        return db.session.execute(
            db.select(StatusReport)
            .where(StatusReport.project_id == project_id)
            .order_by(StatusReport.reporting_period.desc())
        ).scalars().all()

    @staticmethod
    def get_latest(project_id: int) -> Optional[StatusReport]:
        return db.session.execute(
            db.select(StatusReport)
            .where(StatusReport.project_id == project_id)
            .order_by(StatusReport.reporting_period.desc())
            .limit(1)
        ).scalar_one_or_none()

    @staticmethod
    def create(**kwargs) -> StatusReport:
        instance = StatusReport(**kwargs)
        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance


# ===========================================================================
# RiskEntryRepository
# ===========================================================================

class RiskEntryRepository(BaseRepository[RiskEntry]):
    model = RiskEntry

    @staticmethod
    def get_by_project(project_id: int) -> list[RiskEntry]:
        return db.session.execute(
            db.select(RiskEntry).where(RiskEntry.project_id == project_id)
        ).scalars().all()

    @staticmethod
    def get_open_risks(project_id: int) -> list[RiskEntry]:
        from database.models import RiskStatus
        return db.session.execute(
            db.select(RiskEntry).where(
                RiskEntry.project_id == project_id,
                RiskEntry.status == RiskStatus.OPEN,
            )
        ).scalars().all()

    @staticmethod
    def create(**kwargs) -> RiskEntry:
        instance = RiskEntry(**kwargs)
        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance


# ===========================================================================
# HistoricalProjectRepository
# ===========================================================================

class HistoricalProjectRepository(BaseRepository[HistoricalProject]):
    model = HistoricalProject

    @staticmethod
    def get_by_name(name: str) -> Optional[HistoricalProject]:
        return db.session.execute(
            db.select(HistoricalProject).where(HistoricalProject.project_name == name)
        ).scalar_one_or_none()

    @staticmethod
    def search_lessons(keyword: str) -> list[HistoricalProject]:
        """
        Returns historical projects whose lessons_learned JSON contains the keyword.
        Implemented at application level for SQLite compatibility.
        """
        all_records = db.session.execute(db.select(HistoricalProject)).scalars().all()
        return [
            r for r in all_records
            if any(keyword.lower() in lesson.lower() for lesson in (r.lessons_learned or []))
        ]

    @staticmethod
    def create(**kwargs) -> HistoricalProject:
        instance = HistoricalProject(**kwargs)
        db.session.add(instance)
        db.session.commit()
        db.session.refresh(instance)
        return instance


# ===========================================================================
# AuditLogRepository
# ===========================================================================

class AuditLogRepository(BaseRepository[AuditLog]):
    model = AuditLog

    @staticmethod
    def log(
        action: AuditAction,
        entity_type: str | None = None,
        entity_id: int | None = None,
        actor: str | None = None,
        ip_address: str | None = None,
        details: dict | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            action=action, entity_type=entity_type, entity_id=entity_id,
            actor=actor, ip_address=ip_address, details=details or {},
        )
        db.session.add(entry)
        db.session.commit()
        return entry

    @staticmethod
    def get_by_entity(entity_type: str, entity_id: int) -> list[AuditLog]:
        return db.session.execute(
            db.select(AuditLog)
            .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
        ).scalars().all()

    @staticmethod
    def get_recent(limit: int = 100) -> list[AuditLog]:
        return db.session.execute(
            db.select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
        ).scalars().all()
