"""
Enterprise Administration & System Observability REST API Blueprint
"""

import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash
from backend.app.db.models import db, User, AuditLog, KnowledgeDoc
from backend.app.api.auth import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
@role_required(['Admin'])
def get_users():
    """Admin Endpoint: List all user accounts."""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({'status': 'success', 'users': [u.to_dict() for u in users]}), 200

@admin_bp.route('/users', methods=['POST'])
@role_required(['Admin'])
def create_user():
    """Admin Endpoint: Create new user account with role assignment."""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', 'Viewer')

    if not username or not email or not password:
        return jsonify({'error': 'Bad Request', 'message': 'Username, email, and password are required.'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Conflict', 'message': 'Username or email already exists.'}), 409

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
        full_name=data.get('full_name', username)
    )
    db.session.add(user)

    claims = get_jwt()
    audit = AuditLog(user_name=claims.get('username'), user_role='Admin', action='CREATE_USER', target_type='User', details=f'Created user {username} ({role})')
    db.session.add(audit)
    db.session.commit()

    return jsonify({'status': 'success', 'message': f'User {username} created successfully.', 'user': user.to_dict()}), 201

@admin_bp.route('/audit-logs', methods=['GET'])
@role_required(['Admin', 'Program Manager'])
def get_audit_logs():
    """Query system security and action audit logs."""
    limit = int(request.args.get('limit', 50))
    action = request.args.get('action')

    query = AuditLog.query
    if action:
        query = query.filter_by(action=action)

    logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return jsonify({'status': 'success', 'total_returned': len(logs), 'audit_logs': [l.to_dict() for l in logs]}), 200

@admin_bp.route('/system-metrics', methods=['GET'])
@jwt_required()
def get_system_metrics():
    """Telemetry endpoint for System Admin view (token costs, audio logs, guardrail status)."""
    return jsonify({
        'status': 'success',
        'telemetry': {
            'mcp_server_port': 5001,
            'mcp_status': 'ONLINE',
            'guardrails_active': True,
            'pii_redaction_engine': 'Regex + Named Entity Recognition',
            'total_llm_tokens_used': 148520,
            'total_estimated_cost_usd': 0.297,
            'audio_stt_tts_engine': 'Web Speech API / Native Synthesis',
            'audio_events_logged': 14,
            'static_rag_docs': 5,
            'unstructured_rag_items': 12
        }
    }), 200

@admin_bp.route('/knowledge-docs', methods=['GET'])
@jwt_required()
def get_knowledge_docs():
    """List static knowledge documents."""
    docs = KnowledgeDoc.query.order_by(KnowledgeDoc.uploaded_at.desc()).all()
    return jsonify({'status': 'success', 'docs': [d.to_dict() for d in docs]}), 200

@admin_bp.route('/knowledge-docs/upload', methods=['POST'])
@role_required(['Admin', 'Program Manager'])
def upload_knowledge_doc():
    """Uploads static knowledge document for RAG indexing."""
    if 'file' not in request.files:
        return jsonify({'error': 'Bad Request', 'message': 'No file part in request.'}), 400

    file = request.files['file']
    doc_type = request.form.get('doc_type', 'Policy')

    if file.filename == '':
        return jsonify({'error': 'Bad Request', 'message': 'No file selected.'}), 400

    filename = file.filename
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../uploads'))
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)

    file_size = os.path.getsize(file_path)

    claims = get_jwt()
    username = claims.get('username', 'Admin')

    doc = KnowledgeDoc(
        title=filename,
        doc_type=doc_type,
        file_path=f"backend/app/uploads/{filename}",
        file_size=file_size,
        chunk_count=max(1, file_size // 300),
        rag_type='Static',
        uploaded_by=username
    )
    db.session.add(doc)

    audit = AuditLog(user_name=username, user_role=claims.get('role'), action='UPLOAD_DOC', target_type='KnowledgeDoc', details=f'Uploaded {filename} for Static RAG')
    db.session.add(audit)
    db.session.commit()

    return jsonify({'status': 'success', 'message': f'Document {filename} uploaded successfully.', 'doc': doc.to_dict()}), 201
