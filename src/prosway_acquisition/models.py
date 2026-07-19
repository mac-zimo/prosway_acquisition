from __future__ import annotations

from dataclasses import dataclass

from .domain import CompanyProfile, Evidence, LeadResult, RuleResult, WorkflowRunLog


class SourceLog(WorkflowRunLog):
    pass


@dataclass(slots=True)
class Company:
    company_name: str
    siren: str
    segment_prosway: str
    naf_code: str
    naf_label: str
    employee_range: str
    city: str
    region: str
    website: str
    source_company_url: str
    fit_notes: str
    priority_score_0_100: int
    priority_label: str
    department: str = ""

    def as_enterprise_row(self) -> list[object]:
        return [
            self.company_name,
            self.siren,
            self.segment_prosway,
            self.naf_code,
            self.naf_label,
            self.employee_range,
            self.city,
            self.region,
            self.website,
            self.source_company_url,
            self.fit_notes,
            self.priority_score_0_100,
            self.priority_label,
        ]
