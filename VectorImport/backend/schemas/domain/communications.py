"""
schemas/domain/communications.py
----------------------------------
Pydantic domain schemas for: EmailDocument, ChatMessage, MeetingNote.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field, EmailStr

from schemas.base import BaseEntity, BaseTimestampModel


# ===========================================================================
# EmailDocument
# ===========================================================================

class ActionItem(BaseTimestampModel):
    """A single action item extracted from an email or meeting."""
    description: str
    owner:       Optional[str] = None
    due_date:    Optional[str] = None   # ISO date string
    done:        bool          = False


class EmailDocumentCreateSchema(BaseTimestampModel):
    """Input schema for ingesting an email into a project."""

    project_id:  int
    sender:      str                = Field(..., max_length=255)
    recipients:  list[str]          = Field(..., min_length=1)
    subject:     Optional[str]      = Field(default=None, max_length=512)
    timestamp:   Optional[datetime] = None
    body:        Optional[str]      = None
    attachments: list[str]          = Field(default_factory=list, description="Attachment filenames or paths")
    labels:      list[str]          = Field(default_factory=list, description="Email tags/labels")


class EmailDocumentUpdateSchema(BaseTimestampModel):
    """Partial update — mainly for labels/attachments post-processing."""

    labels:      Optional[list[str]] = None
    attachments: Optional[list[str]] = None
    body:        Optional[str]       = None


class EmailDocumentSchema(BaseEntity):
    """Full email document response schema."""

    project_id:  int
    sender:      str
    recipients:  list[str]
    subject:     Optional[str]      = None
    timestamp:   Optional[datetime] = None
    body:        Optional[str]      = None
    attachments: list[str]          = Field(default_factory=list)
    labels:      list[str]          = Field(default_factory=list)


# ===========================================================================
# ChatMessage
# ===========================================================================

class ChatMessageCreateSchema(BaseTimestampModel):
    """Input schema for ingesting a chat message."""

    project_id: int
    channel:    Optional[str]      = Field(default=None, max_length=128)
    sender:     str                = Field(...,          max_length=128)
    timestamp:  Optional[datetime] = None
    message:    Optional[str]      = None
    thread_id:  Optional[str]      = Field(default=None, max_length=128)
    reactions:  dict[str, int]     = Field(default_factory=dict, description="Emoji → count")


class ChatMessageUpdateSchema(BaseTimestampModel):
    """Partial update — reactions and message edits."""

    message:   Optional[str]            = None
    reactions: Optional[dict[str, int]] = None


class ChatMessageSchema(BaseEntity):
    """Full chat message response schema."""

    project_id: int
    channel:    Optional[str]       = None
    sender:     str
    timestamp:  Optional[datetime]  = None
    message:    Optional[str]       = None
    thread_id:  Optional[str]       = None
    reactions:  dict[str, int]      = Field(default_factory=dict)


# ===========================================================================
# MeetingNote
# ===========================================================================

class MeetingActionItem(BaseTimestampModel):
    """A structured action item from a meeting."""

    description: str
    owner:       Optional[str] = None
    due_date:    Optional[str] = None   # ISO date string
    done:        bool          = False


class MeetingNoteCreateSchema(BaseTimestampModel):
    """Input schema for creating a meeting note."""

    project_id:    int
    meeting_title: str                      = Field(..., min_length=1, max_length=255)
    attendees:     list[str]                = Field(default_factory=list)
    decisions:     list[str]                = Field(default_factory=list)
    action_items:  list[MeetingActionItem]  = Field(default_factory=list)
    transcript:    Optional[str]            = None


class MeetingNoteUpdateSchema(BaseTimestampModel):
    """Partial update for a meeting note."""

    meeting_title: Optional[str]                    = None
    attendees:     Optional[list[str]]              = None
    decisions:     Optional[list[str]]              = None
    action_items:  Optional[list[MeetingActionItem]]= None
    transcript:    Optional[str]                    = None


class MeetingNoteSchema(BaseEntity):
    """Full meeting note response schema."""

    project_id:    int
    meeting_title: str
    attendees:     list[str]               = Field(default_factory=list)
    decisions:     list[str]               = Field(default_factory=list)
    action_items:  list[MeetingActionItem] = Field(default_factory=list)
    transcript:    Optional[str]           = None
