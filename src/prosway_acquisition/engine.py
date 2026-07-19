from __future__ import annotations

from pathlib import Path

from .adapters.jobs import JobsManualCsvAdapter
from .adapters.linkedin import LinkedInManualCsvAdapter
from .adapters.news import NewsManualAdapter
from .adapters.recherche_entreprises import RechercheEntreprisesAdapter, iter_search_params
from .domain import CompanyProfile, Evidence, LeadResult
from .models import SourceLog
from .rules import growth_signal_count, evaluate_growth_rules
from .workflows import WorkflowConfig


def collect_base_profiles(workflow: WorkflowConfig, max_pages_per_query: int = 1) -> tuple[list[CompanyProfile], list[SourceLog]]:
    adapter = RechercheEntreprisesAdapter(pause_seconds=0)
    profiles_by_siren: dict[str, CompanyProfile] = {}
    logs: list[SourceLog] = []
    for params in iter_search_params(workflow.naf_codes, workflow.employee_brackets, workflow.departments):
        profiles, source_logs = adapter.fetch_companies(params, max_pages_per_query=max_pages_per_query)
        logs.extend(source_logs)
        for profile in profiles:
            if profile.siren in profiles_by_siren:
                continue
            if profile.department not in workflow.departments:
                continue
            if profile.employee_min is None or profile.employee_max is None:
                continue
            if profile.employee_max < workflow.employee_min or profile.employee_min > workflow.employee_max:
                continue
            profiles_by_siren[profile.siren] = profile
            if workflow.sample_limit is not None and len(profiles_by_siren) >= workflow.sample_limit:
                return list(profiles_by_siren.values()), logs
    return list(profiles_by_siren.values()), logs


def build_growth_adapters(enrichment_input: Path | None) -> list[object]:
    if not enrichment_input:
        return []
    if enrichment_input.suffix.lower() == ".json":
        return [NewsManualAdapter(enrichment_input)]
    stem = enrichment_input.stem.lower()
    if "linkedin" in stem:
        return [LinkedInManualCsvAdapter(enrichment_input)]
    if "job" in stem or "recrut" in stem:
        return [JobsManualCsvAdapter(enrichment_input)]
    return [JobsManualCsvAdapter(enrichment_input), NewsManualAdapter(enrichment_input), LinkedInManualCsvAdapter(enrichment_input)]


def run_growth_workflow(
    workflow: WorkflowConfig,
    enrichment_input: Path | None = None,
    sample_limit: int | None = None,
    max_pages_per_query: int = 1,
) -> tuple[list[LeadResult], list[SourceLog]]:
    effective_workflow = workflow
    if sample_limit is not None:
        from dataclasses import replace

        effective_workflow = replace(workflow, sample_limit=sample_limit)
    companies, logs = collect_base_profiles(effective_workflow, max_pages_per_query=max_pages_per_query)
    adapters = build_growth_adapters(enrichment_input)
    results: list[LeadResult] = []
    for company in companies:
        evidence: list[Evidence] = []
        for adapter in adapters:
            evidence.extend(adapter.collect(company))  # type: ignore[attr-defined]
        score, label, rule_results = evaluate_growth_rules(company, evidence, effective_workflow.rules)
        matched_rules = tuple(result.rule_name for result in rule_results if result.matched)
        signal_count = growth_signal_count(evidence)
        recommended_angle = "Structuration RH liée à la croissance/recrutement" if signal_count else "Enrichissement requis avant approche commerciale"
        results.append(
            LeadResult(
                company=company,
                evidence=tuple(evidence),
                rule_results=rule_results,
                priority_score_0_100=score,
                priority_label=label,
                matched_rules=matched_rules,
                growth_signal_count=signal_count,
                recommended_angle=recommended_angle,
                enrichment_needed=not bool(evidence),
            )
        )
    results.sort(key=lambda result: (-result.priority_score_0_100, result.company.name))
    if not adapters:
        logs.append(SourceLog("Enrichissement", "manual CSV/JSON non fourni", "SKIPPED", "Signaux jobs/news/LinkedIn non collectés; enrichment_needed=oui"))
    return results, logs
