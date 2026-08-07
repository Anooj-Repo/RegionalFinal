"""
adapters/file_adapter.py
-------------------------
FileAdapter — base class for all file-backed adapters.

Every subclass:
    1. Sets `_filename` (e.g. "tasks.json")
    2. Calls `self._read_json(project_id)` to get raw data
    3. Validates and returns typed Pydantic models

File layout:
    data/
    └── projects/
        ├── alpha/
        │   ├── project.json
        │   ├── tasks.json
        │   └── ...
        ├── beta/
        └── gamma/
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Generic

from adapters.base import BaseAdapter, T
from exceptions import AdapterError

# Absolute path to the synthetic dataset root
DATA_DIR: Path = Path(__file__).parent.parent / "data" / "projects"


class FileAdapter(BaseAdapter[T], Generic[T]):
    """
    Reads JSON synthetic data files for a given project_id.

    Subclasses only need to set `_filename` and implement `load()`.
    All file resolution, reading, and error handling lives here.
    """

    _filename: str = ""  # Override in every subclass

    # ── Path resolution ───────────────────────────────────────────────────────

    def _get_project_code(self, project_id: int) -> str:
        """
        Resolve project_id → dataset folder name via PROJECT_REGISTRY.

        Raises:
            AdapterError: If project_id has no registered dataset.
        """
        from adapters.registry_config import PROJECT_REGISTRY
        code = PROJECT_REGISTRY.get(project_id)
        if not code:
            self._raise(
                f"No synthetic dataset for project_id={project_id}. "
                f"Registered IDs: {sorted(PROJECT_REGISTRY)}"
            )
        return code  # type: ignore[return-value]

    def _resolve_path(self, project_id: int) -> Path:
        """
        Build the full path to this adapter's JSON file.

        Raises:
            AdapterError: If the file does not exist on disk.
        """
        code = self._get_project_code(project_id)
        path = DATA_DIR / code / self._filename
        if not path.exists():
            self._raise(
                f"Synthetic data file not found: {path}. "
                f"Expected at data/projects/{code}/{self._filename}"
            )
        return path  # type: ignore[return-value]

    # ── File reading ──────────────────────────────────────────────────────────

    def _read_json(self, project_id: int) -> Any:
        """
        Read and parse the JSON file for the given project_id.

        Returns:
            Parsed Python object (dict or list).

        Raises:
            AdapterError: On missing file, invalid JSON, or IO errors.
        """
        path = self._resolve_path(project_id)
        self._log.debug("[%s] Reading: %s", self.adapter_name, path)
        try:
            with path.open(encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError as exc:
            self._raise(f"Invalid JSON in {path.name}: {exc.msg} (line {exc.lineno})", exc)
        except OSError as exc:
            self._raise(f"Cannot read file: {path}", exc)
