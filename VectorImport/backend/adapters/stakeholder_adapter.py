"""
adapters/stakeholder_adapter.py
--------------------------------
Loads project stakeholders from data/projects/{code}/stakeholders.json.
Returns a list of validated StakeholderSchema.
"""

from __future__ import annotations

from adapters.file_adapter import FileAdapter
from exceptions import AdapterError
from schemas.domain.project import StakeholderSchema


class StakeholderAdapter(FileAdapter[list[StakeholderSchema]]):
    adapter_name = "StakeholderAdapter"
    _filename    = "stakeholders.json"

    def load(self, project_id: int) -> list[StakeholderSchema]:
        self._log.debug("Loading stakeholders for project_id=%s", project_id)
        try:
            raw = self._read_json(project_id)
            stakeholders = [StakeholderSchema(**item) for item in raw]
            self._validate(stakeholders)
            self._log.info(
                "Loaded %d stakeholder(s) for project_id=%s",
                len(stakeholders), project_id,
            )
            return stakeholders
        except AdapterError:
            raise
        except Exception as exc:
            self._raise(f"Failed to parse stakeholders for project_id={project_id}", exc)
