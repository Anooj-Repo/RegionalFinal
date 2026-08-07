"""
prompts/graph2_prompts.py
-------------------------
Centralized prompt templates for Graph 2: Decision Intelligence & Risk Assessment Pipeline.
"""

CONTEXT_BUILDER_PROMPT = """
System: You are an Enterprise Program Management AI Assistant.
Task: Synthesize the input ProjectIntelligence state into a structured context summary.

Input Project ID: {project_id}
Health Score: {health_score} ({health_status})
Blocked Tasks: {blocked_tasks}
Signals Detected: {signal_count}

Output: Produce a clear 2-paragraph synthesis of project state, key drivers, and primary areas of concern.
"""

DECISION_PLANNER_PROMPT = """
System: You are a Strategic PMO Planning Assistant.
Task: Based on project context summary and retrieved historical evidence, generate strategic decision priorities.

Context Summary:
{context_summary}

Retrieved Evidence Items ({evidence_count}):
{evidence_titles}

Output: List top 3 strategic decision priorities for project leadership.
"""

RISK_ASSESSMENT_PROMPT = """
System: You are a Senior Risk Assessment Officer.
Task: Evaluate project signals, health drivers, and evidence to categorize enterprise risks.

Signals:
{signals_summary}

Health Drivers:
{health_drivers}

Output: Categorize risks into Vendor Delivery, Timeline Delay, Data Quality, or Compliance Risk.
"""

MITIGATION_PLANNING_PROMPT = """
System: You are a Program Mitigation Planning Specialist.
Task: Draft actionable mitigation plans for each identified risk.

Categorized Risks:
{risks_summary}

Feedback from previous reflection (if any):
{reflection_feedback}

Output: For each risk, specify action title, action description, assigned owner, target due date, and cost estimate.
"""

REFLECTION_PROMPT = """
System: You are a Quality & Grounding Review Auditor.
Task: Evaluate drafted mitigations and risk report for factual grounding, logical consistency, and unsupported claims.

Context Summary:
{context_summary}

Drafted Mitigations:
{mitigations_summary}

Output: Verify grounding score (0.0 - 1.0) and consistency score (0.0 - 1.0). Return passed=true if both >= 0.8 and no unsupported claims.
"""

RISK_REPORT_BUILDER_PROMPT = """
System: You are an Executive Communication Lead.
Task: Assemble all validated risk assessment components into a final executive RiskAssessmentReport.

Project ID: {project_id}
Priority: {priority}
Recommended Escalation: {escalation_level}

Output: Format executive summary, list of categorized risks, supporting evidence, and mitigation action plans.
"""
