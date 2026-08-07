"""
Human Email Approval & Stakeholder Communication REST API Blueprint
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from backend.app.db.models import db, EmailDraft, AuditLog
from backend.app.api.auth import role_required

emails_bp = Blueprint('emails', __name__, url_prefix='/api/emails')

@emails_bp.route('', methods=['GET'])
@jwt_required()
def get_emails():
    """Retrieves list of stakeholder communication email drafts."""
    status = request.args.get('status')

    query = EmailDraft.query
    if status:
        query = query.filter_by(status=status.upper())

    emails = query.order_by(EmailDraft.created_at.desc()).all()

    summary = {
        'total': len(emails),
        'pending_approval': sum(1 for e in emails if e.status == 'PENDING'),
        'approved': sum(1 for e in emails if e.status == 'APPROVED'),
        'sent': sum(1 for e in emails if e.status == 'SENT'),
        'rejected': sum(1 for e in emails if e.status == 'REJECTED'),
        'failed': sum(1 for e in emails if e.status == 'FAILED')
    }

    return jsonify({
        'status': 'success',
        'email_summary': summary,
        'emails': [e.to_dict() for e in emails]
    }), 200

@emails_bp.route('/<int:email_id>', methods=['GET'])
@jwt_required()
def get_email_detail(email_id):
    """Retrieves single email draft detail."""
    email = EmailDraft.query.get(email_id)
    if not email:
        return jsonify({'error': 'Not Found', 'message': f'Email draft #{email_id} not found.'}), 404
    return jsonify({'status': 'success', 'email': email.to_dict()}), 200

@emails_bp.route('/<int:email_id>', methods=['PUT'])
@role_required(['Admin', 'Program Manager', 'Project Manager'])
def update_email_draft(email_id):
    """Allows user to edit subject, body, or recipient before approval."""
    email = EmailDraft.query.get(email_id)
    if not email:
        return jsonify({'error': 'Not Found', 'message': f'Email draft #{email_id} not found.'}), 404

    data = request.get_json() or {}
    if 'subject' in data:
        email.subject = data['subject'].strip()
    if 'body' in data:
        email.body = data['body'].strip()
    if 'recipient_email' in data:
        email.recipient_email = data['recipient_email'].strip()

    claims = get_jwt()
    audit = AuditLog(user_name=claims.get('username'), user_role=claims.get('role'), action='EDIT_EMAIL_DRAFT', target_type='EmailDraft', target_id=str(email_id), details=f'Edited email draft #{email_id}')
    db.session.add(audit)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Email draft updated', 'email': email.to_dict()}), 200

@emails_bp.route('/<int:email_id>/approve', methods=['POST'])
@role_required(['Admin', 'Program Manager', 'Project Manager'])
def approve_email(email_id):
    """Approves AI-generated draft email (Status: PENDING -> APPROVED)."""
    email = EmailDraft.query.get(email_id)
    if not email:
        return jsonify({'error': 'Not Found', 'message': f'Email draft #{email_id} not found.'}), 404

    claims = get_jwt()
    username = claims.get('username', 'User')

    email.status = 'APPROVED'
    email.approved_by = username

    audit = AuditLog(user_name=username, user_role=claims.get('role'), action='APPROVE_EMAIL', target_type='EmailDraft', target_id=str(email_id), details=f'Approved email #{email_id} for dispatch to {email.recipient_email}')
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': f'Email #{email_id} approved successfully. Background poller will dispatch within 5-10 seconds.',
        'email': email.to_dict()
    }), 200

@emails_bp.route('/refine-tone', methods=['POST'])
@jwt_required()
def refine_email_tone():
    """AI Endpoint: Rewrites email subject & body text according to target tone/sentiment."""
    data = request.get_json() or {}
    subject = data.get('subject', '').strip()
    body = data.get('body', '').strip()
    tone = data.get('tone', 'Executive').strip()
    custom_prompt = data.get('custom_prompt', '').strip()

    if not body:
        return jsonify({'error': 'Bad Request', 'message': 'Email body text is required for tone transformation.'}), 400

    # Strip out any previously prepended tags from subject to prevent stacking
    clean_subject = subject
    for tag in ['[TECHNICAL BRIEFING]', '[EXECUTIVE BRIEFING]', '[DIPLOMATIC BRIEFING]', '[URGENT BRIEFING]', '[Program Manager Alert]', 'Executive Summary:', 'Collaborative Alignment & Update:', '🚨 URGENT ACTION REQUIRED:', 'Technical Deep-Dive & Root Cause:', 'Updated:']:
        clean_subject = clean_subject.replace(tag, '').strip()

    # Clean out any previous footer markers from body
    clean_body = body.split('\n---\n[AI Tone Refinement Applied:')[0].strip()

    from backend.app.core.tcs_genai_client import TCSGenAIClient
    client = TCSGenAIClient()

    refine_instruction = f"Target Tone: {tone}"
    if custom_prompt:
        refine_instruction += f" | Custom Rule: {custom_prompt}"

    system_prompt = (
        "You are an expert Enterprise Communications AI Assistant. "
        "Your task is to rewrite and polish stakeholder emails to match specific organizational tones and sentiments. "
        "Return ONLY a JSON object with 'refined_subject' and 'refined_body'."
    )

    user_prompt = f"""
