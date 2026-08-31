from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class FailureDiagnosis:
    """
    Deterministic diagnosis derived from BOB's existing validation
    result contract.

    This layer does not invent validation failures. It only converts
    existing ValidationResult / ValidationIssue objects into structured
    autonomous repair context.
    """

    failed: int
    files: tuple[str, ...] = ()
    issues: tuple[dict[str, Any], ...] = ()
    validators: tuple[str, ...] = ()

    @property
    def repairable(self) -> bool:
        return bool(self.files)

    def as_context(
        self,
        *,
        objective: str,
        workspace: str,
    ) -> dict[str, Any]:
        return {
            "objective": objective,
            "workspace": workspace,
            "failed": self.failed,
            "files": list(self.files),
            "issues": [dict(issue) for issue in self.issues],
            "validators": list(self.validators),
        }


class FailureDiagnosisEngine:

    def diagnose(
        self,
        validation: dict[str, Any] | None,
    ) -> FailureDiagnosis:

        validation = validation or {}

        errors = list(
            validation.get("errors") or []
        )

        files: list[str] = []
        issues: list[dict[str, Any]] = []
        validators: list[str] = []

        for result in errors:

            validator = str(
                getattr(result, "validator", "")
            ).strip()

            if validator and validator not in validators:
                validators.append(validator)

            result_issues = list(
                getattr(result, "issues", []) or []
            )

            for issue in result_issues:

                file = str(
                    getattr(issue, "file", "")
                ).strip()

                if file and file not in files:
                    files.append(file)

                issues.append(
                    {
                        "validator": str(
                            getattr(issue, "validator", validator)
                        ),
                        "severity": str(
                            getattr(
                                getattr(issue, "severity", ""),
                                "value",
                                getattr(issue, "severity", ""),
                            )
                        ),
                        "message": str(
                            getattr(issue, "message", "")
                        ),
                        "file": file,
                        "line": int(
                            getattr(issue, "line", 0) or 0
                        ),
                        "column": int(
                            getattr(issue, "column", 0) or 0
                        ),
                        "code": str(
                            getattr(issue, "code", "")
                        ),
                        "suggestion": str(
                            getattr(issue, "suggestion", "")
                        ),
                    }
                )

        return FailureDiagnosis(
            failed=int(validation.get("failed", 0) or 0),
            files=tuple(files),
            issues=tuple(issues),
            validators=tuple(validators),
        )


diagnosis = FailureDiagnosisEngine()


__all__ = (
    "FailureDiagnosis",
    "FailureDiagnosisEngine",
    "diagnosis",
)
