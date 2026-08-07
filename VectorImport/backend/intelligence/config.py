"""
intelligence/config.py
----------------------
Configuration-driven thresholds and weights for the Intelligence Engine.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class IntelligenceConfig(BaseModel):
    """
    Configuration parameters for health scoring, risk thresholds, and signal evaluation.
    """

    model_config = ConfigDict(frozen=True)

    # ── Health Score Thresholds (0-100) ──────────────────────────────────────
    healthy_min_score: float = Field(default=80.0, description="Score at or above which a project is HEALTHY.")
    at_risk_min_score: float = Field(default=50.0, description="Score at or above which a project is AT_RISK.")

    # ── Deductions & Weights ──────────────────────────────────────────────────
    blocked_task_deduction: float = Field(default=15.0, description="Score deduction per blocked task.")
    critical_risk_deduction: float = Field(default=20.0, description="Score deduction per critical risk.")
    high_risk_deduction: float = Field(default=10.0, description="Score deduction per high risk.")
    urgent_sentiment_deduction: float = Field(default=5.0, description="Score deduction per urgent document.")
    escalation_deduction: float = Field(default=8.0, description="Score deduction per formal escalation.")

    # ── Velocity & Density Thresholds ─────────────────────────────────────────
    critical_blocker_density: float = Field(default=0.2, description="Blocker density ratio above which alert triggers.")
