"""
schemas/domain/reports.py
--------------------------
Pydantic domain schemas for StatusReport.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from schemas.base import BaseEntity, BaseTimestampModel


# ===========================================================================
# StatusReport
# ===========================================================================

class StatusReportCreateSchema(BaseTimestampModel):
    """Input schema for submitting a status report."""

    project_id:       int
    reporting_period: str         = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Period label, e.g. '2026-W32' or 'August 2026'.",
    )
    accomplishments: list[str]    = Field(
        default_factory=list,
        description="What was completed this period.",
    )
    blockers:        list[str]    = Field(
        default_factory=list,
        description="Current blockers preventing progress.",
    )
    risks:           list[str]    = Field(
        default_factory=list,
        description="High-level risk summaries for this period.",
    )
    next_steps:      list[str]    = Field(
        default_factory=list,
        description="Planned actions for the next period.",
    )


class StatusReportUpdateSchema(BaseTimestampModel):
    """Partial update schema for a status report."""

    reporting_period: Optional[str]       = None
    accomplishments:  Optional[list[str]] = None
    blockers:         Optional[list[str]] = None
    risks:            Optional[list[str]] = None
    next_steps:       Optional[list[str]] = None


class StatusReportSchema(BaseEntity):
    """Full status report response schema."""

    project_id:       int
    reporting_period: str
    accomplishments:  list[str]  = Field(default_factory=list)
    blockers:         list[str]  = Field(default_factory=list)
    risks:            list[str]  = Field(default_factory=list)
    next_steps:       list[str]  = Field(default_factory=list)

    @property
    def has_blockers(self) -> bool:
        """True if any blockers are listed."""
        return bool(self.blockers)

    @property
    def has_risks(self) -> bool:
        """True if any risks are listed."""
        return bool(self.risks)