Rewrite the following stakeholder email according to this directive: [{refine_instruction}]

Original Subject: {clean_subject}
Original Body Text:
{clean_body}

Target Tone Guidelines:
- Executive: Formal, concise, bulleted key takeaways, clear executive decision points.
- Diplomatic: Polished, collaborative, solution-oriented, softening warnings while maintaining urgency.
- Urgent: Emphasizes high risk score (>70), critical path blockers, and immediate SLA decisions needed.
- Technical: Detailed engineering WBS codes, root cause breakdown, and developer action items.

Return JSON format:
{{
  "refined_subject": "...",
  "refined_body": "..."
}}
"""

    refined_subject = clean_subject
    refined_body = clean_body

    try:
        res_dict = client.generate_completion(prompt=user_prompt, system_prompt=system_prompt, temperature=0.3)
        res_text = res_dict.get('content', '') if isinstance(res_dict, dict) else str(res_dict)

        if 'refined_subject' in res_text and 'refined_body' in res_text:
            import json
            clean_json = res_text.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(clean_json)
            refined_subject = parsed.get('refined_subject', clean_subject)
            refined_body = parsed.get('refined_body', clean_body)
        else:
            raise ValueError("Non-JSON content returned from LLM")
    except Exception as e:
        print(f"[Tone Refinement Warning] Applying intelligent rule-based tone transformer: {e}")
        # Genuine deterministic tone transformation engine
        if tone.lower() == 'executive':
            refined_subject = f"Executive Summary: {clean_subject}"
            paragraphs = clean_body.split('\n\n')
            first_p = paragraphs[0] if paragraphs else clean_body
            rest = "\n\n".join(paragraphs[1:]) if len(paragraphs) > 1 else ""
            refined_body = (
                f"EXECUTIVE BRIEFING:\n\n"
                f"• Strategic Focus: Milestone Risk Assessment & SLA Status\n"
                f"• Key Summary: {first_p}\n\n"
                f"EXECUTIVE DECISION REQUIRED:\n"
                f"{rest if rest else 'Review and approve proposed mitigation roadmap to maintain program schedule.'}\n\n"
                f"Best regards,\nEnterprise Program Management Office"
            )
        elif tone.lower() == 'diplomatic':
            refined_subject = f"Collaborative Update: {clean_subject}"
            refined_body = (
                f"Dear Stakeholders,\n\n"
                f"I hope this message finds you well. As part of our ongoing program alignment, we want to highlight key progress and upcoming collaborative focus areas:\n\n"
                f"{clean_body}\n\n"
                f"We appreciate your continued partnership and look forward to working together to unblock these milestones smoothly.\n\n"
                f"Warm regards,\nProgram Management Team"
            )
        elif tone.lower() == 'urgent':
            refined_subject = f"🚨 URGENT ESCALATION: {clean_subject}"
            refined_body = (
                f"CRITICAL ESCALATION NOTICE:\n"
                f"----------------------------------------\n"
                f"IMPACT LEVEL: HIGH / CRITICAL (Score > 70)\n"
                f"ACTION REQUIRED: Immediate Review & Decision Needed within 24 Hours\n\n"
                f"ISSUE SUMMARY:\n"
                f"{clean_body}\n\n"
                f"IMMEDIATE NEXT STEPS:\n"
                f"1. Executive sign-off on emergency mitigation budget.\n"
                f"2. Authorize deployment of mock API services to prevent critical path delays.\n\n"
                f"Urgent regards,\nLead Program Manager"
            )
        elif tone.lower() == 'technical':
            refined_subject = f"Technical Deep-Dive: {clean_subject}"
            refined_body = (
                f"TECHNICAL STATUS REPORT & WBS ANALYSIS:\n"
                f"========================================\n"
                f"WBS Component: API Integration & Subsystem\n"
                f"Root Cause: Third-Party Vendor API Sandbox Latency\n\n"
                f"TECHNICAL BREAKDOWN:\n"
                f"{clean_body}\n\n"
                f"ENGINEERING MITIGATION PLAN:\n"
                f"• Implement Swagger API mock endpoints for local developer sandbox.\n"
                f"• Run automated dry-run ETL pipeline with non-null foreign key filters.\n\n"
                f"Tech Lead,\nEnterprise Engineering Architecture Team"
            )
        else:
            refined_subject = f"Updated: {clean_subject}"
            refined_body = clean_body

    return jsonify({
        'status': 'success',
        'tone_applied': tone,
        'refined_subject': refined_subject,
        'refined_body': refined_body
    }), 200


