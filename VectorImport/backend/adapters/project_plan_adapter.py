"""
adapters/project_plan_adapter.py
---------------------------------
Loads project plan from data/projects/{code}/project.json.
Returns a validated ProjectSchema.
"""

from __future__ import annotations

from adapters.file_adapter import FileAdapter
from exceptions import AdapterError
from schemas.domain.project import ProjectSchema


class ProjectPlanAdapter(FileAdapter[ProjectSchema]):
    adapter_name = "ProjectPlanAdapter"
    _filename    = "project.json"

    def load(self, project_id: int) -> ProjectSchema:
        self._log.debug("Loading project plan for project_id=%s", project_id)
        try:
            data   = self._read_json(project_id)
            schema = ProjectSchema(**data)
            self._validate([schema])
            self._log.info(
                "Loaded project '%s' [%s] for project_id=%s",
                schema.name, schema.status.value, project_id,
            )
            return schema
        except AdapterError:
            raise
        except Exception as exc:
            self._raise(f"Failed to parse project plan for project_id={project_id}", exc)
