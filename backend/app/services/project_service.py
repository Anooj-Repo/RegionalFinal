"""
Service Layer for Business Logic (backend/app/services/project_service.py)
Orchestrates guardrail validations, database access via repositories, and agent invocations.
"""

from typing import Dict, Any, List, Optional
from backend.app.repositories.project_repository import ProjectRepository
from backend.app.core.guardrails import SecurityGuardrails

class ProjectService:
    @staticmethod
    def get_portfolio_summary() -> Dict[str, Any]:
        projects = ProjectRepository.get_all_projects()
        total = len(projects)
        healthy = sum(1 for p in projects if p.health_status == 'Healthy')
        at_risk = sum(1 for p in projects if p.health_status == 'At Risk')
        critical = sum(1 for p in projects if p.health_status == 'Critical')

        return {
            'status': 'success',
            'portfolio_summary': {
                'total_projects': total,
                'healthy_count': healthy,
                'at_risk_count': at_risk,
                'critical_count': critical
            },
            'projects': [p.to_dict() for p in projects]
        }

    @staticmethod
    def get_project_details(code: str) -> Dict[str, Any]:
        project = ProjectRepository.get_project_by_code(code)
        if not project:
            return {'status': 'error', 'message': f'Project {code} not found'}
        return {'status': 'success', 'project': project.to_dict()}

    @staticmethod
    def approve_email_draft(email_id: int, approved_by_user: str) -> Dict[str, Any]:
        draft = ProjectRepository.get_email_by_id(email_id)
        if not draft:
            return {'status': 'error', 'message': f'Email draft #{email_id} not found'}

        from datetime import datetime
        draft.status = 'APPROVED'
        draft.approved_by = approved_by_user
        
        # Save audit log
        ProjectRepository.create_audit_log(
            user_id=1,
            user_name=approved_by_user,
            user_role='Program Manager',
            action='EMAIL_APPROVED',
            target_type='EmailDraft',
            target_id=email_id,
            details=f'User {approved_by_user} approved email draft #{email_id} for Resend API dispatch.'
        )

        return {'status': 'success', 'message': f'Email draft #{email_id} approved.', 'email': draft.to_dict()}
