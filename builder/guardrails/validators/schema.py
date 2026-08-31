from __future__ import annotations
from typing import ClassVar

from collections.abc import Mapping

from builder.guardrails.constants import (
    ALLOWED_OPERATIONS,
    SCHEMA_VERSION,
)
from builder.guardrails.models import (
    Severity,
    ValidationContext,
    ValidationIssue,
    ValidationRequest,
    ValidationResult,
)
from builder.guardrails.validators.base import BaseValidator


class SchemaValidator(BaseValidator):
    """
    Validates the Builder patch schema.
    """

    name = "schema"
    priority = 10

    REQUIRED_TOP_LEVEL: ClassVar = {
        "version",
        "files",
    }

    REQUIRED_FILE_FIELDS: ClassVar = {
        "path",
        "operation",
    }

    def validate(
        self,
        request: ValidationRequest,
        context: ValidationContext,
    ) -> ValidationResult:

        issues: list[ValidationIssue] = []

        patch = request.patch

        if not isinstance(patch, Mapping):
            return ValidationResult.failure(
                self.name,
                [
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.CRITICAL,
                        message="Patch must be a dictionary.",
                        code="SCHEMA001",
                    )
                ],
            )

        missing = self.REQUIRED_TOP_LEVEL - set(patch)

        if missing:
            issues.append(
                ValidationIssue(
                    validator=self.name,
                    severity=Severity.CRITICAL,
                    message=f"Missing top-level fields: {sorted(missing)}",
                    code="SCHEMA002",
                )
            )

        version = patch.get("version")

        if version != SCHEMA_VERSION:
            issues.append(
                ValidationIssue(
                    validator=self.name,
                    severity=Severity.ERROR,
                    message=(
                        f"Unsupported schema version "
                        f"'{version}'. Expected '{SCHEMA_VERSION}'."
                    ),
                    code="SCHEMA003",
                )
            )

        files = patch.get("files")

        if not isinstance(files, list):
            issues.append(
                ValidationIssue(
                    validator=self.name,
                    severity=Severity.CRITICAL,
                    message="'files' must be a list.",
                    code="SCHEMA004",
                )
            )
            return ValidationResult.failure(self.name, issues)

        seen_paths: set[str] = set()

        for index, entry in enumerate(files):
            if not isinstance(entry, Mapping):
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        message=f"files[{index}] must be an object.",
                        code="SCHEMA005",
                    )
                )
                continue

            missing_fields = self.REQUIRED_FILE_FIELDS - set(entry)

            if missing_fields:
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        message=(
                            f"files[{index}] missing fields: {sorted(missing_fields)}"
                        ),
                        code="SCHEMA006",
                    )
                )

            path = entry.get("path")

            if not isinstance(path, str) or not path.strip():
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        message=f"files[{index}] has an invalid path.",
                        code="SCHEMA007",
                    )
                )
            elif path in seen_paths:
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        message=f"Duplicate path '{path}'.",
                        code="SCHEMA008",
                    )
                )
            else:
                seen_paths.add(path)

            operation = entry.get("operation")

            if operation not in ALLOWED_OPERATIONS:
                issues.append(
                    ValidationIssue(
                        validator=self.name,
                        severity=Severity.ERROR,
                        message=(f"Invalid operation '{operation}' for '{path}'."),
                        code="SCHEMA009",
                    )
                )

            if operation in {"create", "modify"}:
                content = entry.get("content")

                if not isinstance(content, str):
                    issues.append(
                        ValidationIssue(
                            validator=self.name,
                            severity=Severity.ERROR,
                            message=(
                                f"'content' is required for {operation} operation."
                            ),
                            code="SCHEMA010",
                        )
                    )

        if issues:
            return ValidationResult.failure(
                self.name,
                issues,
            )

        return ValidationResult.success(self.name)