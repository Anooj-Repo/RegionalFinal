"""
Repository Layer for Database Operations (backend/app/repositories/project_repository.py)
Encapsulates CRUD operations for Projects, Tasks, RAID Items, Email Drafts, and Audit Logs.
"""

from typing import List, Optional, Dict, Any
from backend.app.db.models import db, User, Project, Task, RAIDItem, MitigationAction, EmailDraft, AuditLog

class ProjectRepository:
    @staticmethod
    def get_all_projects(phase: Optional[str] = None, health: Optional[str] = None) -> List[Project]:
        query = Project.query
        if phase:
            query = query.filter_by(lifecycle_phase=phase)
        if health:
            query = query.filter_by(health_status=health)
        return query.all()

    @staticmethod
    def get_project_by_code(code: str) -> Optional[Project]:
        return Project.query.filter_by(code=code).first()

    @staticmethod
    def get_raid_items(project_id: Optional[int] = None, category: Optional[str] = None) -> List[RAIDItem]:
        query = RAIDItem.query
        if project_id:
            query = query.filter_by(project_id=project_id)
        if category:
            query = query.filter_by(category=category)
        return query.order_by(RAIDItem.risk_score.desc()).all()

    @staticmethod
    def get_email_drafts(status: Optional[str] = None) -> List[EmailDraft]:
        query = EmailDraft.query
        if status:
            query = query.filter_by(status=status)
        return query.order_by(EmailDraft.created_at.desc()).all()

    @staticmethod
    def get_email_by_id(email_id: int) -> Optional[EmailDraft]:
        return EmailDraft.query.get(email_id)

    @staticmethod
    def create_email_draft(project_id: int, recipient_role: str, recipient_email: str, subject: str, body: str, created_by: str = 'AI_Agent') -> EmailDraft:
        draft = EmailDraft(
            project_id=project_id,
            recipient_role=recipient_role,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            status='PENDING',
            created_by=created_by
        )
        db.session.add(draft)
        db.session.commit()
        return draft

    @staticmethod
    def create_audit_log(user_id: Optional[int], user_name: str, user_role: str, action: str, target_type: str, target_id: Optional[int], details: str):
        log = AuditLog(
            user_id=user_id,
            user_name=user_name,
            user_role=user_role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details
        )
        db.session.add(log)
        db.session.commit()
        return log
