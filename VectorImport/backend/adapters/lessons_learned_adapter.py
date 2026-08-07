"""
adapters/lessons_learned_adapter.py
-------------------------------------
Loads historical project data from data/projects/{code}/historical_projects.json.
Returns a list of validated HistoricalProjectSchema.
"""

from __future__ import annotations

from adapters.file_adapter import FileAdapter
from exceptions import AdapterError
from schemas.domain.historical import HistoricalProjectSchema


class LessonsLearnedAdapter(FileAdapter[list[HistoricalProjectSchema]]):
    adapter_name = "LessonsLearnedAdapter"
    _filename    = "historical_projects.json"

    def load(self, project_id: int) -> list[HistoricalProjectSchema]:
        self._log.debug("Loading historical projects for project_id=%s", project_id)
        try:
            raw        = self._read_json(project_id)
            historical = [HistoricalProjectSchema(**item) for item in raw]
            self._validate(historical)
            total_lessons = sum(h.lesson_count for h in historical)
            self._log.info(
                "Loaded %d historical project(s) (%d lessons) for project_id=%s",
                len(historical), total_lessons, project_id,
            )
            return historical
        except AdapterError:
            raise
        except Exception as exc:
            self._raise(f"Failed to parse historical projects for project_id={project_id}", exc)
