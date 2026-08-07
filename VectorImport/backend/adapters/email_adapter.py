"""
adapters/email_adapter.py
--------------------------
Loads email communications from data/projects/{code}/emails.json.
Returns a list of validated EmailDocumentSchema.
"""

from __future__ import annotations

from adapters.file_adapter import FileAdapter
from exceptions import AdapterError
from schemas.domain.communications import EmailDocumentSchema


class EmailAdapter(FileAdapter[list[EmailDocumentSchema]]):
    adapter_name = "EmailAdapter"
    _filename    = "emails.json"

    def load(self, project_id: int) -> list[EmailDocumentSchema]:
        self._log.debug("Loading emails for project_id=%s", project_id)
        try:
            raw    = self._read_json(project_id)
            emails = [EmailDocumentSchema(**item) for item in raw]
            self._validate(emails)
            self._log.info(
                "Loaded %d email(s) for project_id=%s",
                len(emails), project_id,
            )
            return emails
        except AdapterError:
            raise
        except Exception as exc:
            self._raise(f"Failed to parse emails for project_id={project_id}", exc)
