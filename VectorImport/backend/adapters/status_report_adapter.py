"""
adapters/status_report_adapter.py
-----------------------------------
Loads status reports from data/projects/{code}/status_reports.json.
Returns a list of validated StatusReportSchema.
"""

from __future__ import annotations

from adapters.file_adapter import FileAdapter
from exceptions import AdapterError
from schemas.domain.reports import StatusReportSchema


class StatusReportAdapter(FileAdapter[list[StatusReportSchema]]):
    adapter_name = "StatusReportAdapter"
    _filename    = "status_reports.json"

    def load(self, project_id: int) -> list[StatusReportSchema]:
        self._log.debug("Loading status reports for project_id=%s", project_id)
        try:
            raw     = self._read_json(project_id)
            reports = [StatusReportSchema(**item) for item in raw]
            self._validate(reports)
            periods = [r.reporting_period for r in reports]
            self._log.info(
                "Loaded %d status report(s) for project_id=%s — periods: %s",
                len(reports), project_id, periods,
            )
            return reports
        except AdapterError:
            raise
        except Exception as exc:
            self._raise(f"Failed to parse status reports for project_id={project_id}", exc)
