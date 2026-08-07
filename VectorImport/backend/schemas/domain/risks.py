"""
schemas/domain/risks.py
-----------------------
Pydantic domain schemas for RiskEntry.
"""

from __future__ import annotations

from typing import Optional
from enum import Enum

from pydantic import Field

from schemas.base import BaseEntity, BaseTimestampModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RiskProbability(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


class RiskImpact(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


class RiskStatus(str, Enum):
    OPEN      = "open"
    MITIGATED = "mitigated"
    ACCEPTED  = "accepted"
    CLOSED    = "closed"


# ===========================================================================
# RiskEntry
# ===========================================================================

class RiskEntryCreateSchema(BaseTimestampModel):
    """Input schema for logging a new risk."""

    project_id:  int
    title:       str                  = Field(..., min_length=1, max_length=255)
    probability: RiskProbability      = RiskProbability.MEDIUM
    impact:      RiskImpact           = RiskImpact.MEDIUM
    owner:       Optional[str]        = Field(default=None, max_length=128)
    mitigation:  Optional[str]        = None
    status:      RiskStatus           = RiskStatus.OPEN


class RiskEntryUpdateSchema(BaseTimestampModel):
    """Partial update schema for a risk entry."""

    title:       Optional[str]              = None
    probability: Optional[RiskProbability]  = None
    impact:      Optional[RiskImpact]       = None
    owner:       Optional[str]              = None
    mitigation:  Optional[str]              = None
    status:      Optional[RiskStatus]       = None


class RiskEntrySchema(BaseEntity):
    """Full risk entry response schema."""

    project_id:  int
    title:       str
    probability: RiskProbability
    impact:      RiskImpact
    owner:       Optional[str]  = None
    mitigation:  Optional[str]  = None
    status:      RiskStatus

    @property
    def risk_score(self) -> str:
        """
        Simple qualitative risk score:
            probability × impact → LOW / MEDIUM / HIGH / CRITICAL
        """
        _p = {"low": 1, "medium": 2, "high": 3}
        _i = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        score = _p[self.probability.value] * _i[self.impact.value]
        if score <= 2:   return "LOW"
        if score <= 6:   return "MEDIUM"
        if score <= 9:   return "HIGH"
        return "CRITICAL"
