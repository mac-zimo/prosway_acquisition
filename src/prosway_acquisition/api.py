from __future__ import annotations

from .adapters.recherche_entreprises import (
    API_BASE,
    USER_AGENT,
    annuaire_url,
    api_get,
    city_from_siege,
    department_from_siege,
    iter_search_params,
    map_row_to_company_profile,
    region_from_siege,
    RechercheEntreprisesAdapter,
)
from .config import ALL_TARGET_NAF, EMPLOYEE_BRACKET_LABELS, IDF_DEPARTMENTS, TARGET_PER_NAF
from .models import Company, SourceLog
from .scoring import priority_label, score_company, segment_for


def company_from_profile(profile) -> Company:
    segment = segment_for(profile.naf_code)
    employee_bracket = ""
    for bracket, label in EMPLOYEE_BRACKET_LABELS.items():
        if label == profile.employee_label:
            employee_bracket = bracket
            break
    score = score_company(segment, employee_bracket)
    fit_notes = (
        f"Taille cible Prosway ({profile.employee_range}), "
        f"segment {segment}, établissement siège actif d’après API publique. "
        "Site/contact à enrichir sans payant."
    )
    return Company(
        company_name=profile.name,
        siren=profile.siren,
        segment_prosway=segment,
        naf_code=profile.naf_code,
        naf_label=profile.naf_label,
        employee_range=profile.employee_range,
        city=profile.city,
        region=profile.region,
        website=profile.website,
        source_company_url=profile.source_urls[0] if profile.source_urls else annuaire_url(profile.siren),
        fit_notes=fit_notes,
        priority_score_0_100=score,
        priority_label=priority_label(score),
        department=profile.department,
    )


def collect_companies(
    max_pages_per_query: int = 2,
    pause_seconds: float = 0.15,
    naf_codes=None,
    employee_brackets=None,
    departments=None,
    target_per_naf=None,
    sample_limit: int | None = None,
) -> tuple[list[Company], list[SourceLog]]:
    companies: dict[str, Company] = {}
    logs: list[SourceLog] = []
    selected_naf = tuple(naf_codes or ALL_TARGET_NAF)
    selected_brackets = tuple(employee_brackets or EMPLOYEE_BRACKET_LABELS.keys())
    selected_departments = tuple(departments or IDF_DEPARTMENTS)
    per_naf = target_per_naf or {naf_code: sample_limit or TARGET_PER_NAF.get(naf_code, 10) for naf_code in selected_naf}
    got_by_naf = {naf_code: 0 for naf_code in selected_naf}
    adapter = RechercheEntreprisesAdapter(pause_seconds=pause_seconds)

    for params_base in iter_search_params(selected_naf, selected_brackets, selected_departments):
        naf_code = str(params_base.get("activite_principale", ""))
        if got_by_naf[naf_code] >= per_naf[naf_code]:
            continue

        profiles, query_logs = adapter.fetch_companies(params_base, max_pages_per_query=max_pages_per_query)
        logs.extend(query_logs)
        for profile in profiles:
            if sample_limit is not None and len(companies) >= sample_limit:
                break
            if got_by_naf[naf_code] >= per_naf[naf_code]:
                break
            if profile.siren in companies:
                continue
            if profile.department not in selected_departments:
                continue
            if profile.employee_label not in {EMPLOYEE_BRACKET_LABELS.get(str(b), "") for b in selected_brackets}:
                continue
            companies[profile.siren] = company_from_profile(profile)
            got_by_naf[naf_code] += 1
        if sample_limit is not None and len(companies) >= sample_limit:
            break

    result = sorted(companies.values(), key=lambda c: (-c.priority_score_0_100, c.segment_prosway, c.company_name))
    return result, logs
