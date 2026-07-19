from pathlib import Path

import pytest

from prosway_acquisition.adapters.linkedin import LinkedInApifyAdapter, LinkedInManualCsvAdapter
from prosway_acquisition.domain import CompanyProfile


def test_linkedin_apify_adapter_is_skeleton_only():
    with pytest.raises(NotImplementedError):
        LinkedInApifyAdapter().collect(CompanyProfile("ACME", "123456789"))


def test_linkedin_manual_csv_adapter_emits_normalized_evidence(tmp_path: Path):
    path = tmp_path / "linkedin.csv"
    path.write_text(
        "siren,company_name,linkedin_url,employee_count_current,employee_count_previous,open_jobs_count,is_hiring,hr_leadership_found,source_url\n"
        "123456789,ACME,https://linkedin.example/acme,120,90,5,true,false,https://linkedin.example/acme\n",
        encoding="utf-8",
    )
    evidence = LinkedInManualCsvAdapter(path).collect(CompanyProfile("ACME", "123456789"))
    assert {item.signal_type for item in evidence} >= {"headcount_growth", "employee_threshold_crossed", "multi_hiring", "people_ops_gap"}
