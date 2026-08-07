"""
services/data_source_registry.py
----------------------------------
DataSourceRegistry — the ONLY class Flask routes should call.

Responsibility:
    Orchestrate all adapters, assemble a ProjectSnapshot,
    and return it to the caller.

Flask never touches adapters directly.
Graph 1 receives ONLY a ProjectSnapshot.

Flow:
    registry.load_project(project_id)
         │
         ├── ProjectPlanAdapter.load()   → ProjectSchema
         ├── TaskAdapter.load()          → list[ProjectTaskSchema]
         ├── StakeholderAdapter.load()   → list[StakeholderSchema]
         ├── EmailAdapter.load()         → list[EmailDocumentSchema]
         ├── ChatAdapter.load()          → list[ChatMessageSchema]
         ├── MeetingNoteAdapter.load()   → list[MeetingNoteSchema]
         ├── StatusReportAdapter.load()  → list[StatusReportSchema]
         ├── RiskRegisterAdapter.load()  → list[RiskEntrySchema]
         └── LessonsLearnedAdapter.load()→ list[HistoricalProjectSchema]
                  │
                  └──► ProjectSnapshot   (handed to Graph 1)

Failure policy:
    - ProjectPlanAdapter failure → raise immediately (no project = no snapshot)
    - All other adapters          → log warning, return empty list (graceful degradation)
"""

from __future__ import annotations

from typing import Callable, TypeVar

from adapters import (
    ChatAdapter,
    EmailAdapter,
    LessonsLearnedAdapter,
    MeetingNoteAdapter,
    ProjectPlanAdapter,
    RiskRegisterAdapter,
    StakeholderAdapter,
    StatusReportAdapter,
    TaskAdapter,
)
from exceptions import AdapterError, ProjectNotFoundError
from schemas.domain.snapshot import ProjectSnapshot
from utils.logger import get_logger

T = TypeVar("T")

_log = get_logger("services.data_source_registry")


class DataSourceRegistry:
    """
    Assembles a ProjectSnapshot from all data-source adapters.

    Usage (Flask route / Graph 1 entry):
        registry = DataSourceRegistry()
        snapshot = registry.load_project(project_id)
        result   = graph1.run(snapshot)
    """

    def __init__(
        self,
        *,
        project_adapter:     ProjectPlanAdapter     | None = None,
        task_adapter:        TaskAdapter            | None = None,
        stakeholder_adapter: StakeholderAdapter     | None = None,
        email_adapter:       EmailAdapter           | None = None,
        chat_adapter:        ChatAdapter            | None = None,
        meeting_adapter:     MeetingNoteAdapter     | None = None,
        status_adapter:      StatusReportAdapter    | None = None,
        risk_adapter:        RiskRegisterAdapter    | None = None,
        lessons_adapter:     LessonsLearnedAdapter  | None = None,
    ) -> None:
        """
        All adapters are injectable for testing.
        Default to mock/file implementations when not provided.
        """
        self._project_adapter      = project_adapter     or ProjectPlanAdapter()
        self._task_adapter         = task_adapter        or TaskAdapter()
        self._stakeholder_adapter  = stakeholder_adapter or StakeholderAdapter()
        self._email_adapter        = email_adapter       or EmailAdapter()
        self._chat_adapter         = chat_adapter        or ChatAdapter()
        self._meeting_adapter      = meeting_adapter     or MeetingNoteAdapter()
        self._status_adapter       = status_adapter      or StatusReportAdapter()
        self._risk_adapter         = risk_adapter        or RiskRegisterAdapter()
        self._lessons_adapter      = lessons_adapter     or LessonsLearnedAdapter()

    # ── Public API ────────────────────────────────────────────────────────────

    def load_project(self, project_id: int) -> ProjectSnapshot:
        """
        Load all project data and return a ProjectSnapshot.

        Args:
            project_id: Integer primary key of the project.

        Returns:
            A fully-assembled, immutable ProjectSnapshot.

        Raises:
            ProjectNotFoundError: If the project cannot be loaded.
            AdapterError:         If a critical adapter fails.
        """
        _log.info("Loading project snapshot for project_id=%s", project_id)

        # ── 1. Project (critical — fail fast) ─────────────────────────────────
        try:
            project = self._project_adapter.load(project_id)
        except AdapterError as exc:
            _log.error("ProjectPlanAdapter failed for project_id=%s", project_id)
            raise ProjectNotFoundError(project_id=project_id) from exc

        # ── 2. All other adapters (graceful degradation) ───────────────────────
        tasks          = self._safe_load(self._task_adapter,        project_id, "tasks")
        stakeholders   = self._safe_load(self._stakeholder_adapter, project_id, "stakeholders")
        emails         = self._safe_load(self._email_adapter,       project_id, "emails")
        chats          = self._safe_load(self._chat_adapter,        project_id, "chat_messages")
        meeting_notes  = self._safe_load(self._meeting_adapter,     project_id, "meeting_notes")
        status_reports = self._safe_load(self._status_adapter,      project_id, "status_reports")
        risk_register  = self._safe_load(self._risk_adapter,        project_id, "risk_register")
        historical     = self._safe_load(self._lessons_adapter,     project_id, "historical_projects")

        # ── 3. Assemble the snapshot ───────────────────────────────────────────
        snapshot = ProjectSnapshot(
            project=project,
            tasks=tasks,
            stakeholders=stakeholders,
            emails=emails,
            chat_messages=chats,
            meeting_notes=meeting_notes,
            status_reports=status_reports,
            risk_register=risk_register,
            historical_projects=historical,
        )

        _log.info(
            "ProjectSnapshot assembled for project '%s' — %s",
            project.name,
            snapshot.summary(),
        )
        return snapshot

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _safe_load(adapter, project_id: int, label: str) -> list:
        """
        Call adapter.load() and return the result.
        On failure, log a warning and return an empty list
        so the rest of the snapshot is still usable.
        """
        try:
            return adapter.load(project_id)
        except Exception as exc:
            _log.warning(
                "Adapter '%s' failed for project_id=%s — returning empty %s. Error: %s",
                adapter.adapter_name, project_id, label, exc,
            )
            return []


# ── Module-level singleton ───────────────────────────────────────────────────

_registry: DataSourceRegistry | None = None


def get_registry() -> DataSourceRegistry:
    """
    Return the module-level DataSourceRegistry singleton.
    Instantiated lazily on first call.

    Flask routes / Graph 1 can use:
        from services.data_source_registry import get_registry
        snapshot = get_registry().load_project(project_id)
    """
    global _registry
    if _registry is None:
        _registry = DataSourceRegistry()
    return _registry
