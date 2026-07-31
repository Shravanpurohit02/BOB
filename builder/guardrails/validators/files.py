from __future__ import annotations

from pathlib import PurePosixPath

from builder.guardrails.constants import (
    DEFAULT_MAX_FILE_SIZE,
    FORBIDDEN_DIRECTORIES,
    FORBIDDEN_EXTENSIONS,
    FORBIDDEN_FILE_NAMES,
)
from builder.guardrails.models import (
    Severity,
    ValidationContext,
    ValidationIssue,
    ValidationRequest,
    ValidationResult,
)
from builder.guardrails.validators.base import BaseValidator


class FileValidator(BaseValidator):
    """
    Validates file names, extensions and generated artifacts.
    """

    name = "files"
    priority = 30

    def validate(
        self,
        request: ValidationRequest,
        context: ValidationContext,
    ) -> ValidationResult:

        issues: list[ValidationIssue] = []

        files = request.patch.get("files", [])

        for entry in files:

            path = str(entry.get("path", "")).replace("\\", "/")
            content = entry.get("content", "")

            p = PurePosixPath(path)

            if p.name in FORBIDDEN_FILE_NAMES:
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        file=path,
                        message=f"Forbidden file '{p.name}'.",
                        code="FILE001",
                    )
                )

            if p.suffix.lower() in FORBIDDEN_EXTENSIONS:
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        file=path,
                        message=f"Forbidden extension '{p.suffix}'.",
                        code="FILE002",
                    )
                )

            forbidden = [
                part
                for part in p.parts
                if part in FORBIDDEN_DIRECTORIES
            ]

            if forbidden:
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        file=path,
                        message=(
                            "Forbidden directory: "
                            + ", ".join(forbidden)
                        ),
                        code="FILE003",
                    )
                )

            if isinstance(content, str):
                size = len(content.encode("utf-8"))

                if size > DEFAULT_MAX_FILE_SIZE:
                    issues.append(
                        ValidationIssue(
                            validator=self.name,
                            severity=Severity.ERROR,
                            file=path,
                            message=(
                                f"File size exceeds "
                                f"{DEFAULT_MAX_FILE_SIZE} bytes."
                            ),
                            code="FILE004",
                        )
                    )

                if "\x00" in content:
                    issues.append(
                        ValidationIssue(
                            validator=self.name,
                            severity=Severity.ERROR,
                            file=path,
                            message="Binary content detected.",
                            code="FILE005",
                        )
                    )

        if issues:
            return ValidationResult.failure(
                self.name,
                issues,
            )

        return ValidationResult.success(self.name)
