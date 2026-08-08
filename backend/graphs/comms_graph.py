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
    def generate_role_tailored_copy(recipient_role: str, project_code: str, raid_item: Dict[str, Any], mitigations: list, recipient_email: str = 'linusimon@gmail.com') -> Dict[str, str]:
        """
        Generates distinct communication wording tailored by recipient role using TCSGenAIClient LLM.
        """
        role = recipient_role.capitalize()
        title = raid_item.get('title', 'Project Risk Alert')
        desc = raid_item.get('description', '')
        score = raid_item.get('risk_score', 75)
        cause = raid_item.get('root_cause', 'Dependency delay')
        mitigation_title = mitigations[0]['title'] if mitigations else "Deploy mock endpoint"

        # Set target recipient person name to Linus Simon
        recipient_name = 'Linus Simon'

        from backend.app.core.tcs_genai_client import TCSGenAIClient
        client = TCSGenAIClient()

        prompt = f"""
Generate an enterprise email draft for a stakeholder communication.

Recipient Name: {recipient_name}
Recipient Role: {role}
Project Code: {project_code}
Risk Title: {title}
Risk Score: {score}/100
Root Cause: {cause}
Proposed Mitigation: {mitigation_title}

Directive: Address the email to "Dear {recipient_name}," and write a role-tailored summary.
Return ONLY JSON format:
{{
  "subject": "...",
  "body": "..."
}}
"""
        try:
            res = client.generate_completion(prompt)
            content = res.get('content', '')
            if 'subject' in content and 'body' in content:
                import json
                clean_json = content.replace('```json', '').replace('```', '').strip()
                parsed = json.loads(clean_json)
                return {"subject": parsed['subject'], "body": parsed['body']}
        except Exception as e:
            print(f"[Comms Graph Warning] LLM copy generation fallback: {e}")

        # Deterministic dynamic fallback
        subject = f"PM Alert [{project_code}]: {title}"
        body = (
            f"Dear {recipient_name},\n\n"
            f"Project {project_code} RAID alert recorded:\n"
            f"• Risk Title: {title} (Score: {score}/100)\n"
            f"• Root Cause: {cause}\n"
            f"• Proposed Mitigation: {mitigation_title}\n\n"
            f"Best regards,\n"
            f"Program Management Office"
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
        copy = cls.generate_role_tailored_copy(recipient_role, project_code, primary_raid, mitigations, recipient_email)

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
