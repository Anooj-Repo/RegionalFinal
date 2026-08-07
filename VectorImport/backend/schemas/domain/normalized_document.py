"""
schemas/domain/normalized_document.py
--------------------------------------
NormalizedDocument schema and DocumentSource enum.

Every input source (emails, chats, meeting notes, status reports, tasks,
risks, historical projects) is normalized into this common contract.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentSource(str, Enum):
    EMAIL              = "email"
    CHAT               = "chat"
    MEETING_NOTE       = "meeting_note"
    STATUS_REPORT      = "status_report"
    PROJECT_TASK       = "project_task"
    RISK_ENTRY         = "risk_entry"
    HISTORICAL_PROJECT = "historical_project"


class NormalizedDocument(BaseModel):
    """
    Unified document representation across heterogeneous enterprise data sources.
    """

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    id: str = Field(..., description="Unique document ID (e.g. email_1001, task_102).")
    source: DocumentSource = Field(..., description="Original source type.")
    title: str = Field(..., description="Document headline or summary title.")
    text: str = Field(..., description="Primary body text content.")
    author: Optional[str] = Field(default=None, description="Sender, creator, or owner.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of original content creation.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary source-specific key-value attributes.",
    )
