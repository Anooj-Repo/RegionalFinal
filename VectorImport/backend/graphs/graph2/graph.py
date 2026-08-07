"""
graphs/graph2/graph.py
----------------------
LangGraph definition for Graph 2: Decision Intelligence & Risk Assessment Pipeline.

Features a sequential workflow with a Reflection Loop.
"""

from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from graphs.graph2.state import Graph2State
from graphs.graph2.nodes import (
    context_builder_node,
    evidence_collector_node,
    decision_planner_node,
    risk_assessment_node,
    mitigation_planning_node,
    reflection_node,
    risk_report_builder_node,
)


def route_after_reflection(state: Graph2State) -> str:
    """
    Conditional routing edge after ReflectionNode.

    If reflection failed AND retry_count < max_retries, loop back to mitigation_planning.
    Otherwise, proceed to risk_report_builder.
    """
    feedback = state.get("reflection_feedback")
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    if feedback and not feedback.passed and retry_count <= max_retries:
        return "mitigation_planning"

    return "risk_report_builder"


def create_graph2() -> StateGraph:
    """
    Construct the Graph 2 workflow graph with Reflection Loop.
    """
    builder = StateGraph(Graph2State)

    # 1. Add nodes
    builder.add_node("context_builder", context_builder_node)
    builder.add_node("evidence_collector", evidence_collector_node)
    builder.add_node("decision_planner", decision_planner_node)
    builder.add_node("risk_assessment", risk_assessment_node)
    builder.add_node("mitigation_planning", mitigation_planning_node)
    builder.add_node("reflection", reflection_node)
    builder.add_node("risk_report_builder", risk_report_builder_node)

    # 2. Add fixed sequential edges
    builder.add_edge(START, "context_builder")
    builder.add_edge("context_builder", "evidence_collector")
    builder.add_edge("evidence_collector", "decision_planner")
    builder.add_edge("decision_planner", "risk_assessment")
    builder.add_edge("risk_assessment", "mitigation_planning")
    builder.add_edge("mitigation_planning", "reflection")

    # 3. Add conditional edge for Reflection Loop
    builder.add_conditional_edges(
        "reflection",
        route_after_reflection,
        {
            "mitigation_planning": "mitigation_planning",
            "risk_report_builder": "risk_report_builder",
        },
    )

    builder.add_edge("risk_report_builder", END)

    return builder.compile()


# Module singleton graph instance
graph2 = create_graph2()
