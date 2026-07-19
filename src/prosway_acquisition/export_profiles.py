from __future__ import annotations

GROWTH_ENTERPRISE_HEADERS = [
    "company_name", "siren", "employee_range", "city", "department", "region", "naf_code", "naf_label", "website", "source_company_url", "priority_score_0_100", "priority_label", "recommended_angle", "enrichment_needed",
]
GROWTH_SIGNAL_HEADERS = ["company_name", "siren", "signal_type", "signal_description", "source_name", "source_url", "confidence_0_100", "observed_at"]
GROWTH_ANGLE_HEADERS = ["company_name", "siren", "target_roles_recommended", "outreach_angle", "why_now", "contact_channel_found", "contact_source_url", "enrichment_needed"]
GROWTH_SCORING_ROWS = [
    ["rule", "weight", "rationale"],
    ["Base fit", "30", "Société active collectée depuis Recherche Entreprises"],
    ["EmployeeRangeRule(50, 200)", "20", "Tranches officielles 21/22 uniquement"],
    ["DepartmentRule(IDF)", "10", "Siège ou établissement en Île-de-France"],
    ["multi_hiring", "25", "3+ postes ouverts"],
    ["fundraising_recent", "25", "Levée/financement récent"],
    ["new_office", "20", "Nouveau bureau/agence/site"],
    ["headcount_growth", "20", "Croissance d'effectif importée"],
    ["strong_growth_claim", "15", "Claim public de forte croissance"],
]
