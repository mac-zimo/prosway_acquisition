from __future__ import annotations

import csv
from pathlib import Path

from prosway_acquisition.domain import CompanyProfile, Evidence


class LinkedInApifyAdapter:
    """Future Apify-backed LinkedIn provider. Intentionally no network calls or credentials now."""

    def collect(self, company: CompanyProfile) -> list[Evidence]:
        del company
        raise NotImplementedError("LinkedIn Apify provider requires actor/input/credentials decisions before implementation")


class LinkedInManualCsvAdapter:
    def __init__(self, path: Path, growth_threshold_ratio: float = 0.15, open_jobs_threshold: int = 3) -> None:
        self.path = path
        self.growth_threshold_ratio = growth_threshold_ratio
        self.open_jobs_threshold = open_jobs_threshold
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
        current = int(row.get("employee_count_current") or 0)
        previous = int(row.get("employee_count_previous") or 0)
        open_jobs = int(row.get("open_jobs_count") or 0)
        hr_found = (row.get("hr_leadership_found") or "").strip().lower() in {"true", "1", "yes", "oui"}
        source_url = row.get("source_url") or row.get("linkedin_url", "")
        evidence = []
        if previous and current > previous and (current - previous) / previous >= self.growth_threshold_ratio:
            evidence.append(Evidence(company.siren, "headcount_growth", f"Effectif LinkedIn estimé {previous} -> {current}", "linkedin_manual_csv", source_url, confidence_0_100=65, raw=row))
        for threshold in (50, 100, 150, 200):
            if previous < threshold <= current:
                evidence.append(Evidence(company.siren, "employee_threshold_crossed", f"Seuil {threshold} salariés franchi", "linkedin_manual_csv", source_url, confidence_0_100=60, raw=row))
        if open_jobs >= self.open_jobs_threshold or (row.get("is_hiring") or "").strip().lower() in {"true", "1", "yes", "oui"}:
            evidence.append(Evidence(company.siren, "multi_hiring", f"{open_jobs} postes LinkedIn ouverts", "linkedin_manual_csv", source_url, confidence_0_100=65, raw=row))
        if not hr_found and (open_jobs >= self.open_jobs_threshold or current > previous):
            evidence.append(Evidence(company.siren, "people_ops_gap", "Croissance/recrutement sans leadership RH visible dans import", "linkedin_manual_csv", source_url, confidence_0_100=55, signal_family="hr_need", raw=row))
        return evidence
