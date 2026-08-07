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

@emails_bp.route('/<int:email_id>/reject', methods=['POST'])
@role_required(['Admin', 'Program Manager', 'Project Manager'])
def reject_email(email_id):
    """Rejects AI-generated draft email."""
    email = EmailDraft.query.get(email_id)
    if not email:
        return jsonify({'error': 'Not Found', 'message': f'Email draft #{email_id} not found.'}), 404

    claims = get_jwt()
    email.status = 'REJECTED'

    audit = AuditLog(user_name=claims.get('username'), user_role=claims.get('role'), action='REJECT_EMAIL', target_type='EmailDraft', target_id=str(email_id), details=f'Rejected email #{email_id}')
    db.session.add(audit)
    db.session.commit()

    return jsonify({'status': 'success', 'message': f'Email #{email_id} rejected.', 'email': email.to_dict()}), 200
