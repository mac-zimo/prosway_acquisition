from __future__ import annotations

import csv
from pathlib import Path

from prosway_acquisition.domain import CompanyProfile, Evidence


class JobsSignalAdapter:
    def collect(self, company: CompanyProfile) -> list[Evidence]:
        return []


class JobsManualCsvAdapter(JobsSignalAdapter):
    def __init__(self, path: Path, min_open_roles: int = 3) -> None:
        self.path = path
        self.min_open_roles = min_open_roles
        self._rows = self._load()

    def _load(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return {}
        with self.path.open(newline="", encoding="utf-8") as handle:
            return {row.get("siren", ""): row for row in csv.DictReader(handle) if row.get("siren")}

    def collect(self, company: CompanyProfile) -> list[Evidence]:
        row = self._rows.get(company.siren)
        if not row:
            return []
        count = int(row.get("open_roles_count") or 0)
        if count < self.min_open_roles:
            return []
        return [Evidence(company.siren, "multi_hiring", f"{count} postes ouverts simultanément", "jobs_manual_csv", row.get("source_url", ""), confidence_0_100=80, raw=row)]
