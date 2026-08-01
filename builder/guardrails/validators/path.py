from __future__ import annotations

from pathlib import PurePosixPath

from builder.guardrails.constants import FORBIDDEN_DIRECTORIES
from builder.guardrails.models import (
    Severity,
    ValidationContext,
    ValidationIssue,
    ValidationRequest,
    ValidationResult,
)
from builder.guardrails.validators.base import BaseValidator


class PathValidator(BaseValidator):
    """
    Validates that every file path remains inside the workspace.
    """

    name = "path"
    priority = 20

    def validate(
        self,
        request: ValidationRequest,
        context: ValidationContext,
    ) -> ValidationResult:

        issues: list[ValidationIssue] = []

        files = request.patch.get("files", [])

        for entry in files:
            path = str(entry.get("path", "")).replace("\\", "/").strip()

            if not path:
                continue

            p = PurePosixPath(path)

            # Absolute path
            if p.is_absolute():
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.CRITICAL,
                        file=path,
                        message="Absolute paths are not allowed.",
                        code="PATH001",
                        suggestion="Use repository-relative paths.",
                    )
                )
                continue

            # Parent traversal
            if ".." in p.parts:
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.CRITICAL,
                        file=path,
                        message="Path traversal detected.",
                        code="PATH002",
                        suggestion="Remove '..' from the path.",
                    )
                )

            # Windows drive
            if ":" in path.split("/")[0]:
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.CRITICAL,
                        file=path,
                        message="Windows drive paths are not allowed.",
                        code="PATH003",
                    )
                )

            # Forbidden directories
            forbidden = [part for part in p.parts if part in FORBIDDEN_DIRECTORIES]

            if forbidden:
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        file=path,
                        message=(
                            "Path contains forbidden directories: "
                            + ", ".join(forbidden)
                        ),
                        code="PATH004",
                    )
                )

            # Empty path component
            if "" in p.parts:
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        file=path,
                        message="Invalid path component.",
                        code="PATH005",
                    )
                )

        if issues:
            return ValidationResult.failure(
                self.name,
                issues,
            )

        return ValidationResult.success(self.name)
