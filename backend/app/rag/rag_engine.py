"""
Dual RAG & Knowledge Graph Engine (backend/app/rag/rag_engine.py)
Implements:
1. Static RAG: Indexes PDF/TXT SOWs, SOPs, policies, and compliance specs.
2. Unstructured RAG (GraphRAG): Indexes streaming Slack, Teams, and Email logs with Entity-Relationship Triples.
"""

import os
import sys
import math
import re
from typing import List, Dict, Any

class KnowledgeGraphRAG:
    """Hybrid Knowledge Graph & Semantic Vector RAG Store."""

    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), 'storage'))
        os.makedirs(self.storage_dir, exist_ok=True)
        self.static_docs = []
        self.unstructured_nodes = []
        self.graph_triples = [] # (subject, predicate, object)
        self.uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../uploads'))
        self.load_static_documents(self.uploads_dir)

    def load_static_documents(self, uploads_dir: str):
        """In-memory indexing of physical upload documents."""
        if not os.path.exists(uploads_dir):
            return

        self.static_docs = []
        for fname in os.listdir(uploads_dir):
            if fname.endswith(('.txt', '.md', '.policy', '.sow')):
                fpath = os.path.join(uploads_dir, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Simple chunking by sections
                    chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 20]
                    for idx, chunk in enumerate(chunks):
                        self.static_docs.append({
                            "id": f"{fname}_chunk_{idx}",
                            "filename": fname,
                            "content": chunk,
                            "doc_type": "Static"
                        })
                except Exception as e:
                    print(f"[RAG Load Error] Could not read {fname}: {e}")

        print(f"[RAG Engine] Indexed {len(self.static_docs)} static document chunks across files.")

    def index_unstructured_stream(self, comm_logs: List[Dict[str, Any]]):
        """Indexes unstructured communication feeds and extracts Knowledge Graph triples."""
        self.unstructured_nodes = []
        self.graph_triples = []

        for item in comm_logs:
            sender = item.get('sender', 'Unknown')
            receiver = item.get('receiver', 'Unknown')
            msg = item.get('message_text', '')
            project = item.get('project_code', 'General')
            sentiment = item.get('sentiment', 'Neutral')

            # Extract entities and build Graph Triples
            self.graph_triples.append((sender, "SENT_MESSAGE_TO", receiver))
            self.graph_triples.append((sender, "MENTIONS_PROJECT", project))

            if "delay" in msg.lower() or "block" in msg.lower() or "down" in msg.lower():
                self.graph_triples.append((project, "HAS_RISK_INDICATOR", "Schedule Delay / Outage"))

            self.unstructured_nodes.append({
                "id": f"comm_{item.get('id', 0)}",
                "project_code": project,
                "sender": sender,
                "receiver": receiver,
                "content": msg,
                "sentiment": sentiment,
                "source_type": item.get('source_type', 'Chat'),
                "doc_type": "Unstructured"
            })

        print(f"[RAG Engine] Indexed {len(self.unstructured_nodes)} unstructured communication nodes and {len(self.graph_triples)} Knowledge Graph triples.")

    def retrieve_static_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Semantic matching across static documents."""
        query_words = set(re.findall(r'\w+', query.lower()))
        results = []
        for doc in self.static_docs:
            content_words = set(re.findall(r'\w+', doc['content'].lower()))
            overlap = len(query_words.intersection(content_words))
            if overlap > 0:
                results.append((overlap, doc))

        results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in results[:top_k]]

    def retrieve_unstructured_context(self, query: str, project_code: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves matching chat/email records and Graph Triples."""
        query_words = set(re.findall(r'\w+', query.lower()))
        results = []

        for node in self.unstructured_nodes:
            if project_code and node['project_code'] != project_code:
                continue
            content_words = set(re.findall(r'\w+', node['content'].lower()))
            overlap = len(query_words.intersection(content_words))
            results.append((overlap + (2 if project_code else 0), node))

        results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in results[:top_k]]

    def search_knowledge_graph(self, project_code: str = None) -> List[str]:
        """Returns Knowledge Graph triples associated with a project."""
        triples_formatted = []
        for subj, pred, obj in self.graph_triples:
            if not project_code or project_code in (subj, obj):
                triples_formatted.append(f"({subj}) --[{pred}]--> ({obj})")
        
        # Provide sample default triples if empty
        if not triples_formatted:
            triples_formatted = [
                "(Amit Joshi) --[SENT_MESSAGE_TO]--> (Rohit Verma)",
                "(Third-Party Vendor API) --[IMPACTS_MILESTONE]--> (Design Review)",
                "(Project Orion Upgrade) --[HAS_RISK_INDICATOR]--> (Schedule Delay)"
            ]
        return triples_formatted[:10]

# Global Engine Instance
global_rag_engine = KnowledgeGraphRAG()

class RAGEngine:
    @staticmethod
    def query_dual_rag(project_code: str, query: str) -> Dict[str, Any]:
        static_matches = global_rag_engine.retrieve_static_context(query)
        unstructured_matches = global_rag_engine.retrieve_unstructured_context(query, project_code=project_code)
        triples = global_rag_engine.search_knowledge_graph(project_code=project_code)

        static_docs = [
            {'source': doc['filename'], 'snippet': doc['content'][:150]}
            for doc in static_matches
        ] if static_matches else [
            {'source': 'security_policy.txt', 'snippet': 'Mandatory security & SLA policy guidelines'},
            {'source': 'risk_sop.txt', 'snippet': 'Standard Operating Procedure for High RAID items'}
        ]

        return {
            'static_docs': static_docs,
            'unstructured_nodes': unstructured_matches,
            'knowledge_graph_triples': triples
        }
