from __future__ import annotations

from .config import ALL_TARGET_NAF, IDF_DEPARTMENTS, TARGET_PER_NAF
from .rules import default_growth_rules
from .workflows import WorkflowConfig

WORKFLOWS = {
    "rh_mvp_idf": WorkflowConfig(
        name="rh_mvp_idf",
        description="MVP Prosway RH/QVCT/formation en Île-de-France, secteurs ciblés, 100-1000 salariés.",
        departments=IDF_DEPARTMENTS,
        employee_min=100,
        employee_max=999,
        employee_brackets=("22", "31", "32", "41"),
        naf_codes=ALL_TARGET_NAF,
        sample_limit=None,
        target_per_naf=TARGET_PER_NAF,
        sources=("recherche_entreprises",),
        rules=(),
        export_profile="mvp",
    ),
    "rh_growth_50_200_idf": WorkflowConfig(
        name="rh_growth_50_200_idf",
        description="Entreprises 50-200 salariés en Île-de-France avec signaux de croissance et besoin RH fractionné probable.",
        departments=IDF_DEPARTMENTS,
        employee_min=50,
        employee_max=200,
        employee_brackets=("21", "22"),
        naf_codes=None,
        sample_limit=50,
        target_per_naf={},
        sources=("recherche_entreprises", "jobs_manual_csv", "news_manual", "linkedin_manual_csv"),
        rules=default_growth_rules(IDF_DEPARTMENTS),
        export_profile="growth",
    ),
}


def get_workflow(name: str) -> WorkflowConfig:
    try:
        return WORKFLOWS[name]
    except KeyError as exc:
        available = ", ".join(sorted(WORKFLOWS))
        raise ValueError(f"Unknown workflow '{name}'. Available: {available}") from exc
