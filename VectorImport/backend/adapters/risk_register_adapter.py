"""
adapters/risk_register_adapter.py
-----------------------------------
Loads the risk register from data/projects/{code}/risk_register.json.
Returns a list of validated RiskEntrySchema.
"""

from __future__ import annotations

from adapters.file_adapter import FileAdapter
from exceptions import AdapterError
from schemas.domain.risks import RiskEntrySchema


class RiskRegisterAdapter(FileAdapter[list[RiskEntrySchema]]):
    adapter_name = "RiskRegisterAdapter"
    _filename    = "risk_register.json"

    def load(self, project_id: int) -> list[RiskEntrySchema]:
        self._log.debug("Loading risk register for project_id=%s", project_id)
        try:
            raw   = self._read_json(project_id)
            risks = [RiskEntrySchema(**item) for item in raw]
            self._validate(risks)

            open_count     = sum(1 for r in risks if r.status.value == "open")
            critical_count = sum(1 for r in risks if r.impact.value == "critical")
            self._log.info(
                "Loaded %d risk(s) for project_id=%s (%d open, %d critical impact)",
                len(risks), project_id, open_count, critical_count,
            )
            return risks
        except AdapterError:
            raise
        except Exception as exc:
            self._raise(f"Failed to parse risk register for project_id={project_id}", exc)
