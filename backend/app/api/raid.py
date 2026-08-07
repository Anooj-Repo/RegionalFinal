"""
RAID Register & Mitigation Action REST API Blueprint
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from backend.app.db.models import db, RAIDItem, MitigationAction, Project, AuditLog
from backend.app.api.auth import role_required

raid_bp = Blueprint('raid', __name__, url_prefix='/api/raid')

@raid_bp.route('', methods=['GET'])
@jwt_required()
def get_raid_items():
    """Retrieves RAID items filtered by project_id or category (Risk, Assumption, Issue, Dependency)."""
    project_id = request.args.get('project_id')
    category = request.args.get('category')

    query = RAIDItem.query
    if project_id and project_id.isdigit():
        query = query.filter_by(project_id=int(project_id))
    if category:
        query = query.filter_by(category=category.capitalize())

    items = query.order_by(RAIDItem.risk_score.desc()).all()

    # RAID category summary
    summary = {
        'total': len(items),
        'risks': sum(1 for i in items if i.category == 'Risk'),
        'assumptions': sum(1 for i in items if i.category == 'Assumption'),
        'issues': sum(1 for i in items if i.category == 'Issue'),
        'dependencies': sum(1 for i in items if i.category == 'Dependency')
    }

    return jsonify({
        'status': 'success',
        'raid_summary': summary,
        'raid_items': [i.to_dict() for i in items]
    }), 200

@raid_bp.route('/<int:raid_id>', methods=['GET'])
@jwt_required()
def get_raid_detail(raid_id):
    """Retrieves single RAID item detail including mitigation checklist."""
    item = RAIDItem.query.get(raid_id)
    if not item:
        return jsonify({'error': 'Not Found', 'message': f'RAID item #{raid_id} not found.'}), 404
    return jsonify({'status': 'success', 'raid_item': item.to_dict()}), 200

@raid_bp.route('', methods=['POST'])
@role_required(['Admin', 'Program Manager', 'Project Manager', 'Team Lead'])
def create_raid_item():
    """Creates a new RAID register item."""
    data = request.get_json() or {}

    project_id = data.get('project_id')
    category = data.get('category', 'Risk').capitalize()
    title = data.get('title', '').strip()

    if not project_id or not title:
        return jsonify({'error': 'Bad Request', 'message': 'project_id and title are required.'}), 400

    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Not Found', 'message': f'Project #{project_id} not found.'}), 404

    likelihood = data.get('likelihood', 'Medium')
    impact = data.get('impact', 'Medium')
    
    # Calculate Risk Score (Likelihood x Impact matrix)
    score_map = {'High': 3, 'Medium': 2, 'Low': 1}
    risk_score = int(data.get('risk_score', score_map.get(likelihood, 2) * score_map.get(impact, 2) * 11))

    item = RAIDItem(
        project_id=project_id,
        category=category,
        title=title,
        description=data.get('description', ''),
        likelihood=likelihood,
        impact=impact,
        risk_score=risk_score,
        status=data.get('status', 'Open'),
        owner_name=data.get('owner_name', project.owner_name),
        root_cause=data.get('root_cause', '')
    )
    db.session.add(item)

    claims = get_jwt()
    audit = AuditLog(user_name=claims.get('username'), user_role=claims.get('role'), action='CREATE_RAID_ITEM', target_type='RAIDItem', details=f'Created {category}: {title} (Score: {risk_score})')
    db.session.add(audit)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'RAID item created successfully', 'raid_item': item.to_dict()}), 201

@raid_bp.route('/<int:raid_id>/mitigation', methods=['POST'])
@role_required(['Admin', 'Program Manager', 'Project Manager', 'Team Lead'])
def add_mitigation_action(raid_id):
    """Adds a mitigation action item to a RAID record."""
    item = RAIDItem.query.get(raid_id)
    if not item:
        return jsonify({'error': 'Not Found', 'message': f'RAID item #{raid_id} not found.'}), 404

    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Bad Request', 'message': 'Action item title is required.'}), 400

    action = MitigationAction(
        raid_id=raid_id,
        title=title,
        description=data.get('description', ''),
        owner_name=data.get('owner_name', item.owner_name),
        due_date=data.get('due_date', ''),
        status=data.get('status', 'In Progress'),
        progress_pct=int(data.get('progress_pct', 0))
    )
    db.session.add(action)

    claims = get_jwt()
    audit = AuditLog(user_name=claims.get('username'), user_role=claims.get('role'), action='ADD_MITIGATION', target_type='MitigationAction', details=f'Added mitigation "{title}" to RAID #{raid_id}')
    db.session.add(audit)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Mitigation action created', 'mitigation': action.to_dict()}), 201
