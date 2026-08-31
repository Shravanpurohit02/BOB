from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass(slots=True)
class LintDiagnostic:
    """
    Represents one lint finding.
    """

    file: str
    line: int
    column: int

    rule: str
    message: str

    severity: str = "warning"


@dataclass(slots=True)
class LintReport:
    """
    Collection of diagnostics.
    """

    diagnostics: list[LintDiagnostic] = field(
        default_factory=list,
    )

    def add(
        self,
        diagnostic: LintDiagnostic,
    ) -> None:
        self.diagnostics.append(
            diagnostic,
        )

    @property
    def total(self) -> int:
        return len(self.diagnostics)

    def by_rule(
        self,
        rule: str,
    ) -> list[LintDiagnostic]:

        return [
            d
            for d in self.diagnostics
            if d.rule == rule
        ]

    def by_file(
        self,
    ) -> dict[str, list[LintDiagnostic]]:

        grouped: dict[
            str,
            list[LintDiagnostic],
        ] = defaultdict(list)

        for diagnostic in self.diagnostics:
            grouped[
                diagnostic.file
            ].append(
                diagnostic,
            )

        return dict(grouped)

    def summary(
        self,
    ) -> dict[str, int]:

        counts: dict[str, int] = defaultdict(int)

        for diagnostic in self.diagnostics:
            counts[
                diagnostic.rule
            ] += 1

        return dict(counts)


lint_report = LintReport()

__all__ = (
    "LintDiagnostic",
    "LintReport",
    "lint_report",
)
