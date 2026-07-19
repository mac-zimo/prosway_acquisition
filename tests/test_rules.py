from prosway_acquisition.domain import CompanyProfile, Evidence
from prosway_acquisition.rules import (
    DepartmentRule,
    EmployeeRangeRule,
    MinSignalsRule,
    WeightedSignalRule,
    default_growth_rules,
    evaluate_growth_rules,
    priority_label_for_growth,
)


def company() -> CompanyProfile:
    return CompanyProfile(name="ACME", siren="123456789", employee_min=50, employee_max=99, employee_label="50-99 salariés", department="75")


def test_employee_range_rule_matches_overlap():
    result = EmployeeRangeRule(50, 200).evaluate(company(), [])
    assert result.matched is True
    assert result.score_delta == 20


def test_department_rule_matches_idf():
    assert DepartmentRule(("75", "92")).evaluate(company(), []).matched is True
    assert DepartmentRule(("13",)).evaluate(company(), []).matched is False


def test_weighted_signal_rule_scores_only_when_evidence_present():
    evidence = [Evidence(company_siren="123456789", signal_type="multi_hiring", description="4 postes", source_name="manual")]
    result = WeightedSignalRule("multi_hiring", 25).evaluate(company(), evidence)
    assert result.matched is True
    assert result.score_delta == 25


def test_min_signals_rule_counts_signal_family():
    evidence = [
        Evidence(company_siren="123456789", signal_type="multi_hiring", description="4 postes", source_name="manual"),
        Evidence(company_siren="123456789", signal_type="new_office", description="nouvelle agence", source_name="manual"),
    ]
    assert MinSignalsRule(2, "growth").evaluate(company(), evidence).matched is True


def test_growth_score_and_labels():
    evidence = [
        Evidence(company_siren="123456789", signal_type="multi_hiring", description="4 postes", source_name="manual"),
        Evidence(company_siren="123456789", signal_type="new_office", description="nouvelle agence", source_name="manual"),
    ]
    score, label, results = evaluate_growth_rules(company(), evidence, default_growth_rules(("75",)))
    assert score == 100
    assert label == "A"
    assert {r.rule_name for r in results if r.matched} >= {"employee_range_50_200", "target_department", "signal_multi_hiring", "signal_new_office", "min_growth_signals_2"}
    assert priority_label_for_growth(65, evidence[:1]) == "B"
