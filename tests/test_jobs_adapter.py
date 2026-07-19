from pathlib import Path

from prosway_acquisition.adapters.jobs import JobsManualCsvAdapter
from prosway_acquisition.domain import CompanyProfile


def test_jobs_manual_csv_adapter_emits_multi_hiring(tmp_path: Path):
    path = tmp_path / "jobs.csv"
    path.write_text("siren,company_name,open_roles_count,source_url,observed_at\n123456789,ACME,4,https://jobs.example,2026-07-19\n", encoding="utf-8")
    evidence = JobsManualCsvAdapter(path).collect(CompanyProfile("ACME", "123456789"))
    assert len(evidence) == 1
    assert evidence[0].signal_type == "multi_hiring"
