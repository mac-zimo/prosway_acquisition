from __future__ import annotations

from .config import ESN_NAF, FINANCE_NAF, INDUSTRY_NAF


def segment_for(naf_code: str) -> str:
    if naf_code in ESN_NAF:
        return "ESN/conseil IT"
    if naf_code in INDUSTRY_NAF:
        return "Industrie"
    if naf_code in FINANCE_NAF:
        return "Banque/assurance"
    return "Autre pertinent"


def score_company(segment: str, employee_bracket: str) -> int:
    score = 40
    score += {"ESN/conseil IT": 25, "Industrie": 22, "Banque/assurance": 12}.get(segment, 5)
    score += {"22": 15, "31": 18, "32": 20, "41": 18}.get(employee_bracket, 0)
    score += 10  # source API publique fiable + SIREN
    return min(100, score)


def priority_label(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    return "D"


def roles_for(segment: str) -> str:
    base = "DRH; RRH; Responsable Développement RH; Responsable Formation; HRBP; Talent/People Partner"
    if segment == "Industrie":
        return base + "; Responsable QVCT/QVT; Responsable Prévention/HSE; Santé au travail"
    if segment == "ESN/conseil IT":
        return base + "; Responsable Talent Acquisition; Learning & Development; Employee Experience"
    if segment == "Banque/assurance":
        return base + "; Responsable QVCT; Responsable mobilité/carrières"
    return base


def signal_type_for(segment: str) -> str:
    if segment == "Industrie":
        return "HSE/QVCT potentiel"
    if segment == "ESN/conseil IT":
        return "formation/recrutement potentiel"
    return "développement RH potentiel"
