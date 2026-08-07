"""
adapters/__init__.py
---------------------
Public surface of the adapters package.
"""

from adapters.base import BaseAdapter
from adapters.file_adapter import FileAdapter
from adapters.project_plan_adapter import ProjectPlanAdapter
from adapters.task_adapter import TaskAdapter
from adapters.email_adapter import EmailAdapter
from adapters.chat_adapter import ChatAdapter
from adapters.status_report_adapter import StatusReportAdapter
from adapters.risk_register_adapter import RiskRegisterAdapter
from adapters.lessons_learned_adapter import LessonsLearnedAdapter
from adapters.stakeholder_adapter import StakeholderAdapter
from adapters.meeting_note_adapter import MeetingNoteAdapter

__all__ = [
    "BaseAdapter",
    "FileAdapter",
    "ProjectPlanAdapter",
    "TaskAdapter",
    "EmailAdapter",
    "ChatAdapter",
    "StatusReportAdapter",
    "RiskRegisterAdapter",
    "LessonsLearnedAdapter",
    "StakeholderAdapter",
    "MeetingNoteAdapter",
]
