from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class WorkflowConfig:
    name: str
    description: str
    departments: tuple[str, ...]
    employee_min: int
    employee_max: int
    employee_brackets: tuple[str, ...]
    naf_codes: tuple[str, ...] | None = None
    sample_limit: int | None = None
    target_per_naf: dict[str, int] = field(default_factory=dict)
    sources: tuple[str, ...] = ("recherche_entreprises",)
    rules: tuple[Any, ...] = ()
    export_profile: str = "mvp"
