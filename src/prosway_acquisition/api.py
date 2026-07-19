from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from collections.abc import Iterable

from .config import (
    ALL_TARGET_NAF,
    EMPLOYEE_BRACKET_LABELS,
    IDF_DEPARTMENTS,
    NAF_LABELS,
    REGION_BY_DEPARTMENT,
    TARGET_EMPLOYEE_BRACKETS,
    TARGET_PER_NAF,
)
from .models import Company, SourceLog
from .scoring import priority_label, score_company, segment_for

API_BASE = "https://recherche-entreprises.api.gouv.fr/search"
USER_AGENT = "Hermes Prosway acquisition research"


def annuaire_url(siren: str) -> str:
    return f"https://annuaire-entreprises.data.gouv.fr/entreprise/{siren}"


def city_from_siege(siege: dict) -> str:
    return siege.get("libelle_commune") or siege.get("commune") or ""


def department_from_siege(siege: dict) -> str:
    return siege.get("departement") or ""


def region_from_siege(siege: dict) -> str:
    return REGION_BY_DEPARTMENT.get(department_from_siege(siege), "")


def api_get(params: dict[str, object]) -> tuple[dict | None, str, str | None]:
    url = API_BASE + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response), url, None
    except Exception as exc:  # network/API failures are logged, not hidden
        return None, url, repr(exc)


def iter_search_params(
    naf_codes: Iterable[str] = ALL_TARGET_NAF,
    employee_brackets: Iterable[str] = TARGET_EMPLOYEE_BRACKETS,
    departments: Iterable[str] = IDF_DEPARTMENTS,
) -> Iterable[dict[str, object]]:
    for naf_code in naf_codes:
        for employee_bracket in employee_brackets:
            for department in departments:
                yield {
                    "activite_principale": naf_code,
                    "tranche_effectif_salarie": employee_bracket,
                    "etat_administratif": "A",
                    "departement": department,
                    "per_page": 25,
                }


def collect_companies(max_pages_per_query: int = 2, pause_seconds: float = 0.15) -> tuple[list[Company], list[SourceLog]]:
    companies: dict[str, Company] = {}
    logs: list[SourceLog] = []
    got_by_naf = {naf_code: 0 for naf_code in ALL_TARGET_NAF}

    for params_base in iter_search_params():
        naf_code = str(params_base["activite_principale"])
        if got_by_naf[naf_code] >= TARGET_PER_NAF[naf_code]:
            continue

        for page in range(1, max_pages_per_query + 1):
            if got_by_naf[naf_code] >= TARGET_PER_NAF[naf_code]:
                break

            params = dict(params_base, page=page)
            data, url, error = api_get(params)
            notes = error or f"{len(data.get('results', [])) if data else 0} résultats page"
            logs.append(SourceLog("API Recherche Entreprises", url, "ERREUR" if error else "OK", notes))

            if error or not data:
                break

            rows = data.get("results", [])
            if not rows:
                break

            for row in rows:
                siren = row.get("siren")
                if not siren or siren in companies:
                    continue

                siege = row.get("siege") or {}
                if siege.get("etat_administratif") and siege.get("etat_administratif") != "A":
                    continue

                department = department_from_siege(siege)
                if department not in IDF_DEPARTMENTS:
                    continue

                employee_bracket = row.get("tranche_effectif_salarie") or siege.get("tranche_effectif_salarie") or params_base["tranche_effectif_salarie"]
                if employee_bracket not in EMPLOYEE_BRACKET_LABELS:
                    continue

                segment = segment_for(naf_code)
                score = score_company(segment, str(employee_bracket))
                name = row.get("nom_complet") or row.get("nom_raison_sociale") or ""
                fit_notes = (
                    f"Taille cible Prosway ({EMPLOYEE_BRACKET_LABELS[employee_bracket]}), "
                    f"segment {segment}, établissement siège actif d’après API publique. "
                    "Site/contact à enrichir sans payant."
                )

                companies[siren] = Company(
                    company_name=name[:120],
                    siren=siren,
                    segment_prosway=segment,
                    naf_code=naf_code,
                    naf_label=NAF_LABELS.get(naf_code, ""),
                    employee_range=EMPLOYEE_BRACKET_LABELS[employee_bracket],
                    city=city_from_siege(siege),
                    region=region_from_siege(siege),
                    website="",
                    source_company_url=annuaire_url(siren),
                    fit_notes=fit_notes,
                    priority_score_0_100=score,
                    priority_label=priority_label(score),
                    department=department,
                )
                got_by_naf[naf_code] += 1

                if got_by_naf[naf_code] >= TARGET_PER_NAF[naf_code]:
                    break

            time.sleep(pause_seconds)

    result = sorted(companies.values(), key=lambda c: (-c.priority_score_0_100, c.segment_prosway, c.company_name))
    return result, logs
