"""
graphs/graph1/graph.py
----------------------
Sequential LangGraph definition for Graph 1: Knowledge Intelligence Pipeline.
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from graphs.graph1.state import Graph1State
from graphs.graph1.nodes import (
    normalize_node,
    entity_extraction_node,
    relationship_extraction_node,
    metadata_enrichment_node,
    chunking_node,
    embedding_node,
    knowledge_bundle_node,
)


def create_graph1() -> StateGraph:
    """
    Construct the sequential Graph 1 workflow graph.
    """
    builder = StateGraph(Graph1State)

    # 1. Add nodes
    builder.add_node("normalize", normalize_node)
    builder.add_node("entity_extraction", entity_extraction_node)
    builder.add_node("relationship_extraction", relationship_extraction_node)
    builder.add_node("metadata_enrichment", metadata_enrichment_node)
    builder.add_node("chunking", chunking_node)
    builder.add_node("embedding", embedding_node)
    builder.add_node("knowledge_bundle", knowledge_bundle_node)

    # 2. Add sequential edges
    builder.add_edge(START, "normalize")
    builder.add_edge("normalize", "entity_extraction")
    builder.add_edge("entity_extraction", "relationship_extraction")
    builder.add_edge("relationship_extraction", "metadata_enrichment")
    builder.add_edge("metadata_enrichment", "chunking")
    builder.add_edge("chunking", "embedding")
    builder.add_edge("embedding", "knowledge_bundle")
    builder.add_edge("knowledge_bundle", END)

    return builder.compile()


# Module singleton graph instance
graph1 = create_graph1()
