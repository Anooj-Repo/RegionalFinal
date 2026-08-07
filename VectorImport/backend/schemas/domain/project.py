"""
schemas/domain/project.py
--------------------------
Pydantic domain schemas for: Project, ProjectTask, Stakeholder.

Each entity has three schema variants:
    <Entity>CreateSchema  — input validation for POST
    <Entity>UpdateSchema  — partial input for PATCH (all fields Optional)
    <Entity>Schema        — full response shape (inherits BaseEntity)
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import Field, field_validator, model_validator

from schemas.base import BaseEntity, BaseTimestampModel

# ---------------------------------------------------------------------------
# Enums (mirrors database/models.py — kept in sync manually)
# ---------------------------------------------------------------------------

from enum import Enum

class ProjectStatus(str, Enum):
    PLANNING  = "planning"
    ACTIVE    = "active"
    ON_HOLD   = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"

class TaskStatus(str, Enum):
    OPEN        = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED     = "blocked"
    COMPLETED   = "completed"
    CANCELLED   = "cancelled"

class CommunicationPreference(str, Enum):
    EMAIL   = "email"
    CHAT    = "chat"
    MEETING = "meeting"
    PHONE   = "phone"


# ===========================================================================
# Project
# ===========================================================================

class ProjectCreateSchema(BaseTimestampModel):
    """Input schema for creating a new project."""

    name:            str                    = Field(..., min_length=1, max_length=255)
    description:     Optional[str]          = None
    start_date:      Optional[date]         = None
    end_date:        Optional[date]         = None
    status:          ProjectStatus          = ProjectStatus.PLANNING
    sponsor:         Optional[str]          = Field(default=None, max_length=128)
    program_manager: Optional[str]          = Field(default=None, max_length=128)

    @model_validator(mode="after")
    def end_after_start(self) -> "ProjectCreateSchema":
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date must be on or after start_date.")
        return self


class ProjectUpdateSchema(BaseTimestampModel):
    """Partial update schema — every field is optional."""

    name:            Optional[str]          = Field(default=None, min_length=1, max_length=255)
    description:     Optional[str]          = None
    start_date:      Optional[date]         = None
    end_date:        Optional[date]         = None
    status:          Optional[ProjectStatus]= None
    sponsor:         Optional[str]          = None
    program_manager: Optional[str]          = None


class ProjectSchema(BaseEntity):
    """Full project response schema."""

    project_id:      str            = Field(..., description="UUID business key")
    name:            str
    description:     Optional[str]  = None
    start_date:      Optional[date] = None
    end_date:        Optional[date] = None
    status:          ProjectStatus
    sponsor:         Optional[str]  = None
    program_manager: Optional[str]  = None


# ===========================================================================
# ProjectTask
# ===========================================================================

class ProjectTaskCreateSchema(BaseTimestampModel):
    """Input schema for creating a project task."""

    project_id:   int
    title:        str                  = Field(..., min_length=1, max_length=255)
    description:  Optional[str]        = None
    owner:        Optional[str]        = Field(default=None, max_length=128)
    priority:     TaskPriority         = TaskPriority.MEDIUM
    status:       TaskStatus           = TaskStatus.OPEN
    due_date:     Optional[date]       = None
    completion:   int                  = Field(default=0, ge=0, le=100)
    dependencies: list[int]            = Field(default_factory=list, description="List of task IDs this task depends on")
    blockers:     list[str]            = Field(default_factory=list, description="Free-text blocker descriptions")


class ProjectTaskUpdateSchema(BaseTimestampModel):
    """Partial update schema for a project task."""

    title:        Optional[str]            = Field(default=None, min_length=1, max_length=255)
    description:  Optional[str]            = None
    owner:        Optional[str]            = None
    priority:     Optional[TaskPriority]   = None
    status:       Optional[TaskStatus]     = None
    due_date:     Optional[date]           = None
    completion:   Optional[int]            = Field(default=None, ge=0, le=100)
    dependencies: Optional[list[int]]      = None
    blockers:     Optional[list[str]]      = None


class ProjectTaskSchema(BaseEntity):
    """Full project task response schema."""

    project_id:   int
    title:        str
    description:  Optional[str]   = None
    owner:        Optional[str]   = None
    priority:     TaskPriority
    status:       TaskStatus
    due_date:     Optional[date]  = None
    completion:   int
    dependencies: list[int]       = Field(default_factory=list)
    blockers:     list[str]       = Field(default_factory=list)


# ===========================================================================
# Stakeholder
# ===========================================================================

class StakeholderCreateSchema(BaseTimestampModel):
    """Input schema for adding a stakeholder."""

    project_id:               int
    name:                     str                       = Field(..., min_length=1, max_length=128)
    role:                     Optional[str]             = Field(default=None, max_length=128)
    department:               Optional[str]             = Field(default=None, max_length=128)
    communication_preference: CommunicationPreference   = CommunicationPreference.EMAIL


class StakeholderUpdateSchema(BaseTimestampModel):
    """Partial update schema for a stakeholder."""

    name:                     Optional[str]                        = None
    role:                     Optional[str]                        = None
    department:               Optional[str]                        = None
    communication_preference: Optional[CommunicationPreference]    = None


class StakeholderSchema(BaseEntity):
    """Full stakeholder response schema."""

    project_id:               int
    name:                     str
    role:                     Optional[str]              = None
    department:               Optional[str]              = None
    communication_preference: CommunicationPreference
