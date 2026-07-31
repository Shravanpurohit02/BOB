from __future__ import annotations

from typing import Iterable

from .models import ValidationIssue


class GuardrailError(Exception):
    """Base exception for the guardrail subsystem."""


class RegistryError(GuardrailError):
    """Raised when validator registration or lookup fails."""


class ValidatorConfigurationError(GuardrailError):
    """Raised when validator configuration is invalid."""


class ValidationError(GuardrailError):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        *,
        issues: Iterable[ValidationIssue] | None = None,
    ) -> None:
        super().__init__(message)
        self.issues = list(issues or [])

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    def __str__(self) -> str:
        text = super().__str__()

        if not self.issues:
            return text

        lines = [text]

        for issue in self.issues:
            location = ""

            if issue.file:
                location = issue.file

                if issue.line:
                    location += f":{issue.line}"

            if location:
                lines.append(
                    f"[{issue.severity.value}] {location} - {issue.message}"
                )
            else:
                lines.append(
                    f"[{issue.severity.value}] {issue.message}"
                )

        return "\n".join(lines)
