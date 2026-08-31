from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import GuardrailReport


class GuardrailReporter:
    """
    Converts GuardrailReport into various output formats.
    """

    @staticmethod
    def to_dict(report: GuardrailReport) -> dict[str, Any]:
        return {
            "passed": report.passed,
            "failed": report.failed,
            "errors": [asdict(issue) for issue in report.errors],
            "warnings": [asdict(issue) for issue in report.warnings],
            "results": [
                {
                    "validator": result.validator,
                    "status": result.status.value,
                    "passed": result.passed,
                    "issues": [asdict(issue) for issue in result.issues],
                    "metadata": result.metadata,
                }
                for result in report.results
            ],
        }

    @classmethod
    def to_json(
        cls,
        report: GuardrailReport,
        *,
        indent: int = 2,
    ) -> str:
        return json.dumps(
            cls.to_dict(report),
            indent=indent,
            default=str,
        )

    @classmethod
    def write_json(
        cls,
        report: GuardrailReport,
        path: str | Path,
    ) -> Path:
        path = Path(path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            cls.to_json(report),
            encoding="utf-8",
        )

        return path

    @staticmethod
    def to_text(
        report: GuardrailReport,
    ) -> str:
        lines: list[str] = []

        lines.append("Guardrail Report")
        lines.append("=" * 60)
        lines.append(f"Status   : {'PASS' if report.passed else 'FAIL'}")
        lines.append(f"Results  : {len(report.results)}")
        lines.append(f"Errors   : {len(report.errors)}")
        lines.append(f"Warnings : {len(report.warnings)}")
        lines.append("")

        for result in report.results:
            lines.append(f"[{result.status.value.upper()}] {result.validator}")

            if not result.issues:
                lines.append("  No issues.")
                continue

            for issue in result.issues:
                location = issue.file

                if issue.line:
                    location += f":{issue.line}"

                if location:
                    lines.append(
                        f"  - [{issue.severity.value}] {location} - {issue.message}"
                    )
                else:
                    lines.append(f"  - [{issue.severity.value}] {issue.message}")

                if issue.suggestion:
                    lines.append(f"      Suggestion: {issue.suggestion}")

            lines.append("")

        return "\n".join(lines)
