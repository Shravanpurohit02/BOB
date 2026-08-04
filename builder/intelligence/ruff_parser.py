from __future__ import annotations

import re

from builder.intelligence.lint_diagnostics import (
    LintDiagnostic,
    LintReport,
)

_PATTERN = re.compile(
    r"^(?P<rule>[A-Z0-9]+)\s+"
    r"(?P<message>.+?)\n"
    r"\s*-->\s+"
    r"(?P<file>.+?):"
    r"(?P<line>\d+):"
    r"(?P<column>\d+)",
    re.MULTILINE,
)


class RuffParser:
    """
    Converts Ruff output into a structured LintReport.
    """

    def parse(
        self,
        output: str,
    ) -> LintReport:

        report = LintReport()

        for match in _PATTERN.finditer(output):

            report.add(
                LintDiagnostic(
                    file=match.group("file"),
                    line=int(match.group("line")),
                    column=int(match.group("column")),
                    rule=match.group("rule"),
                    message=match.group("message").strip(),
                )
            )

        return report


ruff_parser = RuffParser()

__all__ = (
    "RuffParser",
    "ruff_parser",
)
