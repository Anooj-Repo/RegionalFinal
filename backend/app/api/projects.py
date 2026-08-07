"""
Projects REST API Blueprint
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from backend.app.db.models import db, Project, Task, RAIDItem, AuditLog
from backend.app.api.auth import role_required

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    """Retrieves list of projects with optional phase or health filtering."""
    phase = request.args.get('phase')
    health = request.args.get('health')

    query = Project.query
    if phase:
        query = query.filter_by(lifecycle_phase=phase)
    if health:
        query = query.filter_by(health_status=health)

    projects = query.order_by(Project.created_at.desc()).all()

    # Aggregate portfolio health stats
    total = len(projects)
    healthy_cnt = sum(1 for p in projects if p.health_status == 'Healthy')
    at_risk_cnt = sum(1 for p in projects if p.health_status == 'At Risk')
    critical_cnt = sum(1 for p in projects if p.health_status == 'Critical')

    return jsonify({
        'status': 'success',
        'portfolio_summary': {
            'total_projects': total,
            'healthy_count': healthy_cnt,
            'at_risk_count': at_risk_cnt,
            'critical_count': critical_cnt
        },
        'projects': [p.to_dict() for p in projects]
    }), 200

@projects_bp.route('/<identifier>', methods=['GET'])
@jwt_required()
def get_project_by_id_or_code(identifier):
    """Retrieves detailed project model including WBS Tasks and RAID Register."""
    if identifier.isdigit():
        project = Project.query.get(int(identifier))
    else:
        project = Project.query.filter_by(code=identifier.upper()).first()

    if not project:
        return jsonify({'error': 'Not Found', 'message': f'Project "{identifier}" not found.'}), 404

    data = project.to_dict()
    data['tasks'] = [t.to_dict() for t in project.tasks]
    data['raid_items'] = [r.to_dict() for r in project.raid_items]

    return jsonify({'status': 'success', 'project': data}), 200

@projects_bp.route('', methods=['POST'])
@role_required(['Admin', 'Program Manager'])
def create_project():
    """Creates a new enterprise project (Admin / Program Manager only)."""
    data = request.get_json() or {}

    code = data.get('code', '').upper().strip()
    name = data.get('name', '').strip()
    phase = data.get('lifecycle_phase', 'Mobilization')
    owner = data.get('owner_name', '').strip()

    if not code or not name or not owner:
        return jsonify({'error': 'Bad Request', 'message': 'Project code, name, and owner_name are required.'}), 400

    existing = Project.query.filter_by(code=code).first()
    if existing:
        return jsonify({'error': 'Conflict', 'message': f'Project code "{code}" already exists.'}), 409

    project = Project(
        code=code,
        name=name,
        description=data.get('description', ''),
        lifecycle_phase=phase,
        health_status=data.get('health_status', 'Healthy'),
        progress_pct=data.get('progress_pct', 0),
        owner_name=owner,
        start_date=data.get('start_date', ''),
        end_date=data.get('end_date', ''),
        budget=float(data.get('budget', 0.0)),
        spent=float(data.get('spent', 0.0))
    )
    db.session.add(project)

    claims = get_jwt()
    audit = AuditLog(user_name=claims.get('username'), user_role=claims.get('role'), action='CREATE_PROJECT', target_type='Project', details=f'Created project {code}: {name}')
    db.session.add(audit)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Project created successfully', 'project': project.to_dict()}), 201
