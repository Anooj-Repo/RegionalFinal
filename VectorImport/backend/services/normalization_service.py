"""
services/normalization_service.py
-----------------------------------
DocumentNormalizationService — Node 1 service for Graph 1.

Transforms heterogeneous data items inside a ProjectSnapshot into a uniform
list of NormalizedDocument objects.
"""

from __future__ import annotations

from typing import Sequence
from schemas.domain.snapshot import ProjectSnapshot
from schemas.domain.normalized_document import NormalizedDocument, DocumentSource
from utils.logger import get_logger

_log = get_logger("services.normalization")


class DocumentNormalizationService:
    """
    Normalizes ProjectSnapshot content into unified NormalizedDocument schemas.
    """

    def normalize(self, snapshot: ProjectSnapshot) -> list[NormalizedDocument]:
        """
        Convert all project items into NormalizedDocument instances.
        """
        _log.info("Normalizing documents for project_id=%s", snapshot.project.project_id)
        docs: list[NormalizedDocument] = []

        # 1. Emails
        for email in snapshot.emails:
            docs.append(
                NormalizedDocument(
                    id=f"email_{email.id}",
                    source=DocumentSource.EMAIL,
                    title=email.subject or f"Email from {email.sender}",
                    text=email.body or "",
                    author=email.sender,
                    created_at=email.timestamp or snapshot.snapshot_timestamp,
                    metadata={
                        "recipients": email.recipients,
                        "attachments": email.attachments,
                        "labels": email.labels,
                        "project_id": email.project_id,
                    },
                )
            )

        # 2. Chat messages
        for chat in snapshot.chat_messages:
            docs.append(
                NormalizedDocument(
                    id=f"chat_{chat.id}",
                    source=DocumentSource.CHAT,
                    title=f"Chat in {chat.channel or 'general'}",
                    text=chat.message or "",
                    author=chat.sender,
                    created_at=chat.timestamp or snapshot.snapshot_timestamp,
                    metadata={
                        "channel": chat.channel,
                        "thread_id": chat.thread_id,
                        "reactions": chat.reactions,
                        "project_id": chat.project_id,
                    },
                )
            )

        # 3. Meeting Notes
        for meeting in snapshot.meeting_notes:
            content = f"Title: {meeting.meeting_title}\nAttendees: {', '.join(meeting.attendees)}\n"
            if meeting.decisions:
                content += "Decisions:\n" + "\n".join(f"- {d}" for d in meeting.decisions) + "\n"
            if meeting.action_items:
                content += "Action Items:\n" + "\n".join(
                    f"- {item.description} (Owner: {item.owner or 'Unassigned'})"
                    for item in meeting.action_items
                ) + "\n"
            if meeting.transcript:
                content += f"\nTranscript:\n{meeting.transcript}"

            docs.append(
                NormalizedDocument(
                    id=f"meeting_{meeting.id}",
                    source=DocumentSource.MEETING_NOTE,
                    title=meeting.meeting_title,
                    text=content.strip(),
                    author=meeting.attendees[0] if meeting.attendees else "Meeting Participant",
                    created_at=snapshot.snapshot_timestamp,
                    metadata={
                        "attendees": meeting.attendees,
                        "decisions_count": len(meeting.decisions),
                        "action_items_count": len(meeting.action_items),
                        "project_id": meeting.project_id,
                    },
                )
            )

        # 4. Status Reports
        for report in snapshot.status_reports:
            content = f"Reporting Period: {report.reporting_period}\n"
            if report.accomplishments:
                content += "Accomplishments:\n" + "\n".join(f"- {a}" for a in report.accomplishments) + "\n"
            if report.blockers:
                content += "Blockers:\n" + "\n".join(f"- {b}" for b in report.blockers) + "\n"
            if report.risks:
                content += "Risks:\n" + "\n".join(f"- {r}" for r in report.risks) + "\n"
            if report.next_steps:
                content += "Next Steps:\n" + "\n".join(f"- {n}" for n in report.next_steps)

            docs.append(
                NormalizedDocument(
                    id=f"report_{report.id}",
                    source=DocumentSource.STATUS_REPORT,
                    title=f"Status Report {report.reporting_period}",
                    text=content.strip(),
                    author=snapshot.project.program_manager or "Program Manager",
                    created_at=snapshot.snapshot_timestamp,
                    metadata={
                        "reporting_period": report.reporting_period,
                        "has_blockers": report.has_blockers,
                        "has_risks": report.has_risks,
                        "project_id": report.project_id,
                    },
                )
            )

        # 5. Project Tasks
        for task in snapshot.tasks:
            text_body = f"Task: {task.title}\nDescription: {task.description or 'N/A'}\nStatus: {task.status.value}, Priority: {task.priority.value}\nCompletion: {task.completion}%"
            if task.blockers:
                text_body += "\nBlockers:\n" + "\n".join(f"- {b}" for b in task.blockers)

            docs.append(
                NormalizedDocument(
                    id=f"task_{task.id}",
                    source=DocumentSource.PROJECT_TASK,
                    title=task.title,
                    text=text_body,
                    author=task.owner,
                    created_at=snapshot.snapshot_timestamp,
                    metadata={
                        "task_id": task.id,
                        "owner": task.owner,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "completion": task.completion,
                        "dependencies": task.dependencies,
                        "blockers": task.blockers,
                        "project_id": task.project_id,
                    },
                )
            )

        # 6. Risk Entries
        for risk in snapshot.risk_register:
            text_body = f"Risk: {risk.title}\nProbability: {risk.probability.value}, Impact: {risk.impact.value}, Risk Score: {risk.risk_score}\nStatus: {risk.status.value}\nOwner: {risk.owner or 'Unassigned'}\nMitigation: {risk.mitigation or 'None'}"
            docs.append(
                NormalizedDocument(
                    id=f"risk_{risk.id}",
                    source=DocumentSource.RISK_ENTRY,
                    title=risk.title,
                    text=text_body,
                    author=risk.owner,
                    created_at=snapshot.snapshot_timestamp,
                    metadata={
                        "risk_id": risk.id,
                        "probability": risk.probability.value,
                        "impact": risk.impact.value,
                        "risk_score": risk.risk_score,
                        "status": risk.status.value,
                        "project_id": risk.project_id,
                    },
                )
            )

        # 7. Historical Projects
        for hist in snapshot.historical_projects:
            text_body = f"Historical Project: {hist.project_name}\nLessons Learned:\n" + "\n".join(f"- {l}" for l in hist.lessons_learned)
            if hist.successful_mitigations:
                text_body += "\nSuccessful Mitigations:\n" + "\n".join(f"- {m}" for m in hist.successful_mitigations)

            docs.append(
                NormalizedDocument(
                    id=f"historical_{hist.id}",
                    source=DocumentSource.HISTORICAL_PROJECT,
                    title=hist.project_name,
                    text=text_body,
                    author="PMO Knowledge Base",
                    created_at=snapshot.snapshot_timestamp,
                    metadata={
                        "lesson_count": hist.lesson_count,
                        "risk_count": hist.risk_count,
                    },
                )
            )

        _log.info("Normalized %d documents total for project_id=%s", len(docs), snapshot.project.project_id)
        return docs
