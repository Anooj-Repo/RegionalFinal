"""
adapters/task_adapter.py
-------------------------
Loads project tasks from data/projects/{code}/tasks.json.
Returns a list of validated ProjectTaskSchema.
"""

from __future__ import annotations

from adapters.file_adapter import FileAdapter
from exceptions import AdapterError
from schemas.domain.project import ProjectTaskSchema


class TaskAdapter(FileAdapter[list[ProjectTaskSchema]]):
    adapter_name = "TaskAdapter"
    _filename    = "tasks.json"

    def load(self, project_id: int) -> list[ProjectTaskSchema]:
        self._log.debug("Loading tasks for project_id=%s", project_id)
        try:
            raw   = self._read_json(project_id)
            tasks = [ProjectTaskSchema(**item) for item in raw]
            self._validate(tasks)

            blocked = sum(1 for t in tasks if t.status.value == "blocked")
            self._log.info(
                "Loaded %d task(s) for project_id=%s (%d blocked)",
                len(tasks), project_id, blocked,
            )
            return tasks
        except AdapterError:
            raise
        except Exception as exc:
            self._raise(f"Failed to parse tasks for project_id={project_id}", exc)
