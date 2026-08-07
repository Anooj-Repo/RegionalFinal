"""
Dedicated Chat Supervisor Agent (backend/app/agents/chat_supervisor_agent.py)
Streaming chat agent that runs the FULL LangGraph pipeline:
  Node 1: DataIntelligenceGraph  (Guardrails + Dual RAG + GraphRAG)
  Node 2: RiskIntelligenceGraph  (RAID Rule Engine + LLM Scoring)
  Node 3: TCS GenAI LLM          (Grounded reasoning over full state)
  Node 4: MemoryAgent            (Sliding conversation history window)
Yields structured SSE events: status | token | action | done
"""

import time
import json
from typing import Dict, Any, List, Generator

from backend.app.core.tcs_genai_client import TCSGenAIClient
from backend.app.agents.memory_agent import execute_memory_agent
from backend.graphs.data_graph import DataIntelligenceGraph
from backend.graphs.risk_graph import RiskIntelligenceGraph

def _fetch_project_tasks(project_code: str) -> List[Dict[str, Any]]:
    """Fetch tasks for the project from DB so the RAID rule engine can check blocked tasks."""
    try:
        from backend.app.db.models import Task, Project
        project = Project.query.filter_by(code=project_code).first()
        if not project:
            return []
        tasks = Task.query.filter_by(project_id=project.id).all()
        return [{'title': t.title, 'status': t.status, 'phase': t.phase} for t in tasks]
    except Exception:
        return []


# ─── Intent keyword map for action detection ───────────────────────────────────
_ACTION_INTENTS = {
    'ADD_MITIGATION': ['add mitigation', 'create mitigation', 'deploy mock', 'mitigate', 'mitigation action'],
    'CREATE_RAID_ITEM': ['add risk', 'create risk', 'flag issue', 'new risk', 'log a risk', 'raise an issue'],
    'DRAFT_EMAIL': ['draft email', 'send email', 'notify executive', 'escalate', 'stakeholder email'],
    'RUN_WORKFLOW': ['run analysis', 'full analysis', 'run workflow', 'analyze project', 'run langgraph'],
}


def _detect_intent(message: str) -> Dict[str, Any] | None:
    """Detect if user message requests an executable action."""
    msg_lower = message.lower()
    for action_type, keywords in _ACTION_INTENTS.items():
        if any(k in msg_lower for k in keywords):
            return action_type
    return None


def _build_grounded_prompt(
    user_message: str,
    project_code: str,
    user_role: str,
    data_state: Dict[str, Any],
    risk_state: Dict[str, Any],
    conversation_history: List[Dict[str, str]]
) -> tuple[str, str]:
    """
    Build a fully grounded system + user prompt using the LangGraph pipeline state.
    This is what separates enterprise chatbots from simple Q&A bots:
    the LLM answers based on real RAID data, RAG context, and knowledge graph triples.
    """
    # RAG context from DataIntelligenceGraph state
    rag_chunks = data_state.get('retrieved_context', {}).get('static_policy_chunks', [])
    graph_triples = data_state.get('graph_triples_found', [])
    rag_text = '\n'.join(rag_chunks[:3]) if rag_chunks else 'No static policy documents indexed.'
    triples_formatted = []
    for t in (graph_triples if isinstance(graph_triples, list) else []):
        if isinstance(t, dict):
            triples_formatted.append(f"  ({t.get('subject')}) --[{t.get('predicate')}]--> ({t.get('object')})")
        else:
            triples_formatted.append(f"  {t}")
    triples_text = '\n'.join(triples_formatted) or 'No graph triples found.'

    # Risk intelligence state from RiskIntelligenceGraph
    primary_raid = risk_state.get('primary_raid_item', {})
    all_raids = risk_state.get('all_detected_raids', [])
    mitigations = risk_state.get('proposed_mitigations', [])

    raids_text = '\n'.join([
        f"  [{r.get('category')}] {r.get('title')} — Score: {r.get('risk_score')}, "
        f"Likelihood: {r.get('likelihood')}, Impact: {r.get('impact')}"
        for r in all_raids
    ]) or 'No RAID items detected.'

    mitigations_text = '\n'.join([
        f"  • {m.get('title')} (Owner: {m.get('owner')}, Due: {m.get('due_date')})"
        for m in mitigations
    ]) or 'No mitigations proposed.'

    # Conversation history context (multi-turn memory)
    history_text = ''
    if conversation_history:
        history_text = 'Previous conversation turns:\n' + '\n'.join([
            f"  [{t['role'].upper()}]: {t['content']}"
            for t in conversation_history[-6:]  # Last 6 turns max
        ])

    system_prompt = f"""You are the Enterprise Program Management AI Assistant for project {project_code}.
You are speaking to a {user_role}. Tailor your response depth and technical detail accordingly.

GROUNDING RULES:
- Answer ONLY based on the trusted context provided below.
- Do not invent risks, scores, or data not present in the context.
- Be professional, concise, and actionable.
- If asked to perform an action (create risk, add mitigation, draft email), confirm you have proposed it.

=== STATIC RAG POLICY CONTEXT ===
{rag_text}

=== KNOWLEDGE GRAPH TRIPLES (from Slack/Teams/Email feeds) ===
{triples_text}

=== RAID INTELLIGENCE RESULTS (from Risk Intelligence Graph) ===
Primary Risk: {primary_raid.get('title', 'N/A')} (Score: {primary_raid.get('risk_score', 'N/A')})
Root Cause: {primary_raid.get('root_cause', 'N/A')}

All Detected RAID Items:
{raids_text}

Proposed Mitigations:
{mitigations_text}

=== RULES TRIGGERED (RAID Rule Engine) ===
{', '.join(risk_state.get('rules_triggered', ['None']))}

{history_text}"""

    return system_prompt, user_message


