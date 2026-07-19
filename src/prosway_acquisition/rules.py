from __future__ import annotations

from collections.abc import Iterable

from .domain import CompanyProfile, Evidence, RuleResult

GROWTH_SIGNAL_TYPES = {
    "multi_hiring",
    "fundraising_recent",
    "new_office",
    "headcount_growth",
    "strong_growth_claim",
}
STRONG_GROWTH_SIGNAL_TYPES = {"multi_hiring", "fundraising_recent", "headcount_growth"}


class Rule:
    name: str
    weight: int = 0

    def evaluate(self, company: CompanyProfile, evidence: Iterable[Evidence]) -> RuleResult:
        raise NotImplementedError


class EmployeeRangeRule(Rule):
    def __init__(self, minimum: int, maximum: int, weight: int = 20) -> None:
        self.minimum = minimum
        self.maximum = maximum
        self.weight = weight
        self.name = f"employee_range_{minimum}_{maximum}"

    def evaluate(self, company: CompanyProfile, evidence: Iterable[Evidence]) -> RuleResult:
        del evidence
        matched = company.employee_min is not None and company.employee_max is not None and company.employee_max >= self.minimum and company.employee_min <= self.maximum
        return RuleResult(self.name, matched, self.weight if matched else 0, f"{company.employee_range} overlaps {self.minimum}-{self.maximum}", self.weight)


class DepartmentRule(Rule):
    def __init__(self, departments: Iterable[str], weight: int = 10) -> None:
        self.departments = tuple(departments)
        self.weight = weight
        self.name = "target_department"

    def evaluate(self, company: CompanyProfile, evidence: Iterable[Evidence]) -> RuleResult:
        del evidence
        matched = company.department in self.departments
        return RuleResult(self.name, matched, self.weight if matched else 0, f"department={company.department}", self.weight)


class MinSignalsRule(Rule):
    def __init__(self, min_count: int, signal_family: str = "growth", weight: int = 0) -> None:
        self.min_count = min_count
        self.signal_family = signal_family
        self.weight = weight
        self.name = f"min_{signal_family}_signals_{min_count}"

    def evaluate(self, company: CompanyProfile, evidence: Iterable[Evidence]) -> RuleResult:
        del company
        count = sum(1 for item in evidence if item.signal_family == self.signal_family)
        matched = count >= self.min_count
        return RuleResult(self.name, matched, self.weight if matched else 0, f"{count} {self.signal_family} signals", self.weight)


class WeightedSignalRule(Rule):
    def __init__(self, signal_type: str, weight: int) -> None:
        self.signal_type = signal_type
        self.weight = weight
        self.name = f"signal_{signal_type}"

    def evaluate(self, company: CompanyProfile, evidence: Iterable[Evidence]) -> RuleResult:
        del company
        matched = any(item.signal_type == self.signal_type for item in evidence)
        return RuleResult(self.name, matched, self.weight if matched else 0, self.signal_type, self.weight)


def growth_signal_count(evidence: Iterable[Evidence]) -> int:
    return len({item.signal_type for item in evidence if item.signal_type in GROWTH_SIGNAL_TYPES})


def priority_label_for_growth(score: int, evidence: Iterable[Evidence]) -> str:
    items = tuple(evidence)
    count = growth_signal_count(items)
    has_strong = any(item.signal_type in STRONG_GROWTH_SIGNAL_TYPES for item in items)
    if score >= 80 and count >= 2:
        return "A"
    if score >= 65 and has_strong:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def evaluate_growth_rules(company: CompanyProfile, evidence: Iterable[Evidence], rules: Iterable[Rule]) -> tuple[int, str, tuple[RuleResult, ...]]:
    evidence_tuple = tuple(evidence)
    results = tuple(rule.evaluate(company, evidence_tuple) for rule in rules)
    score = min(100, 30 + sum(result.score_delta for result in results))
    return score, priority_label_for_growth(score, evidence_tuple), results


def default_growth_rules(departments: Iterable[str]) -> tuple[Rule, ...]:
    return (
        EmployeeRangeRule(50, 200),
        DepartmentRule(departments),
        WeightedSignalRule("multi_hiring", 25),
        WeightedSignalRule("fundraising_recent", 25),
        WeightedSignalRule("new_office", 20),
        WeightedSignalRule("headcount_growth", 20),
        WeightedSignalRule("strong_growth_claim", 15),
        MinSignalsRule(2, "growth"),
    )
