"""
Agent REST API Blueprint (backend/app/api/agents.py)
Routes agent workflow triggers and chat requests to backend.app.agents module.
"""

from flask import Blueprint, request, jsonify
from backend.app.api.auth import role_required
from backend.app.agents import run_supervisor_workflow, run_chat_supervisor

agents_bp = Blueprint('agents', __name__, url_prefix='/api/agents')

@agents_bp.route('/run-workflow', methods=['POST'])
@role_required(['Admin', 'Program Manager', 'Project Manager', 'Team Lead', 'Executive'])
def run_workflow_api():
    data = request.get_json() or {}
    query = data.get('query', 'Analyze project risks and generate mitigation plan')
    project_code = data.get('project_code', 'PRJ-001')
    recipient_role = data.get('recipient_role', 'Executive')

    res = run_supervisor_workflow(query=query, project_code=project_code, recipient_role=recipient_role)
    return jsonify({
        'status': 'success',
        'workflow_result': res
    }), 200

@agents_bp.route('/chat', methods=['POST'])
@role_required(['Admin', 'Program Manager', 'Project Manager', 'Team Lead', 'Executive', 'Viewer'])
def chat_api():
    data = request.get_json() or {}
    message = data.get('message', 'What are the risks for PRJ-001?')
    project_code = data.get('project_code', 'PRJ-001')

    res = run_chat_supervisor(user_message=message, project_code=project_code)
    return jsonify({
        'status': 'success',
        'chat_result': res
    }), 200
