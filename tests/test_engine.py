from prosway_acquisition.domain import CompanyProfile, Evidence
from prosway_acquisition.engine import run_growth_workflow
from prosway_acquisition.models import SourceLog
from prosway_acquisition.workflow_configs import get_workflow


def test_run_growth_workflow_ranks_manual_evidence(monkeypatch):
    company = CompanyProfile("ACME", "123456789", employee_min=50, employee_max=99, employee_label="50-99 salariés", department="75")

    monkeypatch.setattr("prosway_acquisition.engine.collect_base_profiles", lambda workflow, max_pages_per_query=1: ([company], [SourceLog("test", "q", "OK")]))

    class Adapter:
        def collect(self, company):
            return [
                Evidence(company.siren, "multi_hiring", "4 postes", "test"),
                Evidence(company.siren, "new_office", "nouveau site", "test"),
            ]

    monkeypatch.setattr("prosway_acquisition.engine.build_growth_adapters", lambda enrichment_input: [Adapter()])
    results, logs = run_growth_workflow(get_workflow("rh_growth_50_200_idf"))
    assert logs[0].source == "test"
    assert len(results) == 1
    assert results[0].priority_label == "A"
    assert results[0].enrichment_needed is False
