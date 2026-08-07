"""
schemas/domain/snapshot.py
---------------------------
ProjectSnapshot — Canonical enterprise domain snapshot of a project state.

This object represents the complete, immutable state of an enterprise project
at a specific point in time. It is the canonical business object passed into Graph 1.

Groupings:
    - Project Metadata (snapshot_id, project)
    - Execution Data (tasks, stakeholders)
    - Communication Data (emails, chat_messages, meeting_notes, status_reports)
    - Knowledge Data (risk_register, historical_projects)
    - Snapshot Metadata (snapshot_timestamp, project_version)
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field

from schemas.domain.project import (
    ProjectSchema,
    ProjectTaskSchema,
    StakeholderSchema,
)
from schemas.domain.communications import (
    EmailDocumentSchema,
    ChatMessageSchema,
    MeetingNoteSchema,
)
from schemas.domain.reports import StatusReportSchema
from schemas.domain.risks import RiskEntrySchema
from schemas.domain.historical import HistoricalProjectSchema


class ProjectSnapshot(BaseModel):
    """
    Enterprise snapshot of a project's state at a point in time.

    Canonical business input contract for Graph 1 workflows.
    Immutable once constructed.
    """

    model_config = ConfigDict(
        frozen=True,            # immutable — workflows must not mutate snapshots
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    # ── Project Metadata ──────────────────────────────────────────────────────
    snapshot_id: UUID = Field(
        default_factory=uuid4,
        description="Unique UUID for this specific snapshot instance.",
    )
    project: ProjectSchema = Field(
        ...,
        description="The core project domain entity. Required.",
    )

    # ── Execution Data ────────────────────────────────────────────────────────
    tasks: list[ProjectTaskSchema] = Field(
        default_factory=list,
        description="All tasks associated with the project.",
    )
    stakeholders: list[StakeholderSchema] = Field(
        default_factory=list,
        description="Registered project stakeholders.",
    )

    # ── Communication Data ────────────────────────────────────────────────────
    emails: list[EmailDocumentSchema] = Field(
        default_factory=list,
        description="Ingested email documents related to the project.",
    )
    chat_messages: list[ChatMessageSchema] = Field(
        default_factory=list,
        description="Ingested chat messages related to the project.",
    )
    meeting_notes: list[MeetingNoteSchema] = Field(
        default_factory=list,
        description="Meeting notes captured for the project.",
    )
    status_reports: list[StatusReportSchema] = Field(
        default_factory=list,
        description="Periodic status reports for the project.",
    )

    # ── Knowledge Data ────────────────────────────────────────────────────────
    risk_register: list[RiskEntrySchema] = Field(
        default_factory=list,
        description="Risk entries logged for the project.",
    )
    historical_projects: list[HistoricalProjectSchema] = Field(
        default_factory=list,
        description="Historical projects for benchmarking and lessons learned.",
    )

    # ── Snapshot Metadata ─────────────────────────────────────────────────────
    snapshot_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when this project snapshot was captured.",
    )
    project_version: str = Field(
        default="1.0.0",
        description="Version string for the project state.",
    )

    # ── Convenience Properties ────────────────────────────────────────────────

    @property
    def total_documents(self) -> int:
        """Total number of communication/document items in this snapshot."""
        return len(self.emails) + len(self.chat_messages) + len(self.meeting_notes)

    @property
    def open_risks(self) -> list[RiskEntrySchema]:
        """Filter risk register to open risks only."""
        return [r for r in self.risk_register if r.status.value == "open"]

    @property
    def blocked_tasks(self) -> list[ProjectTaskSchema]:
        """Filter tasks to those currently blocked."""
        return [t for t in self.tasks if t.status.value == "blocked"]

    @property
    def is_empty(self) -> bool:
        """True if no domain items beyond the project itself have been loaded."""
        return (
            not self.tasks
            and not self.stakeholders
            and not self.emails
            and not self.chat_messages
            and not self.meeting_notes
            and not self.status_reports
            and not self.risk_register
            and not self.historical_projects
        )

    def summary(self) -> dict:
        """
        Return a lightweight summary dict for logging and telemetry.
        """
        return {
            "snapshot_id":         str(self.snapshot_id),
            "project_id":          self.project.project_id,
            "project_name":        self.project.name,
            "tasks":               len(self.tasks),
            "stakeholders":        len(self.stakeholders),
            "emails":              len(self.emails),
            "chat_messages":       len(self.chat_messages),
            "meeting_notes":       len(self.meeting_notes),
            "status_reports":      len(self.status_reports),
            "risk_register":       len(self.risk_register),
            "open_risks":          len(self.open_risks),
            "blocked_tasks":       len(self.blocked_tasks),
            "historical_projects": len(self.historical_projects),
            "total_documents":     self.total_documents,
            "snapshot_timestamp":  self.snapshot_timestamp.isoformat(),
            "project_version":     self.project_version,
        }
