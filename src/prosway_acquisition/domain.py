from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class CompanyProfile:
    name: str
    siren: str
    website: str = ""
    naf_code: str = ""
    naf_label: str = ""
    employee_min: int | None = None
    employee_max: int | None = None
    employee_label: str = ""
    city: str = ""
    department: str = ""
    region: str = ""
    source_urls: tuple[str, ...] = ()
    raw: dict[str, Any] = field(default_factory=dict, compare=False)

    @property
    def employee_range(self) -> str:
        if self.employee_label:
            return self.employee_label
        if self.employee_min is not None and self.employee_max is not None:
            return f"{self.employee_min}-{self.employee_max} salariés"
        return ""


@dataclass(frozen=True, slots=True)
class Evidence:
    company_siren: str
    signal_type: str
    description: str
    source_name: str
    source_url: str = ""
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_0_100: int = 70
    signal_family: str = "growth"
    raw: dict[str, Any] = field(default_factory=dict, compare=False)


@dataclass(frozen=True, slots=True)
class RuleResult:
    rule_name: str
    matched: bool
    score_delta: int = 0
    rationale: str = ""
    weight: int = 0


@dataclass(frozen=True, slots=True)
class LeadResult:
    company: CompanyProfile
    evidence: tuple[Evidence, ...] = ()
    rule_results: tuple[RuleResult, ...] = ()
    priority_score_0_100: int = 0
    priority_label: str = "D"
    matched_rules: tuple[str, ...] = ()
    growth_signal_count: int = 0
    recommended_angle: str = ""
    enrichment_needed: bool = True


@dataclass(frozen=True, slots=True)
class WorkflowRunLog:
    source: str
    query_or_url: str
    status: str
    notes: str = ""

    def as_row(self) -> list[str]:
        return [self.source, self.query_or_url, self.status, self.notes]
