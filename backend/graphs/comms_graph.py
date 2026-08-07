"""
Graph 3: Communication Graph (backend/graphs/comms_graph.py)
Workflow: Audience Classification -> Role-Tailored Tone/Wording Generation -> Draft Creation in app.db with PENDING status for Mandatory Human Approval.
"""

import os
import sys
from typing import Dict, Any

# Add parent path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.db.models import db, EmailDraft, AuditLog

class CommunicationGraph:
    """Communication LangGraph Workflow Node enforcing Mandatory Human Approval."""

    @staticmethod
    def generate_role_tailored_copy(recipient_role: str, project_code: str, raid_item: Dict[str, Any], mitigations: list) -> Dict[str, str]:
        """
        Generates distinct communication wording tailored by recipient role.
        """
        role = recipient_role.capitalize()
        title = raid_item.get('title', 'Project Risk Alert')
        desc = raid_item.get('description', '')
        score = raid_item.get('risk_score', 75)
        cause = raid_item.get('root_cause', 'Dependency delay')
        mitigation_title = mitigations[0]['title'] if mitigations else "Deploy mock endpoint"

        if role == 'Executive':
            subject = f"Executive Alert: {project_code} Risk Score Escalated ({score}/100)"
            body = (
                f"Dear Executive Leadership,\n\n"
                f"We are providing an executive alert regarding {project_code}.\n"
                f"Key Issue: {title} (Risk Score: {score}/100).\n"
                f"Strategic Impact: Potential 5-day schedule impact to critical path milestone.\n"
                f"Mitigation Action Plan: {mitigation_title}.\n\n"
                f"No immediate financial budget adjustment is required. PMO will provide a follow-up briefing on Friday.\n\n"
                f"Sincerely,\nProgram Management AI Assistant"
            )
        elif role in ['Tech Lead', 'Developer']:
            subject = f"Technical Action Required: {project_code} - {title}"
            body = (
                f"Hi Technical Team,\n\n"
                f"Technical risk flagged for {project_code}.\n"
                f"Root Cause Details: {cause}.\n"
                f"API / Component Impact: {desc}\n"
                f"Action Item: {mitigation_title}. Please review mock server swagger specs in repository.\n\n"
                f"Regards,\nTech Lead & PM AI"
            )
        elif role == 'Client':
            subject = f"Project Update: {project_code} Quality Assurance & Delivery Plan"
            body = (
                f"Dear Valued Partner,\n\n"
                f"We are sharing a routine delivery update for {project_code}.\n"
                f"Our engineering teams are conducting rigorous pre-deployment testing on external integrations to ensure 100% reliability.\n"
                f"Our team is executing: {mitigation_title} to maintain delivery timelines without compromising quality.\n\n"
                f"Best regards,\nCustomer Success & Delivery Team"
            )
        else: # Program Manager / Project Manager default
            subject = f"PM Alert [{project_code}]: {title}"
            body = (
                f"Hi Program Management Team,\n\n"
                f"Project {project_code} RAID alert recorded:\n"
                f"- Category: {raid_item.get('category', 'Risk')}\n"
                f"- Title: {title}\n"
                f"- Risk Score: {score}/100\n"
                f"- Root Cause: {cause}\n"
                f"- Proposed Mitigation: {mitigation_title}\n\n"
                f"Draft created in Communication Center for Human Approval.\n\n"
                f"Regards,\nPM AI Assistant"
            )

        return {"subject": subject, "body": body}

    @classmethod
    def execute(cls, state: Dict[str, Any], app_context=None) -> Dict[str, Any]:
        """
        Executes Communication Graph processing and creates PENDING email draft in database.
        """
        project_data = state.get('project_data', {})
        project_code = project_data.get('code', 'PRJ-001')
        project_id = project_data.get('id', 1)

        risk_graph_res = state.get('risk_graph_output', {})
        primary_raid = risk_graph_res.get('primary_raid_item', {})
        mitigations = risk_graph_res.get('proposed_mitigations', [])

        recipient_role = state.get('recipient_role', 'Executive')
        recipient_email = state.get('recipient_email', 'linusimon@gmail.com')

        # Generate Tailored Copy
        copy = cls.generate_role_tailored_copy(recipient_role, project_code, primary_raid, mitigations)

        # Database Insertion if app_context is active or standard Flask session
        draft_id = None
        try:
            draft = EmailDraft(
                project_id=project_id,
                recipient_role=recipient_role,
                recipient_email=recipient_email,
                subject=copy['subject'],
                body=copy['body'],
                status='PENDING',
                created_by='Communication Graph Agent'
            )
            db.session.add(draft)
            db.session.commit()
            draft_id = draft.id

            audit = AuditLog(
                user_name='Communication Graph Agent',
                user_role='AI Agent',
                action='CREATE_DRAFT_EMAIL',
                target_type='EmailDraft',
                target_id=str(draft_id),
                details=f'Created PENDING draft email #{draft_id} for {recipient_role} ({recipient_email}). Awaiting Human Approval.'
            )
            db.session.add(audit)
            db.session.commit()
        except Exception as e:
            print(f"[Comms Graph Warning] DB draft write skipped: {e}")

        return {
            "graph": "Communication Graph",
            "status": "COMPLETED",
            "human_approval_required": True,
            "draft_email_status": "PENDING",
            "created_draft_id": draft_id,
            "recipient_role": recipient_role,
            "recipient_email": recipient_email,
            "generated_subject": copy['subject'],
            "generated_body": copy['body']
        }
