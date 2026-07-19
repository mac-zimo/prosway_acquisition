from __future__ import annotations

import csv
import json
from pathlib import Path

from prosway_acquisition.domain import CompanyProfile, Evidence

KEYWORDS = {
    "fundraising_recent": ("levée de fonds", "seed", "série a", "financement", "tour de table", "capital développement"),
    "new_office": ("ouvre un bureau", "nouvelle agence", "s'implante", "nouveau site"),
    "strong_growth_claim": ("forte croissance", "hypercroissance", "double ses effectifs", "recrute", "croissance de"),
}


class FundingNewsSignalAdapter:
    def collect(self, company: CompanyProfile) -> list[Evidence]:
        return []


class NewsManualAdapter(FundingNewsSignalAdapter):
    def __init__(self, path: Path) -> None:
        self.path = path
        self._rows = self._load()

    def _load(self) -> list[dict[str, str]]:
        if not self.path.exists():
            return []
        if self.path.suffix.lower() == ".json":
            return json.loads(self.path.read_text(encoding="utf-8"))
        with self.path.open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def collect(self, company: CompanyProfile) -> list[Evidence]:
        evidence = []
        for row in self._rows:
            if row.get("siren") and row.get("siren") != company.siren:
                continue
            text = " ".join([row.get("title", ""), row.get("description", ""), row.get("text", "")]).lower()
            for signal_type, keywords in KEYWORDS.items():
                if any(keyword in text for keyword in keywords):
                    evidence.append(Evidence(company.siren, signal_type, row.get("description") or row.get("title") or signal_type, "news_manual", row.get("source_url", ""), confidence_0_100=70, raw=row))
        return evidence
