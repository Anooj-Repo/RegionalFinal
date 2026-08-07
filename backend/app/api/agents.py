"""
Multi-Agent LangGraph Workflow & Chat REST API Blueprint
"""

import sys
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from backend.app.db.models import db, Project, RAIDItem, AuditLog
from backend.graphs.supervisor import LangGraphSupervisor

mcp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../mcp'))
if mcp_dir not in sys.path:
    sys.path.insert(0, mcp_dir)

from tools.adapters import SlackTeamsEmailAdapter


agents_bp = Blueprint('agents', __name__, url_prefix='/api/agents')

@agents_bp.route('/run-workflow', methods=['POST'])
@jwt_required()
def run_agent_workflow():
    """
    Triggers the 3-LangGraph Multi-Agent Orchestration Workflow:
    Data Intelligence -> Risk Intelligence (RAID) -> Communication Graph (Human Approval).
    """
    data = request.get_json() or {}
    user_query = data.get('query', 'Analyze risk and mitigation plan for project.')
    project_code = data.get('project_code', 'PRJ-001')
    recipient_role = data.get('recipient_role', 'Executive')

    # Fetch Project & Task Data
    project = Project.query.filter_by(code=project_code.upper()).first()
    project_dict = project.to_dict() if project else {"code": project_code, "name": "Project", "lifecycle_phase": "Mobilization"}
    if project:
        project_dict['tasks'] = [t.to_dict() for t in project.tasks]

    # Fetch Unstructured Comm Logs via MCP Adapter
    comm_data = SlackTeamsEmailAdapter.read_communication_logs(project_code=project_code)
    comm_logs = comm_data.get('logs', [])

    payload = {
        "user_query": user_query,
        "project_data": project_dict,
        "comm_logs": comm_logs,
        "recipient_role": recipient_role,
        "recipient_email": data.get('recipient_email', 'linusimon@gmail.com')
    }

    result = LangGraphSupervisor.run_multi_agent_workflow(payload)

    # Log execution in AuditLog
    claims = get_jwt()
    audit = AuditLog(
        user_name=claims.get('username', 'User'),
        user_role=claims.get('role', 'Viewer'),
        action='RUN_AGENT_WORKFLOW',
        target_type='Project',
        target_id=project_code,
        details=f"Executed 3-LangGraph workflow for {project_code}. Risk Score: {result.get('risk_intelligence', {}).get('top_risk_score', 0)}"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({'status': 'success', 'workflow_result': result}), 200

@agents_bp.route('/chat', methods=['POST'])
@jwt_required()
def agent_chat():
    """Interactive Chat Endpoint with Guardrails & Supervisor Routing."""
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    project_code = data.get('project_code', 'PRJ-001')

    if not user_message:
        return jsonify({'error': 'Bad Request', 'message': 'Message is required.'}), 400

    # Run workflow for chat inquiry
    project = Project.query.filter_by(code=project_code.upper()).first()
    project_dict = project.to_dict() if project else {"code": project_code, "lifecycle_phase": "Mobilization"}
    if project:
        project_dict['tasks'] = [t.to_dict() for t in project.tasks]

    comm_data = SlackTeamsEmailAdapter.read_communication_logs(project_code=project_code)

    payload = {
        "user_query": user_message,
        "project_data": project_dict,
        "comm_logs": comm_data.get('logs', []),
        "recipient_role": "Program Manager"
    }

    res = LangGraphSupervisor.run_multi_agent_workflow(payload)

    risk_info = res.get('risk_intelligence', {}).get('primary_raid_item', {})

    response_text = (
        f"I have analyzed **{project_code}** across data feeds, WBS tasks, and static SOP policies.\n\n"
        f"• **Identified RAID Item:** {risk_info.get('title', 'Schedule Alignment')}\n"
        f"• **Category:** {risk_info.get('category', 'Risk')} (Score: {risk_info.get('risk_score', 75)}/100)\n"
        f"• **Root Cause:** {risk_info.get('root_cause', 'Dependency review')}\n"
        f"• **Proposed Mitigation:** {res.get('risk_intelligence', {}).get('proposed_mitigations', [{}])[0].get('title', 'Deploy mock server')}\n\n"
        f"I have created a draft update in the Communication Center awaiting your review and Human Approval."
    )

    return jsonify({
        'status': 'success',
        'response': response_text,
        'graphical_node_traces': res.get('graphical_node_traces', []),
        'confidence_score': res.get('confidence_score', 0.95),
        'token_usage': res.get('token_usage', {}),
        'estimated_cost_usd': res.get('estimated_cost_usd', 0.0)
    }), 200
