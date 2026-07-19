from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from collections.abc import Iterable

from prosway_acquisition.config import (
    ALL_TARGET_NAF,
    EMPLOYEE_BRACKET_LABELS,
    IDF_DEPARTMENTS,
    NAF_LABELS,
    REGION_BY_DEPARTMENT,
    TARGET_EMPLOYEE_BRACKETS,
)
from prosway_acquisition.domain import CompanyProfile
from prosway_acquisition.models import SourceLog

API_BASE = "https://recherche-entreprises.api.gouv.fr/search"
USER_AGENT = "Hermes Prosway acquisition research"
EMPLOYEE_BRACKET_RANGES = {
    "21": (50, 99),
    "22": (100, 199),
    "31": (200, 249),
    "32": (250, 499),
    "41": (500, 999),
}


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
    except Exception as exc:
        return None, url, repr(exc)


def iter_search_params(
    naf_codes: Iterable[str] | None = ALL_TARGET_NAF,
    employee_brackets: Iterable[str] = TARGET_EMPLOYEE_BRACKETS,
    departments: Iterable[str] = IDF_DEPARTMENTS,
    per_page: int = 25,
) -> Iterable[dict[str, object]]:
    naf_iterable = tuple(naf_codes or ("",))
    for naf_code in naf_iterable:
        for employee_bracket in employee_brackets:
            for department in departments:
                params: dict[str, object] = {
                    "tranche_effectif_salarie": employee_bracket,
                    "etat_administratif": "A",
                    "departement": department,
                    "per_page": per_page,
                }
                if naf_code:
                    params["activite_principale"] = naf_code
                yield params


def map_row_to_company_profile(row: dict, fallback_naf_code: str = "", fallback_employee_bracket: str = "") -> CompanyProfile | None:
    siren = row.get("siren")
    if not siren:
        return None
    siege = row.get("siege") or {}
    if siege.get("etat_administratif") and siege.get("etat_administratif") != "A":
        return None

    naf_code = row.get("activite_principale") or fallback_naf_code
    employee_bracket = row.get("tranche_effectif_salarie") or siege.get("tranche_effectif_salarie") or fallback_employee_bracket
    employee_min, employee_max = EMPLOYEE_BRACKET_RANGES.get(str(employee_bracket), (None, None))
    name = row.get("nom_complet") or row.get("nom_raison_sociale") or ""
    source_url = annuaire_url(str(siren))
    return CompanyProfile(
        name=name[:120],
        siren=str(siren),
        website="",
        naf_code=str(naf_code or ""),
        naf_label=NAF_LABELS.get(str(naf_code), ""),
        employee_min=employee_min,
        employee_max=employee_max,
        employee_label=EMPLOYEE_BRACKET_LABELS.get(str(employee_bracket), ""),
        city=city_from_siege(siege),
        department=department_from_siege(siege),
        region=region_from_siege(siege),
        source_urls=(source_url,),
        raw=row,
    )


class RechercheEntreprisesAdapter:
    def __init__(self, pause_seconds: float = 0.15) -> None:
        self.pause_seconds = pause_seconds

    def fetch_companies(self, params: dict[str, object], max_pages_per_query: int = 2) -> tuple[list[CompanyProfile], list[SourceLog]]:
        companies: list[CompanyProfile] = []
        logs: list[SourceLog] = []
        for page in range(1, max_pages_per_query + 1):
            request_params = dict(params, page=page)
            data, url, error = api_get(request_params)
            notes = error or f"{len(data.get('results', [])) if data else 0} résultats page"
            logs.append(SourceLog("API Recherche Entreprises", url, "ERREUR" if error else "OK", notes))
            if error or not data:
                break
            rows = data.get("results", [])
            if not rows:
                break
            for row in rows:
                profile = map_row_to_company_profile(
                    row,
                    fallback_naf_code=str(params.get("activite_principale", "")),
                    fallback_employee_bracket=str(params.get("tranche_effectif_salarie", "")),
                )
                if profile:
                    companies.append(profile)
            time.sleep(self.pause_seconds)
        return companies, logs
