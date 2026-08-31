
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(slots=True)
class BudgetReport:

    provider: str

    estimated_tokens: int = 0
    estimated_bytes: int = 0

    token_limit: int = 0
    byte_limit: int = 0

    selected_files: list[str] = field(default_factory=list)
    omitted_files: list[str] = field(default_factory=list)

    compression_ratio: float = 1.0

    within_budget: bool = False

    metadata: dict = field(default_factory=dict)
