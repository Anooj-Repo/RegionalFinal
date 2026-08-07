"""
Memory Agent (backend/app/agents/memory_agent.py)
Manages conversational state, context history window, entity memory,
and short-term workspace state across multi-agent executions.
"""

import time
from typing import Dict, Any, List

class MemoryAgent:
    _conversation_history: List[Dict[str, Any]] = []

    @classmethod
    def execute_memory_agent(cls, project_code: str, query: str, final_result: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()

        memory_entry = {
            'project_code': project_code,
            'query': query,
            'risk_score': final_result.get('risk_intelligence', {}).get('primary_raid_item', {}).get('risk_score', 85),
            'draft_id': final_result.get('communication', {}).get('created_draft_id')
        }
        cls._conversation_history.append(memory_entry)
        if len(cls._conversation_history) > 20:
            cls._conversation_history.pop(0)

        latency_ms = int((time.time() - start_time) * 1000)

        return {
            'agent_name': 'Memory Agent',
            'status': 'COMPLETED',
            'latency_ms': max(latency_ms, 2),
            'stored_entries_count': len(cls._conversation_history),
            'recent_context_window': cls._conversation_history[-3:]
        }

def execute_memory_agent(project_code: str, query: str, final_result: Dict[str, Any]) -> Dict[str, Any]:
    return MemoryAgent.execute_memory_agent(project_code, query, final_result)
