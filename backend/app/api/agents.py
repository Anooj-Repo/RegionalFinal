"""
Agent REST API Blueprint (backend/app/api/agents.py)
Routes agent workflow triggers and chat requests to backend.app.agents module.
"""

import json
from flask import Blueprint, request, jsonify, Response, stream_with_context
from backend.app.api.auth import role_required
from backend.app.agents import run_supervisor_workflow, run_chat_supervisor, stream_chat_supervisor

agents_bp = Blueprint('agents', __name__, url_prefix='/api/agents')


@agents_bp.after_request
def add_cors_headers(response):
    """Allow browser SSE streaming and standard CORS."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response


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


@agents_bp.route('/chat-stream', methods=['POST', 'OPTIONS'])
@role_required(['Admin', 'Program Manager', 'Project Manager', 'Team Lead', 'Executive', 'Viewer'])
def chat_stream_api():
    """
    Server-Sent Events (SSE) streaming endpoint for the enterprise chat workspace.
    Runs full LangGraph pipeline: DataIntelligenceGraph → RiskIntelligenceGraph → LLM → MemoryAgent.
    Accepts:
      message             (str)  — user query
      project_code        (str)  — e.g. 'PRJ-001'
      project_data        (dict) — optional project metadata for RAID engine
      conversation_history (list) — [{role, content}, ...] last N turns
      user_role           (str)  — from JWT for RBAC-aware prompting
    """
    if request.method == 'OPTIONS':
        return Response(status=200)

    data = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        def empty_gen():
            yield f"data: {json.dumps({'type': 'done', 'telemetry': {'status': 'ERROR', 'error': 'Message cannot be empty.'}})}\n\n"
        return Response(stream_with_context(empty_gen()), mimetype='text/event-stream')
    project_code = data.get('project_code', 'PRJ-001')
    project_data = data.get('project_data', {'code': project_code, 'lifecycle_phase': 'Execution'})
    conversation_history = data.get('conversation_history', [])
    user_role = data.get('user_role', 'Program Manager')

    def generate():
        try:
            for event in stream_chat_supervisor(
                user_message=message,
                project_code=project_code,
                project_data=project_data,
                conversation_history=conversation_history,
                user_role=user_role
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            error_event = {'type': 'done', 'telemetry': {'status': 'ERROR', 'error': str(e)}}
            yield f"data: {json.dumps(error_event)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

