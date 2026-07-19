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


def collect_companies(max_pages_per_query: int = 2, pause_seconds: float = 0.15) -> tuple[list[Company], list[SourceLog]]:
    companies: dict[str, Company] = {}
    logs: list[SourceLog] = []
    got_by_naf = {naf_code: 0 for naf_code in ALL_TARGET_NAF}
    adapter = RechercheEntreprisesAdapter(pause_seconds=pause_seconds)

    for params_base in iter_search_params():
        naf_code = str(params_base.get("activite_principale", ""))
        if got_by_naf[naf_code] >= TARGET_PER_NAF[naf_code]:
            continue

        profiles, query_logs = adapter.fetch_companies(params_base, max_pages_per_query=max_pages_per_query)
        logs.extend(query_logs)
        for profile in profiles:
            if got_by_naf[naf_code] >= TARGET_PER_NAF[naf_code]:
                break
            if profile.siren in companies:
                continue
            if profile.department not in IDF_DEPARTMENTS:
                continue
            if profile.employee_label not in EMPLOYEE_BRACKET_LABELS.values():
                continue
            companies[profile.siren] = company_from_profile(profile)
            got_by_naf[naf_code] += 1

    result = sorted(companies.values(), key=lambda c: (-c.priority_score_0_100, c.segment_prosway, c.company_name))
    return result, logs
