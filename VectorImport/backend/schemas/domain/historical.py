"""
schemas/domain/historical.py
-----------------------------
Pydantic domain schemas for HistoricalProject.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from schemas.base import BaseEntity, BaseTimestampModel


# ===========================================================================
# HistoricalProject
# ===========================================================================

class HistoricalRisk(BaseTimestampModel):
    """A risk entry stored inside a historical project record."""

    title:      str
    probability: str
    impact:     str
    mitigation: Optional[str] = None
    outcome:    Optional[str] = None


class HistoricalProjectCreateSchema(BaseTimestampModel):
    """Input schema for archiving a completed project."""

    project_name:           str                     = Field(..., min_length=1, max_length=255)
    lessons_learned:        list[str]               = Field(
        default_factory=list,
        description="Key lessons that should inform future projects.",
    )
    historical_risks:       list[HistoricalRisk]    = Field(
        default_factory=list,
        description="Risks that were encountered and how they resolved.",
    )
    successful_mitigations: list[str]               = Field(
        default_factory=list,
        description="Mitigation strategies that worked well.",
    )


class HistoricalProjectUpdateSchema(BaseTimestampModel):
    """Partial update for a historical project record."""

    project_name:           Optional[str]                   = None
    lessons_learned:        Optional[list[str]]             = None
    historical_risks:       Optional[list[HistoricalRisk]]  = None
    successful_mitigations: Optional[list[str]]             = None


class HistoricalProjectSchema(BaseEntity):
    """Full historical project response schema."""

    project_name:           str
    lessons_learned:        list[str]             = Field(default_factory=list)
    historical_risks:       list[HistoricalRisk]  = Field(default_factory=list)
    successful_mitigations: list[str]             = Field(default_factory=list)

    @property
    def risk_count(self) -> int:
        """Number of historical risks recorded."""
        return len(self.historical_risks)

    @property
    def lesson_count(self) -> int:
        """Number of lessons learned recorded."""
        return len(self.lessons_learned)
