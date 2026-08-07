"""
Graph 1: Data Intelligence Graph (backend/graphs/data_graph.py)
Workflow: Input Ingestion -> Normalization & PII Guardrails -> Dual RAG Indexing & Knowledge Graph Extraction.
"""

import os
import sys
from typing import Dict, Any, List

# Add parent path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app.core.guardrails import SecurityGuardrails
from backend.app.rag.rag_engine import global_rag_engine

class DataIntelligenceGraph:
    """Data Intelligence LangGraph Workflow Node."""

    @staticmethod
    def execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes data ingestion, PII masking, and dual RAG indexing.
        """
        raw_text = input_data.get('raw_input', '')
        project_code = input_data.get('project_code', 'PRJ-001')
        comm_logs = input_data.get('comm_logs', [])

        # 1. Execute Security Guardrails
        guardrail_res = SecurityGuardrails.process_input_guardrails(raw_text)
        if not guardrail_res['passed']:
            return {
                "graph": "Data Intelligence Graph",
                "status": "BLOCKED",
                "reason": guardrail_res['reason'],
                "sanitized_input": "",
                "pii_masked": False
            }

        sanitized_input = guardrail_res['sanitized_text']

        # 2. Ensure Static RAG is loaded from uploads
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app/uploads'))
        global_rag_engine.load_static_documents(uploads_dir)

        # 3. Index Unstructured Communication Stream & Build Knowledge Graph
        if comm_logs:
            global_rag_engine.index_unstructured_stream(comm_logs)

        # 4. Perform Retrieval for Context
        static_context = global_rag_engine.retrieve_static_context(sanitized_input, top_k=2)
        unstructured_context = global_rag_engine.retrieve_unstructured_context(sanitized_input, project_code=project_code, top_k=2)
        graph_triples = global_rag_engine.search_knowledge_graph(project_code=project_code)

        return {
            "graph": "Data Intelligence Graph",
            "status": "COMPLETED",
            "sanitized_input": sanitized_input,
            "pii_masked": guardrail_res['pii_masked'],
            "masked_entities_count": guardrail_res['masked_entities_count'],
            "static_chunks_retrieved": len(static_context),
            "unstructured_nodes_retrieved": len(unstructured_context),
            "graph_triples_found": graph_triples,
            "retrieved_context": {
                "static_policy_chunks": [c['content'][:200] + '...' for c in static_context],
                "unstructured_comm_chats": [n['content'] for n in unstructured_context]
            }
        }
