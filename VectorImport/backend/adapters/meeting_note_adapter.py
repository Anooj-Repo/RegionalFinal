"""
adapters/meeting_note_adapter.py
---------------------------------
Loads meeting notes from data/projects/{code}/meeting_notes.json.
Returns a list of validated MeetingNoteSchema.
"""

from __future__ import annotations

from adapters.file_adapter import FileAdapter
from exceptions import AdapterError
from schemas.domain.communications import MeetingNoteSchema


class MeetingNoteAdapter(FileAdapter[list[MeetingNoteSchema]]):
    adapter_name = "MeetingNoteAdapter"
    _filename    = "meeting_notes.json"

    def load(self, project_id: int) -> list[MeetingNoteSchema]:
        self._log.debug("Loading meeting notes for project_id=%s", project_id)
        try:
            raw   = self._read_json(project_id)
            notes = [MeetingNoteSchema(**item) for item in raw]
            self._validate(notes)
            self._log.info(
                "Loaded %d meeting note(s) for project_id=%s",
                len(notes), project_id,
            )
            return notes
        except AdapterError:
            raise
        except Exception as exc:
            self._raise(f"Failed to parse meeting notes for project_id={project_id}", exc)