def stream_chat_supervisor(
    user_message: str,
    project_code: str = 'PRJ-001',
    project_data: Dict[str, Any] = None,
    conversation_history: List[Dict[str, str]] = None,
    user_role: str = 'Program Manager'
) -> Generator[Dict[str, Any], None, None]:
    """
    Full LangGraph + State + Memory streaming chat generator.

    Yields SSE events:
      {'type': 'status',  'content': str}           — node execution status
      {'type': 'token',   'content': str}           — streamed LLM token
      {'type': 'action',  'action': dict}           — proposed HITL action card
      {'type': 'done',    'telemetry': dict}        — final metrics + node traces
    """
    start_time = time.time()
    tcs_client = TCSGenAIClient()
    conversation_history = conversation_history or []
    project_data = project_data or {'code': project_code, 'lifecycle_phase': 'Execution'}
    # Fix #4: Fetch real task data so Rule 1 (blocked tasks) can fire in RiskIntelligenceGraph
    if 'tasks' not in project_data or not project_data.get('tasks'):
        project_data['tasks'] = _fetch_project_tasks(project_code)
    node_traces = []

    # ── NODE 1: DataIntelligenceGraph ─────────────────────────────────────────
    yield {'type': 'status', 'content': '🛡️ Node 1: Running Security Guardrails & Dual RAG...'}
    t1 = time.time()
    data_input = {
        'raw_input': user_message,
        'project_code': project_code,
        'comm_logs': []
    }
    data_state = DataIntelligenceGraph.execute(data_input)
    t1_ms = max(int((time.time() - t1) * 1000), 1)

    node_traces.append({
        'name': '1. Data Intelligence Graph',
        'status': data_state['status'],
        'latency_ms': t1_ms,
        'details': {
            'pii_masked': data_state.get('pii_masked', False),
            'static_chunks': data_state.get('static_chunks_retrieved', 0),
            'graph_triples': len(data_state.get('graph_triples_found', []) or [])
        }
    })

    if data_state['status'] == 'BLOCKED':
        yield {'type': 'status', 'content': '❌ Security Guardrails blocked this request.'}
        yield {'type': 'token', 'content': f"⚠️ Request blocked: {data_state.get('reason', 'Security violation detected.')}"}
        yield {'type': 'done', 'telemetry': {'status': 'BLOCKED', 'node_traces': node_traces}}
        return

    yield {'type': 'status', 'content': f'✅ Node 1 complete — {data_state.get("static_chunks_retrieved", 0)} RAG chunks, {len(data_state.get("graph_triples_found") or [])} graph triples retrieved'}

    # ── NODE 2: RiskIntelligenceGraph ─────────────────────────────────────────
    yield {'type': 'status', 'content': '⚠️ Node 2: Running RAID Rule Engine & Risk Intelligence...'}
    t2 = time.time()
    risk_input = {
        'data_graph_output': data_state,
        'project_data': project_data
    }
    risk_state = RiskIntelligenceGraph.execute(risk_input)
    t2_ms = max(int((time.time() - t2) * 1000), 1)

    node_traces.append({
        'name': '2. Risk Intelligence Graph (RAID Engine)',
        'status': risk_state['status'],
        'latency_ms': t2_ms,
        'details': {
            'rules_triggered': risk_state.get('rules_triggered', []),
            'top_risk_score': risk_state.get('top_risk_score', 0),
            'primary_raid': risk_state.get('primary_raid_item', {}).get('title', 'N/A')
        }
    })

    top_score = risk_state.get('top_risk_score', 0)
    primary = risk_state.get('primary_raid_item', {}).get('title', 'N/A')
    yield {'type': 'status', 'content': f'✅ Node 2 complete — Top risk score: {top_score}, Primary RAID: {primary}'}

    # ── ACTION INTENT DETECTION ───────────────────────────────────────────────
    intent = _detect_intent(user_message)
    if intent == 'ADD_MITIGATION':
        yield {'type': 'action', 'action': {
            'action_type': 'ADD_MITIGATION',
            'title': f'Mitigation: {risk_state.get("primary_raid_item", {}).get("title", "Critical Risk")}',
            'description': f'Proposed mitigation generated from chat for {project_code}.',
            'raid_id': 1,
            'owner_name': 'Technical Lead',
            'due_date': 'Next 5 Days',
            'status': 'In Progress'
        }}
    elif intent == 'CREATE_RAID_ITEM':
        yield {'type': 'action', 'action': {
            'action_type': 'CREATE_RAID_ITEM',
            'title': f'Risk flagged via Chat — {project_code}',
            'description': user_message,
            'category': 'Risk',
            'likelihood': 'High',
            'impact': 'High',
            'risk_score': 85,
            'project_id': 1
        }}
    elif intent == 'DRAFT_EMAIL':
        yield {'type': 'action', 'action': {
            'action_type': 'DRAFT_EMAIL',
            'recipient_role': 'Executive',
            'recipient_email': 'linusimon@gmail.com',
            'subject': f'Executive Alert: {project_code} Risk & Schedule Update',
            'body': f'Top risk: {primary} (Score: {top_score}). Mitigation actions are pending review.'
        }}
    elif intent == 'RUN_WORKFLOW':
        yield {'type': 'action', 'action': {
            'action_type': 'RUN_WORKFLOW',
            'title': f'Run Full 3-Graph RAID Workflow for {project_code}',
            'description': 'Triggers Data Intelligence → Risk Intelligence → Communication Graph pipeline.',
            'project_code': project_code
        }}

    # ── NODE 3: LLM Grounded Reasoning ───────────────────────────────────────
    yield {'type': 'status', 'content': '🤖 Node 3: Generating grounded LLM response...'}
    t3 = time.time()

    system_prompt, user_prompt = _build_grounded_prompt(
        user_message, project_code, user_role,
        data_state, risk_state, conversation_history
    )

    llm_res = tcs_client.generate_completion(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.2
    )
    t3_ms = max(int((time.time() - t3) * 1000), 1)
    full_text = llm_res.get('content', '')

    node_traces.append({
        'name': '3. LLM Grounded Reasoning (TCS GenAI)',
        'status': 'COMPLETED',
        'latency_ms': t3_ms,
        'details': {
            'model': llm_res.get('model'),
            'tokens': llm_res.get('usage', {}).get('total_tokens', 0),
            'cost_usd': llm_res.get('cost_usd', 0)
        }
    })

    # Stream tokens word by word for smooth UX
    words = full_text.split(' ')
    for i, word in enumerate(words):
        yield {'type': 'token', 'content': word + ('' if i == len(words) - 1 else ' ')}

    # ── NODE 4: MemoryAgent ───────────────────────────────────────────────────
    t4 = time.time()
    mem_result = execute_memory_agent(project_code, user_message, {
        'risk_intelligence': risk_state,
        'communication': {'created_draft_id': None},
        # Fix #3: store the assistant reply so multi-turn context is coherent
        'assistant_reply': full_text
    })
    t4_ms = max(int((time.time() - t4) * 1000), 1)

    node_traces.append({
        'name': '4. Memory Agent (Conversation Window)',
        'status': mem_result['status'],
        'latency_ms': t4_ms,
        'details': {
            'stored_entries': mem_result.get('stored_entries_count', 0),
            'window_size': len(mem_result.get('recent_context_window', []))
        }
    })

    total_ms = max(int((time.time() - start_time) * 1000), 1)

    yield {
        'type': 'done',
        'telemetry': {
            'status': 'SUCCESS',
            'total_latency_ms': total_ms,
            'model_used': llm_res.get('model', 'gemini-1.5-pro'),
            'usage': llm_res.get('usage', {}),
            'cost_usd': llm_res.get('cost_usd', 0),
            'confidence_score': risk_state.get('reflection_validation', {}).get('confidence_score', 0.94),
            'top_risk_score': risk_state.get('top_risk_score', 0),
            'node_traces': node_traces,
            'memory_window': mem_result.get('stored_entries_count', 0)
        }
    }


def run_chat_supervisor(user_message: str, project_code: str = 'PRJ-001') -> Dict[str, Any]:
    """Legacy synchronous wrapper — preserved for backward compatibility with /api/agents/chat."""
    chunks = list(stream_chat_supervisor(user_message, project_code))
    text = ''.join(c['content'] for c in chunks if c['type'] == 'token')
    done = next((c for c in chunks if c['type'] == 'done'), {})
    return {
        'status': 'SUCCESS',
        'response': text,
        'telemetry': done.get('telemetry', {})
    }

